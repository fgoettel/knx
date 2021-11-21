#!/usr/bin/env python3
"""Read a projects and display all switches."""

import logging

from projects.devices import dev2vendor
from projects.devices.devices import Switch

from . import read_knxproj


def main():
    """Log all provided group addresses and devices."""

    knxproj = read_knxproj.obtain_knxproj()

    # Get in the vendor specifics
    devices = [dev2vendor(dev, knxproj.groupaddresses) for dev in knxproj.devices]

    logging.info("Switches:")
    for dev in devices:
        if isinstance(dev, Switch):
            dev.doc()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
