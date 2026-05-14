# Tax Execution Summary

- Invoice: `INV-TAX-REAL-BLOCK-001`
- Supplier TIN: `C1234567801`
- Buyer TIN: `C1234567802`
- Total amount: `MYR 120.0`
- Execution mode: `real_provider`
- Overall status: `blocked_honestly`
- Workflow status: `blocked`
- Blocking reason: `awaiting_human_approval`

## Result

- No live MyInvois submission was performed.
- The run stopped at `awaiting_human_approval`.
- Next action: `approvals.approve`.

## Execution Steps

| Step | Action | Status | Next Action | Blocking Reason | Resource |
|---|---|---|---|---|---|
| 1 | `invoices.submit` | `blocked` | `approvals.approve` | `awaiting_human_approval` | `4656b5a9-7012-40a5-81c7-6abf94b59386` |

## Notes

- No live MyInvois submission was performed.
- Real-provider execution is intentionally approval-gated and credential-gated.
