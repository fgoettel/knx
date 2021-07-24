"""Generic device types."""
from dataclasses import dataclass

from ..topology import Device

# pylint: disable=useless-super-delegation


@dataclass
class Switch(Device):
    """Abstract switch class."""

    def __init__(self, *args, **kwargs):
        """Create a switch."""
        super().__init__(*args, **kwargs)

    width = 50
    vsep = "|"
    hsep = "-"
    border = "="

    @classmethod
    def from_device(cls, device, *args, **kwargs):
        """Create a switch from a generic device."""

    def doc(self):
        """Print documentation."""
