# Codebase Review: Malaysia Agent Ops (audited 2026-10-15)

Scope: all of `src/`, the tests, skill, docs and configs (~7.2k LOC Python; last commit 2026-05-14). The bypass, secret, idempotency and MCP-crash findings were confirmed with throwaway probes against a temp DB. No repo files changed.

**Tests:** `python3 -m unittest discover -s tests -v` → **22/22 OK in 0.74 s** (Python 3.13.16). **Time bomb:** `examples/barakah-curry-paste.dossier.json:118` has a cert that expires 2026-10-15. With the date simulated as 2026-10-16, the precheck flips to `needs_remediation`, so the assertions at `tests/test_end_to_end.py:282` and `:364` will **fail from tomorrow**.

**Verdict:** a well-documented single-user local demo whose only external integration is a thin MyInvois client that has never run live. Keep the ideas and the halal rules content; not the platform code.

---

## 1. Inventory (45 actions, `service.py:39-85`; same set via CLI, REST `server.py:14-62` and MCP)

**(a) Live external HTTP. Every test mocks these; no live run has ever happened.**
| Actions | Notes |
|---|---|
| `providers.myinvois.{login, document_types, validate_tin, search_tin, submit_documents, get_submission, cancel_document}` (7) | `providers.py:99-206`. Real LHDN preprod/prod hosts (`config.py:80-95`). |
| `providers.cidb.{states, labour_wage_rate, building_material_price, machinery_rates}` (4) | `providers.py:228-290`. Calls **`/internal/...` paths of the N3C portal backend** (`:231,245,264,283`) with a bearer token pasted by hand. This is not a documented public API. |
| `invoices.submit/status/cancel` (hybrid) | Takes the real path only when `provider=real`, or when `documents` plus credentials are present (`service.py:2517-2531`). Otherwise it is a local simulation. |

The tests mock every remote call (`test_end_to_end.py:429-463, 565-578, 592-635`). The roadmap itself still lists "P4 live sandbox workflow" as **Next** (`docs/roadmap-and-phases.md:198`).

**(b) Real logic over local SQLite (no external calls).**
- **Orchestration and state:** workflows, approvals, exceptions, `payments.ingest_event/reconcile`, `invoices.validate`.
- **Trade:** `trade.*` only checks for dict keys against 3 hard-coded lists (`fixtures.py:81-102`).
- **Halal ops CRUD layer (12 actions, ~1,000 LOC, `service.py:1132-2093`):** suppliers upsert/list, BOM graph, renewals, workflows create/status, checklists (against **unsourced** IHCS/HAS lists, `fixtures.py:112-130`), audit query create/respond, export dossier, dashboard, evidence pack.
- **Self-declared certificate status:** `halal.suppliers.upsert` lets the caller set `certificate_status: "active"` directly (`service.py:1271`).

**(c) Fixtures, stubs and simulations.**
- **Business registry / SSM:** `entities.resolve/verify_taxpayer/verify_business_registry` look up **5 fake seeded companies** (`fixtures.py:4-50`, seeded at `db.py:277+`). There is no SSM call. `verify_taxpayer` is labelled `source_system: myinvois_sandbox` (`config.py:73`), but it never calls MyInvois.
- **Sandbox invoices only accept fixture companies.** Sandbox invoice validation rejects any TIN that is not one of the 5 fixtures (`service.py:2331-2336`), so it is unusable for a real business. There is also no action to add entities.
- **Halal lookup:** `halal.status.lookup` reads **3 fake JAKIM certs** (`fixtures.py:53-78`). Status is a stored string and expiry is never checked (`service.py:1115`).
- **DuitNow:** `payments.create_request` produces a made-up `duitnow://sandbox/request/...` URI (`service.py:2389-2398, 801`). This is not an EMVCo DuitNow QR, and there is no PayNet or bank integration.
- **Sandbox invoice status:** the first status poll simply flips the invoice to `validated` (`service.py:690-701`).
- **Document sharing:** `halal.documents.share` writes a row marked "shared" and sends nothing (`service.py:1787-1822`).
- **Not exposed as tools at all:** the halal precheck and `tax run` are CLI-only (`cli.py:97-140`).

---

## 2. MCP implementation

