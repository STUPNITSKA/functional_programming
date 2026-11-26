from collections.abc import Callable

import pytest

from closures import exponential_backoff, fixed_delay, make_counter, make_logger


def test_counter_keeps_state() -> None:
    c = make_counter(10)
    assert c() == 11
    assert c() == 12


def test_counters_are_independent() -> None:
    a = make_counter()
    b = make_counter()
    a()
    a()
    assert a() == 3
    assert b() == 1


def test_logger_uses_prefix_and_sink() -> None:
    lines: list[str] = []
    info = make_logger("INFO", sink=lines.append)
    info("ready")
    assert lines == ["[INFO] ready"]


def test_fixed_delay() -> None:
    policy = fixed_delay(0.5)
    assert [policy(i) for i in range(1, 5)] == [0.5, 0.5, 0.5, 0.5]
    assert fixed_delay(0)(1) == 0


def test_exponential_backoff() -> None:
    policy = exponential_backoff(0.1, 2.0)
    assert [policy(i) for i in range(1, 5)] == pytest.approx([0.1, 0.2, 0.4, 0.8])


def test_exponential_backoff_max_delay() -> None:
    policy = exponential_backoff(1.0, 3.0, max_delay=5.0)
    assert [policy(i) for i in range(1, 5)] == [1.0, 3.0, 5.0, 5.0]


def test_exponential_backoff_jitter_is_deterministic() -> None:
    policy = exponential_backoff(1.0, 2.0, jitter=0.2, rand=lambda: 0.5)
    assert policy(1) == pytest.approx(1.1)
    assert policy(3) == pytest.approx(4.1)


def test_factor_one_gives_fixed_delay() -> None:
    policy = exponential_backoff(0.3, 1.0)
    assert {policy(i) for i in range(1, 6)} == {0.3}


@pytest.mark.parametrize(
    "make",
    [
        lambda: fixed_delay(-1),
        lambda: exponential_backoff(-1),
        lambda: exponential_backoff(1, 0.5),
        lambda: exponential_backoff(1, jitter=-0.1),
    ],
)
def test_bad_policy_parameters(make: Callable[[], object]) -> None:
    with pytest.raises(ValueError):
        make()
