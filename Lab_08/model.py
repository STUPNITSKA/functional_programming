from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, NoReturn, Protocol, TypeAlias

Level: TypeAlias = Literal["warning", "error", "critical"]


@dataclass(frozen=True)
class Login:
    timestamp: int
    user: str


@dataclass(frozen=True)
class Logout:
    timestamp: int
    user: str


@dataclass(frozen=True)
class FileOpened:
    timestamp: int
    user: str
    path: str


@dataclass(frozen=True)
class ErrorEvent:
    timestamp: int
    level: Level
    message: str
    cause: ErrorEvent | None = None


Event: TypeAlias = Login | Logout | FileOpened | ErrorEvent


class Timestamped(Protocol):
    """Будь-яка подія, що має час."""

    @property
    def timestamp(self) -> int: ...


@dataclass(frozen=True)
class LogState:
    """Незмінний стан, який накопичує reducer."""

    active_users: frozenset[str] = frozenset()
    logins: int = 0
    logouts: int = 0
    files_opened: int = 0
    warnings: int = 0
    errors: int = 0
    critical: int = 0
    invalid: int = 0
    last_timestamp: int = 0


def assert_never(value: NoReturn) -> NoReturn:
    raise AssertionError(f"Unhandled event: {value!r}")
