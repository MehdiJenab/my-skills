---
name: python-project-setup
description: >
  Step-by-step guide (9 steps) for bootstrapping a modern Python project with a complete
  strict toolchain. Ships with ready-to-copy template files.
  Trigger: user asks to start a new Python project, set up Python tooling from scratch,
  configure ruff/mypy/pytest/pre-commit/nox, enforce TDD, structure a Python codebase, or
  set up Claude Code for a Python project. Also trigger when an existing Python project is
  missing tooling (no pyproject.toml, no pre-commit, no coverage config).
  Action: walks through 9 numbered steps — skip to the relevant step if only part is needed:
  (1) git init + .gitignore, (2) venv, (3) src-layout scaffold, (4) pyproject.toml with
  ruff+mypy+pytest+coverage, (5) editable install, (6) pre-commit hooks (remote or local
  options), (7) Makefile + noxfile.py for multi-version testing, (8) commit skeleton,
  (9) per-project .claude/. Template files in templates/ are ready to copy.
  Limitations: assumes Python ≥ 3.11; does not cover Django/Flask/FastAPI project structure,
  data science notebook setups, or PyPI packaging; coverage fail_under=100 may need lowering
  for legacy codebases.
  Relationships: for C++ projects use cpp-project-setup; for projects using AI agents pair
  with spec-driven-development first to write the constitution before scaffolding.
  Examples: "start a new Python project" → full 9-step walkthrough from scratch;
  "set up ruff and mypy for my project" → jumps to Step 4 (pyproject.toml);
  "add pre-commit hooks to my existing Python project" → jumps to Step 6;
  "how do I enforce 100% test coverage in Python" → Step 4 coverage config + Step 7 make coverage.
---

# Python Project Setup — Modern Toolchain & TDD

This skill walks through every step of starting a Python project correctly, in order. No steps are skipped. The result is a project where bad code physically cannot be committed.

---

## Step 1 — Create the project folder and init git

```bash
mkdir my_project && cd my_project
git init
```

Create a `.gitignore` immediately — before any files exist — so nothing leaks into git by accident:

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
dist/
build/

# Virtual environment
.venv/
venv/
env/

# Tool caches
.mypy_cache/
.ruff_cache/
.pytest_cache/
.coverage
htmlcov/

# Editor
.vscode/
.idea/

# Environment
.env
```

```bash
git add .gitignore
git commit -m "init: add .gitignore"
```

---

## Step 2 — Create the virtual environment

Always use a local `.venv` inside the project root — not a global or user-level environment.

```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
```

Verify:

```bash
which python   # should point to .venv/bin/python
python --version
```

The `.venv/` directory is already in `.gitignore`. Never commit it.

---

## Step 3 — Establish the folder structure

Use **src-layout**. This is the modern Python standard. It prevents the package from being accidentally importable without installation, which catches missing `__init__.py` and broken installs early.

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py       # version = "0.1.0"
│       └── py.typed          # declares the package ships type information
├── tests/
│   └── conftest.py           # shared fixtures
├── scripts/                  # runnable entry points (not part of the package)
├── pyproject.toml            # single config file for everything
├── .pre-commit-config.yaml
├── Makefile
└── .gitignore
```

Create the scaffold:

```bash
mkdir -p src/my_package tests scripts

# Package marker files
echo '__version__ = "0.1.0"' > src/my_package/__init__.py
touch src/my_package/py.typed

# Test bootstrap
cat > tests/conftest.py << 'EOF'
# Shared pytest fixtures go here
EOF
```

**Why src-layout?**
- `import my_package` only works after `pip install -e .` — no accidental naked imports
- Keeps installable code clearly separated from tests, scripts, and config
- Required by modern build backends (setuptools, hatch)

---

## Step 4 — Write pyproject.toml

One file replaces: `setup.py`, `setup.cfg`, `requirements.txt`, `pytest.ini`, `mypy.ini`, `.flake8`, `.isort.cfg`.

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "Short description"
authors = [{ name = "Your Name", email = "you@example.com" }]
requires-python = ">=3.11"
dependencies = [
    # add runtime deps here, e.g. "scipy>=1.10", "pydantic>=2.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.4",
    "pre-commit>=3.0",
    "nox>=2024.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

# ── Ruff ──────────────────────────────────────────────────────────────────────
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
]

# ── Mypy ──────────────────────────────────────────────────────────────────────
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true

# ── Pytest ────────────────────────────────────────────────────────────────────
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-m 'not slow'"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]

