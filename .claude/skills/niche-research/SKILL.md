---
name: niche-research
description: "Method for finding and validating profitable US niches for rank-and-rent, pay-per-call and nationwide call sites. It covers the 97-niche prior database, the scoring model, live validation (buyers, spend, payouts, tickets, seasonality, regulation), kill rules and nationwide niche evaluation. Use it for \"find a niche\", \"best niches\", \"potential earning niches\", \"is <niche> good\", or comparing niches."
argument-hint: "[model: rank_and_rent|pay_per_call|nationwide] [City, ST | state] [risk: low|medium|high]"
---

# Niche Research

Owner: `niche-scout`, with `lead-value-economist` for value bands and `compliance-officer` for regulated verticals.
Request: $ARGUMENTS

## What makes a niche good (in order of importance for rank & rent)
1. **Rankable without a GBP**: organic results aren't buried under ads, LSAs, the map pack and AI Overviews, and are
   not owned by national brands or directories.
2. **Valuable leads**: a high ticket or high LTV, so a business happily pays $500-$3,000 a month for a steady flow.
3. **Many buyers**: plenty of small and medium operators per market, some already buying leads (LSAs, Ads, Angi).
4. **Demand**: enough monthly searches in a mid-size city to produce 10+ leads a month at a top-3 ranking.
5. **Urgency**: emergencies produce phone calls (and pay-per-call payouts). Planned projects produce forms and shopping around.
6. **Stability**: seasonality you can live with, or a seasonal tenant who rents year-round.
7. **Low regulatory and platform risk.**

For **pay-per-call**, urgency and payout move up and buyer depth is supplied by the network. For **nationwide**, network
coverage and compliance dominate.

## Step 1: Triage with priors
```
python3 scripts/niche_scorer.py rank --model rank_and_rent --top 25
python3 scripts/niche_scorer.py rank --model rank_and_rent --city "Tulsa, OK" --risk-tolerance low   # adds geo fit + rough potential
python3 scripts/niche_scorer.py rank --model pay_per_call --state FL
python3 scripts/niche_scorer.py rank --model nationwide --risk-tolerance high --top 15
python3 scripts/niche_scorer.py show <niche-id>          # full card: ticket, payout, rent, risks, seeds
```
The score blends value, demand, urgency, rankability, buyers, stability, risk and model fit, plus geo fit and the
city's potential band when a market is given. The "Potential $/mo" column is an order-of-magnitude prior. Phase 3
replaces it with measured demand.

## Step 2: Validate the top 8-12 live (cite URL and date for everything)
| Check | How | Red flag |
|---|---|---|
| Buyer depth | Map results "<service> near <city>"; state license lookup; BBB/Yelp counts | < 5-8 real operators |
| Proof of spend | Ads and LSAs on the SERP; Google Ads Transparency Center for local advertisers | Nobody advertises (no lead budget) |
| Ticket and LTV | 2+ cost sources (HomeGuide, Angi, Fixr, industry associations) | Typical job < $300 with no recurring revenue |
| Pay-per-call | Current offers on network marketplaces or CPA directories: payout, buffer, coverage, hours, caps, allowed traffic | No offer covers the market, or SEO traffic isn't allowed |
| Seasonality | Google Trends, 5 years, US + state | Trough < 30% of peak with no off-season plan |
| SERP feel | 2-3 quick searches (directories? national brands? weak local sites?) | Top 5 = national brands + LSAs |
| Regulation | Licensing in ads, vertical laws (see compliance playbook) | Extreme risk, or counsel needed with no budget for it |

## Step 3: Kill rules (automatic out unless the operator overrides in writing)
- Extreme regulatory risk (Medicare, addiction treatment) without specialist counsel.
- Best-case value below the operator's floor (default: rent < $400/mo or pay-per-call < $300/mo at maturity).
- No buyers, or no network coverage.
- Emergency niche whose money SERPs are fully captured above organic (calls go to the pack and LSAs).
- A fake GBP, fake reviews or expired-domain tricks are needed to compete.

## Step 4: Score and shortlist
Weights by model are in `.claude/agents/niche-scout.md`. Shortlist 3-5 with: why this niche, why now, why this
operator, the biggest risk, and the cheapest kill test (e.g. "call 5 contractors and ask if they'd pay $50/lead",
"check if the network covers ZIP 741xx").

## Nationwide niches (model = nationwide)
- **Unit of analysis**: national demand x the share of it you can rank for x payout x billable rate x buyer coverage.
- **Coverage**: ask the network which states and ZIPs, which hours (timezones), what caps, and what happens to out-of-coverage calls.
- **Site model**: one brand; national hub pages per service; location pages ONLY where you have unique local data
  (Census housing age, climate risk, permit rules, local costs). Start with the top 20-50 metros by demand, not 5,000 towns.
- **Best-fit verticals**: emergency home services (water damage, plumbing, HVAC, garage door, pest), towing and
  roadside, plus compliance-gated legal and insurance verticals only with a CLEAR ruling.
- **Moat**: a brand, speed and genuinely useful tools or guides (cost calculators, emergency checklists). Thin city
  pages won't hold rankings.

## Evergreen R&R niche archetypes (starting hypotheses only, always validate)
- **Outdoor heavy trades**: tree service, land clearing, excavation, concrete, fencing, hardscaping, paving
- **Structural**: foundation repair, basement waterproofing, crawl spaces
- **Restoration**: water damage, mold, fire, biohazard
- **Rural mechanical**: septic, well pumps, water treatment, radon
- **Hauling**: junk removal, dumpster rental, portable toilets
- **Emerging**: epoxy floors, EV chargers, standby generators, artificial turf

## Output
`projects/<slug>/research/01-niche.md` (analyst memo) and `data/niche-ranking.csv`. Feeds Gate 1 in the `war-room` skill.
