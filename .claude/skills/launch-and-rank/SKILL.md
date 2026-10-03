---
name: launch-and-rank
description: "Launch, indexing, tracking and authority-building runbook for a new lead-gen site, plus monthly operations. It covers the launch checklist, Search Console and Bing setup, call tracking and analytics verification, indexing troubleshooting, a 90-day legitimate authority plan (local links, digital PR, partnerships), the tenant GBP, citations and reviews once rented, monthly reporting, kill-criteria reviews and scaling. Use it for \"launch the site\", \"get indexed\", \"build links\", \"rankings stalled\", \"monthly review\", or \"scale the portfolio\"."
argument-hint: "<project slug> [launch | authority | monthly-review | scale]"
---

# Launch & Rank

Owners: `site-architect` (launch), `authority-builder` (authority), orchestrator (monthly ops). Request: $ARGUMENTS

## Launch (day 0)
Copy `templates/ops/launch-checklist.md` to `projects/<slug>/ops/launch-checklist.md` and complete every line:
1. Gate 4 decision exists and `python3 scripts/qa_site.py projects/<slug> --launch` exits 0.
2. `staging: false`, real `base_url`, real tracking number, form endpoint tested (submit a test lead and confirm delivery).
3. Deploy, then check HTTPS, the www/apex redirect, `/robots.txt` (Allow), `/sitemap.xml` and the 404 page.
4. Call tracking: place a test call. Check the recording disclosure plays, the call routes to the buyer, the call is
   logged with its source, and the whisper message plays.
5. Search Console: verify (DNS), submit the sitemap, and inspect and request indexing for the home page plus the top
   service pages. Then Bing Webmaster Tools (import from GSC).
6. Analytics: GA4 receives page views. Mark call clicks (`tel:` link clicks) and form submits as key events.
7. Record the launch date in `project.json` (`live.launched`) and STATUS.md.

## Indexing troubleshooting (weeks 1-6)
- "Discovered - currently not indexed": usually a crawl-priority issue. Improve internal links from the home page,
  add a few quality external links, and check page uniqueness.
- "Crawled - currently not indexed": usually a quality or duplication issue. Strengthen the page, merge
  near-duplicates, and check qa_site.py overlap warnings.
- Don't mass-request indexing or use indexing "hacks" (the Indexing API is for job postings and livestreams only).

## Authority: the 90-day plan (authority-builder; template `templates/ops/authority-plan.md`)
| Weeks | Focus | Examples |
|---|---|---|
| 1-2 | Foundations | GSC/Bing, brand social profiles (honest), consistent brand name |
| 2-6 | Local relevance | Real local sponsorships, community resource pages, chamber membership if eligible, local news story angles |
| 4-10 | Linkable asset | A permit guide from city code, a storm-prep checklist, a cost survey with method, a seasonal calendar. Pitch to local media, HOAs, realtors |
| 6-12 | Expert sourcing and partnerships | Journalist-request platforms (verify which are active), suppliers, complementary trades |
| Ongoing | Internal authority | Improve pages at position 8-20 in GSC first |

Never: PBNs, paid link schemes, link farms, expired-domain redirects, mass guest posting, comment spam, fake GBPs or fake citations.

## After a tenant signs
- The tenant's **real** Google Business Profile links to the site (UTM-tagged). Correct primary category, real
  service areas, real photos.
- Citations for the tenant's real NAP: Apple Business Connect, Bing Places, BBB, Yelp, Nextdoor, trade directories.
- A review program: ask every customer (no gating, no incentives), and respond to all reviews.

## Monthly review (orchestrator, around the 1st of each month)
1. Pull the numbers: GSC (clicks, impressions, avg position for the core cluster, top queries per page), call log
   (calls, duration ≥ 60s, unique callers, missed calls), form leads, revenue.
2. Write `projects/<slug>/ops/reports/YYYY-MM.md` from `templates/ops/monthly-report.md`. Update the STATUS.md live
   numbers and `project.json` (`monthly_revenue`, `status`).
3. **Check the kill criteria** from the Gate 3 decision. If one triggers, run a fast-mode war room (custom question:
   pivot, pay-per-call only, or sell).
4. Content refresh: per the content-engine refresh cycle.
5. Tenant report: send them the monthly report (calls, recordings sample, trends). Proof drives renewals.

## Scale
- **Clone the playbook, not the content**: same niche in another mid city (new project, through Gate 3), or adjacent
  niches for the same tenant (e.g. stump grinding or land clearing for a tree-service tenant).
- Portfolio view: `python3 scripts/portfolio.py`. Diversify across niches and states. Concentration in one niche
  means one core update can hit everything.