# ── Coverage ──────────────────────────────────────────────────────────────────
[tool.coverage.run]
source = ["my_package"]

[tool.coverage.report]
fail_under = 100
show_missing = true
```

**Key decisions:**
- `fail_under = 100` — coverage is not aspirational; it is enforced by the tool
- `addopts = "-m 'not slow'"` — slow tests are excluded from the default run; fast feedback loop
- `disallow_untyped_defs = true` — every function must have type annotations; no exceptions
- `warn_return_any` — prevents `Any` from silently propagating through the codebase

---

## Step 5 — Install the project in editable mode

All dev tools — `ruff`, `mypy`, `pytest`, `pytest-cov`, `pre-commit`, `nox` — live inside the `.venv`. There is no global installation needed. One command installs everything:

```bash
pip install -e ".[dev]"
```

This installs the package (editable, so code changes take effect immediately) plus every dev tool. Verify:

```bash
python -c "import my_package; print(my_package.__version__)"
pytest --version
mypy --version
ruff --version
nox --version
pre-commit --version
```

All binaries resolve to `.venv/bin/`. When the venv is active, there is nothing else to install.

---

## Step 6 — Configure pre-commit hooks

Pre-commit runs ruff and mypy automatically before every `git commit`. This means bad code is blocked at the source — not discovered in CI hours later.

There are two ways to configure the hooks. Pick one per project.

### Option A — Remote repos (default, recommended for shared projects)

Pre-commit downloads and manages its own isolated environments for each hook. Versions are pinned independently of your venv. Consistent across all machines.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        args: [--config-file=pyproject.toml]
        files: ^src/
        additional_dependencies: []   # add stubs here, e.g. "numpy", "scipy"
```

### Option B — Local venv (`language: system`, recommended for single-developer projects)

Hooks use the exact ruff and mypy from your `.venv` — the same versions as `make check`. No separate pre-commit environments. Single source of truth for tool versions.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        language: system
        entry: ruff check --fix
        types: [python]

      - id: ruff-format
        name: ruff format
        language: system
        entry: ruff format
        types: [python]

      - id: mypy
        name: mypy
        language: system
        entry: mypy src/
        pass_filenames: false
```

**Tradeoff summary:**

| | Option A (remote) | Option B (system) |
|---|---|---|
| Tool versions | Pre-commit manages its own | Your `.venv` versions |
| Setup | Works on any machine without venv active | Requires `.venv` active |
| Consistency with `make check` | May differ | Always identical |
| Best for | Team projects, CI | Solo projects, tight control |

Install the hooks (same command for both options):

```bash
pre-commit install
```

From now on, every `git commit` automatically runs ruff and mypy. A failing hook blocks the commit.

---

## Step 7 — Add a Makefile and noxfile.py

### Makefile

`make check` is the single command to run the entire quality suite against the active venv. `make nox` runs it across all Python versions.

```makefile
.PHONY: help install lint format typecheck test coverage check nox nox-tests clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package + dev deps + pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run ruff linter (auto-fix)
	ruff check --fix src/ tests/

format: ## Run ruff formatter
	ruff format src/ tests/

typecheck: ## Run mypy type checker
	mypy src/

test: ## Run tests (excluding slow)
	pytest

coverage: ## Run tests with coverage report
	pytest --cov --cov-report=term-missing

check: lint format typecheck coverage ## Run full quality suite (current venv)

nox: ## Run full suite across all Python versions
	nox

nox-tests: ## Run tests only across all Python versions
	nox -s tests

clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .ruff_cache .pytest_cache htmlcov .coverage dist build
	find . -type d -name __pycache__ -exec rm -rf {} +
```

### noxfile.py — multi-version testing

`nox` uses your installed Python versions (via pyenv) to create isolated venvs and run the test suite against each. The `nox` binary itself lives in `.venv` and is available when the venv is active.

```python
# noxfile.py
import nox

# Python versions to test against.
# Each version must be available on PATH (e.g. via pyenv shims):
#   pyenv install 3.11
#   pyenv install 3.12
#   pyenv install 3.13
#   pyenv global system 3.11 3.12 3.13
PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.install("-e", ".[dev]")
    session.run("pytest", "--cov", "--cov-report=term-missing")


@nox.session(python=PYTHON_VERSIONS)
def typecheck(session: nox.Session) -> None:
    """Run mypy type checker."""
    session.install("-e", ".[dev]")
    session.run("mypy", "src/")