- **Hand-rolled, ~290 LOC.** Newline-delimited JSON-RPC over stdio (`mcp_server.py:184-291`). It handles only `initialize`, `ping`, `tools/list`, `tools/call` and `notifications/initialized` (`:211-268`).
- **Protocol version:** it always advertises `"2025-11-25"` (`:11`) and never negotiates. A client asking for 2025-06-18 still gets 2025-11-25 (verified). Capabilities are `tools` only (`:223`).
- **What is present:**
  - `outputSchema`, but it is a generic envelope where `data` is just `{"type":"object"}` (`:15-35`).
  - `structuredContent` plus text content, and `isError` on tool errors (`:245-266`).
  - Tool annotations (`:161-181`), several of which are wrong:
    - `readOnlyHint: true` on `invoices.status`, which changes state (`service.py:100, 690-708`; the real path also creates exceptions at `:2662-2670`).
    - `readOnlyHint: true` on `halal.workflows.status`, which writes when `completed_items` is passed (`:1601-1612`).
    - `destructiveHint: false` on legally binding `invoices.submit` and `providers.myinvois.submit_documents`.
    - `openWorldHint = not read_only` (`:179`). That is backwards: local halal CRUD is flagged open-world, while external MyInvois and CIDB reads are flagged closed.
    - `idempotentHint: true` on `approvals.approve`.
- **Input schemas exist for only 5 of 45 tools** (`:85-148`). The other 40 get `{"type":"object","additionalProperties":true}` (`:151-158`), so the model gets no parameter guidance.
- **Dotted tool names** are spec-legal but fail the Anthropic/OpenAI function-name rule (`^[a-zA-Z0-9_-]{1,64}$`), so each client must rewrite them.
- **Robustness bugs (verified):**
  - It replies to `notifications/cancelled` with an error response (`id: null`). The spec forbids replying to notifications.
  - Only `InputError` and `NotFoundError` are caught (`:259`). Any other exception kills the server process. Example: `halal.renewals.list {"within_days":"abc"}` raises a `ValueError` at `service.py:1471` and crashes it.
  - A JSON line that is not an object raises `AttributeError` at `:212` and also crashes it.
- **Missing MCP features:** Streamable HTTP; OAuth 2.1, RFC 9728 metadata and sessions; resources, prompts, logging, progress, cancellation, completions, pagination, `listChanged`; elicitation (no server-to-client request path at all), sampling, tasks.
- **Remote connectors: no.** Claude.ai and ChatGPT connectors need a public HTTPS MCP endpoint; only local stdio clients (Claude Desktop/Code, Cursor) would work, and the `:8080` REST API is not MCP. No `.mcp.json` registers this server (`.vincent/mcp.json` points at a third-party server; `.factory/settings.json` is a personal plugin toggle).
- **Moving to the official SDK / FastMCP:**
  1. Register each action as a typed tool. Pydantic input models give real schemas; also set `ToolAnnotations` and return types (for structured output).
  2. Run it with `mcp.run(transport="streamable-http")` (stateless mode for horizontal scale).
  3. Add auth with `AuthSettings` plus a `TokenVerifier` against an external identity provider.
  4. Map `InputError` to `ToolError`.
  5. Handle approvals with URL-mode elicitation.

  Effort: 2–4 days for transport and auth, ~1 week to type 45 tools; tenancy is the real cost. Ends the stdlib-only principle, which is fine.

---

## 3. Architecture quality

- **The three layers exist only on paper.**
  - **The "contract"** is a dict that maps action names to method names (`service.py:39-85`), and every payload is an untyped dict.
  - **Orchestration and provider handling** both live in one `OperationsService` class: **3,036 LOC**, 45 action methods plus ~30 helpers across 8 domains. This is a god object.
  - **`db.py`** is 1,179 LOC of hand-written CRUD for 17 tables. Schema changes only use `CREATE TABLE IF NOT EXISTS` (`:50+`), so there are no migrations.
