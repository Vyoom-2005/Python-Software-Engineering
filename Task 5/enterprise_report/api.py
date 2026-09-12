from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .data import Record, parse_records
from .exceptions import ApiError


def fetch_json_records(url: str, timeout: float = 10.0) -> list[Record]:
    request = Request(
        url,
        headers={"User-Agent": "EnterpriseReportGenerator/1.0"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
        payload = json.loads(raw)
        return parse_records(payload)
    except HTTPError as exc:
        raise ApiError(f"HTTP {exc.code} while fetching API") from exc
    except URLError as exc:
        raise ApiError(f"API connection failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ApiError("API request timed out") from exc
    except json.JSONDecodeError as exc:
        raise ApiError("API returned invalid JSON") from exc
    except Exception as exc:
        if isinstance(exc, ApiError):
            raise
        raise ApiError(f"invalid API response: {exc}") from exc
