import io
import json
from functools import partial, reduce
from operator import attrgetter, itemgetter, methodcaller, mul
from pathlib import Path
from typing import Any

import pytest

from core import (
    clean_and_rank,
    filt,
    has_priority,
    mapf,
    normalize,
    pipeline,
    rank_shipments,
    to_rank,
    top_n,
    total_cost,
    with_adjusted_cost,
)
from loaders import load_shipments
from models import Shipment, ShipmentRank

ROWS: list[dict[str, Any]] = [
    {"id": 1, "weight": 10, "distance": 100, "priority": " HIGH ", "cost": 100},
    {"id": 2, "weight": 5, "distance": 200, "priority": "low", "cost": 300},
    {"id": 3, "weight": 2, "distance": 40, "priority": "Medium", "cost": 50},
    {"id": 4, "weight": 20, "distance": 300, "priority": "medium", "cost": 260},
]
CSV_TEXT = (
    "id,weight,distance,priority,cost\n"
    "1,10,100, HIGH ,100\n"
    "2,5,200,low,300\n"
    "3,2,40,Medium,50\n"
    "4,20,300,medium,260\n"
)


def inc(x: int) -> int:
    return x + 1


def dbl(x: int) -> int:
    return x * 2


# pipeline і reduce


def test_pipeline_runs_in_order() -> None:
    assert pipeline(3, inc, dbl, inc) == 9


def test_pipeline_without_functions() -> None:
    assert pipeline(5) == 5


def test_reduce_with_initial_value() -> None:
    assert reduce(mul, [], 1) == 1


def test_top_n() -> None:
    assert top_n(2)([5, 4, 3]) == [5, 4]
    assert top_n(0)([1]) == []
    assert top_n(10)([1]) == [1]
    with pytest.raises(ValueError):
        top_n(-1)


def test_mapf_and_filt() -> None:
    assert pipeline([1, 2, 3, 4], mapf(dbl), filt(lambda x: x > 4), list) == [6, 8]


# partial


def test_partial_adjusted_cost() -> None:
    tariff = partial(with_adjusted_cost, per_kg=2.0, per_km=0.5)
    shipment = normalize(ROWS[0])
    priced = tariff(shipment)
    assert priced["adjusted_cost"] == 255.0  # (100 + 20 + 50) * 1.5
    assert "adjusted_cost" not in shipment


def test_partial_priority_filter() -> None:
    only_high = partial(has_priority, allowed=frozenset({"high"}))
    shipments = list(map(normalize, ROWS))
    assert [s["id"] for s in filter(only_high, shipments)] == [1]


def test_low_priority_factor() -> None:
    priced = with_adjusted_cost(normalize(ROWS[1]), per_kg=1.0, per_km=0.0)
    assert priced["adjusted_cost"] == 305.0


# operator


def test_normalize_uses_getters_and_methods() -> None:
    expected: Shipment = {
        "id": 1,
        "weight": 10.0,
        "distance": 100.0,
        "priority": "high",
        "cost": 100.0,
    }
    assert normalize(ROWS[0]) == expected


def test_normalize_unknown_priority() -> None:
    with pytest.raises(ValueError):
        normalize({**ROWS[0], "priority": "urgent"})


def test_operator_tools() -> None:
    assert itemgetter("a", "b")({"a": 1, "b": 2}) == (1, 2)
    assert methodcaller("title")("bob") == "Bob"
    rows = [{"a": 1, "b": 2}, {"a": 1, "b": 1}, {"a": 0, "b": 9}]
    assert sorted(rows, key=itemgetter("a", "b")) == [
        {"a": 0, "b": 9},
        {"a": 1, "b": 1},
        {"a": 1, "b": 2},
    ]
    ranks = [ShipmentRank(2, "low", 1.0), ShipmentRank(1, "low", 2.0)]
    assert list(map(attrgetter("id"), sorted(ranks, key=attrgetter("id")))) == [1, 2]


# конвеєр


