#!/usr/bin/env python3
"""Compare knx GAs from ETS and GPA export."""

import argparse
import logging
from pathlib import Path

from projects.gpa import GpaLoader
from projects.knxproj import KnxprojLoader


def main():
    """Compare knx GAs from ETS and GPA export."""
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

    # Run
    gpa_addresses = GpaLoader(gpa_path=gpa_path).run()
    ets_addresses, _ = KnxprojLoader(knxproj_path=knxproj_path).run()

    # Put them to two dicts
    gpa_dict = {ga.address: ga for ga in gpa_addresses}
    ets_dict = {ga.address: ga for ga in ets_addresses}

    def ga_compare(lhs, rhs):
        def ga_str(ga):
            return f"{ga.get_ga_str()}: {ga.name}, {ga.dtype}"

        logging.debug(ga_str(lhs))
        logging.debug(ga_str(rhs))

        addr_ok = lhs.address == rhs.address
        # TODO: Rework
        lhs_dtype_split = lhs.dtype.split("-")
        rhs_dtype_split = rhs.dtype.split("-")
        assert lhs_dtype_split[0] == "DPST"
        assert rhs_dtype_split[0] == "DPST"
        dtype_ok = lhs_dtype_split[1] == rhs_dtype_split[1]
        #
        name_ok = (lhs.name in rhs.name) or (rhs.name in lhs.name)

        if not all((addr_ok, dtype_ok, name_ok)):
            logging.info("Unequal ga.")
            logging.info(ga_str(lhs))
            logging.info(ga_str(rhs))
            if not addr_ok:
                logging.info("Address not eq.")
            if not dtype_ok:
                logging.info("Dtype not eq.")
            if not name_ok:
                logging.info("Name not ok.")

    # Display all from the gpa and their counterpart from the ETS
    for key in sorted(gpa_dict.keys()):
        try:
            ga_compare(gpa_dict[key], ets_dict[key])
        except KeyError:
            ga_missing = gpa_dict[key]
            logging.error(
                "GA in gpa but not in knxproj: %s - %s!",
                ga_missing.get_ga_str(),
                ga_missing,
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
