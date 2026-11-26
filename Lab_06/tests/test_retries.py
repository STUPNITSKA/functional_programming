from collections.abc import Callable

import pytest

from closures import exponential_backoff, fixed_delay, make_counter
from decorators import retries, timed


def flaky(
    fail_times: int, error: type[Exception] = ConnectionError
) -> Callable[[], str]:
    calls = make_counter()

    def task() -> str:
        if calls() <= fail_times:
            raise error("boom")
        return "ok"

    return task


def test_success_on_third_attempt_without_real_sleep() -> None:
    slept: list[float] = []
    calls = {"n": 0}

    @retries(attempts=3, delay=0, sleep=slept.append)
    def task() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert task() == "ok"
    assert calls["n"] == 3
    assert slept == [0, 0]


def test_fixed_policy() -> None:
    slept: list[float] = []
    task = retries(5, (ConnectionError,), policy=fixed_delay(0.5), sleep=slept.append)(
        flaky(3)
    )
    assert task() == "ok"
    assert slept == [0.5, 0.5, 0.5]


def test_exponential_policy() -> None:
    slept: list[float] = []
    policy = exponential_backoff(0.1, 2.0)
    task = retries(5, (ConnectionError,), policy=policy, sleep=slept.append)(flaky(4))
    assert task() == "ok"
    assert slept == pytest.approx([0.1, 0.2, 0.4, 0.8])


def test_delay_and_backoff_without_policy() -> None:
    slept: list[float] = []
    task = retries(4, delay=1.0, backoff=3.0, sleep=slept.append)(flaky(3))
    assert task() == "ok"
    assert slept == [1.0, 3.0, 9.0]


def test_fail_after_all_attempts() -> None:
    slept: list[float] = []
    logs: list[str] = []
    task = retries(3, delay=0.2, sleep=slept.append, logger=logs.append)(flaky(10))
    with pytest.raises(ConnectionError, match="boom"):
        task()
    assert slept == [0.2, 0.2]
    assert len(logs) == 3
    assert logs[-1] == "[retries] fail after 3 attempts: ConnectionError('boom')"


def test_other_exceptions_are_not_retried() -> None:
    slept: list[float] = []
    task = retries(5, (ConnectionError,), sleep=slept.append)(flaky(1, ValueError))
    with pytest.raises(ValueError):
        task()
    assert slept == []


def test_single_attempt() -> None:
    slept: list[float] = []
    task = retries(1, sleep=slept.append)(flaky(1))
    with pytest.raises(ConnectionError):
        task()
    assert slept == []


def test_attempts_must_be_positive() -> None:
    with pytest.raises(ValueError):
        retries(0)


def test_logger_messages() -> None:
    logs: list[str] = []
    task = retries(
        3, policy=fixed_delay(0.25), sleep=lambda _: None, logger=logs.append
    )(flaky(1))
    assert task() == "ok"
    assert logs == [
        "[retries] attempt 1 failed: ConnectionError('boom'); sleeping 0.250s"
    ]


def test_retries_keeps_metadata() -> None:
    def job(x: int) -> int:
        """Подвоєння."""
        return 2 * x

    decorated = retries(2, sleep=lambda _: None)(job)
    assert decorated(4) == 8
    assert decorated.__name__ == "job"
    assert decorated.__doc__ == "Подвоєння."
    assert vars(decorated)["__wrapped__"] is job


def test_timed_over_retries() -> None:
    slept: list[float] = []
    logs: list[str] = []
    ticks = iter([0.0, 0.5])

    @timed("task", unit="s", logger=logs.append, clock=lambda: next(ticks))
    @retries(3, policy=exponential_backoff(0.1, 2.0), sleep=slept.append)
    def task() -> str:
        return job()

    job = flaky(2)
    assert task() == "ok"
    assert slept == pytest.approx([0.1, 0.2])
    assert logs == ["[timed] task took 0.500 s"]
