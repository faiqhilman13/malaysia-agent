# Tax Execution Demo Guide

## Purpose

This guide proves the tax/e-invoicing side of Malaysia Agent Ops without external credentials.

The tax workflow is about execution progression, not dossier readiness:

`submit invoice -> poll invoice status -> create payment request -> ingest payment event -> finish paid or block honestly`

## Demo Commands

Run from the repo root.

### Sandbox Happy Path

```bash
python3 manage.py tax run \
  --file examples/tax/sandbox-happy-path.invoice.json \
  --payment-event examples/tax/payment-success.json \
  --out-dir reports/tax/sandbox-happy-path \
  --pretty
```

Expected summary:

- `overall_status=pass`
- `workflow_status=completed`
- final invoice status is `paid`
- final payment status is `matched`
- no live MyInvois submission was performed

### Real-Provider Blocked Path

```bash
python3 manage.py tax run \
  --file examples/tax/real-provider-attempt.invoice.json \
  --real-provider \
  --out-dir reports/tax/real-provider-blocked \
  --pretty
```

Expected summary:

- `overall_status=blocked_honestly`
- blocking reason is `awaiting_human_approval`
- no live MyInvois submission was performed
- the next action is `approvals.approve`

## Output Files

Each run writes:

- `summary.json`
- `summary.md`

The JSON file is the canonical execution record. The Markdown file is the operator-readable audit summary.

## What This Does Not Claim

- It does not provide tax advice.
- It does not replace accounting software.
- It does not perform a live MyInvois submission without credentials, compliant payloads, and explicit approval.
- It does not auto-approve real-provider submissions.

## Internal Validation

The regression suite covers:

- sandbox tax execution completion
- real-provider approval block behavior
- report generation

Run:

```bash
python3 -m unittest discover -s tests -v
```
