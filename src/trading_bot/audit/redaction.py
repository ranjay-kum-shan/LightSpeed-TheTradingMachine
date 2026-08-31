"""Redaction boundary for structured audit evidence.

Nothing reaches a log line without passing through here. The boundary fails
closed: a value it cannot classify raises, a nesting depth, string length, or
per-event scan budget it cannot honour raises, and a known secret that survives
redaction raises.

Its pattern half is deliberately aggressive. A credential-named field masks its
whole value: a balanced ``[...]`` or ``{...}`` structure, a quoted string, a
YAML block scalar, a value on the following line, or a bare run to the next
field separator. A sub-delimited header such as ``Cookie`` therefore cannot leak
its later pairs, and an unrecognized authorization scheme cannot leave a
credential beside a redaction marker.

The costs are accepted deliberately: ``sort key: symbol`` is masked, a name
containing non-ASCII characters is treated as a credential rather than
normalized, and a credential-named field with an empty value swallows the next
line. Registering canaries with the redactor is the only complete guarantee;
the name list cannot be exhaustive.
"""

import re
from collections.abc import Mapping, Sequence
from typing import Final
from urllib.parse import unquote

REDACTED: Final = "[REDACTED]"

type PayloadValue = (
    str | int | float | bool | Mapping[str, "PayloadValue"] | Sequence["PayloadValue"] | None
)

_MINIMUM_SECRET_LENGTH: Final = 4
_MAXIMUM_TEXT_LENGTH: Final = 64 * 1024
_MAXIMUM_EVENT_LENGTH: Final = 128 * 1024
_MAXIMUM_DEPTH: Final = 32
_MAXIMUM_PROSE_WORD: Final = 12

_VALUE_TERMINATORS: Final = "&,}]\r\n"
_CLOSERS: Final = {"[": "]", "{": "}"}
_PEM_START: Final = "-----BEGIN"
_PEM_END: Final = "-----END"

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
    {"auth", "bearer", "dsn", "jwt", "key", "nonce", "otp", "pass", "pem", "pwd", "salt", "sig",
     "totp"}
)
_SECRET_FRAGMENTS: Final = (
    "accesskey",
    "apikey",
    "appkey",
    "authkey",
    "authorization",
    "backupkey",
    "clientkey",
    "connectionstring",
    "consumerkey",
    "cookie",
    "credential",
    "deploykey",
    "encryptionkey",
    "hmackey",
    "keystore",
    "kmskey",
    "masterkey",
    "mfacode",
    "passphrase",
    "passwd",
    "password",
    "privatekey",
    "recoverycode",
    "secret",
    "sessionkey",
    "sharedkey",
    "signingkey",
    "signature",
    "sshkey",
    "subscriptionkey",
    "token",
    "truststore",
    "vaultkey",
    "webhookkey",
)

# The name group accepts Unicode word characters so a homoglyph is captured and
# then rejected by is_secret_name rather than silently splitting the name. The
# value is located in Python only when the name is a credential, which keeps the
# scan linear on delimiter-dense input.
_CREDENTIAL_FIELD = re.compile(
    r"(?P<name>[\w.\-%]{1,64})"
    r"(?P<sep>(?:\\?[\"']|\])?[ ]{0,16}(?:[=:]|%3[Dd])[ ]{0,16}|\t+)"
)
# A bare scheme word with no field name.
_AUTH_SCHEME = re.compile(
    r"\b(?P<scheme>bearer|basic|digest|token|negotiate|ntlm|oauth|hawk|sas)"
    r"(?P<gap>\s+)(?P<credential>[A-Za-z0-9._~+/=\-]{4,})",
    re.IGNORECASE,
)
_URL_USERINFO = re.compile(r"(?P<prefix>://)(?P<userinfo>[^/\s@]{1,1024})(?P<at>@)")


class RedactionFailure(Exception):
    """Raised when a value cannot be safely recorded."""


class ScanBudget:
    """Bounds the total text one event may put through the scanner."""

    def __init__(self, limit: int = _MAXIMUM_EVENT_LENGTH) -> None:
        self._remaining = limit
        self._limit = limit

    def spend(self, amount: int) -> None:
        self._remaining -= amount
        if self._remaining < 0:
            raise RedactionFailure(f"one event may not scan more than {self._limit} characters")


def is_secret_name(name: str) -> bool:
    """Report whether a field, key, or parameter name may carry a credential."""
    # Percent encoding is checked too, so "api%5Fkey" cannot hide "api_key".
    return any(_is_secret_form(form) for form in {name, unquote(name)})


