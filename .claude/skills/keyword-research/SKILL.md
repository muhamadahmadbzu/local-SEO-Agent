---
name: keyword-research
description: "Method for measuring local search demand. It covers keyword expansion for a niche, city and service-area towns, real volumes and CPC from DataForSEO, Keyword Planner, Ahrefs or Semrush, clustering keywords into pages, seasonality, and traffic, lead and Ads-equivalent value scenarios. Use it for \"search volume\", \"keyword research\", \"how many people search\", \"keyword map\", or demand validation before building."
argument-hint: "<niche-id> <City, ST> [project slug]"
---

# Keyword Research & Demand

Owner: `keyword-demand-analyst`. Request: $ARGUMENTS

## Principles
- **Local demand = searches made BY people in the city**, including "near me" and unmodified queries ("tree removal"),
  plus "<service> <city>" searches made from anywhere. That's what Keyword Planner reports when Location = the city.
- **Never invent volumes.** If there's no data source, stop and get one. Population-share estimates exist for triage
  only and are labeled `ESTIMATE` everywhere downstream.
- **CPC is a price signal.** It's what local businesses already pay per click, and it anchors rent pricing.

## Step 1: Expand the universe
```
python3 scripts/keyword_tool.py expand --niche <id> --city "City, ST" --areas 8 --out projects/<slug>/data/keywords.csv
```
This generates core, near-me, city, emergency, cost and sub-service variants plus area-town keywords (towns are
auto-picked from the service area). Then add variants you find in Google autocomplete, People Also Ask, competitor
titles, Reddit and local Facebook groups. Append rows to the CSV, keeping the `cluster`, `page_type`, `intent` and
`geo` columns.

## Step 2: Measure (best available source)
| Source | Command | Notes |
|---|---|---|
| DataForSEO (Google Ads data) | `python3 scripts/keyword_tool.py volume --provider dataforseo --in <csv> --city "City, ST" --cache-dir projects/<slug>/data/raw` | Set `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`. Location format `City,State,United States`; check it with `keyword_tool.py locations "<city>"`. About 1,000 keywords per request. Monthly trend included. |
| Google Keyword Planner | Export "Keyword ideas" or "Search volume and forecasts" with Location = city, Language = English, then `volume --provider csv --file export.csv --in <csv>` | Without ad spend, KWP shows buckets (e.g. "1K-10K"). The tool converts them to geometric means: low precision, so label it |
| Ahrefs or Semrush export | `volume --provider csv --file export.csv --in <csv> --include-new` | US national volumes are not city volumes. Use them for relative intent, not local demand, unless the tool supports city targeting |
| Estimate (triage only) | `volume --provider estimate --file national.csv --population <pop> --in <csv>` | Pop-share x national. **Not decision-grade.** |

Add `--include-new` to import extra keywords found in an export. `--dry-run` shows the DataForSEO payload.

## Step 3: Sanity checks
- Compare the measured cluster total with the prior: `python3 scripts/niche_scorer.py show <id>` gives the demand tier
  (searches per 100k residents). More than a 3x gap means investigate: wrong location setting, KWP zeroing tiny
  terms, or an atypical market.
- Small cities: KWP often reports 0 or 10 for "<service> <town>" terms that do get searches. Judge the cluster, not
  single terms.
- Seasonality: name the peak and trough months, and the trough as a % of the peak.

## Step 4: Cluster into pages
```
python3 scripts/keyword_tool.py cluster --in projects/<slug>/data/keywords.csv --out projects/<slug>/data/keyword_map.md
```
Then apply judgment:
- **Same intent, same page**: "tree removal tulsa", "tree removal near me" and "tree removal service" go on one page.
- **Different intent, different page**: "tree removal cost" (research) versus "tree removal tulsa" (hire).
- **No demand + no strategic value = no page.** Area towns without demand or unique facts are listed on the hub.
- Keep one primary keyword per page and never target the same primary on two pages.

## Step 5: Report demand to the war room
```
python3 scripts/keyword_tool.py report --in projects/<slug>/data/keywords.csv --niche <id> --out projects/<slug>/research/03-keywords-data.md
```
The scenario table (conservative avg #7, base #4, strong #2) gives visits, leads (6%, 10% and 14% conversion) and
the **Ads-equivalent $/mo** (clicks x CPC). The CTR model is deliberately conservative for local SERPs
(#1 ≈ 15%, near-me x0.6). The SERP analyst may tell you to discount further for heavy ads, LSAs or AI Overviews.

## Output
`research/03-keywords.md` (analyst memo: totals, top keywords, page map summary, seasonality, CPCs, scenario leads,
data quality and prior gap), plus `data/keywords.csv`, `data/keyword_map.md` and `research/03-keywords-data.md`.
Hand the leads range to the `lead-economics` step.