@nox.session(python="3.12")   # lint only needs to run once
def lint(session: nox.Session) -> None:
    """Run ruff linter and formatter check."""
    session.install("ruff")
    session.run("ruff", "check", "src/", "tests/")
    session.run("ruff", "format", "--check", "src/", "tests/")
```

**Usage:**

```bash
nox                     # all sessions, all Python versions
nox -s tests            # tests only, all versions
nox -s tests-3.12       # tests only, Python 3.12
nox -l                  # list all sessions
```

**Getting the Python interpreters via pyenv:**

```bash
# Install versions
pyenv install 3.11
pyenv install 3.12
pyenv install 3.13

# Expose all versions simultaneously via shims
pyenv global system 3.11 3.12 3.13
```

Verify:

```bash
python3.11 --version
python3.12 --version
python3.13 --version
```

Ensure pyenv shims are active in your shell — add to `~/.bashrc` if not already present:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

With shims active, `noxfile.py` uses short names and is fully portable across machines:

```python
PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]
```

The `.venv` only needs the Python version you develop against day-to-day (3.12). Nox creates separate short-lived envs for each version during its run.

---

## Step 8 — Commit the project skeleton

```bash
git add pyproject.toml .pre-commit-config.yaml Makefile src/ tests/
git commit -m "init: project scaffold with toolchain"
```

At this point pre-commit runs for the first time — it will auto-format and lint the files you just staged.

---

## TDD Workflow — The Daily Loop

TDD has one rule: **tests are the specification. Code is the implementation.** The test is written first, against an interface that does not exist yet.

### The cycle

```
1. Write a failing test
2. Run pytest → see RED (test fails, usually ImportError or AssertionError)
3. Write the minimum code to make the test pass
4. Run pytest → see GREEN
5. Refactor if needed → pytest still GREEN
6. make check → full suite passes
7. git commit
```

### Enforce the cycle with coverage

With `fail_under = 100`, pytest fails if any line in `src/` is not executed by a test. This makes it impossible to ship untested code — the CI pipeline rejects it and `make check` fails locally.

```bash
pytest --cov --cov-report=term-missing
# FAIL Required test coverage of 100% not reached. Total coverage: 87.00%
```

### Slow tests

Mark any test that takes more than ~1 second as slow:

```python
import pytest

@pytest.mark.slow
def test_convergence_full_run():
    ...
```

Default `pytest` run skips them (`addopts = "-m 'not slow'"`). Run them explicitly when needed:

```bash
pytest -m slow
pytest -m "slow or not slow"   # everything
```

This keeps the inner TDD loop fast (sub-second feedback) while still covering the full suite in CI.

### Test file naming and layout

```
tests/
├── conftest.py              # shared fixtures
├── test_my_module.py        # one file per source module
└── test_another_module.py
```

- One test file per source module — easy to find tests for any given file
- Fixtures in `conftest.py` — shared across all test files automatically
- Test function names describe the behavior being tested: `test_returns_zero_for_empty_input`, not `test_func1`

### Type annotations are non-negotiable

With `disallow_untyped_defs = true`, this is rejected by mypy:

```python
def add(a, b):          # ❌ mypy error
    return a + b
```

This is required:

```python
def add(a: int, b: int) -> int:   # ✅
    return a + b
```

Type annotations serve as executable documentation. They catch a whole class of bugs before tests even run.

---

## Full bootstrap command sequence

```bash
# 1. Create project
mkdir my_project && cd my_project
git init

# 2. Gitignore
# (create .gitignore as shown above)
git add .gitignore && git commit -m "init: add .gitignore"

# 3. Virtual environment
python3.12 -m venv .venv && source .venv/bin/activate

# 4. Scaffold
mkdir -p src/my_package tests scripts
echo '__version__ = "0.1.0"' > src/my_package/__init__.py
touch src/my_package/py.typed
touch tests/conftest.py

# 5. Config files
# (create pyproject.toml, .pre-commit-config.yaml, Makefile as shown above)

# 6. Install
make install

# 7. Commit skeleton
git add pyproject.toml .pre-commit-config.yaml Makefile src/ tests/
git commit -m "init: project scaffold with toolchain"

# 8. Start TDD
# Write tests/test_my_module.py first, then src/my_package/my_module.py
```

---


## Step 9 — Create per-project .claude/

Every project gets its own `.claude/` directory. This gives Claude Code project-specific context, permissions, agents, and MCP servers — independent of the user's global `~/.claude/` settings.

```
my_project/
└── .claude/
    ├── CLAUDE.md              # Project-specific instructions for Claude
    ├── settings.local.json    # Project permissions + MCP servers (gitignored)
    └── agents/                # Custom sub-agent definitions for this project
        └── codebase-reviewer.md
