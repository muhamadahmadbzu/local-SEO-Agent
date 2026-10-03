#!/usr/bin/env python3
"""QA linter and publish gate for a built site (run after build_site.py).

  python3 scripts/qa_site.py projects/tulsa-ok-tree-service              # development check
  python3 scripts/qa_site.py projects/tulsa-ok-tree-service --launch     # launch gate (stricter)
  python3 scripts/qa_site.py projects/x --out projects/x/research/qa-report.md

Exit code 1 when any ERROR is found, so a launch is blocked until it is clean.

Checks:
  SEO basics      title and meta lengths, exactly one H1, canonical, keyword placement, duplicate titles and descriptions
  Content depth   word counts by page type, near-duplicate pages (doorway/templated geo-page risk with names normalized)
  Honesty         placeholders, and (lead_gen mode) claims a referral site cannot make: licensed, insured, years,
                  "our team", awards, review counts, testimonials. In tenant mode these become verify-with-tenant warnings
  Technical       broken internal links, images without alt, invalid JSON-LD, address/LocalBusiness schema in
                  lead_gen mode, tel: links that don't match the tracking number, sitemap coverage, robots.txt
  Compliance      referral disclosure on every lead_gen page, privacy and terms pages present
  Launch only     real domain, not staging, real phone number (not 555-01xx), analytics/GSC set
"""
import argparse
import itertools
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, md_table, write_text  # noqa: E402
from mdlite import parse_front_matter, render, strip_tags  # noqa: E402

MIN_WORDS = {"home": 600, "service": 600, "area": 400, "cost": 600, "blog": 600, "about": 150}
TITLE_LEN = (25, 65)
DESC_LEN = (70, 165)
DUP_WARN, DUP_ERR = 0.30, 0.50
STOP = {"in", "the", "a", "an", "of", "for", "and", "near", "me", "to", "my", "best"}

PLACEHOLDERS = [
    (r"\{\{|\}\}", "template braces left in output"),
    (r"\b(TODO|TBD|FIXME|XXX)\b", "TODO/TBD marker"),
    (r"lorem ipsum", "lorem ipsum filler"),
    (r"\[(insert|add|your|company|city|phone)[^\]]*\]", "bracketed placeholder"),
    (r"INSERT_|PLACEHOLDER", "placeholder token"),
]

