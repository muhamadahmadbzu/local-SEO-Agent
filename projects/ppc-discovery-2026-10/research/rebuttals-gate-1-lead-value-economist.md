# Rebuttals — Gate 1 — ppc-discovery-2026-10

Each owning agent adds a section. One row per objection addressed.

## lead-value-economist
Date 2026-10-03. No new external evidence was gathered in this round: offer pages are still blocked from this environment, so I bring no REBUTs and do not claim any. All reruns used `scripts/lead_economics.py --model pay_per_call --leads 3 8 15 --billable 0.5 --build-cost 60 --monthly-cost 15 --link-budget 0 --difficulty 50`. Difficulty 50 is an ASSUMPTION giving full rank at month 7, while the original memo used month 9, so the 24-month nets below are **not** comparable to the earlier memo. They are comparable to each other.

| Objection | Response | New evidence (labeled, sourced) / revised estimate / mitigation plan (cost, deadline) |
|---|---|---|
| O-1 (FATAL if true) | **CONCEDE + MITIGATE** | I agree that no niche ranking matters until one network accepts a zero-history SEO publisher. Plan: the operator applies to 2-3 networks covering tree, water damage and plumbing, and records the payout, buffer, SEO allowed (Y/N), ZIP coverage, hours, caps and duplicate window, with a screenshot, URL and date. Cost $0. Deadline 2026-10-17 (14 days). No domain is bought before then (this needs operator approval in any case). Fallback if there are 0 approvals: re-score as a direct per-call deal with a local contractor (tenant-first, needs operator approval to contact businesses). Septic and tree lead that path on R&R priors. |
| O-2 (MAJOR) | **CONCEDE** | Water damage rerun at the scout's E-5 snippet range (OBSERVED-snippet, callscaler.com/marketplace/water-damage, 2026-10-03). 24-mo net PPC-only (cons/base/strong): **$35/call: $462 / $1,932 / $3,990. $62.5: $1,155 / $3,780 / $7,455. $90: $1,848 / $5,628 / $10,920.** PPC $/mo at the base 8 leads falls from $400 (prior $125) to **$200** at $62.5. $500/mo needs **8 billable calls = about 20 leads/mo**, which is above the strong scenario. I withdraw the claim that water damage is "the only niche that reaches $500/mo on PPC alone". **No niche reaches $500/mo on PPC alone under base assumptions.** |
| O-3 (MAJOR) | **CONCEDE** (reconciled below) | I rescored everything on one common input set (table below). HVAC is withdrawn: rankability 3, LSA-heavy and stability 6 [PRIOR], and I have no observed SERP path. The economics alone do not offset that on a $0 link budget. |
| O-4 (MAJOR) | **CONCEDE + MITIGATE** | Demand stays ASSUMPTION. Sensitivity: at -50% leads (4/mo base), every niche's PPC income halves (water damage at $62.5 is about $100/mo). Plan: free Keyword Planner export for core terms of the 3-4 advancing niches in 3-5 candidate cities, plus Trends 5y by state. Cost $0, about 1 hour of operator or keyword-researcher time, before Gate 2 (target 2026-10-24). Kill rule: if measured core volume cannot support about 8 leads/mo in any candidate city, that niche does not reach Gate 3. |
| O-5 (MAJOR) | **MITIGATE** | No SERP was observed, so I can't rebut. Plan: `serp_audit.py template`, 3 location-set mobile SERPs per niche in 2 cities. Record LSA/ad/pack/AIO counts and the national/franchise/directory share of the top 10. About 30 min per niche, $0, before Gate 2. Economic consequence: I apply a provisional 0.7x lead haircut [ASSUMPTION] to water damage and drain/sewer until SERPs are seen. Kill rule: organic #1 below the fold on mobile in both cities means that niche is dropped. |
| O-8 (MAJOR) | **CONCEDE** | Pest control does not advance. Tenant gross profit is $59/lead, fair price $15-27 [PRIOR], and there is an "experience required" offer term with no evidence for a South exception. It can be reopened only with an observed offer that accepts new SEO publishers plus a SERP where national brands hold under 50%. |
| O-10 (MINOR) | **CONCEDE** | Headline is now PPC-only conservative/base. The hybrid $31k/$12k figures are withdrawn as expected values until a buyer is named and anchor 2 (Ads CPL) is measured. |

### Reconciled ranking (one common input set)
Inputs are the same for every niche: leads 3/8/15 [ASSUMPTION], call share 80%, billable 50% [ASSUMPTION], full rank at month 7 [ASSUMPTION], $60 build, $15/mo, $0 links. Payout is the midpoint of the **observed snippet** range where one exists (OBSERVED-snippet, low confidence). Calls needed for $500/mo = 500 / payout (billable). Leads needed = billable / 0.4.

| Niche | Payout used (source) | Billable calls/mo for $500 | Leads/mo for $500 | PPC $/mo at base 8 leads | 24-mo net PPC-only cons/base/strong | Rankability [PRIOR] | Offer evidence | Verdict |
|---|---|---|---|---|---|---|---|---|
| Water damage | $62.5 (E-5, $35-90) | 8 | 20 | $200 | $1,155 / $3,780 / $7,455 | mid | 1 marketplace snippet listing SEO | **Advance** (conditions O-1, O-5, compliance C-2) |
| Tree service | $40 (E-1, $25-55; the high-ticket E-3 is excluded as a ceiling) | 13 | 31 | $128 | $588 / $2,268 / $4,620 | 6 | 3 listings, 90s buffer | **Advance** (lowest compliance risk, credible tenant fallback) |
| Drain/sewer | $50 (E-11 plumbing, $20-80) | 10 | 25 | $160 | $840 / $2,940 / $5,880 | 5 | 1 plumbing listing | **Advance** (conditional on SERP, since it is LSA-heavy) |
| Septic | $55 (E-10, generic $30-80, no live campaign) | 9 | 23 | $176 | $966 / $3,276 / $6,510 | 9 | none live | **Advance as tenant-first fallback only** (O-7) |
| HVAC | prior $50, no snippet | 10 | 25 | ~$160 | n/a | 3 | none observed | Do not advance |
| Pest control | prior $48 | 11 | 26 | ~$154 | n/a | low (national brands) | "experience required" | Do not advance |

Reading: on observed payouts, water damage still earns the most per call, but its lead is about 1.25-1.6x rather than 2.5x. Tree service has the best offer evidence but the lowest payout. **$500/mo is a tenant-step target in every niche.** PPC-only realistically pays $130-200/mo at base, which covers costs and funds proof. That is enough for a $500 bootstrap but not the income goal. Every niche remains **speculative** until O-1 and O-4 are resolved.

**Revised advance set: tree service, water damage, drain/sewer. Septic is a tenant-first fallback.** This matches the devils-advocate's recommended set.

## Rulings (devils-advocate / compliance-officer)
| Objection | Ruling | Reason |
|---|---|---|
| O-1 | RESOLVED / PARTIALLY / STANDS |  |
