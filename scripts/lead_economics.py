#!/usr/bin/env python3
"""Lead value, rent pricing, pay-per-call revenue and a month-by-month cash-flow model for one site.

Examples
  # From measured keyword data (keyword_tool.py volume) + SERP difficulty:
  python3 scripts/lead_economics.py --niche tree-service --keywords projects/x/data/keywords.csv --difficulty 42 \
      --out projects/x/research/economics.md

  # From explicit lead scenarios (conservative base strong) and tenant facts:
  python3 scripts/lead_economics.py --niche roofing --leads 6 15 30 --ticket 9000 --close-rate 0.25 --margin 0.35 \
      --cpc 28 --rent 1500

Model
  value per lead (tenant)  = ticket x close rate x gross margin
  fair price per lead      = 20-45% of that gross profit (tenant keeps the rest)
  Google Ads cost per lead = CPC / ads conversion rate    (the tenant's alternative, used to anchor rent)
  pay-per-call revenue     = leads x call share x billable share x payout
  ramp                     = nothing for `delay` months, then linear to full leads by `months_to_rank`
Rental starts when monthly leads reach --min-leads-to-rent (you need proof before a tenant signs).
Before that, the hybrid path sells calls through a network.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import find_niche, fmt_money, load_niches, md_table, read_csv, write_text  # noqa: E402

CLOSE_RATE_BY_URGENCY = {"emergency": 0.50, "mixed": 0.35, "planned": 0.25}
MONTHS_TO_RANK = [(35, 3), (55, 6), (70, 10), (101, 14)]  # difficulty upper bound -> months to full ranking


def geo_mean(rng):
    return math.sqrt(max(rng[0], 1) * max(rng[1], 1)) if rng and rng[1] else 0


def months_for_difficulty(d):
    for limit, months in MONTHS_TO_RANK:
        if d < limit:
            return months
    return 14


def leads_from_keywords(path):
    from keyword_tool import scenario_table  # same CTR model as the keyword report
    rows = [r for r in read_csv(path) if (r.get("search_volume") or "").strip() not in ("", "None")]
    if not rows:
        sys.exit(f"{path} has no search_volume values - run keyword_tool.py volume first")
    estimate = any((r.get("source") or "").startswith("ESTIMATE") for r in rows)
    sc = scenario_table(rows)
    leads = [round(s[3], 1) for s in sc]
    ads_value = [round(s[5]) for s in sc]
    cpcs = sorted(float(r["cpc"]) for r in rows if (r.get("cpc") or "").strip() not in ("", "None"))
    median_cpc = cpcs[len(cpcs) // 2] if cpcs else None
    return leads, ads_value, median_cpc, estimate


def ramp_factor(month, delay, months_to_rank):
    if month <= delay:
        return 0.0
    return min(1.0, (month - delay) / max(1, months_to_rank - delay))


def simulate(a, leads_full, rent_price, per_call, months):
    """Month-by-month: leads, pay-per-call revenue until rented, then rent. Returns rows + summary."""
    rows, cum, cash_low, breakeven, rented_from = [], -a.build_cost, -a.build_cost, None, None
    for m in range(1, months + 1):
        leads = leads_full * ramp_factor(m, a.delay, a.months_to_rank)
        cost = a.monthly_cost + (a.link_budget if m <= a.link_months else 0)
        rented = rented_from is not None or (leads >= a.min_leads_to_rent and m >= a.delay + 1 and rent_price > 0
                                             and a.model in ("rank_and_rent", "hybrid"))
        if rented and rented_from is None:
            rented_from = m + a.sales_lag  # time to find/sign a tenant after proof
        if rented_from is not None and m >= rented_from:
            revenue, source = rent_price, "rent"
        elif a.model in ("pay_per_call", "hybrid"):
            revenue, source = leads * a.call_share * a.billable * per_call, "ppc"
        else:
            revenue, source = 0.0, "-"
        cum += revenue - cost
        cash_low = min(cash_low, cum)
        if breakeven is None and cum >= 0:
            breakeven = m
        rows.append([m, round(leads, 1), source, round(revenue), round(cost), round(cum)])
    return rows, {"breakeven_month": breakeven, "cumulative": round(cum), "max_cash_at_risk": round(-cash_low),
                  "rented_from_month": rented_from}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--niche", required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--keywords", help="keywords CSV with volumes (from keyword_tool.py)")
    src.add_argument("--leads", type=float, nargs=3, metavar=("CONS", "BASE", "STRONG"),
                     help="monthly leads at full ranking for 3 scenarios")
    ap.add_argument("--model", choices=["rank_and_rent", "pay_per_call", "hybrid"], default="hybrid")
    ap.add_argument("--ticket", type=float, help="average job value (default: niche prior geometric mean)")
    ap.add_argument("--close-rate", type=float, help="tenant close rate on leads (default by urgency)")
    ap.add_argument("--margin", type=float, default=0.40, help="tenant gross margin")
    ap.add_argument("--cpc", type=float, help="median CPC (default: from keywords CSV)")
    ap.add_argument("--ads-cvr", type=float, default=0.10, help="landing-page conversion on Google Ads")
    ap.add_argument("--payout", type=float, help="pay-per-call payout (default: niche prior midpoint)")
    ap.add_argument("--call-share", type=float, default=0.8, help="share of leads that are phone calls")
    ap.add_argument("--billable", type=float, default=0.6, help="share of calls that are billable")
    ap.add_argument("--rent", type=float, help="evaluate a specific monthly rent instead of the recommendation")
    ap.add_argument("--min-leads-to-rent", type=float, default=5)
    ap.add_argument("--sales-lag", type=int, default=1, help="months from proof to a signed tenant")
    ap.add_argument("--difficulty", type=float, help="SERP difficulty 0-100 (sets months to rank)")
    ap.add_argument("--months-to-rank", type=int, help="months until full ranking (overrides difficulty)")
    ap.add_argument("--delay", type=int, default=1, help="months before any leads (indexing)")
    ap.add_argument("--build-cost", type=float, default=600, help="domain, content, setup")
    ap.add_argument("--monthly-cost", type=float, default=60, help="hosting, call tracking, tools")
    ap.add_argument("--link-budget", type=float, default=150, help="monthly authority budget")
    ap.add_argument("--link-months", type=int, default=6)
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    niches, _ = load_niches()
    n = find_niche(niches, a.niche)
    if not n:
        sys.exit(f"unknown niche {a.niche}")
    notes = []
    if a.keywords:
        leads, ads_value, kw_cpc, estimate = leads_from_keywords(a.keywords)
        notes.append(f"Leads from measured keyword volumes in `{os.path.basename(a.keywords)}` via the local CTR model.")
        if estimate:
            notes.append("WARNING: keyword volumes are population-share ESTIMATES -> economics are not decision-grade.")
    else:
        leads, ads_value, kw_cpc = list(a.leads), None, None
        notes.append("Leads supplied manually (state where they came from in the memo).")
    cpc = a.cpc or kw_cpc
    ticket = a.ticket or geo_mean(n["ticket_usd"])
    close = a.close_rate or CLOSE_RATE_BY_URGENCY[n["urgency"]]
    payout = a.payout or ((n["ppc_payout_usd"][0] + n["ppc_payout_usd"][1]) / 2 if n.get("ppc_payout_usd") else 0)
    if a.months_to_rank:
        months_to_rank = a.months_to_rank
    elif a.difficulty is not None:
        months_to_rank = months_for_difficulty(a.difficulty)
    else:
        months_to_rank = 8
        notes.append("No SERP difficulty given; assumed 8 months to full ranking.")
    a.months_to_rank = max(months_to_rank, a.delay + 1)

    value_per_lead = ticket * close * a.margin
    revenue_per_lead = ticket * close
    fair_lo, fair_hi = 0.20 * value_per_lead, 0.45 * value_per_lead
    ads_cpl = cpc / a.ads_cvr if cpc else None
    if n.get("per_lead_usd"):
        fair_lo, fair_hi = (max(fair_lo, n["per_lead_usd"][0] * 0.5), fair_hi)

    def rent_for(l, price):
        return round(l * price / 50) * 50

    rec = {"floor": rent_for(leads[0], fair_lo), "target": rent_for(leads[1], (fair_lo + fair_hi) / 2),
           "stretch": rent_for(leads[2], fair_hi)}
    if ads_value:
        cap = round(0.5 * ads_value[1] / 50) * 50
        if cap and rec["target"] > cap:
            rec["target"] = cap
            notes.append("Target rent capped at 50% of the base-scenario Ads-equivalent value.")
    market = n.get("rent_usd_month")
    if market:
        if rec["target"] > market[1]:
            rec["target"] = market[1]
            notes.append(f"Target rent capped at the niche's market prior high ({fmt_money(market[1])}). Value-based "
                         "pricing above market needs proof (call recordings, closed-job data) before you ask for it.")
        stretch_cap = round(1.5 * market[1] / 50) * 50
        if rec["stretch"] > stretch_cap:
            rec["stretch"] = stretch_cap
        rec["floor"] = min(rec["floor"], rec["target"])
    rent_price = a.rent or rec["target"]

    def scenario_rent(l):
        r = rent_for(l, (fair_lo + fair_hi) / 2)
        return min(r, market[1]) if market else r

    scenarios = []
    for name, l in zip(("conservative", "base", "strong"), leads):
        rows, summary = simulate(a, l, rent_price if a.rent else scenario_rent(l), payout, a.horizon)
        ppc_full = l * a.call_share * a.billable * payout
        scenarios.append({"name": name, "leads": l, "ppc_full": round(ppc_full), "rows": rows, **summary})

    lines = [f"# Lead economics - {n['name']}", "",
             "## Assumptions", "",
             md_table([
                 ["Average ticket", fmt_money(ticket), "user" if a.ticket else f"niche prior (geo-mean of {n['ticket_usd']})"],
                 ["Tenant close rate", f"{close:.0%}", "user" if a.close_rate else f"default for {n['urgency']} niches"],
                 ["Tenant gross margin", f"{a.margin:.0%}", "user/default"],
                 ["Median CPC", fmt_money(cpc, 2) if cpc else "n/a", "keywords CSV" if kw_cpc and not a.cpc else "user"],
                 ["Pay-per-call payout", fmt_money(payout), "user" if a.payout else "niche prior midpoint"],
                 ["Calls share / billable share", f"{a.call_share:.0%} / {a.billable:.0%}", "default"],
                 ["Months to full ranking", a.months_to_rank, f"difficulty {a.difficulty}" if a.difficulty is not None else "assumed"],
                 ["Build cost / monthly cost / links", f"{fmt_money(a.build_cost)} / {fmt_money(a.monthly_cost)} / "
                  f"{fmt_money(a.link_budget)} x {a.link_months} mo", "default"],
             ], ["Input", "Value", "Source"]), "",
             "## What a lead is worth", "",
             f"- Revenue per lead to the tenant: **{fmt_money(revenue_per_lead)}** (ticket x close rate)",
             f"- Gross profit per lead to the tenant: **{fmt_money(value_per_lead)}**",
             f"- Fair price per exclusive lead: **{fmt_money(fair_lo)} - {fmt_money(fair_hi)}**",
             f"- Tenant's Google Ads cost per lead: **{fmt_money(ads_cpl) if ads_cpl else 'n/a'}** "
             f"(CPC / {a.ads_cvr:.0%} conversion)" + (" -> your leads are a bargain next to Ads" if ads_cpl and ads_cpl > fair_hi else ""),
             f"- Niche market priors: rent {n.get('rent_usd_month') or 'n/a'} / mo, per lead {n.get('per_lead_usd') or 'n/a'}, "
             f"pay-per-call {n.get('ppc_payout_usd') or 'n/a'}", "",
             "## Monthly potential at full ranking", "",
             md_table([[s["name"], s["leads"], fmt_money(rent_for(s["leads"], fair_lo)) + " - " + fmt_money(rent_for(s["leads"], fair_hi)),
                        fmt_money(s["ppc_full"]),
                        fmt_money(ads_value[i]) if ads_value else "-"] for i, s in enumerate(scenarios)],
                      ["Scenario", "Leads/mo", "Value-based rent band", "Pay-per-call/mo", "Ads-equivalent/mo"]), "",
             f"**Recommended rent:** floor {fmt_money(rec['floor'])} | target {fmt_money(rec['target'])} | "
             f"stretch {fmt_money(rec['stretch'])} per month" + (f" (evaluating user rent {fmt_money(a.rent)})" if a.rent else ""), "",
             f"## {a.horizon}-month cash flow ({a.model})", "",
             md_table([[s["name"], s["rented_from_month"] or "never", s["breakeven_month"] or f">{a.horizon}",
                        fmt_money(s["max_cash_at_risk"]), fmt_money(s["cumulative"])] for s in scenarios],
                      ["Scenario", "Rented from month", "Break-even month", "Max cash at risk", f"Net after {a.horizon} mo"]), ""]
    base_rows = scenarios[1]["rows"]
    lines += ["<details><summary>Base scenario month by month</summary>", "",
              md_table(base_rows, ["Month", "Leads", "Revenue source", "Revenue", "Cost", "Cumulative"]), "", "</details>", ""]
    monthly_net = rec["target"] - a.monthly_cost
    lines += [f"Indicative asset value once rented at target: {fmt_money(24 * monthly_net)} - {fmt_money(36 * monthly_net)} "
              "(24-36x monthly net, a common small-website multiple, not an appraisal).", ""]
    lines += ["## Notes", ""] + [f"- {x}" for x in notes] + [
        "- Every value-per-lead input should come from the tenant conversation (ticket, close rate) once one exists.",
        "- Kill criteria belong in the IC decision: e.g. 'fewer than N leads/mo by month M -> pivot or sell calls only'.", ""]
    text = "\n".join(lines)
    if a.out:
        write_text(a.out, text)
        print(f"wrote {a.out}")
    else:
        print(text)
    if a.json:
        print(json.dumps({"niche": n["id"], "leads": leads, "value_per_lead": round(value_per_lead),
                          "fair_price_per_lead": [round(fair_lo), round(fair_hi)],
                          "ads_cost_per_lead": round(ads_cpl) if ads_cpl else None, "recommended_rent": rec,
                          "scenarios": [{k: v for k, v in s.items() if k != "rows"} for s in scenarios]}, indent=2))


if __name__ == "__main__":
    main()
