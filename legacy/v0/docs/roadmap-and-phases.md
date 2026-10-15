# Roadmap And Phases

## Purpose Of This Roadmap

This document is the operating roadmap for the repo as it exists today.

It is not a generic product vision memo. It is meant to answer four practical questions:

1. what is already implemented
2. what is testable today
3. what external dependencies still block live execution
4. what the next phase is for each vertical

The governing principle is unchanged:

- agents should run the workflow
- humans should only inspect dashboards, approve sensitive actions, or rectify blocked cases

If a new feature does not move the platform closer to `run until terminal or blocked`, it is lower priority than execution completeness.

## Platform Baseline

As of `2026-03-24`, the repo has these implemented platform primitives:

- `45` service actions in [service.py](/Users/faiqhilman/Projects/malaysia-agent-ops/src/malaysia_agent_ops/service.py)
- `46` POST API routes plus `GET /health` in [server.py](/Users/faiqhilman/Projects/malaysia-agent-ops/src/malaysia_agent_ops/server.py)
- `3` served HTML app routes:
  - `/app/halal-ops`
  - `/app/project-status`
  - `/app/halal-attack-plan`
- `22/22` automated tests passing in [test_end_to_end.py](/Users/faiqhilman/Projects/malaysia-agent-ops/tests/test_end_to_end.py)
- shared execution surfaces:
  - CLI via [manage.py](/Users/faiqhilman/Projects/malaysia-agent-ops/manage.py)
  - HTTP API via [server.py](/Users/faiqhilman/Projects/malaysia-agent-ops/src/malaysia_agent_ops/server.py)
  - stdio MCP via [mcp_server.py](/Users/faiqhilman/Projects/malaysia-agent-ops/src/malaysia_agent_ops/mcp_server.py)
  - repo-local reusable skill via [SKILL.md](/Users/faiqhilman/Projects/malaysia-agent-ops/skill/SKILL.md)

Cross-vertical capabilities that are already real in the codebase:

- stable JSON response envelope with `status`, `next_action`, `blocking_reason`, `source_system`, `resource_id`, `timestamp`, and `data`
- autonomous runner with persisted workflow state
- approval store with approve/reject loop
- event-driven payment ingestion
- exception creation and resolution
- real-provider adapter seams for MyInvois
- experimental provider adapter seams for CIDB, retained outside the core product direction
- persistent halal artifact graph and operator workbench

Cross-vertical capabilities that still need external rails:

- real MyInvois credentials and compliant document payloads
- PayNet or partner-backed payment rails
- MyDigital ID-backed authority binding
- regulator or partner access for halal write-side integration
- customs / NSW access for live trade execution
- hospital and payer access for healthcare

## Cross-Cutting Execution Layer

This section is not a vertical. It is the shared platform every vertical depends on.

### Current state

Implemented:

- `workflows.run`
- `workflows.status`
- `approvals.list`
- `approvals.approve`
- `approvals.reject`
- `payments.ingest_event`
- stdio MCP server
- repo-local skill packaging

Validated behavior:

- a workflow can auto-progress through multiple actions until it hits a terminal or blocked state
- a workflow can stop with `awaiting_external_event`
- a workflow can stop with `awaiting_human_approval`
- approval decisions can resume sensitive execution logic
- MCP can initialize, list tools, and invoke tools

### Remaining dependencies

Internal dependencies:

- stronger observability around long-running runs
- resumable run continuation helpers for blocked runs
- better operator UI for approvals and workflow runs

External dependencies:

- MyDigital ID if approval identity must be cryptographically bound
- real event sources if blocked states must resolve automatically from partner callbacks

### Platform phases

| Phase | Status | Scope | Dependencies | Tests to run |
|---|---|---|---|---|
| P0 contract + persistence | Complete | Stable action envelope, SQLite state, CLI and HTTP parity | None beyond local Python runtime | `python3 -m unittest discover -s tests -v` |
| P1 autonomous runner | Complete | `workflows.run`, state history, explicit blocked states | None | `test_workflow_runner_completes_local_invoice_flow_when_payment_event_is_present`, `test_workflow_runner_waits_for_external_payment_event_when_not_supplied` |
| P2 approval layer | Complete for local identity | approval records, approve/reject actions, policy gating | local payload-based identity only | `test_approval_gate_blocks_then_allows_real_invoice_submission` |
| P3 MCP + skill surfaces | Complete for local use | stdio MCP and repo-local skill bundle | none | `test_mcp_server_initializes_and_calls_tool`, YAML parse for `skill/agents/openai.yaml` |
| P4 operator-grade runtime | Next | dashboards for approvals and blocked runs, resume controls, audit views | product/UI effort | manual browser tests on `/app/project-status` and future approvals UI |
| P5 authority-grade runtime | Planned | MyDigital ID binding, stronger policy model, signed approvals | MyDigital ID access | end-to-end approval with verified identity |

