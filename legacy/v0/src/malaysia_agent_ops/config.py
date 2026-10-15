from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_dir: Path
    db_path: Path
    merchant_name: str
    merchant_city: str
    merchant_country_code: str
    merchant_duitnow_id: str
    default_currency: str
    myinvois_source_system: str
    business_registry_source_system: str
    paynet_source_system: str
    trade_source_system: str
    halal_source_system: str
    myinvois_default_env: str
    myinvois_sandbox_api_base: str
    myinvois_sandbox_identity_base: str
    myinvois_production_api_base: str
    myinvois_production_identity_base: str
    myinvois_sandbox_client_id: str | None
    myinvois_sandbox_client_secret: str | None
    myinvois_production_client_id: str | None
    myinvois_production_client_secret: str | None
    myinvois_access_token: str | None
    cidb_api_base: str
    cidb_access_token: str | None
    workflow_runner_max_steps: int
    approval_payment_threshold: float
    payment_webhook_secret: str | None


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_env_file(project_root: Path) -> None:
    env_path = project_root / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def get_settings(project_root: Path | None = None, db_path: Path | None = None) -> Settings:
    resolved_root = Path(project_root or os.getenv("MYOPS_PROJECT_ROOT") or default_project_root()).resolve()
    load_env_file(resolved_root)
    data_dir = resolved_root / "data"
    resolved_db = Path(db_path or os.getenv("MYOPS_DB_PATH") or (data_dir / "myops.db")).resolve()

    return Settings(
        project_root=resolved_root,
        data_dir=data_dir,
        db_path=resolved_db,
        merchant_name=os.getenv("MYOPS_MERCHANT_NAME", "MYOPS Sandbox Merchant"),
        merchant_city=os.getenv("MYOPS_MERCHANT_CITY", "Kuala Lumpur"),
        merchant_country_code=os.getenv("MYOPS_MERCHANT_COUNTRY_CODE", "MY"),
        merchant_duitnow_id=os.getenv("MYOPS_MERCHANT_DUITNOW_ID", "sandbox@myops.local"),
        default_currency=os.getenv("MYOPS_DEFAULT_CURRENCY", "MYR"),
        myinvois_source_system="myinvois_sandbox",
        business_registry_source_system="business_registry_sandbox",
        paynet_source_system="paynet_duitnow_sandbox",
        trade_source_system="trade_docpack_sandbox",
        halal_source_system="halal_directory_sandbox",
        myinvois_default_env=os.getenv("MYOPS_MYINVOIS_ENV", "sandbox"),
        myinvois_sandbox_api_base=os.getenv(
            "MYOPS_MYINVOIS_SANDBOX_API_BASE",
            "https://preprod-api.myinvois.hasil.gov.my",
        ),
        myinvois_sandbox_identity_base=os.getenv(
            "MYOPS_MYINVOIS_SANDBOX_IDENTITY_BASE",
            "https://preprod-api.myinvois.hasil.gov.my",
        ),
        myinvois_production_api_base=os.getenv(
            "MYOPS_MYINVOIS_PRODUCTION_API_BASE",
            "https://api.myinvois.hasil.gov.my",
        ),
        myinvois_production_identity_base=os.getenv(
            "MYOPS_MYINVOIS_PRODUCTION_IDENTITY_BASE",
            "https://api.myinvois.hasil.gov.my",
        ),
        myinvois_sandbox_client_id=os.getenv("MYOPS_MYINVOIS_SANDBOX_CLIENT_ID") or None,
        myinvois_sandbox_client_secret=os.getenv("MYOPS_MYINVOIS_SANDBOX_CLIENT_SECRET") or None,
        myinvois_production_client_id=os.getenv("MYOPS_MYINVOIS_PROD_CLIENT_ID") or None,
        myinvois_production_client_secret=os.getenv("MYOPS_MYINVOIS_PROD_CLIENT_SECRET") or None,
        myinvois_access_token=os.getenv("MYOPS_MYINVOIS_ACCESS_TOKEN") or None,
        cidb_api_base=os.getenv("MYOPS_CIDB_API_BASE", "https://n3c-api.cidb.gov.my"),
        cidb_access_token=os.getenv("MYOPS_CIDB_ACCESS_TOKEN") or None,
        workflow_runner_max_steps=int(os.getenv("MYOPS_WORKFLOW_RUNNER_MAX_STEPS", "12")),
        approval_payment_threshold=float(os.getenv("MYOPS_APPROVAL_PAYMENT_THRESHOLD", "1000")),
        payment_webhook_secret=os.getenv("MYOPS_PAYMENT_WEBHOOK_SECRET") or None,
    )


def myinvois_environment_name(raw: str | None) -> str:
    value = (raw or "sandbox").strip().lower()
    if value in {"sandbox", "preprod", "pre-production"}:
        return "sandbox"
    if value in {"prod", "production"}:
        return "production"
    raise ValueError(f"Unsupported MyInvois environment: {raw}")
