"""Command-line entry points that expose no broker capability."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from trading_bot.config import load_yaml_config


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trading-bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser(
        "config-check",
        help="validate a runtime YAML file and report only safe status fields",
    )
    config_parser.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command != "config-check":
        raise AssertionError("argparse returned an unsupported command")

    result = load_yaml_config(args.path)
    output = {
        "mode": result.config.mode.value,
        "reason_codes": list(result.reason_codes),
        "valid": result.is_valid,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0 if result.is_valid else 2
