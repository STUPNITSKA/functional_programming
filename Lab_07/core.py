from collections.abc import Callable, Iterable, Iterator
from functools import partial, reduce
from operator import add, attrgetter, itemgetter, methodcaller
from pathlib import Path
from typing import Any, TypeVar

from loaders import Records, load_shipments
from models import (
    PRIORITY_FACTOR,
    PRIORITY_LEVEL,
    PricedShipment,
    Shipment,
    ShipmentRank,
)

T = TypeVar("T")
U = TypeVar("U")

get_id = itemgetter("id")
get_weight = itemgetter("weight")
get_distance = itemgetter("distance")
get_priority = itemgetter("priority")
get_cost = itemgetter("cost")
strip = methodcaller("strip")
lower = methodcaller("lower")


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Пропускає значення через функції зліва направо."""
    return reduce(lambda acc, f: f(acc), funcs, value)


def mapf(fn: Callable[[T], U]) -> Callable[[Iterable[T]], Iterator[U]]:
    return partial(map, fn)


def filt(pred: Callable[[T], bool]) -> Callable[[Iterable[T]], Iterator[T]]:
    return partial(filter, pred)


def top_n(n: int) -> Callable[[Iterable[T]], list[T]]:
    if n < 0:
        raise ValueError("n must be non-negative")
    return lambda it: list(it)[:n]


def normalize(row: dict[str, Any]) -> Shipment:
    """Приводить сирий запис до типів і нормалізує пріоритет."""
    priority = lower(strip(str(get_priority(row))))
    if priority not in PRIORITY_LEVEL:
        raise ValueError(f"Unknown priority: {priority!r}")
    return {
        "id": int(get_id(row)),
        "weight": float(get_weight(row)),
        "distance": float(get_distance(row)),
        "priority": priority,
        "cost": float(get_cost(row)),
    }


def with_adjusted_cost(
    shipment: Shipment, *, per_kg: float, per_km: float
) -> PricedShipment:
    """(cost + weight * per_kg + distance * per_km) * коефіцієнт пріоритету."""
    base = (
        shipment["cost"] + shipment["weight"] * per_kg + shipment["distance"] * per_km
    )
    adjusted = round(base * PRIORITY_FACTOR[shipment["priority"]], 2)
    return {**shipment, "adjusted_cost": adjusted}


def has_priority(shipment: Shipment, *, allowed: frozenset[str]) -> bool:
    return shipment["priority"] in allowed


def to_rank(shipment: PricedShipment) -> ShipmentRank:
    return ShipmentRank(shipment["id"], shipment["priority"], shipment["adjusted_cost"])


def total_cost(ranks: Iterable[ShipmentRank]) -> float:
    """Загальна скоригована вартість через reduce."""
    return round(reduce(add, map(attrgetter("adjusted_cost"), ranks), 0.0), 2)


def rank_shipments(
    src: str | Path | Records,
    *,
    priorities: Iterable[str] = ("high", "medium"),
    per_kg: float = 2.0,
    per_km: float = 0.5,
) -> list[ShipmentRank]:
    """Усі відібрані відправлення від найдорожчого до найдешевшого."""
    result: list[ShipmentRank] = pipeline(
        load_shipments(src),
        mapf(normalize),
        mapf(partial(with_adjusted_cost, per_kg=per_kg, per_km=per_km)),
        filt(partial(has_priority, allowed=frozenset(priorities))),
        mapf(to_rank),
        partial(sorted, reverse=True),
    )
    return result


def clean_and_rank(
    src: str | Path | Records,
    top: int = 3,
    *,
    priorities: Iterable[str] = ("high", "medium"),
    per_kg: float = 2.0,
    per_km: float = 0.5,
) -> list[ShipmentRank]:
    """Top-N відправлень за скоригованою вартістю."""
    ranks = rank_shipments(src, priorities=priorities, per_kg=per_kg, per_km=per_km)
    result: list[ShipmentRank] = pipeline(ranks, top_n(top))
    return result
