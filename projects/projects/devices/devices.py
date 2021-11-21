"""Generic device types."""
from abc import ABC, abstractmethod

from projects.topology import Device


class Switch(Device, ABC):
    """Abstract switch class."""

    width = 50
    vsep = "|"
    hsep = "-"
    border = "="

    @classmethod
    @abstractmethod
    def from_device(cls, device: Device, *args, **kwargs):
        """Create a switch from a generic device."""

    @abstractmethod
    def doc(self):
        """Print documentation."""
