# Лабораторна №7. functools та operator

Варіант 14 — логістичні відправлення. Кожне відправлення має поля `id`, `weight`, `distance`, `priority`, `cost`. Програма рахує скориговану вартість, відбирає відправлення за пріоритетом, формує рейтинг і Top-N, а загальну вартість рахує через `reduce`.

- `models.py`:
  - `Shipment` і `PricedShipment` — `TypedDict` для нормалізованого запису та запису зі скоригованою вартістю.
  - `ShipmentRank` — клас з `@total_ordering`. Порівнюється за скоригованою вартістю, потім за рівнем пріоритету, потім за `id` (ключ через `attrgetter`). Реалізовано лише `__eq__` і `__lt__`, для чужих типів вони повертають `NotImplemented`.
- `loaders.py` — `load_shipments` на `@singledispatch`:
  - `str` — JSON-рядок або шлях до `.json` / `.csv`;
  - `Path` — формат визначається за розширенням;
  - відкритий текстовий файл — JSON, якщо текст починається з `[` або `{`, інакше CSV;
  - `list` — готовий список словників, з перевіркою.
  Інші типи дають `TypeError`, а дані, що не є списком словників, — `ValueError`.
- `core.py`:
  - `pipeline(value, *funcs)` через `reduce`, `mapf` і `filt` через `partial`, `top_n(n)`.
  - `normalize` — типи полів і пріоритет через `itemgetter` та `methodcaller("strip")`, `methodcaller("lower")`.
  - `with_adjusted_cost` — `(cost + weight * per_kg + distance * per_km) * коефіцієнт пріоритету` (high 1.5, medium 1.2, low 1.0). Тариф фіксується через `partial`.
  - `has_priority` — фільтр, набір дозволених пріоритетів фіксується через `partial`.
  - `rank_shipments` — конвеєр: завантаження → нормалізація → вартість → фільтр → `ShipmentRank` → сортування за спаданням.
  - `clean_and_rank(src, top=3)` — Top-N рейтингу, `total_cost` — сума через `reduce(add, ...)`.
- `main.py` завантажує `sample_data.json` і `sample_data.csv` з різних джерел і показує Top-3, рейтинг, загальну вартість та порівняння.
- `tests/test_lab07.py` — тести на `pipeline`, `reduce`, `partial`, засоби `operator`, конвеєр і крайові випадки, однаковий результат для всіх джерел `load_shipments`, помилки завантаження та всі оператори порівняння `ShipmentRank`.

## Запуск

Для запуску потрібен Python 3.10 або новіший. З кореня репозиторію виконай `python Lab_07/main.py`.

```bash
cd Lab_07
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
python -m pytest -q
python -m mypy .
python -m black --check .
python -m ruff check .
```
