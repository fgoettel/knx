"""Provide the base attributes of an KNX element."""
# pylint: disable=unsubscriptable-object  # Optional

import xml.etree.ElementTree as ET
from dataclasses import dataclass

# Project namespaces, currently supported:
#  - ETS 5.7
#  - Gira GPA (April 2020)
PROJECT_NAMESPACES = {
    "ets56": "http://knx.org/xml/project/14",
    "ets57": "http://knx.org/xml/project/20",
    "gpa": "http://service.schema.gira.de/configuration",
}


def postfix(text: str, postfix_: str = "_") -> str:
    """
    Add a postfix `p` to the given text.

    Args:
    ----
        text: the first part
        postfix_: the second part

    Returns:
    -------
        A concatenated string.

    """
    return f"{text}{postfix_}"


@dataclass
class KNXAddress:
    """
    KNXAddress with id, name, and address.

    Used as a base for topology items and groupaddresses.
    """

    id_str: str
    name: str
    address: int


class FinderXml:
    """Create a namespaced xml findall."""

    def __init__(self, namespace: str | None = None) -> None:
        """
        Initialize the namespace for the findall function.

        Args:
        ----
            namespace:
                The namespace of the xml for this findall install.
                Must be contained in `PROJECT_NAMESPACES`.

        Raises:
        ------
            ValueError: If an unsupported version / namespace is used.

        """
        if namespace and namespace not in PROJECT_NAMESPACES:
            msg = f"Unsupported namespace (probably Version): {namespace}."
            raise ValueError(msg)

        self.namespace = namespace

    def findall(self, xml: ET.Element, keyword: str) -> list[ET.Element]:
        """
        Find all elements in an xml.

        Args:
        ----
            xml: The document that should be searched. Given as an xml element.
            keyword: The keyword of interest.

        Returns:
        -------
            list of items that have been found.

        """
        # Adapt to namespace
        keyword_ns = f"{self.namespace}:{keyword}" if self.namespace else keyword

        # Find all items
        return xml.findall(keyword_ns, namespaces=PROJECT_NAMESPACES)