- **Response envelope** (`service.py:160-178`): `status / next_action / blocking_reason / source_system / resource_id / timestamp / data`. This is a good agent-UX idea. However, `next_action` mixes real action names with pseudo-actions that are not enumerated anywhere (`fix_invoice_payload`, `supply_myinvois_credentials`, and the alias `resolve_entity`).
- **Workflow runner** (`:211-389`): a synchronous loop in one call (max 50 steps) with ~7 hard-coded step transitions (`:2787-2834`). Blocked runs can't resume; re-running starts at the root and duplicates submissions. `auto_settle` fakes a successful payment from its own suggested payload (`:2820-2821`).
- **Approvals** (`:2406-2503`). Policies cover only real submissions, cancellations, and payment requests of RM1,000 or more. Verified flaws:
  1. **Identity is self-asserted.** Passing `identity.verified: true` is enough to approve (`:429`). `approvals.approve` is an MCP tool the same agent can call, and `skill/SKILL.md:39,74` tells the agent to approve.
  2. **Approvals are not tied to a payload and are not single-use.** The only check is that the action name matches (`:2416`). In the probe, 1 approval authorised 2 real submits with different invoice numbers and document sets.
  3. **Bypass via the low-level tool:** calling `providers.myinvois.submit_documents` with `provider: "sandbox"` and an access token makes the policy treat it as sandbox (`:2517-2520`). The **real submit then runs with no approval** (verified).
  4. **Bypass via cancel:** `invoices.cancel` on a real submission without `provider: "real"` matches no policy (`:2462-2463`), and the **real cancel runs** via `:734-735` (verified).
  5. **The agent can mark its own invoices paid.** Passing the returned `suggested_event_payload` back into `payments.ingest_event` marks the invoice paid (verified).
- **Multi-tenancy: none.** There is no tenant, org, user, API-key or credential-vault concept anywhere (checked by grep). There is one global `Settings` (`config.py:24-37`) with one MyInvois credential pair and one merchant DuitNow ID, and one SQLite file.
- **HTTP server security** (`server.py`):
  - No authentication or authorisation.
  - `Access-Control-Allow-Origin: *`, including preflight (`:90-93, 153-156`). Any web page can drive the localhost API, including `approvals.approve`.
  - The PayNet webhook route (`:30`) is unauthenticated. `MYOPS_PAYMENT_WEBHOOK_SECRET` is loaded (`config.py:104`) but **never used**.
  - No request body size limit (`:121-123`).
  - Access logs are suppressed (`:158-159`).
  - 500 responses echo the exception text (`:118-119`).
- **Secrets handling:**
  - Secrets (`client_secret`, `access_token`) are accepted as tool arguments, so they end up in the LLM context.
  - `providers.myinvois.login` returns the bearer token to the model (`service.py:2141`).
  - The runner carries secrets from step to step (`:2837-2850`) and **stores raw payloads in plaintext** in `workflow_runs` (`:255-271`, verified).
  - Redaction covers only 3 keys and is applied only to approval records and real-submit records (`:2505-2515`). It does not handle lists.
- **Idempotency and atomicity:**
  - No idempotency keys, and `invoice_number` is not unique (`db.py:75-94`). The same invoice submitted twice produces 2 submissions (verified).
  - `ingest_payment_event` writes three times through separate connections (`service.py:865-976`; each write opens its own connection, `db.py:40-48`). The update is not atomic and events are not de-duplicated.
- **Audit:** there is no append-only log and no record of who acted. So the claim "Every action, transition, and exception is recorded" (`purpose-and-architecture.md:139`) is false.
- **Stdlib + SQLite:** fine for demos; wrong for hosted multi-tenant (no isolation, async, migrations or retries, `providers.py:28-63`).
- **Testability:** one file; the HTTP server is untested beyond its route map, MCP has one happy path, the approval test skips the gate by calling `submit_invoice` directly (`test_end_to_end.py:579`), and there are no negative or security tests.

---

## 4. MyInvois adapter correctness

**Correct:**
- Token endpoint, using client credentials with scope `InvoicingAPI` (`providers.py:99-129`).
- Intermediary `onbehalfof` header on the token request (`:122`).
- `documenttypes` (`:134`), `taxpayer/validate/{tin}` (`:149`), `taxpayer/search/tin` (`:167`), `documentsubmissions` POST/GET (`:174, 190`), and `PUT documents/state/{uuid}/state` to cancel (`:203`).

