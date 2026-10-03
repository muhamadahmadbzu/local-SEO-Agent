---
name: monetization
description: "How to turn a ranking lead-gen site into revenue. It covers choosing rank & rent vs pay-per-call vs hybrid, finding and qualifying tenants, outreach sequences, call scripts and free-trial offers, objection handling, pricing structures and term sheets, pay-per-call network applications (payout, buffer, coverage, hours, caps), call routing and reconciliation, tenant reporting and renewals. Use it for \"find a tenant\", \"rent my site\", \"sell calls\", \"pay per call network\", \"pricing\", or \"contract\"."
argument-hint: "<project slug> [tenant | ppc | pricing | contract | report]"
---

# Monetization

Owners: `monetization-closer` (pipeline, outreach, deals, networks), `lead-value-economist` (pricing),
`compliance-officer` (terms, consent, claims). Gate 5 decides price and terms. Request: $ARGUMENTS

## Choose the path
| Situation | Path |
|---|---|
| No rankings yet, emergency niche with live offers | **Pay-per-call** now, tenant later (hybrid) |
| ≥ 5 calls/mo in a local niche with many buyers | **Rank & rent**: find a tenant |
| Planned/high-ticket niche, forms dominate | **Per-lead** to 1 buyer, or rent once volume is proven |
| Nationwide brand | **Network** (or several), routed by caller ZIP and hours |
| Tenant churned | Back to pay-per-call immediately (no dead air) while re-selling |

## Tenant acquisition (rank & rent)
1. **Prospect list** in `ops/tenant-pipeline.md`: 15-40 businesses from map results, LSA advertisers, Google Ads
   advertisers, state license lookups and BBB/Yelp. Columns: name, phone, website, license status, reviews, ad
   activity (LSA or Ads), size and capacity signals, score (A, B or C), status, notes.
2. **Qualify**: licensed and in good standing, decent reviews (you rent your reputation to them), capacity to take
   more work, already spends on leads (LSAs or Ads = an understood budget), answers the phone.
3. **Outreach** (templates in `templates/outreach/`):
   - `cold-call-script.md`: lead with "I have a customer calling about <service> in <town> right now. Do you want it?"
   - `cold-email-sequence.md`: 3 short emails with proof (call count, a sample recording) and a trial offer.
   - `trial-offer.md`: 7-14 days of calls free, routed to them, then a decision. Proof sells, and slides don't.
4. **Objections**: "I get enough work" (fill slow-season gaps and target higher-ticket jobs), "SEO doesn't work for
   me" (it's not SEO, it's calls; they only pay for calls they get), "Too expensive" (compare to their Ads/LSA cost
   per lead), "What if it stops?" (30-day out clause; you carry the ranking risk), "Is this exclusive?" (yes, by
   service and area).
5. **Close** on a price defended at Gate 5. Start simple: flat monthly, or per qualified call with a monthly cap.

## Term sheet essentials (`templates/outreach/rental-agreement-outline.md`, lawyer-finalized)
- The operator owns the domain, site, content and tracking number. The tenant gets exclusive use for the term.
- Lead definition (for per-lead deals): duration threshold, service area, unique within 30 days, not spam or a sales call.
- Price, payment in advance (card on file or ACH), initial term (3 months after the trial), and month-to-month after that.
- Exclusivity scope (services and towns). Either side can terminate with 30 days' notice.
- The tenant warrants license and insurance and supplies the license number, real photos and claims they can substantiate.
- No guarantee of rankings or volume. Monthly reporting. Call recordings are shared and handled per the privacy policy.
- The tenant's own GBP, reviews and customer relationships stay theirs.

## Pay-per-call (network or direct buyer)
1. Shortlist networks with live offers for the niche and geography (examples: Service Direct, Marketcall, eLocal and
   RingPartner, among others; verify each one's current offers and terms). Platforms like Ringba, Retreaver or
   TrackDrive handle routing and tracking.
2. Apply with `templates/outreach/ppc-network-application.md`: traffic source = organic SEO (sites listed), estimated
   volume, compliance (recording disclosure, no incentivized traffic).
3. Confirm in writing: payout, **buffer** (e.g. 90s), **duplicate window**, **hours and timezone**, **geo coverage**
   (states or ZIPs), **caps**, allowed and prohibited traffic and claims, recording requirements, payment terms and
   reporting access.
4. Routing: the tracking number forwards to the network's number (or your routing platform). Use ZIP-capture IVR for
   multi-geo sites. Handle after-hours with a 24/7 buyer or by setting expectations on the site.
5. Reconcile monthly: compare your logs (duration, caller ID) against billable calls. Dispute with recordings. Track
   the billable rate (target ≥ 60%). If it drops, check call quality, hours and buffer fit.

## Reporting and renewals
Monthly report (`templates/ops/monthly-report.md`): calls, durations, missed calls, sample recordings, top pages and
keywords, and next month's plan. Missed calls are the tenant's problem to fix; show them. Raise the price at renewal
only with data (volume up, or close-rate proof).

## Output
`ops/monetization.md` (path, offers or prospects, price, terms, status), `ops/tenant-pipeline.md`, `ops/outreach/*`,
and `decisions/gate-5-deal.md`.
