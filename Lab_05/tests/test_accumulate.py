import operator
from itertools import accumulate

from streams import (
    drop_while,
    fib_stream,
    naturals,
    prefix_products,
    prefix_sums,
    take,
    take_while,
    window_sums_of_multiples,
)


def test_accumulate_sum_prod() -> None:
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(accumulate([1, 2, 3, 4], operator.mul)) == [1, 2, 6, 24]
    assert list(accumulate([3, 1, 4, 1, 5], max)) == [3, 3, 4, 4, 5]


def test_prefix_wrappers() -> None:
    assert list(prefix_sums([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(prefix_products([1, 2, 3, 4])) == [1, 2, 6, 24]
    assert list(prefix_sums([])) == []
    assert take(4, prefix_sums(naturals(1))) == [1, 3, 6, 10]


def test_take_while_and_drop_while() -> None:
    expected = [0, 1, 1, 2, 3, 5, 8, 13]
    assert list(take_while(lambda x: x < 20, fib_stream())) == expected
    assert list(drop_while(lambda x: x <= 0, [-2, 0, 3, -1, 4])) == [3, -1, 4]


def test_multiples_pipeline() -> None:
    assert window_sums_of_multiples(3, 4, 3) == [30, 42, 54]
    assert window_sums_of_multiples(3, 4, 0) == []
