"""Entrypoint for tests and linting."""

from pathlib import Path

import nox
from nox_poetry import session

locations = ("examples", "projects", "test", "./noxfile.py")
python_default = "3.12"
python_versions = (python_default,)
nox.options.sessions = "lint", "tests", "mypy"


def open_in_browser(path: str) -> None:
    """Open a given path in the default browser."""
    import webbrowser
    from urllib.request import pathname2url

    resolved_path = str(Path(path).resolve())
    webbrowser.open("file://" + pathname2url(resolved_path))


@session(python=python_versions)
def tests(session: session) -> None:
    """Run pytest."""
    session.install("defusedxml", "pytest", "pytest-asyncio")
    session.run("pytest")


@session(python=python_versions)
def coverage(session: session) -> None:
    """Run pytest with coverage."""
    report_dir = f"htmlcov_{session.python}"
    session.install("defusedxml", "pytest", "pytest-asyncio", "pytest-cov")
    session.run("pytest", "--cov=.", f"--cov-report=html:{report_dir}", "test")
    open_in_browser(f"{report_dir}/index.html")


@session(python=python_versions)
def lint(session: session) -> None:
    """Lint it, and format it."""
    session.install(
        "defusedxml",
        "pylint",
        "pytest",
        "ruff",
    )
    session.run("pylint", "projects")
    session.run("pylint", "test", "--disable=unused-import")
    session.run("pylint", "examples", "--disable=duplicate-code")
    session.run("ruff", "format")
    session.run("ruff", "check", "--fix")


@session(python=python_versions)
def mypy(session: session) -> None:
    """Types, types, types."""
    session.install(
        "defusedxml",
        "mypy",
        "nox",
        "pytest",
    )
    session.run("mypy", *locations)
