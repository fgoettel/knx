#!/usr/bin/env python3
"""Test the generated orms."""

import random
import re
import string
from datetime import UTC, timedelta
from datetime import datetime as dt
from typing import Any

import pytest
from sqlalchemy import select
from xknx.dpt import DPTArray, DPTBinary
from xknx.telegram import Telegram, TelegramDirection
from xknx.telegram.apci import GroupValueWrite

from logger import orm
from logger.codegen.gen_orm import DTYPE_DOC_SEPERATION
from logger.dtype_matcher import DTYPE2XKNX
from logger.orm import KNXMixin
from logger.runner import get_rx_cb
from logger.util import is_binary, session_scope

RE_DTYPE = re.compile(
    r"^\s*DType:\s(?P<dtype>.*)$",
    flags=(re.IGNORECASE | re.MULTILINE),
)

LEGAL_CHARS = string.ascii_letters + string.digits + string.punctuation


def all_orms() -> list[tuple[KNXMixin, str]]:
    """Get all autogenerated orms."""
    orm_list = []
    for name in dir(orm):
        orm_class = getattr(orm, name)

        # Continue if it's not a class
        try:
            # Only keep items inherited from the mixin
            if not issubclass(orm_class, KNXMixin):
                continue
        except TypeError:
            continue

        # Don't keep the mixin itself
        if name == KNXMixin.__name__:
            continue

        dtype_search = RE_DTYPE.search(orm_class.__doc__)
        assert dtype_search is not None
        dtype_match = dtype_search.group("dtype")
        orm_list += [(orm_class, dtype) for dtype in dtype_match.split(DTYPE_DOC_SEPERATION)]

    return orm_list


@pytest.fixture
def name(length: int = 10) -> str:
    """Get a random signal name."""
    return "".join(random.choice(LEGAL_CHARS) for _ in range(length))


@pytest.fixture
def payload(dtype: str) -> GroupValueWrite:
    """Get a payload, matching the knx type."""
    xknx_class = DTYPE2XKNX[dtype]

    # Special case for bool
    if is_binary(xknx_class):
        value = DPTBinary(random.randint(0, 1))
        return GroupValueWrite(value=value)

    # Generate a random array of values with corresponding length
    value_raw = [random.randrange(0, 2**8) for _ in range(xknx_class.payload_length)] # type: ignore

    # Bunch of special cases that do not allow the full range available
    dtype_group = dtype.split("-")[1]
    if dtype_group == "3":
        # Boolean + 3-bit unsigned value
        value_raw[0] &= 0xF
    elif dtype in (
        "DPST-9-1",
        "DPST-9-2",
        "DPST-9-4",
        "DPST-9-5",
        "DPST-9-6",
        "DPST-9-7",
        "DPST-9-27",
        "DPST-9-28",
        "DPST-9-29",
        "DPST-9-30",
    ):
        # Value must be > 0
        value_raw[0] &= 0b01111111
    elif dtype == "DPST-10-1":
        # TimeOfDay
        value_raw[0] = (random.randint(1, 7) << 5) | random.randint(
            0,
            23,
        )  # weekday (0 - not set, invalid for datetime) | hours
        value_raw[1] = random.randint(0, 59)  # minutes
        value_raw[2] = random.randint(0, 59)  # seconds
    elif dtype == "DPST-11-1":
        # Date
        value_raw[0] = random.randint(1, 28)  # day
        value_raw[1] = random.randint(1, 12)  # month
        value_raw[2] = random.randint(
            1,
            89,
        )  # year (full range is 0-99, but >= 90 is 19xx)
    elif dtype in ("DPST-18-1", "DPST-17-1"):
        # Scenes must be < 64
        value_raw[0] = random.randint(0, 63)
    elif dtype == "DPST-19-1":
        # Datetime
        value_raw[0] = random.randint(0, 255)  # year
        value_raw[1] = random.randint(1, 12)  # month
        value_raw[2] = random.randint(1, 28)  # day
        value_raw[3] = (random.randint(1, 7) << 5) | random.randint(
            0,
            23,
        )  # weekday | hours
        value_raw[4] = random.randint(0, 59)  # minutes
        value_raw[5] = random.randint(0, 59)  # seconds
        value_raw[6] = 0  # no fault
        value_raw[7] = 0  # no quality indication
    elif dtype in ("DPST-20-102", "DPST-20-105"):
        value_raw[0] = 0

    return GroupValueWrite(value=DPTArray(value_raw))


@pytest.fixture
def src() -> str:
    """Get a random KNX PA."""
    return f"{random.randrange(0, 16)}.{random.randrange(0, 16)}.{random.randrange(0, 256)}"


@pytest.fixture
def dst() -> str:
    """Get a random KNX GA."""
    return f"{random.randrange(0, 256)}/{random.randrange(0, 256)}/{random.randrange(0, 256)}"


@pytest.mark.asyncio
@pytest.mark.parametrize(("orm_under_test", "dtype"), all_orms())
async def test_orm_x(
    orm_under_test: Any,
    dtype: str,
    name: str,
    payload: GroupValueWrite,
    src: Any,
    dst: Any,
) -> None:
    """Test if a xknx message is correctly stored into a database."""
    # Should be a subclass of knxmixin, but not knxmixin
    assert issubclass(orm_under_test, KNXMixin)

    # Constants
    mapping = {dst: {"dtype": dtype, "name": name}}
    addr = "sqlite://"
    tele = Telegram(
        direction=TelegramDirection.INCOMING,
        source_address=src,
        destination_address=dst,
        payload=payload,
    )

    with session_scope(addr) as session:
        rx_cb = await get_rx_cb(mapping=mapping, db_session=session, status=None)

        # Add it to the db, await success
        assert await rx_cb(tele)

        # Get data and ensure it's the only thing added
        statement = select(orm_under_test)
        all_items_from_db = session.execute(statement)

        # Scalar one fails if not exactly one item is returned
        item_from_db = all_items_from_db.scalar_one()

        # Ensure that the thing is correctly added
        # Value is not checked, we trust xknx to do the right thing here.
        tzinfo = UTC
        db_item_time_utc = dt.combine(item_from_db.time.date(), item_from_db.time.time(), tzinfo=tzinfo)
        age = dt.now(tzinfo) - db_item_time_utc
        assert timedelta() <= age < timedelta(seconds=10)  # Relatively large margin of 10sec, due to async testing
        assert item_from_db.name == name
        assert item_from_db.src == src
        assert item_from_db.dst == dst


if __name__ == "__main__":
    pytest.main([__file__])
