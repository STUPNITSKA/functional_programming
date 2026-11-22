from copy import deepcopy

import pytest

from core import (
    DiscountFn,
    Registration,
    TaxFn,
    compose,
    compose_discounts,
    make_multiplier,
    make_package_discount,
    make_processor,
    make_student_discount,
    make_tax,
    process_registrations_pure,
    stamp_total,
    with_total,
)


@pytest.fixture
def sample_registrations() -> list[Registration]:
    return [
        {
            "id": 1,
            "course": "Python",
            "price": 1000.0,
            "student_status": "student",
            "courses_count": 3,
        },
        {
            "id": 2,
            "course": "SQL",
            "price": 800.0,
            "student_status": "regular",
            "courses_count": 1,
        },
        {
            "id": 3,
            "course": "Haskell",
            "price": 1200.0,
            "student_status": "regular",
            "courses_count": 4,
        },
    ]


def test_referential_transparency(sample_registrations: list[Registration]) -> None:
    process = lambda: process_registrations_pure(
        sample_registrations,
        student_rate=0.2,
        package_rate=0.1,
        min_courses=3,
        tax_rate=0.2,
    )
    r1 = process()
    r2 = process()
    assert r1 == r2  # той самий вхід → той самий вихід


def test_no_mutation(sample_registrations: list[Registration]) -> None:
    original = deepcopy(sample_registrations)
    process_registrations_pure(
        sample_registrations,
        student_rate=0.2,
        package_rate=0.1,
        min_courses=3,
        tax_rate=0.2,
    )
    assert sample_registrations == original  # вхід не змінюється


def test_with_total_returns_new_dict(
    sample_registrations: list[Registration],
) -> None:
    reg = sample_registrations[0]
    new_reg = with_total(reg, 100.0)
    assert new_reg["total"] == 100.0
    assert "total" not in reg


def test_process_registrations_pure(
    sample_registrations: list[Registration],
) -> None:
    result = process_registrations_pure(
        sample_registrations,
        student_rate=0.2,
        package_rate=0.1,
        min_courses=3,
        tax_rate=0.2,
    )
    # 1000 * 0.8 * 0.9 * 1.2 = 864; 800 * 1.2 = 960; 1200 * 0.9 * 1.2 = 1296
    assert result["count"] == 3
    assert result["revenue"] == pytest.approx(864 + 960 + 1296)


def test_callable_policies(sample_registrations: list[Registration]) -> None:
    accept = lambda r: r["price"] >= 900
    apply_discount: DiscountFn = compose_discounts(
        make_student_discount(0.2),
        make_package_discount(3, 0.1),
    )
    apply_tax: TaxFn = lambda s: s * 1.2
    processor = make_processor(
        accept=accept, apply_discount=apply_discount, apply_tax=apply_tax
    )
    result = processor(sample_registrations)
    assert result["count"] == 2
    assert result["revenue"] == pytest.approx(864 + 1296)


def test_compose_discounts(sample_registrations: list[Registration]) -> None:
    student = make_student_discount(0.2)
    package = make_package_discount(3, 0.1)
    reg = sample_registrations[0]
    assert compose_discounts(student, package)(reg, 1000.0) == pytest.approx(720.0)
    assert compose_discounts()(reg, 1000.0) == 1000.0


def test_make_tax() -> None:
    assert make_tax(0.2)(100.0) == pytest.approx(120.0)


def test_stamp_total() -> None:
    assert stamp_total(10.0, lambda: 123.0) == (10.0, 123.0)


def test_compose_and_make_multiplier() -> None:
    double = make_multiplier(2)
    triple = make_multiplier(3)
    assert compose(double, triple)(5) == 30
