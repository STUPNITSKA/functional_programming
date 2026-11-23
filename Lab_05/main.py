from streams import (
    drop,
    drop_while,
    fib_stream,
    moving_average,
    naturals,
    pattern_plan,
    pattern_stream,
    pattern_until,
    prefix_products,
    prefix_sums,
    sliding_window,
    take,
    take_while,
    window_sums_of_multiples,
)

LIGHTS = ("червоне", "жовте", "зелене", "жовте")


def main() -> None:
    print("fib, перші 10:", take(10, fib_stream()))
    print("fib, пропустити 5, взяти 8:", take(8, drop(5, fib_stream())))
    print("суми вікон по 3:", take(10, map(sum, sliding_window(naturals(1), 3))))
    print("рухоме середнє k=2:", list(moving_average([2, 4, 6, 8], 2)))
    print("префіксні суми:", list(prefix_sums([1, 2, 3, 4])))
    print("префіксні добутки:", list(prefix_products([1, 2, 3, 4])))
    print("takewhile < 20:", list(take_while(lambda x: x < 20, fib_stream())))
    print("dropwhile <= 0:", list(drop_while(lambda x: x <= 0, [-2, 0, 3, -1, 4])))
    print("кратні 3, суми вікон по 4:", window_sums_of_multiples(3, 4, 10))

    print("\nШаблон:", " -> ".join(LIGHTS))
    print("план на 6 кроків:")
    for number, state in pattern_plan(LIGHTS, 6):
        print(f"  {number}. {state}")

    print("до кроку 10 або до першого зеленого після 5-го:")
    stop = pattern_until(
        LIGHTS, lambda number, state: number >= 10 or (number > 5 and state == "зелене")
    )
    print("  ", list(stop))

    print("переходи:", take(4, sliding_window(pattern_stream(LIGHTS), 2)))


if __name__ == "__main__":
    main()
