from dataclasses import dataclass
from functools import total_ordering
from operator import attrgetter
from typing import TypedDict

PRIORITY_LEVEL = {"low": 1, "medium": 2, "high": 3}
PRIORITY_FACTOR = {"low": 1.0, "medium": 1.2, "high": 1.5}


class Shipment(TypedDict):
    id: int
    weight: float
    distance: float
    priority: str
    cost: float


class PricedShipment(Shipment):
    adjusted_cost: float


_rank_key = attrgetter("adjusted_cost", "level", "id")


@total_ordering
@dataclass(frozen=True, eq=False)
class ShipmentRank:
    """Місце відправлення в рейтингу: вартість, потім пріоритет, потім id."""

    id: int
    priority: str
    adjusted_cost: float

    @property
    def level(self) -> int:
        return PRIORITY_LEVEL[self.priority]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ShipmentRank):
            return NotImplemented
        return bool(_rank_key(self) == _rank_key(other))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ShipmentRank):
            return NotImplemented
        return bool(_rank_key(self) < _rank_key(other))
