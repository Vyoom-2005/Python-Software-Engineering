from __future__ import annotations

import time
from typing import Callable


def run_scheduled(
    job: Callable[[], object],
    interval_minutes: float,
    runs: int | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> int:
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be greater than zero")
    completed = 0
    while runs is None or completed < runs:
        job()
        completed += 1
        if runs is not None and completed >= runs:
            break
        sleep_fn(interval_minutes * 60)
    return completed
