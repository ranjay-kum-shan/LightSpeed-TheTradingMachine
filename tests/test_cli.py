import json
from pathlib import Path

from trading_bot.cli import main


def test_config_check_reports_valid_backtest_without_echoing_config(
    tmp_path: Path,
    capsys: object,
) -> None:
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text('schema_version: "1"\nmode: BACKTEST\n', encoding="utf-8")

    exit_code = main(["config-check", str(config_path)])
    captured = capsys.readouterr()  # type: ignore[attr-defined]

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "mode": "BACKTEST",
        "reason_codes": [],
        "valid": True,
    }
    assert captured.err == ""


def test_config_check_denies_live_and_reports_only_reason_code(
    tmp_path: Path,
    capsys: object,
) -> None:
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        'schema_version: "1"\nmode: LIVE\napi_secret: do-not-echo\n',
        encoding="utf-8",
    )

    exit_code = main(["config-check", str(config_path)])
    captured = capsys.readouterr()  # type: ignore[attr-defined]

    assert exit_code == 2
    assert json.loads(captured.out) == {
        "mode": "HALTED",
        "reason_codes": ["MODE_LIVE_DENIED"],
        "valid": False,
    }
    assert "do-not-echo" not in captured.out
    assert captured.err == ""
