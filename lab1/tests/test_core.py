from core import (
    calculate_consumption,
    calculate_payment,
    make_tariff,
    no_benefit,
)


def test_calculate_consumption():
    result = calculate_consumption(1200, 1300)

    assert result == 100


def test_calculate_payment_does_not_mutate():
    reading = {
        "previous": 1200,
        "current": 1300,
        "tariff_group": "day",
    }

    original = reading.copy()

    tariff = make_tariff({"day": 4.0})

    calculate_payment(
        reading,
        tariff,
        no_benefit,
    )

    assert reading == original


def test_no_benefit():
    amount = 500.0

    result = no_benefit(amount)

    assert result == 500.0


def test_make_tariff():
    rates = {
        "day": 4.0,
        "night": 2.0,
    }

    tariff = make_tariff(rates)

    assert tariff(100, "day") == 400.0
    assert tariff(100, "night") == 200.0


def test_calculate_payment():
    reading = {
        "previous": 1200,
        "current": 1300,
        "tariff_group": "day",
    }

    tariff = make_tariff(
        {
            "day": 4.0,
        }
    )

    result = calculate_payment(
        reading,
        tariff,
        no_benefit,
    )

    assert result == 400.0


def test_calculate_consumption_is_referentially_transparent():
    first_result = calculate_consumption(1200, 1300)
    second_result = calculate_consumption(1200, 1300)

    assert first_result == second_result
