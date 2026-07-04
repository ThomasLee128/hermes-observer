from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .observer import Observer
from .wake import classify_observer_intent


PROTOCOL_VERSION = "2025-06-18"


TOOLS: list[dict[str, Any]] = [
    {
        "name": "hermes_observer_report",
        "description": "Run a read-only Hermes Observer status check and return a concise report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "config_path": {
                    "type": "string",
                    "description": "Path to an Observer config JSON file.",
                    "default": "observer.config.example.json",
                },
                "message": {
                    "type": "string",
                    "description": "Optional user message that triggered the status check.",
                    "default": "",
                },
                "learn": {
                    "type": "boolean",
                    "description": "Whether Observer may update wake-phrase learning state.",
                    "default": False,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "hermes_observer_classify",
        "description": "Classify whether a user message is a read-only status/progress Observer request.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "User message to classify.",
                }
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
]


def _send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _result(request_id: Any, result: dict[str, Any]) -> None:
    _send({"jsonrpc": "2.0", "id": request_id, "result": result})


def _error(request_id: Any, code: int, message: str, data: Any | None = None) -> None:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    _send({"jsonrpc": "2.0", "id": request_id, "error": error})


def _tool_success(text: str, structured: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": structured,
        "isError": False,
    }


def _tool_failure(message: str) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def _call_tool(name: str, arguments: dict[str, Any], default_config: Path) -> dict[str, Any]:
    if name == "hermes_observer_report":
        config_path = Path(str(arguments.get("config_path") or default_config))
        message = str(arguments.get("message") or "")
        learn = bool(arguments.get("learn", False))
        try:
            observer = Observer(config_path)
            report, payload = observer.report(message, learn=learn)
        except Exception as exc:
            return _tool_failure(f"Hermes Observer failed: {type(exc).__name__}: {exc}")
        return _tool_success(report, {"report": report, "payload": payload})

    if name == "hermes_observer_classify":
        text = str(arguments.get("text") or "")
        result = classify_observer_intent(text)
        return _tool_success(json.dumps(result, ensure_ascii=False, indent=2), result)

    return _tool_failure(f"Unknown tool: {name}")


def _handle(message: dict[str, Any], default_config: Path) -> None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        client_version = params.get("protocolVersion") if isinstance(params, dict) else None
        _result(
            request_id,
            {
                "protocolVersion": client_version or PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hermes-observer", "version": __version__},
            },
        )
        return

    if method == "notifications/initialized":
        return

    if method == "ping":
        _result(request_id, {})
        return

    if method == "tools/list":
        _result(request_id, {"tools": TOOLS})
        return

    if method == "tools/call":
        if not isinstance(params, dict):
            _error(request_id, -32602, "Invalid tools/call params")
            return
        name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            _error(request_id, -32602, "Tool arguments must be an object")
            return
        _result(request_id, _call_tool(name, arguments, default_config))
        return

    if request_id is not None:
        _error(request_id, -32601, f"Method not found: {method}")


def serve(default_config: Path) -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            _error(None, -32700, f"Parse error: {exc}")
            continue
        if not isinstance(message, dict):
            _error(None, -32600, "Invalid request")
            continue
        _handle(message, default_config)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Experimental stdio MCP server for Hermes Observer.")
    parser.add_argument("--config", default="observer.config.example.json", help="Default Observer config path.")
    args = parser.parse_args()
    return serve(Path(args.config))


if __name__ == "__main__":
    raise SystemExit(main())
