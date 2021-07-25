"""Test the projects topology."""
# pylint: disable=redefined-outer-name

from xml.etree import ElementTree as ET

import pytest

from ..topology import DEFAULT_ADDR, Area, Device, Line
from ..util import KNXAddress
from .util import area  # noqa: F401  # pylint:disable=unused-import
from .util import get_topo_factory  # noqa: F401  # pylint:disable=unused-import
from .util import line  # noqa: F401  # pylint:disable=unused-import
from .util import param_bools  # noqa: F401  # pylint:disable=unused-import
from .util import xml_knx  # noqa: F401  # pylint:disable=unused-import


def test_item_subclasses():
    """Ensure that all topology items are subclasses of KNXAddress."""
    assert issubclass(Area, KNXAddress)
    assert issubclass(Device, KNXAddress)
    assert issubclass(Line, KNXAddress)


@pytest.mark.parametrize("use_addr", param_bools)
def test_factory_device_addr(use_addr, get_topo_factory, xml_knx, line):
    """Try to create a device."""
    if use_addr:
        expected_addr = xml_knx.attrib["Address"]
    else:
        del xml_knx.attrib["Address"]
        expected_addr = int(DEFAULT_ADDR)

    device = get_topo_factory.device(xml_knx, line)
    assert isinstance(device, Device)

    assert device.id_str == xml_knx.attrib["Id"]
    assert device.name == xml_knx.attrib["Name"]
    assert device.address == expected_addr
    assert device.groupaddress_list == []


@pytest.mark.parametrize("valid_gas", param_bools)
def test_factory_find_connections(valid_gas, get_topo_factory, xml_knx, line):
    """Try to create a device."""
    refs = ET.SubElement(xml_knx, "ComObjectInstanceRefs")
    ref = ET.SubElement(refs, "ComObjectInstanceRef")

    expected_gas = []
    expected_texts = []
    if valid_gas:
        expected_gas = ["a", "b", "c"]
        expected_texts = ["Foo"]

    ref.attrib["Links"] = " ".join(expected_gas)
    ref.attrib["Text"] = " ".join(expected_texts)

    device = get_topo_factory.device(xml_knx, line)

    assert isinstance(device, Device)
    assert device.id_str == xml_knx.attrib["Id"]
    assert device.name == xml_knx.attrib["Name"]
    assert device.address == xml_knx.attrib["Address"]
    assert device.groupaddress_list == expected_gas
    assert device.other["texts"] == expected_texts


def test_factory_line(get_topo_factory, xml_knx, area):
    """Try to create a line."""
    line = get_topo_factory.line(xml=xml_knx, area=area)

    assert isinstance(line, Line)
    assert line.id_str == xml_knx.attrib["Id"]
    assert line.address == xml_knx.attrib["Address"]
    assert line.name == xml_knx.attrib["Name"]
    assert line.medium == xml_knx.attrib["MediumTypeRefId"]


def test_factory_area(get_topo_factory, xml_knx):
    """Try to create an area."""
    area = get_topo_factory.area(xml_knx)

    assert isinstance(area, Area)
    assert area.id_str == xml_knx.attrib["Id"]
    assert area.address == xml_knx.attrib["Address"]
    assert area.name == xml_knx.attrib["Name"]


if __name__ == "__main__":
    pytest.main(["-x"])
