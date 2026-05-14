# Malaysia Agent Ops
## Proposal Brief for LHDN e-Invoicing and the Malaysia Halal Stack

Prepared for:

- investors
- government and ecosystem partners
- JAKIM / MAIN / JAIN / HDC discussions

Prepared as of:

- `March 24, 2026`

## 1. Executive Summary

Malaysia Agent Ops is building the execution layer for AI agents in regulated Malaysian business workflows.

The immediate focus is deliberately narrow:

1. `LHDN e-Invoicing / MyInvois`
2. `Halal compliance operations`

The product is not another accounting system and not another certification consultancy portal.

It is a middleware and workflow layer that allows AI agents to:

- collect and normalize business data
- verify that data against official or trusted sources
- assemble submission-ready payloads and evidence packs
- progress workflows automatically until they are either:
  - completed
  - waiting for an external event
  - blocked by policy
  - awaiting a human approval

The human role is intentionally minimal:

- approve sensitive actions
- resolve missing evidence or non-compliance
- inspect the final dashboard and audit trail

Our thesis is that Malaysia now has two unusually strong and adjacent wedges:

- `e-Invoicing` is already an official API-driven national mandate with immediate demand.
- `Halal` is still operationally manual, document-heavy, and relationship-driven, which creates a large opportunity for workflow infrastructure even before direct regulator-side API access exists.

## 2. Why These Two Wedges

### 2.1 LHDN e-Invoicing is the fastest official rail

As of `March 24, 2026`, LHDN’s official timeline shows:

- taxpayers with annual turnover above `RM100 million`: `1 August 2024`
- above `RM25 million` and up to `RM100 million`: `1 January 2025`
- above `RM5 million` and up to `RM25 million`: `1 July 2025`
- up to `RM5 million`: `1 January 2026`
- less than `RM1,000,000`: exempt, based on the `7 December 2025` timeline update

This creates a live software infrastructure need across:

- ERPs
- POS vendors
- accountants
- finance operations teams
- marketplaces
- procurement and AP/AR systems

Unlike many Malaysian workflows, MyInvois already exposes an official SDK and documented API surface.

### 2.2 Halal is the strongest document-heavy operations wedge

JAKIM has already continued digitizing the certification stack:

- `SPHM e-Cert` began on `5 May 2025`
- `MyHALALINGREDIENTS` took effect on `15 August 2025`
- JAKIM states that `MyHALALINGREDIENTS` integrates with `MYeHALAL` to reduce repeated document handling and speed certification workflows

This matters because the biggest pain in halal today is not just the final portal submission.

The real pain is everything before submission:

- supplier and ingredient verification
- BOM traceability
- evidence assembly
- MHMS / HAS readiness
- renewal discipline
- audit query response
- OEM / client document sharing
- export dossier packaging

That is exactly the kind of workflow an agent can run well.

## 3. The Product We Are Building

### 3.1 Product definition

Malaysia Agent Ops is:

- a `JSON-first` execution layer
- exposed through `CLI`, `HTTP API`, `MCP`, and a reusable agent skill
- designed so agents execute the workflow and humans only intervene when necessary

### 3.2 What the system does

At a high level, the system gives an agent the ability to:

- call a stable action contract
- receive machine-readable state after every step
- follow `next_action` until terminal or blocked
- stop cleanly at approvals, missing evidence, or external-event boundaries

### 3.3 What it is not

This proposal is not:

- a licensed financial institution
- a replacement for LHDN or JAKIM systems
- a claim that public write-side halal APIs are already available
- a browser-automation-only product

The execution layer should use official APIs where they exist, and only use portal automation as a gap filler where no sanctioned machine interface exists.

## 4. Current Product State in the Repo

The current application already implements the core operating pattern.

### 4.1 Shared execution layer

Implemented now:

- autonomous workflow runner
- approval store and approval actions
- payment event ingestion
- exception handling
- CLI and HTTP API parity
- stdio MCP server
- repo-local reusable skill for other agents

### 4.2 LHDN / MyInvois track

Implemented now:

- `entities.resolve`
- `entities.verify_taxpayer`
- `entities.verify_business_registry`
- `invoices.validate`
- `invoices.submit`
- `invoices.status`
- `invoices.cancel`
- low-level MyInvois provider actions for:
  - login
  - document types
  - TIN validation
  - TIN search
  - document submission
  - submission polling
  - cancellation

Important nuance:

- the high-level `invoices.*` flow can delegate to the real MyInvois path
- live execution still depends on valid credentials and compliant document payloads

