"""Read a knxproj and display all switches."""
import argparse
import logging
from pathlib import Path

from knxproj.devices import dev2vendor
from knxproj.devices.devices import Switch
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
