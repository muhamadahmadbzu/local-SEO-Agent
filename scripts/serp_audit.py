#!/usr/bin/env python3
"""Local SERP competition audit: fetch (DataForSEO) or record manually, then score difficulty.

Commands
  template  Print a blank manual-audit JSON to fill from a real (incognito, location-set) Google search.
  fetch     Pull a live organic SERP (+ optional Maps results) from DataForSEO and save the raw JSON.
  score     Score one or more audit files (manual JSON or DataForSEO raw) -> difficulty report.

Examples
  python3 scripts/serp_audit.py template --keyword "tree service tulsa" --city "Tulsa, OK" > projects/x/data/serp/tree-service-tulsa.json
  python3 scripts/serp_audit.py fetch --keyword "tree service tulsa" --city "Tulsa, OK" --maps --out-dir projects/x/data/serp
  python3 scripts/serp_audit.py score projects/x/data/serp/*.json --city "Tulsa, OK" --out projects/x/research/serp-audit.md

Difficulty is 0-100 (higher = harder). It blends top-10 organic composition (directories and marketplaces
are weak, national brands are strong), how many local competitors optimized for the city, map-pack
review depth, SERP-feature pressure (ads, LSAs, map pack, AI Overview) and, when supplied, domain
authority. Verdict bands: <35 easy, 35-55 moderate, 55-70 hard, >70 very hard.
"""
import argparse
import glob
import json
import os
import statistics
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA_DIR, STATE_NAMES, load_json, md_table, parse_city_arg, slugify,  # noqa: E402
                    write_text)

STRENGTH = {"directory": 0.25, "marketplace": 0.3, "ugc": 0.2, "government": 0.4, "local_business": 0.6,
            "lead_gen": 0.6, "national_brand": 0.9, "other": 0.5}
WEAK = {"directory", "marketplace", "ugc"}


def load_domain_lists():
    d = load_json(os.path.join(DATA_DIR, "serp_domains.json"))
    return {k: v for k, v in d.items() if not k.startswith("_")}


def classify(domain, lists):
    domain = (domain or "").lower()
    if domain.startswith("www."):
        domain = domain[4:]
    for kind in ("national_brand", "marketplace", "directory", "ugc"):
        for d in lists.get(kind, []):
            if domain == d or domain.endswith("." + d):
                return kind
    for suffix in lists.get("government", []):
        if domain.endswith(suffix):
            return "government"
    return "local_business"


def domain_of(url):
    try:
        return urlparse(url).netloc.lower()
    except ValueError:
        return ""


# --------------------------------------------------------------------------- template / fetch
def cmd_template(args):
    tpl = {
        "keyword": args.keyword,
        "location": args.city,
        "date": "YYYY-MM-DD",
        "device": "mobile",
        "how_collected": "manual: Google search with location set to the city (or DataForSEO). Record exactly what you see.",
        "features": {"ads_top": 0, "lsa": False, "local_pack": True, "ai_overview": False},
        "local_pack": [
            {"name": "", "rating": None, "reviews": None, "website": ""}
        ],
        "organic": [
            {"position": 1, "url": "", "title": "",
             "type": "auto | local_business | lead_gen | directory | marketplace | national_brand | ugc | government",
             "dr": None, "notes": ""}
        ],
    }
    print(json.dumps(tpl, indent=2))


def dfs_post(path, task):
    from keyword_tool import dfs_request  # reuse auth + retries
    return dfs_request(path, [task])


def cmd_fetch(args):
    city, st = parse_city_arg(args.city)
    loc = args.location_name or f"{city},{STATE_NAMES[st]},United States"
    os.makedirs(args.out_dir, exist_ok=True)
    task = {"keyword": args.keyword, "location_name": loc, "language_code": "en", "device": args.device,
            "depth": args.depth}
    body = dfs_post("/v3/serp/google/organic/live/advanced", task)
    base = slugify(args.keyword)
    path = os.path.join(args.out_dir, f"{base}.dfs-organic.json")
    with open(path, "w") as fh:
        json.dump(body, fh)
    print(f"saved {path}")
    if args.maps:
        mbody = dfs_post("/v3/serp/google/maps/live/advanced",
                         {"keyword": args.keyword, "location_name": loc, "language_code": "en", "depth": 20})
        mpath = os.path.join(args.out_dir, f"{base}.dfs-maps.json")
        with open(mpath, "w") as fh:
            json.dump(mbody, fh)
        print(f"saved {mpath}")


