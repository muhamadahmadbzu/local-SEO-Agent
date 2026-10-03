# Local SEO Agent: a rank & rent and pay-per-call "war room" for Claude Code

A team of **14 specialist Claude agents** that research, **argue**, decide, build, launch and monetize US local
lead-generation websites. It covers rank & rent, pay-per-call and nationwide call brands. Open this repo in
Claude Code and say what you want ("find me a niche", "evaluate roofing in Lawton, OK", "build the site"). The
`rank-and-rent` skill runs the pipeline and calls the war room at every money decision.

> USA only. Built around honest, policy-compliant lead generation: no fake GBPs, no fake reviews, no doorway pages.
> That way the sites you build survive Google's spam updates and the FTC.

## The team

| Research & strategy | Debate & decision | Build | Grow & earn |
|---|---|---|---|
| `niche-scout` | `devils-advocate` (red team) | `site-architect` | `authority-builder` |
| `geo-market-analyst` | `compliance-officer` | `content-strategist` | `monetization-closer` |
| `keyword-demand-analyst` | `ic-chair` (judge) | `local-copywriter` | |
| `serp-competition-analyst` | | `content-qa-editor` | |
| `lead-value-economist` | | | |

## How a decision gets made (the war room)

```
Round 1  POSITIONS        analysts research in parallel and write evidence-labeled memos
Round 2  CROSS-EXAM       devils-advocate: numbered objections (FATAL/MAJOR/MINOR) + pre-mortem
                          compliance-officer: CLEAR / CONDITIONAL / BLOCK rulings
Round 3  REBUTTAL         analysts CONCEDE, REBUT with new evidence, or MITIGATE with a plan (max 2 cycles)
Round 4  VERDICT          ic-chair scores the record -> GO / CONDITIONAL GO / NO-GO + dated kill criteria
```

## The pipeline

```
0 Intake -> 1 Niche research -> [Gate 1] -> 2 City selection -> [Gate 2]
  -> 3 Search volume -> 4 SERP competition -> 5 Lead economics -> [Gate 3: GO/NO-GO]
  -> 6 Architecture & domain -> 7 Content (briefs -> writing -> fact-check) -> [Gate 4: launch QA]
  -> 8 Launch & indexing -> 9 Authority -> 10 Monetize (tenant or pay-per-call) -> [Gate 5: deal] -> 11 Operate & scale
```

Every project is a folder in `projects/<slug>/` with its memos, data, decisions, site and ops files, so the team
can stop and resume at any time.

## Install

**macOS / Linux / WSL**
```bash
git clone https://github.com/muhamadahmadbzu/local-SEO-Agent.git && bash local-SEO-Agent/install.sh --global
```
**Windows (PowerShell)**
```powershell
git clone https://github.com/muhamadahmadbzu/local-SEO-Agent.git; powershell -ExecutionPolicy Bypass -File local-SEO-Agent\install.ps1 -Global
```
The installer checks Git, Python 3.9+ and Claude Code (offers to install Claude Code via npm), clones or updates the
repo into `~/local-SEO-Agent`, runs the self-tests, and with `--global` / `-Global` makes the 14 agents and 11 skills
available in every Claude Code session. Add `--census` / `-Census` to download official Census city data. Re-run it
any time to update.

## Quick start

Requirements: Python 3.9+ (standard library only) and Claude Code.

```bash
# in Claude Code, inside this repo
/rank-and-rent discover                                  # find niches + cities worth building
/rank-and-rent evaluate tree service in Tulsa, OK        # deep-dive one niche x city -> GO/NO-GO
/rank-and-rent build tulsa-ok-tree-service               # architecture, briefs, content, QA
/war-room tulsa-ok-tree-service gate 3                   # re-run a decision debate
```
Or just ask in plain English: "What are the best pay-per-call niches for Florida?", "Which cities should I target for
septic services?", "How much could a roofing site in Lawton make?"

### Useful scripts (the agents use these; you can too)
```bash
python3 scripts/niche_scorer.py rank --model rank_and_rent --city "Tulsa, OK"   # potential-earning niches
python3 scripts/niche_scorer.py rank --model nationwide --risk-tolerance high   # nationwide pay-per-call niches
python3 scripts/niche_scorer.py show water-damage                               # niche card
python3 scripts/city_finder.py rank --niche tree-service --min-pop 50000 --max-pop 300000
python3 scripts/city_finder.py service-area "Tulsa, OK" --radius 25
python3 scripts/keyword_tool.py expand --niche tree-service --city "Tulsa, OK" --out /tmp/kw.csv
python3 scripts/lead_economics.py --niche roofing --leads 6 15 30 --cpc 28
python3 scripts/build_site.py examples/demo-tree-service && python3 -m http.server -d examples/demo-tree-service/dist 8000
python3 scripts/qa_site.py examples/demo-tree-service
python3 -m unittest discover -s tests
```

## Data

| What | Where | Notes |
|---|---|---|
| 97 niches with ticket, urgency, seasonality, demand tier, LSA/directory pressure, pay-per-call payouts and buffers, rent and per-lead ranges, licensing/regulatory/spam risk, seed keywords | `data/niches.json` | Priors (reviewed 2026-10). Live research replaces them |
| ~16.9k US places with population and coordinates | `data/us_places.csv` | GeoNames starter set |
| Official Census population, growth, income, home ownership, housing age, density | `data/census_places.csv` | Run `python3 scripts/fetch_census_data.py` (needs census.gov access) |
| Search volume and CPC | DataForSEO API, or Keyword Planner / Ahrefs / Semrush exports | Set `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`, or import CSVs |
| SERP competition | DataForSEO SERP API, or the manual capture template | `scripts/serp_audit.py` |

## Sites the system builds
Static, fast, mobile-first HTML: a sticky click-to-call bar, schema (`@graph`), breadcrumbs, FAQ accordions, a
sitemap, robots.txt, legal page templates, and a referral disclosure in `lead_gen` mode. One switch (`mode: tenant`)
turns it into the renting business's site with their license number and LocalBusiness schema. Deploy `dist/` to
Cloudflare Pages or Netlify for free. `qa_site.py --launch` is the publish gate: it blocks fake claims, templated
city pages, broken links, bad schema and missing disclosures.

## Disclaimer
Nothing here is legal, tax or financial advice. Search volumes, payouts and rents vary. The system is designed to
measure them, not to promise them. Check state licensing, consent and advertising rules for your niche and state, and
use a lawyer for contracts.