def _is_secret_form(name: str) -> bool:
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

    def redact_text(self, text: str, budget: ScanBudget | None = None) -> str:
        if len(text) > _MAXIMUM_TEXT_LENGTH:
            raise RedactionFailure(
                f"text longer than {_MAXIMUM_TEXT_LENGTH} characters must be summarized "
                "before it can be recorded"
            )
        if budget is not None:
            budget.spend(len(text))
        for secret in self._known_secrets:
            text = text.replace(secret, REDACTED)
        # Fields first: a credential-named field masks the scheme word and any
        # embedded URL too, so neither later rule can leave a marker inside a
        # value the field rule would otherwise have masked whole.
        text = _redact_credential_fields(text)
        text = _URL_USERINFO.sub(rf"\g<prefix>{REDACTED}\g<at>", text)
        return _AUTH_SCHEME.sub(_redact_auth_scheme, text)

    def redact(self, value: object, budget: ScanBudget | None = None) -> PayloadValue:
        """Return an allowlisted, redacted copy or raise for anything else."""
        return self._redact(value, 0, budget if budget is not None else ScanBudget())

    def assert_clean(self, rendered: str) -> None:
        """Fail closed if any known secret survived redaction."""
        for secret in self._known_secrets:
            if secret in rendered:
                raise RedactionFailure("a known secret survived redaction")

    def _redact(self, value: object, depth: int, budget: ScanBudget) -> PayloadValue:
        if depth > _MAXIMUM_DEPTH:
            raise RedactionFailure(f"audit values may not nest deeper than {_MAXIMUM_DEPTH}")
        if value is None or isinstance(value, bool | int):
            return value
        if isinstance(value, float):
            return self._require_finite(value)
        if isinstance(value, str):
            return self.redact_text(value, budget)
        if isinstance(value, bytes | bytearray | memoryview):
            raise RedactionFailure("binary values are never recorded in audit evidence")
        if isinstance(value, Mapping):
            return self._redact_mapping(value, depth, budget)
        if isinstance(value, Sequence):
            return [self._redact(item, depth + 1, budget) for item in value]
        raise RedactionFailure(
            f"{type(value).__name__} is not an allowlisted audit value; "
            "map it to strings, numbers, booleans, null, mappings, or sequences first"
        )

    def _redact_mapping(
        self, value: Mapping[object, object], depth: int, budget: ScanBudget
    ) -> dict[str, PayloadValue]:
        redacted: dict[str, PayloadValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise RedactionFailure("audit mapping keys must be strings")
            safe_key = self.redact_text(key, budget)
            if safe_key in redacted:
                # Silently dropping a record from append-only evidence is worse
                # than refusing to write the event at all.
                raise RedactionFailure(f"redacted key {safe_key!r} collides with another key")
            redacted[safe_key] = (
                REDACTED if is_secret_name(key) else self._redact(item, depth + 1, budget)
            )
        return redacted

    @staticmethod
    def _require_finite(value: float) -> float:
        if value != value or value in (float("inf"), float("-inf")):
            raise RedactionFailure("non-finite numbers are not valid JSON Lines evidence")
        return value


def _quoted_end(text: str, start: int) -> int:
    quote = text[start]
    index = start + 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == quote:
            return index + 1
        index += 1
    return len(text)


def _structured_end(text: str, start: int) -> int:
    stack: list[str] = []
    index = start
    while index < len(text):
        char = text[index]
        if char in "\"'":
            index = _quoted_end(text, index)
            continue
        if char in _CLOSERS:
            stack.append(_CLOSERS[char])
        elif stack and char == stack[-1]:
            stack.pop()
            if not stack:
                return index + 1
        index += 1
    return len(text)


def _block_end(text: str, start: int) -> int:
    """Consume the rest of a wrapped value: its indented or blank continuation."""
    index = text.find("\n", start)
    if index == -1:
        return len(text)
    while index < len(text):
        line_end = text.find("\n", index + 1)
        if line_end == -1:
            line_end = len(text)
        line = text[index + 1 : line_end]
        if line.strip() and not line[:1].isspace():
            return index
        index = line_end
    return len(text)


def _pem_end(text: str, start: int) -> int:
    marker = text.find(_PEM_END, start)
    if marker == -1:
        return len(text)
    line_end = text.find("\n", marker)
    return len(text) if line_end == -1 else line_end


def _value_end(text: str, start: int) -> int:
    index = start
    while index < len(text) and text[index] in " \t\r\n":
        index += 1
    if index >= len(text):
        return start
    char = text[index]
    if char in "\"'":
        return _quoted_end(text, index)
    if char in _CLOSERS:
        return _structured_end(text, index)
    if char in "|>":
        return _block_end(text, index)
    if text.startswith(_PEM_START, index):
        return _pem_end(text, index)
    while index < len(text) and text[index] not in _VALUE_TERMINATORS:
        index += 1
    # A value wrapped onto folded or indented continuation lines is one value.
    if index < len(text) and text[index] in "\r\n":
        return _block_end(text, index)
    return index


def _redact_credential_fields(text: str) -> str:
    parts: list[str] = []
    index = 0
    for match in _CREDENTIAL_FIELD.finditer(text):
        if match.start() < index or not is_secret_name(match.group("name")):
            continue
        end = _value_end(text, match.end())
        if end == match.end():
            # An empty value would produce a marker that promises a redaction
            # nothing performed, so leave the text alone instead.
            continue
        parts.append(text[index : match.end()])
        parts.append(REDACTED)
        index = end
    parts.append(text[index:])
    return "".join(parts)


def _redact_auth_scheme(match: re.Match[str]) -> str:
    credential = match.group("credential")
    # An ordinary short word after a scheme name is prose, not a credential.
    if credential.isalpha() and len(credential) <= _MAXIMUM_PROSE_WORD:
        return match.group(0)
    return f"{match.group('scheme')}{match.group('gap')}{REDACTED}"
