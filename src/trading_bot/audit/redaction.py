"""Redaction boundary for structured audit evidence.

Nothing reaches a log line without passing through here. The boundary fails
closed: a value it cannot classify raises rather than being stringified, and a
known secret that survives redaction raises rather than being written.
"""

import re
from collections.abc import Mapping, Sequence
from typing import Final

REDACTED: Final = "[REDACTED]"

type PayloadValue = (
    str | int | float | bool | Mapping[str, "PayloadValue"] | Sequence["PayloadValue"] | None
)

_MINIMUM_SECRET_LENGTH: Final = 4
_SEPARATORS = re.compile(r"[^0-9a-z]+")
# Pagination cursors are not credentials even though they end in "token".
_ALLOWED_NAMES: Final = frozenset(
    {
        "continuationtoken",
        "nextpagetoken",
        "nexttoken",
        "pagetoken",
    }
)
_SECRET_NAMES: Final = frozenset({"auth", "bearer", "jwt", "key", "pwd", "sig"})
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

# Covers query strings, header lines, and "key: value" text in multiline blobs.
_PAIR = re.compile(r"([A-Za-z0-9_.\-]{1,64})(\s*[=:]\s*)([^\s&;,'\"]+)")
_AUTH_SCHEME = re.compile(r"\b(bearer|basic|digest|token)(\s+)([A-Za-z0-9._~+/=\-]{4,})", re.I)
_URL_USERINFO = re.compile(r"([A-Za-z][A-Za-z0-9+.\-]*://[^/\s:@]+:)([^/\s@]+)(@)")


class RedactionFailure(Exception):
    """Raised when a value cannot be safely recorded."""


def is_secret_name(name: str) -> bool:
    """Report whether a field, key, or parameter name may carry a credential."""
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
        for secret in self._known_secrets:
            text = text.replace(secret, REDACTED)
        text = _URL_USERINFO.sub(rf"\1{REDACTED}\3", text)
        text = _AUTH_SCHEME.sub(rf"\1\2{REDACTED}", text)
        return _PAIR.sub(self._redact_pair, text)

    def redact(self, value: object) -> PayloadValue:
        """Return an allowlisted, redacted copy or raise for anything else."""
        if value is None or isinstance(value, bool | int | float):
            return value
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, bytes | bytearray | memoryview):
            raise RedactionFailure("binary values are never recorded in audit evidence")
        if isinstance(value, Mapping):
            return {
                self._redact_key(key): REDACTED if is_secret_name(key) else self.redact(item)
                for key, item in self._string_keyed(value)
            }
        if isinstance(value, Sequence):
            return [self.redact(item) for item in value]
        raise RedactionFailure(
            f"{type(value).__name__} is not an allowlisted audit value; "
            "map it to strings, numbers, booleans, null, mappings, or sequences first"
        )

    def assert_clean(self, rendered: str) -> None:
        """Fail closed if any known secret survived redaction."""
        for secret in self._known_secrets:
            if secret in rendered:
                raise RedactionFailure("a known secret survived redaction")

    def _redact_key(self, key: str) -> str:
        return self.redact_text(key)

    def _redact_pair(self, match: re.Match[str]) -> str:
        name, separator = match.group(1), match.group(2)
        if not is_secret_name(name):
            return match.group(0)
        return f"{name}{separator}{REDACTED}"

    @staticmethod
    def _string_keyed(value: Mapping[object, object]) -> list[tuple[str, object]]:
        pairs: list[tuple[str, object]] = []
        for key, item in value.items():
            if not isinstance(key, str):
                raise RedactionFailure("audit mapping keys must be strings")
            pairs.append((key, item))
        return pairs