# Claims a lead-gen (referral) site cannot truthfully make about itself. In tenant mode -> verify with tenant.
CLAIMS = [
    (r"\blicensed\s*(and|&)\s*insured\b|\bfully\s+(licensed|insured)\b|\bbonded\b", "licensing/insurance claim"),
    (r"\b(family|veteran|woman|women|locally)[- ]owned\b", "ownership claim"),
    (r"\b\d+\+?\s*(years?|yrs)\s+(of\s+)?(experience|in business|serving)\b|\bsince\s+(19|20)\d{2}\b", "years-in-business claim"),
    (r"\bour\s+(team|crews?|technicians?|techs|arborists?|plumbers?|roofers?|electricians?|staff|experts?|trucks?|employees)\b",
     "'our team' implies you perform the work"),
    (r"\baward[- ]winning\b|\ba\+\s+rat(ed|ing)\b|\bbbb[- ]accredited\b", "award/accreditation claim"),
    (r"\b\d{2,}\s*(\+\s*)?(five[- ]star|5[- ]star)?\s*reviews\b|\b(5|five)[- ]star\s+rated\b", "review/rating claim"),
    (r"\bcertified\s+(arborists?|technicians?|installers?|inspectors?)\b", "certification claim"),
    (r"[\"“][^\"”]{25,}[\"”]\s*(?:<[^>]+>\s*)*[—–-]\s*[A-Z][a-z]+\s+[A-Z]\.?", "testimonial attribution"),
]
SOFT_CLAIMS = [
    (r"\bguarantee[ds]?\b", "guarantee: who guarantees it, and is it written down?"),
    (r"\b#\s?1\b|\bnumber one\b", "superlative ranking claim"),
    (r"\bfree (estimates?|quotes?|inspections?)\b", "'free' offer must be honored by the actual provider"),
    (r"\bsame[- ]day\b|\b24/7\b|\b24 hours?\b|\bwithin (an|one|1|\d+) hours?\b", "availability promise must be true"),
    (r"\b(cheapest|lowest)\s+(price|prices|rates?|quotes?)\b|\b(cheapest|lowest prices?)\s+in\s+[A-Z]", "price superlative"),
]
PHONE_RE = re.compile(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.links, self.imgs, self.h1 = "", {}, [], [], 0
        self.canonical, self.jsonld, self.tels, self.classes = None, [], [], set()
        self._in_title = self._in_ld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for c in (a.get("class") or "").split():
            self.classes.add(c)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and a.get("name"):
            self.meta[a["name"].lower()] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if a["href"].startswith("tel:"):
                self.tels.append(a["href"][4:])
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "h1":
            self.h1 += 1
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_ld:
            self.jsonld.append("".join(self._buf))
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self._buf.append(data)


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def keyword_in(keyword, text):
    need = [t for t in tokens(keyword) if t not in STOP]
    have = set(tokens(text))
    return all(t in have for t in need) if need else True


def shingles(text, names, k=5):
    t = text.lower()
    for nme in sorted({n.lower() for n in names if n}, key=len, reverse=True):
        t = t.replace(nme, " placeholdercity ")
    words = tokens(t)
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def walk_jsonld(obj, types, keys):
    if isinstance(obj, dict):
        t = obj.get("@type")
        for x in (t if isinstance(t, list) else [t]):
            if x:
                types.add(x)
        for k, v in obj.items():
            keys.add(k)
            walk_jsonld(v, types, keys)
    elif isinstance(obj, list):
        for v in obj:
            walk_jsonld(v, types, keys)


LOCAL_BUSINESS_TYPES = {"LocalBusiness", "HomeAndConstructionBusiness", "Plumber", "Electrician", "HVACBusiness",
                        "RoofingContractor", "Locksmith", "MovingCompany", "HousePainter", "GeneralContractor",
                        "AutomotiveBusiness", "AutoRepair", "Dentist", "LegalService", "MedicalBusiness",
                        "InsuranceAgency", "FinancialService", "ProfessionalService"}


def resolve(dist, href):
    path = href.split("#")[0].split("?")[0]
    if not path or path == "/":
        return os.path.join(dist, "index.html")
    rel = path.lstrip("/")
    if path.endswith("/"):
        return os.path.join(dist, rel, "index.html")
    candidate = os.path.join(dist, rel)
    return candidate if os.path.splitext(rel)[1] else os.path.join(dist, rel, "index.html")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--dist", help="built site folder (default <project>/dist)")
    ap.add_argument("--launch", action="store_true", help="apply launch-gate checks")
    ap.add_argument("--out", help="write the markdown report here")
    a = ap.parse_args(argv)

    dist = a.dist or os.path.join(a.project, "dist")
    report_path = os.path.join(dist, "build-report.json")
    if not os.path.exists(report_path):
        sys.exit(f"{report_path} missing - run scripts/build_site.py {a.project} first")
    build = load_json(report_path)
    cfg = load_json(os.path.join(a.project, "site", "site.json"))
    mode = cfg.get("mode", "lead_gen")
    phone_e164 = build.get("phone_e164", "")
    issues = []  # (severity, page, message)

    def add(sev, page, msg):
        issues.append((sev, page, msg))

    names = [cfg.get("primary_city", "")] + list(cfg.get("areas_served") or [])
    texts, titles, descs = {}, {}, {}
    for p in build["pages"]:
        url = p["url"]
        f = os.path.join(dist, p["file"])
        with open(f, encoding="utf-8") as fh:
            raw = fh.read()
        d = Doc()
        d.feed(raw)
        title = d.title.strip()
        desc = d.meta.get("description", "").strip()

        # ---------------- SEO basics
        if not title:
            add("ERROR", url, "missing <title>")
        elif not (TITLE_LEN[0] <= len(title) <= TITLE_LEN[1]) and p["type"] not in ("legal", "hub"):
            add("WARN", url, f"title length {len(title)} (aim {TITLE_LEN[0]}-{TITLE_LEN[1]}): {title}")
        if not desc and not p["noindex"]:
            add("ERROR", url, "missing meta description")
        elif desc and not (DESC_LEN[0] <= len(desc) <= DESC_LEN[1]) and p["type"] not in ("legal", "hub"):
            add("WARN", url, f"meta description length {len(desc)} (aim {DESC_LEN[0]}-{DESC_LEN[1]})")
        if d.h1 != 1:
            add("ERROR", url, f"{d.h1} <h1> tags (need exactly 1)")
        if not d.canonical or not d.canonical.startswith("http"):
            add("ERROR", url, "canonical missing or not absolute")
        titles.setdefault(title, []).append(url)
        if desc:
            descs.setdefault(desc, []).append(url)

        # ---------------- writer text (no shortcodes/boilerplate)
        body_text = ""
        if p.get("source"):
            with open(os.path.join(a.project, p["source"]), encoding="utf-8") as fh:
                meta, body = parse_front_matter(fh.read())
            body_text = strip_tags(render(body, lambda n, arg: ""))
            texts[url] = (p["type"], body_text, [p.get("area") or ""] + names)
            kw = p.get("keyword")
            if kw:
                if not keyword_in(kw, title):
                    add("WARN", url, f"primary keyword '{kw}' not fully in title")
                if not keyword_in(kw, p.get("h1") or ""):
                    add("WARN", url, f"primary keyword '{kw}' not fully in H1")
                first = " ".join(body_text.split()[:120])
                if not keyword_in(kw, first + " " + (p.get("h1") or "")):
                    add("WARN", url, f"primary keyword '{kw}' not in the H1 + first 120 words")
            need = MIN_WORDS.get(p["type"])
            if need and p["words"] < need:
                add("WARN", url, f"thin content: {p['words']} words (target {need}+ for {p['type']} pages)")
        elif p["type"] in MIN_WORDS:
            add("WARN", url, "page has no source file")

        # ---------------- honesty
        visible = strip_tags(raw)
        for pat, label in PLACEHOLDERS:
            if re.search(pat, visible, re.I):
                add("ERROR", url, f"placeholder: {label}")
        scan = body_text + " " + title + " " + desc
        for pat, label in CLAIMS:
            m = re.search(pat, scan, re.I)
            if m:
                if mode == "lead_gen":
                    add("ERROR", url, f"{label}: \"{m.group(0)}\" - a referral site cannot claim this")
                else:
                    add("WARN", url, f"{label}: \"{m.group(0)}\" - confirm the tenant can substantiate it")
        for pat, label in SOFT_CLAIMS:
            m = re.search(pat, scan, re.I)
            if m:
                add("WARN", url, f"{label}: \"{m.group(0)}\"")

        # ---------------- phone numbers
        expected_digits = re.sub(r"\D", "", phone_e164)[-10:]
        for t in d.tels:
            if t != phone_e164:
                add("ERROR", url, f"tel: link {t} does not match tracking number {phone_e164}")
        for ph in PHONE_RE.findall(scan):
            if re.sub(r"\D", "", ph)[-10:] != expected_digits:
                add("WARN", url, f"other phone number in content: {ph}")

        # ---------------- links & images
        for href in d.links:
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "//")):
                if href.startswith("http://"):
                    add("WARN", url, f"insecure external link {href}")
                continue
            if not href.startswith("/"):
                add("WARN", url, f"relative link '{href}' (use root-relative /path/)")
                continue
            if not os.path.exists(resolve(dist, href)):
                add("ERROR", url, f"broken internal link {href}")
        for img in d.imgs:
            if not (img.get("alt") or "").strip():
                add("ERROR", url, f"image without alt text: {img.get('src')}")
            src = img.get("src") or ""
            if src.startswith("/") and not os.path.exists(resolve(dist, src)):
                add("ERROR", url, f"missing image file {src}")

        # ---------------- structured data
        for block in d.jsonld:
            try:
                data = json.loads(block)
            except json.JSONDecodeError as exc:
                add("ERROR", url, f"invalid JSON-LD: {exc}")
                continue
            types, keys = set(), set()
            walk_jsonld(data, types, keys)
            if mode == "lead_gen":
                if types & LOCAL_BUSINESS_TYPES:
                    add("ERROR", url, f"lead_gen site uses business schema types {sorted(types & LOCAL_BUSINESS_TYPES)}")
                if "address" in keys:
                    add("ERROR", url, "lead_gen site publishes an address in schema")
            if "aggregateRating" in keys or "review" in keys:
                add("ERROR" if mode == "lead_gen" else "WARN", url,
                    "review/rating schema: self-serving review markup is ineligible and must reflect real reviews")

        # ---------------- compliance
        if mode == "lead_gen" and "disclosure" not in d.classes:
            add("ERROR", url, "referral disclosure missing")
        if len(raw) > 150_000:
            add("WARN", url, f"HTML is {len(raw) // 1024} KB")

    # ---------------- site-level
    for t, urls in titles.items():
        if len(urls) > 1:
            add("ERROR", ", ".join(urls), f"duplicate title: {t}")
    for dsc, urls in descs.items():
        if len(urls) > 1:
            add("ERROR", ", ".join(urls), "duplicate meta description")
    urls = {p["url"] for p in build["pages"]}
    for need in ("/privacy-policy/", "/terms/"):
        if need not in urls:
            add("ERROR", "site", f"missing {need}")
    for want in ("/about/", "/contact/"):
        if want not in urls:
            add("WARN", "site", f"no {want} page (trust + E-E-A-T)")
    sm_path = os.path.join(dist, "sitemap.xml")
    sitemap = ""
    if os.path.exists(sm_path):
        with open(sm_path, encoding="utf-8") as fh:
            sitemap = fh.read()
    for p in build["pages"]:
        if not p["noindex"] and (build["base_url"] + p["url"]) not in sitemap:
            add("ERROR", p["url"], "indexable page missing from sitemap.xml")

    # near-duplicates (templated pages)
    sh = {u: (t, shingles(txt, nm)) for u, (t, txt, nm) in texts.items()}
    comparable = [u for u, (t, _) in sh.items() if t in ("area", "service", "home", "cost")]
    for u1, u2 in itertools.combinations(comparable, 2):
        t1, t2 = sh[u1][0], sh[u2][0]
        if t1 != t2 and not ({t1, t2} == {"area", "home"}):
            continue
        sim = jaccard(sh[u1][1], sh[u2][1])
        if sim >= DUP_ERR:
            add("ERROR", f"{u1} ~ {u2}", f"near-duplicate content ({sim:.0%} shared 5-word phrases, names normalized): "
                                          "templated/doorway risk")
        elif sim >= DUP_WARN:
            add("WARN", f"{u1} ~ {u2}", f"high overlap ({sim:.0%}); add page-specific substance")

    # launch gate
    base = build.get("base_url", "")
    if re.search(r"example\.(com|org)|\.invalid|localhost|127\.0\.0\.1", base):
        add("ERROR" if a.launch else "INFO", "site", f"base_url is not a real domain: {base}")
    if cfg.get("staging"):
        add("ERROR" if a.launch else "INFO", "site", "staging=true (noindex + robots Disallow)")
    digits = re.sub(r"\D", "", phone_e164)[-10:]
    if not digits or re.search(r"55501\d\d$", digits) or digits[:3] == "555":
        add("ERROR" if a.launch else "INFO", "site", f"phone {phone_e164 or '(none)'} is a placeholder - set the call-tracking number")
    tr = cfg.get("tracking") or {}
    if a.launch and not (tr.get("ga4_id") or tr.get("head_html")):
        add("WARN", "site", "no analytics configured (GA4 or head_html)")
    if a.launch and not tr.get("gsc_verification"):
        add("WARN", "site", "no Google Search Console verification meta (DNS verification is fine too)")
    f = cfg.get("form") or {}
    if f.get("enabled") and (not f.get("action") or "demo" in f.get("action", "")):
        add("ERROR" if a.launch else "INFO", "site", "form enabled but action endpoint is missing/demo")
    if mode == "tenant":
        t = cfg.get("tenant") or {}
        if not t.get("license"):
            add("WARN", "site", "tenant mode without a license number - many states require it in contractor advertising")

    errors = [i for i in issues if i[0] == "ERROR"]
    warns = [i for i in issues if i[0] == "WARN"]
    infos = [i for i in issues if i[0] == "INFO"]
    verdict = "FAIL" if errors else "PASS"
    lines = [f"# QA report - {cfg.get('brand')} ({'LAUNCH GATE' if a.launch else 'development'})", "",
             f"**{verdict}**: {len(errors)} errors, {len(warns)} warnings, {len(infos)} info. "
             f"Pages checked: {len(build['pages'])}. Mode: {mode}.", ""]
    if issues:
        order = {"ERROR": 0, "WARN": 1, "INFO": 2}
        lines.append(md_table([[s, p, m] for s, p, m in sorted(issues, key=lambda i: (order[i[0]], i[1]))],
                              ["Severity", "Page", "Issue"]))
    lines += ["", "Errors block launch. Warnings need a decision: fix them, or record why they're acceptable in "
              "research/09-content-qa.md."]
    text = "\n".join(lines) + "\n"
    if a.out:
        write_text(a.out, text)
        print(f"{verdict}: {len(errors)} errors, {len(warns)} warnings -> {a.out}")
    else:
        print(text)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
