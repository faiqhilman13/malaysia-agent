---
name: "malaysia-agent-ops"
description: "Operate the local malaysia-agent-ops application through its CLI, HTTP API, and MCP surfaces. Use when an agent needs to run Malaysia-specific business workflows like MyInvois invoice submission, payment request creation, payment event ingestion, approval handling, CIDB lookups, halal compliance workflows, or autonomous run-until-blocked execution inside /Users/faiqhilman/Projects/malaysia-agent-ops."
---

# Malaysia Agent Ops

## Overview

Use this skill to treat `malaysia-agent-ops` as an execution layer, not a passive codebase. Prefer autonomous workflow execution, stop only on approvals or exceptions, and use direct action calls only when you need read-only inspection, debugging, provider smoke tests, or explicit operator intervention.

The app lives at:

- `/Users/faiqhilman/Projects/malaysia-agent-ops`

If the repo path changes, discover the new path before running commands.

## Workflow Choice

Choose the execution interface in this order:

1. Use `workflows.run` when the goal is end-to-end business execution and the app can keep following `next_action` automatically.
2. Use direct `manage.py action ...` calls for:
   - read-only inspection
   - approvals
   - exception resolution
   - payment event ingestion
   - provider-level MyInvois or CIDB tests
3. Use the HTTP API when a browser app, webhook sender, or external process needs access.
4. Use `python3 manage.py mcp` only when another MCP-capable agent runtime needs tool discovery over stdio.

## Core Rules

- Treat humans as approvers or rectifiers, not workflow operators.
- Prefer high-level actions like `invoices.submit` over low-level `providers.myinvois.submit_documents` unless you are explicitly testing the provider rail.
- For payment progression, prefer `payments.ingest_event`. Use `payments.reconcile` only as manual fallback.
- When a response is `blocked`, inspect `blocking_reason` and `next_action` before improvising.
- If the app requests approval, use `approvals.list` and `approvals.approve` or `approvals.reject`.
- If the goal is production-like execution, expect credentials and approvals to be required.

## Quick Commands

Run from the project directory:

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
```

Start the HTTP server:

```bash
python3 manage.py serve --host 127.0.0.1 --port 8080
```

Start the MCP server:

```bash
python3 manage.py mcp
```

Invoke one action:

```bash
python3 manage.py action <action-name> --json '<payload>' --pretty
```

## Recommended Operating Pattern

For autonomous finance or compliance execution:

1. Start with `workflows.run`.
2. If the run blocks on:
   - `awaiting_human_approval`: inspect pending approval and decide whether to approve or reject.
   - `awaiting_external_event`: ingest the missing payment or provider event.
   - `remote_api_error`: debug the real provider path.
   - validation or evidence issues: resolve the underlying data problem, then rerun or continue manually.
3. Inspect final state through:
   - `workflows.status`
   - `exceptions.list`
   - `halal.dashboard.snapshot`

## When To Read References

- Read [references/action-map.md](references/action-map.md) when you need:
  - the exact high-value actions
  - the invoice and payment flow
  - the approval loop
  - the halal and provider test surfaces
  - command examples worth copying directly

Do not load the reference file unless you actually need operational detail beyond this summary.
