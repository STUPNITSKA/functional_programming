import random

from algorithms import quicksort


def test_quicksort_basic() -> None:
    assert quicksort([]) == []
    assert quicksort([1]) == [1]
    assert quicksort([3, 2, 1]) == [1, 2, 3]
    assert quicksort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


def test_quicksort_random() -> None:
    xs = [random.randint(-1000, 1000) for _ in range(1000)]
    assert quicksort(xs) == sorted(xs)


def test_quicksort_does_not_mutate_input() -> None:
    xs = [4, 1, 3, 1]
    result = quicksort(xs)
    assert xs == [4, 1, 3, 1]
    assert result is not xs


def test_quicksort_single_element_returns_copy() -> None:
    xs = [7]
    result = quicksort(xs)
    assert result == [7]
    assert result is not xs
