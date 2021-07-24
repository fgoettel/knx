"""Read a knxproj and display all group addresses and devices."""

import argparse
import logging
from pathlib import Path

from knxproj.knxproj import KnxprojLoader


def main():
    """Log all provided group addresses and devices."""
    # Setup argument parser
    description = "Generate documentation for a KNX project based on its ETS export."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("path", type=str, help="Path to the ETS .knxproj export.")

    # Parse arguments
    args = parser.parse_args()
    knxproj_path = Path(args.path)

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
