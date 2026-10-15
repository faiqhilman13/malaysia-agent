# Tax Execution Summary

- Invoice: `INV-TAX-DEMO-001`
- Supplier TIN: `C1234567801`
- Buyer TIN: `C1234567802`
- Total amount: `MYR 150.0`
- Execution mode: `sandbox`
- Overall status: `pass`
- Workflow status: `completed`
- Blocking reason: `None`

## Result

- Run ID: `9eae7d15-b438-4e53-a1be-7abb319d35cf`
- Submission ID: `53d90f94-50a2-4853-8800-9ffec66b137b`
- Payment request ID: `5e33451f-d3e3-424f-99b9-4e7a9172f99a`
- Final invoice status: `paid`
- Final payment status: `matched`
- Exceptions: `0`

## Execution Steps

| Step | Action | Status | Next Action | Blocking Reason | Resource |
|---|---|---|---|---|---|
| 1 | `invoices.submit` | `success` | `invoices.status` | `None` | `53d90f94-50a2-4853-8800-9ffec66b137b` |
| 2 | `invoices.status` | `success` | `payments.create_request` | `None` | `53d90f94-50a2-4853-8800-9ffec66b137b` |
| 3 | `payments.create_request` | `success` | `payments.ingest_event` | `None` | `5e33451f-d3e3-424f-99b9-4e7a9172f99a` |
| 4 | `payments.ingest_event` | `success` | `None` | `None` | `5e33451f-d3e3-424f-99b9-4e7a9172f99a` |

## Notes

- Sandbox execution used local deterministic MyInvois-shaped and DuitNow-shaped workflow state.
- No live MyInvois submission was performed.
