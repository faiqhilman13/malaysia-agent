# Halal Precheck PRD

## Product Decision

Malaysia Agent Ops should focus on a CLI/API/MCP layer for:

- halal dossier operations and internal pre-checks for the Malaysian halal industry
- Malaysia tax and e-invoicing workflows through LHDN/MyInvois

CIDB and construction workflows are not part of the core product direction. They can remain as adapter experiments, but they should not drive the roadmap, narrative, or first demos.

## Problem

The project is at risk of encoding halal workflow assumptions before enough real domain discovery has happened.

The product must therefore separate:

- facts backed by official sources
- facts learned from consultants, applicants, auditors, or authority-side operators
- working product assumptions

The first implementation should prove a narrow, auditable workflow instead of broad certification automation.

## First User Segment

The long-term user base is anyone working in the halal industry, including:

- applicant companies
- halal consultants
- internal halal executives or PICs
- reviewer-side or authority-adjacent operators
- eventually JAKIM, MAIN, JAIN, or other authoritative stakeholders if sanctioned workflows become available

The first practical adoption path should start with applicants and consultants because they are easier to interview, can expose the messy pre-submission workflow, and can use internal pre-checks without official platform access.

## First Workflow

The first workflow is:

`create dossier -> attach/declare evidence -> validate requirements -> verify declared metadata where possible -> emit pre-check reports`

This is an internal pre-check before official submission. The product must not claim to submit to MYeHALAL or determine halal status.

The durable product object is the `dossier/application workspace`, not only a company, premise, or product.

## First Demo

Primary demo:

`one food manufacturer preparing a product halal dossier for internal pre-check`

Secondary demo:

`one restaurant or food premise running halal readiness pre-check before official application`

The manufacturer demo comes first because it exercises richer dossier logic: ingredients, supplier certificates, packaging labels, process flow, premise/factory evidence, and raw-material records.

## CLI Shape

The repo should keep two layers:

1. Agent contract layer:

```bash
myops action halal.evidence_pack.generate --json '{...}'
```

2. Industry operator layer:

```bash
myops halal precheck run --file examples/barakah-curry-paste.dossier.json --out-dir reports/barakah
```

The operator layer should become business-noun oriented over time, but the first slice should stay narrow.

## Input Format

V0 uses JSON only to preserve the repo's dependency-light posture.

YAML can be added later as an optional usability layer. The JSON dossier is the portable business artifact and the source of declared metadata.

## Requirement Rules

Requirement rules should be stored as JSON data, not hard-coded directly into the evaluator.

Each rule should include:

- `requirement_id`
- `applies_to`
- `title`
- `required_document_kinds`
- `severity`
- `evidence_class`
- `source_id`
- `source_url`

This keeps validation output traceable to the ground truth register and easier to update after interviews.

## OCR Direction

OCR is part of the product direction, but it should not be the foundation of V0.

Preferred OCR path:

- local open-source OCR
- GLM-OCR as the preferred model direction
- optional extraction/verification layer

The core pre-check validator must work without OCR.

OCR should verify declared metadata first, not auto-fill the dossier. Auto-fill can come later after field reliability and document variation are understood.

Declared dossier metadata remains the user's claim:

```json
{
  "kind": "ingredient_halal_certificate",
  "path": "docs/supplier-a-cert.pdf",
  "metadata": {
    "supplier_name": "Supplier A",
    "certificate_no": "JAKIM-2025-001",
    "expiry_date": "2026-12-31",
    "covers": ["Coconut milk powder"]
  }
}
```

OCR output is supporting observed evidence:

```json
{
  "document_path": "docs/supplier-a-cert.pdf",
  "fields": {
    "supplier_name": {"observed": "Supplier A Sdn Bhd", "confidence": 0.93},
    "certificate_no": {"observed": "JAKIM-2025-001", "confidence": 0.89}
  }
}
```

The validator compares declared versus observed values and reports:

- `match`
- `mismatch`
- `missing_from_document`
- `low_confidence`
- `not_declared`
- `not_evaluable`

## Report Outputs

V0 should emit:

- `precheck.json`
- `applicant-report.md`
- `reviewer-report.md`
- `applicant-report.html`
- `reviewer-report.html`

JSON is canonical. Markdown and HTML should be rendered from the validation result so the views do not drift.

Applicant report goal:

- help the applicant or consultant fix gaps before official submission

Reviewer report goal:

- help a reviewer or internal auditor understand the dossier, evidence coverage, source-backed rules, OCR confidence, and unresolved assumptions quickly

## Guardrails

- Do not claim direct MYeHALAL submission until a sanctioned integration path is confirmed.
- Do not claim to determine halal status.
- Do not hard-code one universal checklist across schemes.
- Keep evidence classes visible in output.
- Treat source-backed requirements differently from interview-derived observations and product assumptions.
- Keep CIDB out of core positioning unless the project direction changes.

## V0 Acceptance Criteria

The V0 implementation is acceptable when:

- `myops halal precheck run --file ... --out-dir ...` works from the repo root
- it loads a JSON dossier
- it loads JSON requirement rules
- it validates manufacturer requirements first
- it accepts optional OCR verification JSON
- it writes JSON, Markdown, and HTML reports
- every requirement result includes source metadata
- existing tests still pass
- at least one sample dossier can generate reports end to end
