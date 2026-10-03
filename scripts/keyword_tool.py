#!/usr/bin/env python3
"""Keyword research for local lead-gen sites: expand, get volumes, cluster into pages, report.

Commands
  expand     Generate the keyword universe for a niche and city (plus service-area towns).
  volume     Attach search volume and CPC. Providers:
               dataforseo  live Google Ads data (env DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD)
               csv         import a Google Keyword Planner / Ahrefs / Semrush export
               estimate    population-share estimate from a national-volume CSV (clearly labeled)
  cluster    Map keywords to pages (home, service, area, cost guide, blog) -> keyword map
  report     Demand summary: cluster volume, CPC, "ads value", traffic and leads by ranking scenario
  locations  Look up DataForSEO location names (needs credentials)

Typical flow
  python3 scripts/keyword_tool.py expand --niche tree-service --city "Tulsa, OK" --areas 8 --out projects/tulsa-tree/data/keywords.csv
  python3 scripts/keyword_tool.py volume --provider dataforseo --in projects/tulsa-tree/data/keywords.csv --city "Tulsa, OK"
  python3 scripts/keyword_tool.py cluster --in projects/tulsa-tree/data/keywords.csv --out projects/tulsa-tree/data/keyword_map.md
  python3 scripts/keyword_tool.py report --in projects/tulsa-tree/data/keywords.csv --niche tree-service --out projects/tulsa-tree/research/keyword-report.md

Without API credentials: export Keyword Planner ideas for the city (Location = the city, Language = English),
then `volume --provider csv --file export.csv`. Never invent volumes. Unknown stays blank.
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (STATE_NAMES, find_niche, find_place, fmt_int, fmt_money, load_niches,  # noqa: E402
                    load_places, md_table, parse_city_arg, read_csv, slugify, write_csv, write_text)

DFS_BASE = "https://api.dataforseo.com"
US_LOCATION_CODE = 2840
FIELDS = ["keyword", "cluster", "page_type", "intent", "geo", "search_volume", "cpc", "competition",
          "low_bid", "high_bid", "trend", "source"]

# Organic CTR by position on local-intent SERPs (ads + LSAs + map pack push organic down).
# Conservative blend of public CTR studies; near-me queries get NEAR_ME_FACTOR because the map pack dominates.
LOCAL_CTR = {1: 0.15, 2: 0.09, 3: 0.06, 4: 0.04, 5: 0.03, 6: 0.02, 7: 0.015, 8: 0.012, 9: 0.01, 10: 0.01}
NEAR_ME_FACTOR = 0.6
SCENARIOS = {"conservative": {"pos": 7, "cvr": 0.06}, "base": {"pos": 4, "cvr": 0.10},
             "strong": {"pos": 2, "cvr": 0.14}}


# --------------------------------------------------------------------------- expand
KEEP_AND = ("pier & beam", "tile & grout", "heating & cooling", "fire & smoke", "smoke & fire", "fire & water",
            "nuts & bolts")


def service_variants(name):
    """'Tree Trimming & Pruning' -> ['tree trimming', 'tree pruning'];
    'Oven & Stove Repair' -> ['oven repair', 'stove repair']; plain names pass through."""
    name = re.sub(r"\(.*?\)", "", name.lower()).strip()
    for compound in KEEP_AND:
        name = name.replace(compound, compound.replace(" & ", " and "))
    if " and " in name and any(c.replace(" & ", " and ") in name for c in KEEP_AND):
        return [name]
    parts = [p.strip() for p in re.split(r"\s+&\s+|\s+and\s+|\s*/\s*", name) if p.strip()]
    if len(parts) < 2:
        return [name]
    first, out = parts[0], []
    for later in parts[1:]:
        lw, fw = later.split(), first.split()
        if len(lw) == 1 and len(fw) >= 2:
            out.append(" ".join(fw[:-1] + lw))          # tree trimming & pruning -> tree pruning
        else:
            out.append(later)
    if len(first.split()) == 1 and len(parts[-1].split()) >= 2:
        first = f"{first} {parts[-1].split()[-1]}"      # oven & stove repair -> oven repair
    return [first] + out


def build_keywords(niche, city, state, towns, extra_seeds=()):
    st = state.lower()
    c = city.lower()
    seeds = [s.lower() for s in list(niche["seed_keywords"]) + list(extra_seeds)]
    subs = [s.lower() for s in niche["sub_services"]]
    emergency = niche["urgency"] in ("emergency", "mixed")
    kws = {}

    def add(kw, cluster, page_type, intent, geo):
        kw = re.sub(r"\s+", " ", kw).strip()
        if kw and kw not in kws:
            kws[kw] = {"keyword": kw, "cluster": cluster, "page_type": page_type, "intent": intent, "geo": geo}

    core = seeds[0]
    for s in seeds:
        add(s, "core", "home", "transactional", "implicit-local")
        add(f"{s} near me", "core", "home", "transactional", "near-me")
        add(f"{s} {c}", "core", "home", "transactional", "city")
        add(f"{s} {c} {st}", "core", "home", "transactional", "city")
        add(f"{s} in {c}", "core", "home", "transactional", "city")
        add(f"best {s} {c}", "core", "home", "commercial", "city")
        add(f"{s} cost", "cost", "cost", "commercial", "implicit-local")
        add(f"{s} cost {c}", "cost", "cost", "commercial", "city")
        if emergency:
            add(f"emergency {s} {c}", "emergency", "service", "transactional", "city")
            add(f"24 hour {s} {c}", "emergency", "service", "transactional", "city")
            add(f"emergency {s} near me", "emergency", "service", "transactional", "near-me")
    add(f"affordable {core} {c}", "core", "home", "commercial", "city")
    add(f"{core} companies {c}", "core", "home", "transactional", "city")
    add(f"how much does {core} cost", "cost", "cost", "informational", "none")
    for sub in subs:
        cl = slugify(sub)
        for i, kw in enumerate(service_variants(sub)):
            add(kw, cl, "service", "transactional", "implicit-local")
            add(f"{kw} {c}", cl, "service", "transactional", "city")
            add(f"{kw} near me", cl, "service", "transactional", "near-me")
            if i == 0:
                add(f"{kw} cost", cl, "cost", "commercial", "implicit-local")
    for t in towns:
        tl = t.lower()
        add(f"{core} {tl}", f"area-{slugify(t)}", "area", "transactional", "town")
        add(f"{core} {tl} {st}", f"area-{slugify(t)}", "area", "transactional", "town")
        if len(seeds) > 1:
            add(f"{seeds[1]} {tl}", f"area-{slugify(t)}", "area", "transactional", "town")
    return list(kws.values())


def cmd_expand(args):
    niches, _ = load_niches()
    niche = find_niche(niches, args.niche)
    if not niche:
        sys.exit(f"unknown niche '{args.niche}'")
    city, st = parse_city_arg(args.city)
    if not st:
        sys.exit("--city must include a state, e.g. 'Tulsa, OK'")
    towns = list(args.towns or [])
    if args.areas and not towns:
        from city_finder import Grid  # local import: heavy only when needed
        places = load_places()
        center = find_place(places, city, st)
        if center:
            grid = Grid(places)
            near = [(q, d) for q, d in grid.near(center["lat"], center["lon"], args.radius)
                    if q is not center and q["population"] >= args.min_town_pop]
            near.sort(key=lambda qd: -qd[0]["population"] / (1 + qd[1] / 10.0))
            towns = [q["name"] for q, _ in near[: args.areas]]
    rows = build_keywords(niche, city, st, towns, args.seed or ())
    for r in rows:
        r.update({k: "" for k in FIELDS if k not in r})
    write_csv(args.out, rows, FIELDS)
    print(f"wrote {len(rows)} keywords ({len(towns)} towns: {', '.join(towns) or '-'}) -> {args.out}")


# --------------------------------------------------------------------------- volume providers
def dfs_request(path, payload=None, method="POST"):
    login, pwd = os.environ.get("DATAFORSEO_LOGIN"), os.environ.get("DATAFORSEO_PASSWORD")
    if not login or not pwd:
        sys.exit("Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD (https://app.dataforseo.com/api-access) "
                 "or use --provider csv with a Keyword Planner export.")
    token = base64.b64encode(f"{login}:{pwd}".encode()).decode()
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(DFS_BASE + path, data=data, method=method,
                                 headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode())
            if body.get("status_code") != 20000:
                raise RuntimeError(f"DataForSEO error {body.get('status_code')}: {body.get('status_message')}")
            return body
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise RuntimeError("DataForSEO request failed after retries")


def location_name_for(city, st):
    return f"{city},{STATE_NAMES[st]},United States"


def dfs_volumes(keywords, location_name=None, location_code=None, cache_dir=None):
    out = {}
    for i in range(0, len(keywords), 1000):
        chunk = keywords[i:i + 1000]
        task = {"keywords": chunk, "language_code": "en"}
        if location_code:
            task["location_code"] = location_code
        else:
            task["location_name"] = location_name
        body = dfs_request("/v3/keywords_data/google_ads/search_volume/live", [task])
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            tag = slugify(location_name or str(location_code))
            with open(os.path.join(cache_dir, f"dfs_volume_{tag}_{i // 1000}.json"), "w") as fh:
                json.dump(body, fh)
        for t in body.get("tasks", []):
            if t.get("status_code") != 20000:
                raise RuntimeError(f"task error {t.get('status_code')}: {t.get('status_message')}")
            for item in t.get("result") or []:
                trend = [m.get("search_volume") for m in (item.get("monthly_searches") or [])]
                out[item["keyword"].lower()] = {
                    "search_volume": item.get("search_volume"),
                    "cpc": item.get("cpc"),
                    "competition": item.get("competition"),
                    "low_bid": item.get("low_top_of_page_bid"),
                    "high_bid": item.get("high_top_of_page_bid"),
                    "trend": "|".join("" if v is None else str(v) for v in reversed(trend)),
                }
    return out


VOL_COLS = ["avg. monthly searches", "search volume", "volume", "avg monthly searches", "searches",
            "monthly searches", "search_volume"]
CPC_COLS = ["top of page bid (high range)", "cpc", "cpc (usd)", "avg. cpc", "cost per click", "high_bid"]
KW_COLS = ["keyword", "keywords", "query", "search term"]


def _find_col(header, options):
    low = {h.lower().strip(): h for h in header}
    for o in options:
        if o in low:
            return low[o]
    for h in header:
        if any(o in h.lower() for o in options):
            return h
    return None


def _one_number(s):
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([km]?)$", s.strip(), re.I)
    if not m:
        return None
    return float(m.group(1)) * {"k": 1000, "m": 1000000}.get(m.group(2).lower(), 1)


def parse_number(v):
    """'1,300' -> 1300; '$4.50' -> 4.5; '2.4K' -> 2400; KWP bucket '1K - 10K' -> 3162 (geometric mean)."""
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("$", "")
    if not s or s in ("-", "--"):
        return None
    parts = re.split(r"\s*[-–—]\s*", s)
    if len(parts) == 2 and all(parts):
        lo, hi = _one_number(parts[0]), _one_number(parts[1])
        if lo is not None and hi is not None:
            return round((max(lo, 1) * hi) ** 0.5)
    one = _one_number(s)
    if one is not None:
        return round(one, 2) if one % 1 else int(one)
    return None


def read_export(path):
    """Read KWP (UTF-16 TSV with 2 title rows), Ahrefs or Semrush CSV exports."""
    with open(path, "rb") as fh:
        raw = fh.read()
    text = None
    for enc in ("utf-16", "utf-8-sig", "latin-1"):
        try:
            text = raw.decode(enc)
            if "\x00" not in text:
                break
        except UnicodeDecodeError:
            continue
    lines = text.splitlines()
    delim = "\t" if lines and lines[0].count("\t") >= lines[0].count(",") else ","
    start = 0
    for i, line in enumerate(lines[:10]):
        cells = [c.strip().strip('"').lower() for c in line.split(delim)]
        if any(k in cells for k in KW_COLS):
            start = i
            break
    import csv as _csv
    reader = _csv.DictReader(lines[start:], delimiter=delim)
    rows = list(reader)
    header = reader.fieldnames or []
    kc, vc, cc = _find_col(header, KW_COLS), _find_col(header, VOL_COLS), _find_col(header, CPC_COLS)
    if not kc or not vc:
        sys.exit(f"could not find keyword/volume columns in {path}: {header}")
    out = {}
    for r in rows:
        kw = (r.get(kc) or "").strip().lower()
        if kw:
            out[kw] = {"search_volume": parse_number(r.get(vc)), "cpc": parse_number(r.get(cc)) if cc else None}
    return out


def cmd_volume(args):
    rows = read_csv(args.inp)
    kws = [r["keyword"] for r in rows]
    if args.provider == "dataforseo":
        if args.dry_run:
            print(json.dumps([{"keywords": kws[:5] + (["..."] if len(kws) > 5 else []), "language_code": "en",
                               "location_name": args.location_name or "(from --city)"}], indent=2))
            return
        loc_name = args.location_name
        if not loc_name and not args.location_code:
            city, st = parse_city_arg(args.city or "")
            if not st:
                sys.exit("give --city 'City, ST', --location-name or --location-code")
            loc_name = location_name_for(city, st)
        data = dfs_volumes(kws, loc_name, args.location_code, cache_dir=args.cache_dir)
        source = f"dataforseo:{loc_name or args.location_code}"
    elif args.provider == "csv":
        data = read_export(args.file)
        source = f"csv:{os.path.basename(args.file)}"
    else:  # estimate
        if not args.file or not args.population:
            sys.exit("--provider estimate needs --file national.csv (keyword,volume[,cpc]) and --population")
        national = read_export(args.file)
        share = args.population / args.us_population
        data = {}
        for kw, v in national.items():
            if v["search_volume"] is None:
                continue
            factor = args.local_factor if not re.search(r"\b(near me|cost|how|what|why)\b", kw) else 1.0
            data[kw] = {"search_volume": round(v["search_volume"] * share * factor), "cpc": v.get("cpc")}
        source = f"ESTIMATE:pop-share({args.population}/{args.us_population})"
    hit = 0
    for r in rows:
        d = data.get(r["keyword"].lower())
        if d:
            hit += 1
            for k in ("search_volume", "cpc", "competition", "low_bid", "high_bid", "trend"):
                if d.get(k) is not None:
                    r[k] = d[k]
            r["source"] = source
    if args.include_new:
        known = {r["keyword"].lower() for r in rows}
        for kw, d in data.items():
            if kw not in known and (d.get("search_volume") or 0) >= args.min_volume:
                rows.append({"keyword": kw, "cluster": "imported", "page_type": "", "intent": "", "geo": "",
                             "search_volume": d.get("search_volume"), "cpc": d.get("cpc") or "", "source": source})
    write_csv(args.out or args.inp, rows, FIELDS)
    print(f"matched {hit}/{len(kws)} keywords from {source} -> {args.out or args.inp}")


def cmd_locations(args):
    body = dfs_request(f"/v3/keywords_data/google_ads/locations/{args.country}", method="GET")
    q = args.query.lower()
    for t in body.get("tasks", []):
        for loc in t.get("result") or []:
            if q in loc.get("location_name", "").lower():
                print(f"{loc.get('location_code')}\t{loc.get('location_type')}\t{loc.get('location_name')}")


# --------------------------------------------------------------------------- cluster & report
def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def cmd_cluster(args):
    rows = read_csv(args.inp)
    pages = {}
    for r in rows:
        key = (r.get("page_type") or "blog", r.get("cluster") or "misc")
        pages.setdefault(key, []).append(r)
    order = {"home": 0, "service": 1, "emergency": 1, "area": 2, "cost": 3, "blog": 4}
    lines = ["# Keyword map", "",
             "One page per row. The primary keyword is the highest-volume keyword in the cluster. A page targets "
             "its cluster, never a keyword owned by another page (no cannibalization).", ""]
    table = []
    for (ptype, cluster), items in sorted(pages.items(), key=lambda kv: (order.get(kv[0][0], 9), kv[0][1])):
        items.sort(key=lambda r: -(num(r.get("search_volume")) or 0))
        vol = sum(num(r.get("search_volume")) or 0 for r in items)
        has_vol = any(num(r.get("search_volume")) is not None for r in items)
        primary = items[0]["keyword"]
        secondary = ", ".join(r["keyword"] for r in items[1:6])
        table.append([ptype, cluster, primary, secondary or "-", fmt_int(vol) if has_vol else "n/a"])
    lines.append(md_table(table, ["Page type", "Cluster", "Primary keyword", "Secondary keywords", "Cluster volume"]))
    write_text(args.out, "\n".join(lines) + "\n")
    print(f"wrote {len(table)} page targets -> {args.out}")


def scenario_table(rows):
    """Per scenario: visits, leads and the Google Ads cost of buying the same clicks."""
    out = []
    for name, sc in SCENARIOS.items():
        clicks = value = 0.0
        for r in rows:
            v = num(r.get("search_volume")) or 0
            ctr = LOCAL_CTR[sc["pos"]] * (NEAR_ME_FACTOR if "near me" in r["keyword"] else 1.0)
            cpc = num(r.get("cpc")) or num(r.get("high_bid")) or 0
            clicks += v * ctr
            value += v * ctr * cpc
        out.append((name, sc["pos"], clicks, clicks * sc["cvr"], sc["cvr"], value))
    return out


def cmd_report(args):
    rows = read_csv(args.inp)
    with_vol = [r for r in rows if num(r.get("search_volume")) is not None]
    total = sum(num(r["search_volume"]) for r in with_vol)
    cpcs = sorted(c for c in (num(r.get("cpc")) or num(r.get("high_bid")) for r in with_vol) if c)
    sources = sorted({r.get("source", "") for r in with_vol if r.get("source")})
    estimate = any(s.startswith("ESTIMATE") for s in sources)
    lines = [f"# Keyword demand report{' - ' + args.title if args.title else ''}", "",
             f"- Keywords: {len(rows)} ({len(with_vol)} with volume data)",
             f"- Volume source(s): {', '.join(sources) or 'NONE - run keyword_tool.py volume first'}"]
    if estimate:
        lines.append("- **WARNING:** volumes are population-share ESTIMATES, not measured data. Not valid for a GO decision.")
    lines += [f"- Total monthly searches (cluster): **{fmt_int(total)}**",
              f"- Median CPC: {fmt_money(cpcs[len(cpcs) // 2], 2) if cpcs else 'n/a'} | "
              f"Max CPC: {fmt_money(cpcs[-1], 2) if cpcs else 'n/a'}", ""]
    lines += ["## Traffic and leads by ranking scenario", "",
              md_table([[n, f"avg #{p}", fmt_int(c), f"{l:.1f}", f"{int(cvr * 100)}%", fmt_money(val)]
                        for n, p, c, l, cvr, val in scenario_table(with_vol)],
                       ["Scenario", "Position", "Visits/mo", "Leads/mo", "Conv. rate", "Ads-equivalent $/mo"]), "",
              f"CTR model: {LOCAL_CTR} (organic on local SERPs), near-me x{NEAR_ME_FACTOR}. "
              "Ads-equivalent = what the same clicks would cost on Google Ads (sum of clicks x CPC). It anchors "
              "rent pricing. Feed the leads range into scripts/lead_economics.py.", ""]
    by_cluster = {}
    for r in with_vol:
        by_cluster.setdefault(r.get("cluster") or "misc", 0)
        by_cluster[r.get("cluster") or "misc"] += num(r["search_volume"])
    lines += ["## Volume by cluster", "",
              md_table([[k, fmt_int(v)] for k, v in sorted(by_cluster.items(), key=lambda kv: -kv[1])],
                       ["Cluster", "Monthly searches"]), ""]
    top = sorted(with_vol, key=lambda r: -num(r["search_volume"]))[: args.top]
    lines += ["## Top keywords", "",
              md_table([[r["keyword"], fmt_int(r["search_volume"]),
                         fmt_money(num(r.get("cpc")) or num(r.get("high_bid")), 2) if (num(r.get("cpc")) or num(r.get("high_bid"))) else "-",
                         r.get("page_type", ""), r.get("geo", "")] for r in top],
                       ["Keyword", "Volume", "CPC", "Page", "Geo"]), ""]
    trends = [r for r in with_vol if r.get("trend")]
    if trends:
        months = None
        agg = []
        for r in trends:
            vals = [num(x) or 0 for x in r["trend"].split("|")]
            if months is None:
                months = len(vals)
                agg = [0.0] * months
            for i, v in enumerate(vals[:months]):
                agg[i] += v
        peak = max(agg) or 1
        lines += ["## Seasonality (last 12 months, oldest first, all keywords)", "",
                  " ".join(f"{int(100 * v / peak)}%" for v in agg), ""]
    if args.niche:
        niches, _ = load_niches()
        n = find_niche(niches, args.niche)
        if n:
            lines += [f"Prior for {n['name']}: demand tier {n['demand_tier']}. Compare the measured total above "
                      "with the tier's per-100k prior and flag large gaps to the war room.", ""]
    write_text(args.out, "\n".join(lines))
    print(f"wrote report -> {args.out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("expand")
    e.add_argument("--niche", required=True)
    e.add_argument("--city", required=True)
    e.add_argument("--towns", nargs="*", help="explicit service-area towns")
    e.add_argument("--areas", type=int, default=6, help="auto-pick N nearby towns (0 = none)")
    e.add_argument("--radius", type=float, default=25)
    e.add_argument("--min-town-pop", type=int, default=5000)
    e.add_argument("--seed", nargs="*", help="extra seed keywords")
    e.add_argument("--out", required=True)

    v = sub.add_parser("volume")
    v.add_argument("--in", dest="inp", required=True)
    v.add_argument("--out")
    v.add_argument("--provider", choices=["dataforseo", "csv", "estimate"], required=True)
    v.add_argument("--city")
    v.add_argument("--location-name")
    v.add_argument("--location-code", type=int)
    v.add_argument("--file", help="export CSV (csv provider) or national-volume CSV (estimate provider)")
    v.add_argument("--population", type=int)
    v.add_argument("--us-population", type=int, default=340000000)
    v.add_argument("--local-factor", type=float, default=1.0,
                   help="estimate: multiplier for non-near-me keywords (default 1.0)")
    v.add_argument("--include-new", action="store_true", help="append keywords found only in the source")
    v.add_argument("--min-volume", type=int, default=10)
    v.add_argument("--cache-dir")
    v.add_argument("--dry-run", action="store_true")

    c = sub.add_parser("cluster")
    c.add_argument("--in", dest="inp", required=True)
    c.add_argument("--out", required=True)

    r = sub.add_parser("report")
    r.add_argument("--in", dest="inp", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--niche")
    r.add_argument("--title")
    r.add_argument("--top", type=int, default=25)

    lo = sub.add_parser("locations")
    lo.add_argument("query")
    lo.add_argument("--country", default="us")

    args = ap.parse_args(argv)
    {"expand": cmd_expand, "volume": cmd_volume, "cluster": cmd_cluster, "report": cmd_report,
     "locations": cmd_locations}[args.cmd](args)


if __name__ == "__main__":
    main()
