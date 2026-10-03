# Compliance review — Gate 1 (war room Round 2) — ppc-discovery-2026-10

Date: 2026-10-03 · Reviewer: compliance-officer · Not legal advice. Items marked "counsel" need a lawyer.

## Scope reviewed
Niche-level eligibility for a pay-per-call-first, lead_gen referral site (tenant later) in a mid-size inland US market
(CA, NY metro, New England excluded per brief): tree service, water damage (incl. fire damage section), pest control,
septic, HVAC, plumbing drain/sewer, water heater. Reviewed: brief.md, 01-niche.md, 05-economics-gate-1.md,
compliance-playbook.md. No site copy, call flow or signed network terms exist yet, so rulings are niche-level.
Primary-source refetch was not done this round: offer pages were EGRESS_BLOCKED for the niche scout (01-niche.md), and
statute citations below are labeled PRIOR (playbook, checked 2026-10-03) or UNKNOWN/verify where not yet confirmed.

## Common conditions (apply to EVERY niche below; "CC-1..CC-8")
- **CC-1 GBP:** no Google Business Profile for the site, no address of any kind in lead_gen mode. Map pack only via the
  tenant's own verified GBP later. Source: GBP eligibility guidelines https://support.google.com/business/answer/13763036 (PRIOR, playbook 2026-10-03).
- **CC-2 Spam policies:** no city-swapped service-area pages; each page needs unique local substance and must pass
  `qa_site.py`; fresh domain only (no expired-domain purchase); no bought links/PBNs. Source: https://developers.google.com/search/docs/essentials/spam-policies (PRIOR, 2026-10-03).
- **CC-3 Identity/FTC Sec. 5:** referral disclosure on every page (build adds it), no "our technicians", "licensed &
  insured", years in business, guarantees, response-time promises ("on-site in 30 min") or prices the operator cannot
  substantiate. No testimonials, ratings or review schema (16 CFR 465).
- **CC-4 Brand/trademark:** no franchise or manufacturer names (Servpro, Terminix, Orkin, Roto-Rooter, Carrier, Rheem,
  etc.) in domain, brand, headings or ads; no "authorized dealer"; obey each offer's trademark clause.
