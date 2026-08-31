from dataclasses import replace
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from trading_bot.data import (
    CANONICAL_SCHEMA_VERSION,
    CorporateAction,
    CorporateActionType,
    DailyBar,
    DatasetManifest,
    DatasetType,
    Instrument,
    ValidationResult,
)

SESSION_DAY = date(2026, 3, 5)
OPEN_UTC = datetime(2026, 3, 5, 14, 30, tzinfo=UTC)
CLOSE_UTC = datetime(2026, 3, 5, 21, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64


def make_instrument(**overrides: object) -> Instrument:
    fields: dict[str, object] = {
        "instrument_id": "US-ARCX-SPY",
        "symbol": "SPY",
        "exchange": "ARCX",
        "currency": "USD",
    }
    fields.update(overrides)
    return Instrument(**fields)  # type: ignore[arg-type]


def make_bar(**overrides: object) -> DailyBar:
    fields: dict[str, object] = {
        "instrument_id": "US-ARCX-SPY",
        "symbol": "SPY",
        "exchange": "ARCX",
        "currency": "USD",
        "session_date": SESSION_DAY,
        "bar_open_utc": OPEN_UTC,
        "bar_close_utc": CLOSE_UTC,
        "available_at_utc": CLOSE_UTC,
        "open": 500.0,
        "high": 505.0,
        "low": 499.0,
        "close": 503.0,
        "volume": 70_000_000,
        "adjusted_open": 499.5,
        "adjusted_high": 504.5,
        "adjusted_low": 498.5,
        "adjusted_close": 502.5,
        "adjusted_volume": 70_100_000.0,
        "provider_symbol": "SPY",
        "source_row_id": "row-1",
    }
    fields.update(overrides)
    return DailyBar(**fields)  # type: ignore[arg-type]


def make_action(**overrides: object) -> CorporateAction:
    fields: dict[str, object] = {
        "action_id": "act-1",
        "instrument_id": "US-ARCX-SPY",
        "action_type": CorporateActionType.CASH_DIVIDEND,
        "ex_date": SESSION_DAY,
        "record_date": date(2026, 3, 6),
        "pay_date": date(2026, 3, 20),
        "available_at_utc": CLOSE_UTC,
        "ratio": None,
        "cash_amount": Decimal("1.65"),
        "currency": "USD",
        "old_symbol": None,
        "new_symbol": None,
        "source_payload_ref": "raw/actions/act-1.json",
    }
    fields.update(overrides)
    return CorporateAction(**fields)  # type: ignore[arg-type]


def make_manifest(**overrides: object) -> DatasetManifest:
    fields: dict[str, object] = {
        "manifest_version": "1",
        "dataset_id": "daily_bars-" + HASH_A,
        "dataset_type": DatasetType.DAILY_BARS,
        "provider": "example-provider",
        "provider_dataset": "eod/daily",
        "request_parameters": (("end", "2026-03-05"), ("symbol", "SPY")),
        "retrieved_at_utc": CLOSE_UTC,
        "effective_start": date(2026, 1, 2),
        "effective_end": SESSION_DAY,
        "instrument_ids": ("US-ARCX-SPY",),
        "row_count": 44,
        "schema_name": "daily_bars",
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "calendar_name": "XNYS@2026.1",
        "adjustment_policy": "split-and-dividend@1",
        "source_hash": HASH_A,
        "content_hash": HASH_B,
        "parent_dataset_ids": (),
        "validation_result": ValidationResult.PASSED,
        "validation_report": "reports/validation/" + HASH_B + ".json",
        "license_reference": "docs/licenses/example-provider.md",
    }
    fields.update(overrides)
    return DatasetManifest(**fields)  # type: ignore[arg-type]


def test_canonical_schema_version_is_pinned() -> None:
    assert CANONICAL_SCHEMA_VERSION == "1"


def test_enum_members_are_stable_wire_values() -> None:
    assert [member.value for member in DatasetType] == [
        "DAILY_BARS",
        "CORPORATE_ACTIONS",
        "CALENDAR",
        "UNIVERSE",
    ]
    assert [member.value for member in ValidationResult] == ["NOT_RUN", "PASSED", "FAILED"]
    assert [member.value for member in CorporateActionType] == [
        "SPLIT",
        "CASH_DIVIDEND",
        "SYMBOL_CHANGE",
        "MERGER",
        "SPINOFF",
        "DELISTING",
    ]


def test_instrument_accepts_canonical_identity() -> None:
    instrument = make_instrument()

    assert instrument.instrument_id == "US-ARCX-SPY"
    assert instrument.currency == "USD"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"instrument_id": ""}, "instrument_id must be a non-empty trimmed value"),
        ({"instrument_id": " US-ARCX-SPY "}, "instrument_id must be a non-empty trimmed value"),
        ({"symbol": "spy"}, "symbol must be a canonical uppercase value"),
        ({"exchange": "arcx"}, "exchange must be a canonical uppercase value"),
        ({"currency": "usd"}, "currency must be an ISO 4217 alphabetic code"),
        ({"currency": "USDX"}, "currency must be an ISO 4217 alphabetic code"),
    ],
)
def test_instrument_rejects_invalid_identity(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_instrument(**overrides)


def test_bar_normalizes_aware_timestamps_to_utc() -> None:
    eastern = timezone(timedelta(hours=-5))
    bar = make_bar(
        bar_open_utc=OPEN_UTC.astimezone(eastern),
        bar_close_utc=CLOSE_UTC.astimezone(eastern),
        available_at_utc=CLOSE_UTC.astimezone(eastern),
    )

    assert bar.bar_open_utc == OPEN_UTC
    assert bar.bar_close_utc == CLOSE_UTC
    assert bar.bar_close_utc.tzinfo is UTC
    assert bar.session_date == SESSION_DAY


def test_bar_allows_availability_after_the_session_close() -> None:
    bar = make_bar(available_at_utc=CLOSE_UTC + timedelta(hours=2))

    assert bar.available_at_utc == CLOSE_UTC + timedelta(hours=2)


def test_bar_rejects_availability_before_its_own_close() -> None:
    with pytest.raises(ValueError, match="available_at_utc must not precede bar_close_utc"):
        make_bar(available_at_utc=CLOSE_UTC - timedelta(seconds=1))


def test_bar_accepts_a_missing_source_row_id() -> None:
    assert make_bar(source_row_id=None).source_row_id is None


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"instrument_id": " "}, "instrument_id must be a non-empty trimmed value"),
        ({"symbol": "spy"}, "symbol must be a canonical uppercase value"),
        ({"exchange": "arcx"}, "exchange must be a canonical uppercase value"),
        ({"currency": "US"}, "currency must be an ISO 4217 alphabetic code"),
        ({"provider_symbol": ""}, "provider_symbol must be a non-empty trimmed value"),
        ({"source_row_id": ""}, "source_row_id must be a non-empty trimmed value"),
        ({"bar_open_utc": datetime(2026, 3, 5, 14, 30)}, "bar_open_utc must be timezone-aware"),
        ({"bar_close_utc": datetime(2026, 3, 5, 21, 0)}, "bar_close_utc must be timezone-aware"),
        (
            {"available_at_utc": datetime(2026, 3, 5, 21, 0)},
            "available_at_utc must be timezone-aware",
        ),
        ({"bar_open_utc": CLOSE_UTC}, "bar_open_utc must be before bar_close_utc"),
    ],
)
def test_bar_rejects_invalid_fields(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_bar(**overrides)


@pytest.mark.parametrize(
    "field_name",
    [
        "open",
        "high",
        "low",
        "close",
        "adjusted_open",
        "adjusted_high",
        "adjusted_low",
        "adjusted_close",
        "adjusted_volume",
    ],
)
@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_bar_rejects_non_finite_numbers(field_name: str, bad_value: float) -> None:
    with pytest.raises(ValueError, match=f"{field_name} must be a finite number"):
        make_bar(**{field_name: bad_value})


def test_bar_leaves_validation_rule_violations_representable() -> None:
    # DV-004 and DV-005 must be able to report offending canonical rows, so a
    # crossed or negative row is normalized here and quarantined by the validator.
    crossed = make_bar(low=600.0, high=100.0, volume=-1, open=-5.0)

    assert crossed.low > crossed.high
    assert crossed.volume == -1


def test_action_normalizes_availability_and_keeps_local_dates() -> None:
    india = timezone(timedelta(hours=5, minutes=30))
    action = make_action(available_at_utc=CLOSE_UTC.astimezone(india))

    assert action.available_at_utc == CLOSE_UTC
    assert action.ex_date == SESSION_DAY
    assert action.record_date == date(2026, 3, 6)


def test_action_accepts_a_split_with_a_ratio() -> None:
    action = make_action(
        action_type=CorporateActionType.SPLIT,
        ratio=Decimal("4"),
        cash_amount=None,
        currency=None,
    )

    assert action.ratio == Decimal("4")


def test_action_accepts_a_symbol_change() -> None:
    action = make_action(
        action_type=CorporateActionType.SYMBOL_CHANGE,
        cash_amount=None,
        currency=None,
        old_symbol="OLD",
        new_symbol="NEW",
    )

    assert (action.old_symbol, action.new_symbol) == ("OLD", "NEW")


def test_action_accepts_absent_optional_dates() -> None:
    action = make_action(record_date=None, pay_date=None)

    assert action.record_date is None
    assert action.pay_date is None


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"action_id": ""}, "action_id must be a non-empty trimmed value"),
        ({"instrument_id": ""}, "instrument_id must be a non-empty trimmed value"),
        ({"source_payload_ref": " "}, "source_payload_ref must be a non-empty trimmed value"),
        ({"old_symbol": ""}, "old_symbol must be a non-empty trimmed value"),
        ({"new_symbol": " NEW"}, "new_symbol must be a non-empty trimmed value"),
        (
            {"available_at_utc": datetime(2026, 3, 5, 21, 0)},
            "available_at_utc must be timezone-aware",
        ),
        ({"ratio": Decimal("0")}, "ratio must be positive when present"),
        ({"cash_amount": Decimal("-0.01")}, "cash_amount must not be negative"),
        ({"currency": None}, "currency must be present exactly when cash_amount is"),
        (
            {"cash_amount": None, "currency": "USD"},
            "currency must be present exactly when cash_amount is",
        ),
        ({"currency": "usd"}, "currency must be an ISO 4217 alphabetic code"),
        (
            {"action_type": CorporateActionType.SPLIT, "cash_amount": None, "currency": None},
            "split requires a ratio",
        ),
        (
            {"action_type": CorporateActionType.CASH_DIVIDEND, "cash_amount": None,
             "currency": None},
            "cash dividend requires a cash_amount",
        ),
        (
            {"action_type": CorporateActionType.SYMBOL_CHANGE, "cash_amount": None,
             "currency": None, "old_symbol": "OLD"},
            "symbol change requires old_symbol and new_symbol",
        ),
        (
            {"action_type": CorporateActionType.SYMBOL_CHANGE, "cash_amount": None,
             "currency": None, "old_symbol": "SAME", "new_symbol": "SAME"},
            "symbol change requires different symbols",
        ),
    ],
)
def test_action_rejects_invalid_fields(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_action(**overrides)


def test_manifest_accepts_complete_lineage() -> None:
    manifest = make_manifest()

    assert manifest.dataset_type is DatasetType.DAILY_BARS
    assert manifest.validation_result is ValidationResult.PASSED
    assert manifest.content_hash == HASH_B
    assert manifest.retrieved_at_utc.tzinfo is UTC


def test_manifest_accepts_derived_lineage_and_an_empty_request() -> None:
    manifest = make_manifest(
        dataset_type=DatasetType.CALENDAR,
        parent_dataset_ids=("bars-" + HASH_A, "raw-" + HASH_B),
        request_parameters=(),
        row_count=0,
    )

    assert manifest.parent_dataset_ids[0] == "bars-" + HASH_A
    assert manifest.request_parameters == ()


def test_manifest_records_a_failed_validation_without_publishing_it() -> None:
    manifest = make_manifest(validation_result=ValidationResult.FAILED)

    assert manifest.validation_result is ValidationResult.FAILED


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"manifest_version": ""}, "manifest_version must be a non-empty trimmed value"),
        ({"dataset_id": " "}, "dataset_id must be a non-empty trimmed value"),
        ({"provider": ""}, "provider must be a non-empty trimmed value"),
        ({"provider_dataset": ""}, "provider_dataset must be a non-empty trimmed value"),
        ({"schema_name": ""}, "schema_name must be a non-empty trimmed value"),
        ({"schema_version": ""}, "schema_version must be a non-empty trimmed value"),
        ({"calendar_name": ""}, "calendar_name must be a non-empty trimmed value"),
        ({"adjustment_policy": ""}, "adjustment_policy must be a non-empty trimmed value"),
        ({"validation_report": ""}, "validation_report must be a non-empty trimmed value"),
        ({"license_reference": ""}, "license_reference must be a non-empty trimmed value"),
        ({"source_hash": "A" * 64}, "source_hash must be a lowercase SHA-256 hexadecimal digest"),
        ({"content_hash": "abc"}, "content_hash must be a lowercase SHA-256 hexadecimal digest"),
        (
            {"retrieved_at_utc": datetime(2026, 3, 5, 21, 0)},
            "retrieved_at_utc must be timezone-aware",
        ),
        (
            {"effective_start": date(2026, 3, 6)},
            "effective_start must not be after effective_end",
        ),
        ({"row_count": -1}, "row_count must not be negative"),
        ({"instrument_ids": ()}, "instrument_ids must not be empty"),
        ({"instrument_ids": ("",)}, "instrument_ids entry must be a non-empty trimmed value"),
        ({"instrument_ids": ("B", "A")}, "instrument_ids must be sorted"),
        ({"instrument_ids": ("A", "A")}, "instrument_ids must not contain duplicates"),
        ({"parent_dataset_ids": ("B", "A")}, "parent_dataset_ids must be sorted"),
    ],
)
def test_manifest_rejects_invalid_fields(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_manifest(**overrides)


def test_manifest_rejects_self_parentage() -> None:
    manifest = make_manifest()

    with pytest.raises(ValueError, match="parent_dataset_ids must not contain the dataset itself"):
        make_manifest(parent_dataset_ids=(manifest.dataset_id,))


@pytest.mark.parametrize(
    "secret_key",
    ["api_key", "apiKey", "access-key", "token", "authorization", "client_secret", "signature"],
)
def test_manifest_rejects_secret_like_request_keys(secret_key: str) -> None:
    with pytest.raises(ValueError, match="must not carry secret key"):
        make_manifest(request_parameters=((secret_key, "redacted"),))


@pytest.mark.parametrize(
    ("request_parameters", "message"),
    [
        ((("", "x"),), "request_parameters key must be a non-empty trimmed value"),
        ((("symbol", "SPY"), ("end", "2026-03-05")), "request_parameters must be sorted"),
        ((("symbol", "SPY"), ("symbol", "QQQ")), "request_parameters must not contain duplicates"),
    ],
)
def test_manifest_rejects_a_non_canonical_request(
    request_parameters: tuple[tuple[str, str], ...], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        make_manifest(request_parameters=request_parameters)


def test_schema_values_are_frozen() -> None:
    bar = make_bar()

    with pytest.raises(AttributeError):
        bar.close = 1.0  # type: ignore[misc]

    assert replace(bar, close=1.0).close == 1.0