### 4.3 Halal track

Implemented now:

- supplier registry
- BOM dependency graph
- evidence pack generation
- renewal watchlist
- MHMS-style workflow tracking
- HAS / IHCS checklist scoring
- audit query / response workspace
- OEM / client document sharing
- export dossier generation
- seeded F&B pilot
- browser-based halal operator workbench
- source-grounded halal precheck CLI
- JSON requirement rules mapped to official source classes
- demo dossiers for:
  - passing food manufacturer precheck
  - failing food manufacturer remediation
  - restaurant / food-premise precheck
- JSON, Markdown, and HTML precheck reports for applicant and reviewer views
- optional GLM-OCR-shaped verification input for declared document metadata

Important nuance:

- this is already a strong operational product layer
- the precheck layer is designed for internal readiness before official submission
- it is not yet a direct sanctioned `MYeHALAL` submission connector

## 5. The LHDN e-Invoicing Stack

### 5.1 What we are solving

We are building the agent execution layer on top of the official MyInvois rail so that an AI agent can:

1. resolve and verify a taxpayer
2. validate invoice data
3. submit to MyInvois
4. poll submission status
5. create the downstream payment request
6. wait for settlement events
7. escalate only when blocked or policy-gated

### 5.2 Why customers will buy this

The pain is immediate and measurable:

- invoice data must be structured correctly
- errors create delays and rework
- buyers can reject documents
- finance teams still need to monitor status and exceptions
- ERP and POS vendors need a machine-friendly compliance layer quickly

The commercial wedge is therefore:

- not “we are another invoicing UI”
- but “we are the agent execution layer for Malaysia e-Invoicing”

### 5.3 Verified official rail

The official MyInvois SDK publicly documents:

- login
- document types
- TIN validation
- submission
- polling
- cancellation

It also explicitly recommends a submit-and-poll integration pattern and publishes API rate guidance.

### 5.4 Current dependencies

To make this production-real, we need:

- taxpayer or intermediary onboarding
- `client_id` and `client_secret`
- compliant signed document payloads
- approval policy for sensitive operations
- eventual production credentials and operational runbooks

### 5.5 What we would ask from LHDN / ecosystem stakeholders

In an LHDN or implementation-partner meeting, the ask is not “let us replace MyInvois.”

The ask is:

- confirm best-practice intermediary patterns for agent-driven execution
- validate healthy polling and idempotency patterns
- clarify what approval and audit evidence is most useful for production-grade integrations
- support sandbox testing for high-level `invoices.*` flows rather than only raw provider calls

## 6. The Halal Stack

### 6.1 What we are solving

The halal opportunity is not just certification submission.

The practical opportunity is `halal compliance operations`.

That means helping companies and their agents manage:

- ingredients
- suppliers
- supporting documents
- process evidence
- compliance controls
- audit responses
- renewal cycles
- export readiness

### 6.2 The product wedge

The fastest and most credible wedge is:

`submission-ready halal compliance package with human approval checkpoints`

That includes:

- supplier certificate registry
- ingredient and BOM verification
- MyHALALINGREDIENTS-ready evidence preparation
- MHMS workflow orchestration
- HAS / IHCS checklisting
- audit workspace
- shareable dossier generation

### 6.3 What is officially verified

From official JAKIM materials, we can verify that:

- approved SPHM certificates moved to electronic issuance through `MYeHALAL` from `5 May 2025`
- `MyHALALINGREDIENTS` became effective on `15 August 2025`
- JAKIM explicitly says `MyHALALINGREDIENTS` integrates with `MYeHALAL`
- JAKIM’s Halal Management Division remains the primary authority managing certification together with state Islamic departments

### 6.4 What is not yet publicly verified as an API rail

As of `March 24, 2026`, we have not identified public official developer documentation comparable to MyInvois for:

- write-side `MYeHALAL` integration
- public query API documentation for `MyHALALINGREDIENTS`

This means the halal stack must be positioned honestly:

- `v1` is the workflow and evidence layer
- `v2` is the sanctioned connector layer, once process or technical access is confirmed

### 6.5 Why this is still investable now

The absence of public write-side API docs does not kill the product.

It sharpens the wedge.

A large amount of halal value sits before submission:

- reducing evidence churn
- enforcing supplier discipline
- reducing missing-document loops
- preparing auditors and internal halal committees faster
- packaging export-ready documentation

This is valuable even before direct regulator connectivity.

### 6.6 What we would ask from JAKIM / MAIN / JAIN / HDC

Our asks should be practical and low-friction:

