from collections.abc import Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import Any, Callable, TypedDict, TypeVar


class Track(TypedDict):
    id: int
    title: str
    genre: str
    listens: list[int]


class Record(Track, total=False):
    total: float


class Stats(TypedDict):
    count: int
    listens_sum: float
    avg_listens: float


T = TypeVar("T")
R = TypeVar("R")
Transform = Callable[[Iterable[Record]], Iterator[Record]]
Pipeline = Callable[[Iterable[Record]], list[Record]]


def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def run(value: Any) -> Any:
        return reduce(lambda acc, func: func(acc), funcs, value)

    return run


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return pipe(*reversed(funcs))


def juxt(*funcs: Callable[[T], R]) -> Callable[[T], tuple[R, ...]]:
    def run(value: T) -> tuple[R, ...]:
        return tuple(func(value) for func in funcs)

    return run


def with_total() -> Transform:
    return lambda records: map(
        lambda record: {**record, "total": float(sum(record["listens"]))}, records
    )


def boost_genre(genre: str, factor: float) -> Transform:
    def boost(record: Record) -> Record:
        total = record.get("total", 0.0)
        if record["genre"] == genre:
            total = round(total * factor, 2)
        return {**record, "total": total}

    return lambda records: map(boost, records)


def only_popular(min_listens: float) -> Transform:
    return lambda records: filter(
        lambda record: record.get("total", 0.0) >= min_listens, records
    )


def sort_by_total_desc() -> Pipeline:
    key: Callable[[Record], tuple[float, ...]] = juxt(
        lambda record: -record.get("total", 0.0), lambda record: record["id"]
    )
    return lambda records: sorted(records, key=key)


def take(n: int) -> Pipeline:
    if n < 0:
        raise ValueError("top_n must be non-negative")
    return lambda records: list(islice(records, n))


def reduce_stats(records: Iterable[Record]) -> Stats:
    count, listens_sum = reduce(
        lambda acc, record: (acc[0] + 1, acc[1] + record.get("total", 0.0)),
        records,
        (0, 0.0),
    )
    return {
        "count": count,
        "listens_sum": round(listens_sum, 2),
        "avg_listens": round(listens_sum / count, 2) if count else 0.0,
    }


def build_pipeline(
    top_n: int = 3,
    genre: str = "Рок",
    factor: float = 1.1,
    min_listens: float = 100,
) -> Pipeline:
    pipeline: Pipeline = compose(
        take(top_n),
        sort_by_total_desc(),
        only_popular(min_listens),
        boost_genre(genre, factor),
        with_total(),
    )
    return pipeline
