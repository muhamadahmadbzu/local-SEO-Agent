# Lead economics - Plumbing

## Assumptions

| Input | Value | Source |
|---|---|---|
| Average ticket | $612 | niche prior (geo-mean of [150, 2500]) |
| Tenant close rate | 50% | default for emergency niches |
| Tenant gross margin | 40% | user/default |
| Median CPC | n/a | user |
| Pay-per-call payout | $52 | niche prior midpoint |
| Calls share / billable share | 80% / 50% | default |
| Months to full ranking | 9 | assumed |
| Build cost / monthly cost / links | $60 / $15 / $0 x 6 mo | default |

## What a lead is worth

- Revenue per lead to the tenant: **$306** (ticket x close rate)
- Gross profit per lead to the tenant: **$122**
- Fair price per exclusive lead: **$24 - $55**
- Tenant's Google Ads cost per lead: **n/a** (CPC / 10% conversion)
- Niche market priors: rent [800, 2500] / mo, per lead [35, 100], pay-per-call [25, 80]

## Monthly potential at full ranking

| Scenario | Leads/mo | Value-based rent band | Pay-per-call/mo | Ads-equivalent/mo |
|---|---|---|---|---|
| conservative | 3.0 | $50 - $150 | $63 | - |
| base | 8.0 | $200 - $450 | $168 | - |
| strong | 15.0 | $350 - $850 | $315 | - |

**Recommended rent:** floor $50 | target $300 | stretch $850 per month

## 24-month cash flow (pay_per_call)

| Scenario | Rented from month | Break-even month | Max cash at risk | Net after 24 mo |
|---|---|---|---|---|
| conservative | never | 8 | $96 | $777 |
| base | never | 5 | $90 | $2,772 |
| strong | never | 4 | $90 | $5,565 |

<details><summary>Base scenario month by month</summary>

| Month | Leads | Revenue source | Revenue | Cost | Cumulative |
|---|---|---|---|---|---|
| 1 | 0.0 | ppc | 0 | 15 | -75 |
| 2 | 0.0 | ppc | 0 | 15 | -90 |
| 3 | 1.1 | ppc | 24 | 15 | -81 |
| 4 | 2.3 | ppc | 48 | 15 | -48 |
| 5 | 3.4 | ppc | 72 | 15 | 9 |
| 6 | 4.6 | ppc | 96 | 15 | 90 |
| 7 | 5.7 | ppc | 120 | 15 | 195 |
| 8 | 6.9 | ppc | 144 | 15 | 324 |
| 9 | 8.0 | ppc | 168 | 15 | 477 |
| 10 | 8.0 | ppc | 168 | 15 | 630 |
| 11 | 8.0 | ppc | 168 | 15 | 783 |
| 12 | 8.0 | ppc | 168 | 15 | 936 |
| 13 | 8.0 | ppc | 168 | 15 | 1089 |
| 14 | 8.0 | ppc | 168 | 15 | 1242 |
| 15 | 8.0 | ppc | 168 | 15 | 1395 |
| 16 | 8.0 | ppc | 168 | 15 | 1548 |
| 17 | 8.0 | ppc | 168 | 15 | 1701 |
| 18 | 8.0 | ppc | 168 | 15 | 1854 |
| 19 | 8.0 | ppc | 168 | 15 | 2007 |
| 20 | 8.0 | ppc | 168 | 15 | 2160 |
| 21 | 8.0 | ppc | 168 | 15 | 2313 |
| 22 | 8.0 | ppc | 168 | 15 | 2466 |
| 23 | 8.0 | ppc | 168 | 15 | 2619 |
| 24 | 8.0 | ppc | 168 | 15 | 2772 |

</details>

Indicative asset value once rented at target: $6,840 - $10,260 (24-36x monthly net, a common small-website multiple, not an appraisal).

## Notes

- Leads supplied manually (state where they came from in the memo).
- Every value-per-lead input should come from the tenant conversation (ticket, close rate) once one exists.
- Kill criteria belong in the IC decision: e.g. 'fewer than N leads/mo by month M -> pivot or sell calls only'.
