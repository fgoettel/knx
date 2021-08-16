"""Module that defines vendor specific devices.

This is highly experimental.
"""


from typing import List

from projects.topology import Device

from . import mdt


def dev2vendor(device: Device, project_ga_list: List):
    """Create vendor device from the generic device."""
    if "GT2" in device.product_id:
        return mdt.GT2.from_device(device, texts=device.other["texts"])
    if "BE.2D04001" in device.product_id:
        return mdt.BE4.from_device(device, project_ga_list=project_ga_list)
    return device
