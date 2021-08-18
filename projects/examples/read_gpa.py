#!/usr/bin/env python3
"""Read a gpa project and display GAs."""

import argparse
import logging
from pathlib import Path

from projects.gpa import Gpa


def main():
    """Display existing knx datapoints in a gpa project."""
    # Setup argument parser
    description = "Display existing knx datapoints in a gpa project."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--gpa", type=str, required=True, help="Path to the gpa .gpa export."
    )

    # Parse arguments
    args = parser.parse_args()
    gpa_path = Path(args.gpa)

    # Run
    gpa = Gpa(gpa_path)
    gpa.display_infos()

    # Display them all
    for ga_ in sorted(gpa.groupaddresses, key=lambda x: x.name):
        logging.info(ga_)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
