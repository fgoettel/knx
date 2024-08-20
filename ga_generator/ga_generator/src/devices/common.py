"""Base Model and common utilities for devices."""

from abc import ABC
from enum import StrEnum

from pydantic import BaseModel


class Dtype(StrEnum):

    """Generic datatype."""

    # TODO: use xknx
    foo = "FOO"
    bar = "DPT-8"


class GroupAddress(BaseModel):

    """Generic gorup address."""

    # TODO: check if it makes sense to use xknx
    name: str
    dtype: Dtype


class Device(BaseModel, ABC):

    """Generic, abstract device."""

    name: str
    ga: list[GroupAddress] = []
    pa: str = ""


class Dimmer(Device):

    """Generic dimming device."""

    def __init__(self, name: str, channels: int) -> None:
        super().__init__(name=name)
        for idx in range(channels):
            for ga_name, dtype in (("dimm status", Dtype.foo), ("switch status", Dtype.bar)):
                ga = GroupAddress(name=f"Ch{idx} - {ga_name}", dtype=dtype)
                self.ga.append(ga)
