from collections.abc import Iterable, Mapping
from dataclasses import replace
from types import MappingProxyType

from model import ConfigValue, Reading, Sensor


def make_config(source: Mapping[str, ConfigValue]) -> Mapping[str, ConfigValue]:
    return MappingProxyType(dict(source))


def make_sensor(
    sensor_id: str,
    kind: str,
    config: Mapping[str, ConfigValue],
    labels: Iterable[str] = (),
) -> Sensor:
    return Sensor(
        id=sensor_id,
        kind=kind,
        readings=(),
        labels=frozenset(labels),
        config=make_config(config),
    )


def add_reading(sensor: Sensor, timestamp: int, value: float) -> Sensor:
    return replace(sensor, readings=sensor.readings + (Reading(timestamp, value),))


def add_label(sensor: Sensor, label: str) -> Sensor:
    return replace(sensor, labels=sensor.labels | frozenset({label}))


def update_config(sensor: Sensor, **changes: ConfigValue) -> Sensor:
    return replace(sensor, config=make_config({**sensor.config, **changes}))


def top_by_average(sensors: Iterable[Sensor], n: int) -> tuple[Sensor, ...]:
    ranked = sorted(sensors, key=lambda s: (-s.average(), s.id))
    return tuple(ranked[:n])


def freeze(obj: object) -> object:
    if isinstance(obj, Mapping):
        return MappingProxyType({key: freeze(value) for key, value in obj.items()})
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(item) for item in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(item) for item in obj)
    return obj
