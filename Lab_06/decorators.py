import functools
import threading
import time
from collections.abc import Callable, Hashable
from typing import Any, Literal, ParamSpec, Protocol, TypeVar, cast

from closures import DelayPolicy, exponential_backoff

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)

KeyPredicate = Callable[[tuple[Any, ...], dict[str, Any]], bool]


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Логує час виконання функції, навіть якщо вона кинула виняток."""
    factor = {"s": 1.0, "ms": 1e3, "us": 1e6}[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = clock()
            try:
                return func(*args, **kwargs)
            finally:
                dt = (clock() - t0) * factor
                logger(f"[timed] {name} took {dt:.3f} {unit}")

        return wrapper

    return decorator


def retries(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    *,
    policy: DelayPolicy | None = None,
    sleep: Callable[[float], None] = time.sleep,
    logger: Callable[[str], None] = lambda _: None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Повторює виклик при вказаних винятках із затримкою за політикою.

    Якщо policy не передано, затримка рахується як
    delay * backoff ** (i - 1) + джитер.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    wait_for = policy or exponential_backoff(delay, backoff, jitter=jitter)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == attempts:
                        logger(f"[retries] fail after {i} attempts: {e!r}")
                        raise
                    wait = wait_for(i)
                    logger(f"[retries] attempt {i} failed: {e!r}; sleeping {wait:.3f}s")
                    sleep(wait)
            raise AssertionError("unreachable")

        return wrapper

    return decorator


class CachedFunction(Protocol[P, R_co]):
    """Функція з кешем і методами очищення на обгортці."""

    __name__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def cache_clear(self) -> None: ...

    def cache_invalidate(self, predicate: KeyPredicate) -> int: ...


def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Hashable:
    """Ключ кешу з позиційних та іменованих аргументів."""
    return (args, tuple(sorted(kwargs.items())))


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
) -> Callable[[Callable[P, R]], CachedFunction[P, R]]:
    """Кешує результати з TTL; ttl=None означає безстроково."""

    def decorator(func: Callable[P, R]) -> CachedFunction[P, R]:
        cache: dict[Hashable, tuple[float | None, R]] = {}
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = make_key(args, kwargs)
            now = time_fn()
            with lock:
                if key in cache:
                    expiry, value = cache[key]
                    if expiry is None or now < expiry:
                        return value
                    del cache[key]
            value = func(*args, **kwargs)
            with lock:
                cache[key] = (None if ttl is None else now + ttl, value)
            return value

        def cache_clear() -> None:
            with lock:
                cache.clear()

        def cache_invalidate(predicate: KeyPredicate) -> int:
            removed = 0
            with lock:
                for key in list(cache):
                    args_k, kwargs_k = cast(tuple[Any, Any], key)
                    if predicate(args_k, dict(kwargs_k)):
                        del cache[key]
                        removed += 1
            return removed

        setattr(wrapper, "cache_clear", cache_clear)
        setattr(wrapper, "cache_invalidate", cache_invalidate)
        return cast(CachedFunction[P, R], wrapper)

    return decorator
