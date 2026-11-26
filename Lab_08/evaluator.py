from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import replace
from functools import reduce
from typing import Literal, TypeAlias

from model import (
    ErrorEvent,
    Event,
    FileOpened,
    Level,
    Login,
    Logout,
    LogState,
    Timestamped,
    assert_never,
)

Kind: TypeAlias = Literal["login", "logout", "file", "error"]


def check_order(state: LogState, event: Timestamped) -> LogState:
    """Новий стан з часом події; час не може йти назад."""
    if event.timestamp < state.last_timestamp:
        raise ValueError(
            f"event at {event.timestamp} is older than {state.last_timestamp}"
        )
    return replace(state, last_timestamp=event.timestamp)


def reduce_event(state: LogState, event: Event) -> LogState:
    """Чистий reducer: повертає новий стан після однієї події."""
    s = check_order(state, event)
    match event:
        case Login(user=user) if user in s.active_users:
            return replace(s, invalid=s.invalid + 1)
        case Login(user=user):
            return replace(s, logins=s.logins + 1, active_users=s.active_users | {user})
        case Logout(user=user) if user not in s.active_users:
            return replace(s, invalid=s.invalid + 1)
        case Logout(user=user):
            return replace(
                s, logouts=s.logouts + 1, active_users=s.active_users - {user}
            )
        case FileOpened(user=user) if user not in s.active_users:
            return replace(s, invalid=s.invalid + 1)
        case FileOpened():
            return replace(s, files_opened=s.files_opened + 1)
        case ErrorEvent(level=level):
            return count_error(s, level)
        case _:
            assert_never(event)


def count_error(state: LogState, level: Level) -> LogState:
    match level:
        case "warning":
            return replace(state, warnings=state.warnings + 1)
        case "error":
            return replace(state, errors=state.errors + 1)
        case "critical":
            return replace(state, critical=state.critical + 1)
        case _:
            assert_never(level)


def process_log(events: Iterable[Event], initial: LogState = LogState()) -> LogState:
    """Згортає журнал подій у підсумковий стан."""
    return reduce(reduce_event, events, initial)


def event_kind(event: Event) -> Kind:
    match event:
        case Login():
            return "login"
        case Logout():
            return "logout"
        case FileOpened():
            return "file"
        case ErrorEvent():
            return "error"
        case _:
            assert_never(event)


def count_by_kind(events: Iterable[Event]) -> dict[Kind, int]:
    """Статистика: скільки подій кожного виду."""
    return dict(Counter(map(event_kind, events)))


def root_cause(error: ErrorEvent) -> ErrorEvent:
    """Найглибша причина в ланцюжку помилок."""
    match error:
        case ErrorEvent(cause=ErrorEvent() as cause):
            return root_cause(cause)
        case _:
            return error


def chain_length(error: ErrorEvent) -> int:
    """Кількість помилок у ланцюжку разом із самою помилкою."""
    match error:
        case ErrorEvent(cause=ErrorEvent() as cause):
            return 1 + chain_length(cause)
        case _:
            return 1
