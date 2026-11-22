from collections.abc import Callable

import pytest

from algorithms import fib, fib_iter, fib_naive


def test_fib_small() -> None:
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert [fib(i) for i in range(10)] == expected
    assert [fib_naive(i) for i in range(10)] == expected


def test_fib_iter_matches() -> None:
    for n in range(50):
        assert fib(n) == fib_iter(n)


def test_cache_clear_and_info() -> None:
    fib.cache_clear()
    assert fib.cache_info().currsize == 0
    assert fib(30) == 832040
    info = fib.cache_info()
    assert info.currsize == 31
    assert info.misses == 31
    assert fib(30) == 832040
    assert fib.cache_info().hits == info.hits + 1


@pytest.mark.parametrize("func", [fib, fib_iter, fib_naive])
def test_negative_n_is_rejected(func: Callable[[int], int]) -> None:
    with pytest.raises(ValueError):
        func(-1)
