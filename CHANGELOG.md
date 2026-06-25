# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-06-25

Initial public MVP release.

### Added

- Local-first evidence tracking under `.traceframe/` for datasets, transformations, SQL, metrics, charts, claims, and checks
- Python API for pandas, DuckDB SQL, and Polars workflows
- Typer CLI (`init`, `status`, `doctor`, `lineage`, `report`, `verify`, and more)
- Static HTML audit reports with project health summary
- Upstream/downstream lineage graph inspection via API and CLI
- Source-row sampling, chart drilldown, and data quality expectations
- Local assistant planning with optional user-provided LLM command
- MIT License, CI workflow (Python 3.10 and 3.11), and example analyses
