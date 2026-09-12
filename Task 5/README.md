# Enterprise Python Automation Capstone Project

## Automated PDF Report Generator

This repository implements an end-to-end production-style Python automation
application. It reads structured JSON/CSV data, validates and transforms it,
calculates summary statistics, optionally retrieves data from a backend HTTP
API, generates a professional PDF report, and can execute the workflow on a
repeat schedule.

### Why this project fits the capstone

The implementation demonstrates all requested areas:

- **End-to-end logic:** ingestion → validation → processing → reporting.
- **Backend API integration:** optional HTTP/JSON ingestion using the standard
  library `urllib`.
- **Data processing:** totals, averages, min/max, status counts, and category
  summaries.
- **Automated scheduling:** interval scheduler implemented without a daemon
  dependency.
- **Packaging:** `pyproject.toml` and `reportgen` CLI entry point.
- **Documentation:** architecture, installation, examples, execution logs,
  and troubleshooting are included.
- **Reliable execution:** deterministic output, validation, atomic writes,
  meaningful exit codes, and unit tests.

## Architecture

```text
                 +----------------------+
                 | JSON / CSV / HTTP API|
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   Input Validation   |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Data Processing      |
                 | totals / averages    |
                 | status / categories  |
                 +----------+-----------+
                            |
                  +---------+---------+
                  |                   |
                  v                   v
          +---------------+    +---------------+
          | JSON summary  |    | PDF generator |
          +---------------+    +-------+-------+
                                      |
                                      v
                              +---------------+
                              | Report output |
                              +---------------+

        Optional scheduler
              |
              +----> runs the same pipeline at fixed intervals
```

## Data contract

Each record contains:

```json
{
  "id": "ORD-001",
  "customer": "Example Customer",
  "category": "Software",
  "amount": 1250.50,
  "status": "completed"
}
```

Required fields are `id`, `customer`, `category`, `amount`, and `status`.
Amounts must be numeric and non-negative.

## Installation

Python 3.9+ is required.

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it and install the project:

```bash
python -m pip install -e .
```

No runtime third-party dependency is required.

## CLI usage

Generate a report from JSON:

```bash
reportgen --input examples/sales.json --format json --output output/report.pdf
```

Generate from CSV:

```bash
reportgen --input examples/sales.csv --format csv --output output/report.pdf
```

Also save a machine-readable summary:

```bash
reportgen --input examples/sales.json --output output/report.pdf --summary output/summary.json
```

Use a remote JSON endpoint:

```bash
reportgen --url https://example.com/api/sales.json --output output/report.pdf
```

Run continuously every 60 minutes:

```bash
reportgen --input examples/sales.json --output output/report.pdf --schedule-minutes 60
```

For testing scheduling without waiting a long time:

```bash
reportgen --input examples/sales.json --output output/report.pdf --schedule-minutes 1 --runs 2
```

The default is a single execution. Scheduled mode is stopped with `Ctrl+C`.

## Generated report

The PDF contains:

1. Report title and generation metadata
2. Record count
3. Total amount
4. Average amount
5. Minimum and maximum amounts
6. Status distribution
7. Category totals
8. A detailed record table

The PDF writer is implemented in the repository itself, so the application
does not depend on external PDF libraries.

## HTTP API integration

The `--url` option expects a JSON endpoint returning either:

```json
[
  {"id": "...", "customer": "...", "category": "...", "amount": 100, "status": "completed"}
]
```

or:

```json
{"records": [ ... ]}
```

The HTTP client applies a timeout and sends a descriptive User-Agent. HTTP
errors, invalid JSON, and invalid payloads are converted into clear
application errors.

## Testing

Run:

```bash
python -m unittest discover -s tests -v
```

The test suite covers:

- JSON and CSV ingestion
- schema validation
- data aggregation
- deterministic summary generation
- PDF generation
- HTTP API parsing with a mocked network layer
- invalid input handling
- CLI execution
- scheduling iteration logic

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Successful execution |
| 1 | Expected application/input error |
| 2 | Invalid CLI arguments |
| 3 | Unexpected application failure |

## Production considerations

For deployment, configure output directories with appropriate permissions,
run the scheduler under a process supervisor, rotate reports, and add an
external logging/monitoring system. For sensitive data, encrypt storage and
avoid putting credentials in command-line arguments.

## Repository proof

- `execution_log.txt` records a verified local run.
- `output/` contains sample generated artifacts.
- `tests/` contains automated tests.
- `docs/ARCHITECTURE.md` provides the architecture and operational notes.
