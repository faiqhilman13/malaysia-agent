# Contributing

Thanks for contributing to `malaysia-agent-ops`.

This project is an execution-layer alpha for Malaysia-specific agent workflows. The main principle is simple:

- agents should run the workflow
- humans should only inspect, approve, or rectify blocked cases

Contributions that strengthen this pattern are preferred over one-off UI work or disconnected experiments.

## Good Contribution Areas

- MyInvois payload validation and real sandbox execution
- payment event ingestion and webhook verification
- halal compliance workflow depth
- operator dashboards for approvals and blocked runs
- MCP and skill ergonomics
- provider adapters for official Malaysia rails
- tests, fixtures, error handling, and observability

## Before You Start

1. Read [README.md](/Users/faiqhilman/Projects/malaysia-agent-ops/README.md).
2. Read [roadmap-and-phases.md](/Users/faiqhilman/Projects/malaysia-agent-ops/docs/roadmap-and-phases.md).
3. Check existing issues and open a short proposal if the change is large.

## Local Setup

The repo is intentionally lightweight and uses Python stdlib only for the core app.

```bash
cd /Users/faiqhilman/Projects/malaysia-agent-ops
python3 -m unittest discover -s tests -v
python3 manage.py serve --host 127.0.0.1 --port 8080
```

Useful local entrypoints:

- CLI: `python3 manage.py action <action-name> --json '<payload>' --pretty`
- API: `POST /v1/actions/<action-name>`
- MCP: `python3 manage.py mcp`

## Contribution Guidelines

- Keep changes narrow and composable.
- Preserve CLI, API, and service-layer contract parity.
- Prefer adding or extending tests with behavior changes.
- Do not commit secrets, tokens, or real credentials.
- Do not present mocked integrations as production-ready connectors.
- Keep response contracts machine-readable and explicit about blocked states.

## Coding Expectations

- Use ASCII by default.
- Follow the existing JSON-first action pattern.
- Keep human approval and exception boundaries explicit.
- Prefer clear provider seams over hardcoded partner logic.
- If you add a new workflow step, document its `next_action`, terminal states, and failure modes.

## Pull Requests

Please include:

1. What problem the change solves
2. Which vertical or shared platform surface it affects
3. How you tested it
4. Any new env vars, fixtures, or external dependencies
5. Screenshots only if the change affects the HTML workbenches

A good PR is one that moves the system closer to:

- live official rails
- autonomous run-until-blocked execution
- safe human approval boundaries
- clearer operator visibility

## Reporting Issues

When opening a bug, include:

- expected behavior
- actual behavior
- action name or route involved
- sample payload
- traceback or error response
- whether the issue is local-only, provider-specific, or workflow-specific

## Roadmap Alignment

If you want to contribute but are not sure where to start, pick work that helps one of these milestones:

- real MyInvois sandbox workflow through `invoices.*`
- real payment event ingestion instead of manual reconcile
- stronger approval and identity controls
- richer halal workflow execution and evidence automation
- operator-grade approvals and blocked-run UI
