import pytest

from decorators import cached, make_key


class FakeTime:
    def __init__(self, now: float) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def test_cached_ttl_and_invalidate() -> None:
    t = FakeTime(1000.0)
    hit = {"n": 0}

    @cached(ttl=1.0, time_fn=t)
    def f(x: int) -> int:
        hit["n"] += 1
        return x * 2

    assert f(10) == 20
    assert f(10) == 20
    assert hit["n"] == 1
    t.now += 2.0
    assert f(10) == 20
    assert hit["n"] == 2
    removed = f.cache_invalidate(lambda a, kw: a == (10,))
    assert removed == 1
    assert f(10) == 20
    assert hit["n"] == 3


def test_ttl_boundary() -> None:
    t = FakeTime(0.0)
    hit = {"n": 0}

    @cached(ttl=5.0, time_fn=t)
    def f(x: int) -> int:
        hit["n"] += 1
        return x

    f(1)
    t.now = 4.999
    f(1)
    assert hit["n"] == 1
    t.now = 5.0
    f(1)
    assert hit["n"] == 2


def test_no_ttl_never_expires() -> None:
    t = FakeTime(0.0)
    hit = {"n": 0}

    @cached(time_fn=t)
    def f(x: int) -> int:
        hit["n"] += 1
        return x

    f(1)
    t.now = 1e9
    f(1)
    assert hit["n"] == 1


def test_cache_clear() -> None:
    hit = {"n": 0}

    @cached()
    def f(x: int) -> int:
        hit["n"] += 1
        return x

    f(1)
    f(2)
    f.cache_clear()
    f(1)
    f(2)
    assert hit["n"] == 4


def test_partial_invalidation_keeps_other_keys() -> None:
    hit: list[int] = []

    @cached()
    def price(product_id: int, currency: str = "UAH") -> int:
        hit.append(product_id)
        return product_id * 10

    price(1)
    price(2)
    price(3, currency="USD")
    assert price.cache_invalidate(lambda a, kw: kw.get("currency") == "USD") == 1
    assert price.cache_invalidate(lambda a, kw: a == (100,)) == 0
    price(1)
    price(2)
    price(3, currency="USD")
    assert hit == [1, 2, 3, 3]


def test_args_and_kwargs_are_different_keys() -> None:
    assert make_key((1,), {}) != make_key((), {"x": 1})
    assert make_key((), {"a": 1, "b": 2}) == make_key((), {"b": 2, "a": 1})


def test_exception_is_not_cached() -> None:
    hit = {"n": 0}

    @cached()
    def f(x: int) -> int:
        hit["n"] += 1
        if hit["n"] == 1:
            raise RuntimeError("boom")
        return x

    with pytest.raises(RuntimeError):
        f(1)
    assert f(1) == 1
    assert hit["n"] == 2


def test_unhashable_argument() -> None:
    @cached()
    def total(items: list[int]) -> int:
        return sum(items)

    with pytest.raises(TypeError):
        total([1, 2])


def test_cached_keeps_metadata() -> None:
    def square(x: int) -> int:
        """Квадрат числа."""
        return x * x

    decorated = cached()(square)
    assert decorated.__name__ == "square"
    assert decorated.__doc__ == "Квадрат числа."
    assert vars(decorated)["__wrapped__"] is square
