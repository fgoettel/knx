"""Classes and helpers related to the KNX topology."""

import logging
from dataclasses import dataclass, field
from typing import List, Tuple
from xml.etree.ElementTree import Element

from .util import KNXAddress, postfix

DEFAULT_ADDR = 99


@dataclass
class Area(KNXAddress):
    """KNX Area."""


@dataclass
class Line(KNXAddress):
    """KNX Linie."""

    area: Area
    medium: str


@dataclass
class Device(KNXAddress):
    """Generic type for devices."""

    product_id: str
    line: Line
    groupaddress_list: list = field(default_factory=list)
    other: dict = field(default_factory=dict)


class Factory:
    """Factory to create items from xml."""

    def __init__(self, finder, prefix):
        """Create factory."""
        self.finder = finder
        self.prefix = postfix(prefix)

    def _find_id(self, xml: Element) -> str:
        """Find and format the ID."""
        return xml.attrib["Id"].replace(self.prefix, "")

    def _find_connections(self, xml: Element) -> Tuple[List[str], List[str]]:
        """Find group addresses from a xml element."""
        # TODO: Combine connection information
        # TODO: Refactor to refelct the text part
        groupaddress_list: List[str] = []
        text_list: List[str] = []

        # Find top level references
        comobjs_xml = self.finder(xml, "ComObjectInstanceRefs")
        if not comobjs_xml:
            logging.info("%s has no references.", xml)
            return groupaddress_list, text_list

        # Find each single connected ga
        for ccc in self.finder(comobjs_xml[0], "ComObjectInstanceRef"):
            ga_new = ccc.attrib.get("Links", None)
            if ga_new:
                groupaddress_list.extend(ga_new.split(" "))

            txt_new = ccc.attrib.get("Text", None)
            if txt_new:
                text_list.append(txt_new)

        return groupaddress_list, text_list

    def device(self, xml: Element, line: Line) -> Device:
        """Create a device from a xml."""
        # TODO: clean up
        gas, texts = self._find_connections(xml)

        return Device(
            id_str=self._find_id(xml),
            name=xml.attrib["Name"],
            address=int(xml.attrib.get("Address", DEFAULT_ADDR)),
            product_id=xml.attrib["ProductRefId"],
            groupaddress_list=gas,
            line=line,
            other={"texts": texts},
        )

    def line(self, xml: Element, area: Area) -> Line:
        """Create a line from a xml."""
        return Line(
            id_str=self._find_id(xml),
            area=area,
            name=xml.attrib["Name"],
            address=int(xml.attrib["Address"]),
            medium=xml.attrib["MediumTypeRefId"],
        )

    def area(self, xml: Element) -> Area:
        """Create an area from a xml."""
        return Area(
            id_str=self._find_id(xml),
            name=xml.attrib["Name"],
            address=int(xml.attrib["Address"]),
        )
