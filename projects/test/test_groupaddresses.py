"""Test groupadresses."""
# pylint: disable=redefined-outer-name, unused-argument

from copy import copy

import pytest

from projects.groupaddresses import GroupAddress

from .util import (  # noqa: F401  # pylint:disable=unused-import
    get_groupaddress,
    get_groupaddress_factory,
    param_bools,
    xml_knx,
)


def test_groupaddress(get_groupaddress):
    """Ensure that GroupAddresses are
    - constructed as intended
    - properly translate their GA to the x/y/z format

    """

    # Valid GroupAddress
    assert isinstance(get_groupaddress, GroupAddress)

    addr = copy(get_groupaddress)

    for input_, excpected in (
        (0, "0/0/0"),
        (1, "0/0/1"),
        (255, "0/0/255"),
        (256, "0/1/0"),
    ):
        addr.address = input_
        assert addr.get_ga_str() == excpected


def test_factory_address(get_groupaddress_factory, xml_knx):
    """Test the Groupaddress factory."""

    address = get_groupaddress_factory.groupaddress(xml_knx)

    assert isinstance(address, GroupAddress)
    assert xml_knx.attrib["DatapointType"] == address.dtype
    assert xml_knx.attrib["Name"] == address.name

    # Expect to fail
    del xml_knx.attrib["DatapointType"]
    with pytest.raises(KeyError):
        get_groupaddress_factory.groupaddress(xml_knx)


if __name__ == "__main__":
    pytest.main(["-x"])
