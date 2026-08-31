import json
from datetime import UTC, datetime, timedelta, timezone

import pytest

from trading_bot.audit import (
    AUDIT_SCHEMA_VERSION,
    REDACTED,
    AuditEvent,
    RedactionFailure,
    Redactor,
    Severity,
    is_secret_name,
    serialize_event,
)
from trading_bot.config import OperatingMode
from trading_bot.domain import ReasonCode

CANARY = "canary-sk-live-0123456789abcdef"
OTHER_CANARY = "canary-refresh-fedcba9876543210"
OCCURRED = datetime(2026, 3, 5, 14, 30, tzinfo=UTC)
RECORDED = datetime(2026, 3, 5, 14, 30, 1, tzinfo=UTC)


def make_redactor(*secrets: str) -> Redactor:
    return Redactor(known_secrets=secrets or (CANARY,))


def make_event(**overrides: object) -> AuditEvent:
    fields: dict[str, object] = {
        "event_id": "01J0000000000000000000000A",
        "event_type": "risk.order.evaluated",
        "occurred_at_utc": OCCURRED,
        "recorded_at_utc": RECORDED,
        "severity": Severity.INFO,
        "mode": OperatingMode.PAPER,
        "component": "risk.engine",
        "payload": {"symbol": "SPY", "quantity": 10},
        "session_id": "session-1",
    }
    fields.update(overrides)
    return AuditEvent(**fields)  # type: ignore[arg-type]


def make_decision_event(**overrides: object) -> AuditEvent:
    fields: dict[str, object] = {
        "event_type": "decision.order.rejected",
        "reason_code": ReasonCode.ORDER_NOTIONAL_LIMIT,
        "strategy_id": "ma-cross@1",
        "git_revision": "678fdf5",
        "config_hash": "c" * 12,
        "data_hash": "d" * 12,
        "payload": {"projected_notional": "12000.00"},
    }
    fields.update(overrides)
    return make_event(**fields)


def test_schema_version_is_pinned() -> None:
    assert AUDIT_SCHEMA_VERSION == "1"
    assert make_event().schema_version == "1"


def test_severity_members_are_stable_wire_values() -> None:
    assert [member.value for member in Severity] == [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]


@pytest.mark.parametrize(
    "name",
    [
        "api_key",
        "apiKey",
        "access-key",
        "app_key",
        "auth_key",
        "authorization",
        "bearer",
        "consumer_key",
        "cookie",
        "credentials",
        "jwt",
        "key",
        "passphrase",
        "passwd",
        "password",
        "private_key",
        "pwd",
        "session_key",
        "shared_key",
        "sig",
        "signature",
        "Ocp-Apim-Subscription-Key",
        "token",
        "api_token",
        "auth_token",
        "bearer_token",
        "access_token",
        "security_token",
        "client_secret",
    ],
)
def test_is_secret_name_flags_credential_names(name: str) -> None:
    assert is_secret_name(name) is True


@pytest.mark.parametrize(
    "name",
    [
        "page_token",
        "next_page_token",
        "next_token",
        "continuation_token",
        "sort_key",
        "partition_key",
        "keys",
        "keyword",
        "monkey",
        "turnkey",
        "author",
        "authority",
        "signal",
        "sigma",
        "bearer_bond",
        "symbol",
        "quantity",
        "session_id",
    ],
)
def test_is_secret_name_allows_ordinary_names(name: str) -> None:
    assert is_secret_name(name) is False


def test_redactor_rejects_a_too_short_known_secret() -> None:
    with pytest.raises(ValueError, match="at least 4 characters"):
        Redactor(known_secrets=("ab",))


def test_redactor_orders_known_secrets_longest_first() -> None:
    redactor = Redactor(known_secrets=("abcd", "abcdefgh"))

    assert redactor.known_secrets == ("abcdefgh", "abcd")


def test_redactor_masks_a_canary_inside_a_nested_mapping() -> None:
    redactor = make_redactor()

    redacted = redactor.redact({"outer": {"inner": {"note": f"value {CANARY} tail"}}})

    assert redacted == {"outer": {"inner": {"note": f"value {REDACTED} tail"}}}


def test_redactor_masks_a_canary_inside_an_array() -> None:
    redactor = make_redactor()

    redacted = redactor.redact(["safe", [CANARY], ("nested", CANARY)])

    assert redacted == ["safe", [REDACTED], ["nested", REDACTED]]


def test_redactor_masks_a_secret_named_key_value_at_any_depth() -> None:
    redactor = Redactor()

    redacted = redactor.redact({"request": {"api_key": "live-value", "symbol": "SPY"}})

    assert redacted == {"request": {"api_key": REDACTED, "symbol": "SPY"}}


def test_redactor_masks_a_url_query_secret_without_a_known_literal() -> None:
    redactor = Redactor()

    redacted = redactor.redact_text("https://host/v2/bars?symbol=SPY&apikey=live-value")

    assert redacted == f"https://host/v2/bars?symbol=SPY&apikey={REDACTED}"


