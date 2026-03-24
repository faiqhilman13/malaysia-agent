from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import Settings
from .service import InputError, NotFoundError, OperationsService


ROUTES = {
    ("GET", "/health"): None,
    ("POST", "/v1/workflows/run"): "workflows.run",
    ("POST", "/v1/workflows/status"): "workflows.status",
    ("POST", "/v1/approvals/list"): "approvals.list",
    ("POST", "/v1/approvals/approve"): "approvals.approve",
    ("POST", "/v1/approvals/reject"): "approvals.reject",
    ("POST", "/v1/entities/resolve"): "entities.resolve",
    ("POST", "/v1/entities/verify-taxpayer"): "entities.verify_taxpayer",
    ("POST", "/v1/entities/verify-business-registry"): "entities.verify_business_registry",
    ("POST", "/v1/invoices/validate"): "invoices.validate",
    ("POST", "/v1/invoices/submit"): "invoices.submit",
    ("POST", "/v1/invoices/status"): "invoices.status",
    ("POST", "/v1/invoices/cancel"): "invoices.cancel",
    ("POST", "/v1/payments/create-request"): "payments.create_request",
    ("POST", "/v1/payments/events/ingest"): "payments.ingest_event",
    ("POST", "/v1/webhooks/payments/paynet"): "payments.ingest_event",
    ("POST", "/v1/payments/reconcile"): "payments.reconcile",
    ("POST", "/v1/exceptions/list"): "exceptions.list",
    ("POST", "/v1/exceptions/resolve"): "exceptions.resolve",
    ("POST", "/v1/trade/doc-pack/validate"): "trade.doc_pack.validate",
    ("POST", "/v1/trade/submission/status"): "trade.submission.status",
    ("POST", "/v1/halal/status/lookup"): "halal.status.lookup",
    ("POST", "/v1/halal/evidence-pack/generate"): "halal.evidence_pack.generate",
    ("POST", "/v1/halal/suppliers/upsert"): "halal.suppliers.upsert",
    ("POST", "/v1/halal/suppliers/list"): "halal.suppliers.list",
    ("POST", "/v1/halal/bom/graph/generate"): "halal.bom.graph.generate",
    ("POST", "/v1/halal/renewals/list"): "halal.renewals.list",
    ("POST", "/v1/halal/workflows/create"): "halal.workflows.create",
    ("POST", "/v1/halal/workflows/status"): "halal.workflows.status",
    ("POST", "/v1/halal/checklists/evaluate"): "halal.checklists.evaluate",
    ("POST", "/v1/halal/audits/create-query"): "halal.audits.create_query",
    ("POST", "/v1/halal/audits/respond-query"): "halal.audits.respond_query",
    ("POST", "/v1/halal/documents/share"): "halal.documents.share",
    ("POST", "/v1/halal/export-dossier/generate"): "halal.export_dossier.generate",
    ("POST", "/v1/halal/dashboard/snapshot"): "halal.dashboard.snapshot",
    ("POST", "/v1/halal/pilot/seed-fnb"): "halal.pilot.seed_fnb",
    ("POST", "/v1/providers/myinvois/login"): "providers.myinvois.login",
    ("POST", "/v1/providers/myinvois/document-types"): "providers.myinvois.document_types",
    ("POST", "/v1/providers/myinvois/validate-tin"): "providers.myinvois.validate_tin",
    ("POST", "/v1/providers/myinvois/search-tin"): "providers.myinvois.search_tin",
    ("POST", "/v1/providers/myinvois/submit-documents"): "providers.myinvois.submit_documents",
    ("POST", "/v1/providers/myinvois/get-submission"): "providers.myinvois.get_submission",
    ("POST", "/v1/providers/myinvois/cancel-document"): "providers.myinvois.cancel_document",
    ("POST", "/v1/providers/cidb/states"): "providers.cidb.states",
    ("POST", "/v1/providers/cidb/labour-wage-rate"): "providers.cidb.labour_wage_rate",
    ("POST", "/v1/providers/cidb/building-material-price"): "providers.cidb.building_material_price",
    ("POST", "/v1/providers/cidb/machinery-rates"): "providers.cidb.machinery_rates",
}

STATIC_ROUTES = {
    "/app/halal-ops": "docs/halal-ops-workbench.html",
    "/app/project-status": "docs/project-status-dashboard.html",
    "/app/halal-attack-plan": "docs/halal-vertical-attack-plan.html",
}


class OperationsHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], service: OperationsService, settings: Settings) -> None:
        super().__init__(server_address, OperationsRequestHandler)
        self.service = service
        self.settings = settings


class OperationsRequestHandler(BaseHTTPRequestHandler):
    server: OperationsHTTPServer

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch()

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def _dispatch(self) -> None:
        path = urlparse(self.path).path
        if self.command == "GET" and path in STATIC_ROUTES:
            self._send_file(self.server.settings.project_root / STATIC_ROUTES[path])
            return
        route = ROUTES.get((self.command, path))
        if route is None and path != "/health":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "route_not_found"})
            return

        try:
            if path == "/health":
                response = self.server.service.health()
            else:
                payload = self._read_json_body()
                response = self.server.service.invoke(route, payload)
            self._send_json(HTTPStatus.OK, response)
        except InputError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except NotFoundError as exc:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
        except json.JSONDecodeError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": f"invalid_json: {exc.msg}"})
        except Exception as exc:  # pragma: no cover
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        if not raw.strip():
            return {}
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise InputError("JSON body must be an object.")
        return payload

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "file_not_found"})
            return
        body = path.read_bytes()
        content_type = "text/html; charset=utf-8" if path.suffix == ".html" else "text/plain; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def make_server(settings: Settings, host: str = "127.0.0.1", port: int = 8080) -> OperationsHTTPServer:
    service = OperationsService(settings)
    return OperationsHTTPServer((host, port), service, settings)


def serve(settings: Settings, host: str = "127.0.0.1", port: int = 8080) -> None:
    server = make_server(settings, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
