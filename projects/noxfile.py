"""Entrypoint for tests and linting."""

import tempfile

import nox  # type: ignore
from nox_poetry import session  # type: ignore

locations = ("examples", "projects", "test", "./noxfile.py")
python_default = "3.10"
python_versions = (python_default, "3.9")
nox.options.sessions = "lint", "tests", "mypy", "safety"


def open_in_browser(path: str) -> None:
    """Open a given path in the default browser."""
    import os
    import webbrowser
    from urllib.request import pathname2url

    webbrowser.open("file://" + pathname2url(os.path.abspath(path)))


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
    """Lint it, but don't change it."""
    test_ignores = (
        "ANN001",  # Missing arg type
        "ANN201",  # Missing return type
        "DAR101",  # Missing Parameters
        "F811",  # Redefines (needed for fixtures)
        "S101",  # Assert statements
        "DAR201",  # Return in docstring
        "S311",  # Pseudo-random generators unsafe
    )
    per_file_ignores = (
        f"test/*:{','.join(test_ignores)}",
        "noxfile.py:DAR101",
    )
    args_common = (
        "--max-line-length=200",
        "--ignore=E203,W503,ANN101,ANN002,ANN003",
        f"--per-file-ignores={' '.join(per_file_ignores)}",
    )
    args_opt = session.posargs or locations
    args = args_opt + args_common
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-isort",
        "flake8-docstrings",
        "pylint",
        "pytest",
        "darglint",
        "toml",
    )
    session.run("flake8", *args)
    session.run("pylint", "test", "projects")
    session.run("pylint", "examples", "--disable=duplicate-code")


@session(python=python_default)
def mypy(session: session) -> None:
    """Types, types, types."""
    session.install("mypy", "pytest", "defusedxml")
    session.run("mypy", *locations)


@session(python=python_default)
def black(session: session) -> None:
    """Run black."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@session(python=python_default)
def isort(session: session) -> None:
    """Run isort."""
    args = session.posargs or locations
    session.install("isort")
    session.run("isort", *args)


@session(python=python_versions)
def safety(session: session) -> None:
    """Check for security issues."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