def test_redactor_masks_url_userinfo() -> None:
    redactor = Redactor()

    redacted = redactor.redact_text("https://user:supersecret@host/path")

    assert redacted == f"https://user:{REDACTED}@host/path"


@pytest.mark.parametrize("scheme", ["Bearer", "bearer", "Basic", "Digest", "Token"])
def test_redactor_masks_an_authorization_scheme_value(scheme: str) -> None:
    redactor = Redactor()

    redacted = redactor.redact_text(f"Authorization: {scheme} abc123.def456")

    assert "abc123.def456" not in redacted
    assert REDACTED in redacted


def test_redactor_masks_a_canary_inside_a_multiline_string() -> None:
    redactor = make_redactor()
    blob = f"line one\nAuthorization: Bearer {CANARY}\nline three"

    redacted = redactor.redact_text(blob)

    assert CANARY not in redacted
    assert redacted.startswith("line one\n")


def test_redactor_masks_a_canary_used_as_a_mapping_key() -> None:
    redactor = make_redactor()

    redacted = redactor.redact({CANARY: "value"})

    assert redacted == {REDACTED: "value"}


def test_redactor_passes_through_allowlisted_scalars() -> None:
    redactor = Redactor()

    assert redactor.redact({"a": 1, "b": 1.5, "c": True, "d": None}) == {
        "a": 1,
        "b": 1.5,
        "c": True,
        "d": None,
    }


class _Sdk:
    def __repr__(self) -> str:  # pragma: no cover - must never be reached
        return f"secret={CANARY}"


@pytest.mark.parametrize(
    "value",
    [
        _Sdk(),
        Exception("boom"),
        {"nested": _Sdk()},
        [_Sdk()],
        {"when": OCCURRED},
        {"choices"},
    ],
)
def test_redactor_refuses_a_non_allowlisted_value(value: object) -> None:
    redactor = make_redactor()

    with pytest.raises(RedactionFailure, match="not an allowlisted audit value"):
        redactor.redact(value)


def test_redactor_records_a_string_enum_as_its_wire_value() -> None:
    redacted = Redactor().redact({"mode": OperatingMode.PAPER})

    assert redacted == {"mode": "PAPER"}
    assert json.dumps(redacted) == '{"mode": "PAPER"}'


@pytest.mark.parametrize("value", [b"raw", bytearray(b"raw"), memoryview(b"raw")])
def test_redactor_refuses_binary_values(value: object) -> None:
    with pytest.raises(RedactionFailure, match="binary values are never recorded"):
        Redactor().redact(value)


def test_redactor_refuses_a_non_string_mapping_key() -> None:
    with pytest.raises(RedactionFailure, match="mapping keys must be strings"):
        Redactor().redact({1: "value"})


def test_assert_clean_raises_when_a_secret_survives() -> None:
    redactor = make_redactor()

    with pytest.raises(RedactionFailure, match="survived redaction"):
        redactor.assert_clean(f"leaked {CANARY}")


def test_assert_clean_accepts_a_clean_rendering() -> None:
    make_redactor().assert_clean("nothing to see")


def test_event_normalizes_aware_timestamps_to_utc() -> None:
    eastern = timezone(timedelta(hours=-5))
    event = make_event(
        occurred_at_utc=OCCURRED.astimezone(eastern),
        recorded_at_utc=RECORDED.astimezone(eastern),
    )

    assert event.occurred_at_utc == OCCURRED
    assert event.recorded_at_utc.tzinfo is UTC


