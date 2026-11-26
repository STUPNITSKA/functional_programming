import operator
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import accumulate, count, cycle, dropwhile, islice, takewhile
from typing import TypeVar

T = TypeVar("T")


def fib_stream() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def naturals(start: int = 1) -> Iterator[int]:
    yield from count(start)


def take(n: int, it: Iterable[T]) -> list[T]:
    if n < 0:
        raise ValueError("n must be non-negative")
    return list(islice(it, n))


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    if n < 0:
        raise ValueError("n must be non-negative")
    iterator = iter(it)
    next(islice(iterator, n, n), None)
    return iterator


def sliding_window(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    if k <= 0:
        raise ValueError("window size must be positive")
    iterator = iter(it)
    window: deque[T] = deque(islice(iterator, k), maxlen=k)
    if len(window) < k:
        return
    yield tuple(window)
    for item in iterator:
        window.append(item)
        yield tuple(window)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    return (sum(window) / k for window in sliding_window(it, k))


def prefix_sums(it: Iterable[int]) -> Iterator[int]:
    return accumulate(it)


def prefix_products(it: Iterable[int]) -> Iterator[int]:
    return accumulate(it, operator.mul)


def take_while(predicate: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    return takewhile(predicate, it)


def drop_while(predicate: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    return dropwhile(predicate, it)


def window_sums_of_multiples(divisor: int, k: int, n: int) -> list[int]:
    multiples = (x for x in naturals(1) if x % divisor == 0)
    return take(n, map(sum, sliding_window(multiples, k)))


def pattern_stream(pattern: Iterable[T]) -> Iterator[T]:
    yield from cycle(pattern)


def numbered(it: Iterable[T], start: int = 1) -> Iterator[tuple[int, T]]:
    return zip(count(start), it)


def pattern_until(
    pattern: Iterable[T], stop: Callable[[int, T], bool], start: int = 1
) -> Iterator[tuple[int, T]]:
    return takewhile(
        lambda pair: not stop(pair[0], pair[1]),
        numbered(pattern_stream(pattern), start),
    )


def pattern_plan(pattern: Iterable[T], n: int, start: int = 1) -> list[tuple[int, T]]:
    return take(n, numbered(pattern_stream(pattern), start))
