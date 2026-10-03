#!/usr/bin/env python3
"""Portfolio dashboard: one line per project in projects/*/project.json.

  python3 scripts/portfolio.py            # markdown table
  python3 scripts/portfolio.py --json

Update a project's numbers by editing its project.json (phase, status, monthly_revenue, tenant, live.*)
or by asking the orchestrator to run the monthly review.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROJECTS_DIR, fmt_money, load_json, md_table  # noqa: E402

PHASES = ["intake", "niche", "market", "keywords", "serp", "economics", "go/no-go", "architecture",
          "content", "launch-qa", "launch", "authority", "monetization", "operate"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    projects = []
    for path in sorted(glob.glob(os.path.join(PROJECTS_DIR, "*", "project.json"))):
        try:
            projects.append(load_json(path))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skip {path}: {exc}", file=sys.stderr)
    if a.json:
        print(json.dumps(projects, indent=2))
        return
    if not projects:
        print("No projects yet. Start one with: python3 scripts/new_project.py --niche <id> --city 'City, ST'")
        return
    rows, total = [], 0
    for p in projects:
        verdict = p["verdicts"][-1]["verdict"] if p.get("verdicts") else "-"
        rev = p.get("monthly_revenue") or 0
        total += rev
        rows.append([p["slug"], p.get("niche_id") or "-",
                     f"{p.get('city')}, {p.get('state')}" if p.get("city") else p.get("scope", "-"),
                     p.get("model", "-"), p.get("status", "-"), verdict, p.get("domain") or "-",
                     (p.get("tenant") or {}).get("name", "-") if isinstance(p.get("tenant"), dict) else (p.get("tenant") or "-"),
                     fmt_money(rev)])
    print(md_table(rows, ["Project", "Niche", "Market", "Model", "Status", "Last verdict", "Domain", "Tenant", "Revenue/mo"]))
    print(f"\nProjects: {len(projects)} | Portfolio revenue: {fmt_money(total)}/mo")


if __name__ == "__main__":
    main()
