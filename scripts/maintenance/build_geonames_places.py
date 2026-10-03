#!/usr/bin/env python3
"""Rebuild the starter dataset data/us_places.csv from GeoNames (via the
`geonamescache` PyPI package, MIT; data CC BY 4.0 GeoNames).

This is the *fallback* dataset that ships with the repo so the system works
offline. The authoritative dataset is data/census_places.csv, produced by
scripts/fetch_census_data.py (official Census PEP + ACS + Gazetteer).

Usage:
    pip install geonamescache
    python3 scripts/maintenance/build_geonames_places.py
    # or point at an extracted cities1000.json:
    python3 scripts/maintenance/build_geonames_places.py --json path/to/cities1000.json
"""
import argparse
import csv
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data", "us_places.csv")

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


def haversine_mi(lat1, lon1, lat2, lon2):
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_cities(json_path):
    if json_path:
        with open(json_path, encoding="utf-8") as fh:
            return json.load(fh)
    try:
        import geonamescache  # type: ignore
    except ImportError:
        sys.exit("geonamescache not installed: pip install geonamescache (or pass --json)")
    return geonamescache.GeonamesCache(min_city_population=1000).get_cities()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", help="path to a geonamescache cities*.json file")
    ap.add_argument("--min-pop", type=int, default=1000)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    cities = load_cities(args.json)
    rows = []
    for c in cities.values():
        if c.get("countrycode") != "US":
            continue
        st = c.get("admin1code")
        if st not in STATE_NAMES:
            continue  # territories / unknown
        pop = int(c.get("population") or 0)
        if pop < args.min_pop:
            continue
        rows.append({
            "name": c["name"].strip(),
            "state": st,
            "state_name": STATE_NAMES[st],
            "population": pop,
            "lat": round(float(c["latitude"]), 5),
            "lon": round(float(c["longitude"]), 5),
            "timezone": c.get("timezone", ""),
            "geonameid": c.get("geonameid", ""),
        })

    # De-duplicate same name+state records that are the same place (GeoNames
    # sometimes carries a city and an overlapping CDP/section). Keep the most
    # populous record when two share a name+state and sit within 15 miles.
    rows.sort(key=lambda r: -r["population"])
    kept = []
    by_key = {}
    for r in rows:
        key = (r["name"].lower(), r["state"])
        dup = False
        for k in by_key.get(key, []):
            if haversine_mi(r["lat"], r["lon"], k["lat"], k["lon"]) < 15:
                dup = True
                break
        if dup:
            continue
        by_key.setdefault(key, []).append(r)
        kept.append(r)

    kept.sort(key=lambda r: (r["state"], -r["population"], r["name"]))
    fields = ["name", "state", "state_name", "population", "lat", "lon", "timezone", "geonameid", "source"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in kept:
            r["source"] = "geonames"
            w.writerow(r)
    print(f"wrote {len(kept)} places (dropped {len(rows) - len(kept)} duplicates) -> {args.out}")


if __name__ == "__main__":
    main()
