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


@nox.session(python="3.12")  # lint only needs to run once
def lint(session: nox.Session) -> None:
    """Run ruff linter and formatter check."""
    session.install("ruff")
    session.run("ruff", "check", "src/", "tests/")
    session.run("ruff", "format", "--check", "src/", "tests/")
