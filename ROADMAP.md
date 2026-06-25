# Roadmap

## v0.1

- Python package
- Typer CLI
- Local `.traceframe/` project folder
- CSV/Parquet tracking
- Basic profiling
- DuckDB SQL execution
- Metric, chart, and claim registries
- Static HTML report
- Artifact verification

## v0.2

- Lightweight run metadata
- Best-effort notebook context detection
- Manual notebook cell notes
- Manual stale dataset warnings
- Richer static audit report

## v0.3

- Source-row sampling
- Source-row export
- Explicit filter tracking
- DuckDB-backed chart drilldown

## v0.4

- Native Polars DataFrame tracking
- LazyFrame schema profiling
- `scan_csv` and `scan_parquet` for streaming-friendly local reads
- DuckDB SQL support for tracked Polars objects

## v0.5

- Null checks
- Duplicate checks
- Type/schema checks
- Unique-key checks
- Threshold checks
- Lightweight expectation records

## v0.6

- Local heuristic analysis planning
- Optional user-provided local LLM command integration
- Assistant plan evidence records
- No external API calls by default

## v1.0

- Stable local Python API
- Stronger report health summary
- `traceframe doctor` project diagnostics
- Pandas + DuckDB + Polars end-to-end workflow tests
- Expanded examples and documentation

## v2

- Query upstream/downstream lineage by artifact name or ID
- `traceframe lineage ARTIFACT` CLI inspection
- Report lineage edges include readable artifact names alongside stable IDs

## Later

- Stable API hardening
