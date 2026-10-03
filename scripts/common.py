"""Shared helpers for the local-SEO-Agent scripts (Python 3.9+, standard library only)."""
import csv
import json
import math
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
PROJECTS_DIR = os.path.join(ROOT, "projects")
TEMPLATES_DIR = os.path.join(ROOT, "templates")


# --------------------------------------------------------------------------- io
def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows, fields=None):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fields = fields or (list(rows[0].keys()) if rows else [])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


# --------------------------------------------------------------------------- states
_STATES = load_json(os.path.join(DATA_DIR, "us_states.json"))["states"]
STATE_NAMES = {abbr: s["name"] for abbr, s in _STATES.items()}
STATE_ABBR_BY_NAME = {s["name"]: abbr for abbr, s in _STATES.items()}
STATE_ABBR_BY_FIPS = {s["fips"]: abbr for abbr, s in _STATES.items()}
STATE_TAGS = {abbr: set(s.get("tags", [])) for abbr, s in _STATES.items()}
STATE_REGION = {abbr: s["region"] for abbr, s in _STATES.items()}


def normalize_state(value):
    """'ok', 'Oklahoma', 'OK' -> 'OK'. Returns None when unknown."""
    if not value:
        return None
    v = value.strip()
    if v.upper() in STATE_NAMES:
        return v.upper()
    for name, abbr in STATE_ABBR_BY_NAME.items():
        if name.lower() == v.lower():
            return abbr
    return None


def parse_city_arg(text):
    """'Tulsa, OK' / 'Tulsa OK' / 'Tulsa, Oklahoma' -> ('Tulsa', 'OK')."""
    text = text.strip()
    if "," in text:
        city, st = text.rsplit(",", 1)
        return city.strip(), normalize_state(st)
    parts = text.split()
    if len(parts) > 1 and normalize_state(parts[-1]):
        return " ".join(parts[:-1]), normalize_state(parts[-1])
    return text, None


# --------------------------------------------------------------------------- geo
def haversine_mi(lat1, lon1, lat2, lon2):
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _num(v, cast=float):
    if v is None or v == "":
        return None
    try:
        return cast(float(v))
    except (TypeError, ValueError):
        return None


def places_path():
    census = os.path.join(DATA_DIR, "census_places.csv")
    return census if os.path.exists(census) else os.path.join(DATA_DIR, "us_places.csv")


def load_places(path=None):
    """Load places from the official Census build if present, else the GeoNames starter set."""
    path = path or places_path()
    out = []
    for r in read_csv(path):
        p = dict(r)
        p["population"] = _num(r.get("population"), int) or 0
        p["lat"] = _num(r.get("lat"))
        p["lon"] = _num(r.get("lon"))
        for k in ("median_hh_income", "owner_occupied_pct", "median_home_value", "median_year_built",
                  "sfh_detached_pct", "growth_since_2020_pct", "density_per_sqmi"):
            p[k] = _num(r.get(k))
        out.append(p)
    return out


def find_place(places, name, state=None):
    name_l = name.strip().lower()
    cands = [p for p in places if p["name"].lower() == name_l and (not state or p["state"] == state)]
    if not cands:
        cands = [p for p in places if p["name"].lower().startswith(name_l) and (not state or p["state"] == state)]
    return max(cands, key=lambda p: p["population"]) if cands else None


# --------------------------------------------------------------------------- niches
def load_niches():
    d = load_json(os.path.join(DATA_DIR, "niches.json"))
    return {n["id"]: n for n in d["niches"]}, d["_meta"]


def find_niche(niches, query):
    q = slugify(query)
    if q in niches:
        return niches[q]
    for n in niches.values():
        if slugify(n["name"]) == q or q in slugify(n["name"]) or q in n["id"]:
            return n
    return None


# --------------------------------------------------------------------------- text
def slugify(text):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", text)


def fmt_int(v):
    return "-" if v is None or v == "" else f"{int(round(float(v))):,}"


def fmt_money(v, decimals=0):
    if v is None or v == "":
        return "-"
    return f"${float(v):,.{decimals}f}"


def md_table(rows, headers):
    """rows: list of lists/tuples; headers: list of str -> GitHub markdown table."""
    def cell(x):
        return str(x).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(x) for x in r) + " |")
    return "\n".join(out)
