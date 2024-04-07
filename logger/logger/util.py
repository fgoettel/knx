"""Utility functions."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from xknx.dpt import DPTArray, DPTBinary, DPTNumeric


@contextmanager
def session_scope(addr: str) -> Generator[Session, None, None]:
    """Provide context manager for sqlalchemy session."""
    # not at the top, as it needs to be generated
    from logger.orm import Base

    engine = create_engine(addr, future=True)
    Base.metadata.create_all(
        engine,
    )  # TODO: check if this can be refactored to only be done once per db, not for every session
    session_cls = sessionmaker(engine, future=True)
    session = session_cls()
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
    name = xknx_type.__name__  # type: ignore [union-attr]
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
