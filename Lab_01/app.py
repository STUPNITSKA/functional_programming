"""Оболонка побічних ефектів: дані, виведення звіту, поточний час."""

import time

from core import (
    Registration,
    Result,
    compose_discounts,
    make_package_discount,
    make_processor,
    make_student_discount,
    make_tax,
    stamp_total,
)


def render_report(result: Result) -> None:
    registrations = result["registrations"]
    revenue = result["revenue"]
    stamped_at = result["stamped_at"]
    assert isinstance(registrations, list) and isinstance(revenue, float)
    assert isinstance(stamped_at, float)
    for r in registrations:
        print("Processed:", r["id"], r["course"], "total:", round(r["total"], 2))
    print("Count:", result["count"])
    print("Revenue:", round(revenue, 2))
    print("Time:", time.ctime(stamped_at))


def run(registrations: list[Registration]) -> None:
    processor = make_processor(
        accept=lambda r: r["price"] > 0,
        apply_discount=compose_discounts(
            make_student_discount(0.2),
            make_package_discount(3, 0.1),
        ),
        apply_tax=make_tax(0.2),
    )
    result = processor(registrations)
    revenue = result["revenue"]
    assert isinstance(revenue, float)
    _, stamped_at = stamp_total(revenue, time.time)
    render_report({**result, "stamped_at": stamped_at})


if __name__ == "__main__":
    run(
        [
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
    )
