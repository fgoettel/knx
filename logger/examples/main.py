#!/usr/bin/env python3

"""Basic example."""

import asyncio
import logging
from pathlib import Path

from logger.runner import run as logger_run


def main() -> int:
    """Write values to a local temporary database.

    By default it writes to a local sqlite db.

    It could also use a remote db with the following address scheme:
    `postgresql://{user}:{password}@{host}:{port}/{database}`
    """
    addr = "sqlite://"
    mapping = Path(__file__).parent.joinpath("ga_mapping.json")

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("xknx").setLevel(logging.WARN)
    asyncio.run(
        logger_run(
            db_addr=addr,
            knx_mapping=mapping,
            knx_own_address="1.1.99",
            knx_route_back=False,
            knx_local_port=3671,
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