def test_clean_and_rank() -> None:
    result = clean_and_rank(ROWS, top=2)
    assert [r.id for r in result] == [4, 1]
    assert result[0].adjusted_cost == 540.0  # (260 + 40 + 150) * 1.2


def test_clean_and_rank_filters_low_priority() -> None:
    assert 2 not in [r.id for r in clean_and_rank(ROWS, top=10)]
    assert [r.id for r in clean_and_rank(ROWS, priorities=["low"])] == [2]


def test_clean_and_rank_edge_cases() -> None:
    assert clean_and_rank(ROWS, top=0) == []
    assert clean_and_rank([], top=3) == []
    assert clean_and_rank(ROWS, priorities=[]) == []


def test_rank_is_sorted_descending() -> None:
    ranks = rank_shipments(ROWS)
    assert ranks == sorted(ranks, reverse=True)


def test_total_cost_with_reduce() -> None:
    ranks = rank_shipments(ROWS)
    assert total_cost(ranks) == round(sum(r.adjusted_cost for r in ranks), 2)
    assert total_cost([]) == 0.0


def test_source_is_not_changed() -> None:
    rows = [dict(r) for r in ROWS]
    clean_and_rank(rows)
    assert rows == ROWS


# singledispatch


def test_all_sources_give_same_result(tmp_path: Path) -> None:
    json_path = tmp_path / "data.json"
    csv_path = tmp_path / "data.csv"
    json_path.write_text(json.dumps(ROWS), encoding="utf-8")
    csv_path.write_text(CSV_TEXT, encoding="utf-8")
    expected = clean_and_rank(ROWS)
    sources: list[Any] = [
        json.dumps(ROWS),
        str(json_path),
        json_path,
        str(csv_path),
        csv_path,
        io.StringIO(json.dumps(ROWS)),
        io.StringIO(CSV_TEXT),
    ]
    for src in sources:
        assert clean_and_rank(src) == expected
    with csv_path.open(encoding="utf-8") as f:
        assert clean_and_rank(load_shipments(f)) == expected


def test_json_string_equals_path(tmp_path: Path) -> None:
    json_str = '[{"name":"x","age":18}]'
    p = tmp_path / "tmp.json"
    p.write_text(json_str, encoding="utf-8")
    assert load_shipments(json_str) == load_shipments(p)


def test_csv_values_are_strings() -> None:
    assert load_shipments(io.StringIO(CSV_TEXT))[0]["id"] == "1"


def test_list_is_returned_as_is() -> None:
    assert load_shipments(ROWS) is ROWS
    assert load_shipments([]) == []


def test_unsupported_type() -> None:
    with pytest.raises(TypeError):
        load_shipments(42)


def test_list_of_not_dicts() -> None:
    with pytest.raises(ValueError):
        load_shipments([1, 2])
    with pytest.raises(ValueError):
        load_shipments('{"id": 1}')


# total_ordering


A = ShipmentRank(1, "high", 500.0)
B = ShipmentRank(2, "low", 500.0)
C = ShipmentRank(3, "low", 100.0)


def test_all_comparison_operators() -> None:
    assert B < A and C < B
    assert B <= A and A <= ShipmentRank(1, "high", 500.0)
    assert A > B and A > C
    assert A >= B and A >= ShipmentRank(1, "high", 500.0)
    assert A == ShipmentRank(1, "high", 500.0)
    assert A != B


def test_order_by_cost_then_priority_then_id() -> None:
    d = ShipmentRank(4, "low", 500.0)
    assert sorted([A, d, C, B]) == [C, B, d, A]
    assert max([C, A, B]) is A


def test_other_types_return_not_implemented() -> None:
    assert A.__eq__("x") is NotImplemented
    assert A.__lt__(5) is NotImplemented
    assert A != "x"
    with pytest.raises(TypeError):
        _ = A < 5
    with pytest.raises(TypeError):
        _ = A >= "x"


def test_to_rank() -> None:
    priced = with_adjusted_cost(normalize(ROWS[2]), per_kg=0.0, per_km=0.0)
    assert to_rank(priced) == ShipmentRank(3, "medium", 60.0)
