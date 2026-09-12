from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from typing import Any

from .data import Record


def summarize(records: list[Record]) -> dict[str, Any]:
    amounts = [record.amount for record in records]
    status_counts = Counter(record.status for record in records)
    category_totals: dict[str, Decimal] = defaultdict(Decimal)

    for record in records:
        category_totals[record.category] += record.amount

    total = sum(amounts, Decimal("0"))
    average = total / len(amounts) if amounts else Decimal("0")

    return {
        "record_count": len(records),
        "total_amount": total,
        "average_amount": average,
        "minimum_amount": min(amounts) if amounts else Decimal("0"),
        "maximum_amount": max(amounts) if amounts else Decimal("0"),
        "status_counts": dict(sorted(status_counts.items())),
        "category_totals": dict(sorted(category_totals.items())),
    }


def json_safe_summary(summary: dict[str, Any]) -> dict[str, Any]:
    result = dict(summary)
    for key in ("total_amount", "average_amount", "minimum_amount", "maximum_amount"):
        result[key] = f"{result[key]:.2f}"
    result["category_totals"] = {
        key: f"{value:.2f}" for key, value in result["category_totals"].items()
    }
    return result
