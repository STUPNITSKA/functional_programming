from collections.abc import Mapping
from dataclasses import dataclass, field

ConfigValue = str | int | float


@dataclass(frozen=True, slots=True)
class Reading:
    timestamp: int
    value: float


@dataclass(frozen=True, slots=True)
class Sensor:
    id: str
    kind: str
    readings: tuple[Reading, ...]
    labels: frozenset[str]
    config: Mapping[str, ConfigValue] = field(hash=False)

    def average(self) -> float:
        if not self.readings:
            return 0.0
        return sum(r.value for r in self.readings) / len(self.readings)
