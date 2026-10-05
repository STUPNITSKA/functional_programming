from core import MeterReading, calculate_payment, make_tariff, no_benefit


def main() -> None:
    print("Облік електроенергії")

    previous = float(input("Попередній показник: "))
    current = float(input("Поточний показник: "))
    tariff_group = input("Тарифна група: ")
    tariff_rate = float(input("Тариф за 1 кВт·год: "))

    reading: MeterReading = {
        "previous": previous,
        "current": current,
        "tariff_group": tariff_group,
    }

    tariff = make_tariff(
        {
            tariff_group: tariff_rate,
        }
    )

    payment = calculate_payment(
        reading,
        tariff,
        no_benefit,
    )

    consumption = current - previous

    print("\n--- КВИТАНЦІЯ ---")
    print(f"Тарифна група: {tariff_group}")
    print(f"Споживання: {consumption:.2f} кВт·год")
    print(f"До оплати: {payment:.2f}")


if __name__ == "__main__":
    main()