# --------------------------------------------------------------------------- normalize inputs
def from_dfs(body, lists):
    result = ((body.get("tasks") or [{}])[0].get("result") or [{}])[0]
    items = result.get("items") or []
    audit = {"keyword": result.get("keyword"), "location": str(result.get("location_code")),
             "date": (result.get("datetime") or "")[:10], "features": {}, "local_pack": [], "organic": []}
    types = [i.get("type") for i in items]
    audit["features"] = {
        "ads_top": sum(1 for i in items if i.get("type") == "paid" and (i.get("rank_absolute") or 99) <= 6),
        "lsa": "local_services" in types,
        "local_pack": "local_pack" in types or "map" in types,
        "ai_overview": "ai_overview" in types,
    }
    for i in items:
        if i.get("type") == "local_pack":
            r = i.get("rating") or {}
            audit["local_pack"].append({"name": i.get("title"), "rating": r.get("value"),
                                        "reviews": r.get("votes_count"), "website": i.get("domain") or ""})
        elif i.get("type") == "organic":
            audit["organic"].append({"position": i.get("rank_group"), "url": i.get("url"),
                                     "title": i.get("title"), "type": "auto", "dr": None})
    audit["organic"].sort(key=lambda o: o["position"] or 99)
    return audit


def merge_maps(audit, body):
    result = ((body.get("tasks") or [{}])[0].get("result") or [{}])[0]
    maps = [i for i in (result.get("items") or []) if i.get("type") == "maps_search"]
    audit["maps_top"] = [{"name": m.get("title"), "rating": (m.get("rating") or {}).get("value"),
                          "reviews": (m.get("rating") or {}).get("votes_count"), "category": m.get("category"),
                          "website": m.get("domain"), "claimed": m.get("is_claimed")} for m in maps[:10]]
    return audit


def load_audits(paths, lists):
    audits, maps_by_kw = [], {}
    for p in paths:
        body = load_json(p)
        if p.endswith(".dfs-maps.json"):
            maps_by_kw[os.path.basename(p).replace(".dfs-maps.json", "")] = body
            continue
        if "tasks" in body:
            a = from_dfs(body, lists)
            a["_file"] = os.path.basename(p).replace(".dfs-organic.json", "")
        else:
            a = body
            a["_file"] = os.path.basename(p).replace(".json", "")
        audits.append(a)
    for a in audits:
        if a["_file"] in maps_by_kw:
            merge_maps(a, maps_by_kw[a["_file"]])
    return audits


# --------------------------------------------------------------------------- scoring
def review_band(median_reviews):
    if median_reviews is None:
        return None
    for limit, val in ((25, 0.2), (100, 0.4), (300, 0.6), (800, 0.8)):
        if median_reviews < limit:
            return val
    return 1.0


def dr_band(drs):
    if not drs:
        return None
    m = statistics.median(drs)
    for limit, val in ((15, 0.2), (30, 0.5), (50, 0.8)):
        if m < limit:
            return val
    return 1.0


def score_audit(a, lists, city=None):
    organic = [o for o in a.get("organic", []) if o.get("url") or o.get("title")][:10]
    rows, weighted, wsum = [], 0.0, 0.0
    optimized, weak, brands = 0, 0, 0
    city_l = (city or "").lower()
    for o in organic:
        kind = o.get("type") or "auto"
        if kind == "auto" or kind not in STRENGTH:
            kind = classify(domain_of(o.get("url", "")), lists)
        pos = o.get("position") or len(rows) + 1
        w = 1.5 if pos <= 3 else (1.0 if pos <= 6 else 0.6)
        strength = STRENGTH[kind]
        city_in_title = bool(city_l and city_l in (o.get("title") or "").lower())
        if kind in ("local_business", "lead_gen") and city_in_title:
            strength += 0.1
            optimized += 1
        weak += kind in WEAK
        brands += kind == "national_brand"
        weighted += w * strength
        wsum += w
        rows.append([pos, domain_of(o.get("url", "")) or "-", kind, "yes" if city_in_title else "no", o.get("dr") or "-"])
    organic_strength = weighted / wsum if wsum else 0.5

    pack = a.get("local_pack") or []
    reviews = [p.get("reviews") for p in pack if isinstance(p.get("reviews"), (int, float))]
    maps_top = a.get("maps_top") or []
    if not reviews and maps_top:
        reviews = [m.get("reviews") for m in maps_top[:3] if isinstance(m.get("reviews"), (int, float))]
    med_reviews = statistics.median(reviews) if reviews else None
    s_pack = review_band(med_reviews)

    f = a.get("features") or {}
    pressure = min(1.0, 0.15 * min(int(f.get("ads_top") or 0), 4) + (0.3 if f.get("lsa") else 0)
                   + (0.2 if f.get("local_pack") else 0) + (0.2 if f.get("ai_overview") else 0))
    s_dr = dr_band([o["dr"] for o in organic if isinstance(o.get("dr"), (int, float))])

    comps = {"organic": (0.45, organic_strength), "optimized": (0.15, min(1.0, optimized / 5.0)),
             "pack": (0.15, s_pack), "pressure": (0.10, pressure), "authority": (0.15, s_dr)}
    active = {k: v for k, v in comps.items() if v[1] is not None}
    tw = sum(w for w, _ in active.values())
    difficulty = round(100 * sum(w * s for w, s in active.values()) / tw, 1)
    return {"keyword": a.get("keyword"), "difficulty": difficulty, "weak_in_top10": weak,
            "brands_in_top10": brands, "optimized_local": optimized, "median_pack_reviews": med_reviews,
            "features": f, "ctr_pressure": round(pressure, 2), "rows": rows,
            "components": {k: (None if v[1] is None else round(v[1], 2)) for k, v in comps.items()},
            "maps_top": maps_top}


