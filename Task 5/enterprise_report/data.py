from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

from .exceptions import InputDataError

REQUIRED_FIELDS = ("id", "customer", "category", "amount", "status")


@dataclass(frozen=True)
class Record:
    id: str
    customer: str
    category: str
    amount: Decimal
    status: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["amount"] = str(self.amount)
        return data


def _record(raw: dict[str, Any], index: int) -> Record:
    if not isinstance(raw, dict):
        raise InputDataError(f"record {index} must be an object")
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise InputDataError(f"record {index} missing fields: {', '.join(missing)}")

    values = {}
    for field in ("id", "customer", "category", "status"):
        value = raw[field]
        if not isinstance(value, str) or not value.strip():
            raise InputDataError(f"record {index}: {field} must be non-empty")
        values[field] = value.strip()

    try:
        amount = Decimal(str(raw["amount"]))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise InputDataError(f"record {index}: amount must be numeric") from exc
    if not amount.is_finite() or amount < 0:
        raise InputDataError(f"record {index}: amount must be finite and non-negative")

    return Record(amount=amount, **values)


def parse_records(payload: Any) -> list[Record]:
    if isinstance(payload, dict) and "records" in payload:
        payload = payload["records"]
    if not isinstance(payload, list):
        raise InputDataError("input must be a JSON array or an object containing 'records'")
    records = [_record(item, index + 1) for index, item in enumerate(payload)]
    ids = [record.id for record in records]
    if len(ids) != len(set(ids)):
        raise InputDataError("record IDs must be unique")
    return records


def load_json(path: str) -> list[Record]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputDataError(f"JSON file not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise InputDataError(f"cannot read JSON: {exc}") from exc
    return parse_records(payload)


def load_csv(path: str) -> list[Record]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or any(field not in reader.fieldnames for field in REQUIRED_FIELDS):
                raise InputDataError("CSV must contain id, customer, category, amount, status columns")
            return parse_records(list(reader))
    except FileNotFoundError as exc:
        raise InputDataError(f"CSV file not found: {path}") from exc
    except OSError as exc:
        raise InputDataError(f"cannot read CSV: {exc}") from exc


def load_file(path: str, fmt: str | None = None) -> list[Record]:
    extension = Path(path).suffix.lower()
    selected = (fmt or extension.lstrip(".")).lower()
    if selected == "json":
        return load_json(path)
    if selected == "csv":
        return load_csv(path)
    raise InputDataError("input format must be json or csv")


def serialize_records(records: Iterable[Record]) -> list[dict[str, Any]]:
    return [record.to_dict() for record in records]
