"""Classes and helpers to handle KNX groupaddresses."""

import logging
from dataclasses import dataclass
from xml.etree.ElementTree import Element as xml_element

from .util import KNXAddress, postfix


@dataclass
class GroupAddress(KNXAddress):
    """KNX GA.

    Assumes we're living in the "3-stufig-world".
    """

    dtype: str

    @property
    def main(self) -> int:
        """Return the main group."""
        bitmask = 0b1111100000000000
        shift = 11
        return (self.address & bitmask) >> shift

    @property
    def middle(self) -> int:
        """Return the middle group."""
        bitmask = 0b0000011100000000
        shift = 8
        return (self.address & bitmask) >> shift

    @property
    def sub(self) -> int:
        """Return the sub group."""
        bitmask = 0b11111111
        return self.address & bitmask

    def get_ga_str(self) -> str:
        """Create a/b/c groupaddress out of the integer."""
        return "/".join((f"{self.main}", f"{self.middle}", f"{self.sub}"))


class Factory:
    """Factory to create items from xml."""

    def __init__(self, prefix):
        """Create factory."""
        self.prefix = postfix(prefix)

    def groupaddress(self, xml: xml_element) -> GroupAddress:
        """Create a group adress from a xml."""
        try:
            dtype = xml.attrib["DatapointType"]
        except KeyError:
            logging.error("All Datapoints need an assigned DatapointType.")
            logging.error("'%s' has no dtype.", xml.attrib["Name"])
            raise

        return GroupAddress(
            id_str=xml.attrib["Id"].replace(self.prefix, ""),
            address=int(xml.attrib["Address"]),
            name=xml.attrib["Name"],
            dtype=dtype,
        )
