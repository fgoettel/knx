"""Provide the base attributes of an KNX element."""
# pylint: disable=unsubscriptable-object  # Optional

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional

# Project namespaces, currently supported:
#  - ETS 5.7
#  - Gira GPA (April 2020)
PROJECT_NAMESPACES = {
    "ets56": "http://knx.org/xml/project/14",
    "ets57": "http://knx.org/xml/project/20",
    "gpa": "http://service.schema.gira.de/configuration",
}


def postfix(prefix: str, sep: str = "_") -> str:
    """Add a postfix, default to '_' to the given prefix."""
    return "".join((prefix, sep))


@dataclass
class KNXAddress:
    """KNXAddress with id, name, and address.

    Used as a base for topology items and groupaddresses.
    """

    id_str: str
    name: str
    address: int


class FinderXml:
    """Create a namespaced xml findall."""

    def __init__(self, namespace: Optional[str] = None) -> None:
        """Initialize the namespace for the findall function."""
        assert (namespace in PROJECT_NAMESPACES.keys()) or (namespace is None)
        self.namespace = namespace

    def findall(self, xml: ET.Element, keyword: str) -> List:
        """Find all elements in an xml.

        If an expected count `n` is given it is asserted that exaclty `n` elements are found.

        Parameters
        ----------
        xml
            The document that should be searched. Given as an xml element.

        keyword
            The keyword of interest.

        Returns
        -------
        items
            list of items that have been found.

        """
        # Adapt to namespace
        if self.namespace:
            keyword_ns = f"{self.namespace}:{keyword}"
        else:
            keyword_ns = keyword

        # Find all items
        return xml.findall(keyword_ns, namespaces=PROJECT_NAMESPACES)
