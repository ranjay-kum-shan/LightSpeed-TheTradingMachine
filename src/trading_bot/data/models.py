"""Canonical market-data schemas for instruments, bars, actions, and manifests.

These values are the ``NORMALIZED`` stage of the dataset lifecycle, not the
``VALIDATING`` stage. Two kinds of rule are enforced here and no others:

1. Representational rules, without which the value has no defined meaning -
   naive timestamps, non-finite numbers, malformed enums or currency codes, and
   degenerate intervals.
2. One safety rule: a bar may not claim availability before its own session
   close. No ``DV-*`` rule covers availability ordering, so nothing downstream
   would catch lookahead, and unlike a crossed high and low it cannot be
   reviewed into acceptance.

Everything else the twelve mandatory validation rules cover stays representable
so the dataset validator can report and quarantine offending canonical rows.
"""

import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from trading_bot.domain.time import ensure_utc

CANONICAL_SCHEMA_VERSION = "1"

_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1
_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_SEPARATORS = re.compile(r"[^0-9a-z]+")
_SECRET_KEY_NAMES = frozenset(
    {
        "auth",
        "bearer",
        "jwt",
        "key",
        "pwd",
        "sig",
        "signature",
        "token",
        "accesstoken",
        "idtoken",
        "refreshtoken",
        "sessiontoken",
    }
)
_SECRET_KEY_FRAGMENTS = (
    "accesskey",
    "apikey",
    "authorization",
    "credential",
    "passphrase",
    "passwd",
    "password",
    "privatekey",
    "secret",
)


def _require_text(value: str, field_name: str) -> str:
    if not value or value != value.strip():
        raise ValueError(f"{field_name} must be a non-empty trimmed value")
    return value


def _require_upper_text(value: str, field_name: str) -> str:
    _require_text(value, field_name)
    if value != value.upper():
        raise ValueError(f"{field_name} must be a canonical uppercase value")
    return value


def _require_currency(value: str, field_name: str) -> str:
    if not _CURRENCY_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} must be an ISO 4217 alphabetic code")
    return value


def _require_sha256(value: str, field_name: str) -> str:
    if not _SHA256_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 hexadecimal digest")
    return value


