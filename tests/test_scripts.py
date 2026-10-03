"""Test suite for the local-SEO-Agent toolchain. Run: python3 -m unittest discover -s tests -v"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
FIX = os.path.join(ROOT, "tests", "fixtures")

import build_site  # noqa: E402
import city_finder  # noqa: E402
import common  # noqa: E402
import fetch_census_data  # noqa: E402
import keyword_tool  # noqa: E402
import lead_economics  # noqa: E402
import mdlite  # noqa: E402
import niche_scorer  # noqa: E402
import qa_site  # noqa: E402
import serp_audit  # noqa: E402


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def run(fn, argv):
    """Call a script main() capturing stdout; returns (exit_code, output)."""
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            fn(argv)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    return code, buf.getvalue()


class TestData(unittest.TestCase):
    def test_niches_schema(self):
        niches, meta = common.load_niches()
        self.assertGreaterEqual(len(niches), 80)
        tags = set(common.load_json(os.path.join(ROOT, "data", "us_states.json"))["_meta"]["tag_definitions"])
        for n in niches.values():
            self.assertIn(n["demand_tier"], meta["demand_tiers"])
            self.assertIn(n["urgency"], ("emergency", "mixed", "planned"))
            self.assertIn(n["regulatory_risk"], ("low", "medium", "high", "extreme"))
            self.assertTrue(set(n["geo_tags"]) <= tags, n["id"])
            self.assertTrue(n["seed_keywords"] and n["sub_services"], n["id"])
            for k in ("rank_and_rent", "pay_per_call", "nationwide"):
                self.assertTrue(0 <= n["model_fit"][k] <= 10)
            for rng in ("ppc_payout_usd", "rent_usd_month", "per_lead_usd"):
                if n[rng]:
                    self.assertLessEqual(n[rng][0], n[rng][1], (n["id"], rng))

    def test_places_load(self):
        places = common.load_places(os.path.join(ROOT, "data", "us_places.csv"))
        self.assertGreater(len(places), 15000)
        tulsa = common.find_place(places, "Tulsa", "OK")
        self.assertIsNotNone(tulsa)
        self.assertGreater(tulsa["population"], 300000)

    def test_parse_city_arg(self):
        self.assertEqual(common.parse_city_arg("Tulsa, OK"), ("Tulsa", "OK"))
        self.assertEqual(common.parse_city_arg("Broken Arrow Oklahoma"), ("Broken Arrow", "OK"))
        self.assertEqual(common.parse_city_arg("Boise, idaho"), ("Boise", "ID"))


class TestCensusParsing(unittest.TestCase):
    def test_offline_join(self):
        pep = os.path.join(FIX, "census_pep.csv")
        acs = os.path.join(FIX, "census_acs.json")
        gaz = os.path.join(FIX, "census_gaz.txt")
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "census.csv")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                fetch_census_data.main(["--pep-file", pep, "--acs-file", acs, "--gaz-file", gaz, "--out", out,
                                        "--min-pop", "1000"])
            rows = {r["name"]: r for r in common.read_csv(out)}
        self.assertIn("Testville", rows)            # incorporated city: PEP population wins
        self.assertEqual(rows["Testville"]["population"], "120500")
        self.assertEqual(rows["Testville"]["population_source"], "pep2024")
        self.assertEqual(rows["Testville"]["owner_occupied_pct"], "60.0")
        self.assertIn("Suburbia", rows)             # CDP: ACS population, clean name
        self.assertEqual(rows["Suburbia"]["place_type"], "CDP")
        self.assertEqual(rows["Suburbia"]["median_hh_income"], "")  # sentinel -> blank
        self.assertNotIn("Tinytown", rows)          # below min-pop

    def test_clean_names(self):
        self.assertEqual(fetch_census_data.clean_place_name("Tulsa city"), ("Tulsa", "city"))
        self.assertEqual(fetch_census_data.clean_place_name("Nashville-Davidson metropolitan government (balance)")[0],
                         "Nashville")
        self.assertEqual(fetch_census_data.clean_place_name("Brandon CDP"), ("Brandon", "CDP"))


class TestCityFinder(unittest.TestCase):
    def test_rank_and_service_area(self):
        code, out = run(city_finder.main, ["rank", "--niche", "septic", "--states", "NC", "--top", "5"])
        self.assertEqual(code, 0)
        self.assertIn("City shortlist - Septic Services", out)
        code, out = run(city_finder.main, ["service-area", "Tulsa, OK", "--radius", "20", "--format", "json"])
        towns = json.loads(out)
        self.assertTrue(any(t["town"] == "Broken Arrow" for t in towns))

    def test_size_and_cluster_fit(self):
        centre = (50000 * 300000) ** 0.5
        self.assertAlmostEqual(city_finder.size_fit(centre, 50000, 300000), 1.0)
        self.assertGreaterEqual(city_finder.size_fit(100000, 50000, 300000), 0.85)
        self.assertLess(city_finder.size_fit(20000, 50000, 300000), 0.85)
        self.assertEqual(city_finder.size_fit(5000000, 50000, 300000), 0.0)
        self.assertEqual(city_finder.cluster_fit(200000, 150000, 900000), 1.0)
        self.assertLess(city_finder.cluster_fit(3000000, 40000, 300000), 0.2)  # rural niche next to a big metro

    def test_profiles_cover_niches(self):
        niches, _ = common.load_niches()
        self.assertTrue(all(n["market_profile"] in city_finder.PROFILES for n in niches.values()))


class TestNicheScorer(unittest.TestCase):
    def test_rank_models(self):
        for model in ("rank_and_rent", "pay_per_call", "nationwide"):
            code, out = run(niche_scorer.main, ["rank", "--model", model, "--format", "json", "--top", "10"])
            rows = json.loads(out)
            self.assertEqual(len(rows), 10)
            self.assertEqual(rows, sorted(rows, key=lambda r: -r["score"]))

    def test_risk_filter_excludes_extreme(self):
        _, out = run(niche_scorer.main, ["rank", "--risk-tolerance", "low", "--format", "json", "--top", "100"])
        ids = {r["id"] for r in json.loads(out)}
        self.assertNotIn("addiction-treatment", ids)
        self.assertNotIn("medicare", ids)
        self.assertNotIn("locksmith", ids)  # high spam scrutiny filtered at low tolerance

    def test_city_potential(self):
        _, out = run(niche_scorer.main, ["rank", "--city", "Tulsa, OK", "--format", "json", "--top", "5"])
        self.assertIn("potential_usd_mo", json.loads(out)[0])


class TestKeywordTool(unittest.TestCase):
    def test_variants_and_numbers(self):
        self.assertEqual(keyword_tool.service_variants("Tree Trimming & Pruning"), ["tree trimming", "tree pruning"])
        self.assertEqual(keyword_tool.service_variants("Pier & Beam Repair"), ["pier and beam repair"])
        self.assertEqual(keyword_tool.parse_number("1,300"), 1300)
        self.assertEqual(keyword_tool.parse_number("$4.50"), 4.5)
        self.assertEqual(keyword_tool.parse_number("1K - 10K"), 3162)
        self.assertIsNone(keyword_tool.parse_number("--"))

    def test_expand_volume_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            kw = os.path.join(tmp, "kw.csv")
            run(keyword_tool.main, ["expand", "--niche", "tree-service", "--city", "Tulsa, OK", "--areas", "3", "--out", kw])
            rows = common.read_csv(kw)
            self.assertTrue(any(r["keyword"] == "tree service tulsa" for r in rows))
            self.assertTrue(any(r["page_type"] == "area" for r in rows))
            code, _ = run(keyword_tool.main, ["volume", "--provider", "csv", "--file", os.path.join(FIX, "kwp_export.csv"),
                                              "--in", kw])
            self.assertEqual(code, 0)
            rows = {r["keyword"]: r for r in common.read_csv(kw)}
            self.assertEqual(rows["tree service tulsa"]["search_volume"], "590")
            rep = os.path.join(tmp, "rep.md")
            run(keyword_tool.main, ["report", "--in", kw, "--out", rep])
            text = read(rep)
            self.assertIn("Traffic and leads by ranking scenario", text)
            self.assertNotIn("ESTIMATES", text)


class TestSerpAudit(unittest.TestCase):
    def test_score_fixtures(self):
        lists = serp_audit.load_domain_lists()
        audits = serp_audit.load_audits([os.path.join(FIX, "serp_dfs_organic.json"), os.path.join(FIX, "serp_manual.json")], lists)
        weak = serp_audit.score_audit(audits[0], lists, "Exampleville")
        strong = serp_audit.score_audit(audits[1], lists, "Exampleville")
        self.assertGreaterEqual(weak["weak_in_top10"], 5)
        self.assertLess(weak["difficulty"], strong["difficulty"])
        self.assertEqual(serp_audit.classify("www.yelp.com", lists), "directory")
        self.assertEqual(serp_audit.classify("acme-roofing.com", lists), "local_business")


class TestLeadEconomics(unittest.TestCase):
    def test_rent_capped_by_market(self):
        code, out = run(lead_economics.main, ["--niche", "roofing", "--leads", "6", "15", "30", "--ticket", "9000",
                                              "--close-rate", "0.25", "--margin", "0.35", "--cpc", "28", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out[out.index("{\n"):])
        self.assertLessEqual(data["recommended_rent"]["target"], 3000)
        self.assertEqual(len(data["scenarios"]), 3)

    def test_ramp(self):
        self.assertEqual(lead_economics.ramp_factor(1, 1, 6), 0.0)
        self.assertEqual(lead_economics.ramp_factor(6, 1, 6), 1.0)


class TestMarkdown(unittest.TestCase):
    def test_render_subset(self):
        meta, body = mdlite.parse_front_matter("---\ntitle: X\nhero: false\n---\n## Hi\n\n- a\n- b\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
        self.assertEqual(meta, {"title": "X", "hero": False})
        html_out = mdlite.render(body)
        self.assertIn('<h2 id="hi">Hi</h2>', html_out)
        self.assertIn("<ul><li>a</li><li>b</li></ul>", html_out)
        self.assertIn("<table>", html_out)
        self.assertIn("&lt;script&gt;", mdlite.render("<script>alert(1)</script> text"[0:0] + "a <script> b"))

    def test_snake_case_not_italic(self):
        self.assertNotIn("<em>", mdlite.inline("snake_case_word and 2*3*4"))


class TestSiteBuildAndQA(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project = os.path.join(self.tmp, "demo")
        shutil.copytree(os.path.join(ROOT, "examples", "demo-tree-service"), self.project)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return build_site.SiteBuilder(self.project).build()

    def qa(self, *extra):
        return run(qa_site.main, [self.project, *extra])

    def test_demo_builds_and_passes_dev_qa(self):
        report = self.build()
        urls = {p["url"] for p in report}
        for u in ("/", "/services/", "/services/tree-removal/", "/areas/riverside/", "/privacy-policy/", "/terms/"):
            self.assertIn(u, urls)
        dist = os.path.join(self.project, "dist")
        for f in ("sitemap.xml", "robots.txt", "404.html", "favicon.svg", "assets/site.css", "build-report.json"):
            self.assertTrue(os.path.exists(os.path.join(dist, f)), f)
        home = read(os.path.join(dist, "index.html"))
        self.assertIn('"@type": "FAQPage"', home)
        self.assertIn('class="disclosure"', home)
        self.assertNotIn('"address"', home)
        code, out = self.qa()
        self.assertEqual(code, 0, out)
        code, out = self.qa("--launch")
        self.assertEqual(code, 1)  # demo is staging with placeholder phone/domain
        self.assertIn("staging=true", out)

    def test_qa_blocks_fake_claims_and_templated_pages(self):
        areas = os.path.join(self.project, "site", "content", "areas")
        template = ("---\ntitle: Tree Service in {c}, OK | Demo\ndescription: Tree service in {c}, OK. Call now for "
                    "removal, trimming and stump grinding from a local pro near you.\ntype: area\narea: {c}\n---\n"
                    + "Our team is licensed and insured with 20 years of experience serving {c}. " * 3
                    + " ".join(f"Tree care in {{c}} includes pruning step {i} and removal step {i} for every yard." for i in range(40)))
        for c in ("Cedar Falls", "Mill Creek"):
            with open(os.path.join(areas, common.slugify(c) + ".md"), "w") as fh:
                fh.write(template.format(c=c))
        self.build()
        code, out = self.qa()
        self.assertEqual(code, 1)
        self.assertIn("near-duplicate content", out)
        self.assertIn("licensing/insurance claim", out)
        self.assertIn("'our team' implies you perform the work", out)
        self.assertIn("years-in-business claim", out)

    def test_tenant_mode_schema(self):
        cfg_path = os.path.join(self.project, "site", "site.json")
        cfg = common.load_json(cfg_path)
        cfg["mode"] = "tenant"
        cfg["tenant"].update({"legal_name": "Acme Tree LLC", "license": "TX-123", "show_address": True,
                              "schema_type": "HomeAndConstructionBusiness",
                              "address": {"street": "1 Main St", "city": "Demo City", "region": "OK", "postal": "74000"}})
        common.save_json(cfg_path, cfg)
        self.build()
        home = read(os.path.join(self.project, "dist", "index.html"))
        self.assertIn('"HomeAndConstructionBusiness"', home)
        self.assertIn('"PostalAddress"', home)
        self.assertIn("License # TX-123", home)
        self.assertNotIn('class="disclosure"', home)


class TestNationalScope(unittest.TestCase):
    def test_state_hubs_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "site", "content", "locations", "texas"))
            common.save_json(os.path.join(tmp, "site", "site.json"), {
                "brand": "Flood Help Line", "base_url": "https://floodhelp.invalid", "mode": "lead_gen",
                "scope": "national", "niche_name": "Water Damage Restoration", "phone": "(800) 555-0142"})
            with open(os.path.join(tmp, "site", "content", "index.md"), "w") as fh:
                fh.write("---\ntitle: Water Damage Help | Flood Help Line\ntype: home\n---\nHello.\n")
            with open(os.path.join(tmp, "site", "content", "locations", "texas", "houston.md"), "w") as fh:
                fh.write("---\ntitle: Water Damage in Houston, TX\ntype: area\narea: Houston\n---\nHouston.\n")
            with contextlib.redirect_stdout(io.StringIO()):
                report = build_site.SiteBuilder(tmp).build()
            urls = {p["url"]: p for p in report}
            self.assertIn("/locations/", urls)
            self.assertIn("/locations/texas/", urls)
            self.assertTrue(urls["/locations/texas/"]["auto"])
            self.assertIn("Houston", urls["/locations/texas/"]["description"])


class TestClaudeConfig(unittest.TestCase):
    """Frontmatter of agents and skills must stay machine-parseable (quoted descriptions, valid skill refs)."""

    @staticmethod
    def frontmatter(path):
        text = read(path)
        assert text.startswith("---\n"), path
        block = text[4:text.index("\n---\n", 4)]
        fm, key = {}, None
        for line in block.splitlines():
            if line.startswith("  - ") and key:
                fm.setdefault(key, []).append(line[4:].strip())
            elif ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                fm[key] = val if val else []
        return fm

    def test_agents_and_skills(self):
        claude = os.path.join(ROOT, ".claude")
        skills = {}
        for name in os.listdir(os.path.join(claude, "skills")):
            fm = self.frontmatter(os.path.join(claude, "skills", name, "SKILL.md"))
            self.assertEqual(fm["name"], name)
            self.assertTrue(fm["description"].startswith('"') and fm["description"].endswith('"'), name)
            self.assertLess(len(fm["description"]), 1500, name)
            skills[name] = fm
        self.assertIn("rank-and-rent", skills)
        self.assertIn("war-room", skills)
        agents = [f for f in os.listdir(os.path.join(claude, "agents")) if f.endswith(".md")]
        self.assertEqual(len(agents), 14)
        for f in agents:
            fm = self.frontmatter(os.path.join(claude, "agents", f))
            self.assertEqual(fm["name"], f[:-3])
            self.assertTrue(fm["description"].startswith('"'), f)
            self.assertIn("tools", fm)
            for sk in fm.get("skills", []):
                self.assertIn(sk, skills, f"{f} preloads unknown skill {sk}")


if __name__ == "__main__":
    unittest.main()
