"""Entrypoint for tests and linting."""

from pathlib import Path

import nox
from nox_poetry import session

locations = ("examples", "logger", "test", "./noxfile.py")
python_default = "3.12"
python_versions = (python_default,)
nox.options.sessions = "lint", "tests", "mypy"


def open_in_browser(path: str) -> None:
    """Open a given path in the default browser."""
    import webbrowser
    from urllib.request import pathname2url

    pathname = str(Path(path).resolve())
    webbrowser.open("file://" + pathname2url(pathname))


@session(python=python_versions)
def tests(session: session) -> None:
    """Run pytest."""
    session.install("pytest", "sqlalchemy", "xknx", "pytest-asyncio")
    session.run("pytest")


@session(python=python_versions)
def coverage(session: session) -> None:
    """Run pytest with coverage."""
    report_dir = f"htmlcov_{session.python}"
    session.install("pytest", "sqlalchemy", "xknx", "pytest-asyncio", "pytest-cov")
    session.run("pytest", "--cov=.", f"--cov-report=html:{report_dir}", "test")
    open_in_browser(f"{report_dir}/index.html")


@session(python=python_versions)
def lint(session: session) -> None:
    """Lint it, but don't change it."""
    session.install(
        "pytest",
        "sqlalchemy",
        "xknx",
        "ruff",
    )
    session.run("ruff", "format", *session.posargs)
    session.run("ruff", "check", *session.posargs)


@session(python=python_default)
def mypy(session: session) -> None:
    """Types, types, types."""
    session.install("mypy", "xknx", "pytest", "sqlalchemy-stubs")
    session.run("mypy", ".", *session.posargs)
