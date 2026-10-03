#!/usr/bin/env python3
"""Find and rank US cities for a local lead-gen site, and map service areas.

Commands
  rank          Rank candidate cities (default command).
  service-area  List towns around a city, for service-area pages and GBP service areas.
  profile       Show one city's data, nearby towns and state tags.

Examples
  python3 scripts/city_finder.py rank --niche tree-service --min-pop 40000 --max-pop 400000 --top 25
  python3 scripts/city_finder.py rank --niche septic --states NC SC GA TN --sweet-spot 20000 120000
  python3 scripts/city_finder.py rank --niche foundation-repair --region South --format csv --out projects/x/data/cities.csv
  python3 scripts/city_finder.py service-area "Tulsa, OK" --radius 25 --min-pop 3000
  python3 scripts/city_finder.py profile "Boise, ID" --niche roofing

Scores are triage priors (size fit, geo fit, service-area cluster, independence from a big metro and,
with census_places.csv, household economics). They say nothing about SERP competition. Always run a
SERP audit on the shortlist.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (STATE_REGION, STATE_TAGS, find_niche, find_place, fmt_int, fmt_money,  # noqa: E402
                    haversine_mi, load_niches, load_places, md_table, normalize_state, parse_city_arg,
                    places_path, write_csv, write_text)

DEFAULT_SWEET_SPOT = (50000, 300000)
BEARINGS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
# Market profiles (niches.json "market_profile"): city population sweet spot and the ideal population living within
# the service-area radius (excluding the city itself).
PROFILES = {
    "rural": {"sweet": (15000, 120000), "cluster": (40000, 300000)},
    "suburban": {"sweet": (50000, 300000), "cluster": (150000, 900000)},
    "urban": {"sweet": (150000, 1000000), "cluster": (500000, 4000000)},
    "affluent": {"sweet": (40000, 400000), "cluster": (150000, 1500000)},
}


# --------------------------------------------------------------------------- spatial index
class Grid:
    """Bucket places into 0.5-degree cells so radius queries stay fast in pure Python."""

    def __init__(self, places, cell=0.5):
        self.cell = cell
        self.cells = {}
        for p in places:
            if p["lat"] is None or p["lon"] is None:
                continue
            self.cells.setdefault(self._key(p["lat"], p["lon"]), []).append(p)

    def _key(self, lat, lon):
        return (int(math.floor(lat / self.cell)), int(math.floor(lon / self.cell)))

    def near(self, lat, lon, radius_mi):
        dlat = radius_mi / 69.0
        dlon = radius_mi / max(1e-6, 69.0 * math.cos(math.radians(lat)))
        k0 = self._key(lat - dlat, lon - dlon)
        k1 = self._key(lat + dlat, lon + dlon)
        for i in range(k0[0], k1[0] + 1):
            for j in range(k0[1], k1[1] + 1):
                for p in self.cells.get((i, j), ()):
                    d = haversine_mi(lat, lon, p["lat"], p["lon"])
                    if d <= radius_mi:
                        yield p, d


def bearing(lat1, lon1, lat2, lon2):
    y = math.sin(math.radians(lon2 - lon1)) * math.cos(math.radians(lat2))
    x = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2))
         - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(lon2 - lon1)))
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return BEARINGS[int((deg + 22.5) // 45) % 8]


# --------------------------------------------------------------------------- scoring
def size_fit(pop, lo, hi):
    """1.0 at the geometric centre of [lo, hi], >= 0.85 anywhere inside, 0 at 4x outside the band."""
    if lo <= pop <= hi:
        centre = math.sqrt(lo * hi)
        half = math.log(hi / centre) or 1.0
        return 1.0 - 0.15 * abs(math.log(pop / centre)) / half
    edge = lo if pop < lo else hi
    return max(0.0, 0.85 * (1.0 - abs(math.log(pop / edge)) / math.log(4)))


def cluster_fit(cluster_pop, lo, hi):
    """Service-area population: too little = no room to grow, too much = metro-scale competition."""
    if cluster_pop <= 0:
        return 0.0
    if lo <= cluster_pop <= hi:
        return 1.0
    edge = lo if cluster_pop < lo else hi
    return max(0.0, 1.0 - abs(math.log(cluster_pop / edge)) / math.log(6))


def geo_fit(state, niche):
    if not niche or not niche.get("geo_tags"):
        return 0.5, []
    tags = STATE_TAGS.get(state, set())
    matched = [t for t in niche["geo_tags"] if t in tags]
    return len(matched) / len(niche["geo_tags"]), matched


def econ_fit(p, niche, medians):
    """0-1 from ACS economics when available; None when the dataset has no ACS columns."""
    parts = []
    if p.get("median_hh_income") and medians.get("income"):
        parts.append(min(1.0, p["median_hh_income"] / (1.5 * medians["income"])) * 1.0)
    if p.get("owner_occupied_pct") is not None:
        parts.append(min(1.0, p["owner_occupied_pct"] / 75.0))
    if p.get("sfh_detached_pct") is not None:
        parts.append(min(1.0, p["sfh_detached_pct"] / 75.0))
    tags = set((niche or {}).get("geo_tags", []))
    if "older_housing_stock" in tags and p.get("median_year_built"):
        parts.append(max(0.0, min(1.0, (2010 - p["median_year_built"]) / 50.0)))
    if "high_growth" in tags and p.get("growth_since_2020_pct") is not None:
        parts.append(max(0.0, min(1.0, p["growth_since_2020_pct"] / 15.0)))
    return sum(parts) / len(parts) if parts else None


def median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


def context_for(p, grid, radius, metro_radius=25):
    """Cluster population around p and the nearest much-larger city."""
    cluster_pop, towns = 0, 0
    nearest_big, nearest_d = None, None
    for q, d in grid.near(p["lat"], p["lon"], max(radius, metro_radius)):
        if q is p:
            continue
        if d <= radius:
            cluster_pop += q["population"]
            towns += 1
        if q["population"] >= 2 * p["population"] and q["population"] >= 150000 and d <= metro_radius:
            if nearest_d is None or d < nearest_d:
                nearest_big, nearest_d = q, d
    return cluster_pop, towns, nearest_big, nearest_d


def rank(args):
    places = load_places()
    niches, _ = load_niches()
    niche = None
    if args.niche:
        niche = find_niche(niches, args.niche)
        if not niche:
            sys.exit(f"unknown niche '{args.niche}' (see data/niches.json ids)")

    states = {normalize_state(s) for s in (args.states or [])} - {None}
    excl = {normalize_state(s) for s in (args.exclude_states or [])} - {None}
    profile = PROFILES[(niche or {}).get("market_profile", "suburban")]
    lo, hi = args.sweet_spot or profile["sweet"]
    c_lo, c_hi = profile["cluster"]
    args.profile_name = (niche or {}).get("market_profile", "suburban")
    grid = Grid(places)
    medians = {"income": median(p.get("median_hh_income") for p in places)}

    cands = []
    for p in places:
        if p["lat"] is None or p["population"] < args.min_pop or p["population"] > args.max_pop:
            continue
        if states and p["state"] not in states:
            continue
        if p["state"] in excl:
            continue
        if args.region and STATE_REGION.get(p["state"], "").lower() != args.region.lower():
            continue
        if args.min_income and (p.get("median_hh_income") or 0) < args.min_income:
            continue
        if args.min_owner_pct and (p.get("owner_occupied_pct") or 0) < args.min_owner_pct:
            continue
        cands.append(p)

    rows = []
    for p in cands:
        cluster_pop, towns, big, big_d = context_for(p, grid, args.radius)
        s_size = size_fit(p["population"], lo, hi)
        s_geo, matched = geo_fit(p["state"], niche)
        s_cluster = cluster_fit(cluster_pop, c_lo, c_hi)
        s_indep = 1.0 if big is None else (0.4 + 0.6 * min(1.0, big_d / 25.0))
        s_econ = econ_fit(p, niche, medians)
        weights = {"size": 0.35, "geo": 0.20 if niche else 0.0, "cluster": 0.15, "indep": 0.10,
                   "econ": 0.20 if s_econ is not None else 0.0}
        total_w = sum(weights.values())
        score = (weights["size"] * s_size + weights["geo"] * s_geo + weights["cluster"] * s_cluster
                 + weights["indep"] * s_indep + weights["econ"] * (s_econ or 0)) / total_w
        rows.append({
            "city": p["name"], "state": p["state"], "population": p["population"],
            "cluster_pop": cluster_pop, "towns_in_radius": towns,
            "near_metro": f"{big['name']} ({big_d:.0f} mi)" if big else "",
            "geo_tags_matched": ";".join(matched),
            "median_hh_income": p.get("median_hh_income") or "",
            "owner_occupied_pct": p.get("owner_occupied_pct") if p.get("owner_occupied_pct") is not None else "",
            "median_year_built": p.get("median_year_built") or "",
            "growth_since_2020_pct": p.get("growth_since_2020_pct") if p.get("growth_since_2020_pct") is not None else "",
            "score": round(100 * score, 1),
            "s_size": round(s_size, 2), "s_geo": round(s_geo, 2), "s_cluster": round(s_cluster, 2),
            "s_independence": round(s_indep, 2), "s_econ": "" if s_econ is None else round(s_econ, 2),
            "lat": p["lat"], "lon": p["lon"],
        })
    rows.sort(key=lambda r: -r["score"])
    if args.max_per_state:
        seen, capped = {}, []
        for r in rows:
            seen[r["state"]] = seen.get(r["state"], 0) + 1
            if seen[r["state"]] <= args.max_per_state:
                capped.append(r)
        rows = capped
    rows = rows[: args.top]
    emit(rows, args, header=_rank_header(niche, lo, hi, args))


def _rank_header(niche, lo, hi, args):
    src = os.path.basename(places_path())
    lines = [f"# City shortlist{' - ' + niche['name'] if niche else ''}", "",
             f"- Data: `{src}`" + ("" if src == "census_places.csv" else
                                    " (GeoNames starter; run scripts/fetch_census_data.py for official Census data + ACS economics)"),
             f"- Market profile: {getattr(args, 'profile_name', 'suburban')} | population filter "
             f"{fmt_int(args.min_pop)}-{fmt_int(args.max_pop)}; sweet spot {fmt_int(lo)}-{fmt_int(hi)}",
             f"- Cluster radius: {args.radius} mi (ideal service-area population depends on the profile)",
             "- Score = size fit, geo fit, service-area cluster, independence from a larger metro and ACS economics. "
             "This is a PRIOR and says nothing about SERP competition.", ""]
    return "\n".join(lines)


def emit(rows, args, header=""):
    if args.format == "json":
        text = json.dumps(rows, indent=2)
    elif args.format == "csv":
        if args.out:
            write_csv(args.out, rows)
            print(f"wrote {len(rows)} rows -> {args.out}")
            return
        import csv as _csv
        w = _csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()) if rows else ["empty"])
        w.writeheader()
        w.writerows(rows)
        return
    else:
        has_acs = any(r.get("median_hh_income") for r in rows)
        headers = ["#", "City", "Pop", "Cluster pop", "Towns", "Near metro", "Geo tags", "Score"]
        if has_acs:
            headers[7:7] = ["Med. income", "Owner %", "Yr built"]
        table = []
        for i, r in enumerate(rows, 1):
            line = [i, f"{r['city']}, {r['state']}", fmt_int(r["population"]), fmt_int(r["cluster_pop"]),
                    r["towns_in_radius"], r["near_metro"] or "-", r["geo_tags_matched"].replace(";", ", ") or "-",
                    r["score"]]
            if has_acs:
                line[7:7] = [fmt_money(r["median_hh_income"]) if r["median_hh_income"] else "-",
                             r["owner_occupied_pct"] if r["owner_occupied_pct"] != "" else "-",
                             r["median_year_built"] or "-"]
            table.append(line)
        text = (header + "\n" if header else "") + md_table(table, headers) + "\n"
    if args.out:
        write_text(args.out, text)
        print(f"wrote {len(rows)} rows -> {args.out}")
    else:
        print(text)


# --------------------------------------------------------------------------- service area
def service_area(args):
    places = load_places()
    name, st = parse_city_arg(args.city)
    center = find_place(places, name, st)
    if not center:
        sys.exit(f"city not found: {args.city}")
    grid = Grid(places)
    towns = []
    for q, d in grid.near(center["lat"], center["lon"], args.radius):
        if q is center or q["population"] < args.min_pop:
            continue
        towns.append({"town": q["name"], "state": q["state"], "population": q["population"],
                      "miles": round(d, 1), "direction": bearing(center["lat"], center["lon"], q["lat"], q["lon"])})
    # Prefer big AND close towns for dedicated pages: population discounted by distance.
    for t in towns:
        t["page_priority"] = round(t["population"] / (1 + t["miles"] / 10.0))
    towns.sort(key=lambda t: -t["page_priority"])
    if args.format in ("json", "csv"):
        args_rows = towns[: args.top]
        emit(args_rows, args)
        return
    lines = [f"# Service area around {center['name']}, {center['state']} (pop {fmt_int(center['population'])})", "",
             f"Radius {args.radius} mi, towns with population >= {fmt_int(args.min_pop)}. "
             "Sorted by page priority (population discounted by distance).", ""]
    table = [[i, f"{t['town']}, {t['state']}", fmt_int(t["population"]), t["miles"], t["direction"], fmt_int(t["page_priority"])]
             for i, t in enumerate(towns[: args.top], 1)]
    lines.append(md_table(table, ["#", "Town", "Pop", "Miles", "Dir", "Priority"]))
    picks = [t["town"] for t in towns[: args.pages]]
    lines += ["", f"Suggested `site.json` areas (top {args.pages}): " + json.dumps([center["name"]] + picks), "",
              "Only build a dedicated area page when you can write genuinely local content for that town "
              "(see content-engine skill). Otherwise list the town on the main Service Areas page."]
    text = "\n".join(lines) + "\n"
    if args.out:
        write_text(args.out, text)
        print(f"wrote -> {args.out}")
    else:
        print(text)


# --------------------------------------------------------------------------- profile
def profile(args):
    places = load_places()
    niches, _ = load_niches()
    name, st = parse_city_arg(args.city)
    p = find_place(places, name, st)
    if not p:
        sys.exit(f"city not found: {args.city}")
    grid = Grid(places)
    cluster_pop, towns, big, big_d = context_for(p, grid, args.radius)
    state_rank = 1 + sum(1 for q in places if q["state"] == p["state"] and q["population"] > p["population"])
    out = [f"# {p['name']}, {p['state']}", "",
           f"- Population: {fmt_int(p['population'])} ({p.get('population_source') or p.get('source', '')})",
           f"- Rank in state by population: #{state_rank}",
           f"- Within {args.radius} mi: {towns} towns, {fmt_int(cluster_pop)} people",
           f"- Larger metro within 25 mi: {big['name'] + ' (' + str(round(big_d)) + ' mi)' if big else 'none (independent market)'}",
           f"- State tags: {', '.join(sorted(STATE_TAGS.get(p['state'], []))) or '-'}"]
    for label, key, fmt in (("Median household income", "median_hh_income", fmt_money),
                            ("Owner-occupied", "owner_occupied_pct", lambda v: f"{v}%"),
                            ("Single-family detached", "sfh_detached_pct", lambda v: f"{v}%"),
                            ("Median home value", "median_home_value", fmt_money),
                            ("Median year built", "median_year_built", lambda v: str(int(v))),
                            ("Growth since 2020", "growth_since_2020_pct", lambda v: f"{v}%")):
        if p.get(key) not in (None, ""):
            out.append(f"- {label}: {fmt(p[key])}")
    if args.niche:
        n = find_niche(niches, args.niche)
        if n:
            s, matched = geo_fit(p["state"], n)
            out.append(f"- Geo fit for {n['name']}: {round(100 * s)}% (matched: {', '.join(matched) or 'none'}; "
                       f"wanted: {', '.join(n['geo_tags']) or 'none'})")
    print("\n".join(out) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    r = sub.add_parser("rank", help="rank candidate cities")
    r.add_argument("--niche", help="niche id or name from data/niches.json (enables geo fit)")
    r.add_argument("--min-pop", type=int, default=25000)
    r.add_argument("--max-pop", type=int, default=1000000)
    r.add_argument("--sweet-spot", type=int, nargs=2, metavar=("LO", "HI"))
    r.add_argument("--states", nargs="*")
    r.add_argument("--exclude-states", nargs="*")
    r.add_argument("--region", choices=["South", "West", "Midwest", "Northeast"])
    r.add_argument("--min-income", type=int, default=0, help="requires census_places.csv")
    r.add_argument("--min-owner-pct", type=float, default=0, help="requires census_places.csv")
    r.add_argument("--radius", type=float, default=20, help="service-area cluster radius in miles")
    r.add_argument("--max-per-state", type=int, default=0, help="diversify: cap results per state")
    r.add_argument("--top", type=int, default=30)
    r.add_argument("--format", choices=["md", "csv", "json"], default="md")
    r.add_argument("--out")

    s = sub.add_parser("service-area", help="towns around a city")
    s.add_argument("city", help='"City, ST"')
    s.add_argument("--radius", type=float, default=25)
    s.add_argument("--min-pop", type=int, default=2500)
    s.add_argument("--top", type=int, default=30)
    s.add_argument("--pages", type=int, default=8, help="how many towns to suggest for area pages")
    s.add_argument("--format", choices=["md", "csv", "json"], default="md")
    s.add_argument("--out")

    pr = sub.add_parser("profile", help="one city's profile")
    pr.add_argument("city")
    pr.add_argument("--niche")
    pr.add_argument("--radius", type=float, default=20)

    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("rank", "service-area", "profile", "-h", "--help"):
        argv = ["rank"] + list(argv)
    args = ap.parse_args(argv)
    {"rank": rank, "service-area": service_area, "profile": profile}[args.cmd](args)


if __name__ == "__main__":
    main()