def verdict(d):
    if d < 35:
        return "EASY - weak SERP, rank-and-rent friendly"
    if d < 55:
        return "MODERATE - beatable with strong local content + a few local links in ~3-6 months"
    if d < 70:
        return "HARD - needs real authority/links; expect 6-12 months"
    return "VERY HARD - avoid for rank & rent unless you have a structural edge"


def cmd_score(args):
    lists = load_domain_lists()
    paths = []
    for p in args.files:
        paths.extend(sorted(glob.glob(p)) or [p])
    audits = load_audits(paths, lists)
    if not audits:
        sys.exit("no audit files")
    city = parse_city_arg(args.city)[0] if args.city else None
    results = [score_audit(a, lists, city) for a in audits]
    avg = round(sum(r["difficulty"] for r in results) / len(results), 1)
    lines = [f"# SERP competition audit{' - ' + args.city if args.city else ''}", "",
             f"**Average difficulty: {avg}/100 - {verdict(avg)}**", "",
             md_table([[r["keyword"], r["difficulty"], r["weak_in_top10"], r["brands_in_top10"], r["optimized_local"],
                        r["median_pack_reviews"] if r["median_pack_reviews"] is not None else "-",
                        ", ".join(k for k, v in (r["features"] or {}).items() if v) or "-", r["ctr_pressure"]]
                       for r in results],
                      ["Keyword", "Difficulty", "Weak results (top 10)", "National brands", "City-optimized locals",
                       "Median pack reviews", "SERP features", "CTR pressure"]), "",
             "Reading it: 4+ weak results (directories/marketplaces/UGC) in the top 10 means local businesses have weak "
             "sites, which is the classic rank-and-rent opening. National brands and many city-optimized local "
             "pages mean real competition. CTR pressure near 1.0 means ads, LSAs, the map pack and AI Overviews "
             "take most clicks before organic result #1, so discount the traffic model.", ""]
    for r in results:
        lines += [f"## {r['keyword']} - {r['difficulty']}/100", "",
                  f"Components (0-1): {r['components']}", "",
                  md_table(r["rows"], ["Pos", "Domain", "Type", "City in title", "DR"]) if r["rows"] else "_no organic rows_", ""]
        if r["maps_top"]:
            lines += ["Top Maps results:", "",
                      md_table([[m["name"], m["rating"], m["reviews"], m["category"], m["website"] or "-"]
                                for m in r["maps_top"][:5]], ["Business", "Rating", "Reviews", "Category", "Website"]), ""]
    lines += ["_Classification uses data/serp_domains.json. Unknown domains default to local_business; correct "
              "misclassifications in the audit JSON (`type`) and re-score._"]
    text = "\n".join(lines) + "\n"
    if args.out:
        write_text(args.out, text)
        print(f"wrote {args.out} (avg difficulty {avg})")
    else:
        print(text)
    if args.json:
        print(json.dumps({"average_difficulty": avg, "verdict": verdict(avg),
                          "keywords": [{k: v for k, v in r.items() if k != "rows"} for r in results]}, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template")
    t.add_argument("--keyword", required=True)
    t.add_argument("--city", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--keyword", required=True)
    f.add_argument("--city", required=True)
    f.add_argument("--location-name")
    f.add_argument("--device", default="mobile", choices=["mobile", "desktop"])
    f.add_argument("--depth", type=int, default=20)
    f.add_argument("--maps", action="store_true")
    f.add_argument("--out-dir", required=True)
    s = sub.add_parser("score")
    s.add_argument("files", nargs="+")
    s.add_argument("--city")
    s.add_argument("--out")
    s.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    {"template": cmd_template, "fetch": cmd_fetch, "score": cmd_score}[args.cmd](args)


if __name__ == "__main__":
    main()
