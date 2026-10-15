# Halal dossier precheck (parked)

Parked from v0 while the product focuses on MyInvois. It is standalone: no imports from the main package and no dependencies beyond the Python standard library.

What it does: checks a JSON dossier against 15 source-tagged rules in `halal_requirements.json`, compares declared certificate fields with OCR output, flags expired documents, and writes applicant and reviewer reports (JSON, Markdown, HTML).

What it does not do: it never opens the documents themselves. A rule passes if a document of the declared kind is listed. The sample "OCR" files under `examples/ocr/` are hand-written JSON, not real OCR output. Only two official sources back the rules so far (see `docs/halal-ground-truth-register.md`).

Run:

```bash
python3 parked/halal_precheck/halal_precheck.py \
  --file parked/halal_precheck/examples/barakah-curry-paste.dossier.json \
  --ocr-dir parked/halal_precheck/examples/ocr/barakah \
  --out-dir /tmp/halal-report \
  --as-of 2026-06-01
```

Test:

```bash
python3 -m unittest discover -s parked/halal_precheck -p "test_*.py"
```

Why parked: JAKIM has no halal-verification API, the rule sourcing is thin, and JAKIM's MYeHALAL 2.0 AI screening may absorb pre-screening. Revisit after the MyInvois product has paying customers.