**Missing or wrong:**
- **No UBL 2.1 JSON or XML generation.** The real path expects the caller to pass `documents` already shaped as `{format, document (base64), documentHash, codeNumber}` (`service.py:2533-2546`). Without that it blocks with `missing_myinvois_documents`, which is exactly what the "real-provider" demo shows. The normalized invoice model (`:2377-2386`) is missing most of LHDN's ~55 mandatory fields: addresses, MSIC code, ID type/BRN, SST number, classification codes, per-line tax type/rate/amount, unit of measure, issue time, and invoice type code.
- **No digital signature.** v1.1 documents need an enveloped XAdES signature (UBLExtensions, an X.509 cert from a Malaysian CA, canonicalisation, signed properties). There is zero crypto code, and the stdlib cannot do RSA signing. The proposal itself lists "signed compliant document generation" as an unmet dependency (`einvoice-halal-proposal.md:246, 355`).
- **No submission prep:** no SHA-256 hashing, base64 encoding, size limits or duplicate-submission handling.
- **No token caching.** The high-level path logs in again on every call (`service.py:2753-2785`). LHDN's login endpoint is rate-limited, so this will be throttled under load. There is no per-taxpayer token cache for intermediary use, which is the core pattern a hub needs.
- **No rate limiting, backoff or 429 handling.** The timeout is a fixed 20 s (`providers.py:37`). The proposal cites LHDN's "API rate guidance" (`:238`), but nothing implements it.
- **Status mapping only reads `documentSummary[0]`** (`service.py:2738-2751`), so multi-document submissions are tracked wrongly.
- **Missing:** buyer reject, get/search/recent documents, notifications, QR validation links, and credit/debit/refund/self-billed/consolidated document types.
- **Bug:** operator precedence at `service.py:2585` stores `invoice_number` as `"unknown"` whenever every document is rejected.
- **Unconfirmed parameter:** `search_tin` sends `entityType` (`providers.py:161-163`). I couldn't confirm this parameter in LHDN's docs, which list `idType`, `idValue` and `taxpayerName`.

**Net:** about 150 LOC of correct URL and header plumbing. The hard ~80% (UBL mapping, signing, validation, intermediary credential management, rate limits) is absent.

---

## 5. Halal precheck (`halal_precheck.py`, 679 LOC + `data/halal_requirements.json`)

**What it actually does:**
- A pure rules function (`:50-103`). It walks a JSON dossier for `documents[]` entries, each with a **self-declared** `kind`, `path` and `metadata` (`:106-125`).
- It applies 15 JSON rules, filtered by application type and one simple equality condition (`:244-260`).
- **A rule passes if any document of any listed kind exists** (`:272-274`). Files are never opened or even checked to exist; the examples point at `docs/barakah/*.pdf`, which is absent.
- It checks expiry dates against today (`:358-388`).
- "OCR" means comparing declared metadata with OCR JSON supplied beforehand (`:292-398`). There is no OCR engine. The example OCR files are hand-written but labelled `"extractor": "glm-ocr"` (`examples/ocr/barakah/supplier-a-coconut-cert.json:3`), while OCR is still "Planned" (`purpose-and-architecture.md:164`).
- Output is JSON plus applicant and reviewer reports in MD and HTML.

**How source-grounded it is:**
- **Good:** every rule carries `source_id`, `source_url` and `evidence_class`, and there is a ground-truth register with evidence classes.
- **Thin:** the rules cite only 2 sources (a portal procedure page, S1, and a 2021 announcement, S2). S3 is defined but unused. There are no MPPHM 2020 or MS 1500:2019 clause references, and no `interview_observation` entries (the discovery backlog is entirely open).
- **Dead code:** `requirements_skipped` is always 0 (`:422`).
- **Two parallel halal rule systems:** the precheck's 15 sourced rules, and the ops layer's unsourced lists (`fixtures.py:105-130`). The second contradicts the register's own guardrails.

**Value as an agent tool:** modest, a document-presence checklist that needs real intake/OCR and directory lookups to matter; MYeHALAL and MyHALALINGREDIENTS have no public API (`einvoice-halal-proposal.md:305-313`). Not exposed through MCP. **Coupling:** none (only `cli.py:10` imports it), so it is the easiest module to lift.

---

## 6. Docs and README hygiene

