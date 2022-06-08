"""Utility functions."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as sqla_session
from sqlalchemy.orm import sessionmaker
from xknx.dpt import DPTArray, DPTBinary, DPTNumeric


@contextmanager
def session_scope(addr: str) -> Generator[sqla_session, None, None]:
    """Provide context manager for sqlalchemy session."""
    # not at the top, as it needs to be generated
    from logger.orm import Base  # pylint: disable=import-outside-toplevel

    engine = create_engine(addr, future=True)
    Base.metadata.create_all(
        engine
    )  # TODO: check if this can be refactored to only be done once per db, not for every session
    Session = sessionmaker(engine, future=True)  # pylint: disable=invalid-name
    session = Session()
    try:
        yield session
        session.flush()
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@cache
def xknx2name(xknx_type: DPTNumeric | DPTBinary | DPTArray) -> str:
    """Make a proper name out of an xknx dpt."""
    name = xknx_type.__name__  # type: ignore
    name = name.removeprefix("DPT")
    name = name.removesuffix("2Byte")

    if name.startswith("16"):
        name = name.replace("16", "Sixteen")
    if name.startswith("1"):
        name = name.replace("1", "One")
    if name.startswith("2"):
        name = name.replace("2", "Two")
    if name.startswith("4"):
        name = name.replace("4", "Four")
    if name.startswith("8"):
        name = name.replace("8", "Eight")
    logging.debug("Converting '%s' to '%s'.", xknx_type, name)
    return name
