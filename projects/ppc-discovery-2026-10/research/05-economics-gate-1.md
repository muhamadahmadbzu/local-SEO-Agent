# Pay-per-call value bands for the Gate 1 niche shortlist (Lead Value Economist)

| Project | Gate / phase | Date | Question |
|---|---|---|---|
| `projects/ppc-discovery-2026-10` | Phase 1 niche research, feeds Gate 1 | 2026-10-03 | With a budget under $500 and pay-per-call first (tenant later), which niches have the best realistic value per call and the fastest path to first revenue? |

## Bottom line
**RECOMMEND WITH CONDITIONS: water damage restoration first, then HVAC, then a plumbing sub-niche (drain/sewer or water heater).** Water damage pays about 2.5x more per billable call than the trades (prior $50-200 vs $25-80), so it needs the fewest calls to cover the budget and to reach $500 a month. It also has the highest tenant value per lead among the high-volume niches. The main risk: every payout here is a PRIOR. OfferVault was blocked from this environment (egress 403), so nothing is OBSERVED yet. The ranking also depends on finding an offer that **accepts organic/SEO call traffic in the chosen ZIPs**. On these numbers alone, every niche is **speculative** until we have measured volume and a real offer.

## Recommendation and score
Value bands use `data/niches.json` priors (PRIOR, reviewed 2026-10). Lead scenarios are ASSUMPTION: 3 / 8 / 15 leads a month at full ranking (conservative / base / strong) for a new site in a mid-size inland city. Billable share is 50% (ASSUMPTION, conservative inside the 50-70% skill range), call share is 80%, there is a 2-month indexing delay, the site ranks fully at month 9 (ASSUMPTION for a new domain with no paid links), a tenant signs 3 months after proof, build cost is $60 and running cost is $15 a month.

