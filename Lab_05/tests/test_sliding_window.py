from collections.abc import Iterator
from itertools import count

import pytest

from streams import moving_average, naturals, sliding_window, take


def test_windows_basic() -> None:
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]


def test_window_sums() -> None:
    sums = list(map(sum, sliding_window(range(5), 2)))
    assert sums == [1, 3, 5, 7]


def test_window_edge_cases() -> None:
    assert list(sliding_window([], 2)) == []
    assert list(sliding_window([1, 2], 3)) == []
    assert list(sliding_window([1, 2], 2)) == [(1, 2)]
    assert list(sliding_window([1, 2, 3], 1)) == [(1,), (2,), (3,)]


@pytest.mark.parametrize("k", [0, -1])
def test_wrong_window_size(k: int) -> None:
    with pytest.raises(ValueError):
        list(sliding_window([1, 2, 3], k))


def test_window_on_infinite_stream() -> None:
    sums = take(10, map(sum, sliding_window(naturals(1), 3)))
    assert sums == [6, 9, 12, 15, 18, 21, 24, 27, 30, 33]


def test_window_is_lazy() -> None:
    produced: list[int] = []

    def source() -> Iterator[int]:
        for x in count(1):
            produced.append(x)
            yield x

    assert take(2, sliding_window(source(), 3)) == [(1, 2, 3), (2, 3, 4)]
    assert produced == [1, 2, 3, 4]


def test_moving_average() -> None:
    assert list(moving_average([2, 4, 6, 8], 2)) == [3.0, 5.0, 7.0]
    assert list(moving_average([1, 2], 3)) == []
    assert take(3, moving_average(naturals(1), 3)) == [2.0, 3.0, 4.0]
