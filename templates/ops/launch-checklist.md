# Launch checklist — <project>

Owner: site-architect · Date: YYYY-MM-DD

## Pre-flight
- [ ] Gate 4 decision file exists (`decisions/gate-4-launch.md`), verdict GO
- [ ] `site.json`: `staging: false`, real `base_url`, real tracking `phone` + `phone_e164`, legal `contact_email`
- [ ] Form endpoint set and a test submission delivered (if form enabled)
- [ ] `python3 scripts/build_site.py projects/<slug>` then `python3 scripts/qa_site.py projects/<slug> --launch` -> **PASS, 0 errors**
- [ ] Privacy policy + terms reviewed by the operator (generated templates are a starting point)

## Deploy
- [ ] Hosting project created (Cloudflare Pages / Netlify); `dist/` deployed
- [ ] Custom domain connected; HTTPS active; www <-> apex redirect works
- [ ] `/robots.txt` allows crawling and lists the sitemap; `/sitemap.xml` loads; 404 page works
- [ ] Mobile check: call bar, call button and form all work on a real phone

## Calls and tracking
- [ ] Test call: recording disclosure plays, routes to the buyer, whisper plays, logged with source
- [ ] Missed-call / voicemail handling set
- [ ] GA4 receiving data. Key events: `tel:` clicks, form submits
- [ ] Call-tracking dashboard access shared with whoever needs it

## Search engines
- [ ] Google Search Console verified (DNS), sitemap submitted, home + top service pages inspected and indexing requested
- [ ] Bing Webmaster Tools verified (import from GSC), sitemap submitted

## Records
- [ ] `project.json` -> `live.launched` set; `status: "live"`
- [ ] STATUS.md Phase 8 ticked with notes
- [ ] Authority plan started (`ops/authority-plan.md`)
