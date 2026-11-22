import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from core import (
    Record,
    boost_genre,
    build_pipeline,
    compose,
    juxt,
    only_popular,
    pipe,
    reduce_stats,
    sort_by_total_desc,
    take,
    with_total,
)


@pytest.fixture
def tracks() -> list[Record]:
    return [
        {"id": 3, "title": "C", "genre": "rock", "listens": [100, 100]},
        {"id": 1, "title": "A", "genre": "pop", "listens": [150, 70]},
        {"id": 2, "title": "B", "genre": "rock", "listens": [50, 50]},
        {"id": 4, "title": "D", "genre": "jazz", "listens": [20]},
        {"id": 5, "title": "E", "genre": "pop", "listens": []},
    ]


def test_with_total_sums_listens(tracks: list[Record]) -> None:
    result = list(with_total()(tracks))

    assert [track["total"] for track in result] == [200, 220, 100, 20, 0]


def test_boost_only_selected_genre(tracks: list[Record]) -> None:
    result = list(boost_genre("rock", 1.1)(with_total()(tracks)))

    assert [track["total"] for track in result] == [220, 220, 110, 20, 0]


def test_only_popular_keeps_threshold(tracks: list[Record]) -> None:
    result = only_popular(100)(with_total()(tracks))

    assert [track["id"] for track in result] == [3, 1, 2]


def test_top_n_sorted_by_total_then_id(tracks: list[Record]) -> None:
    pipeline = build_pipeline(top_n=2, genre="rock", factor=1.1, min_listens=100)

    result = pipeline(tracks)

    assert [(track["id"], track["total"]) for track in result] == [
        (1, 220),
        (3, 220),
    ]


@pytest.mark.parametrize("top_n", [0, 1, 3, 10])
def test_top_n_length(tracks: list[Record], top_n: int) -> None:
    result = build_pipeline(top_n=top_n, genre="rock", min_listens=100)(tracks)

    assert len(result) == min(top_n, 3)


def test_negative_top_n_is_rejected() -> None:
    with pytest.raises(ValueError):
        take(-1)


def test_sort_does_not_reorder_input(tracks: list[Record]) -> None:
    with_totals = list(with_total()(tracks))

    result = sort_by_total_desc()(with_totals)

    assert [track["id"] for track in with_totals] == [3, 1, 2, 4, 5]
    assert [track["id"] for track in result] == [1, 3, 2, 4, 5]


def test_pipeline_does_not_mutate_input(tracks: list[Record]) -> None:
    original = deepcopy(tracks)
    pipeline = build_pipeline(top_n=5, genre="rock", min_listens=0)

    first = pipeline(tracks)
    second = pipeline(tracks)

    assert tracks == original
    assert first == second
    assert all("total" not in track for track in tracks)


def test_reduce_stats(tracks: list[Record]) -> None:
    rating = build_pipeline(top_n=3, genre="rock", factor=1.1, min_listens=100)(tracks)

    assert reduce_stats(rating) == {
        "count": 3,
        "listens_sum": 550.0,
        "avg_listens": 183.33,
    }


def test_reduce_stats_empty() -> None:
    assert reduce_stats([]) == {"count": 0, "listens_sum": 0.0, "avg_listens": 0.0}


def test_compose_and_pipe_order() -> None:
    def double(value: int) -> int:
        return value * 2

    def increment(value: int) -> int:
        return value + 1

    assert compose(double, increment)(3) == 8
    assert pipe(double, increment)(3) == 7
    assert compose()(3) == pipe()(3) == 3


def test_juxt_applies_all_functions() -> None:
    def double(value: int) -> int:
        return value * 2

    assert juxt(abs, double)(-4) == (4, -8)


def test_main_prints_rating_for_sample_data() -> None:
    lab_dir = Path(__file__).resolve().parents[1]
    run = subprocess.run(
        [sys.executable, "main.py", "--top", "3"],
        cwd=lab_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        check=True,
    )

    lines = run.stdout.splitlines()
    assert lines[0].startswith("1. Світанок")
    assert lines[-1] == "count: 3, listens_sum: 990, avg_listens: 330"
