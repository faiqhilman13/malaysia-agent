# Halal Precheck Demo Guide

## Purpose

This guide shows the internal demo artifacts for the halal precheck workflow.

The point is to prove three things without external dependencies:

1. a clean manufacturer dossier can pass source-tagged checks
2. an incomplete manufacturer dossier produces useful remediation output
3. a restaurant / food-premise dossier uses a different requirement set from a manufacturer dossier

## Demo Commands

Run from the repo root.

### Passing Manufacturer Dossier

```bash
python3 manage.py halal precheck run \
  --file examples/barakah-curry-paste.dossier.json \
  --ocr-dir examples/ocr/barakah \
  --out-dir reports/barakah \
  --pretty
```

Expected summary:

- `overall_status=pass`
- source-backed manufacturer requirements pass
- GLM-OCR-style metadata verification matches the declared supplier certificate metadata

### Failing Manufacturer Dossier

```bash
python3 manage.py halal precheck run \
  --file examples/barakah-curry-paste-incomplete.dossier.json \
  --ocr-dir examples/ocr/barakah-failing \
  --out-dir reports/barakah-failing \
  --pretty
```

Expected summary:

- `overall_status=needs_remediation`
- missing process flow evidence is flagged
- missing financial statement evidence is flagged
- one expired supplier certificate metadata check is flagged
- one OCR supplier-name mismatch is flagged

### Passing Restaurant / Food Premise Dossier

```bash
python3 manage.py halal precheck run \
  --file examples/seri-melaka-restaurant.dossier.json \
  --ocr-dir examples/ocr/seri-melaka \
  --out-dir reports/seri-melaka \
  --pretty
```

Expected summary:

- `overall_status=pass`
- food-premise rules apply
- manufacturer-only rules such as manufacturing process flow do not apply
- KKM food-premise registration and menu evidence are checked

## Output Files

Each command writes:

- `precheck.json`
- `applicant-report.md`
- `reviewer-report.md`
- `applicant-report.html`
- `reviewer-report.html`

JSON is the canonical machine-readable output. Markdown and HTML are report views rendered from the same validation result.

## What This Does Not Claim

- It does not submit to MYeHALAL.
- It does not decide halal status.
- It does not replace JAKIM, MAIN, JAIN, or official reviewers.
- It does not use live GLM-OCR yet; the OCR artifacts are GLM-OCR-shaped verification examples so the validator contract is testable now.

## Internal Validation

The regression suite covers:

- passing manufacturer dossier evaluation
- failing manufacturer remediation output
- food-premise rule selection
- CLI report generation

Run:

```bash
python3 -m unittest discover -s tests -v
```