### Platform tests to run now

Automated:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 -m unittest discover -s tests -v
```

Manual autonomous run:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action workflows.run --json '{
  "action":"invoices.submit",
  "payload":{
    "invoice_number":"INV-ROADMAP-1",
    "issue_date":"2026-03-24",
    "supplier_tin":"C1234567801",
    "buyer_tin":"C1234567802",
    "line_items":[{"description":"Roadmap test","quantity":1,"unit_price":120.00}],
    "total_amount":120.00
  }
}' --pretty
```

Expected result today:

- the run should auto-progress through invoice submission and payment request creation
- it should stop cleanly with `next_action=payments.ingest_event`
- `blocking_reason` should be `missing_external_input_for_next_action`

## Vertical 1: Tax, Invoicing, And MyInvois

### Goal

Make `invoices.*` the real execution surface for e-invoicing so agents do not need to drop down to provider-specific commands except for smoke tests and debugging.

### Current state

Implemented:

- `entities.resolve`
- `entities.verify_taxpayer`
- `entities.verify_business_registry`
- `invoices.validate`
- `invoices.submit`
- `invoices.status`
- `invoices.cancel`
- low-level MyInvois provider actions:
  - `providers.myinvois.login`
  - `providers.myinvois.document_types`
  - `providers.myinvois.validate_tin`
  - `providers.myinvois.search_tin`
  - `providers.myinvois.submit_documents`
  - `providers.myinvois.get_submission`
  - `providers.myinvois.cancel_document`

What is real already:

- the provider adapter targets official MyInvois endpoints
- the high-level invoice flow can delegate to the real provider path
- real execution is approval-gated

What is still sandboxed:

- default invoice runs still use the local sandbox unless the real-provider path is configured
- the sample invoice payloads in the README are business-valid for the app, not guaranteed fully compliant UBL payloads for MyInvois

### External dependencies

Mandatory:

- MyInvois sandbox or production `client_id`
- MyInvois sandbox or production `client_secret`
- correct auth mode and environment selection
- compliant document payload content

Operational:

- taxpayer or intermediary portal setup
- approval policy for live submissions and cancellations

### Phases

| Phase | Status | Scope | External dependencies | Tests to run |
|---|---|---|---|---|
| P0 local invoice lifecycle | Complete | validate, submit, status, cancel in sandbox state machine | none | `test_phase1_end_to_end_flow` |
| P1 low-level MyInvois adapter | Complete | login, TIN validation, document submit/poll/cancel request shaping | none for mocked tests | `test_provider_myinvois_login_with_mocked_remote`, `test_myinvois_submit_documents_uses_official_path` |
| P2 high-level delegation through `invoices.*` | Partial | `invoices.submit/status/cancel` can route to provider-backed execution | credentials and compliant payloads | `test_approval_gate_blocks_then_allows_real_invoice_submission` plus live sandbox smoke tests |
| P3 local execution credibility pack | Complete | `tax run` produces sandbox happy-path and real-provider blocked summaries | none | tax execution CLI/report tests |
| P4 live sandbox workflow | Next | complete one full MyInvois sandbox invoice lifecycle via `invoices.*` | sandbox credentials | manual live tests below |
| P5 production-hardening | Planned | retries, provider-specific error mapping, document-type selection, idempotency | production access | live pilot with design partner |

### Tests to run now

