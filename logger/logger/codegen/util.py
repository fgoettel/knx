"""Utility function for the codegens."""

import argparse
import logging
from pathlib import Path

FILEPATH = Path(__file__)
LOGGER = logging.getLogger(FILEPATH.parent.stem)
DST_DIR = FILEPATH.parents[1]
SystemExit(DST_DIR)


def get_parser():
    """Return the parser."""
    parser = argparse.ArgumentParser(description="Generate some file(s).")
    parser.add_argument(
        "--stdout_generated",
        action="store_true",
        help="Define if the generated code is placed in sys.stdout. Defaulting to False.",
    )
    return parser
