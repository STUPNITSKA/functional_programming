from collections.abc import Callable

from closures import exponential_backoff, fixed_delay, make_counter, make_logger
from decorators import cached, retries, timed


def make_flaky_task(fail_times: int, result: str) -> Callable[[], str]:
    """Задача, яка перші fail_times разів падає з ConnectionError."""
    calls = make_counter()

    def task() -> str:
        n = calls()
        if n <= fail_times:
            raise ConnectionError(f"сервер недоступний (спроба {n})")
        return result

    return task


def main() -> None:
    log_retry = make_logger("планувальник")
    log_time = make_logger("час")

    fixed = fixed_delay(0.05)
    expo = exponential_backoff(0.01, 2.0, max_delay=0.1)
    print("фіксована затримка, спроби 1-5:", [fixed(i) for i in range(1, 6)])
    print("експоненційна затримка, спроби 1-5:", [expo(i) for i in range(1, 6)])

    backup_task = make_flaky_task(2, "копію збережено")
    sync_task = make_flaky_task(3, "дані синхронізовано")
    report_task = make_flaky_task(5, "звіт готовий")

    @timed("backup", logger=log_time)
    @retries(4, (ConnectionError,), policy=fixed, logger=log_retry)
    def backup() -> str:
        """Резервне копіювання з фіксованою затримкою."""
        return backup_task()

    @timed("sync", logger=log_time)
    @retries(4, (ConnectionError,), policy=expo, logger=log_retry)
    def sync() -> str:
        """Синхронізація з експоненційним backoff."""
        return sync_task()

    @timed("report", logger=log_time)
    @retries(2, (ConnectionError,), policy=fixed, logger=log_retry)
    def report() -> str:
        """Звіт, якому не вистачає двох спроб."""
        return report_task()

    print("backup:", backup())
    print("sync:", sync())
    try:
        report()
    except ConnectionError as e:
        print("report не виконано:", e)

    @cached(ttl=10.0)
    def square(x: int) -> int:
        return x * x

    print("кеш:", square(4), square(4))
    print("видалено з кешу:", square.cache_invalidate(lambda a, kw: a == (4,)))
    print("метадані:", backup.__name__, "|", backup.__doc__)


if __name__ == "__main__":
    main()