- **41 absolute `/Users/faiqhilman/Projects/malaysia-agent-ops` paths:** README (16), roadmap (15), action-map (4), SKILL.md (3, including the frontmatter `description` at `:3`), CONTRIBUTING (3). The links are broken on GitHub, and the repo directory name now differs (`malaysia-agent`).
- **Counts are accurate today** (45 actions, 46 POST routes, 22/22 tests; `README.md:85, 481`), but the test count goes stale 2026-10-16 and the roadmap baseline predates the May changes.
- **Overstated claims:**
  - "Live MyInvois integration … against LHDN's official rails" (`purpose-and-architecture.md:151`).
  - `docs/index.html:839-841` "Live … Real LHDN sandbox integration" and `:1078` "Live sandbox tested". The roadmap ("P4 Next") and the all-mocked tests contradict this.
  - A "Live" badge for halal (`index.html:872`) on what is local CRUD.
  - "Sandbox parity: every production workflow has a sandbox path" (`purpose:192`). In practice it is the reverse: the sandbox invoice flow has no production equivalent.
  - The dashboard's "2 official provider families wired to documented endpoints", when CIDB uses portal `/internal` paths.
  - Naming that suggests integrations which don't exist: the `myhalalingredients_records` field (`service.py:1205`), `source_system: myinvois_sandbox` on fixture lookups, and the `glm-ocr` labels. The video script says the precheck compares against "what the scanned certificate actually says", but no scan or OCR ever happens.
- **Honest parts:** README "What is sandboxed" (`:412-417`), tax PRD guardrails, roadmap phase tables.
- **Repo hygiene:** ~31 MB of MP4/PNG committed (`.git` 57 MB), personal agent configs committed (`.vincent`, `.factory`), no CI, lint, type checking or Dockerfile.

---

## 7. Pivot assessment: reuse vs. discard, verdict, top 10 gaps

**Reusable (~10–15% of the code, plus concepts):**
- **Concepts:**
  - The response envelope with `next_action` and `blocking_reason`.
  - Policy-keyed approval gates.
  - The "block honestly / never fake a submission" principle.
  - The evidence-class ground-truth register.
- **Code:**
  - The MyInvois client paths and headers in `providers.py:66-213`, as a reference.
  - `halal_precheck.py` and its JSON rules, as an optional vertical tool or content asset.
  - The test scenarios, as acceptance specs.

**Throw away:**
- The hand-rolled MCP server, `server.py`, `db.py`, and the fixture-backed "providers" (entities, halal directory, DuitNow, trade).
- The halal ops CRUD layer (~1k LOC; it is a local app, not connectivity).
- The CIDB adapter (undocumented internal endpoints).
- The synchronous workflow runner: replace it with agent-side orchestration or a durable workflow engine.
- The HTML dashboards and the videos.

**Overall verdict:** technically, **pivot everything**. Retrofitting tenancy, OAuth, remote MCP, a vault, signing and idempotency into a 3k-line stdlib/SQLite god object costs more than a clean build on the official MCP SDK + Postgres + external IdP. What survives is knowledge: the LHDN endpoint map, the halal taxonomy, agent-UX patterns. A hub's defensible parts (MyInvois UBL mapping and signing, per-business intermediary credentials, real SSM/PayNet/bank access) are entirely absent.

**Top 10 technical gaps:**
1. **No multi-tenancy or identity.** No orgs, users, agents, API keys or OAuth. Single global config (`config.py:24-37`).
2. **No remote MCP.** Stdio only (`mcp_server.py:192-209`); no Streamable HTTP, OAuth or sessions, so Claude.ai and ChatGPT connectors can't use it.
3. **The approval model can be bypassed and self-approved.** Self-asserted identity, approvals not tied to a payload, no single-use, and 2 verified bypasses (`service.py:429, 2416, 2462-2463, 2517-2520`).
4. **No credential vault.** Secrets travel in tool arguments, are returned to the model (`:2141`), and are stored in plaintext (`:255-271`).
5. **MyInvois is a pass-through.** No UBL generation, no signing, no hashing, no token cache, no rate limits or retries, and it has never been run against preprod.
6. **Every other "integration" is a fixture.** SSM, the halal directory, DuitNow and trade (`fixtures.py`). The sandbox only accepts 5 fake TINs.
7. **Unauthenticated HTTP API** with `CORS *` and an unverified payment webhook (`server.py:30, 153-156`; `config.py:104` unused).
8. **No idempotency, atomicity or event de-duplication.** Duplicate invoices are accepted, and multi-write updates are not atomic (`db.py:40-48, 75-94`).
9. **Weak tool contracts.** 40 of 45 tools have no input schema, several annotations are wrong, the server crashes on unexpected exceptions, and it violates the spec by replying to notifications.
10. **Maintainability and ops.** A 3k-LOC god object, untyped dict payloads, no migrations, no audit log or observability, logs suppressed, date-dependent tests that break 2026-10-16, and no CI.
