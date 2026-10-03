#!/usr/bin/env python3
"""Score and rank niches from data/niches.json for a monetization model.

Commands
  rank   (default) Rank niches for a model, optionally for a city or state.
  show   Print the full card for one niche.

Examples
  python3 scripts/niche_scorer.py rank --model rank_and_rent --top 20
  python3 scripts/niche_scorer.py rank --model rank_and_rent --city "Tulsa, OK" --risk-tolerance low
  python3 scripts/niche_scorer.py rank --model pay_per_call --state FL --format csv --out projects/x/data/niches.csv
  python3 scripts/niche_scorer.py rank --model nationwide --top 15
  python3 scripts/niche_scorer.py show water-damage

Models
  rank_and_rent  Rank a local site and rent it to one business (flat monthly fee or per lead).
  pay_per_call   Local or regional sites whose calls are sold through a network or buyer.
  nationwide     One brand covering many states, with calls routed by a network to buyers by caller ZIP.

Every number comes from priors (data/niches.json). The ranking is a triage shortlist for the war room.
It is not a decision.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (STATE_TAGS, find_niche, find_place, fmt_int, fmt_money, load_niches,  # noqa: E402
                    load_places, md_table, normalize_state, parse_city_arg, write_csv, write_text)

LEVEL = {"low": 9, "medium": 6, "high": 3}
REG = {"low": 10, "medium": 6, "high": 3, "extreme": 0}
LICENSE = {"low": 10, "medium": 7, "high": 5}
URGENCY = {"emergency": 10, "mixed": 7, "planned": 4}
SEASON = {"year_round": 9, "seasonal": 6, "highly_seasonal": 3}
TIER = {"A": 10, "B": 7.5, "C": 5, "D": 2.5}

WEIGHTS = {
    # R&R sites usually rank WITHOUT a Google Business Profile (organic only, below ads/LSAs/map pack),
    # so rankability carries the most weight.
    "rank_and_rent": {"value": .20, "demand": .12, "urgency": .06, "rankability": .22, "buyers": .12,
                      "stability": .06, "risk": .10, "model_fit": .12},
    "pay_per_call": {"value": .22, "demand": .15, "urgency": .15, "rankability": .13, "buyers": .08,
                     "stability": .05, "risk": .10, "model_fit": .12},
    "nationwide": {"value": .22, "demand": .18, "urgency": .12, "rankability": .10, "buyers": .05,
                   "stability": .05, "risk": .13, "model_fit": .15},
}
GEO_WEIGHT = 0.10

# Assumptions behind the rough "potential" band (shown in the report header).
ORGANIC_CAPTURE = (0.05, 0.20)   # share of cluster searches that click a top-3 organic result
CONVERSION = (0.08, 0.18)        # visit -> call/form
BILLABLE = (0.5, 0.7)            # share of calls that meet buffer / are not duplicates (pay-per-call)


def log_scale(value, lo, hi):
    """Map value onto 0-10 logarithmically between lo (0) and hi (10)."""
    if not value or value <= 0:
        return 0.0
    return max(0.0, min(10.0, 10 * (math.log(value) - math.log(lo)) / (math.log(hi) - math.log(lo))))


def mid(rng):
    return (rng[0] + rng[1]) / 2 if rng else 0


def value_score(n, model):
    if model == "rank_and_rent":
        rent = log_scale(mid(n["rent_usd_month"]), 150, 3000) if n.get("rent_usd_month") else 0.0
        ticket = log_scale(mid(n["ticket_usd"]), 100, 20000) if n["ticket_usd"][1] else 0.0
        return 0.65 * rent + 0.35 * ticket
    payout = log_scale(mid(n["ppc_payout_usd"]), 8, 300) if n.get("ppc_payout_usd") else 0.0
    return payout


def demand_score(n, model, pop=None, tiers=None):
    base = TIER.get(n["demand_tier"], 5)
    if pop and tiers and model != "nationwide":
        lo, hi = tiers[n["demand_tier"]]["searches_per_100k_residents_per_month"]
        est = (lo + hi) / 2 * pop / 100000
        # 50 searches/mo -> ~2.5, 500 -> ~6, 5000 -> 10
        return 0.4 * base + 0.6 * log_scale(est, 15, 5000)
    return base


def score_niche(n, model, state=None, pop=None, tiers=None):
    comps = {
        "value": value_score(n, model),
        "demand": demand_score(n, model, pop, tiers),
        "urgency": URGENCY[n["urgency"]],
        "rankability": (LEVEL[n["competition_baseline"]] + LEVEL[n["lsa_presence"]] + LEVEL[n["directory_pressure"]]) / 3,
        "buyers": (LEVEL_INV(n["buyer_density"]) if model == "rank_and_rent"
                   else 0.5 * LEVEL_INV(n["buyer_density"]) + 0.5 * n["model_fit"][model]),
        "stability": SEASON[n["seasonality"]],
        "risk": 0.5 * REG[n["regulatory_risk"]] + 0.3 * LEVEL[n["spam_scrutiny"]] / 0.9 + 0.2 * LICENSE[n["license_sensitivity"]],
        "model_fit": n["model_fit"][model],
    }
    weights = dict(WEIGHTS[model])
    if pop and tiers and model != "nationwide":
        # With a real market, the city-specific revenue band matters more than generic priors.
        weights = {k: v * 0.8 for k, v in weights.items()}
        weights["potential"] = 0.20
        comps["potential"] = log_scale(potential(n, model, pop, tiers)[2][1], 100, 3000)
    geo_matched = []
    if state and model != "nationwide":
        tags = STATE_TAGS.get(state, set())
        if n["geo_tags"]:
            geo_matched = [t for t in n["geo_tags"] if t in tags]
            comps["geo"] = 10 * len(geo_matched) / len(n["geo_tags"])
        else:
            comps["geo"] = 6.0  # location-agnostic niche
        weights["geo"] = GEO_WEIGHT
    total = sum(weights.values())
    score = sum(weights[k] * comps[k] for k in weights) / total * 10
    if n["model_fit"][model] <= 1:
        score *= 0.3  # structurally wrong model for this niche
    return round(score, 1), comps, geo_matched


def LEVEL_INV(level):
    return {"low": 3, "medium": 6, "high": 9}[level]


def flags_for(n, model):
    f = []
    if n["regulatory_risk"] == "extreme":
        f.append("EXTREME-REG")
    elif n["regulatory_risk"] == "high":
        f.append("REGULATED")
    if n["spam_scrutiny"] == "high":
        f.append("SPAM-SCRUTINY")
    if n["seasonality"] == "highly_seasonal":
        f.append("HIGHLY-SEASONAL")
    if n["lsa_presence"] == "high":
        f.append("LSA-HEAVY")
    if n["directory_pressure"] == "high":
        f.append("DIRECTORY-HEAVY")
    if model == "rank_and_rent" and not n.get("rent_usd_month"):
        f.append("NOT-RENTABLE")
    if model != "rank_and_rent" and not n.get("ppc_payout_usd"):
        f.append("NO-PPC-BUYERS")
    if n["ticket_usd"][1] and n["ticket_usd"][1] < 600:
        f.append("LOW-TICKET")
    return f


def potential(n, model, pop, tiers):
    """Very rough monthly lead & revenue band at top-3 organic for a city of `pop` people."""
    lo, hi = tiers[n["demand_tier"]]["searches_per_100k_residents_per_month"]
    s_lo, s_hi = lo * pop / 100000, hi * pop / 100000
    leads_lo = s_lo * ORGANIC_CAPTURE[0] * CONVERSION[0]
    leads_hi = s_hi * ORGANIC_CAPTURE[1] * CONVERSION[1]
    if model == "rank_and_rent":
        pl = n.get("per_lead_usd") or [0, 0]
        rev_lo, rev_hi = leads_lo * pl[0], leads_hi * pl[1]
        if n.get("rent_usd_month"):
            rev_hi = min(rev_hi, n["rent_usd_month"][1])
    else:
        pay = n.get("ppc_payout_usd") or [0, 0]
        rev_lo, rev_hi = leads_lo * BILLABLE[0] * pay[0], leads_hi * BILLABLE[1] * pay[1]
    leads_base = math.sqrt(max(leads_lo, 0.01) * max(leads_hi, 0.01))
    rev_base = math.sqrt(max(rev_lo, 1) * max(rev_hi, 1))
    return ((round(s_lo), round(s_hi)), (round(leads_lo, 1), round(leads_base, 1), round(leads_hi, 1)),
            (round(rev_lo), round(rev_base), round(rev_hi)))


def rank(args):
    niches, meta = load_niches()
    tiers = meta["demand_tiers"]
    state, pop, city_label = normalize_state(args.state) if args.state else None, args.population, None
    if args.city:
        name, st = parse_city_arg(args.city)
        place = find_place(load_places(), name, st)
        if not place:
            sys.exit(f"city not found: {args.city}")
        state, pop = place["state"], pop or place["population"]
        city_label = f"{place['name']}, {place['state']}"

    allowed_reg = {"low": {"low", "medium"}, "medium": {"low", "medium", "high"},
                   "high": {"low", "medium", "high", "extreme"}}[args.risk_tolerance]
    rows = []
    for n in niches.values():
        if args.category and n["category"] not in args.category:
            continue
        if n["regulatory_risk"] not in allowed_reg:
            continue
        if args.risk_tolerance == "low" and n["spam_scrutiny"] == "high":
            continue
        score, comps, matched = score_niche(n, args.model, state, pop, tiers)
        row = {"id": n["id"], "niche": n["name"], "score": score,
               **{f"c_{k}": round(v, 1) for k, v in comps.items()},
               "flags": ";".join(flags_for(n, args.model)), "geo_matched": ";".join(matched)}
        if pop:
            searches, leads, rev = potential(n, args.model, pop, tiers)
            row.update({"searches_mo": f"{searches[0]}-{searches[1]}",
                        "leads_mo": f"{leads[1]} ({leads[0]}-{leads[2]})",
                        "potential_usd_mo": f"{rev[1]} ({rev[0]}-{rev[2]})"})
        rent = n.get("rent_usd_month")
        ppc = n.get("ppc_payout_usd")
        row["market_rent"] = f"{rent[0]}-{rent[1]}" if rent else ""
        row["ppc_payout"] = f"{ppc[0]}-{ppc[1]}" if ppc else ""
        rows.append(row)
    rows.sort(key=lambda r: -r["score"])
    rows = rows[: args.top]

    if args.format == "json":
        out = json.dumps(rows, indent=2)
    elif args.format == "csv":
        if args.out:
            write_csv(args.out, rows)
            print(f"wrote {len(rows)} rows -> {args.out}")
            return
        import csv as _csv
        w = _csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        return
    else:
        head = [f"# Niche ranking - model: {args.model}", ""]
        if city_label or state:
            head.append(f"- Market: {city_label or state}" + (f" (population {fmt_int(pop)})" if pop else ""))
        head.append(f"- Risk tolerance: {args.risk_tolerance}" + ("" if args.risk_tolerance == "high"
                                                                  else " (higher-risk niches filtered out)"))
        head.append("- Scores use PRIORS from data/niches.json. Validate the shortlist with live keyword, SERP and offer data.")
        if pop:
            head.append(f"- Potential = searches x organic capture {ORGANIC_CAPTURE} x conversion {CONVERSION}"
                        + (f" x billable {BILLABLE} x payout" if args.model != "rank_and_rent" else
                           " x per-lead price (capped at market rent)") + ". Base = geometric mean of the band. "
                        "Order-of-magnitude only; Phase 3 replaces it with real search volume.")
        head.append("")
        headers = ["#", "Niche", "Score", "Value", "Demand", "Urgency", "Rankability", "Risk", "Flags"]
        if args.model == "rank_and_rent":
            headers.append("Market rent $/mo")
        else:
            headers.append("Payout $/call")
        if pop:
            headers += ["Searches/mo", "Leads/mo base (range)", "Potential $/mo base (range)"]
        table = []
        for i, r in enumerate(rows, 1):
            line = [i, f"{r['niche']} (`{r['id']}`)", r["score"], r["c_value"], r["c_demand"], r["c_urgency"],
                    r["c_rankability"], r["c_risk"], r["flags"].replace(";", ", ") or "-",
                    (r["market_rent"] if args.model == "rank_and_rent" else r["ppc_payout"]) or "-"]
            if pop:
                line += [r["searches_mo"], r["leads_mo"], r["potential_usd_mo"]]
            table.append(line)
        out = "\n".join(head) + "\n" + md_table(table, headers) + "\n"
    if args.out:
        write_text(args.out, out)
        print(f"wrote {len(rows)} rows -> {args.out}")
    else:
        print(out)


def show(args):
    niches, meta = load_niches()
    n = find_niche(niches, args.niche)
    if not n:
        sys.exit(f"unknown niche '{args.niche}'")
    rng = lambda r, f=fmt_money: f"{f(r[0])} - {f(r[1])}" if r else "n/a"  # noqa: E731
    tiers = meta["demand_tiers"][n["demand_tier"]]
    lines = [f"# {n['name']} (`{n['id']}`) - {n['category']}", "",
             f"- Model fit (0-10): rank & rent {n['model_fit']['rank_and_rent']}, pay-per-call "
             f"{n['model_fit']['pay_per_call']}, nationwide {n['model_fit']['nationwide']}",
             f"- Ticket: {rng(n['ticket_usd']) if n['ticket_usd'][1] else 'n/a (not a job-ticket business)'}",
             f"- Urgency: {n['urgency']} | Seasonality: {n['seasonality']} ({n['peak']})",
             f"- Demand tier: {n['demand_tier']} ({tiers['label']}; prior {tiers['searches_per_100k_residents_per_month'][0]}-"
             f"{tiers['searches_per_100k_residents_per_month'][1]} searches / 100k residents / month)",
             f"- SERP pressure: competition {n['competition_baseline']}, LSAs {n['lsa_presence']}, directories {n['directory_pressure']}",
             f"- Pay-per-call payout: {rng(n['ppc_payout_usd'])} per qualified call; buffer "
             f"{str(n['call_buffer_sec'][0]) + '-' + str(n['call_buffer_sec'][1]) + 's' if n['call_buffer_sec'] else 'n/a'}",
             f"- Market rent: {rng(n['rent_usd_month'])} / month | Per lead: {rng(n['per_lead_usd'])}",
             f"- Buyer density: {n['buyer_density']} | License sensitivity: {n['license_sensitivity']} | "
             f"Regulatory risk: {n['regulatory_risk']} | Spam scrutiny: {n['spam_scrutiny']}",
             f"- Favourable geo tags: {', '.join(n['geo_tags']) or 'location-agnostic'} | Market profile: "
             f"{n.get('market_profile', 'suburban')} (sets city_finder defaults)",
             f"- Tenant-mode schema type: `{n['schema_type']}`",
             f"- Sub-services: {', '.join(n['sub_services'])}",
             f"- Seed keywords: {', '.join(n['seed_keywords'])}",
             f"- Notes: {n['notes']}", ""]
    print("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("rank")
    r.add_argument("--model", choices=list(WEIGHTS), default="rank_and_rent")
    r.add_argument("--city", help='"City, ST" - adds geo fit and a rough potential band')
    r.add_argument("--state", help="state for geo fit when no city is chosen")
    r.add_argument("--population", type=int, help="override population for the potential band")
    r.add_argument("--risk-tolerance", choices=["low", "medium", "high"], default="medium")
    r.add_argument("--category", nargs="*", help="limit to categories (e.g. outdoor restoration mechanical)")
    r.add_argument("--top", type=int, default=25)
    r.add_argument("--format", choices=["md", "csv", "json"], default="md")
    r.add_argument("--out")
    s = sub.add_parser("show")
    s.add_argument("niche")
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("rank", "show", "-h", "--help"):
        argv = ["rank"] + list(argv)
    args = ap.parse_args(argv)
    {"rank": rank, "show": show}[args.cmd](args)


if __name__ == "__main__":
    main()
