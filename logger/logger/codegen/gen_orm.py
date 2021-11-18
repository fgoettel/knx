#!/usr/bin/env python3
"""Generate an ORM for database logging based on xknx datatypes."""
from __future__ import annotations

import logging
import re
from collections import OrderedDict, defaultdict
from typing import DefaultDict, Dict, Set

from xknx import dpt

from logger.util import xknx2name

from ..dtype_matcher import DTYPE2XKNX
from . import DST_DIR, LOGGER

KNXMIXIN = "KNXMixin"
DBBASEBAME = "Base"
ORM_PATH = DST_DIR / "orm.py"


def dpst2db(dpst: str) -> str:
    """Translate a knx dtype into a db type."""
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches

    xknx_class = DTYPE2XKNX[dpst]

    try:
        xknx_return_type = xknx_class.from_knx.__annotations__["return"]  # type: ignore
    except AttributeError:
        if issubclass(xknx_class, dpt.DPTBinary):
            # Binary not stored as boolean, rationale:
            # - easier to display in grafana
            # - memory: boolean uses 1 byte, an integer 4 bytes
            #   https://www.postgresql.org/docs/12/datatype-boolean.html
            xknx_return_type = "int"
        else:
            LOGGER.warning("No 'from_knx' method: %s", str(xknx_class))
            raise
    except KeyError:
        LOGGER.fatal("No return value for: %s", str(xknx_class))
        raise
    except TypeError:
        LOGGER.fatal("Multiple return values for %s", str(xknx_class))
        raise

    if xknx_return_type == "int":
        return "types.Integer"
    if xknx_return_type == "float":
        return "types.Float"
    if xknx_return_type == "time.struct_time":
        if dpst == "DPST-10-1":
            return "types.Time"
        if dpst == "DPST-11-1":
            return "types.Date"
        if dpst == "DPST-19-1":
            return "types.DateTime"
    if xknx_return_type == "str":
        return "types.String(14)"
    if xknx_return_type == "HVACModeType":
        # This will be only saved as integer
        return "types.Integer"

    raise ValueError(f"{xknx_return_type} / {dpst} is not mapped to a db type.")


def get_mixin() -> str:
    """Create KNXMixin for all ORMs.

    Returns
    -------
    KNXMixin : str
        KNXMixin as string to form foundation for all orms.

    """
    repr_str = (
        "{self.__class__.__name__}"
        + "(value={self.value}, name={self.name}, time={self.time} "
        + "src={self.src}, dst={self.dst})"
    )
    mixin = f"""
class {KNXMIXIN}:
    \"""Basic properties of each knx request.\"""

    id_ = Column(types.Integer, primary_key=True)
    time = Column(types.DateTime, default=datetime.utcnow)
    src = Column(types.String)
    dst = Column(types.String)
    name = Column(types.String)

    @property
    @abstractmethod
    def value(self):
        \"""Abstract placeholder for values.\"""

    def __repr__(self):
        \"""Return basic information about this entity (value, name, time, src, dst).\"""
        return f"{repr_str}"  # noqa: E501
    """
    return mixin.strip()


def get_imports(import_raw: Dict[str, set]) -> str:
    """Dump imports to string.

    Parameters
    ----------
    import_raw : Dict[str, set]
        The imports in the form {module: type}

    Returns
    -------
    imports : str
        Stringified imports

    """
    lines = []
    # 1. group: Type (\D+)
    # 2. group: Length restrictions
    # E.g., from 'String(14)' get 'String' in the first group
    expr = re.compile(r"^(\D+)(\(\d+\))?$")

    import_sorted = OrderedDict(sorted(import_raw.items()))
    for key, values in import_sorted.items():
        values_clean = []
        for val in values:
            result = expr.match(val)
            if result is None:
                LOGGER.error("Couldn't identify '%s: %s'.", key, val)
                raise NotImplementedError
            type_ = result.group(1)
            values_clean.append(type_)
        if values_clean:
            imports = ", ".join(sorted(set(values_clean)))
            lines.append(f"from {key} import {imports}")
    return "\n".join(lines)


def get_base(import_dict: DefaultDict[str, Set[str]]) -> str:
    """Create base for sqlalchemy.

    Attention: The provided import dict is modified.

    Parameters
    ----------
    import_dict : Dict[str, set]
        The imports in the form {module: type}

    Returns
    -------
    baseline : str
        Stringified code to create a base

    """
    import_dict["sqlalchemy.ext.declarative"].add("declarative_base")
    baseline = f"{DBBASEBAME} = declarative_base() \n"
    return baseline


def _get_orm(
    name: str, xknx_name: str, table_name: str, db_type: str, dpst_list: list
) -> str:
    """Create the ORM.

    Parameters
    ----------
    name
        Name of the orm class (also used for the table)
    xknx_name
        Name of the associated xknx datatype (documentation only)
    table_name
        Name of the table
    db_type
        Type of the database entry
    dpst_list
        Datapoint type (in knx notation)

    Returns
    -------
    str
        Stringified code for the orm class.

    """
    return f"""
class {name}({KNXMIXIN}, {DBBASEBAME}):
    \"""ORM for xknx '{xknx_name}'.

    DType: {", ".join(dpst_list)}
    \"""

    __tablename__ = "{table_name}"
    value = Column({db_type})
"""


def get_orms() -> str:
    """Create all orms for dpsts.

    Attention: the provided import dict is modified.
    """
    type_dict = defaultdict(list)
    for dpst, xknx_type in DTYPE2XKNX.items():
        name = xknx2name(xknx_type)
        type_dict[name].append(dpst)

    orm_dict: Dict[str, str] = {}
    for name, dpst_list in type_dict.items():

        # Ensure that all dpsts map to the same db type
        db_types = {dpst2db(d) for d in dpst_list}
        assert len(db_types) == 1
        db_type = db_types.pop()

        # Ensure each name is only used once
        if name in orm_dict:
            raise ValueError(f"ORM {name} already exists (check {orm_dict[name]}).")

        # Shouldn't matter which dpst we take (just documentation)
        # Exception: Power, there we have two xknx typesx
        xknx_type = DTYPE2XKNX[dpst_list[0]]
        orm_dict[name] = _get_orm(
            name=name,
            xknx_name=xknx_type.__name__,
            table_name=name.lower(),
            db_type=db_type,
            dpst_list=dpst_list,
        )

    # Sort em by the classname
    orms_sorted = OrderedDict(sorted(orm_dict.items(), key=lambda x: x[0]))
    orms_combined = "\n".join(orms_sorted.values())
    return orms_combined


def get_doc() -> str:
    """ORM Documentation."""
    file_ = "logger" + __file__.rsplit("logger", maxsplit=1)[1]
    return f'"""Autogenerated by {file_}."""'


class ORMGenerator:
    """Generate all orms.

    Each ORM is based on the xknx dpt class in logger.DTYPE2xknx.
    """

    @classmethod
    def run(cls) -> None:
        """Generate the ORMs."""
        # Get used xknx dtypes
        imports: DefaultDict[str, Set[str]] = defaultdict(set)

        imports["abc"].add("abstractmethod")
        imports["datetime"].add("datetime")
        imports["sqlalchemy"].add("Column")
        imports["sqlalchemy"].add("types")

        orms = get_orms()
        base = get_base(imports)

        # Combine it and write it to a file
        combined = "\n\n".join(
            (get_doc(), get_imports(imports), base, get_mixin(), orms)
        )
        with open(ORM_PATH, "w") as file_:
            file_.write(combined)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ORMGenerator.run()
