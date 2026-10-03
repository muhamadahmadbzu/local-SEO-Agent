---
name: market-selection
description: "Method for choosing US cities and service areas for a niche. It covers population bands, service-area clusters, metro spillover, Census housing and income data, climate fit, competition sampling and verified local fact sheets for unique city content. Use it for \"which city\", \"city population\", \"best cities for <niche>\", \"service area towns\", or building local facts for pages."
argument-hint: "<niche-id> [states/region] [population range]"
---

# Market Selection

Owner: `geo-market-analyst`, with quick checks from `keyword-demand-analyst` and `serp-competition-analyst`.
Request: $ARGUMENTS

## Data
- `data/census_places.csv` (preferred): official Census PEP population (latest vintage), 2020 base and growth, ACS
  5-year income, owner-occupied %, home value, median year built, single-family-detached %, land area, density and
  coordinates. It covers incorporated places AND CDPs. Build it with `python3 scripts/fetch_census_data.py` (needs
  `www2.census.gov` and `api.census.gov`).
- `data/us_places.csv` (fallback): GeoNames starter data with ~16.9k places of 1,000+ people. Its populations come
  from mixed vintages and it includes some neighborhoods. Fine for triage, so label it.
- `data/us_states.json`: coarse climate and housing tags per state (hail belt, termite zones, basements, septic and so on).

## Step 1: Rank candidates
```
python3 scripts/city_finder.py rank --niche <id> --min-pop 40000 --max-pop 400000 --max-per-state 3 --top 30
python3 scripts/city_finder.py rank --niche septic --states NC SC TN GA --sweet-spot 20000 120000
python3 scripts/city_finder.py rank --niche foundation-repair --region South --min-owner-pct 60   # owner % needs census data
python3 scripts/city_finder.py profile "Lawton, OK" --niche roofing
```
The score (a prior) = population fit to the sweet spot + niche geo fit + service-area cluster population +
independence from a much larger metro + ACS economics (income, ownership, single-family share; housing age for
repair niches; growth for new-construction niches).

Each niche has a `market_profile` in niches.json (rural, suburban, urban or affluent) that sets city_finder's default
sweet spot and ideal service-area cluster: rural 15k-120k city with a 40k-300k cluster (septic, wells, land
clearing); suburban 50k-300k with 150k-900k; urban 150k-1M with 500k-4M (bed bugs, towing, legal); affluent 40k-400k
with 150k-1.5M (pools, remodeling, hardscaping). Override with `--sweet-spot LO HI`.

### Population bands (rules of thumb)
| Band | Population | Rank & rent | Pay-per-call |
|---|---|---|---|
| Small town | < 25k | Only rural niches (septic, wells, land clearing), aggregated by county | Rarely worth it alone |
| Small city | 25k-75k | Good for low-competition niches, often 1 tenant | Low volume |
| **Mid city** | **75k-300k** | **Sweet spot**: real demand, beatable SERPs | Good |
| Large city | 300k-1M | Competitive core terms; win with sub-services or suburbs | Strong |
| Metro core | 1M+ | Avoid core terms as a beginner; target suburbs with their own identity | Strongest volume, toughest SERP |

## Step 2: Read each market (top ~10)
- **Independence vs. suburb**: is there a 150k+ city within 25 miles? (city_finder's "Near metro" column). Suburbs
  with a strong local identity can work. Generic suburbs lose to metro-wide brands.
- **Service-area depth**: `python3 scripts/city_finder.py service-area "City, ST" --radius 25 --min-pop 3000`.
  8+ towns over 5k people = room for area pages and a bigger tenant footprint.
- **Housing**: owner-occupied ≥ 55% and single-family ≥ 55% suit home services. Median year built before ~1980 favors
  plumbing, electrical, foundation and chimney work. Recent growth favors fencing, landscaping, concrete and pools.
- **Income and home value**: high-ticket remodeling, pools and hardscaping need affluent pockets. Emergency trades
  don't care as much.
- **Climate fit**: confirm the state tags locally (NOAA Storm Events database, termite probability maps, frost-line
  depth, FEMA flood maps).
- **Quick competition sample**: 2-3 money keywords per city (see the competition-audit skill). Don't pick a city
  before you've looked at its SERP.

## Step 3: Shortlist and thesis
3-5 cities, each with a one-sentence thesis and its main risk. Two mid cities in different states diversify a
portfolio better than one big city.

## Step 4: Local fact sheets (after Gate 2)
For the chosen city and every candidate area-page town, fill `templates/briefs/city-fact-sheet.md` and save it to
`projects/<slug>/research/local-facts/<town-slug>.md`. Only verified facts with source URLs:
- Permit and code rules for the trade (city or county website), HOA prevalence, tree ordinances, right-of-way rules
- Utilities (water, power, gas) and their programs (rebates, line-clearance policies, call-before-you-dig)
- Climate and hazards: storm history, freeze days, flood zones, soil type, termite pressure, radon zone
- Housing: median year built, share of older homes, typical construction (slab, basement, crawlspace)
- Geography: neighborhoods, ZIP codes, distances and drive times, notable terrain (hills, river bottoms)
- Local costs: published local price data, or surveyed quotes with a date
A town with fewer than 3 unique, useful facts gets NO standalone page. It's listed on the areas hub instead.

## Output
`projects/<slug>/research/02-market.md`, `data/cities.md` (or .csv), and `research/local-facts/*.md`. Feeds Gate 2.
