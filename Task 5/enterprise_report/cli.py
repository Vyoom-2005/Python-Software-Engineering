from __future__ import annotations

import argparse
import json
import sys

from .api import fetch_json_records
from .data import load_file
from .exceptions import ReportGeneratorError
from .pdf import create_pdf
from .processing import json_safe_summary, summarize
from .scheduler import run_scheduled


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reportgen",
        description="Generate automated PDF reports from JSON, CSV, or an HTTP JSON API.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Input JSON or CSV file.")
    source.add_argument("--url", help="HTTP endpoint returning JSON records.")
    parser.add_argument("--format", choices=["json", "csv"], help="Input format; inferred from extension when omitted.")
    parser.add_argument("--output", default="output/report.pdf", help="PDF output path.")
    parser.add_argument("--summary", help="Optional JSON summary output.")
    parser.add_argument("--schedule-minutes", type=float, help="Repeat the job at this interval.")
    parser.add_argument("--runs", type=int, help="Number of scheduled executions; omit for continuous mode.")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.runs is not None and args.runs < 1:
        parser.error("--runs must be at least 1")

    def job():
        records = (
            load_file(args.input, args.format)
            if args.input
            else fetch_json_records(args.url)
        )
        create_pdf(records, args.output)
        if args.summary:
            from pathlib import Path
            target = Path(args.summary)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(json_safe_summary(summarize(records)), indent=2) + "\n",
                encoding="utf-8",
            )
        print(f"Generated {args.output} from {len(records)} records.")

    try:
        if args.schedule_minutes is not None:
            run_scheduled(job, args.schedule_minutes, args.runs)
        else:
            job()
        return 0
    except KeyboardInterrupt:
        print("\\nScheduler stopped.")
        return 0
    except ReportGeneratorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: unexpected failure: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
