"""Regression checks for the public company verification dashboard."""

import json
from pathlib import Path
import tempfile
import unittest

from progress import build_progress, classify_status


ROOT = Path(__file__).resolve().parents[1]


class ProgressTests(unittest.TestCase):
    def test_verification_is_separate_from_location(self):
        self.assertEqual(classify_status({
            "verification_status": "partial", "location": {"status": "verified"}
        })[0], "partial")
        self.assertEqual(classify_status({"location": {"status": "verified"}})[0], "not_verified")
        self.assertEqual(classify_status({"verification_status": "verified"})[0], "verified")
        self.assertEqual(classify_status({"verification_status": "unresolved"})[0], "unresolved")
        self.assertEqual(classify_status({"verification_status": "new_unknown_value"})[0], "not_verified")

    def test_page_rows_and_escaping(self):
        companies = [
            {
                "name": "A&B <Company>", "_slug": "a-and-b", "_source_path": "companies/a-and-b.yml",
                "verification_status": "verified", "industry": "Technology",
                "last_verified": "2026-10-07", "location": {"status": "verified"},
            },
            {
                "name": "Partial", "_slug": "partial", "_source_path": "companies/partial.yml",
                "verification_status": "partial", "location": {"status": "verified"},
            },
            {
                "name": "Unresolved", "_slug": "unresolved", "_source_path": "companies/unresolved.yml",
                "verification_status": "unresolved", "location": {"status": "unresolved"},
            },
            {
                "name": "No status", "_slug": "no-status", "_source_path": "companies/no-status.yml",
                "location": {"status": "verified"},
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            counts = build_progress(companies, directory)
            page = (Path(directory) / "progress.html").read_text(encoding="utf-8")
        self.assertEqual(counts["verified"], 1)
        self.assertEqual(counts["partial"], 1)
        self.assertEqual(counts["unresolved"], 1)
        self.assertEqual(counts["not_verified"], 1)
        self.assertEqual(page.count('<tr data-status='), 4)
        self.assertIn("A&amp;B &lt;Company&gt;", page)
        self.assertNotIn("A&B <Company>", page)
        self.assertIn("companies/a-and-b.html", page)
        self.assertIn("companies/a-and-b.yml", page)
        self.assertIn("1 of 4 companies fully verified", page)

    def test_full_build_lists_every_company(self):
        """Run after scripts/build.py in CI."""
        companies_json = ROOT / "_site" / "companies.json"
        progress_html = ROOT / "_site" / "progress.html"
        if not companies_json.exists() or not progress_html.exists():
            self.skipTest("Full build not present")
        data = json.loads(companies_json.read_text(encoding="utf-8"))
        html = progress_html.read_text(encoding="utf-8")
        self.assertEqual(html.count('<tr data-status='), len(data))
        for company in data:
            self.assertIn('companies/' + company["_slug"] + '.html', html)
            self.assertIn(company["_source_path"], html)


if __name__ == "__main__":
    unittest.main()
