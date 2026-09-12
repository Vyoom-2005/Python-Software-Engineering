# Packaged CLI Diagnostics Tool

`dev-health` is an installable Python command-line tool that inspects a developer
machine and produces a deterministic health report.

## Features

- Python version and executable inspection
- Disk-space inspection
- Safe environment-variable inventory (names only; values are never printed)
- Developer-tool detection (`git`, `docker`, `node`, `npm`, `uv`, `poetry`, `pip`, `pytest`)
- Optional JSON configuration for required tools and paths
- Optional diagnostic-event summary
- Human-readable and structured JSON output
- Deterministic ordering and stable exit codes
- Unit tests for success, missing dependencies, and malformed configuration

## Requirements

Python 3.9+.

The runtime package has no third-party dependencies.

## Install

Create an isolated virtual environment and install the project:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install .
```

The console entry point is:

```bash
dev-health
```

## Usage

Basic human-readable report:

```bash
dev-health
```

Structured JSON:

```bash
dev-health --json
```

Use a configuration file:

```bash
dev-health --config config/example.json
```

Include the supplied diagnostic events:

```bash
dev-health --events diagnostic-events.json
```

Use both:

```bash
dev-health --config config/example.json --events diagnostic-events.json --json
```

## Configuration

Example:

```json
{
  "required_tools": ["python", "git"],
  "paths": [".", "README.md"]
}
```

- `required_tools` must be a JSON array of command names.
- `paths` must be a JSON array of existing files/directories.
- A missing required tool is reported as `FAIL`.
- A missing configured path is reported as `FAIL`.
- Invalid configuration is a configuration error.

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Diagnostics completed and all configured checks passed |
| 1 | Diagnostics completed, but one or more health checks failed |
| 2 | Invalid/malformed configuration or events input |
| 3 | Unexpected runtime error |

## Determinism

The report does not include the current time. Environment variables are sorted
and only their names are reported. Developer tools are checked in a fixed order.
Event records are processed in input order. This makes identical inputs produce
identical JSON output apart from machine-dependent inspection results.

## Test

```bash
python -m unittest discover -s tests -v
```

If `pytest` is installed, this also works:

```bash
python -m pytest
```

## Project layout

```text
packaged-cli-diagnostics/
├── pyproject.toml
├── README.md
├── config/
│   └── example.json
├── dev_health/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── checks.py
│   ├── config.py
│   ├── events.py
│   └── report.py
├── samples/
│   ├── sample-report.json
│   └── sample-report.txt
└── tests/
    ├── test_cli.py
    ├── test_config.py
    └── test_events.py
```
