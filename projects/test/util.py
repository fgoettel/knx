"""Central place for mocks, fixtures, etc."""
# pylint: disable=invalid-name,no-name-in-module,import-error,unused-argument

import random
from string import ascii_lowercase
from xml.etree import ElementTree as ET

import pytest

from projects.groupaddresses import Factory as ga_factory
from projects.groupaddresses import GroupAddress
from projects.topology import Area, Line
from projects.topology import Factory as topo_factory
from projects.util import FinderXml

PREFIX = "FOO"

param_bools = [True, False]
param_none_numbers = [None, 1, 2, 3, 4, 5, 6, 7]
# get that from the loger
param_dtypes = [
    "DPT-1",
    "DPST-1-1",
    "DPST-1-2",
    "DPST-1-3",
    "DPST-1-5",
    "DPST-1-6",
    "DPST-1-7",
    "DPST-1-8",
    "DPST-1-9",
    "DPST-1-10",
    "DPST-1-11",
    "DPST-1-15",
    "DPST-1-17",
    "DPST-1-19",
    "DPST-1-23",
    "DPST-2-1",
    "DPST-3-7",
    "DPT-5",
    "DPST-5-1",
    "DPST-5-5",
    "DPST-5-10",
    "DPST-6-20",
    "DPT-7",
    "DPST-7-1",
    "DPST-7-7",
    "DPST-7-12",
    "DPST-7-600",
    "DPT-8",
    "DPT-9",
    "DPST-9-1",
    "DPST-9-4",
    "DPST-9-5",
    "DPST-9-6",
    "DPST-9-7",
    "DPST-9-20",
    "DPST-9-24",
    "DPST-9-26",
    "DPST-10-1",
    "DPST-11-1",
    "DPT-13",
    "DPST-13-10",
    "DPST-13-100",
    "DPST-14-19",
    "DPST-14-27",
    "DPST-14-33",
    "DPST-14-56",
    "DPST-14-65",
    "DPST-16-0",
    "DPST-16-1",
    "DPST-17-1",
    "DPST-18-1",
    "DPST-19-1",
    "DPST-20-105",
    "DPST-21-1",
    "DPST-27-1",
    "DPST-238-600",
]
param_medium = ["TP", "IP", "TP_OR_IP"]
param_productRefId = ["MDT_GT2", "FOO", "BAR.Baz"]


def _get_address() -> int:
    return random.randrange(0, 255)


def _get_id() -> str:
    return str(random.randrange(0, 99999))


def _get_area() -> Area:
    return Area(id_str=_get_id(), address=_get_address(), name=_get_name_str())


def _get_name_str() -> str:
    name_len = random.randrange(1, 15)  # Arbitrarily chosen length
    return "".join(random.choice(ascii_lowercase) for _ in range(name_len)).capitalize()


@pytest.fixture()
def get_groupaddress():
    """Get a randomized group address."""
    return GroupAddress(
        id_str=_get_id(),
        address=_get_address(),
        name=_get_name_str(),
        dtype=random.choice(param_dtypes),
    )


@pytest.fixture()
def get_groupaddress_factory():
    """Get one factory to crate gas from xml."""
    return ga_factory(PREFIX)


@pytest.fixture()
def get_topo_factory():
    """Get a factory to convert xml to topology items."""
    return topo_factory(prefix=PREFIX, finder=FinderXml().findall)


@pytest.fixture()
def xml_knx(dtype="DPST-1-1"):
    """Create a xml for a knx element."""
    xml_ = ET.Element(PREFIX)
    xml_.attrib["DatapointType"] = dtype
    xml_.attrib["Id"] = _get_id()
    xml_.attrib["Name"] = _get_name_str()
    xml_.attrib["Address"] = _get_address()
    xml_.attrib["MediumTypeRefId"] = random.choice(param_medium)
    xml_.attrib["ProductRefId"] = random.choice(param_productRefId)

    return xml_


@pytest.fixture()
def area():
    """Get a valid knx topology 'Area'."""
    return _get_area()


@pytest.fixture()
def line():
    """Get a valid knx topology 'Line'."""
    return Line(
        id_str=_get_id(),
        address=_get_address(),
        name=_get_name_str(),
        medium=random.choice(param_medium),
        area=_get_area(),
    )
