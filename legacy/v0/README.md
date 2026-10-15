# v0 reference (archived)

The original single-user demo, moved here unchanged when the project was rebuilt in October 2026. The same code is at commit `227a07a` (tag `v0-reference`).

Nothing in the new package imports from this folder, and its tests are not run in CI. It is kept for reference:

- `src/malaysia_agent_ops/providers.py` lines 66-213: MyInvois endpoint and header map.
- `tests/test_end_to_end.py`: v0 scenarios, reused as acceptance specs for the rebuild.
- `docs/`: v0 strategy and PRDs. Several claims in them overstate what v0 did (for example "Live MyInvois integration"); see `reports/Malaysian AI agent integration landscape.md` for the audit.

Safe to delete once the rebuild covers what you still need from it.
