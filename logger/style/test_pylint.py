"""Run pylint on all logger directories."""


from pathlib import Path

import pylint.lint

from logger.style.util import (  # pylint: disable=unused-import
    fixture_logger_directories,
)


def test_pylint(logger_directories):
    """Run pylint on all files yielded by logger_directories"""
    error_count = 0
    rc_file = Path(__file__).parent / "pylintrc"
    assert rc_file.exists() and rc_file.is_file()

    for dir_x in logger_directories:
        pylint_opts = [str(dir_x), "--rcfile", str(rc_file)]
        print(f"Running pylint on {dir_x.name}")
        # print(f"Running pylint with {pylint_opts}")
        try:
            res = pylint.lint.Run(pylint_opts)
            print(res)
        except SystemExit as err:
            if err.code != 0:
                print(f"Error on {dir_x}: {err}")
                error_count += 1

    assert error_count == 0
