from itertools import islice

from streams import drop, fib_stream, take


def test_first_10() -> None:
    assert list(islice(fib_stream(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_drop_then_take_fib() -> None:
    assert take(8, drop(5, fib_stream())) == [5, 8, 13, 21, 34, 55, 89, 144]


def test_new_stream_starts_again() -> None:
    stream = fib_stream()
    assert take(3, stream) == [0, 1, 1]
    assert take(3, stream) == [2, 3, 5]
    assert take(3, fib_stream()) == [0, 1, 1]
