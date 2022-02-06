"""Utility functions for the tests."""


from pathlib import Path

import pytest


@pytest.fixture(name="logger_directories")
def fixture_logger_directories():
    """Get all directories inside logger."""

    def skip(path_x):
        """Skip everything that's not a legit dir."""
        # Non directorires
        if not path_x.is_dir():
            return True

        # External packages
        if "external" in str(path_x):
            return True

        # Cached files
        if path_x.stem == "__pycache__":
            return True

        return False

    logger_dir = Path(Path(__file__).parents[2])
    logger_dirs = [x for x in logger_dir.glob("**/*") if not skip(x)]

    return logger_dirs
