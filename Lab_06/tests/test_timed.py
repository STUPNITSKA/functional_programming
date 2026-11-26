import inspect
from collections.abc import Callable
from typing import Literal

import pytest

from decorators import timed


def fake_clock(*ticks: float) -> Callable[[], float]:
    values = list(ticks)
    return lambda: values.pop(0)


def test_timed_uses_clock_and_logger() -> None:
    logs: list[str] = []

    @timed("work", unit="ms", logger=logs.append, clock=fake_clock(0.0, 0.012345))
    def work(x: int) -> int:
        return x * x

    assert work(5) == 25
    assert logs == ["[timed] work took 12.345 ms"]


@pytest.mark.parametrize(
    ("unit", "expected"),
    [("s", "1.500 s"), ("ms", "1500.000 ms"), ("us", "1500000.000 us")],
)
def test_units(unit: Literal["s", "ms", "us"], expected: str) -> None:
    logs: list[str] = []

    @timed(unit=unit, logger=logs.append, clock=fake_clock(2.0, 3.5))
    def job() -> None:
        return None

    job()
    assert logs == [f"[timed] job took {expected}"]


def test_timed_logs_even_on_exception() -> None:
    logs: list[str] = []

    @timed("bad", logger=logs.append, clock=fake_clock(1.0, 1.002))
    def bad() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        bad()
    assert logs == ["[timed] bad took 2.000 ms"]


def test_timed_keeps_metadata() -> None:
    def work(x: int) -> int:
        """Квадрат числа."""
        return x * x

    decorated = timed(logger=lambda _: None)(work)
    assert decorated.__name__ == "work"
    assert decorated.__doc__ == "Квадрат числа."
    assert vars(decorated)["__wrapped__"] is work
    assert inspect.signature(decorated) == inspect.signature(work)
