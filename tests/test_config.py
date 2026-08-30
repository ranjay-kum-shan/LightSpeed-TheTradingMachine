from pathlib import Path

import pytest

from trading_bot.config import OperatingMode, load_runtime_config, load_yaml_config


@pytest.mark.parametrize("mode", [OperatingMode.BACKTEST, OperatingMode.PAPER])
def test_explicit_supported_mode_is_valid(mode: OperatingMode) -> None:
    result = load_runtime_config({"schema_version": "1", "mode": mode})

    assert result.is_valid
    assert result.config.mode is mode
    assert result.reason_codes == ()


@pytest.mark.parametrize(
    ("raw", "reason_code"),
    [
        (None, "MODE_CONFIG_MISSING"),
        ({"schema_version": "1"}, "MODE_CONFIG_INVALID"),
        ({"schema_version": "2", "mode": "BACKTEST"}, "MODE_CONFIG_INVALID"),
        ({"schema_version": "1", "mode": "UNKNOWN"}, "MODE_CONFIG_INVALID"),
        ({"schema_version": "1", "mode": "LIVE"}, "MODE_LIVE_DENIED"),
        (
            {"schema_version": "1", "mode": "PAPER", "live_enabled": True},
            "MODE_CONFIG_INVALID",
        ),
    ],
)
def test_missing_invalid_or_live_config_falls_back_to_halted(
    raw: dict[str, object] | None,
    reason_code: str,
) -> None:
    result = load_runtime_config(raw)

    assert not result.is_valid
    assert result.config.mode is OperatingMode.HALTED
    assert result.reason_codes == (reason_code,)


@pytest.mark.parametrize(
    "content",
    [
        "schema_version: '1'\nmode: BACKTEST\nmode: PAPER\n",
        "schema_version: [\n",
        "- schema_version\n- mode\n",
    ],
)
def test_invalid_yaml_falls_back_to_halted(tmp_path: Path, content: str) -> None:
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(content, encoding="utf-8")

    result = load_yaml_config(config_path)

    assert not result.is_valid
    assert result.config.mode is OperatingMode.HALTED
    assert result.reason_codes == ("MODE_CONFIG_INVALID",)


def test_missing_yaml_file_falls_back_to_halted(tmp_path: Path) -> None:
    result = load_yaml_config(tmp_path / "missing.yaml")

    assert not result.is_valid
    assert result.config.mode is OperatingMode.HALTED
    assert result.reason_codes == ("MODE_CONFIG_INVALID",)