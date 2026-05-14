# Reviewer Halal Precheck Report

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

## Dossier Inventory

| Kind | Path | Metadata Fields |
|---|---|---|
| `premise_location_map` | `docs/barakah/location-map.pdf` | premise_name |
| `company_profile` | `docs/barakah/company-profile.pdf` | company_name |
| `ssm_certificate` | `docs/barakah/ssm.pdf` | company_name, registration_no |
| `pbt_license` | `docs/barakah/pbt-license.pdf` | license_holder |
| `product_description` | `docs/barakah/product-description.pdf` | product_name |
| `ingredient_list` | `docs/barakah/ingredient-list.pdf` | product_name |
| `supplier_list` | `docs/barakah/supplier-list.pdf` | - |
| `packaging_material` | `docs/barakah/packaging-material.pdf` | - |
| `packaging_label` | `docs/barakah/label.pdf` | product_name |
| `ingredient_halal_certificate` | `docs/barakah/supplier-a-coconut-cert.pdf` | certificate_no, covers, expiry_date, issuing_body, supplier_name |
| `ingredient_halal_certificate` | `docs/barakah/supplier-b-chili-cert-expired.pdf` | certificate_no, covers, expiry_date, issuing_body, supplier_name |

## Requirement Matrix

| Requirement | Status | Severity | Evidence Class | Source | Missing Kinds |
|---|---|---|---|---|---|
| `MY-HALAL-APP-COMPANY-001` Company profile | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-APP-SSM-001` Company or business registration | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-APP-PBT-001` PBT license or government support letter | `pass` | `required` | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | - |
| `MY-HALAL-APP-PRODUCT-001` Product name and description | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-INGREDIENTS-001` Ingredient or raw material list | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-SUPPLIER-001` Ingredient supplier or manufacturer details | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-INGREDIENT-CERT-001` Ingredient halal certificates or critical ingredient specifications | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-PACKAGING-001` Packaging material | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-LABEL-001` Product packaging label | `pass` | `required` | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | - |
| `MY-HALAL-PROCESS-001` Manufacturing process flow | `fail` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | process_flow_chart, manufacturing_process |
| `MY-HALAL-PREMISE-MAP-001` Premise or factory location map | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-FINANCIAL-001` Latest company financial statement | `fail` | `required` | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | financial_statement |

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
