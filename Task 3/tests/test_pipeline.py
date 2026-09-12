import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from scraper.pipeline import (
    ScraperError,
    build_summary,
    fetch_page,
    parse_quotes,
    write_csv,
    write_json,
    write_summary,
)


HTML = '''
<html><body>
<div class="quote">
  <span class="text">“First quote”</span>
  <small class="author">Author One</small>
  <div class="tags">
    <a class="tag">life</a><a class="tag">inspiration</a><a class="tag">life</a>
  </div>
</div>
<div class="quote">
  <span class="text">“Second quote”</span>
  <small class="author">Author Two</small>
  <div class="tags"><a class="tag">books</a></div>
</div>
<li class="next"><a href="/page/2/">next</a></li>
</body></html>
'''


class PipelineTests(unittest.TestCase):
    def test_parse_quotes_and_next_page(self):
        records = parse_quotes(HTML, "https://quotes.toscrape.com/")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].author, "Author One")
        self.assertEqual(records[0].tags, "inspiration|life")

    def test_summary(self):
        records = parse_quotes(HTML, "https://quotes.toscrape.com/")
        summary = build_summary(records, 1)
        self.assertEqual(summary["records_extracted"], 2)
        self.assertEqual(summary["unique_authors"], 2)
        self.assertEqual(summary["top_tags"]["life"], 1)

    def test_output_files(self):
        records = parse_quotes(HTML, "https://quotes.toscrape.com/")
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "quotes.csv"
            json_path = Path(tmp) / "quotes.json"
            txt_path = Path(tmp) / "summary.txt"
            write_csv(records, str(csv_path))
            write_json(records, str(json_path))
            write_summary(build_summary(records, 1), str(txt_path))

            with csv_path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 2)
            self.assertTrue(json_path.exists())
            self.assertIn("Records extracted: 2", txt_path.read_text(encoding="utf-8"))

    def test_retry_success(self):
        session = Mock()
        first = requests.RequestException("temporary")
        response = Mock(text="OK")
        response.raise_for_status.return_value = None
        session.get.side_effect = [first, response]

        with patch("scraper.pipeline.time.sleep") as sleep:
            result = fetch_page(session, "https://example.com", retries=1)

        self.assertEqual(result, "OK")
        sleep.assert_called_once()

    def test_retry_failure(self):
        session = Mock()
        session.get.side_effect = requests.RequestException("down")

        with patch("scraper.pipeline.time.sleep"):
            with self.assertRaises(ScraperError):
                fetch_page(session, "https://example.com", retries=2)

    def test_malformed_cards_are_skipped(self):
        html = '<div class="quote"><span class="text">Only text</span></div>'
        self.assertEqual(parse_quotes(html, "https://example.com"), [])

    def test_invalid_arguments(self):
        from scraper.pipeline import scrape
        with self.assertRaises(ValueError):
            scrape(max_pages=0)
        with self.assertRaises(ValueError):
            scrape(delay=-1)


if __name__ == "__main__":
    unittest.main()
