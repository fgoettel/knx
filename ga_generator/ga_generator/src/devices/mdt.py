"""MDT devices."""

from xknx.dpt import DPTBool
from pydantic import BaseModel

from ga_generator.src.devices.common import HALight, GroupAddress


class AKD040102(BaseModel):
    """AKD dimmer."""

    ha: list[HALight]

    channels: int = 4

    def __init__(self, name: str) -> None:

        # HA entities
        self.ha = []
        # TODO: ensure that gas for all channels are created
        for idx, name in enumerate(("flur", "bad", "wc"), start=1):
            self.ha.append(HALight(
                name=name,
                idx=idx,

            ))

        # Special Addresses
        #status_ga = GroupAddress(name="day_night", dtype=DPTBool)
