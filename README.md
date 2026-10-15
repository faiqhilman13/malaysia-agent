# Malaysia Agent Ops

Compliance-grade MyInvois e-invoicing for AI agents.

Any MCP-capable agent (Claude, ChatGPT, Copilot, your own) can draft, submit, track, cancel and reject Malaysian e-invoices for the businesses that appointed you as their MyInvois intermediary. A human approves every legally binding action outside the agent's reach, and every step lands in a tamper-evident audit log.

It is built for bookkeeping firms acting for many SMEs, and for SME software vendors that want MyInvois plus agents without building it themselves. Why this scope: [`reports/Malaysian AI agent integration landscape.md`](reports/Malaysian%20AI%20agent%20integration%20landscape.md).

## Status

What works, tested against a fake MyInvois (64 tests, on SQLite and Postgres 16):

- multi-tenant accounts, API keys with roles, mandates per taxpayer, encrypted credential vault
- invoice model with MyInvois mandatory fields, UBL 2.1 JSON, consolidated B2C invoices with the RM10,000 carve-out
- MyInvois client: per-taxpayer token cache, per-endpoint rate limits, `Retry-After`, intermediary `onbehalfof` login
- approvals bound to the exact payload, single use, expiring, decided only by a human
- hash-chained audit log (append-only in Postgres), idempotency keys
- remote MCP (Streamable HTTP) and REST on the same core, plus MCP over stdio

Not yet done or not yet verified:

- **Never run against LHDN preprod.** That round trip is the next milestone; expect field-level fixes from it.
- v1.1 signing follows LHDN's published steps but is unverified. Stay on version 1.0 until preprod accepts a signed document.
- Rate limits for TIN validation, TIN search and document details are assumptions (marked in `myinvois/client.py`).
- Approval links are only written to the server log (`LogNotifier`). WhatsApp and email delivery still need building.
- Bulk cancellation (production from 24 Oct 2026) is not wired; its endpoint path is not confirmed yet.
- The rate limiter and token cache live in one process. Running several workers needs a shared store.
- OAuth: the server verifies JWTs from an external authorization server; it does not issue tokens itself.

## Tools

| Tool | Kind | What it does |
|---|---|---|
| `taxpayers_list` | read | Businesses you may act for, granted permissions, credential readiness |
| `counterparty_validate_tin` | read | Check a buyer's TIN against their registration number with LHDN |
| `counterparty_search_tin` | read | Find a TIN by registration number or name |
| `einvoice_draft` | write | Validate, total and save an invoice, note or self-billed document; returns a preview |
| `einvoice_draft_consolidated` | write | Monthly consolidated B2C e-invoice; lists receipts above RM10,000 that need their own |
| `einvoice_submit` | destructive | Submit to MyInvois, after human approval when policy requires it |
| `einvoice_refresh_status` | read | Validation status, validation link, or validation errors |
| `einvoice_get`, `einvoice_list` | read | Recorded state of documents |
| `einvoice_cancel` | destructive | Cancel within 72 hours of validation (approval required) |
| `einvoice_reject_received` | destructive | As buyer, reject a received e-invoice within 72 hours (approval required) |
| `approval_get_status` | read | Whether a human has decided. There is no tool to approve. |
| `audit_export` | read | Audit events and hash-chain verification |

Every result is an envelope with `status` (`success`, `awaiting_human_approval`, `awaiting_external_event`, `blocked`, `invalid`, `error`), `next_action`, `blocking_reason` and `data`.

## Quickstart

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"            # add ,postgres for Postgres

export MYOPS_VAULT_KEYS=$(myops vault generate-key)   # keep this safe; it decrypts stored credentials
myops db upgrade

myops tenant create --name "Kira Bookkeeping"                          # -> tenant_id
myops user create --tenant $T --email owner@example.my --role approver --phone +60123456789
myops apikey create --tenant $T --role agent --name claude            # shown once

