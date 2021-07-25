"""Read a gpa project and display GAs."""

import argparse
import logging
from pathlib import Path

from projects.gpa import GpaLoader


def main():
    """Display existing knx datapoints in a gpa project."""
    # Setup argument parser
    description = "Display existing knx datapoints in a gpa project."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("path", type=str, help="Path to the gpa .gpa export.")

    # Parse arguments
    args = parser.parse_args()
    gpa_path = Path(args.path)

    # Run
    group_addresses = GpaLoader(gpa_path=gpa_path).run()

    # Display them all
    for ga_ in sorted(group_addresses, key=lambda x: x.name):
        logging.info(ga_)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
