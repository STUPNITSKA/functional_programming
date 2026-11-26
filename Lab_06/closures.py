import random
from collections.abc import Callable

DelayPolicy = Callable[[int], float]


def make_counter(start: int = 0) -> Callable[[], int]:
    """Повертає лічильник, який пам'ятає своє значення між викликами."""
    value = start

    def inc() -> int:
        nonlocal value
        value += 1
        return value

    return inc


def make_logger(
    prefix: str, sink: Callable[[str], None] = print
) -> Callable[[str], None]:
    """Повертає логер, який додає префікс до кожного повідомлення."""

    def log(msg: str) -> None:
        sink(f"[{prefix}] {msg}")

    return log


def fixed_delay(delay: float) -> DelayPolicy:
    """Політика з однаковою затримкою перед кожною повторною спробою."""
    if delay < 0:
        raise ValueError("delay must be non-negative")

    def policy(attempt: int) -> float:
        return delay

    return policy


def exponential_backoff(
    base: float,
    factor: float = 2.0,
    *,
    max_delay: float | None = None,
    jitter: float = 0.0,
    rand: Callable[[], float] = random.random,
) -> DelayPolicy:
    """Політика base * factor ** (attempt - 1) з верхньою межею та джитером."""
    if base < 0 or jitter < 0:
        raise ValueError("base and jitter must be non-negative")
    if factor < 1:
        raise ValueError("factor must be at least 1")

    def policy(attempt: int) -> float:
        wait = base * factor ** (attempt - 1)
        if max_delay is not None:
            wait = min(wait, max_delay)
        if jitter:
            wait += rand() * jitter
        return wait

    return policy
