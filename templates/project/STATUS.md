# {{project_name}} — Status

| Field | Value |
|---|---|
| Project slug | `{{slug}}` |
| Niche | {{niche_name}} (`{{niche_id}}`) |
| Market | {{market}} |
| Monetization model | {{model}} |
| Created | {{date}} |
| Current phase | 0 — Intake |
| Current verdict | — |

## Pipeline

The orchestrator (`rank-and-rent` skill) ticks these off and links each artifact. A gate cannot be passed
until its decision file exists in `decisions/`.

- [ ] **Phase 0 — Intake**: operator brief (`brief.md`)
- [ ] **Phase 1 — Niche research** (`research/01-niche.md`)
- [ ] **Gate 1 — Niche shortlist** (`decisions/gate-1-niche.md`)
- [ ] **Phase 2 — Market selection** (`research/02-market.md`, `data/cities.md`)
- [ ] **Gate 2 — Market pick** (`decisions/gate-2-market.md`)
- [ ] **Phase 3 — Keyword demand** (`research/03-keywords.md`, `data/keywords.csv`)
- [ ] **Phase 4 — SERP competition** (`research/04-serp.md`, `data/serp/`)
- [ ] **Phase 5 — Lead economics** (`research/05-economics.md`)
- [ ] **Red team + compliance review** (`research/06-red-team-gate-3.md`, `research/07-compliance-gate-3.md`, `research/rebuttals-gate-3.md`)
- [ ] **Gate 3 — GO / NO-GO** (`decisions/gate-3-go-no-go.md`)
- [ ] **Phase 6 — Architecture & domain** (`research/08-architecture.md`, `site/site.json`)
- [ ] **Phase 7 — Content production** (`site/briefs/`, `site/content/`, `research/09-content-qa.md`)
- [ ] **Gate 4 — Launch readiness** (`decisions/gate-4-launch.md`; `qa_site.py` passes with 0 errors)
- [ ] **Phase 8 — Launch & indexing** (`ops/launch-checklist.md`)
- [ ] **Phase 9 — Authority plan** (`ops/authority-plan.md`)
- [ ] **Phase 10 — Monetization** (`ops/monetization.md`, `ops/tenant-pipeline.md`)
- [ ] **Gate 5 — Pricing & deal terms** (`decisions/gate-5-deal.md`)
- [ ] **Phase 11 — Operate & scale** (`ops/reports/YYYY-MM.md`)

## Decision log

| Date | Gate | Verdict | Key reasons | Kill criteria / conditions |
|---|---|---|---|---|

## Live numbers (update monthly)

| Month | Indexed pages | Avg position (core) | Organic clicks | Calls | Forms | Revenue | Notes |
|---|---|---|---|---|---|---|---|

## Open questions / blockers

-
