# Architecture and Operational Design

## Layers

### 1. CLI
`enterprise_report/cli.py` handles user input, exit codes, and scheduling.

### 2. Ingestion
`data.py` reads JSON/CSV and enforces the record contract.
`api.py` integrates with HTTP JSON backends.

### 3. Processing
`processing.py` computes deterministic aggregate statistics using `Decimal`
for financial values.

### 4. Output
`pdf.py` produces a self-contained PDF and writes it atomically.
A JSON summary can also be generated for downstream automation.

### 5. Scheduler
`scheduler.py` repeatedly invokes the same job function, keeping scheduling
separate from business logic and making it straightforward to test.

## Reliability

- Strict input validation
- Unique record IDs
- Decimal arithmetic for money
- Network timeout
- HTTP error translation
- Atomic report replacement
- Stable sorting for aggregate output
- Explicit exit codes
- Unit tests without network dependency

## Deployment

For enterprise deployment, the CLI can be launched from cron, Windows Task
Scheduler, a container, or a process supervisor. The built-in scheduler is
useful for a self-contained demonstration and controlled environments.
