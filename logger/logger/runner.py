#!/usr/bin/env python3

"""Log all knx telegrams to database."""

import datetime as dt
import json
import logging
import typing
from collections.abc import Callable
from pathlib import Path
from threading import Thread

from sqlalchemy.orm import Session
from xknx import XKNX, dpt
from xknx.dpt import DPTArray
from xknx.io import ConnectionConfig, ConnectionType
from xknx.telegram import Telegram
from xknx.telegram.apci import GroupValueWrite

from logger import orm
from logger.dtype_matcher import DTYPE2XKNX
from logger.statusserver import Data
from logger.util import session_scope, xknx2name


async def get_mapping(mapping_path: Path) -> dict:
    """Load mapping and validate it.

    Load mapping from given json path and ensure that all used
    dtypes are covered by the xknx mapping.

    Parameters
    ----------
    mapping_path : Path
        Path to a json mapping

    Returns
    -------
    dict
        A mapping loaded and validated to match the used dtypes.

    Raises
    ------
    ValueError
        In case not all used dpts are covered.

    """
    logging.info("Loading mapping from %s", mapping_path.resolve())
    with Path(mapping_path).open(encoding="utf-8") as file_:
        mapping = json.load(file_)

    # Find unmatched
    needed_dtypes = {val["dtype"] for val in mapping.values()}
    available_dtypes = set(DTYPE2XKNX.keys())

    for needed_not_available in needed_dtypes - available_dtypes:
        logging.error("%s not covered by DTYPE2XKNX", needed_not_available)

    if not needed_dtypes.issubset(available_dtypes):
        error_msg = "Not all dpst that are needed are covered."
        raise ValueError(error_msg)

    return mapping


async def get_rx_cb(
    mapping: dict,
    db_session: Session,
    status: Data | None,
) -> Callable:
    """Yield a msg receive callback."""

    @typing.no_type_check
    async def telegram_rx_cb(telegram: Telegram) -> bool:
        """Extract value from received telegram and store in database.

        Parameters
        ----------
        telegram : Telegram
            A received telegram

        Returns
        -------
            True on success
            False on failure

        """
        logging.debug("Telegram rx: %s", telegram)

        # Only act on write requests
        if not isinstance(telegram.payload, GroupValueWrite):
            logging.debug("Ignored non-write request: %s", telegram.payload)
            return False

        # Extract info from telegram
        try:
            src = str(telegram.source_address)
            dst = str(telegram.destination_address)
            value_raw = telegram.payload.value.value
        except Exception as err:
            logging.exception("Couldn't extract necessary information from telegram.")
            logging.exception(err)
            return False

        # Map telegram information to knx a-priori information
        try:
            meta = mapping[str(dst)]

            name = meta["name"]
            dtype = meta["dtype"]
            xknx_class = DTYPE2XKNX[dtype]

            # Calculate value
            # Also translate hvac enum
            if xknx_class in (
                dpt.DPTHVACContrMode,
                dpt.DPTControlStepwise,
                dpt.DPTControlStepwiseBlinds,
                dpt.DPTControlStepwiseDimming,
            ):
                # This is an enum, just take the raw value
                value = value_raw[0]
            elif xknx_class == dpt.DPTBinary:
                # Keep the binary as integer for easier storage
                value = int(value_raw)
            else:
                value = xknx_class.from_knx(DPTArray(value_raw))

            # Translate time_struct to datetime objects
            if dtype == "DPST-10-1":
                # value_raw is a tuple with 3 elements
                value = dt.time(
                    hour=value_raw[0] & 0b11111,
                    minute=value_raw[1],
                    second=value_raw[2],
                )
            elif dtype == "DPST-11-1":
                value = dt.date(day=value_raw[0], month=value_raw[1], year=value_raw[2])
            elif dtype == "DPST-19-1":
                # value_raw is a tuple with 8 elements
                value = dt.datetime(
                    year=value_raw[0],
                    month=value_raw[1],
                    day=value_raw[2],
                    hour=value_raw[3] & 0b11111,
                    minute=value_raw[4],
                    second=value_raw[5],
                )

            # Get unit (if existent)
            try:
                unit = xknx_class.unit
            except AttributeError:
                unit = ""
            if unit is None:
                unit = ""
            logging.info("%s sent %s%s from %s to %s.", name, value, unit, src, dst)
        except Exception as err:
            logging.exception(
                "Couldn't map received telegram to a-priori knx information.",
            )
            logging.exception(err)
            return False

        # Translate information to db ORM
        try:
            orm_name = xknx2name(xknx_class)
            orm_class = getattr(orm, orm_name)
            orm_instance = orm_class(src=src, dst=dst, name=name, value=value)
        except Exception as err:
            logging.exception("Couldn't map info to ORM.")
            logging.exception(err)
            return False

        # Save to db
        try:
            db_session.add(orm_instance)
            db_session.commit()
        except Exception as err:
            logging.exception("Couldn't save instance of orm: %s", orm_instance)
            logging.exception(err)
            return False

        # Populate status
        if status is not None:
            try:
                status.last_rx_time = dt.datetime.now()
                status.data_dict["last_rx"] = f"{name} sent {value}{unit} from {src} to {dst}."
            except Exception as err:
                logging.exception("Couldn't populate status.")
                logging.exception(err)
                return False

        return True

    return telegram_rx_cb


async def run(
    db_addr: str,
    knx_mapping: Path,
    knx_own_address: str,
    knx_gateway_ip: str | None = None,
    *,
    knx_gateway_port: int = 3671,
    knx_route_back: bool = False,
    knx_local_ip: str | None = None,
    knx_local_port: int = 0,
    knx_connection_type: ConnectionType = ConnectionType.AUTOMATIC,
    status_server: bool = False,
    status_server_port: int = 8080,
) -> None:
    """Write all logged knx telegrams to a db."""
    # Get validated mapping
    mapping = await get_mapping(knx_mapping)

    # Get up a status server
    status = None
    if status_server:
        logging.info("Status Server enabled.")
        from logger.statusserver import StatusServer

        status = Data(
            last_rx_time=dt.datetime(year=2000, month=1, day=1),
            max_delta=dt.timedelta(minutes=5),
            data_dict={},
        )
        server = StatusServer(port=status_server_port, data=status)
        Thread(target=server.run).start()

    # Get session with scope
    connection_conf = ConnectionConfig(
        connection_type=knx_connection_type,
        local_ip=knx_local_ip,
        local_port=knx_local_port,
        gateway_ip=knx_gateway_ip,
        gateway_port=knx_gateway_port,
        route_back=knx_route_back,
        individual_address=knx_own_address,
    )
    xknx = XKNX(
        daemon_mode=True,
        connection_config=connection_conf,
    )
    with session_scope(db_addr) as session:
        rx_cb = await get_rx_cb(mapping, session, status)
        xknx.telegram_queue.register_telegram_received_cb(rx_cb)
        await xknx.start()
        await xknx.stop()
