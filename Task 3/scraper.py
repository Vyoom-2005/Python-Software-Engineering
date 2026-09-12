#!/usr/bin/env python3
from __future__ import annotations

import argparse

from scraper.pipeline import DEFAULT_URL, run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated web scraping and ETL pipeline")
    parser.add_argument("--url", default=DEFAULT_URL, help="Public target URL")
    parser.add_argument("--pages", type=int, default=5, help="Maximum pages to scrape")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between pages in seconds")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    summary = run_pipeline(
        start_url=args.url,
        pages=args.pages,
        delay=args.delay,
        output_dir=args.output,
    )
    print("Scraping completed successfully.")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
