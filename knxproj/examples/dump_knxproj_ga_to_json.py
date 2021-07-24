"""Read a knxproj and dump its group addresses to a json file."""

import argparse
import json
import logging
from collections import OrderedDict
from pathlib import Path

from knxproj.knxproj import KnxprojLoader


def main(json_path="knx_mapping.json"):
    """Dump a dictionary that links group_addresses to data types."""
    # Setup argument parser
    description = "Generate documentation for a KNX project based on its ETS export."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--knxproj", required=True, type=str, help="Path to the ETS .knxproj export."
    )

    # Parse arguments
    args = parser.parse_args()
    knxproj_path = Path(args.knxproj)

    # Run
    group_addresses, _ = KnxprojLoader(knxproj_path=knxproj_path).run()

    # Iterate over group addresses and create mapping
    groupaddress_to_dtype = {}
    for group_address in group_addresses:
        groupaddress_to_dtype[group_address.get_ga_str()] = {
            "dtype": group_address.dtype,
            "name": group_address.name,
        }

    ordered_by_address = OrderedDict(sorted(groupaddress_to_dtype.items()))

    with open(json_path, "w", encoding="utf-8") as file_:
        json.dump(ordered_by_address, file_, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
