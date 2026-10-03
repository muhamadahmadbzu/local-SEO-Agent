# Compliance playbook (US lead-gen sites)

Practical guardrails for the team, especially the `compliance-officer`. This is **not legal advice**. Rules change,
so re-verify against the primary source before a high-stakes ruling and record the retrieval date. Facts below were
checked on **2026-10-03**.

## 1. Google Business Profile
- Lead-generation agents and companies are **ineligible** for a Business Profile. The profile must belong to the
  business that actually serves the customer.
  Sources: [Business eligibility and ownership guidelines](https://support.google.com/business/answer/13763036),
  [Guidelines for representing your business](https://support.google.com/business/answer/3038177).
- **Team rule:** never create, buy or "borrow" a GBP for a rank-and-rent site. No virtual offices, coworking desks,
  UPS boxes or a friend's address. Map-pack visibility comes from the **tenant's own** verified profile linking to
  the rented site.

## 2. Google Search spam policies
- [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies): doorway pages, scaled
  content abuse (AI or human, method-agnostic), expired-domain abuse, site reputation abuse, link schemes, cloaking,
  hidden text, sneaky redirects and thin affiliation.
- [March 2024 announcement](https://developers.google.com/search/blog/2024/03/core-update-spam-policies) introduced
  scaled content abuse, expired-domain abuse and site reputation abuse. The **March 2026 spam update** hit templated
  location pages that only swap the city name
  ([Search Engine Land](https://searchengineland.com/google-releases-march-2026-spam-update-472411)), and an
  **August 2026 spam update** followed.
- **Team rule:** every indexable page needs unique purpose and substance. `qa_site.py` blocks near-duplicates at 50%
  or more shared 5-word phrases (names normalized) and warns at 30% or more. Fresh domains only.

## 3. Structured data
- FAQ rich results were restricted to authoritative government and health sites in 2023, then **retired** from
  Google Search in 2026 ([SEJ](https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/)).
  FAQPage markup is still valid vocabulary, but don't promise rich snippets.
- Review or rating markup about yourself (self-serving reviews) is ineligible. A lead-gen site has no reviews of its
  own, so the build never emits rating schema.
- In lead_gen mode, use Organization + Service (no address). Use a LocalBusiness subtype only in tenant mode, with real details.

## 4. Reviews and testimonials (FTC)
- Trade Regulation Rule on the Use of Consumer Reviews and Testimonials, **16 CFR Part 465**
  ([eCFR](https://www.ecfr.gov/current/title-16/part-465)), effective **October 21, 2024**. It bans fake or
  AI-generated reviews and testimonials, buying reviews or conditioning incentives on sentiment, undisclosed insider
  reviews, review suppression, company-controlled "independent" review sites, and fake social influence. Civil
  penalties apply per violation (inflation-adjusted annually).
- **Team rule:** no testimonials or ratings on a lead-gen site. In tenant mode, show only real, attributable reviews
  (better: link to the tenant's GBP). Review requests go to every customer: no gating, no incentives for positive reviews.

## 5. Truthful advertising and disclosure
- FTC Act Sec. 5 and state UDAP laws: no deceptive claims. A referral site must not imply it is the contractor.
- The build adds a referral disclosure to every page in lead_gen mode. The copy rules in CLAUDE.md ban "our team",
  "licensed & insured", years in business, awards, guarantees and so on, unless the business making the claim
  (the tenant) can substantiate them.

## 6. Contractor advertising and licensing
- Many states require the contractor's license number in advertising and restrict unlicensed advertising. Examples:
  California B&P [7030.5](https://law.justia.com/codes/california/code-bpc/division-3/chapter-9/article-2/section-7030-5/)
  (license number in ads) and 7027.1 (unlicensed advertising is a misdemeanor); Florida
  [489.119](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0489/Sections/0489.119.html)
  (license number in every advertisement).
- **Team rule:** lead_gen mode presents a referral service, never a contractor. Tenant mode shows the tenant's license
  number (site.json `tenant.license`). Look up the state board for the trade before launch in each state.

## 7. Calls, texts and consent
- **TCPA**: autodialed, prerecorded or AI-voice calls and texts for marketing need prior express written consent. The FCC's
  one-to-one consent rule was **vacated** by the 11th Circuit on Jan 24, 2025 (*Insurance Marketing Coalition v. FCC*;
  [summary](https://www.mofo.com/resources/insights/250130-eleventh-circuit-vacates-fcc-s-tcpa-one-to-one-consent-rule)).
  Best practice remains naming or limiting who will contact the consumer. The default form consent in site.json names
  "{brand} and one matched local provider".
- Inbound calls a consumer places to the site's number don't need TCPA consent. Outbound follow-up does.
- National Do Not Call Registry and internal DNC lists apply to outbound telemarketing.
- **Call recording**: several states require all-party consent. **Always** play a recording disclosure on tracked
  calls ("This call may be recorded for quality"). Configure it in the call-tracking platform.

## 8. Privacy
- Publish a privacy policy that matches reality (the build generates a template that must be reviewed). List form
  fields, call recordings, analytics, and sharing with the matched provider.
- Collect the minimum. Don't ask for health, financial or ID details on forms. State privacy laws (CCPA/CPRA and
  others) apply above thresholds, so check before scaling.

## 9. Regulated verticals (compliance memo required before Gate 1 advancement)
| Vertical | Main constraints | Default ruling |
|---|---|---|
| Legal (PI, criminal, etc.) | State bar advertising rules; restrictions on paying for referrals (ABA Model Rule 7.2 variants); disclaimers | CONDITIONAL: flat-fee advertising structures, state-by-state check |
| Insurance (auto, final expense) | Producer licensing if discussing or selling; state DOI rules; TCPA | CONDITIONAL: nationwide via licensed buyers only |
| Medicare | CMS third-party marketing organization rules, scripted disclaimers, recording | BLOCK unless a specialist is engaged |
| Debt / tax relief | FTC Telemarketing Sales Rule, state debt-settlement laws, no outcome promises | CONDITIONAL |
| Addiction treatment | Federal EKRA (18 U.S.C. 220), state patient-brokering laws, LegitScript for ads | **BLOCK** |
| Moving / auto transport | FMCSA broker authority for arranging interstate moves or transport | CONDITIONAL: route only to registered carriers or brokers; never act as a broker |
| Bail bonds | State licensing; commercial bail banned or eliminated in some states; Google Ads prohibits | CONDITIONAL: organic only, licensed states only |
| Solar | TCPA litigation, state solar consumer-protection rules, incentive claims | CONDITIONAL: experts only |
| Healthcare / dental | Advertising rules; HIPAA exposure for the tenant if forms collect health info | CONDITIONAL: no health details in forms |

## 10. Trademarks and networks
- No franchise or manufacturer marks in domains, brands or "authorized" claims.
- Pay-per-call offers: obey each network's allowed traffic sources, prohibited claims, recording requirements and
  brand-bidding rules. Read the terms before routing a single call.
