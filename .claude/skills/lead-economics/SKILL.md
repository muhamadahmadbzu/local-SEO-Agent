---
name: lead-economics
description: "Method for valuing leads and pricing lead-gen sites. It covers value per lead for the tenant, the fair per-lead and rent price, Google Ads and LSA alternative cost, pay-per-call revenue (payout, buffer, billable share), the ramp and cash-flow model, break-even, asset value, sensitivity and kill criteria. Use it for \"lead value\", \"how much can I earn\", \"what should I charge\", \"rent price\", \"pay per call payout\", \"ROI\", or comparing projects."
argument-hint: "<niche-id> [project slug] [--leads cons base strong]"
---

# Lead Economics

Owner: `lead-value-economist`. Request: $ARGUMENTS

## Core formulas
```
revenue per lead (tenant)   = average ticket x close rate
value per lead (tenant)     = revenue per lead x gross margin
fair price per lead         = 20%-45% of value per lead
Google Ads cost per lead    = CPC / landing conversion (≈10%)
rent band                   = leads/mo x fair price per lead   (capped by market reality)
pay-per-call revenue        = leads x call share (≈80%) x billable share (≈50-70%) x payout
Ads-equivalent value        = organic clicks x CPC  (from keyword report)
```

## Run it
```
# from measured keywords + SERP difficulty (preferred)
python3 scripts/lead_economics.py --niche tree-service --keywords projects/<slug>/data/keywords.csv --difficulty 42 \
    --model hybrid --out projects/<slug>/research/05-economics-data.md
# from explicit lead scenarios and tenant facts
python3 scripts/lead_economics.py --niche roofing --leads 6 15 30 --ticket 9000 --close-rate 0.25 --margin 0.35 --cpc 28 --rent 1500
```
Key flags: `--model rank_and_rent|pay_per_call|hybrid`, `--payout`, `--billable`, `--min-leads-to-rent` (default 5),
`--sales-lag` (months to sign a tenant after proof), `--build-cost`, `--monthly-cost`, `--link-budget`,
`--link-months`, `--horizon` and `--json`.

## The three price anchors (all must appear in the memo)
1. **Value anchor**: the tenant's gross profit per lead. If you charge more than ~45% of it, they churn.
2. **Alternative-cost anchor**: what the tenant pays elsewhere. Google Ads CPL (CPC divided by about 10%), LSA cost
   per lead (ask a contractor, or use the observed LSA category range), and Angi or Thumbtack lead prices (shared leads, lower quality).
3. **Market anchor**: the niche rent prior (`niche_scorer.py show <id>`) and comparable deals.
Price where all three overlap. Your first price should be an easy yes. Raise it at renewal with call data.

## Pricing structures
| Structure | When | Watch out |
|---|---|---|
| Flat monthly rent | Steady volume, trusting tenant | Tenant feels it during slow months, so show seasonality upfront |
| Per qualified call/lead | First deal, skeptical tenant | Define "qualified" precisely (duration ≥ 60-90s, in service area, not spam or a duplicate within 30 days) |
| Base + per lead | Volatile volume | More admin, so automate the reporting |
| Pay-per-call network | No tenant yet, emergency niches, nationwide | Payout varies by ZIP and hour; buffer and duplicate rules; reconcile monthly |
| Hybrid | Default for new sites | Sell calls via the network until a tenant signs, then switch routing |

## Ramp and cash flow
Months to full ranking come from difficulty (< 35: 3 months; 35-55: 6; 55-70: 10; > 70: 14), plus 1 month of
indexing delay. The tool simulates pay-per-call revenue until leads reach the rental threshold, then rent from the
month after (the sales lag). Report the break-even month, max cash at risk and 24-month net for all three scenarios.

## Sensitivity (always)
Rerun with leads at -50%, the ticket at -30% and months-to-rank x1.5. If the base case only works when every
assumption is favorable, call it speculative.

## Kill criteria (examples)
- Not in the top 10 for the core keyword by month 5 (moderate difficulty) -> stop link spend and reassess on-page and SERP.
- Fewer than 5 calls a month by month 7 -> pay-per-call only, or sell the site.
- No tenant after 20 qualified conversations -> drop the price to the floor, switch to per-lead, or pay-per-call.
- Tenant churn twice in 12 months -> the niche's lead quality or price is wrong, so revisit.

## Portfolio comparison
Rank projects by payback months, max cash at risk and expected 24-month net. Put the next dollar where the
payback is fastest and the risk independent of other sites (a different niche or state).

## Output
`research/05-economics.md` (analyst memo) + `research/05-economics-data.md` (tool output).
