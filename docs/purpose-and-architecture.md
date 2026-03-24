# Malaysia Agent Ops -- Vision, Purpose, and Architecture

## Executive Summary

Malaysia Agent Ops is an execution middleware platform purpose-built for AI agents operating within Malaysian business workflows. It provides a standardised, machine-readable interface that connects autonomous software agents to Malaysia's official regulatory, financial, and operational systems -- starting with e-invoicing (MyInvois) and construction market data (CIDB), with a clear expansion path into payments, digital identity, trade logistics, halal compliance, and healthcare.

The platform does not replace ERPs, government portals, or licensed financial institutions. It sits between them and the next generation of AI-powered business software, translating agent intent into compliant, auditable actions on Malaysian rails.

---

## The Problem

### Malaysia's digital infrastructure is growing -- but it was built for humans, not agents

Malaysia has made significant strides in national digitalisation. The MyInvois e-invoicing mandate, DuitNow real-time payments, MyDigital ID, and CIDB's construction data APIs all represent genuine progress. However, every one of these systems was designed around human operators navigating web portals, downloading PDFs, and copying data between screens.

At the same time, businesses across Southeast Asia are rapidly adopting AI agents to automate finance operations, procurement, compliance tracking, and supply chain management. These agents can reason, plan, and execute -- but only if there is a clean programmatic surface to act against.

**Today, that surface does not exist for Malaysia.**

The gap is specific and measurable:

- **E-invoicing**: The MyInvois mandate requires every business to submit structured tax documents electronically. Most accounting platforms are building integrations, but none expose an agent-friendly contract that an AI can invoke autonomously, check status against, and handle exceptions from -- without human intervention at every step.

- **Payments**: DuitNow enables real-time bank transfers and payment requests, but creating and reconciling these programmatically requires navigating bank-specific onboarding, callback infrastructure, and amount-matching logic that no existing middleware abstracts for agent use.

- **Market data**: Construction firms and procurement teams need current pricing for labour, materials, and equipment. CIDB publishes this data, but accessing it requires manual portal navigation or bespoke integrations that are not designed for automated consumption.

- **Compliance**: Halal certification, trade document validation, and business registry verification all involve querying fragmented government systems with inconsistent interfaces. An agent that needs to verify a supplier's halal status or validate a trade document pack has no unified API to call.

### The cost of this gap

Without an execution layer, AI agents in Malaysian business contexts hit a wall. They can draft invoices but cannot submit them. They can recommend payments but cannot initiate them. They can flag compliance risks but cannot verify them against official sources.

This forces businesses into one of two positions:

1. **Manual handoffs** -- Agents prepare work, humans execute it. This eliminates most of the efficiency gains that justify agent adoption in the first place.
2. **Custom integrations** -- Each business builds its own connectors to each government system. This is expensive, fragile, and duplicates effort across the entire market.

Malaysia Agent Ops eliminates this gap by providing a single, stable, agent-optimised execution layer across Malaysia's key operational systems.

---

## The Solution

### A Malaysia-first middleware layer for AI agents

Malaysia Agent Ops is a JSON-first API and command-line interface that exposes Malaysian business operations as simple, composable actions. An AI agent (or any software client) can:

1. **Resolve and verify** Malaysian business entities -- TIN validation, business registry lookups, taxpayer verification.
2. **Submit and manage** e-invoices through MyInvois-compliant workflows -- validation, submission, status polling, cancellation.
3. **Create and progress** payment requests through event-driven settlement shaped for DuitNow and Malaysian banking rails.
4. **Query live market data** from CIDB -- labour wages, building material prices, machinery rates by state and year.
5. **Track and resolve exceptions** -- mismatches, blocked workflows, and compliance issues surface as structured data that agents can act on.

Every action returns a consistent response envelope containing a status, the next recommended action, any blocking reason, and the relevant data payload. This means an agent can chain operations without custom parsing logic per endpoint -- it reads the response, understands whether it can proceed, and knows exactly what to do next.

### What this is not

