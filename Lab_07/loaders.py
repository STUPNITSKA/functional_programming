import csv
import io
import json
from functools import singledispatch
from pathlib import Path
from typing import Any

Records = list[dict[str, Any]]


def parse_json(text: str) -> Records:
    return check_records(json.loads(text))


def parse_csv(text: str) -> Records:
    return check_records(list(csv.DictReader(io.StringIO(text))))


def parse_text(text: str) -> Records:
    """JSON, якщо текст починається з '[' або '{', інакше CSV."""
    is_json = text.lstrip().startswith(("[", "{"))
    return parse_json(text) if is_json else parse_csv(text)


def check_records(data: object) -> Records:
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError("Expected list of dicts")
    return data


@singledispatch
def load_shipments(src: object) -> Records:
    """Завантажує відправлення з JSON/CSV-рядка, шляху, файлу або списку."""
    raise TypeError(f"Unsupported type: {type(src)!r}")


@load_shipments.register
def _(src: str) -> Records:
    s = src.strip()
    if s.startswith(("[", "{")):
        return parse_json(s)
    return load_shipments(Path(s))


@load_shipments.register
def _(src: Path) -> Records:
    text = src.read_text(encoding="utf-8")
    return parse_csv(text) if src.suffix.lower() == ".csv" else parse_json(text)


@load_shipments.register
def _(src: io.TextIOBase) -> Records:
    return parse_text(src.read())


@load_shipments.register(list)
def _(src: list[Any]) -> Records:
    return check_records(src)