Local high-level workflow:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action invoices.submit --json '{
  "invoice_number":"INV-LOCAL-1",
  "issue_date":"2026-03-24",
  "supplier_tin":"C1234567801",
  "buyer_tin":"C1234567802",
  "line_items":[{"description":"Local invoice test","quantity":1,"unit_price":100.00}],
  "total_amount":100.00
}' --pretty
```

Expected result today:

- `status=success`
- `next_action=invoices.status`
- `source_system=myinvois_sandbox`

Provider auth gating:

```bash
python3 manage.py action providers.myinvois.login --json '{
  "environment":"sandbox",
  "mode":"taxpayer"
}' --pretty
```

Expected result today without credentials:

- `status=blocked`
- `blocking_reason=missing_myinvois_credentials`

Live sandbox tests once credentials exist:

1. login
2. validate TIN
3. submit one compliant document
4. poll submission status
5. cancel the document if business rules allow

Exit criteria for the next phase:

- one MyInvois sandbox invoice is submitted through `invoices.submit`
- one status poll is returned through `invoices.status`
- one cancellation path is exercised through `invoices.cancel`

## Vertical 2: Payments And Reconciliation

### Goal

Replace human-triggered reconciliation with event-driven settlement progression while keeping exceptions first-class.

### Current state

Implemented:

- `payments.create_request`
- `payments.ingest_event`
- `payments.reconcile`
- `exceptions.list`
- `exceptions.resolve`

What is real already:

- event ingestion is the primary modeled progression path
- workflow runs can stop on payment events instead of pretending to be complete
- mismatches create persistent exceptions

What is still sandboxed:

- payment request URLs are sandbox-shaped
- no real PayNet signing, callbacks, or bank integration exists
- `payments.reconcile` remains as manual fallback

### External dependencies

Mandatory for live payment execution:

- PayNet onboarding or partner rail access
- real request creation API or indirect acquirer integration
- callback/webhook configuration
- signature or shared-secret verification rules

Operational:

- merchant identity and settlement account setup
- approval policy for payment amounts above threshold

### Phases

| Phase | Status | Scope | External dependencies | Tests to run |
|---|---|---|---|---|
| P0 local request + reconcile flow | Complete | request creation, manual reconcile fallback, mismatch exceptions | none | `test_payment_mismatch_creates_exception` |
| P1 event-driven local flow | Complete | `payments.ingest_event`, request lookup, invoice settlement update | none | `test_payment_event_ingestion_sets_invoice_paid`, workflow runner tests |
| P2 webhook route | Complete for local mapping | `/v1/payments/events/ingest` and `/v1/webhooks/payments/paynet` mapped into service action | none | route map test and manual curl |
| P3 real PayNet integration | Planned | signed callbacks, provider request creation, settlement status mapping | PayNet access | live callback replay tests |
| P4 production reconciliation | Planned | duplicate event handling, reconciliation reporting, dispute workflow | provider access and pilot data | live pilot runbook |

### Tests to run now

Create request:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action payments.create_request --json '{"submission_id":"<submission-id>"}' --pretty
```

Expected result today:

- `status=success`
- `next_action=payments.ingest_event`
- `data.event_ingest_endpoint=/v1/payments/events/ingest`

Ingest success event:

```bash
python3 manage.py action payments.ingest_event --json '{
  "request_id":"<request-id>",
  "event_type":"payment_received",
  "payment_status":"succeeded",
  "amount":120.00,
  "external_reference":"BANKREF-100"
}' --pretty
```

Expected result today:

- payment request moves to matched state
- invoice submission moves to `paid`
- no exception created

Mismatch test:

```bash
python3 manage.py action payments.reconcile --json '{
  "request_id":"<request-id>",
  "received_amount":119.00,
  "external_reference":"BANKREF-MISMATCH"
}' --pretty
```

Expected result today:

- payment request moves to `mismatch`
- persistent exception is created

Exit criteria for the next phase:

- one real callback can be replayed through the webhook route
- one live provider event settles an invoice without manual reconcile

## Archived Adapter Track: Construction And CIDB N3C

### Goal

Keep the CIDB provider adapter available for technical experiments, but do not treat it as a product pillar while the project is focused on halal dossier operations and MyInvois tax workflows.

### Current state

Implemented:

- `providers.cidb.states`
- `providers.cidb.labour_wage_rate`
- `providers.cidb.building_material_price`
- `providers.cidb.machinery_rates`

What is real already:

- request shapes target official CIDB paths
- bearer-token gating is explicit
- current tests verify path shapes and mocked remote behavior

What is missing:

- no high-level business workflow currently sits on top of CIDB
- no caching or procurement decision layer exists yet

### External dependencies

Mandatory:

- CIDB bearer token or account access

Optional but useful:

- one design partner use case, such as procurement quoting or cost estimation

### Phases

| Phase | Status | Scope | External dependencies | Tests to run |
|---|---|---|---|---|
| P0 request-shape integration | Complete | official path mapping and auth envelope | none | `test_cidb_states_uses_official_path` |
| P1 mocked remote behavior | Complete | provider actions behave correctly with stubbed remote responses | none | `test_provider_cidb_dataset_with_mocked_remote` |
| P2 live read-only execution | Parked | states and at least one pricing endpoint exercised with real token | CIDB token | manual live tests below |
| P3 workflow layer | Out of current scope | quoting, cost benchmarking, or procurement helpers on top of CIDB data | design partner workflow | product-specific tests |

