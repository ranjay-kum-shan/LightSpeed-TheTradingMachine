"""Deterministic in-memory exchange calendar."""

from bisect import bisect_right
from collections.abc import Iterable
from datetime import datetime
from itertools import pairwise

from trading_bot.domain.time import ExchangeSession, ensure_utc


class StaticExchangeCalendar:
    """Sessions are supplied explicitly; any date without one is a non-trading day."""

    def __init__(
        self,
        name: str,
        version: str,
        sessions: Iterable[ExchangeSession],
    ) -> None:
        if not name or name != name.strip():
            raise ValueError("name must be a non-empty trimmed value")
        if not version or version != version.strip():
            raise ValueError("version must be a non-empty trimmed value")
        ordered = tuple(sorted(sessions, key=lambda session: session.open_utc))
        if not ordered:
            raise ValueError("sessions must not be empty")
        if len({session.session_date for session in ordered}) != len(ordered):
            raise ValueError("sessions must contain at most one row per session date")
        for earlier, later in pairwise(ordered):
            if earlier.close_utc > later.open_utc:
                raise ValueError("sessions must not overlap")
        self._name = name
        self._version = version
        self._sessions = ordered
        self._opens = [session.open_utc for session in ordered]

    @property
    def calendar_name(self) -> str:
        return self._name

    @property
    def calendar_version(self) -> str:
        return self._version

    def session_at(self, instant: datetime) -> ExchangeSession | None:
        moment = ensure_utc(instant, "instant")
        index = bisect_right(self._opens, moment) - 1
        if index < 0:
            return None
        session = self._sessions[index]
        return session if session.contains(moment) else None

    def is_open(self, instant: datetime) -> bool:
        return self.session_at(instant) is not None
