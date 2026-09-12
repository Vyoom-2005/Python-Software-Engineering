from __future__ import annotations

import csv
import json
import re
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://quotes.toscrape.com/"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PublicDataETL/1.0; +https://example.com/bot-info)"
}


@dataclass(frozen=True)
class Quote:
    quote: str
    author: str
    tags: str
    source_url: str


class ScraperError(RuntimeError):
    pass


def fetch_page(
    session: requests.Session,
    url: str,
    *,
    timeout: float = 10.0,
    retries: int = 3,
    backoff: float = 0.5,
) -> str:
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(backoff * (2 ** attempt))
    raise ScraperError(f"failed to fetch {url}: {last_error}") from last_error


def parse_quotes(html: str, source_url: str) -> List[Quote]:
    soup = BeautifulSoup(html, "html.parser")
    records: List[Quote] = []

    for card in soup.select("div.quote"):
        text_node = card.select_one("span.text")
        author_node = card.select_one("small.author")
        if not text_node or not author_node:
            continue

        text = re.sub(r"\s+", " ", text_node.get_text(" ", strip=True))
        author = re.sub(r"\s+", " ", author_node.get_text(" ", strip=True))
        tags = [
            re.sub(r"\s+", " ", tag.get_text(" ", strip=True))
            for tag in card.select("a.tag")
        ]

        if text and author:
            records.append(
                Quote(
                    quote=text,
                    author=author,
                    tags="|".join(sorted(set(tags))),
                    source_url=source_url,
                )
            )
    return records


def next_page_url(html: str, current_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one("li.next a")
    if not link or not link.get("href"):
        return None
    return requests.compat.urljoin(current_url, link["href"])


def scrape(
    start_url: str = DEFAULT_URL,
    *,
    max_pages: int = 5,
    delay: float = 0.5,
    session: Optional[requests.Session] = None,
) -> List[Quote]:
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")
    if delay < 0:
        raise ValueError("delay cannot be negative")

    own_session = session is None
    session = session or requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    records: List[Quote] = []
    url: Optional[str] = start_url

    try:
        for page_number in range(max_pages):
            if not url:
                break
            html = fetch_page(session, url)
            records.extend(parse_quotes(html, url))

            if page_number + 1 < max_pages:
                time.sleep(delay)
                url = next_page_url(html, url)
            else:
                url = None
    finally:
        if own_session:
            session.close()

    # Stable deduplication.
    unique = {}
    for record in records:
        key = (record.quote, record.author)
        unique.setdefault(key, record)
    return list(unique.values())


def write_csv(records: Iterable[Quote], path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["quote", "author", "tags", "source_url"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def write_json(records: Iterable[Quote], path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(record) for record in records]
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_summary(records: List[Quote], pages: int) -> dict:
    tag_counts = Counter()
    lengths = []
    authors = set()

    for record in records:
        authors.add(record.author)
        lengths.append(len(record.quote))
        if record.tags:
            tag_counts.update(record.tags.split("|"))

    return {
        "pages_requested": pages,
        "records_extracted": len(records),
        "unique_authors": len(authors),
        "average_quote_length": round(sum(lengths) / len(lengths), 2) if lengths else 0.0,
        "top_tags": dict(tag_counts.most_common(10)),
    }


def write_summary(summary: dict, path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "WEB SCRAPING ETL SUMMARY",
        "========================",
        f"Pages requested: {summary['pages_requested']}",
        f"Records extracted: {summary['records_extracted']}",
        f"Unique authors: {summary['unique_authors']}",
        f"Average quote length: {summary['average_quote_length']} characters",
        "",
        "Top tags:",
    ]
    if summary["top_tags"]:
        lines.extend(f"- {tag}: {count}" for tag, count in summary["top_tags"].items())
    else:
        lines.append("- None")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(
    *,
    start_url: str = DEFAULT_URL,
    pages: int = 5,
    delay: float = 0.5,
    output_dir: str = "output",
) -> dict:
    records = scrape(start_url, max_pages=pages, delay=delay)
    output = Path(output_dir)
    write_csv(records, str(output / "quotes.csv"))
    write_json(records, str(output / "quotes.json"))
    summary = build_summary(records, pages)
    write_summary(summary, str(output / "summary_report.txt"))
    return summary
