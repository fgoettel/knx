"""Provide the base attributes of an KNX element."""
# pylint: disable=unsubscriptable-object  # Optional

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

# Project namespaces, currently supported:
#  - ETS 5.7
#  - Gira GPA (April 2020)
PROJECT_NAMESPACES = {
    "ets56": "http://knx.org/xml/project/14",
    "ets57": "http://knx.org/xml/project/20",
    "gpa": "http://service.schema.gira.de/configuration",
}


def postfix(prefix: str, sep: str = "_") -> str:
    """Add a postfix, default to '_' to the prefix."""
    return "".join((prefix, sep))


@dataclass
class KNXBase:
    """Class with all common knx information."""

    id_str: str
    name: str


@dataclass
class KNXAddress(KNXBase):
    """KNXBase w/ address."""

    address: int


class FinderXml:
    """Create a namespaced xml findall."""

    def __init__(self, namespace=""):
        """Initialize Find function."""
        assert (namespace in PROJECT_NAMESPACES.keys()) or (namespace == "")
        self.namespace = namespace

    def __call__(
        self, xml: ET.Element, keyword: str, expected_count: Optional[int] = None
    ):
        """Find all elements in an xml.

        If an expected count is given iit is asserted that exaclty n elements are found.

        If expected count == 1, only that element is returned, no list.
        """
        # Adapt to namespace
        if self.namespace:
            keyword_ns = f"{self.namespace}:{keyword}"
        else:
            keyword_ns = keyword

        # Find all items
        items = xml.findall(keyword_ns, namespaces=PROJECT_NAMESPACES)
        if expected_count:
            assert len(items) == expected_count

        if expected_count == 1:
            return items[0]

        return items
