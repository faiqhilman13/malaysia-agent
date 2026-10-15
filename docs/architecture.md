# Architecture

## Shape

```
AI client (Claude, ChatGPT, Copilot, custom)      Software vendor backend        Approver (phone / browser)
        │ MCP over Streamable HTTP or stdio               │ REST /v1                        │ /approve/<id> link
        ▼                                                 ▼                                 ▼
  api/mcp_server.py  ─────────────┐        api/app.py (FastAPI) ───────────────────── approval page
        13 workflow tools         │                 │
                                  ▼                 ▼
                    services/einvoice.py  ── services/approvals.py ── services/notify.py
                    (mandate checks, policy,     (payload-bound, single use,
                     idempotency, audit)          human-only decisions)
                                  │
                    myinvois/ (invoice → UBL → sign → client)        services/audit.py (hash chain)
                                  │                                   security/vault.py (Fernet)
                                  ▼
                     LHDN MyInvois (preprod / production)
```

MCP and REST are thin adapters over the same service methods. A service method takes a `Principal` (tenant, subject, role) and returns an envelope. It never raises to the caller: known errors become `blocked`/`invalid`/`error` envelopes and are audited, unexpected errors are logged and return a generic error.

## Data model

| Table | Purpose |
|---|---|
| `tenants` | Customer accounts. `settings.approval_policy`, plus the head of the audit hash chain. |
| `users` | People. Approvers and admins receive approval links. |
| `api_keys` | SHA-256 hashes of bearer keys, with role `agent`, `approver` or `admin`. |
| `taxpayers` | Businesses a tenant may act for. |
| `appointments` | The mandate: mode (`intermediary` or `self`), permissions, validity window, evidence. |
| `credentials` | Encrypted MyInvois Client ID/secret pairs and signing certificates, per environment. |
| `documents` | Drafted documents: the input, exact UBL bytes, payload hash, MyInvois ids and status. |
| `approvals` | Requests bound to `(action, resource, payload_hash)`, with a per-approver token hash. |
| `idempotency_keys` | Final results of submit, cancel and reject, by key. |
| `audit_events` | Append-only; `hash = sha256(prev_hash + canonical event)`. |

## Document lifecycle

```
draft ──submit──► (awaiting approval) ──approved──► submitted ──refresh──► valid ──cancel (≤72h)──► cancelled
  ▲                                                     │                     │
  └──────────── redraft (same code_number) ◄── invalid ◄┘                     └── after 72h: credit note (type 02)
```

- The issue time is fixed when the document is drafted, because the approval covers it. MyInvois rejects issue times older than 72 hours, so a draft left unapproved for more than 72 hours has to be drafted again.
- Redrafting an invoice number is allowed only while the document is `draft` or `invalid`.
- A transport failure during submit leaves the document as `draft` and the approval unconsumed. A retry is safe because MyInvois rejects exact duplicates within 10 minutes.

## MyInvois specifics handled

- Intermediary login sends an `onbehalfof: <taxpayer TIN>` header. Tokens are cached per (environment, Client ID, taxpayer) and refreshed 5 minutes before expiry or after a 401.
- Rate limits are per Client ID: login 12/min, submit 100, get submission 300, cancel 12, reject 12, search documents 12. Others are assumed (see `myinvois/client.py`). The client waits up to `MYOPS_MYINVOIS_MAX_RATE_LIMIT_WAIT_SECONDS` for a free slot, then returns `blocked` with a retry time.
- Submission entries are `{format: JSON, document: base64(bytes), documentHash: sha256(bytes), codeNumber}`. The exact bytes that were hashed are the ones sent.
- Versions: 1.0 unsigned, 1.1 signed; SVDP 1.2 and 1.3 are only accepted from 7 Jul 2026 to 31 Dec 2027.
- Consolidated e-invoices use buyer TIN `EI00000000010` and classification `004`. Single receipts above RM10,000 are carved out. The submit-by date is month end + 7 days.

## Deployment notes

- Run `myops db upgrade` per release. Postgres is recommended; the migration adds the append-only audit trigger.
- Set `MYOPS_PUBLIC_BASE_URL` to the public HTTPS URL and add its host to `MYOPS_MCP_ALLOWED_HOSTS` (DNS-rebinding protection rejects unknown Host headers).
- Keep `MYOPS_VAULT_KEYS` outside the database host. To rotate, prepend a new key and re-encrypt credentials.
- Hosting in Malaysia keeps stored taxpayer data onshore. Tool results still travel to the AI client.
- One process for now: the MyInvois rate limiter and token cache are in memory.

## Next steps (from the plan)

1. Round trip against LHDN preprod for every document type, then a nightly preprod test in CI.
2. Approval delivery over WhatsApp (utility templates) and email.
3. Verify v1.1 signing in preprod. Confirm with LHDN whose certificate an intermediary signs with.
4. Bulk cancellation; a shared rate limiter and token cache (Redis) for multiple workers.
5. Quote-to-cash: gateway webhooks (Billplz/CHIP), matching payments to invoices, Bukku/Xero sync.
