# Malaysia Agent Ops

Execution-layer alpha for Malaysia-specific agent workflows, exposed through JSON-first CLI, HTTP API, MCP, and a repo-local agent skill.

This MVP implements the Phase 1 wedge from the strategy:

- `workflows.run`
- `workflows.status`
- `approvals.list`
- `approvals.approve`
- `approvals.reject`
- `entities.resolve`
- `entities.verify_taxpayer`
- `entities.verify_business_registry`
- `invoices.validate`
- `invoices.submit`
- `invoices.status`
- `invoices.cancel`
- `payments.create_request`
- `payments.ingest_event`
- `payments.reconcile`
- `exceptions.list`
- `exceptions.resolve`

It also includes the Phase 2/3 interface surfaces so the contract shape is already stable:

- `trade.doc_pack.validate`
- `trade.submission.status`
- `halal.status.lookup`
- `halal.evidence_pack.generate`

The halal module now also includes an execution-oriented compliance layer:

- `halal.suppliers.upsert`
- `halal.suppliers.list`
- `halal.bom.graph.generate`
- `halal.renewals.list`
- `halal.workflows.create`
- `halal.workflows.status`
- `halal.checklists.evaluate`
- `halal.audits.create_query`
- `halal.audits.respond_query`
- `halal.documents.share`
- `halal.export_dossier.generate`
- `halal.dashboard.snapshot`
- `halal.pilot.seed_fnb`

## Why this implementation is scoped this way

The immediate product is not a full regulated network integration. It is the middleware layer that lets an agent:

1. Resolve and verify Malaysian business identities.
2. Validate and submit an invoice into a sandbox or real MyInvois workflow.
3. Create a DuitNow-shaped payment request.
4. Progress a workflow automatically until it completes, blocks, or waits for an external event.
5. Stop only for approvals, exceptions, or missing external inputs.

This keeps the MVP inside the workflow orchestration layer instead of pretending to be a licensed payments or tax operator.

## Stack

- Python stdlib only
- SQLite for durable state
- Local HTTP server for the API
- CLI that invokes the same service layer as the API

The package is intentionally dependency-free so it runs in this environment without installing anything.

## Docs

- [Purpose and architecture](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/purpose-and-architecture.md)
- [Roadmap and phases](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/roadmap-and-phases.md)
- [Halal ground truth register](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/halal-ground-truth-register.md)
- [Halal precheck PRD](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/halal-precheck-prd.md)
- [Halal precheck demo guide](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/halal-precheck-demo-guide.md)
- [Project status dashboard](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/project-status-dashboard.html)
- [Halal vertical attack plan](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/halal-vertical-attack-plan.html)
- [Halal operations workbench](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/halal-ops-workbench.html)
- [Repo-local agent skill](/Users/faiqhilman/Projects/malaysia-agent-ops/skill/SKILL.md)

## Current state

- `45` action contracts are exposed through the shared service layer.
- The autonomous runner, approval store, payment event ingestion path, MCP server, and repo-local skill are implemented.
- `MyInvois` official actions are wired, but live execution is still gated by credentials and compliant document payloads.
- The core product direction is halal dossier pre-check plus Malaysia tax/e-invoicing workflows.
- `CIDB` remains available as an experimental provider adapter, but it is no longer a core product pillar.
- The richest vertical in the repo is the halal operations layer with a seeded F&B pilot, persistent artifact graph, browser workbench, and source-grounded precheck reports.

## Run

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py serve --host 127.0.0.1 --port 8080
```

Run the MCP server:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py mcp
```

Health check:

```bash
curl http://127.0.0.1:8080/health
```

Frontend workbench:

```bash
open http://127.0.0.1:8080/app/halal-ops
```

## CLI examples

