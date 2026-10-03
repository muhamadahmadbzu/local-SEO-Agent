# Local SEO Agent: operating manual for Claude

This repository is a **multi-agent system for US local lead-generation websites**: rank & rent, pay-per-call and
nationwide call brands. It goes from niche research to a ranking, earning site. **USA only.**

## Start here
- For anything about niches, cities, search volume, lead value, earnings, building, launching, renting or selling
  calls, use the **`rank-and-rent` skill** (`.claude/skills/rank-and-rent/SKILL.md`). It is the orchestrator. It
  dispatches the 14 agents in `.claude/agents/` and runs decision gates through the **`war-room` skill**.
- Method skills: `niche-research`, `market-selection`, `keyword-research`, `competition-audit`, `lead-economics`,
  `site-factory`, `content-engine`, `launch-and-rank`, `monetization`.
- Every project lives in `projects/<slug>/`. Read its `STATUS.md` and `project.json` first and resume from there.

## Repository map
```
.claude/agents/        14 specialist subagents (research, red team, compliance, judge, build, growth)
.claude/skills/        orchestrator, war room and method skills (+ rank-and-rent/reference/compliance-playbook.md)
data/                  niches.json (97 niche priors), us_places.csv (GeoNames starter), census_places.csv (after fetch),
                       us_states.json (region/climate tags), serp_domains.json (SERP classifier lists)
scripts/               stdlib-only Python CLIs (see the cheat sheet below)
templates/             memos (analyst, red team, compliance, rebuttal, decision), briefs, outreach, ops
examples/              demo-tree-service: a complete reference site project (fictional city)
projects/              one folder per real project (created by scripts/new_project.py)
tests/                 python3 -m unittest discover -s tests
```

## House rules (non-negotiable, for every agent)
1. **Never fabricate**: no invented search volumes, payouts, populations, prices, statistics, laws, quotes,
   businesses, reviews or sources. Unknown stays UNKNOWN until measured.
2. **No fake local presence**: never create or suggest a Google Business Profile for a lead-gen site (lead
   generators are ineligible). No virtual or borrowed addresses, no fake citations. Map-pack presence comes later,
   from the tenant's real GBP.
3. **No fake trust signals**: no fake reviews, testimonials, ratings, awards, licenses, insurance claims, years in
   business, team members or project photos (FTC rule 16 CFR 465, FTC Act Sec. 5).
4. **Honest identity**: while unrented (`mode: lead_gen`), the site is a referral service and says so (the build
   adds a disclosure). It never implies it is the contractor. In `mode: tenant`, use only claims the tenant confirms.
5. **No spam architecture**: no doorway or templated city pages, no scaled low-value content, no expired-domain
   abuse, no link schemes or PBNs. Every page needs unique purpose and substance (`qa_site.py` enforces part of this).
6. **Consent and recording**: a recording disclosure on tracked calls, accurate form consent, and no outbound
   autodialed, prerecorded or AI calls and texts without prior express written consent.
7. **Regulated verticals** (legal, insurance, Medicare, finance, health, addiction treatment, moving/transport, bail,
   solar) need a `compliance-officer` CLEAR or CONDITIONAL ruling before advancing. Addiction treatment and
   Medicare are BLOCK by default.
8. **Operator approval** before spending money (domains, tools, links, content) and before contacting businesses.

## Evidence labels (use in every memo, table and claim)
| Label | Meaning |
|---|---|
| `MEASURED` | From a tool, API or export (DataForSEO, Keyword Planner, GSC, call logs). Cite the source and date |
| `OBSERVED` | Seen directly (a SERP, a competitor page, an offer page). Cite the URL, date and method (e.g. "location-set mobile") |
| `PRIOR` | From `data/niches.json`, `us_states.json` or a public benchmark. Guides triage, never decides |
| `ASSUMPTION` | An explicit guess. State its sensitivity |
| `UNKNOWN` | Not known yet. Say how to find out |
Measurements beat priors. Observations beat opinions. Use ranges with a base case.

## Agent conventions
- Agents write full work to files in `projects/<slug>/` (memo templates in `templates/memos/`) and return
  **≤ 10 lines** to the orchestrator: bottom line, score or verdict, top risks, open questions, file path.
- Independent agents are dispatched **in parallel** (one message, several Agent calls).
- Gates: 1 Niche, 2 Market, 3 GO/NO-GO, 4 Launch, 5 Deal. No post-gate spending without a decision file in
  `projects/<slug>/decisions/`.

## Script cheat sheet
```
python3 scripts/new_project.py --niche <id> --city "City, ST" --model hybrid      # scaffold a project
python3 scripts/niche_scorer.py rank --model rank_and_rent [--city "City, ST"]    # niche triage (also: show <id>)
python3 scripts/city_finder.py rank --niche <id> --min-pop 40000 --max-pop 400000 # city triage
python3 scripts/city_finder.py service-area "City, ST" --radius 25                # towns for area pages
python3 scripts/keyword_tool.py expand|volume|cluster|report ...                  # keyword research
python3 scripts/serp_audit.py template|fetch|score ...                            # SERP difficulty
python3 scripts/lead_economics.py --niche <id> --keywords <csv> --difficulty <n>  # lead value, rent, cash flow
python3 scripts/build_site.py projects/<slug>                                     # build static site -> dist/
python3 scripts/qa_site.py projects/<slug> [--launch]                             # QA / publish gate
python3 scripts/portfolio.py                                                      # all projects at a glance
python3 scripts/fetch_census_data.py                                              # official Census data (needs census.gov access)
```
Optional live data: set `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` for search volume and SERP APIs. Without
them, use Keyword Planner exports and manual SERP templates.

## Data notes
- `data/census_places.csv` (official, preferred) is used automatically when present. Otherwise the tools fall back
  to `data/us_places.csv` (GeoNames, mixed 2010-2020 vintages, includes some neighborhoods). Memos must say which
  one they used.
- `data/niches.json` values are **priors** reviewed 2026-10. Payouts and rents vary by ZIP, buyer and season.

## Engineering conventions
- Scripts are Python 3.9+ **standard library only** (portable to any machine and to Cloudflare Pages builds). Shared
  helpers live in `scripts/common.py`, and the Markdown renderer is `scripts/mdlite.py`.
- Every script has `--help` with examples. Keep outputs in Markdown or CSV that agents can read.
- Run `python3 -m unittest discover -s tests` after changing scripts.
