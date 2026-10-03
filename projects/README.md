# Projects

One folder per site (or per discovery run), created by:

```
python3 scripts/new_project.py --niche <id> --city "City, ST" --model hybrid
python3 scripts/new_project.py --niche water-damage --scope national --model nationwide
python3 scripts/new_project.py --discovery --slug my-first-hunt
```

## Layout
```
projects/<slug>/
  project.json     machine-readable state (phase, status, verdicts, domain, tenant, monthly_revenue)
  STATUS.md        pipeline checklist + decision log + live numbers
  brief.md         operator brief (Phase 0)
  research/        agent memos: 01-niche, 02-market, 03-keywords, 04-serp, 05-economics, 06-red-team, 07-compliance,
                   08-architecture, 09-content-*, rebuttals-gate-N; local-facts/<town>.md
  decisions/       war-room verdicts: gate-1-niche ... gate-5-deal
  data/            keywords.csv, keyword_map.md, cities.md, serp/*.json, niche-ranking.csv
  site/            site.json, content/ (Markdown pages), briefs/, static/ (images, favicon)
  dist/            built site (git-ignored; rebuild any time)
  ops/             launch checklist, authority plan, tenant pipeline, monetization, outreach/, reports/
```

`python3 scripts/portfolio.py` summarizes every project.