Resolve an entity:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action entities.resolve --json '{"query":"Acme"}' --pretty
```

Submit an invoice:

```bash
python3 manage.py action invoices.submit --json '{
  "invoice_number": "INV-1001",
  "issue_date": "2026-03-24",
  "supplier_tin": "C1234567801",
  "buyer_tin": "C1234567802",
  "line_items": [
    {"description": "Middleware subscription", "quantity": 1, "unit_price": 100.00},
    {"description": "Support retainer", "quantity": 1, "unit_price": 20.00}
  ],
  "total_amount": 120.00
}' --pretty
```

Poll invoice status:

```bash
python3 manage.py action invoices.status --json '{"submission_id":"<submission-id>"}' --pretty
```

Create a payment request:

```bash
python3 manage.py action payments.create_request --json '{"submission_id":"<submission-id>"}' --pretty
```

Ingest a payment event:

```bash
python3 manage.py action payments.ingest_event --json '{
  "request_id":"<request-id>",
  "event_type":"payment_received",
  "payment_status":"succeeded",
  "amount":120.00,
  "external_reference":"BANKREF-001"
}' --pretty
```

Manual reconcile fallback:

```bash
python3 manage.py action payments.reconcile --json '{
  "request_id":"<request-id>",
  "received_amount":120.00,
  "external_reference":"BANKREF-001"
}' --pretty
```

Register or refresh a halal supplier in the compliance registry:

```bash
python3 manage.py action halal.suppliers.upsert --json '{
  "supplier_tin": "C1234567803"
}' --pretty
```

Generate a halal BOM compliance graph:

```bash
python3 manage.py action halal.bom.graph.generate --json '{
  "applicant_name": "Barakah Foods Manufacturing Sdn Bhd",
  "product_name": "Instant curry paste",
  "bom": [
    {"ingredient": "Main paste", "supplier_tin": "C1234567803"},
    {"ingredient": "Packaging", "supplier_tin": "C1234567801"}
  ]
}' --pretty
```

Seed the F&B halal pilot dataset:

```bash
python3 manage.py action halal.pilot.seed_fnb --json '{}' --pretty
```

Read the aggregated halal dashboard snapshot:

```bash
python3 manage.py action halal.dashboard.snapshot --json '{}' --pretty
```

Run a source-grounded halal dossier precheck:

```bash
python3 manage.py halal precheck run \
  --file examples/barakah-curry-paste.dossier.json \
  --ocr-dir examples/ocr/barakah \
  --out-dir reports/barakah \
  --pretty
```

Run the failing demo dossier:

```bash
python3 manage.py halal precheck run \
  --file examples/barakah-curry-paste-incomplete.dossier.json \
  --ocr-dir examples/ocr/barakah-failing \
  --out-dir reports/barakah-failing \
  --pretty
```

Run the restaurant / food-premise demo dossier:

```bash
python3 manage.py halal precheck run \
  --file examples/seri-melaka-restaurant.dossier.json \
  --ocr-dir examples/ocr/seri-melaka \
  --out-dir reports/seri-melaka \
  --pretty
