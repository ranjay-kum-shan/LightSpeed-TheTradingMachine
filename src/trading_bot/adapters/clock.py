"""Clock adapters for production and deterministic tests."""

from datetime import UTC, datetime, timedelta

from trading_bot.domain.time import ensure_utc


class SystemClock:
    """Host wall clock, always returned as aware UTC."""

    def now_utc(self) -> datetime:
        return datetime.now(UTC)


class ManualClock:
    """Deterministic clock; time moves only when a caller advances it."""

    def __init__(self, start: datetime) -> None:
        self._now = ensure_utc(start, "start")

    def now_utc(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> datetime:
        if delta < timedelta(0):
            raise ValueError("delta must not be negative")
        self._now += delta
        return self._now

    def set_to(self, instant: datetime) -> datetime:
        moment = ensure_utc(instant, "instant")
        if moment < self._now:
            raise ValueError("clock must not move backwards")
        self._now = moment
        return self._now
