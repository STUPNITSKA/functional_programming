from typing import Any

from core import add_label, add_reading, make_sensor, update_config
from model import Sensor

ROUNDS = 20_000


def run_mutable() -> dict[str, Any]:
    sensor: dict[str, Any] = {}
    for i in range(ROUNDS):
        sensor = {
            "id": "temp-1",
            "readings": [],
            "labels": set(),
            "config": {"unit": "C", "interval": 60},
        }
        sensor["readings"].append((1, float(i)))
        sensor["readings"].append((2, float(i) + 1))
        sensor["labels"].add("critical")
        sensor["config"]["interval"] = 30
    return sensor


def run_immutable() -> Sensor:
    sensor = make_sensor("temp-1", "temperature", {"unit": "C", "interval": 60})
    for i in range(ROUNDS):
        sensor = make_sensor("temp-1", "temperature", {"unit": "C", "interval": 60})
        sensor = add_reading(sensor, 1, float(i))
        sensor = add_reading(sensor, 2, float(i) + 1)
        sensor = add_label(sensor, "critical")
        sensor = update_config(sensor, interval=30)
    return sensor


def test_mutable_model_operations() -> None:
    sensor = run_mutable()

    assert len(sensor["readings"]) == 2
    assert sensor["config"]["interval"] == 30


def test_immutable_model_operations() -> None:
    sensor = run_immutable()

    assert len(sensor.readings) == 2
    assert sensor.config["interval"] == 30
