from core import add_label, add_reading, make_sensor, top_by_average, update_config
from model import ConfigValue, Sensor


def show(title: str, sensor: Sensor) -> None:
    values = ", ".join(f"{r.value:g}" for r in sensor.readings) or "-"
    print(f"{title}: {sensor.id}")
    print(f"  показники: {values}")
    print(f"  середнє: {sensor.average():.2f}")
    print(f"  мітки: {', '.join(sorted(sensor.labels))}")
    print(f"  конфігурація: {dict(sensor.config)}")


def main() -> None:
    raw_config: dict[str, ConfigValue] = {"unit": "C", "interval": 60}
    sensor = make_sensor("temp-1", "temperature", raw_config, labels={"kitchen"})
    raw_config["interval"] = 1

    updated = add_reading(sensor, 1, 21.5)
    updated = add_reading(updated, 2, 22.5)
    updated = add_label(updated, "critical")
    updated = update_config(updated, interval=30)

    show("Початкова версія", sensor)
    show("Нова версія", updated)
    print("Різні об'єкти:", sensor is not updated)
    print("Обидві версії в множині:", len({sensor, updated}))

    other = add_reading(make_sensor("hum-1", "humidity", {"unit": "%"}), 1, 45.0)
    print("Найбільше середнє:", top_by_average((updated, other), 1)[0].id)


if __name__ == "__main__":
    main()
