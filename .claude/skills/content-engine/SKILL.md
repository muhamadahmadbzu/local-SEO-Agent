---
name: content-engine
description: "Production system for website content that ranks and converts without tripping Google's doorway or scaled-content policies. It covers the brief, write, fact-check and QA loop, page-type specifications (home, service, area, cost guide, blog, about, contact), local-substance rules, honesty rules for lead_gen vs tenant mode, the Markdown/front-matter format, parallel writing, and the uniqueness gate. Use it for \"write the content\", \"create pages\", \"content plan\", \"city pages\", \"service pages\", or \"fix thin content\"."
argument-hint: "<project slug> [brief | write <pages> | qa | refresh]"
---

# Content Engine

Owners: `content-strategist` (briefs), `local-copywriter` (writing), `content-qa-editor` (fact-check and gate).
Request: $ARGUMENTS

## The quality bar (what Google rewards and what makes people call)
1. **Helpful and specific**: process, price drivers, timelines, what to check, what can go wrong, local rules. The
   reader leaves knowing more than they would from the top 3 results.
2. **Locally true**: facts that only apply to this place, verified, with the authority named.
3. **Honest about who we are**: referral service (lead_gen) or the tenant's real claims (tenant).
4. **Unique per page**: every page has its own purpose and substance. No city-swapped templates. Google's
   scaled-content and doorway policies, and the 2026 spam updates, target exactly that.
5. **Clear next step**: call (primary) and form (secondary), repeated where decisions happen.

## The loop
```
keyword_map + SERP gaps + local fact sheets
      -> content-strategist: site/briefs/<page>.md (one per page; template templates/briefs/page-brief.md)
      -> local-copywriter (parallel batches of 3-5 pages per agent): site/content/<path>.md
      -> build_site.py + qa_site.py   (fix all ERRORs)
      -> content-qa-editor: fact-check, honesty, uniqueness, research/09-content-qa.md
      -> Gate 4 war room (qa_site.py --launch must pass)
```
Parallel writing: split pages by type so no two writers share a page. Give every writer the brief path, fact sheet
paths, site.json and this skill. The home page and the cost guide go to the strongest pass (writer, then editor).

## Page specifications
| Type | Words | Must include | Never |
|---|---|---|---|
| home | 900-1,400 | Service + city in H1; what we connect people with (lead_gen); services grid `[[services]]`; how it works; price drivers; what to ask a pro; local rules/hazards (sourced); areas `[[areas]]`; FAQ (3-6) | Fake claims, stock "welcome" fluff |
| service | 800-1,300 | When you need it (signs); how it's done (steps); options and materials; price drivers + link to cost guide; safety/permit notes; FAQ | Generic text that fits any city |
| area | 600-1,000 | Only with ≥ 3 verified local facts: local conditions (housing, terrain, climate, species, soils), local rules (permits, HOA, utilities), which services matter most there and why; FAQ specific to the town | Same paragraphs as other area pages; landmark lists as filler |
| cost | 1,000-1,600 | Sourced ranges (with dates) or the tenant's price sheet; table; each price driver explained; how to compare quotes; red flags | Invented local prices |
| blog | 900-1,500 | Answers one real question fully; links to the relevant service | Topics with no demand and no link value |
| about | 250-600 | Who runs the site, what it is (referral service vs business), how providers are matched (only true statements), contact | Invented team or history |
| contact | 100-300 | Phone, form, hours only if true, disclosure | — |

## Format
Markdown with front matter. See `.claude/skills/site-factory/SKILL.md` for the full key list and shortcodes, and
`examples/demo-tree-service/site/content/` for complete examples. The H1 comes from front matter (`h1`). Use H2 and H3
in the body. Put `[[cta]]` after the intro and mid-page. End with `## Frequently Asked Questions` and `###` questions.

## Honesty rules (enforced by qa_site.py and the editor)
**lead_gen mode**, never: "our team, crew, technicians", "licensed & insured", "bonded", "X years of experience",
"since 19xx", "family-, veteran- or locally owned", "certified <role>", "award-winning", "A+ rated", "N five-star
reviews", testimonials, guarantees we can't honor, "free estimates" unless every routed provider honors them, or
"24/7" or "same-day" unless the buyer's hours support it.
Write instead: "a local pro", "providers in your area", "get connected", "ask the provider for proof of insurance".
**tenant mode**: only claims the tenant confirms in writing. Keep the confirmations in `ops/tenant-facts.md`.

## Local facts
Facts come from `research/local-facts/<town>.md` (built by geo-market-analyst with source URLs). The writer may verify
and add facts (primary sources only: city, county or state sites, utilities, NOAA, USDA, EPA, Census) and must add the
source to the fact sheet. No source, no fact.

## AI-assisted writing policy
AI drafting is fine. Unedited, unsourced, mass-produced pages are not. Every page goes through a brief with real
substance, fact-checking, uniqueness checks and an honest QA pass. If you can't make a page genuinely useful,
don't publish it.

## Refresh cycle (post-launch)
Monthly: pull GSC queries per page. Expand pages ranking 5-20 with sections answering the actual queries, update
costs and dates, add new FAQs, and prune or merge pages with no impressions after 6 months.
