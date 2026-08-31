"""Typed, fail-closed runtime configuration."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from trading_bot.domain import ReasonCode


class OperatingMode(StrEnum):
    """Modes available before any separately approved real-money stage."""

    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    RECOVERY = "RECOVERY"
    HALTED = "HALTED"


class RuntimeConfig(BaseModel):
    """Immutable runtime configuration with an explicit operating mode."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1"]
    mode: OperatingMode


@dataclass(frozen=True, slots=True)
class ConfigLoadResult:
    """A validated config or a safe halted fallback with stable reason codes."""

    config: RuntimeConfig
    reason_codes: tuple[ReasonCode, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.reason_codes


SAFE_HALTED_CONFIG: Final = RuntimeConfig(schema_version="1", mode=OperatingMode.HALTED)


class _UniqueKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found duplicate key",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_runtime_config(raw: Mapping[str, object] | None) -> ConfigLoadResult:
    """Validate raw configuration and return HALTED for every invalid input."""

    if raw is None:
        return ConfigLoadResult(SAFE_HALTED_CONFIG, (ReasonCode.CONFIG_MISSING,))

    if str(raw.get("mode", "")).upper() == "LIVE":
        return ConfigLoadResult(SAFE_HALTED_CONFIG, (ReasonCode.LIVE_DENIED,))

    try:
        config = RuntimeConfig.model_validate(raw)
    except ValidationError:
        return ConfigLoadResult(SAFE_HALTED_CONFIG, (ReasonCode.CONFIG_INVALID,))

    return ConfigLoadResult(config)


def load_yaml_config(path: Path) -> ConfigLoadResult:
    """Load YAML without duplicate keys and fail closed without leaking values."""

    try:
        with path.open(encoding="utf-8") as config_file:
            raw = yaml.load(config_file, Loader=_UniqueKeySafeLoader)
    except (OSError, yaml.YAMLError):
        return ConfigLoadResult(SAFE_HALTED_CONFIG, (ReasonCode.CONFIG_INVALID,))

    if not isinstance(raw, Mapping):
        return ConfigLoadResult(SAFE_HALTED_CONFIG, (ReasonCode.CONFIG_INVALID,))

    return load_runtime_config(raw)
