# Lead economics - Roofing

## Assumptions

| Input | Value | Source |
|---|---|---|
| Average ticket | $2,739 | niche prior (geo-mean of [500, 15000]) |
| Tenant close rate | 35% | default for mixed niches |
| Tenant gross margin | 40% | user/default |
| Median CPC | n/a | user |
| Pay-per-call payout | $62 | niche prior midpoint |
| Calls share / billable share | 80% / 50% | default |
| Months to full ranking | 9 | assumed |
| Build cost / monthly cost / links | $60 / $15 / $0 x 6 mo | default |

## What a lead is worth

- Revenue per lead to the tenant: **$959** (ticket x close rate)
- Gross profit per lead to the tenant: **$383**
- Fair price per exclusive lead: **$77 - $173**
- Tenant's Google Ads cost per lead: **n/a** (CPC / 10% conversion)
- Niche market priors: rent [1000, 3000] / mo, per lead [50, 150], pay-per-call [35, 90]

## Monthly potential at full ranking

| Scenario | Leads/mo | Value-based rent band | Pay-per-call/mo | Ads-equivalent/mo |
|---|---|---|---|---|
| conservative | 3.0 | $250 - $500 | $75 | - |
| base | 8.0 | $600 - $1,400 | $200 | - |
| strong | 15.0 | $1,150 - $2,600 | $375 | - |

**Recommended rent:** floor $250 | target $1,000 | stretch $2,600 per month

## 24-month cash flow (pay_per_call)

| Scenario | Rented from month | Break-even month | Max cash at risk | Net after 24 mo |
|---|---|---|---|---|
| conservative | never | 8 | $94 | $1,005 |
| base | never | 5 | $90 | $3,380 |
| strong | never | 4 | $90 | $6,705 |

<details><summary>Base scenario month by month</summary>

| Month | Leads | Revenue source | Revenue | Cost | Cumulative |
|---|---|---|---|---|---|
| 1 | 0.0 | ppc | 0 | 15 | -75 |
| 2 | 0.0 | ppc | 0 | 15 | -90 |
| 3 | 1.1 | ppc | 29 | 15 | -76 |
| 4 | 2.3 | ppc | 57 | 15 | -34 |
| 5 | 3.4 | ppc | 86 | 15 | 36 |
| 6 | 4.6 | ppc | 114 | 15 | 136 |
| 7 | 5.7 | ppc | 143 | 15 | 264 |
| 8 | 6.9 | ppc | 171 | 15 | 420 |
| 9 | 8.0 | ppc | 200 | 15 | 605 |
| 10 | 8.0 | ppc | 200 | 15 | 790 |
| 11 | 8.0 | ppc | 200 | 15 | 975 |
| 12 | 8.0 | ppc | 200 | 15 | 1160 |
| 13 | 8.0 | ppc | 200 | 15 | 1345 |
| 14 | 8.0 | ppc | 200 | 15 | 1530 |
| 15 | 8.0 | ppc | 200 | 15 | 1715 |
| 16 | 8.0 | ppc | 200 | 15 | 1900 |
| 17 | 8.0 | ppc | 200 | 15 | 2085 |
| 18 | 8.0 | ppc | 200 | 15 | 2270 |
| 19 | 8.0 | ppc | 200 | 15 | 2455 |
| 20 | 8.0 | ppc | 200 | 15 | 2640 |
| 21 | 8.0 | ppc | 200 | 15 | 2825 |
| 22 | 8.0 | ppc | 200 | 15 | 3010 |
| 23 | 8.0 | ppc | 200 | 15 | 3195 |
| 24 | 8.0 | ppc | 200 | 15 | 3380 |

</details>

Indicative asset value once rented at target: $23,640 - $35,460 (24-36x monthly net, a common small-website multiple, not an appraisal).

## Notes

- Leads supplied manually (state where they came from in the memo).
- Every value-per-lead input should come from the tenant conversation (ticket, close rate) once one exists.
- Kill criteria belong in the IC decision: e.g. 'fewer than N leads/mo by month M -> pivot or sell calls only'.
