# Malaysia Agent Ops Action Map

## Project Root

- `/Users/faiqhilman/Projects/malaysia-agent-ops`

If `myops` is not on `PATH`, use:

```bash
python3 /Users/faiqhilman/Projects/malaysia-agent-ops/manage.py action ...
```

## Primary Interfaces

### 1. Autonomous runner

Use this first when the task should progress until completion or a clean blocked state:

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
    "total_amount": 95.00
  }
}' --pretty
```

Read run status:

```bash
python3 manage.py action workflows.status --json '{"run_id":"<run-id>"}' --pretty
```

### 2. Direct action invocation

Use this for:

- read-only inspection
- debugging a blocked workflow
- operator fallbacks
- approvals
- provider smoke tests

Pattern:

```bash
python3 manage.py action <action-name> --json '<payload>' --pretty
```

### 3. HTTP API

Start:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py serve --host 127.0.0.1 --port 8080
```

Important routes:

- `POST /v1/workflows/run`
- `POST /v1/workflows/status`
- `POST /v1/approvals/list`
- `POST /v1/approvals/approve`
- `POST /v1/approvals/reject`
- `POST /v1/payments/events/ingest`
- `POST /v1/webhooks/payments/paynet`

### 4. MCP server

Start:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py mcp
```

This exposes the same action contract as MCP tools over stdio.

## Core Finance Flow

Recommended order:

1. `entities.resolve`
2. `entities.verify_taxpayer`
3. `invoices.submit`
4. `invoices.status`
5. `payments.create_request`
6. `payments.ingest_event`
7. `exceptions.resolve` only if needed

### Key behavior

- `invoices.submit` uses sandbox flow by default.
- `invoices.submit` can use real MyInvois if `provider=real` or equivalent execution config is present.
- real MyInvois submission is approval-gated.
- `payments.create_request` now expects event-driven progression.
- `payments.reconcile` is manual fallback only.

## Approval Loop

List approvals:

```bash
python3 manage.py action approvals.list --json '{"workflow_status":"pending"}' --pretty
```

Approve:

```bash
python3 manage.py action approvals.approve --json '{
  "approval_id":"<approval-id>",
  "identity":{
    "authority_id":"user-1",
    "authority_type":"human",
    "provider":"manual",
    "verified":true
  }
}' --pretty
```

Reject:

```bash
python3 manage.py action approvals.reject --json '{
  "approval_id":"<approval-id>",
  "identity":{
    "authority_id":"user-1",
    "authority_type":"human",
    "provider":"manual",
    "verified":true
  },
  "note":"Rejecting due to commercial dispute."
}' --pretty
```

## Payment Event Ingestion

Preferred pattern:

```bash
python3 manage.py action payments.ingest_event --json '{
  "request_id":"<request-id>",
  "event_type":"payment_received",
  "payment_status":"succeeded",
  "amount":120.00,
  "external_reference":"BANKREF-001"
}' --pretty
```

Use this when:

- a simulated settlement event arrives
- a webhook payload needs to be replayed
- the workflow runner is waiting for external payment state

## Halal Surfaces

Use these for compliance workflows and dashboard inspection:

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

Useful starting point:

```bash
python3 manage.py action halal.dashboard.snapshot --json '{}' --pretty
```

## Real Provider Smoke Tests

### MyInvois

- `providers.myinvois.login`
- `providers.myinvois.document_types`
- `providers.myinvois.validate_tin`
- `providers.myinvois.search_tin`
- `providers.myinvois.submit_documents`
- `providers.myinvois.get_submission`
- `providers.myinvois.cancel_document`

Use provider-level actions when:

- debugging authentication
- validating credentials
- testing raw provider payloads
- isolating provider behavior from business workflow logic

### CIDB

- `providers.cidb.states`
- `providers.cidb.labour_wage_rate`
- `providers.cidb.building_material_price`
- `providers.cidb.machinery_rates`

## Status Semantics

Treat these as machine signals, not decorative fields:

- `status=success` with `next_action`: continue automatically if safe
- `status=success` with no `next_action`: terminal success
- `status=blocked` with `blocking_reason=awaiting_human_approval`: approval boundary
- `status=blocked` with `blocking_reason=awaiting_remote_processing`: provider still processing
- `status=blocked` with `blocking_reason=missing_external_input_for_next_action`: agent needs an event or extra payload
- `status=blocked` with `blocking_reason=remote_api_error`: provider troubleshooting required

## Operator Principle

The app is designed so that:

- agents execute workflows
- humans inspect dashboards
- humans approve sensitive actions
- humans resolve exceptions or missing evidence only when necessary

Do not default to manual step-by-step operation if the same task can be expressed through `workflows.run`.
