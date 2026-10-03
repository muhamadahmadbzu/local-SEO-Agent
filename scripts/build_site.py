#!/usr/bin/env python3
"""Build a fast, SEO-ready static site from projects/<slug>/site/ (site.json + Markdown content).

  python3 scripts/build_site.py projects/tulsa-ok-tree-service
  python3 scripts/build_site.py projects/tulsa-ok-tree-service --drafts --out /tmp/preview
  python3 -m http.server -d projects/tulsa-ok-tree-service/dist 8000     # preview locally

Output (dist/): pretty-URL HTML pages, assets/site.css, sitemap.xml, robots.txt, 404.html, favicon.svg,
_headers (Netlify / Cloudflare Pages), build-report.json (consumed by scripts/qa_site.py).

Modes (site.json "mode"):
  lead_gen  the site is a referral/matching service. It shows a disclosure on every page, uses
            Organization + Service schema, and never shows a business address.
  tenant    the site represents the renting business. Its name, license, optional address and
            LocalBusiness-subtype schema come from site.json "tenant".
Scope (site.json "scope"): local (services/ + areas/) or national (locations/<state>/<city>/).
Deploy dist/ to Cloudflare Pages / Netlify / any static host.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json  # noqa: E402
from mdlite import parse_front_matter, render, slug_id, strip_tags  # noqa: E402

HUB_TITLES = {"services": "Services", "areas": "Service Areas", "locations": "Locations We Serve",
              "blog": "Guides & Resources", "guides": "Guides & Resources", "cost": "Cost Guides",
              "costs": "Cost Guides", "pricing": "Pricing Guides"}
HERO_TYPES = {"home", "service", "area"}
FAQ_HEADINGS = re.compile(r"^(frequently asked questions|faqs?)\b", re.I)

ICON_PHONE = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8'
              'a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 '
              '0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>')
ICON_CHECK = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="3"><path d="M5 13l4 4L19 7"/></svg>')

CSS = """
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.65;font-size:1.0625rem}
img{max-width:100%;height:auto}
a{color:var(--primary)}
a:hover{color:var(--primary-dark)}
.skip{position:absolute;left:-999px;top:0;background:#000;color:#fff;padding:.5rem 1rem;z-index:100}
.skip:focus{left:0}
.wrap{max-width:1120px;margin:0 auto;padding:0 1.1rem}
.topbar{background:var(--primary-dark);color:#fff;font-size:.9rem}
.topbar .wrap{display:flex;justify-content:space-between;gap:1rem;padding-top:.35rem;padding-bottom:.35rem}
.topbar a{color:#fff;font-weight:700;text-decoration:none}
header.site{border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:50}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:64px;flex-wrap:wrap}
.brand{font-weight:800;font-size:1.2rem;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.brand span{color:var(--primary)}
nav.main ul{list-style:none;margin:0;padding:0;display:flex;gap:1.1rem;flex-wrap:wrap}
nav.main a{text-decoration:none;color:var(--ink);font-weight:600;font-size:.97rem;white-space:nowrap}
nav.main a[aria-current]{color:var(--primary)}
.btn{display:inline-flex;align-items:center;gap:.5rem;padding:.8rem 1.2rem;border-radius:10px;font-weight:800;text-decoration:none;border:2px solid transparent;line-height:1.2}
.btn-call{background:var(--accent);color:#111}
.btn-call:hover{filter:brightness(.95);color:#111}
.btn-ghost{border-color:#fff;color:#fff}
.btn-ghost:hover{background:rgba(255,255,255,.12);color:#fff}
.hero{background:linear-gradient(135deg,var(--primary-dark),var(--primary));color:#fff;padding:3rem 0 2.6rem}
.hero h1{font-size:clamp(1.8rem,4.5vw,2.8rem);line-height:1.15;margin:0 0 .8rem;letter-spacing:-.02em;color:#fff}
.hero p.lead{font-size:1.15rem;max-width:46rem;margin:0 0 1.2rem;opacity:.95}
.hero ul.points{list-style:none;padding:0;margin:0 0 1.4rem;display:grid;gap:.4rem}
.hero ul.points li{display:flex;gap:.5rem;align-items:center}
.hero .actions{display:flex;gap:.8rem;flex-wrap:wrap}
main .content{max-width:780px;margin:0 auto;padding:2rem 1.1rem 3rem}
main .content.wide{max-width:1120px}
h1,h2,h3{line-height:1.25;color:var(--ink)}
.content h1{font-size:clamp(1.7rem,4vw,2.4rem);margin-top:.5rem}
.content h2{font-size:1.55rem;margin-top:2.2rem}
.content h3{font-size:1.2rem;margin-top:1.6rem}
.crumbs{font-size:.88rem;color:var(--muted);padding-top:.8rem}
.crumbs ol{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:.35rem}
.crumbs li+li::before{content:"/";margin-right:.35rem;color:var(--line-dark)}
.crumbs a{color:var(--muted)}
.cta{background:var(--soft);border:1px solid var(--line);border-left:6px solid var(--accent);border-radius:12px;padding:1.2rem 1.3rem;margin:2rem 0;display:flex;gap:1rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
.cta p{margin:0;font-weight:700;font-size:1.08rem;max-width:34rem}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:1rem;margin:1.5rem 0;padding:0;list-style:none}
.cards li{border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;background:#fff}
.cards a{font-weight:800;text-decoration:none;font-size:1.05rem}
.cards p{margin:.4rem 0 0;color:var(--muted);font-size:.95rem}
.area-list{columns:2 180px;padding-left:1.1rem}
.faq details{border:1px solid var(--line);border-radius:10px;padding:.8rem 1rem;margin:.7rem 0;background:#fff}
.faq summary{cursor:pointer;font-weight:700}
.faq details[open] summary{margin-bottom:.5rem}
.table-wrap{overflow-x:auto;margin:1.2rem 0}
table{border-collapse:collapse;width:100%;font-size:.97rem}
th,td{border:1px solid var(--line);padding:.55rem .7rem;text-align:left;vertical-align:top}
th{background:var(--soft)}
blockquote{margin:1.4rem 0;padding:.6rem 1.1rem;border-left:4px solid var(--primary);background:var(--soft);border-radius:0 8px 8px 0}
.note{font-size:.9rem;color:var(--muted)}
.disclosure{font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:1rem;margin-top:1.4rem}
form.lead{display:grid;gap:.8rem;background:var(--soft);padding:1.3rem;border-radius:12px;border:1px solid var(--line);margin:2rem 0}
form.lead label{font-weight:700;font-size:.95rem;display:grid;gap:.3rem}
form.lead input,form.lead select,form.lead textarea{font:inherit;padding:.65rem .7rem;border:1px solid var(--line-dark);border-radius:8px;width:100%}
form.lead .consent{font-size:.8rem;color:var(--muted);font-weight:400}
form.lead button{border:0;cursor:pointer;font-size:1rem}
footer.site{background:#0f172a;color:#cbd5e1;padding:2.5rem 0 5.5rem;margin-top:2rem;font-size:.95rem}
footer.site a{color:#e2e8f0}
footer.site .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem}
footer.site h2{color:#fff;font-size:1.05rem;margin:0 0 .6rem}
footer.site ul{list-style:none;padding:0;margin:0;display:grid;gap:.3rem}
footer.site .disclosure{color:#94a3b8;border-color:#1e293b}
.callbar{position:fixed;bottom:0;left:0;right:0;z-index:60;display:none;background:var(--accent);text-align:center;box-shadow:0 -4px 14px rgba(0,0,0,.15)}
.callbar a{display:flex;justify-content:center;align-items:center;gap:.5rem;padding:.95rem;color:#111;font-weight:900;font-size:1.1rem;text-decoration:none}
@media (max-width:760px){.callbar{display:block}.topbar .hide-sm{display:none}nav.main{width:100%;overflow-x:auto}nav.main ul{flex-wrap:nowrap;padding-bottom:.4rem}header.site .btn-call{display:none}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
"""


# --------------------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s or ""), quote=True)


def darken(hex_color, factor=0.72):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))


def e164(phone):
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return ("+" + digits) if digits else ""


def word_count(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", text))


class Page:
    def __init__(self, src, rel, meta, body):
        self.src, self.rel, self.meta, self.body = src, rel, meta, body
        parts = rel[:-3].split("/")  # strip .md
        if parts[-1] == "index":
            parts = parts[:-1]
        self.parts = parts
        self.url = "/" + "/".join(parts) + ("/" if parts else "")
        self.type = (meta.get("type") or ("home" if not parts else "page")).lower()
        self.h1 = meta.get("h1")
        self.title = meta.get("title")
        self.auto = False
        self.html = ""
        self.faq = []

    @property
    def label(self):
        return self.meta.get("nav") or self.h1 or self.title or self.parts[-1].replace("-", " ").title()

    @property
    def order(self):
        try:
            return float(self.meta.get("order", 999))
        except ValueError:
            return 999.0


# --------------------------------------------------------------------------- builder
class SiteBuilder:
    def __init__(self, project, out=None, drafts=False, base_url=None):
        self.project = project
        self.site_dir = os.path.join(project, "site")
        self.cfg = load_json(os.path.join(self.site_dir, "site.json"))
        if base_url:
            self.cfg["base_url"] = base_url
        self.base = (self.cfg.get("base_url") or "https://example.com").rstrip("/")
        self.out = out or os.path.join(project, "dist")
        self.drafts = drafts
        self.mode = self.cfg.get("mode", "lead_gen")
        self.phone = self.cfg.get("phone", "")
        self.phone_href = self.cfg.get("phone_e164") or e164(self.phone)
        self.today = dt.date.today().isoformat()
        self.pages = []
        self.css_version = hashlib.sha1(CSS.encode()).hexdigest()[:8]

    # ----------------------------------------------------------------- loading
    def load(self):
        root = os.path.join(self.site_dir, "content")
        for dirpath, _, files in os.walk(root):
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                src = os.path.join(dirpath, f)
                rel = os.path.relpath(src, root).replace(os.sep, "/")
                with open(src, encoding="utf-8") as fh:
                    meta, body = parse_front_matter(fh.read())
                if meta.get("draft") is True and not self.drafts:
                    continue
                page = Page(src, rel, meta, body)
                if not page.h1:
                    m = re.match(r"^\s*#\s+(.+)\n", body)
                    if m:
                        page.h1 = m.group(1).strip()
                        page.body = body[m.end():]
                page.h1 = page.h1 or (page.title.split(" | ")[0] if page.title else page.label)
                self.pages.append(page)
        self._add_hubs()
        self._add_legal()

    def _add_hubs(self):
        urls = {p.url for p in self.pages}
        dirs = set()
        for p in self.pages:
            for k in range(1, len(p.parts)):
                dirs.add(tuple(p.parts[:k]))
        for d in sorted(dirs):
            url = "/" + "/".join(d) + "/"
            if url in urls:
                continue
            name = d[-1]
            title = HUB_TITLES.get(name) if len(d) == 1 else None
            if not title:
                pretty = name.replace("-", " ").title()
                title = f"{self.cfg.get('niche_name', '')} in {pretty}".strip() if d[0] == "locations" else pretty
            meta = {"type": "hub", "h1": title, "title": f"{title} | {self.cfg.get('brand', '')}",
                    "description": f"{title} from {self.cfg.get('brand', '')}: browse every page in this section.",
                    "nav": title}
            body = "[[children]]\n\n[[cta]]\n"
            if d == ("areas",):
                body = "[[children]]\n\n## All communities we serve\n\n[[areas]]\n\n[[cta]]\n"
            hub = Page(None, "/".join(d) + "/index.md", meta, body)
            hub.auto = True
            self.pages.append(hub)
            urls.add(url)
        for hub in [p for p in self.pages if p.auto and p.type == "hub"]:
            labels = [c.meta.get("area") or (c.parts[-1].replace("-", " ").title() if c.auto else c.label)
                      for c in sorted(self.children_of(hub), key=lambda c: (c.order, c.label))]
            if labels:
                listed = ", ".join(labels[:6]) + (" and more" if len(labels) > 6 else "")
                desc = f"{hub.h1}: {listed}. {self.cfg.get('brand', '')}."
                hub.meta["description"] = desc if len(desc) <= 160 else desc[:157].rsplit(" ", 1)[0] + "..."

    def _add_legal(self):
        urls = {p.url for p in self.pages}
        brand = self.cfg.get("brand", "")
        if "/privacy-policy/" not in urls:
            self.pages.append(Page(None, "privacy-policy.md",
                                   {"type": "legal", "h1": "Privacy Policy", "title": f"Privacy Policy | {brand}",
                                    "description": f"How {brand} collects, uses and protects information.",
                                    "nav": "Privacy Policy", "noindex": False}, self._privacy_md()))
        if "/terms/" not in urls:
            self.pages.append(Page(None, "terms.md",
                                   {"type": "legal", "h1": "Terms of Use", "title": f"Terms of Use | {brand}",
                                    "description": f"Terms that apply when you use {brand}.", "nav": "Terms of Use"},
                                   self._terms_md()))
        for p in self.pages:
            if p.src is None:
                p.auto = True

    # ----------------------------------------------------------------- text blocks
    def disclosure_text(self):
        custom = (self.cfg.get("lead_gen") or {}).get("disclosure")
        if custom:
            return custom
        niche = (self.cfg.get("niche_name") or "home service").lower()
        where = self.cfg.get("primary_city") or "your area"
        return (f"{self.cfg.get('brand')} is a free referral service that connects people in {where} and nearby "
                f"communities with independent local {niche} providers. We are not a contractor and do not perform "
                "services ourselves. Providers are independent businesses responsible for their own work, licensing "
                "and insurance. Calls may be recorded for quality and are routed to a participating provider.")

    def _privacy_md(self):
        brand = self.cfg.get("brand")
        email = (self.cfg.get("legal") or {}).get("contact_email") or self.cfg.get("email") or ""
        eff = (self.cfg.get("legal") or {}).get("effective_date") or self.today
        share = ("the local service provider we match you with" if self.mode == "lead_gen" else "our team")
        return f"""_Effective {eff}. This template must be reviewed by the site owner before launch; it is not legal advice._

## Information we collect

- **Information you give us**: your name, phone number, ZIP code and the details of your request when you call or submit a form.
- **Call information**: calls to the numbers on this site go through a call-tracking provider. Call details (caller number, time, duration) and recordings may be stored for quality, billing and dispute purposes.
- **Usage data**: standard analytics such as pages viewed, device and approximate location, collected with cookies or similar technology.

## How we use information

We use it to respond to your request and connect you with {share}, to measure and improve the website, to prevent fraud and to meet legal obligations.

## How we share information

We share your request details with {share} so they can contact you about the service you asked for. We also use vendors (hosting, call tracking, analytics, form processing) that handle data on our behalf. We do not sell your personal information for money.

## Your choices

You can ask us to access, correct or delete your information{(' by emailing ' + email) if email else ' using the contact details on this site'}. To stop receiving calls or texts about a request, tell the caller or reply STOP to a text.

## Children

This site is not directed to children under 13 and we do not knowingly collect their information.

## Changes

We may update this policy. The effective date above shows when it last changed.
"""

    def _terms_md(self):
        brand = self.cfg.get("brand")
        if self.mode == "lead_gen":
            role = (f"{brand} is a referral service. We help you reach independent local service providers. We do not "
                    "perform services, are not a party to any agreement between you and a provider, and do not guarantee "
                    "a provider's work, pricing, availability, licensing or insurance. Verify any provider you hire, "
                    "including license status with your state or local licensing authority.")
        else:
            role = f"These terms apply to your use of the {brand} website. Services are provided under the terms you agree to with {brand}."
        return f"""_This template must be reviewed by the site owner before launch; it is not legal advice._

## About this site

{role}

## Information on this site

Content is general information, not professional advice. Prices and timelines are typical ranges, not quotes. A provider can only quote after assessing your situation.

## Calls and messages

Calls may be recorded. By submitting a form you agree to be contacted about your request as described next to the form. You can opt out at any time.

## Limitation of liability

To the fullest extent the law allows, {brand} is not liable for indirect or consequential damages arising from your use of this site or from services performed by independent providers.

## Changes

We may update these terms at any time by posting a new version on this page.
"""

    # ----------------------------------------------------------------- components
    def cta_html(self, text=None, page=None):
        area = (page.meta.get("area") if page else None) or self.cfg.get("primary_city") or ""
        service = (page.meta.get("service") if page else None) or self.cfg.get("niche_name", "")
        if not text:
            if self.mode == "lead_gen":
                text = f"Need {service.lower()} in {area}? Call now to get connected with a local pro." if area else \
                    f"Need {service.lower()}? Call now to get connected with a local pro."
            else:
                text = f"Call {self.cfg.get('brand')} for {service.lower()}{' in ' + area if area else ''}."
        return (f'<aside class="cta" aria-label="Call to action"><p>{esc(text)}</p>'
                f'<a class="btn btn-call" href="tel:{esc(self.phone_href)}">{ICON_PHONE} {esc(self.phone)}</a></aside>')

    def form_html(self):
        f = self.cfg.get("form") or {}
        if not f.get("enabled") or not f.get("action"):
            return ""
        consent = (f.get("consent_text") or "").replace("{brand}", self.cfg.get("brand", ""))
        services = [p for p in self.pages if p.type == "service"]
        opts = "".join(f"<option>{esc(p.label)}</option>" for p in sorted(services, key=lambda p: (p.order, p.label)))
        return f"""<form class="lead" id="quote" action="{esc(f['action'])}" method="{esc(f.get('method', 'POST'))}">
<h2>Request service</h2>
<label>Name<input name="name" autocomplete="name" required></label>
<label>Phone<input name="phone" type="tel" autocomplete="tel" required></label>
<label>ZIP code<input name="zip" inputmode="numeric" autocomplete="postal-code" required></label>
{('<label>Service needed<select name="service"><option value="">Choose one</option>' + opts + '</select></label>') if opts else ''}
<label>Details<textarea name="message" rows="3"></textarea></label>
<label class="consent"><input type="checkbox" name="consent" value="yes" required> {esc(consent)}</label>
<button class="btn btn-call" type="submit">Send request</button>
</form>"""

    def cards_html(self, pages):
        items = []
        for p in sorted(pages, key=lambda p: (p.order, p.label)):
            summary = p.meta.get("summary") or p.meta.get("description") or ""
            items.append(f'<li><a href="{esc(p.url)}">{esc(p.label)}</a>{"<p>" + esc(summary) + "</p>" if summary else ""}</li>')
        return f'<ul class="cards">{"".join(items)}</ul>' if items else ""

    def areas_html(self):
        area_pages = {p.meta.get("area", p.label).lower(): p for p in self.pages if p.type == "area"}
        names = list(self.cfg.get("areas_served") or [])
        for key, p in area_pages.items():
            if key not in [n.lower() for n in names]:
                names.append(p.meta.get("area") or p.label)
        lis = []
        for nme in names:
            p = area_pages.get(nme.lower())
            lis.append(f'<li><a href="{esc(p.url)}">{esc(nme)}</a></li>' if p else f"<li>{esc(nme)}</li>")
        return f'<ul class="area-list">{"".join(lis)}</ul>' if lis else ""

    def children_of(self, page):
        depth = len(page.parts) + 1
        return [p for p in self.pages if len(p.parts) == depth and p.parts[:-1] == page.parts and p.type != "legal"]

    def shortcode(self, page):
        def handler(name, arg):
            if name == "cta":
                return self.cta_html(arg, page)
            if name == "services":
                return self.cards_html([p for p in self.pages if p.type == "service"])
            if name == "areas":
                return self.areas_html()
            if name == "children":
                return self.cards_html(self.children_of(page))
            if name == "form":
                return self.form_html()
            if name == "disclosure":
                return f'<p class="disclosure">{esc(self.disclosure_text())}</p>' if self.mode == "lead_gen" else ""
            if name == "toc":
                return "<!--TOC-->"
            if name == "phone":
                return f'<p><a class="btn btn-call" href="tel:{esc(self.phone_href)}">{ICON_PHONE} {esc(self.phone)}</a></p>'
            return f"<!-- unknown shortcode {esc(name)} -->"
        return handler

    # ----------------------------------------------------------------- rendering
    def extract_faq(self, body_html):
        """Turn an 'FAQ' H2 section with H3 questions into <details> + collect Q/A for schema."""
        faq, m = [], None
        for h2 in re.finditer(r'<h2 id="[^"]*">(.*?)</h2>', body_html):
            if FAQ_HEADINGS.match(strip_tags(h2.group(1))):
                m = h2
                break
        else:
            return body_html, faq
        start = m.end()
        nxt = re.search(r"<h2 ", body_html[start:])
        end = start + nxt.start() if nxt else len(body_html)
        section = body_html[start:end]
        parts = re.split(r'<h3 id="[^"]*">(.*?)</h3>', section)
        intro, qa_html = parts[0], []
        for i in range(1, len(parts) - 1, 2):
            q, a = parts[i].strip(), parts[i + 1].strip()
            faq.append((strip_tags(q), strip_tags(a)))
            qa_html.append(f"<details><summary>{q}</summary>{a}</details>")
        if not faq:
            return body_html, faq
        new = f'{body_html[:m.start()]}<section class="faq">{m.group(0)}{intro}{"".join(qa_html)}</section>{body_html[end:]}'
        return new, faq

    def toc(self, body_html):
        items = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)
        if len(items) < 3:
            return body_html.replace("<!--TOC-->", "")
        lis = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items)
        return body_html.replace("<!--TOC-->", f'<nav class="toc" aria-label="On this page"><p class="note">On this page</p><ol>{lis}</ol></nav>')

    def render_page_body(self, page):
        body = render(page.body, self.shortcode(page), used_ids={slug_id(page.h1 or "", set())})
        body, page.faq = self.extract_faq(body)
        body = self.toc(body)
        if page.type in ("home", "service", "area", "cost") and "class=\"cta\"" not in body:
            body += self.cta_html(page=page)
        if page.type in ("home", "service", "area", "contact") and (self.cfg.get("form") or {}).get("enabled") \
                and 'id="quote"' not in body:
            body += self.form_html()
        return body

    def breadcrumbs(self, page):
        crumbs = [("Home", "/")]
        by_url = {p.url: p for p in self.pages}
        for k in range(1, len(page.parts) + 1):
            url = "/" + "/".join(page.parts[:k]) + "/"
            p = by_url.get(url)
            crumbs.append((p.label if p else page.parts[k - 1].replace("-", " ").title(), url))
        return crumbs

    def nav_items(self):
        if self.cfg.get("nav"):
            return [(n["label"], n["href"]) for n in self.cfg["nav"]]
        urls = {p.url: p for p in self.pages}
        items = []
        for url, label in (("/services/", "Services"), ("/areas/", "Service Areas"), ("/locations/", "Locations"),
                           ("/cost/", "Cost Guides"), ("/costs/", "Cost Guides"), ("/blog/", "Guides"),
                           ("/about/", "About"), ("/contact/", "Contact")):
            if url in urls:
                items.append((label, url))
        return items

    def schema(self, page, crumbs):
        base = self.base
        url = base + page.url
        cfg = self.cfg
        areas = [{"@type": "City", "name": f"{a}, {cfg.get('state', '')}".strip(", ")} for a in (cfg.get("areas_served") or [])]
        graph = [{"@type": "WebSite", "@id": base + "/#website", "url": base + "/", "name": cfg.get("brand"),
                  "inLanguage": "en-US"}]
        tenant = cfg.get("tenant") or {}
        if self.mode == "tenant":
            org = {"@type": tenant.get("schema_type") or "LocalBusiness", "@id": base + "/#business",
                   "name": tenant.get("legal_name") or cfg.get("brand"), "url": base + "/",
                   "telephone": self.phone_href or None}
            addr = tenant.get("address") or {}
            if tenant.get("show_address") and addr.get("street") and addr.get("city"):
                org["address"] = {"@type": "PostalAddress", "streetAddress": addr.get("street"),
                                  "addressLocality": addr.get("city"), "addressRegion": addr.get("region"),
                                  "postalCode": addr.get("postal"), "addressCountry": "US"}
            if tenant.get("same_as"):
                org["sameAs"] = tenant["same_as"]
            if areas:
                org["areaServed"] = areas
            provider_id = base + "/#business"
        else:
            org = {"@type": "Organization", "@id": base + "/#org", "name": cfg.get("brand"), "url": base + "/",
                   "telephone": self.phone_href or None, "description": self.disclosure_text()}
            if cfg.get("email"):
                org["email"] = cfg["email"]
            provider_id = base + "/#org"
        graph.append({k: v for k, v in org.items() if v})
        webpage = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": page.title or page.h1,
                   "isPartOf": {"@id": base + "/#website"}, "breadcrumb": {"@id": url + "#breadcrumb"},
                   "inLanguage": "en-US", "dateModified": page.meta.get("updated") or self.today}
        if page.meta.get("description"):
            webpage["description"] = page.meta["description"]
        graph.append(webpage)
        graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb",
                      "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": base + u}
                                          for i, (n, u) in enumerate(crumbs)]})
        if page.type in ("service", "home", "area"):
            served = areas
            if page.type == "area" and page.meta.get("area"):
                served = [{"@type": "City", "name": f"{page.meta['area']}, {cfg.get('state', '')}".strip(", ")}]
            svc = {"@type": "Service", "@id": url + "#service",
                   "name": page.meta.get("service") or page.h1, "serviceType": page.meta.get("service") or cfg.get("niche_name"),
                   "provider": {"@id": provider_id}, "url": url}
            if served:
                svc["areaServed"] = served
            graph.append(svc)
        if page.type == "blog":
            graph.append({"@type": "BlogPosting", "@id": url + "#article", "headline": page.h1,
                          "datePublished": page.meta.get("date") or page.meta.get("updated") or self.today,
                          "dateModified": page.meta.get("updated") or self.today,
                          "author": {"@id": provider_id}, "publisher": {"@id": provider_id},
                          "mainEntityOfPage": {"@id": url + "#webpage"}})
        if page.faq:
            graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in page.faq]})
        return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)

    def layout(self, page, body):
        cfg = self.cfg
        theme = cfg.get("theme") or {}
        primary = theme.get("primary", "#14532d")
        accent = theme.get("accent", "#d97706")
        brand = cfg.get("brand", "")
        title = page.title or f"{page.h1} | {brand}"
        desc = page.meta.get("description", "")
        canonical = self.base + page.url
        crumbs = self.breadcrumbs(page)
        noindex = page.meta.get("noindex") is True or cfg.get("staging") is True
        tr = cfg.get("tracking") or {}
        head_extra = []
        if tr.get("gsc_verification"):
            head_extra.append(f'<meta name="google-site-verification" content="{esc(tr["gsc_verification"])}">')
        if tr.get("bing_verification"):
            head_extra.append(f'<meta name="msvalidate.01" content="{esc(tr["bing_verification"])}">')
        if tr.get("ga4_id"):
            gid = esc(tr["ga4_id"])
            head_extra.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
                              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
                              f"gtag('js',new Date());gtag('config','{gid}');</script>")
        if tr.get("head_html"):
            head_extra.append(tr["head_html"])
        image = page.meta.get("image")
        og_image = f'<meta property="og:image" content="{esc(self.base + image if image.startswith("/") else image)}">' if image else ""
        current = ' aria-current="page"'
        nav = "".join(f'<li><a href="{esc(u)}"{current if page.url.startswith(u) else ""}>{esc(lbl)}</a></li>'
                      for lbl, u in self.nav_items())
        crumbs_html = ""
        if page.url != "/":
            lis = "".join(f'<li><a href="{esc(u)}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>'
                          for i, (n, u) in enumerate(crumbs))
            crumbs_html = f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'
        hero_setting = page.meta.get("hero")
        hero_on = hero_setting is True or (hero_setting is None and page.type in HERO_TYPES)
        h1_html = f"<h1>{esc(page.h1)}</h1>"
        hero = ""
        if hero_on:
            points = [p.strip() for p in str(page.meta.get("hero_points", "")).split("|") if p.strip()]
            pts = "".join(f"<li>{ICON_CHECK}<span>{esc(p)}</span></li>" for p in points)
            lead = page.meta.get("subtitle") or desc
            lead_html = f'<p class="lead">{esc(lead)}</p>' if lead else ""
            pts_html = f'<ul class="points">{pts}</ul>' if pts else ""
            second = ('<a class="btn btn-ghost" href="#quote">Request service</a>'
                      if (cfg.get("form") or {}).get("enabled") and (cfg.get("form") or {}).get("action") else "")
            hero = (f'<section class="hero"><div class="wrap">{h1_html}{lead_html}{pts_html}'
                    f'<div class="actions"><a class="btn btn-call" href="tel:{esc(self.phone_href)}">{ICON_PHONE} '
                    f'Call {esc(self.phone)}</a>{second}</div></div></section>')
        content_h1 = "" if hero else h1_html
        wide = " wide" if page.type == "hub" else ""
        services = sorted([p for p in self.pages if p.type == "service"], key=lambda p: (p.order, p.label))[:8]
        area_pages = sorted([p for p in self.pages if p.type == "area"], key=lambda p: (p.order, p.label))[:10]
        tenant = cfg.get("tenant") or {}
        license_line = ""
        if self.mode == "tenant" and tenant.get("license"):
            license_line = f'<p>{esc(tenant.get("license_label") or "License #")} {esc(tenant["license"])}</p>'
        address_line = ""
        addr = tenant.get("address") or {}
        if self.mode == "tenant" and tenant.get("show_address") and addr.get("street"):
            address_line = f'<p>{esc(addr.get("street"))}, {esc(addr.get("city"))}, {esc(addr.get("region"))} {esc(addr.get("postal"))}</p>'
        disclosure = f'<p class="disclosure">{esc(self.disclosure_text())}</p>' if self.mode == "lead_gen" else ""
        hours = f"<p>{esc(cfg['hours'])}</p>" if cfg.get("hours") else ""
        footer = f"""<footer class="site"><div class="wrap"><div class="cols">
<div><h2>{esc(brand)}</h2><p><a href="tel:{esc(self.phone_href)}">{esc(self.phone)}</a></p>{hours}{license_line}{address_line}</div>
{('<div><h2>Services</h2><ul>' + ''.join(f'<li><a href="{esc(p.url)}">{esc(p.label)}</a></li>' for p in services) + '</ul></div>') if services else ''}
{('<div><h2>Areas</h2><ul>' + ''.join(f'<li><a href="{esc(p.url)}">{esc(p.label)}</a></li>' for p in area_pages) + '</ul></div>') if area_pages else ''}
<div><h2>Company</h2><ul>{''.join(f'<li><a href="{u}">{l}</a></li>' for l, u in (('About', '/about/'), ('Contact', '/contact/')) if any(p.url == u for p in self.pages))}<li><a href="/privacy-policy/">Privacy Policy</a></li><li><a href="/terms/">Terms of Use</a></li></ul></div>
</div>{disclosure}<p class="note">&copy; {dt.date.today().year} {esc(brand)}</p></div></footer>"""
        return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
{'<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta property="og:type" content="{'article' if page.type == 'blog' else 'website'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="{esc(brand)}">
{og_image}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{esc(primary)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>:root{{--primary:{esc(primary)};--primary-dark:{esc(darken(primary))};--accent:{esc(accent)};--ink:#111827;--muted:#4b5563;--line:#e5e7eb;--line-dark:#9ca3af;--soft:#f8fafc}}</style>
<link rel="stylesheet" href="/assets/site.css?v={self.css_version}">
{chr(10).join(head_extra)}
<script type="application/ld+json">{self.schema(page, crumbs)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><span class="hide-sm">{esc(cfg.get('tagline') or ('Serving ' + cfg['primary_city'] + ' and nearby areas' if cfg.get('primary_city') else ''))}</span><a href="tel:{esc(self.phone_href)}">Call {esc(self.phone)}</a></div></div>
<header class="site"><div class="wrap"><a class="brand" href="/">{esc(theme.get('logo_text') or brand)}</a>
<nav class="main" aria-label="Main"><ul>{nav}</ul></nav>
<a class="btn btn-call" href="tel:{esc(self.phone_href)}">{ICON_PHONE} {esc(self.phone)}</a></div></header>
{crumbs_html}
<main id="main">{hero}<div class="content{wide}">{content_h1}{body}</div></main>
{footer}
<div class="callbar"><a href="tel:{esc(self.phone_href)}">{ICON_PHONE} Call {esc(self.phone)}</a></div>
</body>
</html>
"""

    # ----------------------------------------------------------------- output
    def write(self, rel_path, text):
        path = os.path.join(self.out, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def build(self):
        self.load()
        if os.path.exists(self.out):
            shutil.rmtree(self.out)
        os.makedirs(self.out)
        static = os.path.join(self.site_dir, "static")
        if os.path.isdir(static):
            shutil.copytree(static, self.out, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".gitkeep"))
        self.write("assets/site.css", CSS.strip() + "\n")
        report = []
        for page in sorted(self.pages, key=lambda p: p.url):
            body = self.render_page_body(page)
            page.html = self.layout(page, body)
            out_rel = "index.html" if page.url == "/" else page.url.strip("/") + "/index.html"
            self.write(out_rel, page.html)
            report.append({"url": page.url, "file": out_rel, "source": os.path.relpath(page.src, self.project) if page.src else None,
                           "type": page.type, "title": page.title or f"{page.h1} | {self.cfg.get('brand')}",
                           "h1": page.h1, "description": page.meta.get("description", ""),
                           "keyword": page.meta.get("keyword", ""), "area": page.meta.get("area", ""),
                           "service": page.meta.get("service", ""), "auto": page.auto,
                           "noindex": page.meta.get("noindex") is True, "faq_count": len(page.faq),
                           "words": word_count(strip_tags(render(page.body, lambda n, a: ""))),
                           "updated": page.meta.get("updated") or ""})
        self.write("404.html", self.layout(Page(None, "404.md", {"type": "page", "h1": "Page not found",
                                                                 "title": f"Page not found | {self.cfg.get('brand')}",
                                                                 "noindex": True}, ""),
                                           '<p>Sorry, that page does not exist. Try the <a href="/">home page</a>.</p>' + self.cta_html()))
        self.write("sitemap.xml", self.sitemap(report))
        robots = ("User-agent: *\nDisallow: /\n" if self.cfg.get("staging") else
                  f"User-agent: *\nAllow: /\n\nSitemap: {self.base}/sitemap.xml\n")
        self.write("robots.txt", robots)
        if not os.path.exists(os.path.join(self.out, "favicon.svg")):
            self.write("favicon.svg", self.favicon())
        self.write("_headers", "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
                               "  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: geolocation=(), camera=(), microphone=()\n"
                               "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n")
        meta = {"built": dt.datetime.now().isoformat(timespec="seconds"), "base_url": self.base, "mode": self.mode,
                "scope": self.cfg.get("scope", "local"), "phone_e164": self.phone_href, "pages": report}
        self.write("build-report.json", json.dumps(meta, indent=2))
        return report

    def sitemap(self, report):
        urls = []
        for r in report:
            if r["noindex"]:
                continue
            lastmod = r["updated"] or self.today
            urls.append(f"  <url><loc>{esc(self.base + r['url'])}</loc><lastmod>{esc(lastmod)}</lastmod></url>")
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(urls) + "\n</urlset>\n")

    def favicon(self):
        brand = self.cfg.get("brand") or "S"
        letters = "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", brand)[:2]).upper() or "S"
        color = (self.cfg.get("theme") or {}).get("primary", "#14532d")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{esc(color)}"/>'
                f'<text x="32" y="42" font-family="Arial,Helvetica,sans-serif" font-size="28" font-weight="700" '
                f'text-anchor="middle" fill="#fff">{esc(letters)}</text></svg>\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="project folder, e.g. projects/tulsa-ok-tree-service")
    ap.add_argument("--out", help="output folder (default <project>/dist)")
    ap.add_argument("--drafts", action="store_true", help="include pages with draft: true")
    ap.add_argument("--base-url", help="override site.json base_url (e.g. a staging URL)")
    a = ap.parse_args(argv)
    if not os.path.exists(os.path.join(a.project, "site", "site.json")):
        sys.exit(f"{a.project}/site/site.json not found")
    builder = SiteBuilder(a.project, a.out, a.drafts, a.base_url)
    report = builder.build()
    print(f"built {len(report)} pages -> {builder.out}")
    print(f"next: python3 scripts/qa_site.py {a.project}")


if __name__ == "__main__":
    main()