### Tests to run now

Token gating:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action providers.cidb.states --json '{}' --pretty
```

Expected result today without token:

- `status=blocked`
- `blocking_reason=missing_cidb_access_token`

Live tests once token exists:

```bash
python3 manage.py action providers.cidb.states --json '{"access_token":"YOUR_CIDB_ACCESS_TOKEN"}' --pretty
python3 manage.py action providers.cidb.building_material_price --json '{"access_token":"YOUR_CIDB_ACCESS_TOKEN","state_code":"SGR","year":2026}' --pretty
python3 manage.py action providers.cidb.labour_wage_rate --json '{"access_token":"YOUR_CIDB_ACCESS_TOKEN","state_code":"SGR","year":2026}' --pretty
```

Exit criteria for the next phase:

- one real CIDB state lookup succeeds
- one real pricing lookup succeeds
- the response is stable enough to anchor a procurement-oriented workflow

## Vertical 4: Halal Compliance Operations

### Goal

Build the operational layer that brands, OEMs, consultants, and exporters can use before direct regulator-side integration exists.

### Current state

Implemented:

- `halal.status.lookup`
- `halal.evidence_pack.generate`
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
- browser workbench at `/app/halal-ops`

What is real already:

- persistent supplier registry
- BOM dependency graph with blocked/ready states
- checklist scoring and missing-controls detection
- workflow records for internal halal ops
- audit query-response workspace
- export dossier generation
- seeded F&B pilot data

What is still sandboxed:

- official halal lookup is fixture-backed
- there is no public write-side regulator integration in the app
- `MYeHALAL` and `MyHALALINGREDIENTS` remain external relationship dependencies

### Current local demo state

Latest workspace snapshot from `halal.dashboard.snapshot`:

- `5` supplier registry entries
- `2` renewal-watch items
- `4` workflows ready for submission
- `4` evidence packs
- `4` export dossiers
- `4` resolved audit queries
- `5` BOM graphs

### External dependencies

Commercial:

- 3 to 5 design partners in F&B, cosmetics, OEM manufacturing, logistics, or consulting
- one strong halal domain expert

Regulatory or ecosystem:

- JAKIM conversation
- relevant `MAIN/JAIN` conversation
- HDC channel or advisory relationship
- sanctioned process or access model for regulator-side submissions if that becomes part of scope

### Phases

| Phase | Status | Scope | External dependencies | Tests to run |
|---|---|---|---|---|
| P0 local compliance operating model | Complete | registry, graph, evidence, checklist, workflow, audit, sharing, dossier | none | halal automated tests and seeded pilot |
| P1 operator workbench | Complete for local use | interactive HTML workbench consuming local API | local server only | manual browser walkthrough |
| P2 pilot data + productization | Partial | seeded F&B pilot proves the artifact model | design partner data still needed | `halal.pilot.seed_fnb`, `halal.dashboard.snapshot` |
| P3 design-partner validation | Next | map real document taxonomies, renewal cadences, audit loops | design partners and domain expert | pilot-specific acceptance tests |
| P4 regulator-adjacent integration | Planned | sanctioned lookup or submission helpers around official systems | JAKIM / MAIN / HDC clarity | workflow tests with real partner data |
| P5 direct regulator-side execution | Later | write-side submission or sanctioned upload flows | official access | end-to-end regulator-connected pilot |

### Tests to run now

Seed the pilot:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action halal.pilot.seed_fnb --json '{}' --pretty
```

Inspect the dashboard:

```bash
python3 manage.py action halal.dashboard.snapshot --json '{}' --pretty
```

Expected result today:

- seeded applicant profile is present
- suppliers, renewals, workflows, evidence packs, audits, and dossiers are all returned

Generate a BOM graph:

```bash
python3 manage.py action halal.bom.graph.generate --json '{
  "applicant_name":"Barakah Foods Manufacturing Sdn Bhd",
  "product_name":"Instant curry paste",
  "bom":[
    {"ingredient":"Spice blend","supplier_tin":"C1234567810"},
    {"ingredient":"Coconut milk powder","supplier_tin":"C1234567811"},
    {"ingredient":"Retort pouch packaging","supplier_tin":"C1234567801"}
  ]
}' --pretty
```

Workbench test:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py serve --host 127.0.0.1 --port 8092
```

Then open:

- `http://127.0.0.1:8092/app/halal-ops`
- `http://127.0.0.1:8092/app/project-status`
- `http://127.0.0.1:8092/app/halal-attack-plan`

