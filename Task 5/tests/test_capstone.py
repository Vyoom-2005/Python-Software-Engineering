import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from enterprise_report.api import fetch_json_records
from enterprise_report.data import InputDataError, load_csv, load_json, parse_records
from enterprise_report.pdf import create_pdf
from enterprise_report.processing import json_safe_summary, summarize
from enterprise_report.scheduler import run_scheduled


class CapstoneTests(unittest.TestCase):
    def setUp(self):
        self.records = parse_records([
            {"id": "1", "customer": "A", "category": "Software", "amount": "10.50", "status": "completed"},
            {"id": "2", "customer": "B", "category": "Cloud", "amount": 20, "status": "pending"},
            {"id": "3", "customer": "C", "category": "Software", "amount": 9, "status": "completed"},
        ])

    def test_json_loading_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"
            path.write_text(json.dumps([r.to_dict() for r in self.records]), encoding="utf-8")
            loaded = load_json(str(path))
            summary = summarize(loaded)
            self.assertEqual(summary["record_count"], 3)
            self.assertEqual(str(summary["total_amount"]), "39.50")
            self.assertEqual(summary["status_counts"]["completed"], 2)
            self.assertEqual(json_safe_summary(summary)["average_amount"], "13.17")

    def test_csv_loading(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            path.write_text(
                "id,customer,category,amount,status\n"
                "1,A,Software,10.5,completed\n"
                "2,B,Cloud,20,pending\n",
                encoding="utf-8",
            )
            loaded = load_csv(str(path))
            self.assertEqual(len(loaded), 2)

    def test_invalid_data(self):
        with self.assertRaises(InputDataError):
            parse_records([{"id": "1", "customer": "A", "category": "X", "amount": -1, "status": "ok"}])
        with self.assertRaises(InputDataError):
            parse_records([{"id": "1", "customer": "A", "category": "X", "amount": 1, "status": "ok"},
                           {"id": "1", "customer": "B", "category": "Y", "amount": 2, "status": "ok"}])

    def test_pdf_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.pdf"
            create_pdf(self.records, str(output))
            data = output.read_bytes()
            self.assertTrue(data.startswith(b"%PDF-1.4"))
            self.assertIn(b"Automated Python Capstone Report", data)
            self.assertGreater(len(data), 500)

    def test_scheduler(self):
        calls = []
        sleeps = []
        count = run_scheduled(lambda: calls.append(1), 0.01, runs=3, sleep_fn=lambda s: sleeps.append(s))
        self.assertEqual(count, 3)
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(sleeps), 2)

    def test_api_payload_is_parsed(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'[{"id":"1","customer":"A","category":"X","amount":5,"status":"ok"}]'

        with patch("enterprise_report.api.urlopen", return_value=FakeResponse()):
            result = fetch_json_records("https://example.test/data")
        self.assertEqual(len(result), 1)
        self.assertEqual(str(result[0].amount), '5')

    def test_cli_end_to_end(self):
        from enterprise_report.cli import main
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.pdf"
            summary = Path(tmp) / "summary.json"
            code = main([
                "--input", "examples/sales.json",
                "--output", str(output),
                "--summary", str(summary),
            ])
            self.assertEqual(code, 0)
            self.assertTrue(output.exists())
            self.assertTrue(summary.exists())
            self.assertEqual(json.loads(summary.read_text())["record_count"], 6)


if __name__ == "__main__":
    unittest.main()
