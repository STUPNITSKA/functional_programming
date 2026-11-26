import json
from operator import attrgetter
from pathlib import Path

from core import clean_and_rank, rank_shipments, total_cost
from loaders import load_shipments
from models import ShipmentRank

HERE = Path(__file__).parent
JSON_PATH = HERE / "sample_data.json"
CSV_PATH = HERE / "sample_data.csv"


def main() -> None:
    raw = load_shipments(JSON_PATH)
    sources = {
        "JSON-рядок": JSON_PATH.read_text(encoding="utf-8"),
        "шлях str": str(JSON_PATH),
        "Path": JSON_PATH,
        "CSV-шлях": str(CSV_PATH),
        "список": json.loads(JSON_PATH.read_text(encoding="utf-8")),
    }
    for name, src in sources.items():
        print(f"{name}: {len(load_shipments(src))} записів")
    with CSV_PATH.open(encoding="utf-8") as f:
        print(f"відкритий файл CSV: {len(load_shipments(f))} записів")
    print(
        "однаково для JSON і CSV:",
        clean_and_rank(JSON_PATH) == clean_and_rank(CSV_PATH),
    )

    print("\nTop-3 (high і medium):")
    for place, rank in enumerate(clean_and_rank(raw, top=3), start=1):
        print(f"  {place}. id={rank.id} {rank.priority:<6} {rank.adjusted_cost:.2f}")

    ranks = rank_shipments(raw)
    print("id у рейтингу:", list(map(attrgetter("id"), ranks)))
    print("загальна вартість:", total_cost(ranks))
    only_high = clean_and_rank(raw, 2, priorities=["high"])
    print("лише high, top-2:", list(map(attrgetter("id", "adjusted_cost"), only_high)))

    a = ShipmentRank(1, "high", 500.0)
    b = ShipmentRank(2, "low", 500.0)
    print("\nпорівняння:", a > b, a >= b, a < b, a <= b, a == b, a != b)


if __name__ == "__main__":
    main()
