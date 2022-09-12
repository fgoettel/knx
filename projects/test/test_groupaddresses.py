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
    """Test group adresses.

    Ensure that GroupAddresses are
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


def test_groupaddress_almost_eq(get_groupaddress):
    """Test groupaddress.

    Ensure that GroupAddresses are
    - constructed as intended
    - properly translate their GA to the x/y/z format
    """
    # Valid GroupAddress
    assert isinstance(get_groupaddress, GroupAddress)

    lhs = copy(get_groupaddress)
    lhs.address = "1/2/3"

    # Different type
    assert not lhs.almost_equal(None)

    # Different address
    rhs = copy(lhs)
    rhs.address = "4/5/6"
    assert not lhs.almost_equal(rhs)

    # Different dtype
    rhs = copy(lhs)
    rhs.dtype = "Foo"
    assert not lhs.almost_equal(rhs)

    # Different name
    rhs = copy(lhs)
    rhs.name = "Foo"
    assert not lhs.almost_equal(rhs)

    # Almost same name
    rhs = copy(lhs)
    rhs.name += "Foo"
    assert lhs.almost_equal(rhs)

    # Same name
    rhs = copy(lhs)
    assert lhs.almost_equal(rhs)


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
