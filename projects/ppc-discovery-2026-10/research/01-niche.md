# Niche shortlist for pay-per-call-first hybrid — niche-scout

| Project | Gate / phase | Date | Question |
|---|---|---|---|
| `projects/ppc-discovery-2026-10` | Phase 1 niche research (feeds Gate 1) | 2026-10-03 | Which 3-5 US niches should advance for a <$500 site monetized first by public pay-per-call offers, then a monthly tenant? |

## Bottom line
RECOMMEND WITH CONDITIONS: **Tree Service** as the top pick. It is the only niche with several public OfferVault pay-per-call listings (static and high-ticket variants, 90s duration) plus strong tenant priors (R&R #2, rankability 6, risk 9.4). **Water Damage** (highest payouts, SEO traffic explicitly allowed in a public snippet, but harder SERPs), **Pest Control** (many offers, but "experience required" and LSA-heavy) and **Septic** (best tenant fallback, but the pay-per-call offer is thin) advance with conditions. The main risk is that every offer page here was seen **only through search-engine snippets**. offervault.com, callscaler.com, marketcall.com and servicedirect.com all returned EGRESS_BLOCKED from this environment, so new-affiliate approval, SEO-traffic permission and geo caps stay UNKNOWN until the operator applies.

## Recommendation and score
Prior scores come from `niche_scorer.py` (risk-tolerance medium, no geo) [PRIOR]. Payout ranges are network-published ranges, not expected earnings.

| # | Niche | PPC score | R&R score | Rankability (0-10) | Public offer evidence | Published payout | Seasonality | Key risk | Kill test | Position |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Tree Service (`tree-service`) | 66.9 | 74.5 | 6.0 | 3 OfferVault listings (E-1..E-3) | $25-55; $27-135; $72-360 (high-ticket) [OBSERVED-snippet] | Spring/summer storm peaks; Dec-Feb trough in northern states [PRIOR/ASSUMPTION, Trends not pulled] | Offers may cap or exclude ZIPs; the "high ticket" variant may need a qualified job type | Apply to 2 tree offers; get written confirmation of SEO allowed + target-ZIP coverage within 7 days | RECOMMEND WITH CONDITIONS |
| 2 | Water Damage (`water-damage`) | 75.0 | 70.4 | 5.0 | OfferVault listing + Marketcall SEO case study + CallScaler category (E-4..E-6) | $35-90 typical; dynamic $70-1,000 premium [OBSERVED-snippet] | Fairly flat; freeze and storm spikes [PRIOR] | Emergency SERP likely captured by LSAs/pack + national franchises (Servpro etc.); heavy spam competition | 3 SERP checks in candidate city: if organic #1 sits below LSAs + 3 ads + pack + AIO, kill | RECOMMEND WITH CONDITIONS |
| 3 | Pest Control (`pest-control`) | 71.5 | (not in R&R top 25) | 4.0 | 4+ OfferVault listings (E-7..E-9) | $25 (120s after IVR, 7am-11pm EST); up to $60; RTB $2-60 [OBSERVED-snippet] | Spring-summer peak, winter trough in the north; flatter in the South [PRIOR] | One listing says "experience required"; LSA-heavy; national brands (Terminix/Orkin) own the SERPs | Ask the network whether a new SEO publisher is accepted; SERP check for national-brand share of top 5 | RECOMMEND WITH CONDITIONS (South/inland only) |
| 4 | Septic Services (`septic`) | 66.4 | 76.8 (R&R #1) | 9.0 | Only a CallScaler category page for "septic tank installation" (E-10); no OfferVault septic listing found | "$30-80 typical" (generic category text) [OBSERVED-snippet] | Mild; spring/fall pumping [PRIOR] | Pay-per-call accessibility weak, so it may need to go tenant-first, which delays revenue | Ask 2 networks for a live septic campaign covering target ZIPs; if none, call 5 local septic firms and ask about $X/lead | RECOMMEND WITH CONDITIONS (tenant-led) |

Alternate (not shortlisted): Drain/Sewer (`drain-sewer`, PPC 73.5 / R&R 74.0, rankability 5). Plumbing offers exist ($20-80, 90-120s buffer) [OBSERVED-snippet, E-11], but the niche is LSA-heavy. Revisit it if tree service fails the coverage test.

Weighted pay-per-call scores from the agent rubric (1-5; Lead value 25, Urgency 20, Demand 20, Rankability 15, Risk 15, Stability 5) [ASSUMPTION: my judgment, mapped from priors plus offer evidence]:

| Niche | Value | Urgency | Demand | Rank | Risk | Stab | Weighted |
|---|---|---|---|---|---|---|---|
| Water damage | 4 | 5 | 3 | 2 | 3 | 4 | 3.55 |
| Tree service | 3 | 4 | 4 | 3 | 5 | 3 | 3.70 |
| Pest control | 3 | 4 | 5 | 2 | 4 | 3 | 3.50 |
| Septic | 3 | 4 | 3 | 5 | 5 | 4 | 3.85 (but offer accessibility = UNKNOWN, which overrides) |

Offer accessibility, the operator's key criterion, breaks the tie in tree service's favor: it has the most distinct public listings with a stated buffer, and a strong tenant fallback.

## Evidence
All OfferVault, CallScaler, Marketcall and Service Direct pages were **blocked by the egress proxy on 2026-10-03** (WebFetch EGRESS_BLOCKED). Their contents below come from WebSearch result summaries of those URLs dated 2026-10-03. Treat each one as OBSERVED-snippet (lower confidence) until someone opens the page in a browser.

| # | Claim | Evidence | Label | Source (date) | Confidence |
|---|---|---|---|---|---|
| E-1 | Tree service PPC, nationwide 24/7 | $25-55 | OBSERVED-snippet | https://offervault.com/offer/6bad9e6eadd05b7618033d683997a9a2/tree-service-calls-nationwide-24-7-dollar25-dollar55 (2026-10-03) | Med |
| E-2 | Tree service leads, static payment | $27-135, live transfer, min 90s | OBSERVED-snippet | https://www.offervault.com/offer/d31bd507985a229b096ec04861d6ae5b/tree-service-leads-pay-per-call-fix-static-payment-campaign (2026-10-03) | Med |
| E-3 | Tree service high-ticket | $72-360, live transfer, min 90s | OBSERVED-snippet | https://www.offervault.com/offer/3b28f9aee9f4262cdae6c7a040978e35/tree-service-leads-high-ticket-pay-per-call-fix-static-payment-campaign (2026-10-03) | Med |
| E-4 | Water damage PPC on OfferVault | Real-time inbound; payout by dynamic duration. Exact payout not confirmed (snippet mixes several sources) | OBSERVED-snippet | https://www.offervault.com/offer/00e0f1471a45abf70f1f12a9e138c63c/water-damage-restoration-pay-per-call (2026-10-03) | Low |
| E-5 | Water damage typical payout range | $35-90 per qualified call; search summary says traffic sources incl. "Paid Search, SEO, Social, GMB" | OBSERVED-snippet | https://callscaler.com/marketplace/water-damage (2026-10-03) | Low-Med |
| E-6 | An affiliate earned $25,000 on water damage with SEO traffic (network marketing claim) | case study | OBSERVED-snippet | https://www.marketcall.com/blog/waterdamagecasestudy (2026-10-03) | Low (self-promotional) |
| E-7 | Pest control nationwide 24/7 | up to $60; "experience required" in the URL slug | OBSERVED-snippet | https://www.offervault.com/offer/07712b579dc92dc53e24762d7f54121d/pest-control-nationwide-24-7-experience-required (2026-10-03) | Med |
| E-8 | Pest control, 120s after IVR | $25; Mon-Sun 7am-11pm EST | OBSERVED-snippet | https://www.offervault.com/offer/64024c6412a65b8213a89a635965626a/pest-control-or-pay-per-call-or-120-seconds-after-ivr (2026-10-03) | Med |
| E-9 | Pest control RTB | $2-60 | OBSERVED-snippet | https://www.offervault.com/offer/c294f35d79da22a3eeaaa8591db45b92/pest-control-rtb-campaign-or-pay-per-call (2026-10-03) | Med |
| E-10 | Septic tank installation PPC | "$30-80 typical" (generic marketplace copy, no specific campaign) | OBSERVED-snippet | https://callscaler.com/marketplace/septic-tank-installation (2026-10-03) | Low |
| E-11 | Plumbing PPC | $20-80 dynamic, 90-120s billable | OBSERVED-snippet | https://www.offervault.com/offer/adb101e9de33e173f4d444acce34490b/plumbing-pay-per-call (2026-10-03) | Med |
| E-12 | Basement waterproofing PPC typical | $25-70; Service Direct average home-service payout ~$40 (search summary) | OBSERVED-snippet | https://callscaler.com/marketplace/basement-waterproofing ; https://servicedirect.com/pay-per-lead-affiliate-program/ (2026-10-03) | Low |
| E-13 | Networks vary: some need approval to join and again per offer; Marketcall is described as fast-approval / beginner-friendly | review sites | OBSERVED-snippet | https://www.affinsight.com/blog/pay-per-call-affiliate-networks ; https://diggitymarketing.com/best-affiliate-programs/pay-per-call/ (2026-10-03) | Low |
| E-14 | Prior scores, rent bands, rankability and flags | see tables | PRIOR | data/niches.json via scripts/niche_scorer.py (2026-10-03) | Med |
| E-15 | Search volumes, Trends shapes, local buyer counts | not measured | UNKNOWN | No keyword access; Trends not pulled. Get them from a Keyword Planner export + Google Trends 5y US/state + map-pack counts in Phase 2 | - |

## Assumptions and sensitivity
| Assumption | Value used | Why | If wrong by... | Effect |
|---|---|---|---|---|
| A new affiliate can be approved for at least one tree/water/pest offer | yes, for at least 1 network | many listings, beginner-friendly networks cited (E-13) | if no network accepts a zero-history SEO publisher | The PPC-first plan fails and the project goes tenant-first, with septic or tree as the lead niche |
| SEO/organic traffic allowed | assumed for home services | one snippet lists SEO (E-5) | if offers are PPC-only/GMB-only | Kills that offer |
| Billable rate of calls (90-120s buffer) | 40-60% [ASSUMPTION] | typical for referral sites | ±20 pts | Changes monthly value roughly 1.5x |
| Floor of $300/mo pay-per-call at maturity | met by tree/water if ~6-12 billable calls/mo at $25-55 | arithmetic on the published low end | if demand per city < 10 billable/mo | Fails the floor; needs a wider area |

## Geography and seasonality fit
- Brief excludes CA, NY metro and New England; prefer inland mid-size.
- Tree service: wooded, storm-exposed inland South/Midwest (e.g. TN, MO, AR, OK, KY, inland NC/GA) [ASSUMPTION: canopy and storm frequency; confirm with us_states.json tags in market-selection].
- Pest control: the South (long season, termites) [PRIOR].
- Water damage: freeze-thaw Midwest plus storm-belt states [PRIOR].
- Septic: rural-fringe metros with low sewer coverage [PRIOR].
- Dead months: tree Dec-Feb (north), pest Nov-Feb (north). Trends not measured: UNKNOWN.

## Regulated verticals seen in pay-per-call markets (flagged, not shortlisted)
| Niche | Prior | Status |
|---|---|---|
| Personal injury, criminal defense | PPC #2 / #14, REGULATED | Legal: needs a compliance-officer ruling (bar advertising rules, referral-fee limits). Not shortlisted |
| Auto insurance | PPC #25, REGULATED | Insurance producer licensing and TCPA exposure. Not shortlisted |
| Bail bonds | PPC #20, REGULATED | State bail-agent rules. Not shortlisted |
| Dental implants | PPC #19 | Health advertising. Not shortlisted |
| Medicare, addiction treatment | - | BLOCK by default. Excluded |
| Moving, solar | - | Regulated per playbook. Excluded |

## Rejected and why
| Niche | Prior PPC score | Reason |
|---|---|---|
| Plumbing, HVAC, electrician, garage door | 77.4 / 76.6 / 69.1 / 68.8 | Rankability 3, LSA- and directory-heavy; emergency calls go to the pack (kill rule 4 likely). Garage door also carries SPAM-SCRUTINY |
| Roofing | 70.2 | LSA-heavy, storm-chaser and insurance-claim solicitation rules, risk 6 |
| Towing | 70.1 | Low ticket ($10-30 prior), spam scrutiny |
| Fire damage, biohazard | 71.6 / 70.1 | Demand 2.5; too few calls per mid-size city for a $300 floor on one site |
| Water heater, drain/sewer | 73.5 | Kept as alternates; LSA-heavy |
| Personal injury etc. | see above | Regulated |

## Risks
1. Offer access (high likelihood, high impact): zero-history publishers are often refused or held to caps. Mitigation: apply to 2-3 networks before buying a domain. The test costs $0.
2. Unverified offer details (certain, medium impact): all evidence is snippet-level because of the proxy. Mitigation: the operator screenshots offer pages with the date before Gate 1 closes.
3. SERP capture by LSAs and the map pack (medium-high, high impact for water damage and pest control): Mitigation: SERP checks in Phase 2 and a target on long-tail and cost/guide queries.

## What would change my mind
- A network confirms in writing that it does not accept SEO traffic or new publishers for tree service: tree drops and septic or water damage leads.
- A live septic offer covering the target ZIPs: septic becomes #1 (best rankability and tenant priors).
- Keyword Planner shows under ~150 combined monthly searches for core tree terms in candidate cities: tree drops.

## Open questions for the war room / other agents
- @operator: Apply to 2-3 pay-per-call networks (they do not need the site yet) and report approval, SEO allowance, coverage, hours, caps and duplicate window. Do not spend money until Gate 1.
- @market-selector: Find inland mid-size cities (40k-400k) for tree service and septic, outside CA, NY metro and New England.
- @lead-value-economist: Calls/mo needed at $25-55 and a 40-60% billable rate to clear the $300 floor.
- @compliance-officer: Recording disclosure and referral-service disclosure for live-transfer offers. TCPA does not apply to inbound-only calls, so confirm the model stays inbound-only.

## Data and files
- projects/ppc-discovery-2026-10/data/niche-ranking.csv (pay_per_call, medium, top 40)
- Rank & rent ranking: run `python3 scripts/niche_scorer.py rank --model rank_and_rent --top 25 --risk-tolerance medium` (output reproduced in the tables above)