1. confirm the operational boundaries of what third-party software may assist with
2. validate the evidence taxonomy and workflow stages we are modeling
3. clarify whether sanctioned machine interfaces, import templates, batch uploads, or partner pathways exist or are planned
4. identify the most common causes of avoidable delays and queries
5. support a pilot where the system prepares submission-ready packages before any direct write-side integration is attempted

The key point in these meetings:

- we are not asking to become the certifier
- we are asking to become the workflow infrastructure that makes applicants and the certification ecosystem more efficient

## 7. Dependencies

## 7.1 Technical dependencies

### LHDN / e-Invoicing

- MyInvois credentials
- signed compliant document generation
- approval and policy logic
- payment settlement event source

### Halal

- accepted evidence taxonomy
- partner data models from real manufacturers or OEMs
- sanctioned process guidance for MYeHALAL / MyHALALINGREDIENTS interaction

## 7.2 Commercial dependencies

We need:

- design partners in accounting / ERP / finance ops for the e-Invoice side
- design partners in F&B, cosmetics, OEM manufacturing, logistics, or consulting for the halal side

## 7.3 Institutional dependencies

For the halal stack in particular, the most important meetings are:

- JAKIM Halal Management Division
- relevant `MAIN / JAIN`
- HDC

For the e-Invoice stack:

- LHDN implementation or ecosystem counterparts
- software vendors or accounting operators who are already integrating MyInvois

## 8. Roadmap

## 8.1 Track A: LHDN e-Invoicing

### Phase A0: local execution layer

Status:

- complete

Outcome:

- local workflow runner
- invoice lifecycle
- approvals and blocked states

### Phase A1: official MyInvois adapter

Status:

- complete at provider level
- partial at live high-level execution level

Outcome:

- low-level official calls exist
- high-level `invoices.*` path can delegate to provider-backed execution

### Phase A2: live MyInvois sandbox flow

Status:

- next priority

Required dependencies:

- sandbox credentials
- compliant test payloads

Outcome:

- one full sandbox submission through the high-level business contract

### Phase A3: production-grade finance operations layer

Required dependencies:

- production access
- partner deployment
- real payment event source

Outcome:

- invoice operations, exception handling, and payment progression in one real customer workflow

## 8.2 Track B: Halal Compliance Operations

### Phase B0: workflow and evidence operating system

Status:

- complete for local use

Outcome:

- supplier, ingredient, evidence, workflow, audit, and dossier model exists
- source-grounded halal precheck rules and reports exist for local demo use
- manufacturer and food-premise demo dossiers prove both pass and remediation paths

### Phase B0.5: precheck credibility package

Status:

- complete for local use

Outcome:

- `halal precheck run` validates a structured dossier JSON file
- requirement outputs preserve source IDs, source URLs, and evidence classes
- applicant reports show what to fix before submission
- reviewer reports show dossier inventory, requirement coverage, metadata checks, and OCR verification results
- failing demos catch missing process flow evidence, missing financial statement evidence, expired certificate metadata, and OCR-declared metadata mismatch

### Phase B1: design-partner pilot

Status:

- next priority

Required dependencies:

- one or more real partner datasets
- halal domain expert validation

Outcome:

- replace synthetic demo assumptions with real operational evidence
- classify every new workflow rule as official-source-backed, interview-derived, or product assumption

### Phase B2: sanctioned regulator-adjacent integration

Required dependencies:

- JAKIM / state / HDC guidance
- clarification on permitted software interaction patterns

Outcome:

- approved or accepted system behavior around preparation, upload, or structured submission support

### Phase B3: direct connector layer

Required dependencies:

- actual sanctioned technical or procedural access

Outcome:

- machine-assisted `MYeHALAL` / `MyHALALINGREDIENTS` execution where allowed

## 9. Meeting-Specific Positioning

## 9.1 For investors

The pitch is:

- e-Invoicing gives us the fastest official API wedge and near-term revenue path
- halal gives us the largest document-heavy moat and strategic differentiation
- both tracks share the same execution-layer architecture
- this creates a Malaysia-first infrastructure company, not two unrelated products

## 9.2 For government or ecosystem partners

The positioning is:

- we are not trying to bypass national systems
- we make national systems easier for compliant businesses and software vendors to use
- we reduce avoidable data-entry errors, evidence churn, and workflow delays
- we provide a machine-readable execution layer that can improve digital adoption without displacing regulators

## 9.3 For JAKIM / halal stakeholders

The positioning is:

- we are building the workflow layer first
- we want to reduce avoidable friction for applicants and auditors
- we are not claiming the role of halal authority
- we want alignment on what is permissible, useful, and operationally realistic

## 10. Pilot Proposal

## 10.1 e-Invoice pilot

Candidate pilot users:

- accounting software vendor
- ERP reseller
- outsourced finance team

Pilot workflow:

- resolve entity
- verify taxpayer
- submit invoice
- poll status
- create payment request
- ingest settlement event
- raise or resolve exception if needed

Pilot KPI:

- reduce manual finance-ops steps and exception resolution time

## 10.2 Halal pilot

Candidate pilot users:

- F&B manufacturer
- cosmetics brand
- OEM / co-manufacturer
- halal consultant

Pilot workflow:

- ingest BOM
- verify suppliers and ingredient status
- generate evidence pack
- evaluate controls
- create workflow record
- handle audit query
- generate export dossier
- stop for final human sign-off

Pilot KPI:

- reduce submission-preparation cycle time
- reduce missing-evidence loops
- improve supplier renewal discipline

## 11. Risks And Mitigations

### Risk 1: Overclaiming official halal integration

Mitigation:

- explicitly separate verified public rails from relationship-gated rails
- position the current halal product as workflow infrastructure first

### Risk 2: Being seen as another internal tool

Mitigation:

- emphasize the agent-execution layer, not a manual ops UI
- show that the same contract works via CLI, API, MCP, and agent skill

### Risk 3: Fragmented adoption

Mitigation:

- use e-Invoicing as the immediate revenue rail
- use halal as the differentiation and moat layer

### Risk 4: Human bottlenecks remain too large

Mitigation:

- reserve humans only for approvals, exception handling, and missing evidence
- keep all normal execution automated

## 12. What We Need Next

### For the e-Invoice track

- MyInvois sandbox credentials
- one real partner workflow
- one live high-level sandbox execution

### For the halal track

- one halal domain expert
- one or more real partner datasets
- direct discussions with JAKIM / MAIN / JAIN / HDC on what is allowed and useful

### For the company

- capital to support:
  - integrations
  - compliance-oriented product development
  - design partner onboarding
  - vertical GTM in finance ops and halal industry operations

## 13. Closing Position

Malaysia Agent Ops is not trying to digitize all of Malaysia at once.

We are starting where the infrastructure is strongest and the pain is clearest:

- `LHDN e-Invoicing` for immediate official API-driven execution
- `Halal compliance operations` for workflow depth, strategic relationships, and long-term moat

The result is a Malaysia-first execution layer for AI agents:

- official where official rails already exist
- workflow-first where public machine interfaces are not yet open
- human-approved where policy or authority requires it

That is a credible path to near-term utility, institutional relevance, and long-term defensibility.

## 14. Official Reference Links

- LHDN e-Invoice implementation timeline: [hasil.gov.my](https://www.hasil.gov.my/en/e-invoice/implementation-of-e-invoicing-in-malaysia/e-invoice-implementation-timeline/)
- MyInvois SDK home: [sdk.myinvois.hasil.gov.my](https://sdk.myinvois.hasil.gov.my/)
- MyInvois API index: [sdk.myinvois.hasil.gov.my/api](https://sdk.myinvois.hasil.gov.my/api/)
- MyInvois e-Invoice APIs: [sdk.myinvois.hasil.gov.my/einvoicingapi](https://sdk.myinvois.hasil.gov.my/einvoicingapi/)
- MyInvois integration practices: [sdk.myinvois.hasil.gov.my/integration-practices](https://sdk.myinvois.hasil.gov.my/integration-practices/)
- JAKIM e-Cert announcement: [islam.gov.my](https://www.islam.gov.my/en/media-statement/4704-kenyataan-media-ketua-pengarah-jabatan-kemajuan-islam-malaysia-berkenaan-pelaksanaan-sijil-pengesahan-halal-malaysia-sphm-secara-elektronik-e-cert)
- JAKIM MyHALALINGREDIENTS announcement: [islam.gov.my](https://www.islam.gov.my/en/media-statement/4798-kenyataan-media-jabatan-kemajuan-islam-malaysia-jakim-berkenaan-pelaksanaan-myhalalingredients)
- JAKIM halal status check: [islam.gov.my](https://www.islam.gov.my/en/law-legal/halal-status-check)
- JAKIM Bahagian Pengurusan Halal profile: [islam.gov.my](https://www.islam.gov.my/ms/bahagian-pengurusan-halal/profil)
- HDC about page: [hdcglobal.com](https://hdcglobal.com/about-hdc/)