- **CC-5 Call recording:** recording disclosure played at the start of every tracked call (call-tracking platform AND
  confirm the network's IVR does it). Inland all-party-consent states that may be in play include e.g. IL, PA, MI
  (contested), MT, NV, WA, MD, FL [PRIOR/general knowledge, verify per state before launch]; the always-disclose rule
  makes the per-state question moot.
- **CC-6 TCPA:** inbound calls only. No outbound autodialed/prerecorded/AI calls or texts. If a form exists, consent text
  names "{brand} and one matched local provider"; no sale of form leads to multiple buyers without matching consent;
  honor DNC/STOP.
- **CC-7 Network terms (written, before build spend):** get written confirmation that (a) organic SEO is an allowed
  traffic source, (b) target ZIPs are covered, (c) no incentivized traffic, (d) the network's own brand/disclosure and
  recording practices, (e) prohibited claims list. Honestly declare the traffic source; never route calls from one
  niche's number into another offer. Offer pages are UNKNOWN (only snippets seen) until the operator reads them.
- **CC-8 Privacy:** privacy policy names call recording, analytics, form fields and sharing with the network/buyer.

## Rulings
| # | Item | Ruling | Rule / source (URL, retrieved date) | Required change / condition |
|---|---|---|---|---|
| C-1 | Tree service | CONDITIONAL | CC-1..CC-8; contractor/arborist licensing varies by state (some states license tree work or require registration) — UNKNOWN per target state | CC-1..CC-8. No "certified arborist" / ISA claims in lead_gen mode. No storm-chasing urgency claims that imply a dispatched crew. Before tenant mode: look up the target state's tree/contractor license and show the tenant's number if required. Lowest-risk niche. |
| C-2 | Water damage (incl. fire damage section) | CONDITIONAL (highest-risk of the set) | CC-1..CC-8; public-adjuster licensing laws in most states restrict anyone not licensed from acting/advertising as handling or negotiating an insured's claim (state-specific, UNKNOWN until checked); assignment-of-benefits rules vary (e.g., FL reformed AOB in 2022-2023 — PRIOR, verify); IICRC is a trademark/certification body | Copy must NOT say or imply: "we handle/work with your insurance", "we bill your insurance directly", "maximize your claim", "insurance-approved", "free if insured", "direct billing". Allowed: neutral educational text ("contact your insurer; ask the provider whether they work with your carrier"). No "IICRC certified" in lead_gen mode. No mold remediation/health claims (mold licensing exists in some states, e.g. TX, FL — verify). Fire damage section: same insurance limits, no adjuster-like language, no smoke/soot health claims. Confirm the network offer forbids/permits restoration-franchise brand use (CC-4: Servpro, ServiceMaster, Paul Davis etc. never). If target state is FL: counsel before launch. |
| C-3 | Pest control | CONDITIONAL | CC-1..CC-8; FIFRA (7 U.S.C. 136 et seq.) and state structural pest control licensing; some states regulate pest-control advertising and may treat soliciting as engaging in the business — UNKNOWN per state | No pesticide safety claims ("safe", "non-toxic", "harmless to pets/kids", "green/eco") — these are restricted label/advertising claims for pesticides under EPA/FIFRA practice [PRIOR, verify 40 CFR 156.10(a)(5)]. No "licensed applicators" claim. Termite: no WDI/real-estate inspection report claims. Before launch: check target state's structural pest control board rule on advertising by non-licensees (counsel if the rule reaches referral services). Network "experience required" term must be honestly met (CC-7). |
| C-4 | Septic | CONDITIONAL | CC-1..CC-8; septic installers/pumpers are licensed or permitted by state/county health departments in many states — UNKNOWN per target | No claims of "licensed septic installer", permit pulling, or system "inspections/certifications" for real-estate transfer. Tenant mode: display tenant's license/permit number where required. Tenant-led per 01-niche, so tenant license check moves to Gate 5. |
| C-5 | HVAC | CONDITIONAL | CC-1..CC-8; state mechanical/HVAC licensing; some states require license number in ads (e.g. TX TDLR ACR rules — PRIOR, verify); EPA Section 608 (refrigerant) | No "EPA certified", "NATE certified", "factory authorized" claims; no manufacturer names as brand (CC-4); no rebate/tax-credit promises (energy credits change; don't quote amounts). Tenant mode: license number in footer if state requires. |
| C-6 | Plumbing drain/sewer | CONDITIONAL | CC-1..CC-8; state plumbing licensing, many states require license number in advertising (PRIOR, verify per state) | No "licensed master plumber" claims; no Roto-Rooter/Mr. Rooter names; no price/"$X drain cleaning" claims not set by the buyer. Tenant mode: license number. Sewer-line work may need municipal permits — keep content educational. |
| C-7 | Water heater | CONDITIONAL | Same as C-6; gas work licensing; utility rebate programs | Same as C-6; no manufacturer names (Rheem, AO Smith, Bradford White) as brand or "authorized dealer"; no rebate amounts unless linked to the live utility source. |
| C-8 | Roofing (raised in 05-economics, not in scope) | NOT RULED | Some states restrict contractor solicitation of insurance claims (e.g. TX, CO, others — UNKNOWN/verify) | Needs its own ruling before any advance. |

Counts: CLEAR 0 · CONDITIONAL 7 · BLOCK 0 (none of the seven is a regulated vertical under CLAUDE.md rule 7).

## Must-fix before the next phase
1. CC-7: written network confirmation (SEO allowed, ZIP coverage, trademark and recording terms) for the chosen niche before any spend beyond a domain.
2. Water damage: insurance-claim language ban written into the content brief; state public-adjuster/AOB check once the city is picked (Gate 2).
3. Pest control: no pesticide-safety claims; state advertising-by-non-licensee check at Gate 2.
4. Per-state license-display rule for the chosen trade looked up at Gate 2 (stored for tenant mode).
5. Recording disclosure confirmed in the call-tracking/network IVR before launch (Gate 4).

## Requires counsel
- Water damage in FL or any state where the target city sits with strict public-adjuster/AOB solicitation rules.
- Pest control if the target state's board rule applies to advertising/referral by non-licensees.
- Any network contract with indemnity, clawback or "publisher warrants compliance with all laws" clauses (read before signing).
- Roofing, if it is ever advanced (insurance-claim solicitation statutes).

## Notes for the operator
All seven home-service niches can be done compliantly as an honest referral site feeding pay-per-call offers; none is
a regulated vertical. Risk order (low to high): tree service, septic, HVAC/plumbing/water heater, pest control, water
damage. Water damage is the one most likely to drift into illegal territory, because the natural marketing language
("we work with your insurance") is exactly what public-adjuster laws restrict. The biggest practical risk across all
niches is not law but the network contract: confirm in writing that SEO traffic is accepted and that you are not
promising anything the buyer doesn't deliver.
