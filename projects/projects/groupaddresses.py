"""Classes and helpers to handle KNX groupaddresses."""

import logging
from dataclasses import dataclass
from xml.etree.ElementTree import Element as xml_element

from .util import KNXAddress, postfix


@dataclass
class GroupAddress(KNXAddress):
    """KNX Group Address.

    Warnings
    --------
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

    def almost_equal(self, other: "GroupAddress") -> bool:
        """Compare two group addresses.

        Returns true if
          * both are of same type
          * both addresses are identical
          * both dtypes are the same group
          * One name is a subset of the other name
        """

        # Equal items
        if not isinstance(other, type(self)):
            return False
        if self.address != other.address:
            return False

        # Dtypes don't need to be exactly equal, just the "main" type
        if self.dtype.split("-")[:2] != other.dtype.split("-")[:2]:
            return False

        # Name is almost equal
        return (self.name in other.name) or (self.name in other.name)

    def __str__(self) -> str:
        """Concatenate ga, name and dtype."""
        return f"{self.get_ga_str()}: {self.name}, {self.dtype}"  # pragma: no cover


class Factory:
    """Factory to create `GroupAdress`items from a xml."""

    def __init__(self, prefix: str) -> None:
        """Create factory.

        Parameters
        ----------
        prefix
            The project prefix.

        """
        self.prefix = postfix(prefix)

    def groupaddress(self, xml: xml_element) -> GroupAddress:
        """Create a group adress from a xml.

        Parameters
        ----------
        xml
            The xml element containing the group address information.

        Returns
        -------
        group_adress
            A configured group adress.

        """
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
