from __future__ import annotations

from collections.abc import Iterable

from model import ErrorEvent, Event, FileOpened, Login, Logout, LogState, assert_never


def render_event(event: Event) -> str:
    """Один рядок журналу; причини помилки виводяться рекурсивно."""
    match event:
        case Login(timestamp=t, user=user):
            return f"[{t:>4}] LOGIN    {user}"
        case Logout(timestamp=t, user=user):
            return f"[{t:>4}] LOGOUT   {user}"
        case FileOpened(timestamp=t, user=user, path=path):
            return f"[{t:>4}] OPEN     {user} {path}"
        case ErrorEvent():
            return render_error(event)
        case _:
            assert_never(event)


def render_error(error: ErrorEvent) -> str:
    head = f"[{error.timestamp:>4}] {error.level.upper():<8} {error.message}"
    match error:
        case ErrorEvent(cause=ErrorEvent() as cause):
            return f"{head} <- {render_error(cause)}"
        case _:
            return head


def render_log(events: Iterable[Event]) -> str:
    return "\n".join(map(render_event, events))


def render_state(state: LogState) -> str:
    users = ", ".join(sorted(state.active_users)) or "-"
    return (
        f"входів: {state.logins}, виходів: {state.logouts}, "
        f"файлів: {state.files_opened}\n"
        f"warning: {state.warnings}, error: {state.errors}, "
        f"critical: {state.critical}, некоректних: {state.invalid}\n"
        f"активні користувачі: {users}"
    )
