"""Чисте ядро: розрахунок вартості навчальних курсів (варіант 14)."""

from functools import reduce
from typing import Callable, Iterable, TypedDict, TypeVar  # noqa: UP035


class Registration(TypedDict, total=False):
    id: int
    course: str
    price: float
    student_status: str  # "student" або "regular"
    courses_count: int
    total: float  # з'явиться в результаті


FilterFn = Callable[[Registration], bool]  # (registration) -> bool
DiscountFn = Callable[
    [Registration, float], float
]  # (registration, amount) -> discounted
TaxFn = Callable[[float], float]  # (discounted) -> with tax
NowFn = Callable[[], float]
Result = dict[str, object]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def registration_subtotal(registration: Registration) -> float:
    return registration["price"]


def with_total(registration: Registration, total: float) -> Registration:
    # повертаємо НОВИЙ словник (вхідний не чіпаємо)
    return {**registration, "total": total}


def make_student_discount(rate: float) -> DiscountFn:
    def apply(registration: Registration, amount: float) -> float:
        if registration["student_status"] == "student":
            return amount * (1 - rate)
        return amount

    return apply


def make_package_discount(min_courses: int, rate: float) -> DiscountFn:
    def apply(registration: Registration, amount: float) -> float:
        if registration["courses_count"] >= min_courses:
            return amount * (1 - rate)
        return amount

    return apply


def compose_discounts(*rules: DiscountFn) -> DiscountFn:
    def apply(registration: Registration, amount: float) -> float:
        return reduce(lambda acc, rule: rule(registration, acc), rules, amount)

    return apply


def make_tax(rate: float) -> TaxFn:
    return lambda amount: amount * (1 + rate)


def summarize(registrations: list[Registration]) -> Result:
    return {
        "count": len(registrations),
        "revenue": sum((r["total"] for r in registrations), 0.0),
        "registrations": registrations,
    }


def process_registrations_pure(
    registrations: Iterable[Registration],
    *,
    student_rate: float,
    package_rate: float,
    min_courses: int,
    tax_rate: float,
) -> Result:
    apply_discount = compose_discounts(
        make_student_discount(student_rate),
        make_package_discount(min_courses, package_rate),
    )
    apply_tax = make_tax(tax_rate)
    processed = [
        with_total(r, apply_tax(apply_discount(r, registration_subtotal(r))))
        for r in registrations
    ]
    return summarize(processed)


def make_processor(
    *,
    accept: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: TaxFn,
) -> Callable[[Iterable[Registration]], Result]:
    def process(registrations: Iterable[Registration]) -> Result:
        qualified = [
            with_total(r, apply_tax(apply_discount(r, registration_subtotal(r))))
            for r in registrations
            if accept(r)
        ]
        return summarize(qualified)

    return process


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    # чиста щодо total, а "час" прийшов ззовні
    return total, now()


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k