```

Run a workflow automatically until completion or blocked state:

```bash
python3 manage.py action workflows.run --json '{
  "action": "invoices.submit",
  "payload": {
    "invoice_number": "INV-AUTO-1",
    "issue_date": "2026-03-24",
    "supplier_tin": "C1234567801",
    "buyer_tin": "C1234567802",
    "line_items": [
      {"description": "Agentic ops subscription", "quantity": 1, "unit_price": 95.00}
    ],
    "total_amount": 95.00,
    "payment_event": {
      "event_type": "payment_received",
      "payment_status": "succeeded",
      "amount": 95.00,
      "external_reference": "BANKREF-AUTO-1"
    }
  }
}' --pretty
```

Approve a sensitive action:

```bash
python3 manage.py action approvals.approve --json '{
  "approval_id": "<approval-id>",
  "identity": {
    "authority_id": "user-1",
    "authority_type": "human",
    "provider": "manual",
    "verified": true
  }
}' --pretty
```

## HTTP endpoints

Every API action is a POST with a JSON object body:

- `POST /v1/workflows/run`
- `POST /v1/workflows/status`
- `POST /v1/approvals/list`
- `POST /v1/approvals/approve`
- `POST /v1/approvals/reject`
- `POST /v1/entities/resolve`
- `POST /v1/entities/verify-taxpayer`
- `POST /v1/entities/verify-business-registry`
- `POST /v1/invoices/validate`
- `POST /v1/invoices/submit`
- `POST /v1/invoices/status`
- `POST /v1/invoices/cancel`
- `POST /v1/payments/create-request`
- `POST /v1/payments/events/ingest`
- `POST /v1/webhooks/payments/paynet`
- `POST /v1/payments/reconcile`
- `POST /v1/exceptions/list`
- `POST /v1/exceptions/resolve`
- `POST /v1/trade/doc-pack/validate`
- `POST /v1/trade/submission/status`
- `POST /v1/halal/status/lookup`
- `POST /v1/halal/evidence-pack/generate`
- `POST /v1/halal/suppliers/upsert`
- `POST /v1/halal/suppliers/list`
- `POST /v1/halal/bom/graph/generate`
- `POST /v1/halal/renewals/list`
- `POST /v1/halal/workflows/create`
- `POST /v1/halal/workflows/status`
- `POST /v1/halal/checklists/evaluate`
- `POST /v1/halal/audits/create-query`
- `POST /v1/halal/audits/respond-query`
- `POST /v1/halal/documents/share`
- `POST /v1/halal/export-dossier/generate`
- `POST /v1/halal/dashboard/snapshot`
- `POST /v1/halal/pilot/seed-fnb`
- `POST /v1/providers/myinvois/login`
- `POST /v1/providers/myinvois/document-types`
- `POST /v1/providers/myinvois/validate-tin`
- `POST /v1/providers/myinvois/search-tin`
- `POST /v1/providers/myinvois/submit-documents`
- `POST /v1/providers/myinvois/get-submission`
- `POST /v1/providers/myinvois/cancel-document`
- `POST /v1/providers/cidb/states`
- `POST /v1/providers/cidb/labour-wage-rate`
- `POST /v1/providers/cidb/building-material-price`
- `POST /v1/providers/cidb/machinery-rates`

Every response includes:

- `status`
- `next_action`
- `blocking_reason`
- `source_system`
- `resource_id`
- `timestamp`
- `data`

## Data model and state transitions

### Invoices

- `submitted` -> `validated` -> `payment_requested` -> `paid`
- `submitted|validated` -> `canceled`

### Payments

- `pending` -> `matched`
- `pending` -> `mismatch` + exception
- `pending` -> `failed`

### Workflow runs

- `running`
- `completed`
- `blocked`
- `awaiting_external_event`
- `awaiting_human_approval`
- `failed`

### Approvals

- `pending`
- `approved`
- `rejected`

### Trade

- `blocked_missing_documents`
- `ready_for_submission`

### Halal evidence packs

- `blocked_missing_evidence`
- `ready`

### Halal operations

- supplier registry: `active`, `unknown`, `expired`
- BOM graphs: `ready`, `blocked_non_compliant_bom`
- workflows: `active`, `ready_for_submission`
- checklists: `ready`, `blocked_missing_controls`
- audit queries: `open`, `resolved`
- export dossiers: `ready`, `blocked_missing_evidence`

### Halal frontend

- `GET /app/halal-ops`
- `GET /app/project-status`
- `GET /app/halal-attack-plan`

## What is sandboxed

- High-level `invoices.*` can delegate to real MyInvois, but still depends on valid credentials and compliant caller-supplied document payloads.
- DuitNow payment requests are still emitted as sandbox request URIs unless a real payment provider is wired.
- Business registry and halal lookup use seeded Malaysian fixtures to keep the contract stable without claiming live official access.
- Approval identity is local and verified by payload context for now, not by MyDigital ID.

## What is ready for next

The codebase already leaves clean expansion seams for:

- real PayNet auth and settlement adapters
- MyDigital ID-backed session binding
- trade and halal provider integrations
- healthcare DRG and coding APIs as a separate bounded context

## Real-provider commands

The project includes explicit real-provider actions for official MyInvois rails. It also includes CIDB provider actions as an experimental adapter surface, but CIDB is not part of the current core product direction.

Prepare env vars:

```bash
cp /Users/faiqhilman/Projects/malaysia-agent-ops/.env.example /Users/faiqhilman/Projects/malaysia-agent-ops/.env
```

MyInvois sandbox login:

```bash
python3 manage.py action providers.myinvois.login --json '{
  "environment": "sandbox",
  "mode": "taxpayer",
  "client_id": "YOUR_SANDBOX_CLIENT_ID",
  "client_secret": "YOUR_SANDBOX_CLIENT_SECRET"
}' --pretty
```

MyInvois validate TIN:

```bash
python3 manage.py action providers.myinvois.validate_tin --json '{
  "environment": "sandbox",
  "access_token": "YOUR_ACCESS_TOKEN",
  "tin": "C1234567890",
  "id_type": "BRN",
  "id_value": "201901234567"
}' --pretty
```

CIDB states:

```bash
python3 manage.py action providers.cidb.states --json '{
  "access_token": "YOUR_CIDB_ACCESS_TOKEN"
}' --pretty
```

CIDB building material prices:

```bash
python3 manage.py action providers.cidb.building_material_price --json '{
  "access_token": "YOUR_CIDB_ACCESS_TOKEN",
  "state_code": "SGR",
  "year": 2026
}' --pretty
```

## Tests

Current automated status in this workspace: `20/20` passing.

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 -m unittest discover -s tests -v
```
