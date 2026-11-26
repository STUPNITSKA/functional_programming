from evaluator import chain_length, count_by_kind, process_log, root_cause
from model import ErrorEvent, Event, FileOpened, Login, Logout
from pretty import render_log, render_state

DISK_ERROR = ErrorEvent(
    40,
    "critical",
    "сервіс зупинено",
    ErrorEvent(39, "error", "запис не вдався", ErrorEvent(38, "warning", "мало місця")),
)

LOG: tuple[Event, ...] = (
    Login(10, "anna"),
    FileOpened(12, "anna", "/docs/report.txt"),
    Login(15, "petro"),
    FileOpened(20, "petro", "/src/main.py"),
    ErrorEvent(25, "warning", "повільна відповідь диска"),
    FileOpened(27, "oleh", "/etc/passwd"),
    Logout(30, "anna"),
    Logout(31, "anna"),
    DISK_ERROR,
    Logout(45, "petro"),
)


def main() -> None:
    print(render_log(LOG))
    print()
    print(render_state(process_log(LOG)))
    print("статистика:", count_by_kind(LOG))
    print("довжина ланцюжка помилок:", chain_length(DISK_ERROR))
    print("першопричина:", root_cause(DISK_ERROR).message)


if __name__ == "__main__":
    main()
