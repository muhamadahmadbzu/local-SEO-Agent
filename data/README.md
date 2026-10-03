# Data layer

Every agent and script reads from this folder. **Treat everything here as a prior.** Live research in
Phases 3–5 (keywords, SERPs, economics) must confirm it before any GO decision.

| File | What it is | Source / license | Refresh |
|---|---|---|---|
| `us_places.csv` | Starter list of ~16.9k US places with population ≥ 1,000, plus state, coordinates and timezone | [GeoNames](https://www.geonames.org/) (CC BY 4.0) via the `geonamescache` package (MIT). Populations are a mix of 2010–2020 vintages. | `pip install geonamescache && python3 scripts/maintenance/build_geonames_places.py` |
| `census_places.csv` | **Preferred** once built. Incorporated places + CDPs with the latest PEP population, 2020 base and growth, median household income, owner-occupied %, median home value, median year built, single-family-detached %, land area, density and coordinates | US Census Bureau (public domain): PEP SUB-EST, ACS 5-year API, Gazetteer | `python3 scripts/fetch_census_data.py` (needs access to `www2.census.gov` and `api.census.gov`) |
| `niches.json` | 97 US local-service and pay-per-call niches: ticket size, urgency, seasonality, demand tier, LSA/directory pressure, indicative pay-per-call payouts and call buffers, rent and per-lead ranges, licensing/regulatory/spam risk, geo tags, schema type, sub-services and seed keywords | Synthesized from public cost guides, pay-per-call marketplaces and rank-and-rent practitioner benchmarks (reviewed 2026-10) | Edit by hand. Bump `_meta.version` |
| `us_states.json` | States with FIPS codes, Census region/division and coarse climate/housing tags (hail belt, termite zones, basements, septic and so on) | Curated heuristics | Edit by hand |
| `serp_domains.json` | Domain lists (directories, marketplaces, UGC, national brands) that `serp_audit.py` uses to classify SERP results | Curated | Add domains as you meet them |

## Rules for using the data

1. **Cite the vintage.** When a memo quotes a population, it says which file and source it came from, for
   example `census_places.csv pep2025` or `us_places.csv geonames`.
2. **GeoNames caveats.** The starter file includes some neighborhoods and boroughs as separate places
   (for example Brooklyn and Van Nuys). They are still valid search targets, but they are not separate
   municipalities. Its populations can also be several years old. Build `census_places.csv` before you
   make a final city decision.
3. **Niche numbers are ranges, not facts.** Payouts vary by ZIP code, hour, buyer and call buffer. Rents
   depend on what the tenant can actually close. Confirm against a live network offer or a tenant
   conversation.
4. **Region tags are state-level and coarse.** Before relying on a tag, check it at the city level with
   NOAA storm events, ACS housing data or the local permit office.

## Census API note

`fetch_census_data.py` works without a key (the Census Bureau allows a limited number of keyless calls
per day). Set `CENSUS_API_KEY` if you hit the limit (free at <https://api.census.gov/data/key_signup.html>).
Downloads are cached in `data/raw/`, which is git-ignored.
