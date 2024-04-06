"""Generic device types."""

from abc import ABC, abstractmethod
from typing import TypeVar

from projects.topology import Device

T = TypeVar("T", bound="Switch")


class Switch(Device, ABC):
    """Abstract switch class."""

    width = 50
    vsep = "|"
    hsep = "-"
    border = "="

    @classmethod
    @abstractmethod
    def from_device(cls: type[T], device: Device, *args, **kwargs) -> T:
        """
        Create a switch from a generic device.

        Args:
        ----
            device: The basic Device to create a swtich from.
            args: Position only arguments.
            kwargs: Keyword arguments.

        """

    @abstractmethod
    def doc(self) -> None:
        """Print documentation."""
