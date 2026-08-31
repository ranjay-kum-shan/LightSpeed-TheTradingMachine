"""Redaction boundary for structured audit evidence.

Nothing reaches a log line without passing through here. The boundary fails
closed: a value it cannot classify raises, a nesting depth or input length it
cannot scan safely raises, and a known secret that survives redaction raises.

Its pattern half is deliberately aggressive. A credential-named field masks its
whole value up to the next delimiter, so a scheme word cannot be masked while
the credential beside it survives, and a quoted value cannot slip past. Masking
a legitimate value such as ``sort key: symbol`` is an accepted cost.
"""

import re
from collections.abc import Mapping, Sequence
from typing import Final

REDACTED: Final = "[REDACTED]"

type PayloadValue = (
    str | int | float | bool | Mapping[str, "PayloadValue"] | Sequence["PayloadValue"] | None
)

_MINIMUM_SECRET_LENGTH: Final = 4
_MAXIMUM_TEXT_LENGTH: Final = 64 * 1024
_MAXIMUM_DEPTH: Final = 32

_SEPARATORS = re.compile(r"[^0-9a-z]+")
_PRINTABLE_ASCII = re.compile(r"^[\x20-\x7e]*$")
# Pagination cursors are not credentials even though they end in "token".
_ALLOWED_NAMES: Final = frozenset(
    {
        "continuationtoken",
        "nextpagetoken",
        "nexttoken",
        "pagetoken",
    }
)
_SECRET_NAMES: Final = frozenset(
    {"auth", "bearer", "jwt", "key", "nonce", "pass", "pwd", "sig"}
)
_SECRET_FRAGMENTS: Final = (
    "accesskey",
    "apikey",
    "appkey",
    "authkey",
    "authorization",
    "consumerkey",
    "cookie",
    "credential",
    "passphrase",
    "passwd",
    "password",
    "privatekey",
    "secret",
    "sessionkey",
    "sharedkey",
    "signature",
    "subscriptionkey",
    "token",
)

# A credential-named field masks everything to the next delimiter, so quoted
# values, JSON bodies, and unrecognized authorization schemes cannot survive.
# The value is a lookahead so an ordinary field such as "https:" cannot consume
# a credential field that follows it.
_CREDENTIAL_FIELD = re.compile(
    r"(?P<name>[A-Za-z0-9_.\-]{1,64})"
    r"(?P<sep>[\"']?[ ]{0,4}(?:[=:]|%3[Dd])[ ]{0,4}|\t+)"
    r"(?=(?P<value>[^&;,}\]\r\n]*))"
)
# A bare scheme word with no field name; the length floor avoids prose matches.
_AUTH_SCHEME = re.compile(
    r"\b(?P<scheme>bearer|basic|digest|token|negotiate|ntlm|oauth|hawk|sas|signature)"
    r"(?P<gap>[ ]+)(?P<credential>[A-Za-z0-9._~+/=\-]{8,})",
    re.IGNORECASE,
)
_URL_USERINFO = re.compile(r"(?P<prefix>://[^/\s:@]{1,256}:)(?P<secret>[^/\s@]{1,1024})(?P<at>@)")


class RedactionFailure(Exception):
    """Raised when a value cannot be safely recorded."""


def is_secret_name(name: str) -> bool:
    """Report whether a field, key, or parameter name may carry a credential."""
    # A non-printable or non-ASCII name is hostile until proven otherwise:
    # normalization would erase a homoglyph and hide "apikey" behind "pikey".
    if not _PRINTABLE_ASCII.fullmatch(name):
        return True
    normalized = _SEPARATORS.sub("", name.lower())
    if normalized in _ALLOWED_NAMES:
        return False
    if normalized in _SECRET_NAMES:
        return True
    return any(fragment in normalized for fragment in _SECRET_FRAGMENTS)


class Redactor:
    """Removes credentials from audit values and refuses unclassifiable ones."""

    def __init__(self, known_secrets: Sequence[str] = ()) -> None:
        for secret in known_secrets:
            if len(secret.strip()) < _MINIMUM_SECRET_LENGTH:
                raise ValueError(
                    f"known secret must be at least {_MINIMUM_SECRET_LENGTH} characters"
                )
        # Longest first so a secret containing another is masked whole.
        unique = {secret.strip() for secret in known_secrets}
        self._known_secrets = tuple(sorted(unique, key=len, reverse=True))

    @property
    def known_secrets(self) -> tuple[str, ...]:
        return self._known_secrets

    def redact_text(self, text: str) -> str:
        if len(text) > _MAXIMUM_TEXT_LENGTH:
            raise RedactionFailure(
                f"text longer than {_MAXIMUM_TEXT_LENGTH} characters must be summarized "
                "before it can be recorded"
            )
        for secret in self._known_secrets:
            text = text.replace(secret, REDACTED)
        text = _URL_USERINFO.sub(rf"\g<prefix>{REDACTED}\g<at>", text)
        text = _AUTH_SCHEME.sub(rf"\g<scheme>\g<gap>{REDACTED}", text)
        return _redact_credential_fields(text)

    def redact(self, value: object) -> PayloadValue:
        """Return an allowlisted, redacted copy or raise for anything else."""
        return self._redact(value, 0)

    def assert_clean(self, rendered: str) -> None:
        """Fail closed if any known secret survived redaction."""
        for secret in self._known_secrets:
            if secret in rendered:
                raise RedactionFailure("a known secret survived redaction")

    def _redact(self, value: object, depth: int) -> PayloadValue:
        if depth > _MAXIMUM_DEPTH:
            raise RedactionFailure(f"audit values may not nest deeper than {_MAXIMUM_DEPTH}")
        if value is None or isinstance(value, bool | int):
            return value
        if isinstance(value, float):
            return self._require_finite(value)
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, bytes | bytearray | memoryview):
            raise RedactionFailure("binary values are never recorded in audit evidence")
        if isinstance(value, Mapping):
            return self._redact_mapping(value, depth)
        if isinstance(value, Sequence):
            return [self._redact(item, depth + 1) for item in value]
        raise RedactionFailure(
            f"{type(value).__name__} is not an allowlisted audit value; "
            "map it to strings, numbers, booleans, null, mappings, or sequences first"
        )

    def _redact_mapping(
        self, value: Mapping[object, object], depth: int
    ) -> dict[str, PayloadValue]:
        redacted: dict[str, PayloadValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise RedactionFailure("audit mapping keys must be strings")
            safe_key = self.redact_text(key)
            if safe_key in redacted:
                # Silently dropping a record from append-only evidence is worse
                # than refusing to write the event at all.
                raise RedactionFailure(f"redacted key {safe_key!r} collides with another key")
            redacted[safe_key] = (
                REDACTED if is_secret_name(key) else self._redact(item, depth + 1)
            )
        return redacted

    @staticmethod
    def _require_finite(value: float) -> float:
        if value != value or value in (float("inf"), float("-inf")):
            raise RedactionFailure("non-finite numbers are not valid JSON Lines evidence")
        return value


def _redact_credential_fields(text: str) -> str:
    parts: list[str] = []
    index = 0
    for match in _CREDENTIAL_FIELD.finditer(text):
        if match.start() < index or not is_secret_name(match.group("name")):
            continue
        parts.append(text[index : match.end("sep")])
        parts.append(REDACTED)
        index = match.end("value")
    parts.append(text[index:])
    return "".join(parts)
