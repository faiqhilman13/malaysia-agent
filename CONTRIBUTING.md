# Contributing

The product is a compliance-grade MyInvois layer for AI agents. Changes are judged on one question: does this make an agent's e-invoicing safer, more correct, or more complete for a real Malaysian business?

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,postgres]"
pytest
ruff check src tests && ruff format --check src tests
```

To run the suite against Postgres, set `MYOPS_TEST_DATABASE_URL=postgresql+psycopg://...`.

## Rules

- **Never fake a submission.** If something cannot be done (no credentials, no mandate, window passed), return `blocked` with a `next_action`. Do not return a fake success.
- **Fixtures stay in `tests/`.** The fake MyInvois is for tests only and is never a runtime provider.
- **Every legally binding action goes through the approval gate.** Add a regression test whenever a new path reaches MyInvois.
- **No secrets in tool arguments, tool results, logs or audit details.** `services/redaction.py` is the backstop, not the plan.
- **MCP tools are workflow-level.** Use underscore names, a `read_only` or `destructive` hint, and keep read and write tools separate.
- **Schema changes need an Alembic migration.** Run `alembic -c src/malaysia_agent_ops/migrations/alembic.ini check` to confirm it matches the models.
- **LHDN rules change often.** When you encode one, cite the SDK page or guideline version in a comment.
