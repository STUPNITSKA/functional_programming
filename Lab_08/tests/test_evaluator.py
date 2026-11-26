import pytest

from evaluator import (
    chain_length,
    count_by_kind,
    event_kind,
    process_log,
    reduce_event,
    root_cause,
)
from model import ErrorEvent, Event, FileOpened, Level, Login, Logout, LogState


def test_login() -> None:
    state = reduce_event(LogState(), Login(1, "anna"))
    assert state.logins == 1
    assert state.active_users == frozenset({"anna"})
    assert state.last_timestamp == 1


def test_logout() -> None:
    state = process_log([Login(1, "anna"), Logout(2, "anna")])
    assert (state.logins, state.logouts) == (1, 1)
    assert state.active_users == frozenset()


def test_file_opened() -> None:
    state = process_log([Login(1, "anna"), FileOpened(2, "anna", "/a.txt")])
    assert state.files_opened == 1


@pytest.mark.parametrize(
    ("level", "expected"),
    [("warning", (1, 0, 0)), ("error", (0, 1, 0)), ("critical", (0, 0, 1))],
)
def test_error_levels(level: Level, expected: tuple[int, int, int]) -> None:
    state = reduce_event(LogState(), ErrorEvent(1, level, "boom"))
    assert (state.warnings, state.errors, state.critical) == expected


def test_invalid_transitions() -> None:
    state = process_log(
        [
            Logout(1, "anna"),
            FileOpened(2, "anna", "/a.txt"),
            Login(3, "anna"),
            Login(4, "anna"),
        ]
    )
    assert state.invalid == 3
    assert (state.logins, state.logouts, state.files_opened) == (1, 0, 0)


def test_empty_log() -> None:
    assert process_log([]) == LogState()


def test_events_out_of_order() -> None:
    with pytest.raises(ValueError):
        process_log([Login(5, "anna"), Logout(3, "anna")])


def test_same_timestamp_is_allowed() -> None:
    state = process_log([Login(5, "anna"), FileOpened(5, "anna", "/a")])
    assert state.files_opened == 1


def test_reducer_does_not_change_input() -> None:
    before = LogState(active_users=frozenset({"anna"}), logins=1)
    after = reduce_event(before, Logout(2, "anna"))
    assert before == LogState(active_users=frozenset({"anna"}), logins=1)
    assert after is not before


def test_initial_state() -> None:
    start = LogState(active_users=frozenset({"root"}), last_timestamp=100)
    state = process_log([FileOpened(101, "root", "/etc/hosts")], start)
    assert state.files_opened == 1


def test_full_session() -> None:
    log: list[Event] = [
        Login(1, "anna"),
        Login(2, "petro"),
        FileOpened(3, "anna", "/a"),
        FileOpened(4, "petro", "/b"),
        ErrorEvent(5, "error", "x", ErrorEvent(4, "warning", "y")),
        Logout(6, "anna"),
    ]
    state = process_log(log)
    assert state.active_users == frozenset({"petro"})
    assert state.files_opened == 2
    assert state.errors == 1
    assert state.warnings == 0


def test_event_kind_and_stats() -> None:
    log: list[Event] = [
        Login(1, "a"),
        FileOpened(2, "a", "/x"),
        FileOpened(3, "a", "/y"),
        ErrorEvent(4, "critical", "z"),
        Logout(5, "a"),
    ]
    assert event_kind(log[0]) == "login"
    assert count_by_kind(log) == {"login": 1, "file": 2, "error": 1, "logout": 1}
    assert count_by_kind([]) == {}


def test_error_chain() -> None:
    first = ErrorEvent(1, "warning", "low space")
    chain = ErrorEvent(
        3, "critical", "stopped", ErrorEvent(2, "error", "failed", first)
    )
    assert root_cause(chain) is first
    assert chain_length(chain) == 3


def test_single_error_chain() -> None:
    error = ErrorEvent(1, "error", "alone")
    assert root_cause(error) is error
    assert chain_length(error) == 1