| # | Niche | Payout / qualified call low-base-high (PRIOR) | Buffer (PRIOR) | Tenant gross profit / lead (tool, PRIOR inputs) | Fair price / lead (20-45%) | Rent band, niche prior / value-based at base 8 leads | PPC $/mo at full rank (cons/base/strong) | 24-mo net PPC-only (base) | 24-mo net hybrid (base) | Position |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Water damage (`water-damage`) | $50 / $125 / $200 | 90-180s | $775 | $155-349 | $1,500-3,500 / $1,250-2,800 | $150 / $400 / $750 | $7,180 | $31,180 | **RECOMMEND w/ conditions** |
| 2 | HVAC (`hvac`) | $25 / $50 / $75 | 60-120s | $300 | $60-135 | $800-2,500 / $500-1,100 | $60 / $160 / $300 | $2,620 | $12,220 | RECOMMEND w/ conditions (seasonal, LSA-heavy) |
| 3 | Drain & sewer (`drain-sewer`) | $25 / $48 / $70 | 60-120s | $268 | $54-121 | $600-1,800 / $450-950 | $57 / $152 / $285 | $2,468 | $10,688 | RECOMMEND w/ conditions (easier SERP than plumbing) |
| 4 | Water heater (`water-heater`) | $25 / $48 / $70 | 60-120s | $232 | $46-105 | $500-1,500 / $350-850 | $57 / $152 / $285 | $2,468 | $9,188 | RECOMMEND w/ conditions |
| 5 | Roofing (`roofing`) | $35 / $62 / $90 | 90-120s | $383 | $77-173 | $1,000-3,000 / $600-1,400 | $75 / $200 / $375 | $3,380 | $15,380 | Hold: strong for rent, weaker for PPC-first (mixed urgency, storm-chaser SERPs, state solicitation rules) |
| 6 | Biohazard cleanup (`biohazard-cleanup`) | $50 / $100 / $150 | 90-180s | $949 | $190-427 | $800-2,000 / $1,500-3,400 | $120 / $320 / $600 | $5,660 | $30,860 | Hold: few buyers and low volume, so 8 leads a month is unlikely. Add as a secondary page only |
| 7 | Fire & smoke damage (`fire-damage`) | $50 / $125 / $200 | 90-180s | $2,449 | $490-1,102 | $800-2,500 / capped | $150 / $400 / $750 | $7,180 | $38,680 | Do not build standalone: low demand (2.5/10). Make it a section of the water-damage site |
| 8 | Plumbing, general (`plumbing`) | $25 / $52 / $80 | 60-120s | $122 | $24-55 | $800-2,500 / $200-450 | $63 / $168 / $315 | $2,772 | $4,752 | DO NOT RECOMMEND head term (rankability 3/10). Go after a sub-niche (#3, #4) instead |
| 9 | Pest control (`pest-control`) | $25 / $48 / $70 | 60-120s | $59 (prior ticket geo-mean $424 ignores recurring-plan LTV) | $15-27 | $500-1,500 / $100-200 | $57 / $152 / $285 | $2,468 | $2,438 | DO NOT RECOMMEND as first site: national brands dominate the SERP and tenant value is thin |
| 10 | Towing (`towing`) | $10 / $20 / $30 | 60-90s | $35 | $8-16 | $300-900 / $50-100 | $24 / $64 / $120 | $796 | $1,336 | DO NOT RECOMMEND: low ticket, SPAM-SCRUTINY flag, local permit rules |

Excluded from the top 15: personal injury and criminal defense (REGULATED; under house rule 7 they need a compliance-officer ruling, and they don't fit a $500 bootstrap). Electrician, garage door (SPAM-SCRUTINY) and foundation repair ranked #11-15. Foundation repair (rankability 6, risk 9.4, payout $40-100) is the best alternate if water damage SERPs turn out to be franchise-locked.

### Time to first revenue (new organic site, ASSUMPTION)
- Months 0-2: indexing, no revenue. Offer approval can run in parallel (UNKNOWN: many networks need traffic proof or reject new SEO publishers).
- First billable call: **months 3-6** in low-competition sub-niches (drain/sewer, water heater, water damage in a mid-size city), **months 5-9** for HVAC, roofing and general plumbing.
- Steady 5+ calls a month (tenant-proof threshold): months 6-10 in the base case, never in the conservative case.
- First tenant: months 9-13 in the base case (the model puts the rent start at month 10).

## Budget arithmetic (under $500)
- **What $500 buys:** domain about $10-15/yr, free Cloudflare Pages hosting, $0 content (operator-written), a call-tracking number plus minutes about $5-20/mo (network-provided numbers are often free; UNKNOWN per network), and an optional ~$50 DataForSEO deposit for measured volume before Gate 3. Realistic 6-month spend: **$90-$250**. That leaves about $250+ in reserve, which is **not** enough for meaningful paid links. Ranking must come from on-page work, content depth and free or earned citations.
- **Break-even (recover about $150 of 6-month costs):** water damage needs about **2-3 billable calls in total** at $62.5-125/call (that is, about 1-2 billable calls a month over a quarter). The $48-52 trades need **about 3-6 billable calls in total**.
- **$500/month from pay-per-call alone:** water damage needs **4 billable calls/mo** at $125 (about 10 leads at 80% call share x 50% billable), or 10 billable at the $50 low payout. HVAC, plumbing and the subs need **10 billable calls/mo** at $50 (about 25 leads), which is above our base scenario. **So pay-per-call reaches $500/mo only in water damage under base assumptions. Everywhere else, $500/mo needs the tenant step.**

## Evidence
| # | Claim | Evidence (numbers) | Label | Source | Confidence |
|---|---|---|---|---|---|
| E-1 | Niche ranking | Top 15 by PPC score, risk filter medium | PRIOR | `niche_scorer.py rank --model pay_per_call --top 15 --risk-tolerance medium`, 2026-10-03 | Med |
| E-2 | Payout, buffer, rent, per-lead bands | See the table | PRIOR | `data/niches.json` via `niche_scorer.py show <id>` | Low-Med (varies by ZIP, buyer, hour) |
| E-3 | Gross profit per lead, cash flow | Tool output (prior ticket geo-mean x default close rate x 40% margin) | PRIOR + ASSUMPTION | `research/econ-runs/<niche>-<model>.md` | Low |
| E-4 | Observed network payouts | Could not fetch: offervault.com blocked by the egress proxy (2026-10-03) | UNKNOWN | Operator should check OfferVault and 2-3 PPC networks by hand | n/a |
| E-5 | Lead volumes | 3/8/15 leads/mo | ASSUMPTION | No keyword data (brief: no tools) | Low |
| E-6 | Google Ads CPL and LSA anchors | Not computed: no CPC data | UNKNOWN | Keyword Planner export needed (Phase 3) | n/a |

### Three price anchors (for water damage, the lead candidate)
1. **Value anchor:** gross profit $775/lead, so a fair price of $155-349/lead (tool, PRIOR inputs).
2. **Alternative-cost anchor:** Google Ads CPL is **UNKNOWN** (no CPC yet; it becomes CPC / 10% once we have the Keyword Planner export). The marketplace and LSA price for restoration is UNKNOWN; ask a contractor.
3. **Market anchor:** niche rent prior $1,500-3,500/mo, per-lead prior $75-250.
Two anchors overlap at about **$150-250/lead or $1,250-2,500/mo at 8 leads**. Under the evidence rule this is not yet defensible as a quoted rent (anchor 2 is missing), so it is indicative only.

## Assumptions and sensitivity
| Assumption | Value used | Why | If wrong by... | Effect on conclusion |
|---|---|---|---|---|
| Leads at full rank | 3/8/15 | No data | -50% (1.5/4/7.5) | Water damage base 24-mo net drops from $31.2k to $3.4k (never reaches the rent threshold). HVAC drops to $1.1k and roofing to $1.5k. **This is the assumption that kills the deal.** |
| Ticket (water damage) | $3,873 prior | Geo-mean | -30% ($2,700) with rank at 14 mo | Base still positive ($18.2k). Fair price falls to about $110-245/lead and target rent to about $1,400 |
| Months to rank | 9 | New domain, no links | x1.5 (14) | First rent slips from month 10 to month 13. Cash at risk stays about $90 |
| Billable share | 50% | Long 90-180s buffers in restoration | 30% | PPC revenue -40%. Water damage needs about 7 leads for $500/mo at the base payout |
| Offer accepts SEO traffic in the city | Yes | Required by the model | No offer | The PPC-first path fails. Fall back to direct per-call deals with a local contractor (needs operator approval) |
| Max cash at risk | about $90-115 | Bootstrap costs | Paid tools added | Still under $500 |

Note: the hybrid 24-month nets assume a tenant signs at the target rent. In the conservative case no tenant ever signs, and PPC-only nets are $660-2,430 over 24 months. That is the realistic floor.

## Risks
1. **Payout and acceptance (high likelihood, high impact):** networks set payouts by ZIP and hour, and many cap or reject organic publishers that are new. Mitigation: before Gate 2, have the operator get 2-3 real offers with written traffic rules for the shortlisted niches.
2. **Volume (medium likelihood, high impact):** at -50% leads, nothing reaches a tenant. Mitigation: get measured Keyword Planner volume before Gate 3, and choose a city where water damage plus fire/mold demand stacks.
3. **SERP pressure (medium likelihood, medium impact):** restoration franchises and LSAs in metros, and LSA-heavy trades. Mitigation: target a mid-size inland city, and check SERPs (Phase 4).
- Compliance note: never imply the site handles insurance claims for water or fire damage (some states restrict assignment of benefits and public adjusting). Roofing has state rules on insurance-claim solicitation.

## Kill criteria (proposed for the Gate 3 decision)
- No PPC offer that accepts organic traffic for the niche and city by Gate 2 -> drop the niche or switch to a direct contractor per-call deal.
- Measured core-term volume is too low to support about 8 leads a month (Phase 3) -> do not build.
- Fewer than 3 billable calls a month by month 7 -> stop new content and keep PPC only. Fewer than 5 calls a month by month 10 -> sell the site or the calls.
- No tenant after 20 qualified conversations -> drop to the floor ($450/mo water damage) or per-call pricing.

## What would change my mind
- Observed water damage offers for organic traffic paying under $50/call with buffers over 120s -> HVAC or drain/sewer moves to #1.
- Measured volume showing water damage under about 100 searches a month in all candidate cities -> sub-trade plumbing first.

## Open questions for the war room / other agents
- @operator: please check OfferVault and 2-3 pay-per-call networks by hand (water damage, HVAC, plumbing). Note the payout, buffer, allowed traffic and states, with URL and date. Also tell us your hours per week and your $/month target.
- @keyword-researcher: free Keyword Planner volumes and CPCs, so we can add the Ads CPL anchor.
- @compliance-officer: water damage claims and insurance language. Is roofing solicitation a concern in the candidate states?

## Data and files
- Tool runs: `projects/ppc-discovery-2026-10/research/econ-runs/*-pay_per_call.md`, `*-hybrid.md`
- Priors: `data/niches.json`
