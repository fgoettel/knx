#!/usr/bin/env python3
"""Read a projects and display all switches."""

import logging
from pathlib import Path

from examples.read_knxproj import setup_parser
from projects.devices import dev2vendor
from projects.devices.devices import Switch
from projects.knxproj import KnxprojLoader


def main():
    """Log all provided group addresses and devices."""

    # Parse arguments
    parser = setup_parser()
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