```

### `.claude/CLAUDE.md` — Instructions for Claude

This is the first file Claude reads when opening this project. Write it for Claude, not for humans. Keep it short and authoritative.

```markdown
# Project: my_package

## Environment
- Python 3.12 via `.venv/` — always activate before running commands
- Install: `pip install -e ".[dev]"` then `pre-commit install`

## Toolchain
- Lint + format: `ruff check --fix` and `ruff format`
- Type check: `mypy src/`
- Tests: `pytest` (slow tests excluded by default)
- Full suite: `make check`

## Rules
- Tests are the specification. Never modify a test to make it pass.
- Coverage is enforced at 100%. Every new code path needs a test.
- All functions must be type-annotated. No `# type: ignore` without explanation.
- Pre-commit hooks must pass. Never use `--no-verify`.

## Before making changes
1. Run `make check` — it must pass before you start
2. Read the relevant module(s) under `src/` to understand the contract you're modifying
```

### `.claude/settings.local.json` — Permissions and MCP servers

Pre-approve the commands Claude will need during development so it does not prompt on every run:

```json
{
  "permissions": {
    "allow": [
      "Bash(make check)",
      "Bash(make test)",
      "Bash(make coverage)",
      "Bash(make lint)",
      "Bash(make typecheck)",
      "Bash(pytest*)",
      "Bash(ruff*)",
      "Bash(mypy src/*)",
      "Bash(pip install*)",
      "Bash(pre-commit run*)"
    ]
  },
  "mcpServers": {
    "project-db": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", ".data/project.db"]
    }
  }
}
```

`settings.local.json` contains machine-specific paths and secrets — **add it to `.gitignore`**. Commit a `settings.json` with the non-secret structure if you want shared project defaults.

### `.claude/agents/` — Custom sub-agents

Define project-specific sub-agents that Claude can spawn for specialized tasks:

```markdown
---
name: codebase-reviewer
description: "Reviews Python code changes against project constraints. Use when reviewing a PR or before merging a feature branch."
---

# Codebase Reviewer

When reviewing code in this project:

1. Check all new functions have type annotations
2. Verify every new code path has a corresponding test
3. Check coverage is still 100% (`make coverage`)
4. Verify ruff and mypy pass (`make lint && make typecheck`)

Report: list of violations (if any), or "LGTM" with a one-line summary.
```

Add CLAUDE.md and agents to git; keep settings.local.json out:

```bash
echo ".claude/settings.local.json" >> .gitignore
git add .claude/CLAUDE.md .claude/agents/
git commit -m "chore: add per-project Claude configuration"
```

---

## Final folder structure

```
my_project/
├── .claude/
│   ├── CLAUDE.md                  # Instructions for Claude Code
│   ├── settings.local.json        # Permissions + MCPs (gitignored)
│   └── agents/
│       └── codebase-reviewer.md   # Custom sub-agent
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── py.typed
├── tests/
│   └── conftest.py
├── scripts/
├── pyproject.toml
├── .pre-commit-config.yaml
├── noxfile.py
├── Makefile
└── .gitignore
```

---

## Tool summary

| Tool | Role | Configured in |
|------|------|---------------|
| `venv` | Isolated Python environment | (manual, `.venv/`) |
| `pip` + `setuptools` | Package install and build | `pyproject.toml` |
| `ruff` | Lint + format (replaces flake8, black, isort) | `[tool.ruff]` in `pyproject.toml` |
| `mypy` | Static type checking | `[tool.mypy]` in `pyproject.toml` |
| `pytest` | Test runner | `[tool.pytest.ini_options]` in `pyproject.toml` |
| `pytest-cov` | Coverage enforcement (`fail_under = 100`) | `[tool.coverage]` in `pyproject.toml` |
| `pre-commit` | Blocks commits that fail lint/typecheck | `.pre-commit-config.yaml` |
| `nox` | Runs full suite across multiple Python versions | `noxfile.py` |
| `pyenv` | Provides Python 3.11, 3.12, 3.13 interpreters for nox | `pyenv install <version>` |
| `Makefile` | Single entry point for all quality commands | `Makefile` |
| `.claude/` | Per-project Claude instructions, permissions, agents, MCPs | `.claude/CLAUDE.md`, `settings.local.json`, `agents/` |
