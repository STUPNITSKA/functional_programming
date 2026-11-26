from collections.abc import Iterator

from streams import numbered, pattern_plan, pattern_stream, pattern_until, take

PATTERN = ("A", "B", "C")


def test_pattern_repeats() -> None:
    assert take(7, pattern_stream(PATTERN)) == ["A", "B", "C", "A", "B", "C", "A"]


def test_empty_pattern_gives_empty_stream() -> None:
    assert take(5, pattern_stream([])) == []
    assert pattern_plan([], 3) == []


def test_numbering() -> None:
    assert pattern_plan(PATTERN, 4) == [(1, "A"), (2, "B"), (3, "C"), (4, "A")]
    assert pattern_plan(PATTERN, 2, start=0) == [(0, "A"), (1, "B")]
    assert pattern_plan(PATTERN, 0) == []
    assert list(numbered("xy", 5)) == [(5, "x"), (6, "y")]


def test_stop_by_number() -> None:
    result = list(pattern_until(PATTERN, lambda number, state: number > 4))
    assert result == [(1, "A"), (2, "B"), (3, "C"), (4, "A")]


def test_stop_by_state() -> None:
    result = list(
        pattern_until(PATTERN, lambda number, state: number > 3 and state == "B")
    )
    assert result == [(1, "A"), (2, "B"), (3, "C"), (4, "A")]


def test_stop_immediately() -> None:
    assert list(pattern_until(PATTERN, lambda number, state: True)) == []


def test_pattern_source_is_not_changed() -> None:
    source = ["A", "B"]
    take(5, pattern_stream(source))
    assert source == ["A", "B"]


def test_pattern_is_lazy() -> None:
    produced: list[int] = []

    def states() -> Iterator[str]:
        for state in PATTERN:
            produced.append(1)
            yield state

    stream = pattern_stream(states())
    assert produced == []
    assert take(2, stream) == ["A", "B"]
    assert len(produced) == 2
