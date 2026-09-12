# Automated Web Scraping & Data Extraction Pipeline

A practical ETL web-scraping pipeline using **Requests + BeautifulSoup**.

## Target

The default target is the public **Quotes to Scrape** website:
`https://quotes.toscrape.com/`

The pipeline extracts:
- quote text
- author
- tags
- source URL

It then transforms the HTML into structured CSV/JSON data and creates a
summary statistics report.

## Features

- Custom User-Agent headers
- Request timeout
- Rate limiting between requests
- Retry with exponential backoff
- Pagination support
- Clean HTML parsing with BeautifulSoup
- Deduplication
- CSV and JSON output
- Automated summary report
- CLI arguments
- Unit tests with mocked HTML/network calls

## Installation

```bash
python -m venv .venv
```

Activate the environment and install:

```bash
python -m pip install -r requirements.txt
```

## Run

Scrape the default site:

```bash
python scraper.py
```

Scrape a limited number of pages:

```bash
python scraper.py --pages 2
```

Custom delay:

```bash
python scraper.py --pages 3 --delay 1.0
```

The command creates:

```text
output/quotes.csv
output/quotes.json
output/summary_report.txt
```

## ETL flow

1. **Extract**: download public HTML pages using Requests.
2. **Transform**: parse quote cards, normalize whitespace, split tags, and
   deduplicate records.
3. **Load**: save CSV and JSON files.
4. **Analyze**: calculate quote count, unique authors, tag frequencies,
   average quote length, and page count.

## Scraping best practices

The scraper uses a descriptive custom User-Agent, a configurable delay,
timeouts, limited retries, and exponential backoff. It is intended for
public pages and should only be used where the target site's terms and
robots policy permit automated access.

## Tests

Tests do not require internet access:

```bash
python -m unittest discover -s tests -v
```

The tests cover HTML extraction, transformation, retry behavior, report
generation, CSV output, and malformed HTML handling.
