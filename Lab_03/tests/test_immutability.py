from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from core import (
    add_label,
    add_reading,
    freeze,
    make_config,
    make_sensor,
    top_by_average,
    update_config,
)
from model import Reading, Sensor


@pytest.fixture
def sensor() -> Sensor:
    base = make_sensor("temp-1", "temperature", {"unit": "C", "interval": 60}, {"lab"})
    return add_reading(base, 1, 20.0)


def test_add_reading_returns_new_sensor(sensor: Sensor) -> None:
    before = replace(sensor)

    updated = add_reading(sensor, 2, 24.0)

    assert updated is not sensor
    assert sensor == before
    assert sensor.readings == (Reading(1, 20.0),)
    assert updated.readings == (Reading(1, 20.0), Reading(2, 24.0))
    assert updated.average() == 22.0


def test_add_label_keeps_old_labels(sensor: Sensor) -> None:
    updated = add_label(sensor, "critical")

    assert sensor.labels == frozenset({"lab"})
    assert updated.labels == frozenset({"lab", "critical"})
    assert add_label(updated, "critical").labels == updated.labels


def test_update_config_creates_new_mapping(sensor: Sensor) -> None:
    updated = update_config(sensor, interval=30, mode="fast")

    assert sensor.config == {"unit": "C", "interval": 60}
    assert updated.config == {"unit": "C", "interval": 30, "mode": "fast"}
    assert updated.config is not sensor.config


def test_config_is_read_only(sensor: Sensor) -> None:
    assert isinstance(sensor.config, MappingProxyType)
    with pytest.raises(TypeError):
        sensor.config["unit"] = "F"  # type: ignore[index]


def test_make_config_copies_source() -> None:
    source: dict[str, str | int | float] = {"unit": "C"}
    config = make_config(source)

    source["unit"] = "F"

    assert config["unit"] == "C"


def test_fields_cannot_be_changed(sensor: Sensor) -> None:
    with pytest.raises(FrozenInstanceError):
        sensor.kind = "humidity"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        sensor.readings[0].value = 0.0  # type: ignore[misc]


def test_readings_and_labels_are_immutable_types(sensor: Sensor) -> None:
    assert isinstance(sensor.readings, tuple)
    assert isinstance(sensor.labels, frozenset)


def test_sensor_and_reading_are_hashable(sensor: Sensor) -> None:
    updated = add_label(sensor, "critical")

    assert len({sensor, updated, replace(sensor)}) == 2
    assert {Reading(1, 20.0): "first"}[Reading(1, 20.0)] == "first"


def test_config_is_not_part_of_hash(sensor: Sensor) -> None:
    changed = update_config(sensor, interval=5)

    assert hash(changed) == hash(sensor)
    assert changed != sensor


def test_top_by_average_returns_tuple(sensor: Sensor) -> None:
    other = add_reading(make_sensor("hum-1", "humidity", {"unit": "%"}), 1, 45.0)
    same = add_reading(make_sensor("abc", "temperature", {}), 1, 20.0)

    result = top_by_average([sensor, other, same], 2)

    assert isinstance(result, tuple)
    assert [s.id for s in result] == ["hum-1", "abc"]


def test_average_of_empty_sensor() -> None:
    assert make_sensor("x", "temperature", {}).average() == 0.0


def test_freeze_nested_structures() -> None:
    limits = [1, 2]
    raw = {"limits": limits, "tags": {"a"}, "inner": {"k": [3]}}

    frozen = freeze(raw)
    limits.append(5)

    assert isinstance(frozen, MappingProxyType)
    assert isinstance(frozen["inner"], MappingProxyType)
    assert frozen["limits"] == (1, 2)
    assert frozen["tags"] == frozenset({"a"})
    assert frozen["inner"]["k"] == (3,)
