"""Test the projects."""
from xml.etree import ElementTree as ET

import pytest

from projects.util import PROJECT_NAMESPACES, FinderXml, postfix

from .util import (  # noqa: F401  # pylint:disable=unused-import
    get_groupaddress,
    param_bools,
    param_none_numbers,
    xml_knx,
)

# pylint: disable=redefined-outer-name,protected-access


@pytest.mark.parametrize("expected_count", [None, 0, 1, 10])
@pytest.mark.parametrize("namespace", ["", "ets56", "ets57"])
def test_finder_xml(namespace, expected_count):
    """Test the finder function with namespace variation."""
    # Setup xml
    xml = ET.Element("KNX")
    if namespace:
        xml.attrib["xmlns"] = PROJECT_NAMESPACES[namespace]
    # Add keyword / value
    keyword = "Foo"
    payload = {"Bar": "Baz"}
    if expected_count is None:
        counts = range(1)
    else:
        counts = range(expected_count)
    for _ in counts:
        for key, value in payload.items():
            ET.SubElement(xml, keyword).attrib[key] = value
    xml_string = ET.tostring(xml, encoding="utf-8").decode("utf-8")

    # Setup finder
    finder = FinderXml(namespace=namespace)
    assert callable(finder)

    # Find
    result = finder(
        ET.fromstring(xml_string), keyword=keyword, expected_count=expected_count
    )

    # TODO: Fix special treatment of 1 finding
    if expected_count == 1:
        result = [result]
    assert isinstance(result, list)

    for res in result:
        assert res.attrib == payload


def test_postfix():
    """Test that the separator is properly attended."""
    assert postfix("foo") == "foo_"
    assert postfix("foo", "+") == "foo+"


if __name__ == "__main__":
    pytest.main(["-x"])
