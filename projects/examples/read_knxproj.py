#!/usr/bin/env python3
"""Read a projects and display all group addresses and devices."""

import argparse
import logging
from pathlib import Path

from projects.knxproj import Knxproj


def obtain_knxproj() -> Knxproj:
    """Obtain a Knxproj object.

    Returns:
        Knxproj: The read knxproj object.
    """
    description = "Read a knxproj export from the ETS and fiddle around with it."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--knxproj", required=True, type=str, help="Path to the ETS .knxproj export."
    )
    args = parser.parse_args()
    knxproj_path = Path(args.knxproj)

    return Knxproj(knxproj_path=knxproj_path)


def main() -> None:
    """Log all provided group addresses and devices."""
    knxproj = obtain_knxproj()

    logging.info("Group addresses:")
    for group_addr in knxproj.groupaddresses:
        logging.info("\t%s", group_addr)

    logging.info("Devices:")
    for dev in knxproj.devices:
        logging.info("\t%s", dev)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