| Not this | This instead |
|---|---|
| A new ERP system | Middleware that connects agents to existing systems |
| A licensed financial institution | An orchestration layer that interfaces with licensed rails |
| A replacement for MyInvois or DuitNow | A programmatic bridge to those platforms |
| A generic AI framework | A Malaysia-specific execution surface |

---

## Market Opportunity

### Why Malaysia, why now

**Regulatory tailwinds**: Malaysia's e-invoicing mandate is rolling out in phases, requiring all businesses to adopt electronic invoicing. This creates immediate, universal demand for programmatic invoice submission infrastructure.

**Agent adoption acceleration**: AI agent frameworks (LangChain, CrewAI, AutoGen, and proprietary enterprise agents) are moving from experimental to production. These agents need country-specific execution rails to be useful in regulated markets.

**Regional beachhead**: Malaysia's regulatory infrastructure is among the most advanced in ASEAN. A platform proven here has a natural expansion path into Indonesia, Thailand, Vietnam, and the Philippines as those markets digitalise.

**Construction and procurement data**: CIDB's public APIs offer an underserved data access opportunity. Construction firms, procurement platforms, and market intelligence tools need structured, programmatic access to pricing data that currently requires manual lookups.

### Target customers

- **Accounting and finance software vendors** building AI features that need to submit invoices, create payments, ingest settlement events, and reconcile transactions against Malaysian systems.
- **Procurement and construction platforms** that need real-time Malaysian market pricing data for automated quoting, cost estimation, and supplier evaluation.
- **Enterprise AI teams** deploying agents for finance operations, compliance monitoring, and supply chain management in Malaysian subsidiaries.
- **System integrators and consultancies** building automation solutions for Malaysian businesses that need reliable government system connectivity.

---

## Architecture

The platform is built around a deliberate three-layer separation that keeps the system extensible, testable, and ready for new Malaysian rails as they become available.

### Layer 1: Action Contract

The top layer defines a stable set of action names and a uniform request/response format. Actions are named using clear business verbs:

- `invoices.submit`, `invoices.status`, `invoices.cancel`
- `payments.create_request`, `payments.ingest_event`, `payments.reconcile`
- `entities.resolve`, `entities.verify_taxpayer`
- `trade.doc_pack.validate`

Every action accepts a JSON request and returns a JSON response with a consistent structure. This contract is what agents and integrating software depend on -- it does not change when the underlying provider changes.

### Layer 2: Workflow Orchestration

The middle layer manages stateful business logic -- status transitions, validation rules, exception handling, and the coordination between multiple actions. For example, an invoice moves through a defined lifecycle:

```
submitted --> validated --> payment_requested --> paid
```

If a payment reconciliation finds an amount mismatch, the system creates a structured exception that an agent can inspect and resolve. This layer ensures that workflows are durable, auditable, and resumable.

### Layer 3: Provider Adapters

The bottom layer connects to external systems. Each provider adapter handles authentication, payload translation, and the specifics of a particular Malaysian API. The platform currently supports:

- **MyInvois** (LHDN e-invoicing) -- authentication, TIN validation, document submission, status polling, cancellation.
- **CIDB N3C** (construction market data) -- state lookups, labour wage rates, building material prices, machinery/equipment rates.

The adapter layer runs in two modes:

| Mode | Purpose |
|---|---|
| **Sandbox** | Deterministic local simulation for development and testing, no credentials required |
| **Live** | Direct connection to official Malaysian APIs with proper authentication |

This dual-mode design means development and testing move fast, while production deployment connects to real government systems without architectural changes.

### Why this separation matters

This three-layer architecture is the platform's core structural advantage:

- **For customers**: The action contract is stable. Integrations do not break when a provider API changes or a new provider is added.
- **For expansion**: Adding a new Malaysian system (PayNet, MyDigital ID, DagangNet) means adding a new adapter -- not redesigning the product.
- **For trust**: Workflow state is persisted and auditable. Every action, transition, and exception is recorded.

---

## Current State and Traction