def test_event_allows_equal_occurrence_and_record_times() -> None:
    assert make_event(recorded_at_utc=OCCURRED).recorded_at_utc == OCCURRED


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"event_id": ""}, "event_id must be a non-empty trimmed value"),
        ({"schema_version": " "}, "schema_version must be a non-empty trimmed value"),
        ({"component": ""}, "component must be a non-empty trimmed value"),
        ({"event_type": "Risk.Order"}, "event_type must be a stable dotted lowercase name"),
        ({"event_type": "risk"}, "event_type must be a stable dotted lowercase name"),
        ({"event_type": "risk..order"}, "event_type must be a stable dotted lowercase name"),
        ({"session_id": ""}, "session_id must be a non-empty trimmed value"),
        ({"run_id": " x"}, "run_id must be a non-empty trimmed value"),
        ({"correlation_id": ""}, "correlation_id must be a non-empty trimmed value"),
        ({"git_revision": ""}, "git_revision must be a non-empty trimmed value"),
        ({"config_hash": ""}, "config_hash must be a non-empty trimmed value"),
        ({"data_hash": ""}, "data_hash must be a non-empty trimmed value"),
        ({"strategy_id": ""}, "strategy_id must be a non-empty trimmed value"),
        ({"account_fingerprint": ""}, "account_fingerprint must be a non-empty trimmed value"),
        (
            {"occurred_at_utc": datetime(2026, 3, 5, 14, 30)},
            "occurred_at_utc must be timezone-aware",
        ),
        (
            {"recorded_at_utc": datetime(2026, 3, 5, 14, 30)},
            "recorded_at_utc must be timezone-aware",
        ),
        (
            {"recorded_at_utc": OCCURRED - timedelta(seconds=1)},
            "recorded_at_utc must not precede occurred_at_utc",
        ),
        ({"payload": {"api_key": "x"}}, "payload must not carry secret key"),
    ],
)
def test_event_rejects_invalid_fields(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_event(**overrides)


def test_event_requires_run_id_in_backtest_mode() -> None:
    with pytest.raises(ValueError, match="run_id is required for backtest events"):
        make_event(mode=OperatingMode.BACKTEST, session_id=None)


@pytest.mark.parametrize("mode", [OperatingMode.PAPER, OperatingMode.RECOVERY])
def test_event_requires_session_id_in_session_modes(mode: OperatingMode) -> None:
    with pytest.raises(ValueError, match="session_id is required for session-scoped events"):
        make_event(mode=mode, session_id=None)


def test_event_requires_neither_identity_when_halted() -> None:
    event = make_event(mode=OperatingMode.HALTED, session_id=None)

    assert event.session_id is None
    assert event.run_id is None


def test_backtest_event_accepts_a_run_id() -> None:
    event = make_event(mode=OperatingMode.BACKTEST, session_id=None, run_id="run-1")

    assert event.run_id == "run-1"


def test_decision_event_accepts_a_complete_record() -> None:
    event = make_decision_event()

    assert event.is_decision is True
    assert event.reason_code is ReasonCode.ORDER_NOTIONAL_LIMIT


def test_non_decision_event_is_not_marked_as_a_decision() -> None:
    assert make_event().is_decision is False


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        ("strategy_id", "strategy_id is required for a decision event"),
        ("git_revision", "git_revision is required for a decision event"),
        ("config_hash", "config_hash is required for a decision event"),
        ("data_hash", "data_hash is required for a decision event"),
        ("reason_code", "reason_code is required for a decision event"),
    ],
)
def test_decision_event_requires_full_lineage(field_name: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_decision_event(**{field_name: None})


def test_decision_event_requires_inputs() -> None:
    with pytest.raises(ValueError, match="payload is required for a decision event"):
        make_decision_event(payload={})


def test_serialized_event_is_one_json_line_with_contract_fields() -> None:
    rendered = serialize_event(make_decision_event(), make_redactor())

    assert "\n" not in rendered
    record = json.loads(rendered)
    assert list(record) == [
        "schema_version",
        "event_id",
        "event_type",
        "occurred_at_utc",
        "recorded_at_utc",
        "severity",
        "mode",
        "session_id",
        "run_id",
        "correlation_id",
        "component",
        "reason_code",
        "git_revision",
        "config_hash",
        "data_hash",
        "strategy_id",
        "account_fingerprint",
        "payload",
    ]
    assert record["reason_code"] == "ORDER_NOTIONAL_LIMIT"
    assert record["occurred_at_utc"] == "2026-03-05T14:30:00+00:00"


def test_serialized_event_omits_no_optional_field_but_renders_null() -> None:
    record = json.loads(serialize_event(make_event(), make_redactor()))

    assert record["reason_code"] is None
    assert record["account_fingerprint"] is None


def test_serialized_event_masks_canaries_in_every_carrier() -> None:
    redactor = make_redactor(CANARY, OTHER_CANARY)
    event = make_event(
        account_fingerprint=f"acct-{OTHER_CANARY}",
        payload={
            "url": f"https://host/v2?symbol=SPY&apikey={CANARY}",
            "headers": {"authorization": f"Bearer {CANARY}"},
            "trace": [f"line\nAuthorization: Bearer {CANARY}\nline"],
            "nested": {"deep": {"note": OTHER_CANARY}},
        },
    )

    rendered = serialize_event(event, redactor)

    assert CANARY not in rendered
    assert OTHER_CANARY not in rendered
    assert REDACTED in rendered


def test_serialization_fails_closed_when_a_secret_would_survive() -> None:
    # A secret shorter than the redactor's floor cannot be registered, so an
    # unregistered one must still be caught by the caller's own scan.
    redactor = Redactor(known_secrets=(CANARY,))
    rendered = serialize_event(make_event(), redactor)

    with pytest.raises(RedactionFailure, match="survived redaction"):
        redactor.assert_clean(rendered + CANARY)


def test_serialized_payload_keeps_ordinary_values() -> None:
    record = json.loads(serialize_event(make_event(), make_redactor()))

    assert record["payload"] == {"symbol": "SPY", "quantity": 10}
