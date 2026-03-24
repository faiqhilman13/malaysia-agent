from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .fixtures import BUSINESS_FIXTURES, HALAL_FIXTURES


JSON_FIELDS = {
    "entities": {"aliases_json", "raw_json"},
    "halal_directory": {"products_json", "raw_json"},
    "invoice_submissions": {"payload_json", "validation_json"},
    "payment_requests": {"metadata_json"},
    "payment_events": {"payload_json"},
    "exceptions": {"details_json"},
    "approvals": {"requested_payload_json", "approval_context_json", "decision_context_json"},
    "workflow_runs": {"initial_payload_json", "final_output_json", "execution_log_json"},
    "trade_submissions": {"validation_json", "payload_json"},
    "halal_packs": {"payload_json"},
    "halal_supplier_registry": {"products_json", "metadata_json"},
    "halal_bom_graphs": {"payload_json"},
    "halal_workflows": {"payload_json"},
    "halal_checklists": {"payload_json"},
    "halal_audit_queries": {"payload_json", "response_json"},
    "halal_document_shares": {"payload_json"},
    "halal_export_dossiers": {"payload_json"},
}


class Repository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
        self._seed_fixtures()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    tin TEXT PRIMARY KEY,
                    registration_no TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    industry TEXT,
                    tax_active INTEGER NOT NULL,
                    business_registry_status TEXT NOT NULL,
                    aliases_json TEXT NOT NULL,
                    raw_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_directory (
                    certificate_ref TEXT PRIMARY KEY,
                    company_tin TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    products_json TEXT NOT NULL,
                    raw_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS invoice_submissions (
                    id TEXT PRIMARY KEY,
                    invoice_number TEXT NOT NULL,
                    supplier_tin TEXT NOT NULL,
                    buyer_tin TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    next_action TEXT,
                    blocking_reason TEXT,
                    poll_count INTEGER NOT NULL DEFAULT 0,
                    external_submission_id TEXT,
                    external_document_id TEXT,
                    payload_json TEXT NOT NULL,
                    validation_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    canceled_at TEXT
                );

                CREATE TABLE IF NOT EXISTS payment_requests (
                    id TEXT PRIMARY KEY,
                    invoice_submission_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    qr_payload TEXT NOT NULL,
                    received_amount REAL,
                    source_system TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS payment_events (
                    id TEXT PRIMARY KEY,
                    request_id TEXT,
                    reference TEXT,
                    provider TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    amount REAL,
                    currency TEXT,
                    external_reference TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS exceptions (
                    id TEXT PRIMARY KEY,
                    exception_type TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    resolution_note TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    target_resource_type TEXT,
                    target_resource_id TEXT,
                    policy_key TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    requested_payload_json TEXT NOT NULL,
                    approval_context_json TEXT,
                    decision_context_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS workflow_runs (
                    id TEXT PRIMARY KEY,
                    root_action TEXT NOT NULL,
                    current_action TEXT,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    next_action TEXT,
                    blocking_reason TEXT,
                    initial_payload_json TEXT NOT NULL,
                    final_output_json TEXT,
                    execution_log_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trade_submissions (
                    id TEXT PRIMARY KEY,
                    doc_type TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    validation_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_supplier_registry (
                    id TEXT PRIMARY KEY,
                    supplier_tin TEXT,
                    supplier_name TEXT NOT NULL,
                    certificate_ref TEXT,
                    certificate_status TEXT NOT NULL,
                    expiry_date TEXT,
                    risk_level TEXT NOT NULL,
                    products_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_bom_graphs (
                    id TEXT PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_workflows (
                    id TEXT PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    scheme TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_checklists (
                    id TEXT PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    score REAL NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_audit_queries (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    query_title TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    response_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_document_shares (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    share_target TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_export_dossiers (
                    id TEXT PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS halal_packs (
                    id TEXT PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    workflow_status TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def _seed_fixtures(self) -> None:
        with self.connect() as conn:
            entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            if entity_count == 0:
                conn.executemany(
                    """
                    INSERT INTO entities (
                        tin, registration_no, name, industry, tax_active,
                        business_registry_status, aliases_json, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            item["tin"],
                            item["registration_no"],
                            item["name"],
                            item["industry"],
                            int(item["tax_active"]),
                            item["business_registry_status"],
                            json.dumps(item["aliases"]),
                            json.dumps(item),
                        )
                        for item in BUSINESS_FIXTURES
                    ],
                )

            halal_count = conn.execute("SELECT COUNT(*) FROM halal_directory").fetchone()[0]
            if halal_count == 0:
                conn.executemany(
                    """
                    INSERT INTO halal_directory (
                        certificate_ref, company_tin, company_name, status,
                        expiry_date, products_json, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            item["certificate_ref"],
                            item["company_tin"],
                            item["company_name"],
                            item["status"],
                            item["expiry_date"],
                            json.dumps(item["products"]),
                            json.dumps(item),
                        )
                        for item in HALAL_FIXTURES
                    ],
                )

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        if isinstance(value, bool):
            return int(value)
        return value

    def _row_to_dict(self, table: str, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        item = dict(row)
        for field in JSON_FIELDS.get(table, set()):
            if item.get(field):
                item[field] = json.loads(item[field])
        return item

    def search_entities(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        cleaned = query.strip().lower()
        like_query = f"%{cleaned}%"
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM entities
                WHERE lower(name) LIKE ?
                   OR tin = ?
                   OR registration_no = ?
                   OR lower(aliases_json) LIKE ?
                ORDER BY name ASC
                LIMIT ?
                """,
                (like_query, query.strip(), query.strip(), like_query, limit),
            ).fetchall()
        return [self._row_to_dict("entities", row) for row in rows]

    def get_entity_by_tin(self, tin: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM entities WHERE tin = ?", (tin.strip(),)).fetchone()
        return self._row_to_dict("entities", row)

    def get_entity_by_registration_no(self, registration_no: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE registration_no = ?",
                (registration_no.strip(),),
            ).fetchone()
        return self._row_to_dict("entities", row)

    def get_halal_status(
        self,
        *,
        certificate_ref: str | None = None,
        company_name: str | None = None,
        company_tin: str | None = None,
    ) -> dict[str, Any] | None:
        with self.connect() as conn:
            if certificate_ref:
                row = conn.execute(
                    "SELECT * FROM halal_directory WHERE certificate_ref = ?",
                    (certificate_ref.strip(),),
                ).fetchone()
            elif company_tin:
                row = conn.execute(
                    """
                    SELECT * FROM halal_directory
                    WHERE company_tin = ?
                    ORDER BY expiry_date DESC
                    LIMIT 1
                    """,
                    (company_tin.strip(),),
                ).fetchone()
            elif company_name:
                row = conn.execute(
                    """
                    SELECT * FROM halal_directory
                    WHERE lower(company_name) = ?
                    ORDER BY expiry_date DESC
                    LIMIT 1
                    """,
                    (company_name.strip().lower(),),
                ).fetchone()
            else:
                row = None
        return self._row_to_dict("halal_directory", row)

    def list_halal_directory(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_directory
                ORDER BY expiry_date ASC, company_name ASC
                """
            ).fetchall()
        return [self._row_to_dict("halal_directory", row) for row in rows]

    def create_invoice_submission(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO invoice_submissions (
                    id, invoice_number, supplier_tin, buyer_tin, currency, total_amount,
                    workflow_status, source_system, next_action, blocking_reason,
                    poll_count, external_submission_id, external_document_id, payload_json,
                    validation_json, created_at, updated_at, canceled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "invoice_number",
                    "supplier_tin",
                    "buyer_tin",
                    "currency",
                    "total_amount",
                    "workflow_status",
                    "source_system",
                    "next_action",
                    "blocking_reason",
                    "poll_count",
                    "external_submission_id",
                    "external_document_id",
                    "payload_json",
                    "validation_json",
                    "created_at",
                    "updated_at",
                    "canceled_at",
                ]),
            )

    def get_invoice_submission(self, submission_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM invoice_submissions WHERE id = ?",
                (submission_id,),
            ).fetchone()
        return self._row_to_dict("invoice_submissions", row)

    def update_invoice_submission(self, submission_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = [self._serialize(value) for value in fields.values()]
        with self.connect() as conn:
            conn.execute(
                f"UPDATE invoice_submissions SET {assignments} WHERE id = ?",
                (*values, submission_id),
            )

    def create_payment_request(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO payment_requests (
                    id, invoice_submission_id, amount, currency, reference, workflow_status,
                    qr_payload, received_amount, source_system, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "invoice_submission_id",
                    "amount",
                    "currency",
                    "reference",
                    "workflow_status",
                    "qr_payload",
                    "received_amount",
                    "source_system",
                    "metadata_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_payment_request(self, request_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM payment_requests WHERE id = ?",
                (request_id,),
            ).fetchone()
        return self._row_to_dict("payment_requests", row)

    def get_payment_request_by_reference(self, reference: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM payment_requests WHERE reference = ?",
                (reference,),
            ).fetchone()
        return self._row_to_dict("payment_requests", row)

    def list_payment_requests_for_submission(self, submission_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM payment_requests
                WHERE invoice_submission_id = ?
                ORDER BY created_at ASC
                """,
                (submission_id,),
            ).fetchall()
        return [self._row_to_dict("payment_requests", row) for row in rows]

    def update_payment_request(self, request_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = [self._serialize(value) for value in fields.values()]
        with self.connect() as conn:
            conn.execute(
                f"UPDATE payment_requests SET {assignments} WHERE id = ?",
                (*values, request_id),
            )

    def create_payment_event(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO payment_events (
                    id, request_id, reference, provider, event_type, workflow_status,
                    amount, currency, external_reference, payload_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "request_id",
                    "reference",
                    "provider",
                    "event_type",
                    "workflow_status",
                    "amount",
                    "currency",
                    "external_reference",
                    "payload_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def list_payment_events(
        self,
        *,
        request_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        conditions = []
        values: list[Any] = []
        if request_id:
            conditions.append("request_id = ?")
            values.append(request_id)
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM payment_events
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (*values, limit),
            ).fetchall()
        return [self._row_to_dict("payment_events", row) for row in rows]

    def create_exception(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO exceptions (
                    id, exception_type, workflow_status, severity, resource_type,
                    resource_id, summary, source_system, details_json, resolution_note,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "exception_type",
                    "workflow_status",
                    "severity",
                    "resource_type",
                    "resource_id",
                    "summary",
                    "source_system",
                    "details_json",
                    "resolution_note",
                    "created_at",
                    "updated_at",
                ]),
            )

    def list_exceptions(
        self,
        *,
        workflow_status: str | None = None,
        resource_id: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions = []
        values: list[Any] = []
        if workflow_status:
            conditions.append("workflow_status = ?")
            values.append(workflow_status)
        if resource_id:
            conditions.append("resource_id = ?")
            values.append(resource_id)
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM exceptions
                {where_clause}
                ORDER BY created_at ASC
                """,
                tuple(values),
            ).fetchall()
        return [self._row_to_dict("exceptions", row) for row in rows]

    def resolve_exception(self, exception_id: str, resolution_note: str, updated_at: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE exceptions
                SET workflow_status = ?, resolution_note = ?, updated_at = ?
                WHERE id = ?
                """,
                ("resolved", resolution_note, updated_at, exception_id),
            )

    def get_exception(self, exception_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM exceptions WHERE id = ?", (exception_id,)).fetchone()
        return self._row_to_dict("exceptions", row)

    def create_approval(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO approvals (
                    id, action, target_resource_type, target_resource_id, policy_key,
                    workflow_status, reason, requested_payload_json, approval_context_json,
                    decision_context_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "action",
                    "target_resource_type",
                    "target_resource_id",
                    "policy_key",
                    "workflow_status",
                    "reason",
                    "requested_payload_json",
                    "approval_context_json",
                    "decision_context_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        return self._row_to_dict("approvals", row)

    def list_approvals(
        self,
        *,
        workflow_status: str | None = None,
        action: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        conditions = []
        values: list[Any] = []
        if workflow_status:
            conditions.append("workflow_status = ?")
            values.append(workflow_status)
        if action:
            conditions.append("action = ?")
            values.append(action)
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM approvals
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (*values, limit),
            ).fetchall()
        return [self._row_to_dict("approvals", row) for row in rows]

    def update_approval(self, approval_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = [self._serialize(value) for value in fields.values()]
        with self.connect() as conn:
            conn.execute(
                f"UPDATE approvals SET {assignments} WHERE id = ?",
                (*values, approval_id),
            )

    def create_workflow_run(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_runs (
                    id, root_action, current_action, workflow_status, source_system,
                    next_action, blocking_reason, initial_payload_json, final_output_json,
                    execution_log_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "root_action",
                    "current_action",
                    "workflow_status",
                    "source_system",
                    "next_action",
                    "blocking_reason",
                    "initial_payload_json",
                    "final_output_json",
                    "execution_log_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_workflow_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM workflow_runs WHERE id = ?", (run_id,)).fetchone()
        return self._row_to_dict("workflow_runs", row)

    def list_workflow_runs(self, *, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM workflow_runs
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("workflow_runs", row) for row in rows]

    def update_workflow_run(self, run_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = [self._serialize(value) for value in fields.values()]
        with self.connect() as conn:
            conn.execute(
                f"UPDATE workflow_runs SET {assignments} WHERE id = ?",
                (*values, run_id),
            )

    def create_trade_submission(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO trade_submissions (
                    id, doc_type, workflow_status, source_system, validation_json,
                    payload_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "doc_type",
                    "workflow_status",
                    "source_system",
                    "validation_json",
                    "payload_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_trade_submission(self, submission_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM trade_submissions WHERE id = ?", (submission_id,)).fetchone()
        return self._row_to_dict("trade_submissions", row)

    def create_halal_pack(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_packs (
                    id, applicant_name, workflow_status, source_system, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "applicant_name",
                    "workflow_status",
                    "source_system",
                    "payload_json",
                    "created_at",
                ]),
            )

    def get_halal_pack(self, pack_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_packs WHERE id = ?", (pack_id,)).fetchone()
        return self._row_to_dict("halal_packs", row)

    def upsert_halal_supplier(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_supplier_registry (
                    id, supplier_tin, supplier_name, certificate_ref, certificate_status,
                    expiry_date, risk_level, products_json, metadata_json, source_system,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    supplier_tin = excluded.supplier_tin,
                    supplier_name = excluded.supplier_name,
                    certificate_ref = excluded.certificate_ref,
                    certificate_status = excluded.certificate_status,
                    expiry_date = excluded.expiry_date,
                    risk_level = excluded.risk_level,
                    products_json = excluded.products_json,
                    metadata_json = excluded.metadata_json,
                    source_system = excluded.source_system,
                    updated_at = excluded.updated_at
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "supplier_tin",
                    "supplier_name",
                    "certificate_ref",
                    "certificate_status",
                    "expiry_date",
                    "risk_level",
                    "products_json",
                    "metadata_json",
                    "source_system",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_halal_supplier(self, supplier_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM halal_supplier_registry WHERE id = ?",
                (supplier_id,),
            ).fetchone()
        return self._row_to_dict("halal_supplier_registry", row)

    def get_halal_supplier_by_tin(self, supplier_tin: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM halal_supplier_registry
                WHERE supplier_tin = ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (supplier_tin,),
            ).fetchone()
        return self._row_to_dict("halal_supplier_registry", row)

    def list_halal_suppliers(self, *, risk_level: str | None = None) -> list[dict[str, Any]]:
        values: list[Any] = []
        where_clause = ""
        if risk_level:
            where_clause = "WHERE risk_level = ?"
            values.append(risk_level)
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM halal_supplier_registry
                {where_clause}
                ORDER BY risk_level DESC, expiry_date ASC, supplier_name ASC
                """,
                tuple(values),
            ).fetchall()
        return [self._row_to_dict("halal_supplier_registry", row) for row in rows]

    def create_halal_bom_graph(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_bom_graphs (
                    id, applicant_name, product_name, workflow_status, source_system,
                    payload_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "applicant_name",
                    "product_name",
                    "workflow_status",
                    "source_system",
                    "payload_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_halal_bom_graph(self, graph_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_bom_graphs WHERE id = ?", (graph_id,)).fetchone()
        return self._row_to_dict("halal_bom_graphs", row)

    def create_halal_workflow(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_workflows (
                    id, applicant_name, product_name, scheme, framework, current_stage,
                    workflow_status, source_system, payload_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "applicant_name",
                    "product_name",
                    "scheme",
                    "framework",
                    "current_stage",
                    "workflow_status",
                    "source_system",
                    "payload_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_halal_workflow(self, workflow_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_workflows WHERE id = ?", (workflow_id,)).fetchone()
        return self._row_to_dict("halal_workflows", row)

    def update_halal_workflow(self, workflow_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = [self._serialize(value) for value in fields.values()]
        with self.connect() as conn:
            conn.execute(
                f"UPDATE halal_workflows SET {assignments} WHERE id = ?",
                (*values, workflow_id),
            )

    def create_halal_checklist(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_checklists (
                    id, applicant_name, framework, workflow_status, score,
                    source_system, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "applicant_name",
                    "framework",
                    "workflow_status",
                    "score",
                    "source_system",
                    "payload_json",
                    "created_at",
                ]),
            )

    def get_halal_checklist(self, checklist_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_checklists WHERE id = ?", (checklist_id,)).fetchone()
        return self._row_to_dict("halal_checklists", row)

    def create_halal_audit_query(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_audit_queries (
                    id, workflow_id, query_title, workflow_status, severity,
                    source_system, payload_json, response_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "workflow_id",
                    "query_title",
                    "workflow_status",
                    "severity",
                    "source_system",
                    "payload_json",
                    "response_json",
                    "created_at",
                    "updated_at",
                ]),
            )

    def get_halal_audit_query(self, query_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_audit_queries WHERE id = ?", (query_id,)).fetchone()
        return self._row_to_dict("halal_audit_queries", row)

    def list_halal_audit_queries(
        self,
        *,
        workflow_id: str | None = None,
        workflow_status: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions = []
        values: list[Any] = []
        if workflow_id:
            conditions.append("workflow_id = ?")
            values.append(workflow_id)
        if workflow_status:
            conditions.append("workflow_status = ?")
            values.append(workflow_status)
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM halal_audit_queries
                {where_clause}
                ORDER BY created_at ASC
                """,
                tuple(values),
            ).fetchall()
        return [self._row_to_dict("halal_audit_queries", row) for row in rows]

    def update_halal_audit_query(self, query_id: str, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = [self._serialize(value) for value in fields.values()]
        with self.connect() as conn:
            conn.execute(
                f"UPDATE halal_audit_queries SET {assignments} WHERE id = ?",
                (*values, query_id),
            )

    def create_halal_document_share(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_document_shares (
                    id, workflow_id, share_target, workflow_status, source_system,
                    payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "workflow_id",
                    "share_target",
                    "workflow_status",
                    "source_system",
                    "payload_json",
                    "created_at",
                ]),
            )

    def get_halal_document_share(self, share_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_document_shares WHERE id = ?", (share_id,)).fetchone()
        return self._row_to_dict("halal_document_shares", row)

    def create_halal_export_dossier(self, record: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO halal_export_dossiers (
                    id, applicant_name, product_name, workflow_status, source_system,
                    payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(self._serialize(record[key]) for key in [
                    "id",
                    "applicant_name",
                    "product_name",
                    "workflow_status",
                    "source_system",
                    "payload_json",
                    "created_at",
                ]),
            )

    def get_halal_export_dossier(self, dossier_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM halal_export_dossiers WHERE id = ?", (dossier_id,)).fetchone()
        return self._row_to_dict("halal_export_dossiers", row)

    def list_halal_packs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_packs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("halal_packs", row) for row in rows]

    def list_halal_bom_graphs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_bom_graphs
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("halal_bom_graphs", row) for row in rows]

    def list_halal_workflows(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_workflows
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("halal_workflows", row) for row in rows]

    def list_halal_checklists(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_checklists
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("halal_checklists", row) for row in rows]

    def list_halal_document_shares(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_document_shares
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("halal_document_shares", row) for row in rows]

    def list_halal_export_dossiers(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM halal_export_dossiers
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict("halal_export_dossiers", row) for row in rows]
