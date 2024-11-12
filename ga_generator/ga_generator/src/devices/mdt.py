"""MDT devices."""

from ga_generator.src.devices.common import Dimmer, Dtype, GroupAddress


class AKD040102(Dimmer):
    """AKD dimmer."""

    def __init__(self, name: str) -> None:
        super().__init__(name=name, channels=4)

        status_ga = GroupAddress(name="status", dtype=Dtype.bar)
        self.ga.append(status_ga)
