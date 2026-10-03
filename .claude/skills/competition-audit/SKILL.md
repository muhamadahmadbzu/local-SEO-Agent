---
name: competition-audit
description: "Method for auditing local Google SERPs and competitors. It covers capturing location-accurate SERPs (DataForSEO or a manual template), classifying results (directories, marketplaces, national brands, local businesses, lead-gen sites), map-pack depth, LSAs, ads, AI Overviews, difficulty scoring, competitor page teardown, time-to-rank and exploitable gaps. Use it for \"competition\", \"how hard to rank\", \"SERP analysis\", \"who ranks for\", or difficulty checks."
argument-hint: "<keyword(s)> <City, ST> [project slug]"
---

# Competition Audit

Owner: `serp-competition-analyst`. Request: $ARGUMENTS

## Why location matters
A Tulsa searcher and a Chicago searcher see different results for "tree service". Generic web search, including
the WebSearch tool, is NOT location-set. Valid captures come from DataForSEO (`location_name` = the city) or a manual
search with the location set (Google search settings or a location-set browser), on mobile where possible. Record how
each capture was made.

## Step 1: Choose 3-6 money keywords
The core "<service> <city>", the top 2 sub-services, one near-me query, and one service-area town query.

## Step 2: Capture
```
# API (preferred)
python3 scripts/serp_audit.py fetch --keyword "tree service tulsa" --city "Tulsa, OK" --maps --out-dir projects/<slug>/data/serp
# Manual: generate a template, then fill it from a real location-set SERP
python3 scripts/serp_audit.py template --keyword "tree service tulsa" --city "Tulsa, OK" > projects/<slug>/data/serp/tree-service-tulsa.json
```
Manual template fields: `features` (ads_top count, lsa, local_pack, ai_overview), `local_pack` (name, rating,
reviews, website), and `organic` (position, url, title, type = auto or override, dr if you have a real authority metric).

## Step 3: Score
```
python3 scripts/serp_audit.py score projects/<slug>/data/serp/*.json --city "Tulsa, OK" --out projects/<slug>/research/04-serp-data.md
```
Difficulty 0-100 = organic top-10 composition (45%: directories, marketplaces and UGC are weak; national brands are
strong; weighted by position) + city-optimized local competitors (15%) + map-pack review depth (15%) + SERP-feature
pressure (10%) + domain authority when supplied (15%).
Bands: **< 35 easy**, **35-55 moderate**, **55-70 hard**, **> 70 very hard**. Correct misclassified domains (set
`type` in the JSON, or add the domain to `data/serp_domains.json`) and re-score.

## Step 4: Competitor teardown (top 3 organic for the core term)
For each one, use WebFetch on the ranking URL and record:
- Page type (home or dedicated service page), title, H1, word count, depth (prices? process? FAQs? local specifics?)
- Service and area page coverage (do they have pages for each sub-service and town?)
- Trust (real photos, reviews, license number shown), freshness, mobile UX, speed impression
- Schema present, internal linking, and the obvious on-page gaps
- Authority: only from a real tool (Ahrefs DR, Moz DA, Semrush AS, DataForSEO backlinks). Otherwise UNKNOWN

## Step 5: Interpret
- **Opportunity signals**: 4+ directory or marketplace results in the top 10; no local site with a dedicated page for
  a sub-service; thin top-3 pages (< 500 words, no local substance); stale sites; map-pack leaders with < 50 reviews.
- **Danger signals**: national brands or franchise locator pages in the top 3; several city-optimized local sites
  with real content; an EMD lead-gen competitor with links; LSAs + 3 ads + map pack + AI Overview above organic.
- **Time to rank (organic top 3)**: easy 2-4 months, moderate 4-7, hard 7-12, very hard 12+ (fresh domain, honest
  links, strong content). Hand the number to the economist (`--difficulty`).
- **CTR pressure**: the `ctr_pressure` field (0-1). Above 0.6, tell the keyword analyst and economist to use the
  conservative scenario as the base.

## Output
`research/04-serp.md` (analyst memo: difficulty table, competitor teardown, gaps to exploit, months to rank, CTR
pressure and data-quality notes), plus `research/04-serp-data.md` and the raw JSON in `data/serp/`.
