#!/usr/bin/env python3
"""Compare knx GAs from ETS and GPA export."""

import argparse
import logging
from pathlib import Path
from typing import Tuple

from projects.gpa import Gpa
from projects.knxproj import Knxproj


def get_args() -> Tuple[Path, Path]:
    """Set up the parser.

    Returns a tuple with (gpa_path, knxproj_path).
    """

    # Setup argument parser
    description = "Compare knx GAs from ETS and GPA export."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--gpa", type=str, required=True, help="Path to the gpa .gpa export."
    )
    parser.add_argument(
        "--knxproj", type=str, required=True, help="Path to the ETS .knxproj export."
    )

    # Parse arguments
    args = parser.parse_args()
    gpa_path = Path(args.gpa)
    knxproj_path = Path(args.knxproj)

    return (gpa_path, knxproj_path)


def main():
    """Compare knx GAs from ETS and GPA export."""

    gpa_path, knxproj_path = get_args()

    # Run
    gpa_addresses = Gpa(gpa_path=gpa_path).groupaddresses
    ets_addresses = Knxproj(knxproj_path=knxproj_path).groupaddresses

    # Put them to two dicts
    gpa_dict = {ga.address: ga for ga in gpa_addresses}
    ets_dict = {ga.address: ga for ga in ets_addresses}

    # Display all from the gpa and their counterpart from the ETS
    for key in sorted(gpa_dict.keys()):
        lhs = gpa_dict[key]
        try:
            rhs = ets_dict[key]
        except KeyError:
            logging.error(
                "GA in gpa but not in knxproj: \n\t%s",
                lhs,
            )
            continue

        if not lhs.almost_equal(rhs):
            logging.info("Unequal:\n\t%s\n\t%s", lhs, rhs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
