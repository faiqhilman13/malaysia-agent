# Tax Execution PRD

## Product Decision

The tax side of Malaysia Agent Ops is not an accounting app and not tax advice.

It is an execution layer for Malaysian e-invoicing workflows:

`validate invoice -> submit invoice -> poll status -> create payment request -> ingest payment event -> settle or surface exceptions`

For live MyInvois use, the system must block honestly on approvals, credentials, and compliant document payloads. It must never imply a live LHDN submission happened when it did not.

## First User

The first tax user is:

- finance operations team
- ERP/POS/accounting software operator
- agent builder integrating Malaysian invoice execution

The first user is not an individual taxpayer using this as a tax-advice tool.

## V0 Workflow

V0 proves two internal paths:

1. Sandbox happy path:
   - run a normalized invoice through the local MyInvois-shaped workflow
   - create a DuitNow-shaped payment request
   - ingest a payment success event
   - finish with the invoice paid and no open exception

2. Real-provider blocked path:
   - attempt a real MyInvois invoice submission
   - stop at the first safety gate
   - report `awaiting_human_approval` or the next credential/document blocker
   - explicitly state that no live MyInvois submission was performed

## CLI Shape

The durable operator command is:

```bash
python3 manage.py tax run \
  --file examples/tax/sandbox-happy-path.invoice.json \
  --payment-event examples/tax/payment-success.json \
  --out-dir reports/tax/sandbox-happy-path
```

For live-provider safety behavior:

```bash
python3 manage.py tax run \
  --file examples/tax/real-provider-attempt.invoice.json \
  --real-provider \
  --out-dir reports/tax/real-provider-blocked
```

The command writes:

- `summary.json`
- `summary.md`

## Report Purpose

The report is an execution trace, not a dossier report.

It should show:

- invoice number, supplier TIN, buyer TIN, amount
- execution mode
- workflow status
- steps executed
- final status and blocking reason
- submission id when created
- payment request id when created
- payment status when settled
- exception ids when created
- a clear note when no live MyInvois submission was performed

## Guardrails

- Do not provide tax advice.
- Do not claim production submission without live credentials and official response evidence.
- Do not auto-approve real-provider submissions.
- Do not hide approval, credential, document, or remote API blockers.
- Keep the sandbox path deterministic and repeatable.

## V0 Acceptance Criteria

- `tax run` works for sandbox invoice execution.
- `tax run --real-provider` blocks before live submission without credentials or approval.
- Both paths write `summary.json` and `summary.md`.
- Tests cover sandbox completion and real-provider block behavior.
- Docs and README show the repeatable commands.