# The business's director appoints you as intermediary in the MyInvois portal; record that mandate here.
myops taxpayer add --tenant $T --tin C25845632020 --id-type BRN --id-value 201901234567 --name "Acme Trading Sdn Bhd"
myops appointment add --tenant $T --tin C25845632020 --mode intermediary \
  --permissions view_documents,submit_documents,cancel_documents --valid-to 2027-10-15 \
  --evidence "Appointed in MyInvois portal by director"

# Your intermediary Client ID from the MyInvois preprod portal; the secret is read from stdin.
myops credential set-myinvois --tenant $T --environment preprod --client-id YOUR_CLIENT_ID

myops serve --port 8080            # REST at /v1, OpenAPI at /docs, MCP at /mcp
```

Connect Claude Code:

```bash
claude mcp add --transport http myinvois http://127.0.0.1:8080/mcp --header "Authorization: Bearer myops_..."
```

Or run it locally over stdio: `MYOPS_API_KEY=myops_... myops mcp-stdio`.

Claude.ai, ChatGPT and Copilot Studio connectors use OAuth. Point `MYOPS_OAUTH_ISSUER`, `MYOPS_OAUTH_AUDIENCE` and `MYOPS_OAUTH_JWKS_URL` at an authorization server (Auth0, Keycloak, WorkOS and so on) whose access tokens carry `myops_tenant` and `myops_role` claims. The server publishes OAuth protected-resource metadata at `/.well-known/oauth-protected-resource/mcp`.

## How approvals work

1. The agent calls `einvoice_submit`. If policy requires approval, the result is `awaiting_human_approval` and nothing reaches MyInvois.
2. Each approver and admin gets their own one-time link (`/approve/<id>?u=…&t=…`). The link never appears in any tool or API response.
3. The approver opens the link, sees the issuer, buyer and amount, and approves or rejects. Opening the link does not decide anything; only the form does.
4. The agent sees `approved` in `approval_get_status` and calls `einvoice_submit` again. The approval is consumed.

The approval is bound to a hash of the exact document. Redrafting voids it, and it cannot be reused for another document. Approver keys can decide through `POST /v1/approvals/{id}/decision`, but not for requests they made themselves. Production cancellations and rejections always need approval. Per tenant you can switch off approval for submissions (useful while testing in preprod) or auto-approve submissions up to an amount:

```bash
myops tenant set-approval-policy --tenant $T --policy '{"auto_approve_submit_max": 500}'
```

## Security model

- **Roles.** `agent` keys call tools. `approver` and `admin` keys belong to a person and can decide approvals. Approver keys cannot call agent tools.
- **Mandates.** Every call checks that the tenant holds a current appointment for that taxpayer with the needed permission (`view_documents`, `submit_documents`, `cancel_documents`, `reject_documents`). The issuer on a draft must be that taxpayer.
- **Secrets.** MyInvois secrets and signing certificates are Fernet-encrypted at rest and decrypted only for the upstream call. They are never tool arguments or results, and MyInvois tokens are never returned.
- **Personal data.** Tool results carry what the agent needs (names, TINs, amounts) and mask identity numbers. Results go to whichever AI client the business uses, often outside Malaysia, so PDPA cross-border rules apply.
- **Audit.** Every action, approval and failure is recorded in a per-tenant hash chain. Run `myops audit verify --tenant $T` to check it; Postgres also blocks UPDATE and DELETE on the table.

## Layout

```
src/malaysia_agent_ops/
  myinvois/     invoice model, code lists, UBL, signing, consolidation, HTTP client
  services/     e-invoice workflows, approvals, audit, idempotency, admin, notifications
  security/     API keys / JWT auth, credential vault
  api/          FastAPI app (REST + approval page) and MCP server
  migrations/   Alembic
tests/          pytest suite with a fake MyInvois
skills/         Agent Skill for using the tools
parked/         halal dossier precheck, parked (standalone)
legacy/v0/      the original demo, archived
```

More detail: [`docs/architecture.md`](docs/architecture.md).

## Development

```bash
pytest                                   # SQLite
MYOPS_TEST_DATABASE_URL=postgresql+psycopg://postgres@localhost/myops_test pytest
ruff check src tests && ruff format --check src tests
```

## License

MIT
