from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .config import get_settings
from .halal_precheck import HalalPrecheckError, run_halal_precheck
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

    halal_parser = subparsers.add_parser("halal", help="Run halal-industry operator workflows.")
    halal_subparsers = halal_parser.add_subparsers(dest="halal_command", required=True)
    precheck_parser = halal_subparsers.add_parser("precheck", help="Run halal dossier pre-check workflows.")
    precheck_subparsers = precheck_parser.add_subparsers(dest="precheck_command", required=True)
    precheck_run = precheck_subparsers.add_parser("run", help="Validate a halal dossier and write reports.")
    precheck_run.add_argument("--file", required=True, dest="dossier_file", help="Path to a JSON dossier file.")
    precheck_run.add_argument("--out-dir", required=True, help="Directory for JSON, Markdown, and HTML reports.")
    precheck_run.add_argument("--ocr-dir", help="Optional directory of OCR verification JSON files.")
    precheck_run.add_argument("--requirements", help="Optional requirements JSON file.")
    precheck_run.add_argument("--pretty", action="store_true", help="Pretty-print the CLI summary JSON.")

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

    try:
        if args.command == "serve":
            settings = get_settings(db_path=Path(args.db_path).resolve() if getattr(args, "db_path", None) else None)
            serve(settings, host=args.host, port=args.port)
            return 0
        if args.command == "mcp":
            settings = get_settings(db_path=Path(args.db_path).resolve() if getattr(args, "db_path", None) else None)
            serve_mcp(settings)
            return 0
        if args.command == "halal" and args.halal_command == "precheck" and args.precheck_command == "run":
            result = run_halal_precheck(
                dossier_path=Path(args.dossier_file),
                out_dir=Path(args.out_dir),
                requirements_path=Path(args.requirements) if args.requirements else None,
                ocr_dir=Path(args.ocr_dir) if args.ocr_dir else None,
            )
            emit(
                {
                    "status": "success",
                    "overall_status": result["summary"]["overall_status"],
                    "out_dir": args.out_dir,
                    "files": [
                        "precheck.json",
                        "applicant-report.md",
                        "reviewer-report.md",
                        "applicant-report.html",
                        "reviewer-report.html",
                    ],
                },
                pretty=args.pretty,
            )
            return 0

        settings = get_settings(db_path=Path(args.db_path).resolve() if getattr(args, "db_path", None) else None)
        payload = load_payload(args)
        service = OperationsService(settings)
        response = service.invoke(args.action, payload)
        emit(response, pretty=args.pretty)
        return 0
    except (InputError, NotFoundError, HalalPrecheckError, json.JSONDecodeError) as exc:
        emit({"error": str(exc)}, pretty=True)
        return 1
