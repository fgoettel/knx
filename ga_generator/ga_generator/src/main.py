#!/usr/bin/env python3

"""Entry point."""

import logging

from ga_generator.src.devices.mdt import AKD040102

LOG = logging.getLogger(__name__)


def main() -> None:
    """Entry point to create all teh group addresses."""
    foo = AKD040102(name="magic")

    LOG.info(foo)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