def _require_finite(value: float, field_name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be a finite number")
    return value


def _require_finite_decimal(value: Decimal, field_name: str) -> Decimal:
    # Comparing a Decimal NaN raises InvalidOperation, so this must run first.
    if not value.is_finite():
        raise ValueError(f"{field_name} must be a finite number")
    return value


def _require_int64(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not _INT64_MIN <= value <= _INT64_MAX:
        raise ValueError(f"{field_name} must be an integer representable in 64 bits")
    return value


def _require_sorted_unique(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        _require_text(value, f"{field_name} entry")
    if len(set(values)) != len(values):
        raise ValueError(f"{field_name} must not contain duplicates")
    if list(values) != sorted(values):
        raise ValueError(f"{field_name} must be sorted")


def _is_secret_key(key: str) -> bool:
    normalized = _SEPARATORS.sub("", key.lower())
    if normalized in _SECRET_KEY_NAMES:
        return True
    return any(fragment in normalized for fragment in _SECRET_KEY_FRAGMENTS)


class DatasetType(StrEnum):
    DAILY_BARS = "DAILY_BARS"
    CORPORATE_ACTIONS = "CORPORATE_ACTIONS"
    CALENDAR = "CALENDAR"
    UNIVERSE = "UNIVERSE"


class ValidationResult(StrEnum):
    NOT_RUN = "NOT_RUN"
    PASSED = "PASSED"
    FAILED = "FAILED"


class CorporateActionType(StrEnum):
    SPLIT = "SPLIT"
    CASH_DIVIDEND = "CASH_DIVIDEND"
    SYMBOL_CHANGE = "SYMBOL_CHANGE"
    MERGER = "MERGER"
    SPINOFF = "SPINOFF"
    DELISTING = "DELISTING"


@dataclass(frozen=True, slots=True)
class Instrument:
    """Stable internal identity; provider symbols are dated aliases of it."""

    instrument_id: str
    symbol: str
    exchange: str
    currency: str

    def __post_init__(self) -> None:
        _require_text(self.instrument_id, "instrument_id")
        _require_upper_text(self.symbol, "symbol")
        _require_upper_text(self.exchange, "exchange")
        _require_currency(self.currency, "currency")


@dataclass(frozen=True, slots=True)
class DailyBar:
    """One canonical daily row carrying both the raw and the adjusted series."""

    instrument_id: str
    symbol: str
    exchange: str
    currency: str
    session_date: date
    bar_open_utc: datetime
    bar_close_utc: datetime
    available_at_utc: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_open: float
    adjusted_high: float
    adjusted_low: float
    adjusted_close: float
    adjusted_volume: float
    provider_symbol: str
    source_row_id: str | None

    def __post_init__(self) -> None:
        _require_text(self.instrument_id, "instrument_id")
        _require_upper_text(self.symbol, "symbol")
        _require_upper_text(self.exchange, "exchange")
        _require_currency(self.currency, "currency")
        _require_text(self.provider_symbol, "provider_symbol")
        if self.source_row_id is not None:
            _require_text(self.source_row_id, "source_row_id")
        for field_name, field_value in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
            ("adjusted_open", self.adjusted_open),
            ("adjusted_high", self.adjusted_high),
            ("adjusted_low", self.adjusted_low),
            ("adjusted_close", self.adjusted_close),
            ("adjusted_volume", self.adjusted_volume),
        ):
            _require_finite(field_value, field_name)
        _require_int64(self.volume, "volume")
        object.__setattr__(self, "bar_open_utc", ensure_utc(self.bar_open_utc, "bar_open_utc"))
        object.__setattr__(self, "bar_close_utc", ensure_utc(self.bar_close_utc, "bar_close_utc"))
        object.__setattr__(
            self, "available_at_utc", ensure_utc(self.available_at_utc, "available_at_utc")
        )
        if self.bar_open_utc >= self.bar_close_utc:
            raise ValueError("bar_open_utc must be before bar_close_utc")
        # A complete session bar cannot be known before that session has closed.
        if self.available_at_utc < self.bar_close_utc:
            raise ValueError("available_at_utc must not precede bar_close_utc")


@dataclass(frozen=True, slots=True)
class CorporateAction:
    """One corporate action; announcement availability and effective date differ."""

    action_id: str
    instrument_id: str
    action_type: CorporateActionType
    ex_date: date
    record_date: date | None
    pay_date: date | None
    available_at_utc: datetime
    ratio: Decimal | None
    cash_amount: Decimal | None
    currency: str | None
    old_symbol: str | None
    new_symbol: str | None
    source_payload_ref: str

    def __post_init__(self) -> None:
        _require_text(self.action_id, "action_id")
        _require_text(self.instrument_id, "instrument_id")
        _require_text(self.source_payload_ref, "source_payload_ref")
        for field_name, field_value in (
            ("old_symbol", self.old_symbol),
            ("new_symbol", self.new_symbol),
        ):
            if field_value is not None:
                _require_text(field_value, field_name)
        object.__setattr__(
            self, "available_at_utc", ensure_utc(self.available_at_utc, "available_at_utc")
        )
        if self.ratio is not None:
            _require_finite_decimal(self.ratio, "ratio")
            if self.ratio <= 0:
                raise ValueError("ratio must be positive when present")
        if self.cash_amount is not None:
            _require_finite_decimal(self.cash_amount, "cash_amount")
            if self.cash_amount < 0:
                raise ValueError("cash_amount must not be negative")
        if (self.cash_amount is None) != (self.currency is None):
            raise ValueError("currency must be present exactly when cash_amount is")
        if self.currency is not None:
            _require_currency(self.currency, "currency")
        self._require_type_completeness()

    def _require_type_completeness(self) -> None:
        if self.action_type is CorporateActionType.SPLIT and self.ratio is None:
            raise ValueError("split requires a ratio")
        if self.action_type is CorporateActionType.CASH_DIVIDEND and self.cash_amount is None:
            raise ValueError("cash dividend requires a cash_amount")
        if self.action_type is CorporateActionType.SYMBOL_CHANGE:
            if self.old_symbol is None or self.new_symbol is None:
                raise ValueError("symbol change requires old_symbol and new_symbol")
            if self.old_symbol.casefold() == self.new_symbol.casefold():
                raise ValueError("symbol change requires different symbols")


@dataclass(frozen=True, slots=True)
class DatasetManifest:
    """Immutable lineage record identifying one published or quarantined dataset."""

    manifest_version: str
    dataset_id: str
    dataset_type: DatasetType
    provider: str
    provider_dataset: str
    request_parameters: tuple[tuple[str, str], ...]
    retrieved_at_utc: datetime
    effective_start: date
    effective_end: date
    instrument_ids: tuple[str, ...]
    row_count: int
    schema_name: str
    schema_version: str
    calendar_name: str
    adjustment_policy: str
    source_hash: str
    content_hash: str
    parent_dataset_ids: tuple[str, ...]
    validation_result: ValidationResult
    validation_report: str
    license_reference: str

    def __post_init__(self) -> None:
        for field_name, field_value in (
            ("manifest_version", self.manifest_version),
            ("dataset_id", self.dataset_id),
            ("provider", self.provider),
            ("provider_dataset", self.provider_dataset),
            ("schema_name", self.schema_name),
            ("schema_version", self.schema_version),
            ("calendar_name", self.calendar_name),
            ("adjustment_policy", self.adjustment_policy),
            ("validation_report", self.validation_report),
            ("license_reference", self.license_reference),
        ):
            _require_text(field_value, field_name)
        _require_text(self.source_hash, "source_hash")
        _require_sha256(self.content_hash, "content_hash")
        object.__setattr__(
            self, "retrieved_at_utc", ensure_utc(self.retrieved_at_utc, "retrieved_at_utc")
        )
        if self.effective_start > self.effective_end:
            raise ValueError("effective_start must not be after effective_end")
        # One day of slack because session dates are exchange-local, not UTC.
        if self.effective_end > self.retrieved_at_utc.date() + timedelta(days=1):
            raise ValueError("effective_end must not postdate retrieved_at_utc")
        _require_int64(self.row_count, "row_count")
        if self.row_count < 0:
            raise ValueError("row_count must not be negative")
        _require_sorted_unique(self.instrument_ids, "instrument_ids")
        _require_sorted_unique(self.parent_dataset_ids, "parent_dataset_ids")
        if self.dataset_id in self.parent_dataset_ids:
            raise ValueError("parent_dataset_ids must not contain the dataset itself")
        self._require_canonical_request()

    def _require_canonical_request(self) -> None:
        keys = tuple(key for key, _ in self.request_parameters)
        for key, value in self.request_parameters:
            _require_text(key, "request_parameters key")
            if value != value.strip():
                raise ValueError("request_parameters value must be trimmed")
            # Key-name guard only; the audit redaction boundary is separate.
            if _is_secret_key(key):
                raise ValueError(f"request_parameters must not carry secret key {key!r}")
        _require_sorted_unique(keys, "request_parameters")
