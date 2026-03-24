# Roadmap And Phases

## Objective Reset

The target product is not "a collection of Malaysia-specific APIs."

The target product is:

- an execution layer that agents can use directly
- a policy layer that decides what can run automatically
- an approval layer for actions that require human authority
- a final dashboard for inspection, exception handling, and approvals

That means the roadmap must optimize for:

1. autonomous execution
2. explicit blocked states
3. provider-backed rails
4. approval and identity controls
5. agent-native interfaces like MCP

The core rule from this point forward is:

`no new vertical should be added unless the existing verticals can run end-to-end until blocked`

## Current State

What already exists:

- stable JSON action contract
- CLI and HTTP API parity
- SQLite persistence
- exception store
- sandbox invoice and payment flows
- real MyInvois provider adapter
- real CIDB provider adapter
- substantive halal operations module and dashboard

What is still missing relative to the actual objective:

- autonomous workflow runner
- provider-backed execution inside the high-level `invoices.*` flow
- event-driven payment ingestion
- approval and delegated authority gating
- MCP server exposure
- real MyDigital ID integration
- real PayNet settlement loop

## Phase 0: Contract And Local Workflow Core

Status:

- complete

Delivered:

- action contract with `status`, `next_action`, `blocking_reason`, `source_system`, `resource_id`
- durable local persistence
- local HTTP API
- local CLI
- sandbox business-state transitions for invoices, payments, trade, and halal

Success criteria:

- deterministic tests for local workflows
- one envelope shape across every action

## Phase 1: Autonomous Runner And State Machine

Status:

- in progress

Goal:

- make the platform execute actions automatically until terminal or blocked

Why this phase is first:

- without this, the product is still a toolkit rather than an agentic operations layer
- it is the difference between "agent-ready" and "agent-operating"

Deliverables:

- workflow runner that accepts an initial action and payload
- automatic chaining via `next_action`
- loop protection and max-step protection
- persisted workflow run history
- explicit terminal states:
  - `completed`
  - `blocked`
  - `awaiting_external_event`
  - `awaiting_human_approval`
  - `failed`

Success criteria:

- one invoice workflow can run from submission through payment request creation without human sequencing
- one halal workflow can run until audit or approval gates
- final run record can be inspected after execution

## Phase 2: Provider-Backed Invoice Execution

Status:

- in progress

Goal:

- move the high-level `invoices.*` actions off purely local transitions and onto the real MyInvois rail when credentials are present

Design rule:

- `providers.myinvois.*` remains the low-level rail
- `invoices.*` becomes the high-level business workflow that delegates to the provider when configured

Deliverables:

- `invoices.submit` can use MyInvois directly
- `invoices.status` can poll MyInvois submission state directly
- `invoices.cancel` can call real MyInvois cancellation directly
- sandbox fallback remains available for local and test workflows

Success criteria:

- one invoice can be submitted to MyInvois sandbox through `invoices.submit`
- one invoice status can be refreshed through `invoices.status`
- one cancellation can be issued through `invoices.cancel`

Known constraints:

- sandbox or production credentials are still required
- real UBL payload generation still depends on caller-supplied compliant document content

## Phase 3: Event-Driven Payments

Status:

- in progress

Goal:

- remove manual reconciliation as the primary payment path

Why this matters:

- autonomous systems should react to provider events, not wait for a human to call a reconcile endpoint

Deliverables:

- payment event ingestion endpoint
- event persistence and audit trail
- request lookup by payment reference
- automatic invoice status updates on successful settlement events
- mismatch handling that creates exceptions automatically
- manual `payments.reconcile` retained only as an operator fallback

Success criteria:

- a payment request can be completed by an ingested event without human intervention
- mismatches automatically raise exceptions and stop the run

Future completion criteria for this phase:

- real PayNet or partner callbacks
- provider signature verification
- provider-specific event mapping

## Phase 4: Approval, Policy, And Delegated Authority

Status:

- in progress

Goal:

- ensure that only the right actions require a human and that those actions stop cleanly

Principle:

- humans should not operate the workflow
- humans should only approve or rectify actions that policy says cannot run unattended

Deliverables:

- approval request store
- policy evaluation for sensitive actions
- approval and rejection actions
- local verified identity context for approvals
- workflow runner integration so runs stop on approval boundaries

Sensitive actions to gate first:

- real MyInvois submission
- real MyInvois cancellation
- payment request creation above threshold
- any future production-only external execution

Success criteria:

- at least one workflow stops on a generated approval request
- after approval, the same workflow can continue without changing business logic

Future completion criteria for this phase:

- MyDigital ID-backed identity binding
- delegated authority scopes
- stronger policy DSL

## Phase 5: MCP Server Exposure

Status:

- in progress

Goal:

- make the platform directly consumable by agent runtimes through MCP

Why this matters:

- the product thesis is agent-first
- MCP is the cleanest standard interface for agent tool discovery and invocation

Deliverables:

- local stdio MCP server
- comprehensive tool exposure over the current action contract
- structured tool results
- tool descriptions and schemas

Success criteria:

- an MCP client can list tools
- an MCP client can call high-value tools like:
  - `entities.resolve`
  - `invoices.submit`
  - `invoices.status`
  - `payments.create_request`
  - `payments.ingest_event`
  - `approvals.approve`
  - `halal.dashboard.snapshot`

Future completion criteria for this phase:

- resources and prompts if needed
- auth-aware MCP server deployment
- remote transport if multi-tenant serving is required

## Phase 6: Real PayNet And MyDigital ID

Status:

- planned

Goal:

- replace local identity and payment control seams with official rails

Deliverables:

- real PayNet request and callback mapping
- real settlement status retrieval
- MyDigital ID sign-in and authority assertion
- policy binding to verified human or corporate authority

Success criteria:

- one approval-gated workflow where the approval identity is cryptographically or platform-verified
- one payment workflow driven by real provider events

## Phase 7: Vertical Expansion Only After Execution Completeness

Status:

- planned

Rule:

- no new vertical is first-class until Phases 1 through 5 are usable on at least one core rail

Priority order after execution completeness:

1. tax and payment operations
2. halal compliance operations
3. trade and logistics documentation
4. healthcare DRG

## Immediate Build Order

This is the practical implementation order for the current repo:

1. add workflow runner
2. route `invoices.*` through MyInvois when configured
3. add payment event ingestion and webhook handling
4. add approvals and local identity gating
5. expose the contract over MCP
6. only then deepen PayNet, MyDigital ID, and new verticals

## Anti-Roadmap

The project should avoid:

- becoming a generic agent platform disconnected from Malaysian workflows
- shipping more dashboards before the execution layer is autonomous
- adding more mock verticals while core execution is still manual
- treating MCP as a cosmetic wrapper rather than a first-class interface
- claiming full autonomy before approvals, events, and provider rails are actually wired
