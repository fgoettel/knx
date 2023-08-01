#!/usr/bin/env python3
"""Generate an ORM for database logging based on xknx datatypes."""
import logging
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

from xknx import dpt

from logger.dtype_matcher import DTYPE2XKNX
from logger.util import xknx2name

from . import DST_DIR, LOGGER

KNXMIXIN = "KNXMixin"
DBBASEBAME = "Base"
DTYPE_DOC_SEPERATION = ", "
ORM_PATH = DST_DIR / "orm.py"


def dpst2db(dpst: str) -> str:
    """Translate a knx dtype into a db type."""
    xknx_class = DTYPE2XKNX[dpst]

    try:
        xknx_return_type = xknx_class.from_knx.__annotations__["return"]
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
    if xknx_return_type == "HVACModeT":
        # This will be only saved as integer
        return "types.Integer"

    error_msg = f"{xknx_return_type} / {dpst} is not mapped to a db type."
    raise ValueError(error_msg)


def get_mixin() -> str:
    """Create KNXMixin for all ORMs.

    Returns
    -------
    str
        KNXMixin as string to form foundation for all orms.

    """
    repr_str = (
        "{self.__class__.__name__}",
        "(value={self.value}, name={self.name}, time={self.time} ",
        "src={self.src}, dst={self.dst})",
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
    def value(self) -> Column:
        \"""Abstract placeholder for values.\"""

    def __repr__(self) -> str:
        \"""Return basic information about this entity (value, name, time, src, dst).\"""
        return f"{repr_str}"
    """
    return mixin.strip()


def get_imports(import_raw: dict[str, set]) -> str:
    """Dump imports to string.

    Parameters
    ----------
    import_raw : Dict[str, set]
        The imports in the form {module: type}

    Returns
    -------
    str
        Stringified imports

    Raises
    ------
    NotImplementedError
        For stuff that is not implemented.

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

        # Mimick isort
        additional_newline = "\n" if key == "datetime" else ""

        if values_clean:
            imports = ", ".join(sorted(set(values_clean)))
            lines.append(f"from {key} import {imports}{additional_newline}")

    return "\n".join(lines)


def get_base(import_dict: defaultdict[str, set[str]]) -> str:
    """Create base for sqlalchemy.

    Attention: The provided import dict is modified.

    Parameters
    ----------
    import_dict : Dict[str, set]
        The imports in the form {module: type}

    Returns
    -------
    str
        Stringified code to create a base

    """
    import_dict["sqlalchemy.orm"].add("declarative_base")
    return f"{DBBASEBAME} = declarative_base()\n"


def _get_orm(
    name: str,
    xknx_name: str,
    table_name: str,
    db_type: str,
    dpst_list: list,
) -> str:
    """Create the ORM.

    Parameters
    ----------
    name : str
        Name of the orm class (also used for the table)
    xknx_name : str
        Name of the associated xknx datatype (documentation only)
    table_name : str
        Name of the table
    db_type : str
        Type of the database entry
    dpst_list : list
        Datapoint type (in knx notation)

    Returns
    -------
    str
        Stringified code for the orm class.

    """
    return f"""
class {name}({KNXMIXIN}, {DBBASEBAME}):
    \"""ORM for xknx '{xknx_name}'.

    DType: {DTYPE_DOC_SEPERATION.join(dpst_list)}
    \"""

    __tablename__ = "{table_name}"
    value = Column({db_type})
"""


def get_orms() -> str:
    """Create all orms for dpsts.

    Returns
    -------
    str
        A string representing all sorted orms.

    Raises
    ------
    AssertionError
        In case of ambiguous db types.
    ValueError
        In case of duplicated orms.

    """
    type_dict = defaultdict(list)
    for dpst, xknx_type in DTYPE2XKNX.items():
        name = xknx2name(xknx_type)
        type_dict[name].append(dpst)

    orm_dict: dict[str, str] = {}
    for name, dpst_list in type_dict.items():
        # Ensure that all dpsts map to the same db type
        db_types = {dpst2db(d) for d in dpst_list}
        if len(db_types) != 1:
            raise AssertionError
        db_type = db_types.pop()

        # Ensure each name is only used once
        if name in orm_dict:
            error_msg = f"ORM {name} already exists (check {orm_dict[name]})."
            raise ValueError(error_msg)

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
    return "\n".join(orms_sorted.values())


def get_doc() -> str:
    """ORM Documentation."""
    file_ = "logger" + __file__.rsplit("logger", maxsplit=1)[1]
    return f'"""Autogenerated by {file_}."""'


class ORMGenerator:
    """Generate all orms.

    Each ORM is based on the xknx dpt class in logger.DTYPE2xknx.
    """

    @staticmethod
    def run() -> None:
        """Generate the ORMs."""
        # Get used xknx dtypes
        imports: defaultdict[str, set[str]] = defaultdict(set)

        imports["abc"].add("abstractmethod")
        imports["datetime"].add("datetime")
        imports["sqlalchemy"].add("Column")
        imports["sqlalchemy"].add("types")

        orms = get_orms()
        base = get_base(imports)

        # Combine it and write it to a file
        combined = "\n\n".join(
            (get_doc(), get_imports(imports), base, get_mixin(), orms),
        )
        with Path(ORM_PATH).open("w", encoding="utf-8") as file_:
            file_.write(combined)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ORMGenerator.run()
