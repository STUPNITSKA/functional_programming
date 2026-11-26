import dataclasses

import pytest

from evaluator import check_order
from model import ErrorEvent, Event, FileOpened, Login, Logout, LogState, Timestamped


def test_nodes_are_frozen() -> None:
    login = Login(1, "anna")
    with pytest.raises(dataclasses.FrozenInstanceError):
        login.user = "petro"  # type: ignore[misc]


def test_nodes_compare_by_value() -> None:
    assert Login(1, "anna") == Login(1, "anna")
    login: Event = Login(1, "anna")
    logout: Event = Logout(1, "anna")
    assert login != logout
    assert ErrorEvent(1, "error", "x") != ErrorEvent(1, "warning", "x")


def test_nested_error_is_immutable_value() -> None:
    inner = ErrorEvent(1, "warning", "low space")
    outer = ErrorEvent(2, "error", "write failed", inner)
    assert outer.cause is inner
    assert outer == ErrorEvent(
        2, "error", "write failed", ErrorEvent(1, "warning", "low space")
    )


def test_state_is_frozen_and_hashable() -> None:
    state = LogState()
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.logins = 5  # type: ignore[misc]
    assert hash(state) == hash(LogState())


class Tick:
    """Не подія з журналу, але має timestamp."""

    def __init__(self, timestamp: int) -> None:
        self._t = timestamp

    @property
    def timestamp(self) -> int:
        return self._t


def test_protocol_accepts_any_timestamped() -> None:
    items: list[Timestamped] = [Login(1, "a"), FileOpened(2, "a", "/f"), Tick(3)]
    state = LogState()
    for item in items:
        state = check_order(state, item)
    assert state.last_timestamp == 3
