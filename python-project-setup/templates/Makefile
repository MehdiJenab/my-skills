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
