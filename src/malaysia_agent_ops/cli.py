"""Admin CLI: database, vault, tenants, users, keys, mandates, credentials, and running the servers.

Secrets are read from stdin or files, never from command-line arguments (which end up in shell history).
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import get_settings
from .runtime import Runtime
from .security.vault import Vault
from .services import admin, audit


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _when(value: str | None, default: datetime) -> datetime:
    if not value:
        return default
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _read_secret(prompt: str) -> str:
    if sys.stdin.isatty():
        import getpass

        return getpass.getpass(prompt)
    return sys.stdin.readline().strip()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="myops", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    db = sub.add_parser("db", help="Database migrations").add_subparsers(dest="db_cmd", required=True)
    db.add_parser("upgrade", help="Apply migrations (alembic upgrade head)")

    vault = sub.add_parser("vault", help="Credential vault").add_subparsers(dest="vault_cmd", required=True)
    vault.add_parser("generate-key", help="Print a new key for MYOPS_VAULT_KEYS")

    tenant = sub.add_parser("tenant").add_subparsers(dest="tenant_cmd", required=True)
    t = tenant.add_parser("create")
    t.add_argument("--name", required=True)
    t = tenant.add_parser("set-approval-policy", help="e.g. --policy '{\"auto_approve_submit_max\": 500}'")
    t.add_argument("--tenant", required=True)
    t.add_argument("--policy", required=True)

    user = sub.add_parser("user").add_subparsers(dest="user_cmd", required=True)
    u = user.add_parser("create")
    u.add_argument("--tenant", required=True)
    u.add_argument("--email", required=True)
    u.add_argument("--role", choices=["admin", "approver", "member"], required=True)
    u.add_argument("--name")
    u.add_argument("--phone", help="WhatsApp-capable number for approval links")

    key = sub.add_parser("apikey").add_subparsers(dest="key_cmd", required=True)
    k = key.add_parser("create")
    k.add_argument("--tenant", required=True)
    k.add_argument("--role", choices=["agent", "approver", "admin"], required=True)
    k.add_argument("--name", required=True)
    k.add_argument("--user", help="User id (required for approver and admin keys)")
    k = key.add_parser("revoke")
    k.add_argument("--id", required=True)

    tp = sub.add_parser("taxpayer").add_subparsers(dest="tp_cmd", required=True)
    a = tp.add_parser("add")
    a.add_argument("--tenant", required=True)
    a.add_argument("--tin", required=True)
    a.add_argument("--id-type", choices=["BRN", "NRIC", "PASSPORT", "ARMY"], required=True)
    a.add_argument("--id-value", required=True)
    a.add_argument("--name", required=True)

    ap = sub.add_parser("appointment").add_subparsers(dest="ap_cmd", required=True)
    a = ap.add_parser("add", help="Record a mandate (mirror the MyInvois portal appointment)")
    a.add_argument("--tenant", required=True)
    a.add_argument("--tin", required=True)
    a.add_argument("--mode", choices=["intermediary", "self"], required=True)
    a.add_argument(
        "--permissions",
        required=True,
        help="Comma-separated: view_documents,submit_documents,cancel_documents,reject_documents",
    )
    a.add_argument("--valid-from", help="ISO date/time (default now)")
    a.add_argument("--valid-to", required=True, help="ISO date/time")
    a.add_argument("--evidence", help="Where the appointment was made and by whom")

    cred = sub.add_parser("credential").add_subparsers(dest="cred_cmd", required=True)
    c = cred.add_parser("set-myinvois", help="Client secret is read from stdin")
    c.add_argument("--tenant", required=True)
    c.add_argument("--environment", choices=["preprod", "production"], required=True)
    c.add_argument("--client-id", required=True)
    c.add_argument("--tin", help="Only for a taxpayer's own (self mode) credentials")
    c = cred.add_parser("set-signing-cert", help="PKCS#12 file; password is read from stdin")
    c.add_argument("--tenant", required=True)
    c.add_argument("--environment", choices=["preprod", "production"], required=True)
    c.add_argument("--pkcs12", required=True, type=Path)
    c.add_argument("--tin", help="Sign for this taxpayer only (default: whole tenant)")

    au = sub.add_parser("audit").add_subparsers(dest="audit_cmd", required=True)
    v = au.add_parser("verify")
    v.add_argument("--tenant", required=True)

    s = sub.add_parser("serve", help="Run the REST API and remote MCP server")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8080)

    m = sub.add_parser("mcp-stdio", help="Run MCP over stdio for a local client; API key from MYOPS_API_KEY or stdin")
    m.add_argument("--api-key-env", default="MYOPS_API_KEY")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "vault":
        print(Vault.generate_key())
        return 0
    if args.cmd == "db":
        from alembic import command
        from alembic.config import Config

        cfg = Config(str(Path(__file__).parent / "migrations" / "alembic.ini"))
        cfg.set_main_option("script_location", str(Path(__file__).parent / "migrations"))
        cfg.set_main_option("sqlalchemy.url", get_settings().database_url)
        command.upgrade(cfg, "head")
        return 0
    if args.cmd == "serve":
        import uvicorn

        from .api.app import create_app

        uvicorn.run(create_app(), host=args.host, port=args.port)
        return 0
    if args.cmd == "mcp-stdio":
        import os

        from .api.mcp_server import build_mcp
        from .security.auth import authenticate_api_key
        from .services.einvoice import EInvoiceService

        rt = Runtime.from_settings()
        raw = os.environ.get(args.api_key_env) or _read_secret("API key: ")
        with rt.db.session() as session:
            principal = authenticate_api_key(session, raw)
        build_mcp(rt, EInvoiceService(rt), fixed_principal=principal).run("stdio")
        return 0

    rt = Runtime.from_settings()
    now = datetime.now(timezone.utc)
    with rt.db.session() as s:
        if args.cmd == "tenant" and args.tenant_cmd == "create":
            tenant = admin.create_tenant(s, args.name)
            _print({"tenant_id": tenant.id, "name": tenant.name})
        elif args.cmd == "tenant":
            admin.set_approval_policy(s, args.tenant, json.loads(args.policy))
            _print({"ok": True})
        elif args.cmd == "user":
            user = admin.create_user(s, args.tenant, email=args.email, role=args.role, name=args.name, phone=args.phone)
            _print({"user_id": user.id, "email": user.email, "role": user.role})
        elif args.cmd == "apikey" and args.key_cmd == "create":
            record, raw = admin.create_api_key(s, args.tenant, role=args.role, name=args.name, user_id=args.user)
            _print({"key_id": record.id, "role": record.role, "api_key": raw, "note": "Shown once. Store it now."})
        elif args.cmd == "apikey":
            admin.revoke_api_key(s, args.id)
            _print({"revoked": args.id})
        elif args.cmd == "taxpayer":
            tp = admin.add_taxpayer(
                s, args.tenant, tin=args.tin, id_type=args.id_type, id_value=args.id_value, name=args.name
            )
            _print({"taxpayer_id": tp.id, "tin": tp.tin})
        elif args.cmd == "appointment":
            appt = admin.add_appointment(
                s,
                args.tenant,
                taxpayer_tin=args.tin,
                mode=args.mode,
                permissions=[p.strip() for p in args.permissions.split(",") if p.strip()],
                valid_from=_when(args.valid_from, now),
                valid_to=_when(args.valid_to, now),
                evidence=args.evidence,
            )
            _print({"appointment_id": appt.id, "permissions": appt.permissions})
        elif args.cmd == "credential" and args.cred_cmd == "set-myinvois":
            secret = {"client_id": args.client_id, "client_secret": _read_secret("Client secret: ")}
            cred = admin.store_credential(
                s,
                rt.vault,
                args.tenant,
                kind="myinvois_client",
                environment=args.environment,
                secret=secret,
                taxpayer_tin=args.tin,
            )
            _print({"credential_id": cred.id})
        elif args.cmd == "credential":
            secret = {
                "pkcs12_b64": base64.b64encode(args.pkcs12.read_bytes()).decode(),
                "password": _read_secret("Certificate password: ") or None,
            }
            from .myinvois.signing import SigningKey

            SigningKey.from_secret(secret)  # fail now, not at first submission
            cred = admin.store_credential(
                s,
                rt.vault,
                args.tenant,
                kind="signing_certificate",
                environment=args.environment,
                secret=secret,
                taxpayer_tin=args.tin,
            )
            _print({"credential_id": cred.id})
        elif args.cmd == "audit":
            _print(audit.verify_chain(s, args.tenant))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
