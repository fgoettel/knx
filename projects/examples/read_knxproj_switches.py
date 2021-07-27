#!/usr/bin/env python3
"""Read a projects and display all switches."""

import argparse
import logging
from pathlib import Path

from devices import dev2vendor
from devices.devices import Switch
from projects.knxproj import KnxprojLoader


def main():
    """Log all provided group addresses and devices."""
    # Setup argument parser
    description = "Generate documentation for a KNX project based on its ETS export."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--knxproj", required=True, type=str, help="Path to the ETS .knxproj export."
    )

    # Parse arguments
    args = parser.parse_args()
    knxproj_path = Path(args.knxproj)

    # Generic, non-vendor specific
    gas, devices = KnxprojLoader(knxproj_path=knxproj_path).run()

    # Get in the vendor specifics
    devices = [dev2vendor(dev, gas) for dev in devices]

    logging.info("Switches:")
    for dev in devices:
        if isinstance(dev, Switch):
            dev.doc()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
