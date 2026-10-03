---
name: site-factory
description: "How to architect, configure, build, preview, QA and deploy a fast static lead-gen website with scripts/build_site.py. It covers domain and brand choice, URL structure, site.json reference, content folder layout, shortcodes, lead_gen vs tenant mode, local vs national scope, schema, call tracking, forms, Cloudflare Pages or Netlify deploys, and switching a rented site to the tenant. Use it for \"build the website\", \"create the site\", \"site structure\", \"deploy\", or \"switch to tenant\"."
argument-hint: "<project slug> [build | preview | qa | deploy | tenant-switch]"
---

# Site Factory

Owner: `site-architect` (with `local-copywriter` and `content-qa-editor` for content). Request: $ARGUMENTS

## Commands
```
python3 scripts/new_project.py --niche <id> --city "City, ST" --model hybrid   # scaffolds projects/<slug>/ incl. site/site.json
python3 scripts/build_site.py projects/<slug>                   # -> projects/<slug>/dist/
python3 scripts/build_site.py projects/<slug> --drafts --base-url https://staging.example.net
python3 -m http.server -d projects/<slug>/dist 8000             # preview at http://localhost:8000
python3 scripts/qa_site.py projects/<slug>                      # dev QA (exit 1 on errors)
python3 scripts/qa_site.py projects/<slug> --launch             # launch gate
```
`examples/demo-tree-service/` is a complete reference project (fictional city).

## Domain and brand
- Brandable plus partial match: `<city><service>pros.com`, `<region><service>.com`, `<city>treecare.com`. Short,
  .com, no hyphen chains, no trademarks (franchise or manufacturer names).
- A fresh registration by default. Buying expired or aged domains to inherit authority is "expired domain abuse"
  under Google's spam policies.
- One site per niche-by-market. Don't stack unrelated niches on one domain.

## Architecture (local scope)
```
/                         home: core service + primary city (type: home)
/services/<service>/      one per sub-service cluster with demand (type: service)
/areas/<town>/            only towns with demand AND a verified fact sheet (type: area)
/areas/                   auto hub: area page cards + all towns served (areas_served)
/cost/<guide>/            cost / price intent (type: cost)
/blog/<post>/             question intent (type: blog)
/about/  /contact/        trust + conversion (type: about / contact)
/privacy-policy/ /terms/  auto-generated templates if absent (review before launch)
```
National scope (`"scope": "national"`): `/services/...` for national service hubs, `/locations/<state>/` (auto hub) and
`/locations/<state>/<city>/` (type: area) only where you have unique local data.

## Content files (`site/content/**.md`)
The path maps to the URL: `services/tree-removal.md` -> `/services/tree-removal/`, `index.md` -> `/`. Front matter keys:
`title, description, h1, type, keyword, service, area, nav, order, summary, subtitle, hero (true/false),
hero_points (a | b | c), image, image_alt, updated, date (blog), draft, noindex`.
Shortcodes, each on its own line: `[[cta]]`, `[[cta: custom text]]`, `[[services]]`, `[[areas]]`, `[[children]]`,
`[[form]]`, `[[toc]]`, `[[disclosure]]`, `[[phone]]`.
An `## Frequently Asked Questions` (or `## FAQ`) section with `###` questions becomes an accordion plus FAQPage schema.
Images go in `site/static/images/` (WebP, sized). Reference them as `/images/x.webp` with alt text.

## site.json reference
| Key | Meaning |
|---|---|
| `brand`, `base_url` | Site name; production URL (no trailing slash) |
| `staging` | `true` = noindex everywhere and robots Disallow. Keep true until launch |
| `mode` | `lead_gen` (referral service: disclosure, Organization schema, no address) or `tenant` (the renting business) |
| `scope` | `local` or `national` |
| `niche_id`, `niche_name`, `primary_city`, `state`, `state_name` | Used in defaults, CTAs and schema |
| `phone`, `phone_e164` | Display number and E.164 for `tel:` links. Use the call-tracking number |
| `hours`, `tagline`, `email` | Optional. Hours only if true for whoever answers |
| `areas_served` | Towns for the footer, areas hub and schema areaServed |
| `theme` | `primary`, `accent`, `logo_text` |
| `form` | `enabled`, `action` (Formspree, Web3Forms, Netlify Forms or your endpoint), `consent_text` ({brand} placeholder) |
| `tracking` | `ga4_id`, `gsc_verification`, `bing_verification`, `head_html` (e.g. a call-tracking DNI script) |
| `lead_gen.disclosure` | Override the default referral disclosure text |
| `tenant` | `legal_name`, `license`, `license_label`, `schema_type`, `address{}`, `show_address`, `same_as[]`, `gbp_url` |
| `nav` | Optional `[{label, href}]` override |
| `legal` | `contact_email`, `effective_date` |

## What the build gives you
Pretty URLs, inline theme variables plus one cached stylesheet, a mobile sticky call bar, header call button, hero
with CTA, breadcrumbs (plus BreadcrumbList), JSON-LD `@graph` (WebSite, Organization or a LocalBusiness subtype,
WebPage, Service, FAQPage, BlogPosting), canonical, OG and Twitter tags, sitemap.xml, robots.txt, 404, generated
favicon, `_headers` (security and caching for Netlify or Cloudflare Pages) and `build-report.json` for QA.

## Call tracking and forms
- Buy one local tracking number (CallRail, CallTrackingMetrics, Ringba or Retreaver). Set a recording-disclosure
  greeting, forward it to the buyer (network or tenant), and enable call recording and source tracking. Put the
  number in `phone`. If using dynamic number insertion, add the vendor script in `tracking.head_html`.
- Forms only when someone answers fast. Use a form backend that emails or texts the lead instantly. Keep consent
  text accurate about who will contact the person.

## Deploy (Cloudflare Pages or Netlify, both free)
1. Push the repo, or upload `projects/<slug>/dist/`. For Cloudflare Pages Git builds: build command
   `python3 scripts/build_site.py projects/<slug>`, output directory `projects/<slug>/dist`.
2. Add the custom domain. HTTPS is automatic. Pick www or the apex and redirect the other.
3. Launch switch: set `"staging": false`, rebuild, run `qa_site.py --launch` (0 errors), and deploy.
4. Search Console: verify the domain (DNS) and submit `/sitemap.xml`. Do the same in Bing Webmaster Tools.

## Tenant switch (after a signed deal)
1. `mode: "tenant"`, fill in `tenant` (license is mandatory where the state requires it in ads; show the address only
   if the tenant wants it and it's real), and `same_as: [GBP URL, social profiles]`.
2. Rewrite referral phrasing in content into tenant voice. Add only claims the tenant confirms in writing (years,
   licensing, insurance, guarantees) and real photos.
3. Point the tracking number to the tenant (whisper "Call from <brand> website"). Keep number ownership with the operator.
4. Rebuild, run `qa_site.py --launch`, deploy, and record it in STATUS.md and project.json (`tenant`, `monthly_revenue`).
