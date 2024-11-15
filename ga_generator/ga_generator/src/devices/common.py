"""Base Model and common utilities for devices."""

from abc import ABC
from typing import ClassVar

from pydantic import BaseModel
from xknx.dpt import DPTBase, DPTPercentU8, DPTSwitch
from pydantic import BaseModel, ValidationError, field_validator, computed_field




class GroupAddress(BaseModel):
    """Generic gorup address."""

    # TODO: check if it makes sense to use xknx for the groupaddress validation
    name: str
    dtype: type[DPTBase]


class HALight(BaseModel):
    """Light entity."""

    name: str
    idx: int

    ga_cmd: str = "1/1/"
    ga_state: str = "2/2/"

    idx_offset: int = 2

    @computed_field
    @property
    def address(self) -> GroupAddress:
        name = f"{self.ga_cmd}{self.idx*self.idx_offset+0}"
        return GroupAddress(name=name, dtype=DPTSwitch)

    @computed_field
    @property
    def state_address(self) -> GroupAddress:
        name =f"{self.ga_state}{self.idx*self.idx_offset+0}"
        return GroupAddress(name=name, dtype=DPTSwitch)

    @computed_field
    @property
    def brightness_address(self) -> GroupAddress:
        name = f"{self.ga_cmd}{self.idx*self.idx_offset+0}"
        return GroupAddress(name=name, dtype=DPTPercentU8)

    @computed_field
    @property
    def brightness_state_address(self) -> GroupAddress:
        name = f"{self.ga_state}{self.idx*self.idx_offset+1}"
        return GroupAddress(name=name, dtype=DPTPercentU8)

