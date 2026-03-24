from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .config import get_settings
from .mcp_server import serve_mcp
from .server import serve
from .service import InputError, NotFoundError, OperationsService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="myops",
        description="Malaysia-first operations API/CLI for agentic workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Run the local HTTP API server.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8080)
    serve_parser.add_argument("--db-path")

    mcp_parser = subparsers.add_parser("mcp", help="Run the local MCP stdio server.")
    mcp_parser.add_argument("--db-path")

    action_parser = subparsers.add_parser("action", help="Invoke a contract action directly from the CLI.")
    action_parser.add_argument("action", choices=sorted(OperationsService.ACTIONS.keys()))
    action_parser.add_argument("--json", dest="json_payload")
    action_parser.add_argument("--file", dest="payload_file")
    action_parser.add_argument("--db-path")
    action_parser.add_argument("--pretty", action="store_true")

    return parser


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.json_payload:
        payload = json.loads(args.json_payload)
    elif args.payload_file:
        path = Path(args.payload_file)
        payload = json.loads(path.read_text())
    elif not sys.stdin.isatty():
        payload = json.loads(sys.stdin.read() or "{}")
    else:
        payload = {}

    if not isinstance(payload, dict):
        raise InputError("Payload must be a JSON object.")
    return payload


def emit(payload: dict[str, Any], pretty: bool = False) -> None:
    dump = json.dumps(payload, indent=2 if pretty else None, ensure_ascii=True)
    print(dump)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings(db_path=Path(args.db_path).resolve() if getattr(args, "db_path", None) else None)

    try:
        if args.command == "serve":
            serve(settings, host=args.host, port=args.port)
            return 0
        if args.command == "mcp":
            serve_mcp(settings)
            return 0

        payload = load_payload(args)
        service = OperationsService(settings)
        response = service.invoke(args.action, payload)
        emit(response, pretty=args.pretty)
        return 0
    except (InputError, NotFoundError, json.JSONDecodeError) as exc:
        emit({"error": str(exc)}, pretty=True)
        return 1