Expected result today:

- dashboard metrics load from the local API
- workflows and artifacts render
- the BOM dependency graph renders as an actual graph, not just a table

Automated tests covering halal today:

- `test_halal_ops_layer_supports_registry_graph_workflow_and_dossier`
- `test_halal_bom_and_registry_block_on_non_active_supplier`
- `test_halal_pilot_seed_and_dashboard_snapshot`
- `test_trade_and_halal_surfaces`

Exit criteria for the next phase:

- one real design partner dataset is modeled
- one pilot produces measurable time savings in evidence assembly or renewal tracking

## Vertical 5: Trade And Logistics

### Goal

Turn document validation into an agent-usable customs and permit execution layer, but only after the execution platform and the core finance rails are stable enough.

### Current state

Implemented:

- `trade.doc_pack.validate`
- `trade.submission.status`

What is real already:

- deterministic validation of trade document packs
- clear missing-document signaling

What is missing:

- no customs submission adapter
- no NSW or DagangNet integration
- no HS-code inference or permit routing logic

### External dependencies

Mandatory for real execution:

- DagangNet / National Single Window access or alternative customs gateway access
- permit / OGA process mapping
- trade operator design partner

### Phases

| Phase | Status | Scope | External dependencies | Tests to run |
|---|---|---|---|---|
| P0 document readiness | Complete | pack validation and status contract | none | `test_trade_and_halal_surfaces` |
| P1 document intelligence | Planned | better field-level validation, HS-code and permit readiness helpers | trade domain input | validation fixtures |
| P2 gateway integration | Planned | live customs or gateway adapter | NSW / DagangNet access | live submission smoke tests |
| P3 operational workflow | Later | end-to-end import/export orchestration | design partner workflow | production pilot tests |

### Tests to run now

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 manage.py action trade.doc_pack.validate --json '{
  "doc_type":"import_k1",
  "documents":{
    "commercial_invoice":true,
    "packing_list":true
  }
}' --pretty
```

Expected result today:

- missing required items are identified
- workflow status reflects readiness versus blocked state

Exit criteria for the next phase:

- one design partner trade dataset is encoded into fixtures
- one gateway or customs access path is identified and documented

## Vertical 6: Healthcare Revenue Cycle / DRG

### Goal

Eventually build a Malaysia-specific clinical revenue-cycle execution layer for discharge extraction, ICD mapping, and DRG grouping, but only once the current business ops platform is stronger on live external rails.

### Current state

Implemented:

- no dedicated healthcare module

What exists today:

- only the architectural thesis and market rationale

### External dependencies

Mandatory:

- hospital or clinic partner access
- privacy and compliance design
- payer or reimbursement workflow access
- Malaysian DRG / grouper domain knowledge

### Phases

| Phase | Status | Scope | External dependencies | Tests to run |
|---|---|---|---|---|
| P0 strategy only | Current | market thesis only | none | none |
| P1 data model + fixtures | Planned | discharge summary fixtures, ICD mapping contracts, clinical exception model | domain expert | unit tests against synthetic data |
| P2 extraction + coding engine | Later | multilingual extraction, ICD mapping, grouper interface | partner data | accuracy and regression tests |
| P3 payer workflow integration | Later | claim packaging and submission orchestration | hospital and payer access | live pilot tests |

### Tests to run now

- none beyond architectural review

Exit criteria for the first coding phase:

- one partner and one concrete reimbursement workflow are committed

## Immediate Build Order From Here

This is the recommended order for the next implementation cycle:

1. complete one real MyInvois sandbox flow through the high-level `invoices.*` path
2. replace sandbox payment completion with a real provider-backed event source
3. add operator-facing approvals and run-inspection UI
4. deepen halal precheck from demo dossiers to real discovered workflows once interviews exist
5. add local GLM-OCR extraction as an optional metadata verification input
6. only then deepen trade gateway work, revisit CIDB, or start healthcare coding

## Anti-Roadmap

Do not spend the next phase on:

- adding new mock verticals before the current live rails are exercised
- building more static dashboards without improving execution completeness
- calling the app fully autonomous before MyInvois and payments are live enough to prove it
- treating MCP or the skill as the product; they are distribution surfaces for the execution layer

## Definition Of Success

The platform has reached its intended shape when this is true:

- an agent starts a real business workflow through the high-level contract
- the runner progresses until completion or a clean blocked state
- approvals are the only human intervention for sensitive steps
- provider events, not manual callbacks, drive settlement or remote completion
- the final dashboard is for inspection and exception handling, not routine operation
