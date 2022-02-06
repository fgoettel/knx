"""Check the style of the python and bazel files."""
import black

from logger.style.util import (  # pylint: disable=unused-import
    fixture_logger_directories,
)


def test_black(logger_directories):
    """Running black on all files yielded by the logger dir fixture."""
    everything_ok = True
    mode = black.FileMode()
    fast = False

    for dir_x in logger_directories:
        print(f"Running black on {dir_x}")
        for file_ in dir_x.glob("**/*.py"):

            print(f"\tRunning black on {file_.name}")
            with open(file_, "r", encoding="utf-8") as python_file:
                data = python_file.read()

            try:
                black.format_file_contents(data, fast=fast, mode=mode)
            except black.NothingChanged:
                pass
            else:
                print(f"Failed on {dir_x.stem}/{file_.stem}.")
                everything_ok = False

    assert everything_ok
