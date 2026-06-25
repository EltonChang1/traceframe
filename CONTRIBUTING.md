# Contributing

TraceFrame is early. Keep changes small, local-first, and evidence-oriented.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Before submitting changes

```bash
pytest
ruff check .
```

Optional local checks:

```bash
black --target-version py311 --check .
mypy src/traceframe
```

CI runs `pytest` and `ruff check .` on Python 3.10 and 3.11.