### What is built and working

- Full action contract covering entity resolution, invoice lifecycle, payment requests, event ingestion, approvals, exception management, trade validation, and halal operations.
- Autonomous workflow runner that follows `next_action` until completion or a clean blocked state.
- Sandbox environment with deterministic Malaysian business fixtures for end-to-end testing.
- High-level invoice actions that can delegate to real MyInvois flows when credentials and compliant documents are provided.
- Live MyInvois integration -- authentication, TIN validation, document submission, status retrieval, and cancellation against LHDN's official rails.
- Live CIDB N3C integration -- state lookups, labour wages, building material prices, and machinery rates from official APIs.
- CLI, HTTP API, stdio MCP server, and repo-local agent skill exposing the same business contract through different agent entrypoints.
- Halal operator workbench and seeded F&B pilot dataset on top of the same local API contract.

### What is next

| Phase | Focus | Status |
|---|---|---|
| Phase 0 | Contract and sandbox core | Complete |
| Phase 1 | Autonomous runner, approvals, event-driven payments, MCP | Complete |
| Phase 2 | MyInvois high-level execution through `invoices.*` | Partial |
| Phase 3 | CIDB read-only live retrieval | Partial |
| Phase 4 | PayNet and DuitNow real settlement rails | Planned |
| Phase 5 | MyDigital ID and delegated authority | Planned |
| Phase 6 | Trade and logistics live execution (DagangNet / NSW) | Planned |
| Phase 7 | Halal regulator-side integration | Planned |
| Phase 8 | Healthcare revenue cycle (DRG, ICD-10) | Later stage |

### Commercial milestones

- **Milestone A**: 5 design partners -- at least 2 in finance/accounting software, at least 1 in procurement/construction.
- **Milestone B**: Full MyInvois sandbox workflow demonstrated; live CIDB retrieval workflow demonstrated.
- **Milestone C**: First production-connected customer workflow with a measured reduction of at least 50% in manual finance-ops or market-data lookup effort.

---

## Competitive Positioning

Malaysia Agent Ops occupies a distinct position in the market:

- **vs. ERP vendors adding AI features**: ERPs are building AI into their existing products, but their integrations are proprietary and locked to their platform. Malaysia Agent Ops is platform-agnostic middleware that any agent or software can use.
- **vs. generic API aggregators**: General-purpose API platforms do not understand Malaysian regulatory workflows, status transitions, or exception handling patterns. This platform is purpose-built for Malaysia's specific systems.
- **vs. custom in-house integrations**: Every business building its own MyInvois or CIDB connector is duplicating effort. Malaysia Agent Ops centralises that work into a shared, maintained layer.

---

## Technical Principles

- **Zero external dependencies**: The platform runs on Python standard library only, with SQLite for state persistence. This eliminates supply chain risk and simplifies deployment.
- **Agent-first design**: Every output is structured for machine consumption. Status transitions are explicit. Next actions are recommended in every response. No human-oriented dashboards are required to operate the system.
- **Sandbox parity**: Every workflow that runs in production has an equivalent deterministic sandbox path. This makes testing reliable and onboarding fast.
- **Clean expansion seams**: The architecture is designed so that adding PayNet, MyDigital ID, or any future Malaysian API is an adapter addition, not a platform rewrite.

---

## Summary

Malaysia Agent Ops solves a specific, timely problem: Malaysia's government and financial systems are digitalising rapidly, but the programmatic execution layer that AI agents need to operate within those systems does not yet exist.

This platform fills that gap. It provides a stable, machine-readable interface to Malaysian business operations -- starting with e-invoicing and construction market data, expanding into payments, identity, trade, and compliance. The architecture is deliberately layered to keep the action contract stable while adapters connect to new Malaysian rails as they become available.

The commercial opportunity is driven by two converging forces: Malaysia's regulatory mandates creating demand for programmatic access, and the global acceleration of AI agent adoption creating demand for country-specific execution infrastructure. Malaysia Agent Ops sits at the intersection of both.
