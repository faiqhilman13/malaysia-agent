from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from malaysia_agent_ops.config import get_settings
from malaysia_agent_ops.mcp_server import McpStdioServer
from malaysia_agent_ops.providers import CIDBClient, MyInvoisClient
from malaysia_agent_ops.server import ROUTES
from malaysia_agent_ops.service import OperationsService


class OperationsServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.settings = get_settings(project_root=Path(self.temp_dir.name), db_path=db_path)
        self.service = OperationsService(self.settings)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_phase1_end_to_end_flow(self) -> None:
        resolved = self.service.resolve_entity({"query": "Acme"})
        self.assertEqual(resolved["status"], "success")
        supplier_tin = resolved["data"]["primary_match"]["tin"]

        taxpayer = self.service.verify_taxpayer({"tin": supplier_tin})
        self.assertEqual(taxpayer["status"], "success")

        submit = self.service.submit_invoice(
            {
                "invoice_number": "INV-1001",
                "issue_date": "2026-03-24",
                "supplier_tin": "C1234567801",
                "buyer_tin": "C1234567802",
                "line_items": [
                    {"description": "Middleware subscription", "quantity": 1, "unit_price": 100.0},
                    {"description": "Support retainer", "quantity": 1, "unit_price": 20.0},
                ],
                "total_amount": 120.0,
            }
        )
        self.assertEqual(submit["status"], "success")
        submission_id = submit["data"]["submission_id"]

        status = self.service.invoice_status({"submission_id": submission_id})
        self.assertEqual(status["data"]["submission_status"], "validated")

        payment = self.service.create_payment_request({"submission_id": submission_id})
        self.assertEqual(payment["status"], "success")
        request_id = payment["data"]["request_id"]

        reconciled = self.service.reconcile_payment(
            {
                "request_id": request_id,
                "received_amount": 120.0,
                "external_reference": "BANKREF-001",
            }
        )
        self.assertEqual(reconciled["status"], "success")

        exceptions = self.service.list_exceptions({})
        self.assertEqual(exceptions["data"]["items"], [])

    def test_payment_mismatch_creates_exception(self) -> None:
        submit = self.service.submit_invoice(
            {
                "invoice_number": "INV-1002",
                "issue_date": "2026-03-24",
                "supplier_tin": "C1234567801",
                "buyer_tin": "C1234567804",
                "line_items": [
                    {"description": "Settlement", "quantity": 1, "unit_price": 150.0},
                ],
                "total_amount": 150.0,
            }
        )
        submission_id = submit["data"]["submission_id"]
        self.service.invoice_status({"submission_id": submission_id})
        payment = self.service.create_payment_request({"submission_id": submission_id})

        mismatch = self.service.reconcile_payment(
            {
                "request_id": payment["data"]["request_id"],
                "received_amount": 149.0,
                "external_reference": "BANKREF-ERR",
            }
        )
        self.assertEqual(mismatch["status"], "blocked")

        exceptions = self.service.list_exceptions({})
        self.assertEqual(len(exceptions["data"]["items"]), 1)
        self.assertEqual(exceptions["data"]["items"][0]["exception_type"], "payment_mismatch")

    def test_trade_and_halal_surfaces(self) -> None:
        trade = self.service.trade_doc_pack_validate(
            {
                "doc_type": "import_k1",
                "documents": {
                    "commercial_invoice": True,
                    "packing_list": True,
                },
            }
        )
        self.assertEqual(trade["status"], "blocked")
        self.assertIn("hs_code", trade["data"]["validation"]["missing_documents"])

        halal = self.service.halal_status_lookup({"company_tin": "C1234567803"})
        self.assertEqual(halal["status"], "success")

        pack = self.service.halal_evidence_pack_generate(
            {
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "product_name": "Instant curry paste",
                "bom": [
                    {"ingredient": "Packaging", "supplier_tin": "C1234567801"},
                    {"ingredient": "Main paste", "supplier_tin": "C1234567803"},
                ],
                "supporting_documents": [
                    "business_registration",
                    "product_specification",
                    "ingredient_declarations",
                ],
            }
        )
        self.assertEqual(pack["status"], "success")
        self.assertEqual(pack["data"]["workflow_status"], "ready")

    def test_halal_ops_layer_supports_registry_graph_workflow_and_dossier(self) -> None:
        supplier = self.service.halal_suppliers_upsert({"supplier_tin": "C1234567803"})
        self.assertEqual(supplier["status"], "success")
        self.assertEqual(supplier["data"]["supplier"]["certificate_status"], "active")

        graph = self.service.halal_bom_graph_generate(
            {
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "product_name": "Instant curry paste",
                "bom": [
                    {"ingredient": "Main paste", "supplier_tin": "C1234567803"},
                    {"ingredient": "Packaging", "supplier_tin": "C1234567801"},
                ],
            }
        )
        self.assertEqual(graph["status"], "success")
        graph_id = graph["data"]["graph_id"]

        checklist = self.service.halal_checklists_evaluate(
            {
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "framework": "IHCS",
                "completed_controls": [
                    "halal_policy",
                    "ingredient_register",
                    "supplier_certificate_control",
                    "traceability_log",
                    "staff_training",
                ],
            }
        )
        self.assertEqual(checklist["status"], "success")
        checklist_id = checklist["data"]["checklist_id"]

        pack = self.service.halal_evidence_pack_generate(
            {
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "product_name": "Instant curry paste",
                "bom": [
                    {"ingredient": "Main paste", "supplier_tin": "C1234567803"},
                    {"ingredient": "Packaging", "supplier_tin": "C1234567801"},
                ],
                "supporting_documents": [
                    "business_registration",
                    "product_specification",
                    "ingredient_declarations",
                ],
            }
        )
        self.assertEqual(pack["status"], "success")
        self.assertTrue(pack["data"]["myhalalingredients_records"])
        pack_id = pack["data"]["pack_id"]

        workflow = self.service.halal_workflows_create(
            {
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "product_name": "Instant curry paste",
                "framework": "IHCS",
                "supplier_registry_ready": True,
                "bom_graph_id": graph_id,
                "pack_id": pack_id,
                "checklist_id": checklist_id,
            }
        )
        self.assertEqual(workflow["status"], "success")
        workflow_id = workflow["data"]["workflow_id"]

        query = self.service.halal_audits_create_query(
            {
                "workflow_id": workflow_id,
                "query_title": "Clarify supplier declaration",
                "query_text": "Upload the refreshed declaration for the packaging supplier.",
                "requested_documents": ["packaging_supplier_declaration"],
            }
        )
        self.assertEqual(query["status"], "success")
        query_id = query["data"]["query_id"]

        responded = self.service.halal_audits_respond_query(
            {
                "query_id": query_id,
                "response_summary": "Updated supplier declaration attached.",
                "attachments": ["packaging_supplier_declaration_v2.pdf"],
            }
        )
        self.assertEqual(responded["status"], "success")

        workflow_status = self.service.halal_workflows_status({"workflow_id": workflow_id})
        self.assertEqual(workflow_status["data"]["current_stage"], "ready_for_submission")

        dossier = self.service.halal_export_dossier_generate(
            {
                "workflow_id": workflow_id,
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "product_name": "Instant curry paste",
                "target_markets": ["United Arab Emirates", "Indonesia"],
                "supporting_documents": [
                    "business_registration",
                    "product_specification",
                    "ingredient_declarations",
                ],
            }
        )
        self.assertEqual(dossier["status"], "success")
        dossier_id = dossier["data"]["dossier_id"]

        share = self.service.halal_documents_share(
            {
                "workflow_id": workflow_id,
                "dossier_id": dossier_id,
                "share_target": "oem_partner",
                "documents": ["export_dossier.pdf", "supplier_matrix.xlsx"],
                "recipients": ["ops@oem.example"],
            }
        )
        self.assertEqual(share["status"], "success")

        renewals = self.service.halal_renewals_list({"within_days": 10000})
        self.assertEqual(renewals["status"], "success")
        self.assertGreaterEqual(len(renewals["data"]["items"]), 1)

    def test_halal_bom_and_registry_block_on_non_active_supplier(self) -> None:
        supplier = self.service.halal_suppliers_upsert({"supplier_tin": "C1234567805"})
        self.assertEqual(supplier["status"], "blocked")

        graph = self.service.halal_bom_graph_generate(
            {
                "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
                "product_name": "Instant curry paste",
                "bom": [
                    {"ingredient": "Gelatine additive", "supplier_tin": "C1234567805"},
                ],
            }
        )
        self.assertEqual(graph["status"], "blocked")
        self.assertEqual(graph["data"]["issues"][0]["issue"], "supplier_without_active_certificate")

    def test_halal_pilot_seed_and_dashboard_snapshot(self) -> None:
        seeded = self.service.halal_pilot_seed_fnb({})
        self.assertEqual(seeded["status"], "success")
        self.assertEqual(seeded["data"]["sector"], "Food and beverage")
        self.assertTrue(seeded["data"]["workflow_id"])

        snapshot = self.service.halal_dashboard_snapshot({})
        self.assertEqual(snapshot["status"], "success")
        self.assertGreaterEqual(snapshot["data"]["summary"]["supplier_registry_total"], 3)
        self.assertGreaterEqual(snapshot["data"]["summary"]["export_dossiers_total"], 1)
        self.assertEqual(snapshot["data"]["pilot_profile"]["pilot_id"], "barakah-fnb-pilot")

    def test_provider_myinvois_login_with_mocked_remote(self) -> None:
        with patch.object(MyInvoisClient, "default_credentials", return_value=("client-id", "client-secret")):
            with patch.object(
                MyInvoisClient,
                "login_taxpayer",
                return_value={"access_token": "token-123", "expires_in": 3600},
            ):
                response = self.service.provider_myinvois_login(
                    {"environment": "sandbox", "mode": "taxpayer"}
                )
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["data"]["auth"]["access_token"], "token-123")
        self.assertEqual(response["data"]["environment"], "sandbox")

    def test_provider_cidb_dataset_with_mocked_remote(self) -> None:
        with patch.object(
            CIDBClient,
            "get_states",
            return_value=[{"id": 10, "name": "Selangor", "code": "SGR"}],
        ):
            with patch.object(
                CIDBClient,
                "get_building_material_price",
                return_value={"items": [{"specification": "Cement", "price": 18.2}]},
            ):
                response = self.service.provider_cidb_building_material_price(
                    {
                        "access_token": "cidb-token",
                        "state_code": "SGR",
                        "year": 2026,
                    }
                )
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["data"]["state"]["code"], "SGR")
        self.assertEqual(response["data"]["building_material_price"]["items"][0]["price"], 18.2)

    def test_workflow_runner_completes_local_invoice_flow_when_payment_event_is_present(self) -> None:
        run = self.service.workflows_run(
            {
                "action": "invoices.submit",
                "payload": {
                    "invoice_number": "INV-RUN-1",
                    "issue_date": "2026-03-24",
                    "supplier_tin": "C1234567801",
                    "buyer_tin": "C1234567802",
                    "line_items": [
                        {"description": "Agentic ops subscription", "quantity": 1, "unit_price": 90.0},
                    ],
                    "total_amount": 90.0,
                    "payment_event": {
                        "event_type": "payment_received",
                        "payment_status": "succeeded",
                        "amount": 90.0,
                        "external_reference": "PAY-EVT-1",
                    },
                },
            }
        )
        self.assertEqual(run["status"], "success")
        self.assertEqual(run["data"]["workflow_status"], "completed")
        self.assertEqual(run["data"]["final_response"]["data"]["workflow_status"], "matched")

    def test_workflow_runner_waits_for_external_payment_event_when_not_supplied(self) -> None:
        run = self.service.workflows_run(
            {
                "action": "invoices.submit",
                "payload": {
                    "invoice_number": "INV-RUN-2",
                    "issue_date": "2026-03-24",
                    "supplier_tin": "C1234567801",
                    "buyer_tin": "C1234567802",
                    "line_items": [
                        {"description": "Agentic ops subscription", "quantity": 1, "unit_price": 75.0},
                    ],
                    "total_amount": 75.0,
                },
            }
        )
        self.assertEqual(run["status"], "blocked")
        self.assertEqual(run["data"]["workflow_status"], "awaiting_external_event")
        self.assertEqual(run["blocking_reason"], "missing_external_input_for_next_action")

    def test_payment_event_ingestion_sets_invoice_paid(self) -> None:
        submit = self.service.submit_invoice(
            {
                "invoice_number": "INV-EVT-1",
                "issue_date": "2026-03-24",
                "supplier_tin": "C1234567801",
                "buyer_tin": "C1234567802",
                "line_items": [
                    {"description": "Ops automation", "quantity": 1, "unit_price": 110.0},
                ],
                "total_amount": 110.0,
            }
        )
        submission_id = submit["data"]["submission_id"]
        self.service.invoice_status({"submission_id": submission_id})
        payment = self.service.create_payment_request({"submission_id": submission_id})
        event = self.service.ingest_payment_event(
            {
                "request_id": payment["data"]["request_id"],
                "event_type": "payment_received",
                "payment_status": "succeeded",
                "amount": 110.0,
                "external_reference": "PAY-EVT-2",
            }
        )
        self.assertEqual(event["status"], "success")
        invoice = self.service.invoice_status({"submission_id": submission_id})
        self.assertEqual(invoice["data"]["submission_status"], "paid")

    def test_approval_gate_blocks_then_allows_real_invoice_submission(self) -> None:
        blocked = self.service.invoke(
            "invoices.submit",
            {
                "provider": "real",
                "invoice_number": "INV-REAL-1",
                "documents": [{"format": "JSON", "document": "e30=", "documentHash": "hash", "codeNumber": "INV-REAL-1"}],
            }
        )
        self.assertEqual(blocked["status"], "blocked")
        approval_id = blocked["data"]["approval_id"]

        approved = self.service.approvals_approve(
            {
                "approval_id": approval_id,
                "identity": {
                    "authority_id": "user-1",
                    "authority_type": "human",
                    "provider": "manual",
                    "verified": True,
                },
            }
        )
        self.assertEqual(approved["status"], "success")

        with patch.object(
            OperationsService,
            "_myinvois_client_and_token_for_execution",
            return_value=(MyInvoisClient(self.settings, environment="sandbox"), "token-123"),
        ):
            with patch.object(
                MyInvoisClient,
                "submit_documents",
                return_value={
                    "submissionUID": "SUBMISSION123",
                    "acceptedDocuments": [{"uuid": "DOC123", "invoiceCodeNumber": "INV-REAL-1"}],
                    "rejectedDocuments": [],
                },
            ):
                submitted = self.service.submit_invoice(
                    {
                        "provider": "real",
                        "approval_id": approval_id,
                        "invoice_number": "INV-REAL-1",
                        "documents": [{"format": "JSON", "document": "e30=", "documentHash": "hash", "codeNumber": "INV-REAL-1"}],
                    }
                )
        self.assertEqual(submitted["status"], "success")
        self.assertEqual(submitted["data"]["execution_mode"], "real")
        self.assertEqual(submitted["data"]["remote_submission"]["submissionUID"], "SUBMISSION123")


class ProviderRequestShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "shape.db"
        self.settings = get_settings(project_root=Path(self.temp_dir.name), db_path=db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_myinvois_submit_documents_uses_official_path(self) -> None:
        class Recorder:
            def __init__(self) -> None:
                self.last_call = None

            def request_json(self, **kwargs):
                self.last_call = kwargs
                return {"ok": True}

        recorder = Recorder()
        client = MyInvoisClient(self.settings, environment="sandbox", http=recorder)
        client.submit_documents(access_token="token-123", documents=[{"format": "JSON"}])
        self.assertEqual(
            recorder.last_call["url"],
            "https://preprod-api.myinvois.hasil.gov.my/api/v1.0/documentsubmissions/",
        )
        self.assertEqual(recorder.last_call["headers"]["Authorization"], "Bearer token-123")

    def test_cidb_states_uses_official_path(self) -> None:
        class Recorder:
            def __init__(self) -> None:
                self.last_call = None

            def request_json(self, **kwargs):
                self.last_call = kwargs
                return [{"id": 1, "name": "Johor", "code": "JHR"}]

        recorder = Recorder()
        client = CIDBClient(self.settings, http=recorder)
        client.get_states(access_token="cidb-token")
        self.assertEqual(
            recorder.last_call["url"],
            "https://n3c-api.cidb.gov.my/internal/states",
        )
        self.assertEqual(recorder.last_call["headers"]["Authorization"], "Bearer cidb-token")


class ApiContractTests(unittest.TestCase):
    def test_route_map_exposes_expected_contracts(self) -> None:
        self.assertEqual(ROUTES[("POST", "/v1/workflows/run")], "workflows.run")
        self.assertEqual(ROUTES[("POST", "/v1/workflows/status")], "workflows.status")
        self.assertEqual(ROUTES[("POST", "/v1/approvals/list")], "approvals.list")
        self.assertEqual(ROUTES[("POST", "/v1/approvals/approve")], "approvals.approve")
        self.assertEqual(ROUTES[("POST", "/v1/entities/resolve")], "entities.resolve")
        self.assertEqual(ROUTES[("POST", "/v1/invoices/submit")], "invoices.submit")
        self.assertEqual(ROUTES[("POST", "/v1/payments/events/ingest")], "payments.ingest_event")
        self.assertEqual(ROUTES[("POST", "/v1/payments/reconcile")], "payments.reconcile")
        self.assertEqual(ROUTES[("POST", "/v1/trade/doc-pack/validate")], "trade.doc_pack.validate")
        self.assertEqual(ROUTES[("POST", "/v1/halal/evidence-pack/generate")], "halal.evidence_pack.generate")
        self.assertEqual(ROUTES[("POST", "/v1/halal/suppliers/upsert")], "halal.suppliers.upsert")
        self.assertEqual(ROUTES[("POST", "/v1/halal/workflows/create")], "halal.workflows.create")
        self.assertEqual(ROUTES[("POST", "/v1/halal/export-dossier/generate")], "halal.export_dossier.generate")
        self.assertEqual(ROUTES[("POST", "/v1/halal/dashboard/snapshot")], "halal.dashboard.snapshot")
        self.assertEqual(ROUTES[("POST", "/v1/halal/pilot/seed-fnb")], "halal.pilot.seed_fnb")
        self.assertEqual(ROUTES[("POST", "/v1/providers/myinvois/login")], "providers.myinvois.login")
        self.assertEqual(ROUTES[("POST", "/v1/providers/cidb/states")], "providers.cidb.states")
        self.assertIsNone(ROUTES[("GET", "/health")])


class McpContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "mcp.db"
        self.settings = get_settings(project_root=Path(self.temp_dir.name), db_path=db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_mcp_server_initializes_and_calls_tool(self) -> None:
        server = McpStdioServer(self.settings)
        input_stream = io.StringIO(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"},
                    },
                }
            )
            + "\n"
            + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
            + "\n"
            + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            + "\n"
            + json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "entities.resolve",
                        "arguments": {"query": "Acme"},
                    },
                }
            )
            + "\n"
        )
        output_stream = io.StringIO()
        server.serve_forever(in_stream=input_stream, out_stream=output_stream)
        lines = [json.loads(line) for line in output_stream.getvalue().splitlines() if line.strip()]
        self.assertEqual(lines[0]["result"]["protocolVersion"], "2025-11-25")
        tool_names = [tool["name"] for tool in lines[1]["result"]["tools"]]
        self.assertIn("workflows.run", tool_names)
        self.assertIn("payments.ingest_event", tool_names)
        self.assertEqual(lines[2]["result"]["structuredContent"]["status"], "success")
