#!/usr/bin/env python3
"""Read a projects and display all group addresses and devices."""

import argparse
import logging
from pathlib import Path

from projects.knxproj import KnxprojLoader


def setup_parser() -> argparse.ArgumentParser:
    """Set up parser."""

    description = "Read a knxproj export from the ETS and fiddle around with it."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--knxproj", required=True, type=str, help="Path to the ETS .knxproj export."
    )
    return parser


def main():
    """Log all provided group addresses and devices."""

    # Parse arguments
    parser = setup_parser()
    args = parser.parse_args()
    knxproj_path = Path(args.knxproj)

    group_addresses, devices = KnxprojLoader(knxproj_path=knxproj_path).run()

    logging.info("Group addresses:")
    for group_addr in group_addresses:
        logging.info("\t%s", group_addr)

    logging.info("Devices:")
    for dev in devices:
        logging.info("\t%s", dev)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
