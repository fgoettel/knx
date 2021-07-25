"""Code generator scripts."""
import logging
from pathlib import Path

FILEPATH = Path(__file__)
LOGGER = logging.getLogger(FILEPATH.stem)
DST_DIR = FILEPATH.parents[1]
