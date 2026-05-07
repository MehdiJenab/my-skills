# Project: {{project_name}}

## Environment
- Python 3.12 via `.venv/` — always activate before running commands
- Bootstrap: `pip install -e ".[dev]"` then `pre-commit install`

## Toolchain
- Lint + format: `make lint && make format`
- Type check: `make typecheck`
- Tests: `make test` (slow tests excluded by default)
- Full suite: `make check`
- Multi-version: `make nox`

## Rules
- Tests are the specification. Never modify a test to make it pass.
- Coverage is enforced at 100%. Every new code path needs a test.
- All functions must be type-annotated. No `# type: ignore` without explanation.
- Pre-commit hooks must pass. Never use `--no-verify`.
- Write the test first, then the implementation.

## Before making changes
1. Run `make check` — it must pass before you start
2. Read the relevant module(s) under `src/` to understand the contract you're modifying
