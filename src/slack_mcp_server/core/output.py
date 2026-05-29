"""CLI output formatting."""

from __future__ import annotations

import json
import sys
from typing import Any


def emit_result(result: dict[str, Any], *, output: str = "json", pretty: bool = False, quiet: bool = False) -> None:
    """Print a command result or exit with error."""
    if result.get("error"):
        if not quiet:
            _write(result, output=output, pretty=pretty, stream=sys.stderr)
        raise SystemExit(1)

    if quiet:
        return

    _write(result, output=output, pretty=pretty, stream=sys.stdout)


def _write(payload: dict[str, Any], *, output: str, pretty: bool, stream: Any) -> None:
    if output == "pretty" or pretty:
        stream.write(json.dumps(payload, indent=2, sort_keys=True))
        stream.write("\n")
        return

    stream.write(json.dumps(payload))
    stream.write("\n")
