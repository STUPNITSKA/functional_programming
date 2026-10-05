from typing import Callable, TypedDict  # noqa: UP035


class MeterReading(TypedDict):
    previous: float
    current: float
    tariff_group: str


def calculate_consumption(previous: float, current: float) -> float:
    return current - previous


def calculate_cost(consumption: float, tariff: float) -> float:
    return consumption * tariff


BenefitFn = Callable[[float], float]
TariffFn = Callable[[float, str], float]


def make_tariff(rates: dict[str, float]) -> TariffFn:
    def tariff(consumption: float, tariff_group: str) -> float:
        return calculate_cost(consumption, rates[tariff_group])

    return tariff


def no_benefit(amount: float) -> float:
    return amount


def calculate_payment(
    reading: MeterReading,
    tariff: TariffFn,
    benefit: BenefitFn,
) -> float:
    consumption = calculate_consumption(
        reading["previous"],
        reading["current"],
    )
    amount = tariff(consumption, reading["tariff_group"])
    return benefit(amount)
