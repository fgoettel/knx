"""Classes and helpers to handle KNX groupaddresses."""

import logging
from dataclasses import dataclass
from xml.etree.ElementTree import Element as xml_element

from .util import KNXAddress, postfix


@dataclass
class GroupAddress(KNXAddress):
    """
    KNX Group Address.

    Warnings:
    --------
    Assumes we're living in the "3-stufig-world".

    """

    dtype: str

    @property
    def main(self) -> int:
        """
        Return the main group.

        Returns
        -------
            The main group.

        """
        bitmask = 0b1111100000000000
        shift = 11
        return (self.address & bitmask) >> shift

    @property
    def middle(self) -> int:
        """
        Return the middle group.

        Returns
        -------
            The middle group.

        """
        bitmask = 0b0000011100000000
        shift = 8
        return (self.address & bitmask) >> shift

    @property
    def sub(self) -> int:
        """
        Return the sub group.

        Returns
        -------
            The sub group.

        """
        bitmask = 0b11111111
        return self.address & bitmask

    def get_ga_str(self) -> str:
        """
        Create a/b/c groupaddress out of the integer.

        Returns
        -------
            A string representation of the GA.

        """
        return f"{self.main}/{self.middle}/{self.sub}"

    def almost_equal(self, other: "GroupAddress") -> bool:
        """
        Compare two group addresses.

        Returns true if
          * both are of same type
          * both addresses are identical
          * both dtypes are the same group
          * One name is a subset of the other name

        Args:
        ----
            other: The GA to compare with.

        Returns:
        -------
            Boolean to indicate almost equalness.

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
        """
        Concatenate ga, name and dtype.

        Returns
        -------
            A readable representation of the GA.

        """
        return f"{self.get_ga_str()}: {self.name}, {self.dtype}"  # pragma: no cover


class Factory:
    """Factory to create `GroupAdress`items from a xml."""

    def __init__(self, prefix: str) -> None:
        """
        Create factory.

        Args:
        ----
            prefix: The project prefix.

        """
        self.prefix = postfix(prefix)

    def groupaddress(self, xml: xml_element) -> GroupAddress:
        """
        Create a group adress from a xml.

        Args:
        ----
            xml: The xml element containing the group address information.

        Returns:
        -------
            A configured group adress.

        Raises:
        ------
            KeyError: in case a datapoint has no type assigned.

        """
        try:
            dtype = xml.attrib["DatapointType"]
        except KeyError:
            logging.exception("All Datapoints need an assigned DatapointType.")
            logging.exception("'%s' has no dtype.", xml.attrib["Name"])
            raise

        return GroupAddress(
            id_str=xml.attrib["Id"].replace(self.prefix, ""),
            address=int(xml.attrib["Address"]),
            name=xml.attrib["Name"],
            dtype=dtype,
        )
