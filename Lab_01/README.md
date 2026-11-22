# Лабораторна робота №1
## Основи функціонального програмування у Python

Студентка: Ступницька Юлія Ярославівна

### Варіант №14 — Вартість навчальних курсів

- **Вхідні дані:** курс, ціна, статус студента, кількість курсів.
- **Основне завдання:** застосувати пакетну/студентську знижку і податок.
- **Функціональні вимоги:** компонувати правила знижок; не мутувати реєстрації.

### Що зроблено

**Завдання 1. Функціональний стиль.** `process_registrations_pure()` обчислює вартість
усіх реєстрацій. Усі параметри (`student_rate`, `package_rate`, `min_courses`, `tax_rate`)
передаються явно, глобальних констант немає. Вхідні словники не змінюються:
`with_total()` повертає новий словник з полем `total`.

**Завдання 2. `typing.Callable`.** Політики винесені у функції:

- `FilterFn = Callable[[Registration], bool]` — фільтр реєстрацій;
- `DiscountFn = Callable[[Registration, float], float]` — правило знижки;
- `TaxFn = Callable[[float], float]` — податок.

`make_processor(accept=..., apply_discount=..., apply_tax=...)` — функція вищого порядку,
що повертає налаштований обробник.

Правила знижок створюються фабриками `make_student_discount(rate)` і
`make_package_discount(min_courses, rate)` та компонуються через `compose_discounts(*rules)`.
Податок створює `make_tax(rate)`.

**Завдання 3. Ізоляція побічних ефектів.** Усі `print` і `time` знаходяться в `app.py`
(`render_report()`, `run()`). Час передається в ядро через `NowFn = Callable[[], float]`
у функції `stamp_total(total, now)`.

**Звіт:** `report/lab1.pdf`.

**Додаткові вправи:** `compose(f, g)`, `make_multiplier(k)`; списки формуються через
list comprehension замість мутацій.

### Чисті функції (`core.py`)

- `registration_subtotal()` — базова ціна курсу;
- `with_total()` — новий запис з полем `total`;
- `make_student_discount()` — студентська знижка;
- `make_package_discount()` — пакетна знижка (від певної кількості курсів);
- `compose_discounts()` — композиція правил знижок;
- `make_tax()` — податок;
- `summarize()` — кількість реєстрацій і загальний дохід;
- `process_registrations_pure()` — обробка з явними параметрами;
- `make_processor()` — фабрика обробника з Callable-політиками;
- `stamp_total()` — інжекція часу;
- `compose()`, `make_multiplier()`.

### Структура проєкту

```text
Lab_01/
├── README.md          # що зроблено, як запускати
├── core.py            # чисті функції
├── app.py             # I/O-оболонка
├── report/
│   └── lab1.pdf       # звіт
├── tests/
│   ├── conftest.py
│   └── test_core.py
└── requirements.txt   # pytest, mypy, black, ruff
```

### Запуск

```bash
cd Lab_01
pip install -r requirements.txt
python app.py
```

### Перевірки

```bash
pytest
mypy .
black --check .
ruff check .
```

Тести перевіряють референтну прозорість, відсутність мутацій вхідних даних
і правильність Callable-політик.
