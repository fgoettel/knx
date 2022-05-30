#!/usr/bin/env python3

"""Basic example."""

import asyncio
import logging
from pathlib import Path

from xknx.io import ConnectionType

from logger.runner import run as logger_run


def main() -> int:
    """Write values to a sqlite database."""
    # Set address of database
    # addr = "postgresql://{user}:{password}@{host}:{port}/{database}"
    addr = "sqlite://"
    mapping = Path(__file__).parent.joinpath("ga_mapping.json")

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("xknx").setLevel(logging.WARN)
    asyncio.run(
        logger_run(
            db_addr=addr,
            knx_mapping=mapping,
            knx_own_address="1.1.99",
            knx_gateway_ip="10.1.1.104",
            knx_gateway_port=3671,
            knx_route_back=False,
            knx_local_ip="10.1.1.135",
            knx_local_port=3671,
            knx_connection_type=ConnectionType.ROUTING,
            status_server=False,
            status_server_port=8080,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
