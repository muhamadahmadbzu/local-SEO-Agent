#!/usr/bin/env python3
"""Scaffold a new site project under projects/<slug>/.

Examples
  python3 scripts/new_project.py --niche tree-service --city "Tulsa, OK" --model rank_and_rent
  python3 scripts/new_project.py --niche water-damage --scope national --model nationwide --slug water-damage-usa
  python3 scripts/new_project.py --discovery --slug q4-niche-hunt   # research-only project before a niche is chosen

Creates:
  project.json      machine-readable state (phase, decisions, live numbers)
  STATUS.md         pipeline checklist + decision log
  brief.md          operator brief (Phase 0)
  research/ decisions/ data/serp/ ops/reports/
  site/site.json    site config pre-filled from the niche + service-area towns
  site/content/ site/briefs/ site/static/
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (PROJECTS_DIR, STATE_NAMES, TEMPLATES_DIR, find_niche, find_place, load_niches,  # noqa: E402
                    load_places, parse_city_arg, save_json, slugify, write_text)


def render(template_path, values):
    with open(template_path, encoding="utf-8") as fh:
        text = fh.read()
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text


def service_area_towns(city, st, limit=8, radius=25, min_pop=3000):
    from city_finder import Grid
    places = load_places()
    center = find_place(places, city, st)
    if not center:
        return [city]
    grid = Grid(places)
    near = [(q, d) for q, d in grid.near(center["lat"], center["lon"], radius)
            if q is not center and q["population"] >= min_pop]
    near.sort(key=lambda qd: -qd[0]["population"] / (1 + qd[1] / 10.0))
    return [center["name"]] + [q["name"] for q, _ in near[:limit]]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--niche", help="niche id from data/niches.json")
    ap.add_argument("--city", help='"City, ST" for local projects')
    ap.add_argument("--scope", choices=["local", "national"], default="local")
    ap.add_argument("--model", choices=["rank_and_rent", "pay_per_call", "hybrid", "nationwide"], default="hybrid")
    ap.add_argument("--discovery", action="store_true", help="research-only project (no niche/city yet)")
    ap.add_argument("--slug")
    ap.add_argument("--brand")
    ap.add_argument("--domain", default="https://example.com")
    ap.add_argument("--phone", default="")
    ap.add_argument("--risk", choices=["low", "medium", "high"], default="medium")
    ap.add_argument("--mission", default="")
    ap.add_argument("--force", action="store_true", help="allow writing into an existing project folder")
    a = ap.parse_args(argv)

    niches, _ = load_niches()
    niche = find_niche(niches, a.niche) if a.niche else None
    if a.niche and not niche:
        sys.exit(f"unknown niche '{a.niche}'")
    city = st = None
    if a.city:
        city, st = parse_city_arg(a.city)
        if not st:
            sys.exit("--city must include a state: 'Tulsa, OK'")
    if not a.discovery and not niche:
        sys.exit("--niche is required (or use --discovery for a research-only project)")
    if not a.discovery and a.scope == "local" and not city:
        sys.exit("local projects need --city 'City, ST' (or --scope national)")

    if a.slug:
        slug = slugify(a.slug)
    elif a.discovery:
        slug = f"discovery-{dt.date.today().isoformat()}"
    elif a.scope == "national":
        slug = f"{niche['id']}-national"
    else:
        slug = f"{slugify(city)}-{st.lower()}-{niche['id']}"
    root = os.path.join(PROJECTS_DIR, slug)
    if os.path.exists(root) and not a.force:
        sys.exit(f"{root} already exists (use --force to re-scaffold missing files only)")

    for d in ("research", "decisions", "data/serp", "ops/reports", "site/content", "site/briefs", "site/static"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
        keep = os.path.join(root, d, ".gitkeep")
        if not os.listdir(os.path.join(root, d)):
            open(keep, "w").close()

    market = (f"{city}, {st}" if city else ("United States (nationwide)" if a.scope == "national" else "to be chosen"))
    name = (f"{niche['name']} — {market}" if niche else f"Discovery — {market}")
    values = {
        "project_name": name, "slug": slug, "niche_name": niche["name"] if niche else "to be chosen",
        "niche_id": niche["id"] if niche else "-", "market": market, "model": a.model,
        "date": dt.date.today().isoformat(), "risk": a.risk,
        "mission": a.mission or ("Find, validate and build a profitable US lead-generation site." if a.discovery else
                                 f"Build a {niche['name'].lower()} lead-generation site for {market} and monetize it via {a.model}."),
        "rank_month": "6", "revenue_month": "9", "target": "unknown - ask the operator",
    }
    for fname in ("STATUS.md", "brief.md"):
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            write_text(path, render(os.path.join(TEMPLATES_DIR, "project", fname), values))

    project = {
        "slug": slug, "name": name, "created": values["date"], "scope": a.scope, "model": a.model,
        "niche_id": niche["id"] if niche else None, "city": city, "state": st,
        "phase": 0, "status": "intake", "verdicts": [], "domain": a.domain if a.domain != "https://example.com" else None,
        "tenant": None, "monthly_revenue": 0, "live": {"launched": None, "first_lead": None, "rented": None},
    }
    pj = os.path.join(root, "project.json")
    if not os.path.exists(pj):
        save_json(pj, project)

    sj = os.path.join(root, "site", "site.json")
    if niche and not os.path.exists(sj):
        areas = service_area_towns(city, st) if city else []
        site = {
            "brand": a.brand or (f"{city} {niche['name']}" if city else f"{niche['name']} Pros"),
            "base_url": a.domain.rstrip("/"),
            "mode": "lead_gen",
            "scope": a.scope,
            "niche_id": niche["id"],
            "niche_name": niche["name"],
            "primary_city": city or "",
            "state": st or "",
            "state_name": STATE_NAMES.get(st, "") if st else "",
            "phone": a.phone,
            "phone_e164": "",
            "email": "",
            "hours": "",
            "tagline": "",
            "areas_served": areas,
            "services_plan": [{"name": s, "slug": slugify(s)} for s in niche["sub_services"]],
            "theme": {"primary": "#14532d", "accent": "#d97706", "logo_text": ""},
            "form": {"enabled": False, "action": "", "method": "POST",
                     "consent_text": "By submitting, you agree that {brand} and one matched local provider may contact you "
                                     "at the number provided about your request, including by call or text. "
                                     "Consent is not a condition of purchase. Message and data rates may apply."},
            "tracking": {"ga4_id": "", "gsc_verification": "", "bing_verification": "", "head_html": ""},
            "lead_gen": {"disclosure": ""},
            "tenant": {"legal_name": "", "license": "", "license_label": "License #", "schema_type": niche["schema_type"],
                       "address": {"street": "", "city": "", "region": st or "", "postal": ""},
                       "show_address": False, "gbp_url": "", "same_as": [], "hours": "", "founded": ""},
            "legal": {"contact_email": "", "effective_date": values["date"]},
        }
        save_json(sj, site)
    print(f"project scaffolded -> {os.path.relpath(root)}")
    print("next: fill brief.md with the operator, then run Phase 1 (see .claude/skills/rank-and-rent/SKILL.md)")


if __name__ == "__main__":
    main()
