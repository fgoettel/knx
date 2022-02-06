"""Check the style of the python and bazel files."""
import isort

from logger.style.util import (  # pylint: disable=unused-import
    fixture_logger_directories,
)


def test_isort(logger_directories):
    """Run isort on all files."""
    everything_ok = True
    for dir_x in logger_directories:
        print(f"Running isort on {dir_x}")
        for file_ in dir_x.glob("**/*.py"):
            if not isort.check_file(file_, profile="black"):
                print(f"Failed on {dir_x.stem}/{file_.stem}.")
                everything_ok = False

    assert everything_ok
