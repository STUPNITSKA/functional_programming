# Лабораторна №8. Алгебраїчні типи даних

Варіант 14 — події системи. Журнал складається з подій `Login`, `Logout`, `FileOpened` і `ErrorEvent`, а чиста функція-reducer згортає його в підсумковий стан.

## Модель

- `model.py`:
  - `Login(timestamp, user)`, `Logout(timestamp, user)`, `FileOpened(timestamp, user, path)`, `ErrorEvent(timestamp, level, message, cause)` — незмінні вузли `@dataclass(frozen=True)`.
  - `Event: TypeAlias = Login | Logout | FileOpened | ErrorEvent` — сума варіантів.
  - `Level: TypeAlias = Literal["warning", "error", "critical"]` — рівні помилки.
  - `ErrorEvent.cause` — інша помилка, яка її спричинила, тому помилки утворюють рекурсивний ланцюжок.
  - `Timestamped` — `Protocol` для будь-якого об'єкта з властивістю `timestamp`.
  - `LogState` — незмінний стан: активні користувачі, лічильники входів, виходів, відкритих файлів, помилок за рівнями, некоректних подій і час останньої події.
  - `assert_never` — перевірка, що `match` розібрав усі варіанти. Якщо додати новий вузол і забути його обробити, mypy покаже помилку.
- `evaluator.py`:
  - `reduce_event(state, event)` — через `match/case` з guard-умовами повертає новий стан. Повторний вхід, вихід без входу і відкриття файлу неактивним користувачем рахуються як некоректні події.
  - `check_order` приймає будь-який `Timestamped` і не дозволяє часу йти назад.
  - `process_log(events, initial)` — згортка журналу через `reduce`.
  - `event_kind` і `count_by_kind` — статистика подій за видами, `root_cause` і `chain_length` — рекурсивний розбір ланцюжка помилок.
- `pretty.py` — `render_event`, `render_log` і `render_state` для текстового виводу, причини помилки виводяться через `<-`.
- `main.py` — демонстраційний журнал з некоректними подіями та ланцюжком із трьох помилок.

## Тести

- `tests/test_model.py` — незмінність вузлів і стану, порівняння за значенням, вкладені помилки, `Protocol` для стороннього класу з `timestamp`.
- `tests/test_evaluator.py` — кожен вид події, усі рівні помилки, некоректні переходи, порожній журнал, неправильний порядок часу, початковий стан, незмінність вхідного стану, статистика і ланцюжки помилок.
- `tests/test_pretty.py` — рендер кожної події, вкладеної помилки, журналу та стану.

## Запуск

Для запуску потрібен Python 3.10 або новіший.

```bash
cd Lab_08
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
python -m pytest -q
python -m mypy --strict .
python -m black --check .
python -m ruff check .
```
