#!/usr/bin/env python3

"""Generate the mapping of dtype to xknx class."""

import logging
import sys
from typing import Dict, List

from xknx import dpt

from . import DST_DIR, LOGGER

DTYPE_MATCHER_PATH = DST_DIR / "dtype_matcher.py"


def get_mapping() -> Dict[str, str]:
    """Map all existing xknx dpt classes against their dtype.

    Returns a dict {dpt_name: xknx_name}.
    """
    mapping = {}
    for name in dir(dpt):

        if name.startswith("_"):
            continue

        xknx_dpt_class = getattr(dpt, name)

        # Get a valid "main" number
        try:
            dpt_main = xknx_dpt_class.dpt_main_number
        except AttributeError:
            # I.e. manual patching required
            LOGGER.error("No main number for %s", name)
            continue
        if dpt_main is None:
            LOGGER.error("Main is 'None' for %s", name)
            continue

        # Try to get a valid sub number
        dpt_sub = getattr(xknx_dpt_class, "dpt_sub_number", None)
        if dpt_sub is None:
            LOGGER.info("No sub number for %s", name)
            dtype_str = f"DPT-{dpt_main}"
        else:
            dtype_str = f"DPST-{dpt_main}-{dpt_sub}"

        mapping[dtype_str] = f"dpt.{name},"

    return mapping


def extend_mapping(mapping):
    """Extend the autogenerated mapping with additionally used types."""
    # TODO: fix upstream
    extension = {}
    extension["DPT-1"] = "dpt.DPTBinary,"
    extension["DPST-1-1"] = "dpt.DPTBinary,  # Switch"
    extension["DPST-1-2"] = "dpt.DPTBinary,  # Bool"
    extension["DPST-1-3"] = "dpt.DPTBinary,  # Enable"
    extension["DPST-1-5"] = "dpt.DPTBinary,  # Alarm"
    extension["DPST-1-6"] = "dpt.DPTBinary,  # BinaryValue"
    extension["DPST-1-7"] = "dpt.DPTBinary,  # Step"
    extension["DPST-1-8"] = "dpt.DPTBinary,  # UpDown"
    extension["DPST-1-9"] = "dpt.DPTBinary,  # OpenClose"
    extension["DPST-1-10"] = "dpt.DPTBinary,  # Start"
    extension["DPST-1-11"] = "dpt.DPTBinary,  # State"
    extension["DPST-1-15"] = "dpt.DPTBinary,  # Reset"
    extension["DPST-1-16"] = "dpt.DPTBinary,  # Acknowledge"
    extension["DPST-1-17"] = "dpt.DPTBinary,  # Trigger"
    extension["DPST-1-19"] = "dpt.DPTBinary,  # Window_Door"
    extension["DPST-1-23"] = "dpt.DPTBinary,  # ShutterBlinds_Mode"
    extension["DPST-2-1"] = "dpt.DPTValue1Ucount,  # Switch_Control TODO: xknx type"
    extension["DPST-2-2"] = "dpt.DPTValue1Ucount,  # Bool_Control TODO: xknx type"
    extension[
        "DPST-6-20"
    ] = "dpt.DPTSignedRelativeValue,  # Status_Mode3 TODO:xknx type"
    extension["DPST-10-1"] = "dpt.DPTTime,"
    extension["DPST-11-1"] = "dpt.DPTDate,"
    extension["DPST-16-1"] = "dpt.DPTString,  # encoding: iso-8859-1"

    extension["DPST-18-1"] = "dpt.DPTSceneNumber,  # SceneControl"
    extension["DPST-19-1"] = "dpt.DPTDateTime,"
    extension["DPST-20-105"] = "dpt.DPTHVACContrMode,"
    extension["DPST-21-1"] = "dpt.DPTValue1Ucount,  # StatusGen TODO: xknx type"
    extension["DPT-22"] = "dpt.DPT2ByteUnsigned,  # StatusGen TODO: xknx type"
    extension[
        "DPST-27-1"
    ] = "dpt.DPT4ByteUnsigned,  # CombinedInfoOnOff TODO: xknx type; info_on_off"
    extension[
        "DPST-238-600"
    ] = "dpt.DPT4ByteUnsigned,  # TODO: xknx type, just a guess now"

    extension_keys = set(extension.keys())
    mapping_keys = set(mapping.keys())
    if not extension_keys.isdisjoint(mapping_keys):
        common_keys = extension_keys & mapping_keys
        LOGGER.warning("Manually overriding autogenerated keys: %s", common_keys)

    mapping.update(extension)

    return mapping


def dtype_sorter(dtype_str) -> int:
    """Sort by dtype maingroup."""
    value = int(dtype_str.split("-")[1]) * 1000

    try:
        value += int(dtype_str.split("-")[2])
    except IndexError:
        pass
    return value


def get_lines(mapping: dict) -> List:
    """Create a list of lines containing the serialized mapping."""
    lines = []
    # Doc
    file_ = "logger" + __file__.rsplit("logger", maxsplit=1)[1]
    lines.append(f'"""Autogenerated by {file_}."""')

    # Imports
    lines.append("from xknx import dpt")
    lines.append("DTYPE2XKNX = {")
    for dtype in sorted(mapping.keys(), key=dtype_sorter):
        lines.append(4 * " " + f'"{dtype}": {mapping[dtype]}')
    lines.append("}")

    return lines


def main():
    """Let's autogenerate a dpst <-> xknx mapping."""
    mapping = get_mapping()
    mapping_extended = extend_mapping(mapping)

    lines = get_lines(mapping_extended)

    with open(DTYPE_MATCHER_PATH, "w", encoding="utf-8") as file_:
        file_.write("\n".join(lines))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
