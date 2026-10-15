---
name: myinvois-einvoicing
description: Issue, track, correct and reject Malaysian e-invoices in LHDN MyInvois through the malaysia-agent-ops MCP tools (taxpayers_list, einvoice_draft, einvoice_submit and related). Use when a user asks to invoice a Malaysian buyer, submit or check an e-invoice, issue a credit note, consolidate monthly B2C sales, or reject an e-invoice they received.
---

# MyInvois e-invoicing

You act for Malaysian businesses that appointed this account as their MyInvois intermediary. Every e-invoice you submit in production is a legal tax document, so work carefully and let the human approve.

## Before anything

- Call `taxpayers_list`. Act only for a listed business, and only within its permissions (`submit_documents`, `cancel_documents`, `reject_documents`, `view_documents`).
- Use `environment: "preprod"` unless the user clearly means production.
- Never ask for MyInvois client secrets, certificates or passwords. If the result says credentials are missing, tell the user an admin must add them.

## Issue an invoice

1. Get the buyer's TIN and registration number (12-digit BRN or NRIC). For a new buyer, call `counterparty_validate_tin`. If it is not valid, ask the user to confirm the details; do not guess.
2. Call `einvoice_draft`. The supplier is the business you act for (for self-billed types 11-14, the buyer is). Each line needs a classification code (`022` = others), a tax type (`06` = not applicable, `02` = service tax with `tax_rate` 8, `E` = exempt with a reason), quantity and unit price.
3. Show the user the preview: buyer, lines, totals and any `warnings`. If anything is wrong, draft again with the same `code_number`.
4. Call `einvoice_submit`, passing an `idempotency_key` such as `submit-<code_number>`.
   - `awaiting_human_approval`: tell the user an approver has been sent a link. Check `approval_get_status` later. When it is `approved`, call `einvoice_submit` again with the same key. You cannot approve anything yourself.
   - `blocked`: read `blocking_reason`, tell the user, and follow `next_action`. Do not work around it.
5. Call `einvoice_refresh_status` until the status is `valid` (share `validation_link`) or `invalid` (fix the fields in `errors` and redraft with the same `code_number`).

## Corrections

- Within 72 hours of validation: `einvoice_cancel` with a clear reason (needs approval).
- After 72 hours: draft a credit note (`document_type` "02") or debit note ("03") with `original_document` set to the original `code_number` and `uuid`.
- Received a wrong e-invoice? `einvoice_reject_received` within 72 hours (needs approval). The supplier must then cancel it.

## Monthly B2C sales

Use `einvoice_draft_consolidated` with the month's receipts. Receipts above RM10,000 cannot be consolidated; they are listed in `individual_einvoice_required`, and each needs its own `einvoice_draft`. Submit by `submit_by` (7 days after month end).

## Reading results

Every result has `status`, `next_action`, `blocking_reason` and `data`. Follow `next_action`. Report `blocked` and `invalid` to the user in plain language. Never report a submission as done until `einvoice_refresh_status` shows `valid`.
