#!/usr/bin/env python3
"""Build data/census_places.csv from official US Census Bureau sources.

Joins three public datasets on the place GEOID (state FIPS + place FIPS):
  1. Population Estimates Program (PEP) "SUB-EST" city & town totals (latest vintage)
  2. American Community Survey 5-year estimates (API) - income, ownership, home value, housing age
  3. Gazetteer place file - internal point lat/lon and land area

Output covers incorporated places AND Census Designated Places (CDPs - many big
suburbs are CDPs, e.g. Brandon FL, Columbia MD). Run it on any machine with open
internet. It needs no API key; set CENSUS_API_KEY to raise the API rate limit.

Usage:
    python3 scripts/fetch_census_data.py                 # auto-detect newest vintages
    python3 scripts/fetch_census_data.py --min-pop 2500
    python3 scripts/fetch_census_data.py --pep-file sub-est2024.csv --acs-file acs.json --gaz-file gaz.txt   # offline
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR, STATE_ABBR_BY_FIPS, STATE_NAMES  # noqa: E402

RAW_DIR = os.path.join(DATA_DIR, "raw")
OUT = os.path.join(DATA_DIR, "census_places.csv")

PEP_URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-{v}/cities/totals/sub-est{v}.csv"
ACS_URL = "https://api.census.gov/data/{y}/acs/acs5"
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/{y}_Gazetteer/{y}_Gaz_place_national.zip"

ACS_VARS = {
    "B01003_001E": "acs_population",
    "B19013_001E": "median_hh_income",
    "B25003_001E": "occupied_units",
    "B25003_002E": "owner_occupied_units",
    "B25077_001E": "median_home_value",
    "B25035_001E": "median_year_built",
    "B25024_001E": "units_in_structure_total",
    "B25024_002E": "single_family_detached_units",
    "B25001_001E": "housing_units",
}

# Longest first so "city and borough" wins over "borough".
LSAD_SUFFIXES = [
    " metropolitan government", " consolidated government", " unified government", " metro government",
    " city and borough", " municipality", " comunidad", " zona urbana", " village", " borough", " city",
    " town", " CDP", " plantation", " township", " urban county",
]
NAME_ALIASES = {
    "Nashville-Davidson": "Nashville",
    "Louisville/Jefferson County": "Louisville",
    "Lexington-Fayette": "Lexington",
    "Augusta-Richmond County": "Augusta",
    "Athens-Clarke County": "Athens",
    "Macon-Bibb County": "Macon",
    "Urban Honolulu": "Honolulu",
    "San Buenaventura (Ventura)": "Ventura",
    "Boise City": "Boise",
}


def clean_place_name(raw):
    """'Tulsa city' -> ('Tulsa', 'city'); 'Brandon CDP' -> ('Brandon', 'CDP')."""
    name = raw.strip()
    name = re.sub(r"\s*\(balance\)$", "", name)
    kind = ""
    for suf in LSAD_SUFFIXES:
        if name.endswith(suf):
            name, kind = name[: -len(suf)], suf.strip()
            break
    name = NAME_ALIASES.get(name, name)
    return name.strip(), kind


def to_num(val):
    """Census sentinels (-666666666 etc.) and blanks -> None."""
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() in ("null", "n/a", "na"):
        return None
    try:
        num = float(s)
    except ValueError:
        return None
    if num < -1:
        return None
    return int(num) if num.is_integer() else num


def http_get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "local-seo-agent/1.0 (census data fetch)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cached_download(url, filename, refresh=False):
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, filename)
    if os.path.exists(path) and not refresh:
        return path
    data = http_get(url)
    with open(path, "wb") as fh:
        fh.write(data)
    return path


def decode(raw_bytes):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return raw_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------- PEP
def parse_pep(text):
    """Return {geoid: {...}} for incorporated places (SUMLEV 162)."""
    reader = csv.DictReader(io.StringIO(text))
    est_cols = sorted([c for c in reader.fieldnames if re.fullmatch(r"POPESTIMATE\d{4}", c)])
    if not est_cols:
        raise ValueError("PEP file has no POPESTIMATEyyyy columns")
    latest = est_cols[-1]
    vintage = latest[-4:]
    out = {}
    for row in reader:
        if row.get("SUMLEV") != "162":
            continue
        geoid = row["STATE"].zfill(2) + row["PLACE"].zfill(5)
        out[geoid] = {
            "pep_name": row["NAME"],
            "pep_population": to_num(row.get(latest)),
            "pop_2020_base": to_num(row.get("ESTIMATESBASE2020")),
            "pep_vintage": vintage,
        }
    return out


def load_pep(args):
    if args.pep_file:
        with open(args.pep_file, "rb") as fh:
            return parse_pep(decode(fh.read()))
    for v in args.pep_vintages:
        url = PEP_URL.format(v=v)
        try:
            path = cached_download(url, f"sub-est{v}.csv", args.refresh)
            with open(path, "rb") as fh:
                data = parse_pep(decode(fh.read()))
            print(f"[pep] vintage {v}: {len(data)} incorporated places", file=sys.stderr)
            return data
        except (urllib.error.URLError, ValueError, OSError) as exc:
            print(f"[pep] vintage {v} unavailable ({exc}); trying older", file=sys.stderr)
    print("[pep] no PEP file available - falling back to ACS population only", file=sys.stderr)
    return {}


# --------------------------------------------------------------------------- ACS
def parse_acs(payload):
    """ACS API JSON (list of lists, first row header) -> {geoid: {...}}."""
    rows = json.loads(payload) if isinstance(payload, (str, bytes)) else payload
    header = rows[0]
    idx = {h: i for i, h in enumerate(header)}
    out = {}
    for r in rows[1:]:
        geoid = r[idx["state"]].zfill(2) + r[idx["place"]].zfill(5)
        rec = {"acs_name": r[idx["NAME"]]}
        for var, field in ACS_VARS.items():
            if var in idx:
                rec[field] = to_num(r[idx[var]])
        out[geoid] = rec
    return out


def load_acs(args):
    if args.acs_file:
        with open(args.acs_file, "rb") as fh:
            return parse_acs(decode(fh.read())), "file"
    key = os.environ.get("CENSUS_API_KEY", "")
    for y in args.acs_years:
        params = {"get": "NAME," + ",".join(ACS_VARS), "for": "place:*", "in": "state:*"}
        if key:
            params["key"] = key
        url = ACS_URL.format(y=y) + "?" + urllib.parse.urlencode(params)
        try:
            path = cached_download(url, f"acs5_{y}_places.json", args.refresh)
            with open(path, "rb") as fh:
                data = parse_acs(decode(fh.read()))
            print(f"[acs] {y} 5-year: {len(data)} places", file=sys.stderr)
            return data, str(y)
        except (urllib.error.URLError, ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"[acs] {y} unavailable ({exc}); trying older", file=sys.stderr)
    sys.exit("[acs] could not download ACS data - check network access to api.census.gov")


# --------------------------------------------------------------------------- Gazetteer
def parse_gazetteer(text):
    lines = text.splitlines()
    header = [h.strip() for h in lines[0].split("\t")]
    idx = {h: i for i, h in enumerate(header)}
    out = {}
    for line in lines[1:]:
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < len(header):
            continue
        out[parts[idx["GEOID"]].zfill(7)] = {
            "lat": to_num(parts[idx["INTPTLAT"]]),
            "lon": to_num(parts[idx["INTPTLONG"]]),
            "land_sqmi": to_num(parts[idx["ALAND_SQMI"]]),
        }
    return out


def load_gazetteer(args):
    if args.gaz_file:
        with open(args.gaz_file, "rb") as fh:
            return parse_gazetteer(decode(fh.read()))
    for y in args.gaz_years:
        url = GAZ_URL.format(y=y)
        try:
            path = cached_download(url, f"{y}_Gaz_place_national.zip", args.refresh)
            with zipfile.ZipFile(path) as zf:
                name = [n for n in zf.namelist() if n.endswith(".txt")][0]
                data = parse_gazetteer(decode(zf.read(name)))
            print(f"[gaz] {y}: {len(data)} places with coordinates", file=sys.stderr)
            return data
        except (urllib.error.URLError, OSError, IndexError, zipfile.BadZipFile, KeyError) as exc:
            print(f"[gaz] {y} unavailable ({exc}); trying older", file=sys.stderr)
    print("[gaz] no Gazetteer file - output will lack coordinates", file=sys.stderr)
    return {}


# --------------------------------------------------------------------------- join
def pct(num, den):
    if num is None or not den:
        return None
    return round(100.0 * num / den, 1)


def build_rows(pep, acs, gaz, acs_label, min_pop):
    rows = []
    for geoid, a in acs.items():
        state = STATE_ABBR_BY_FIPS.get(geoid[:2])
        if not state:
            continue  # Puerto Rico & territories
        acs_name = a.get("acs_name", "")
        place_part, _, _ = acs_name.rpartition(", ")
        state_name = STATE_NAMES[state]
        name, kind = clean_place_name(place_part or acs_name)
        p = pep.get(geoid, {})
        population = p.get("pep_population") or a.get("acs_population")
        if population is None or population < min_pop:
            continue
        pop_source = f"pep{p['pep_vintage']}" if p.get("pep_population") else f"acs{acs_label}"
        base = p.get("pop_2020_base")
        g = gaz.get(geoid, {})
        land = g.get("land_sqmi")
        rows.append({
            "geoid": geoid,
            "name": name,
            "state": state,
            "state_name": state_name,
            "place_type": kind or "place",
            "population": int(population),
            "population_source": pop_source,
            "pop_2020_base": base if base is not None else "",
            "growth_since_2020_pct": pct(population - base, base) if base else "",
            "median_hh_income": a.get("median_hh_income", "") if a.get("median_hh_income") is not None else "",
            "owner_occupied_pct": pct(a.get("owner_occupied_units"), a.get("occupied_units")) or "",
            "median_home_value": a.get("median_home_value") if a.get("median_home_value") is not None else "",
            "median_year_built": a.get("median_year_built") if a.get("median_year_built") is not None else "",
            "sfh_detached_pct": pct(a.get("single_family_detached_units"), a.get("units_in_structure_total")) or "",
            "housing_units": a.get("housing_units") if a.get("housing_units") is not None else "",
            "land_sqmi": land if land is not None else "",
            "density_per_sqmi": round(population / land, 1) if land else "",
            "lat": g.get("lat", ""),
            "lon": g.get("lon", ""),
            "source": f"census:{pop_source};acs5:{acs_label}",
        })
    rows.sort(key=lambda r: (r["state"], -r["population"], r["name"]))
    return rows


FIELDS = ["geoid", "name", "state", "state_name", "place_type", "population", "population_source",
          "pop_2020_base", "growth_since_2020_pct", "median_hh_income", "owner_occupied_pct",
          "median_home_value", "median_year_built", "sfh_detached_pct", "housing_units", "land_sqmi",
          "density_per_sqmi", "lat", "lon", "source"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-pop", type=int, default=1000)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--refresh", action="store_true", help="ignore cached downloads in data/raw/")
    ap.add_argument("--pep-vintages", nargs="+", default=["2025", "2024", "2023"])
    ap.add_argument("--acs-years", nargs="+", default=["2024", "2023", "2022"])
    ap.add_argument("--gaz-years", nargs="+", default=["2025", "2024", "2023"])
    ap.add_argument("--pep-file", help="local SUB-EST csv (offline mode)")
    ap.add_argument("--acs-file", help="local ACS API JSON (offline mode)")
    ap.add_argument("--gaz-file", help="local Gazetteer place .txt (offline mode)")
    args = ap.parse_args(argv)

    pep = load_pep(args)
    acs, acs_label = load_acs(args)
    gaz = load_gazetteer(args)
    rows = build_rows(pep, acs, gaz, acs_label, args.min_pop)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} places -> {args.out}")


if __name__ == "__main__":
    main()
