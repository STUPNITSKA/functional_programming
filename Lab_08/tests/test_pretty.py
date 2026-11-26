from model import ErrorEvent, Event, FileOpened, Login, Logout, LogState
from pretty import render_event, render_log, render_state


def test_render_each_event() -> None:
    assert render_event(Login(5, "anna")) == "[   5] LOGIN    anna"
    assert render_event(Logout(15, "anna")) == "[  15] LOGOUT   anna"
    assert (
        render_event(FileOpened(7, "anna", "/a.txt")) == "[   7] OPEN     anna /a.txt"
    )
    assert render_event(ErrorEvent(9, "warning", "slow")) == "[   9] WARNING  slow"


def test_render_nested_error() -> None:
    error = ErrorEvent(3, "critical", "stopped", ErrorEvent(2, "error", "failed"))
    assert render_event(error) == ("[   3] CRITICAL stopped <- [   2] ERROR    failed")


def test_render_log() -> None:
    log: list[Event] = [Login(1, "a"), Logout(2, "a")]
    assert render_log(log) == "[   1] LOGIN    a\n[   2] LOGOUT   a"
    assert render_log([]) == ""


def test_render_state() -> None:
    text = render_state(LogState(active_users=frozenset({"b", "a"}), logins=2))
    assert "входів: 2" in text
    assert text.endswith("активні користувачі: a, b")
    assert render_state(LogState()).endswith("активні користувачі: -")
