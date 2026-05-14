# Applicant Halal Precheck Report

- Dossier: `barakah-curry-paste-incomplete-demo`
- Applicant: Barakah Foods Manufacturing Sdn Bhd
- Application type: `manufacturer`
- Product/menu: Instant Curry Paste
- Generated: `2026-05-14T01:55:02+00:00`

## Summary

- Overall status: `needs_remediation`
- Requirements passed: 10
- Requirements failed: 2
- Conditional requirements skipped: 0
- OCR matches: 1
- OCR mismatches: 1
- OCR low-confidence checks: 0
- Expired document metadata checks: 1

## Fix Before Submission

- `MY-HALAL-PROCESS-001` Manufacturing process flow: add one of `process_flow_chart, manufacturing_process`. Source: S1.
- `MY-HALAL-FINANCIAL-001` Latest company financial statement: add one of `financial_statement`. Source: S2.
- `docs/barakah/supplier-b-chili-cert-expired.pdf` has expired metadata: `2024-12-31`.
- OCR check for `docs/barakah/supplier-b-chili-cert-expired.pdf` returned `mismatch`.

## Requirement Coverage

| Status | Requirement | Evidence Class | Source | Matched Documents |
|---|---|---|---|---|
| `pass` | Company profile | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/company-profile.pdf |
| `pass` | Company or business registration | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/ssm.pdf |
| `pass` | PBT license or government support letter | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | docs/barakah/pbt-license.pdf |
| `pass` | Product name and description | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/product-description.pdf |
| `pass` | Ingredient or raw material list | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/ingredient-list.pdf |
| `pass` | Ingredient supplier or manufacturer details | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/supplier-list.pdf |
| `pass` | Ingredient halal certificates or critical ingredient specifications | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/supplier-a-coconut-cert.pdf, docs/barakah/supplier-b-chili-cert-expired.pdf |
| `pass` | Packaging material | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/packaging-material.pdf |
| `pass` | Product packaging label | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | docs/barakah/label.pdf |
| `fail` | Manufacturing process flow | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `pass` | Premise or factory location map | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | docs/barakah/location-map.pdf |
| `fail` | Latest company financial statement | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | - |

## Document Metadata Checks

| Document | Field | Declared | Status | As Of |
|---|---|---|---|---|
| `docs/barakah/supplier-a-coconut-cert.pdf` | `expiry_date` | 2026-12-31 | `valid` | 2026-05-14 |
| `docs/barakah/supplier-b-chili-cert-expired.pdf` | `expiry_date` | 2024-12-31 | `expired` | 2026-05-14 |

## OCR Metadata Verification

| Document | Status | Field | Declared | Observed | Confidence |
|---|---|---|---|---|---|
| `docs/barakah/location-map.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/company-profile.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/ssm.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/pbt-license.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/product-description.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/ingredient-list.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/label.pdf` | `not_evaluable` | - | - | - | - |
| `docs/barakah/supplier-a-coconut-cert.pdf` | `match` | `supplier_name` | Supplier A Sdn Bhd | Supplier A Sdn Bhd | 0.94 |
| `docs/barakah/supplier-a-coconut-cert.pdf` | `match` | `certificate_no` | JAKIM-2025-001 | JAKIM-2025-001 | 0.91 |
| `docs/barakah/supplier-a-coconut-cert.pdf` | `match` | `issuing_body` | JAKIM | JAKIM | 0.88 |
| `docs/barakah/supplier-a-coconut-cert.pdf` | `match` | `expiry_date` | 2026-12-31 | 2026-12-31 | 0.87 |
| `docs/barakah/supplier-b-chili-cert-expired.pdf` | `mismatch` | `supplier_name` | Supplier B Sdn Bhd | Supplier Bee Sdn Bhd | 0.93 |
| `docs/barakah/supplier-b-chili-cert-expired.pdf` | `match` | `certificate_no` | JAKIM-2023-099 | JAKIM-2023-099 | 0.89 |
| `docs/barakah/supplier-b-chili-cert-expired.pdf` | `match` | `issuing_body` | JAKIM | JAKIM | 0.86 |
| `docs/barakah/supplier-b-chili-cert-expired.pdf` | `match` | `expiry_date` | 2024-12-31 | 2024-12-31 | 0.85 |
