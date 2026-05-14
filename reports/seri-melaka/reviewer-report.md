# Reviewer Halal Precheck Report

- Dossier: `seri-melaka-restaurant-demo`
- Applicant: Seri Melaka Bistro Sdn Bhd
- Application type: `food_premise`
- Product/menu: Seri Melaka Bistro Main Menu
- Generated: `2026-05-14T01:55:02+00:00`

## Summary

- Overall status: `pass`
- Requirements passed: 10
- Requirements failed: 0
- Conditional requirements skipped: 0
- OCR matches: 1
- OCR mismatches: 0
- OCR low-confidence checks: 0
- Expired document metadata checks: 0

## Dossier Inventory

| Kind | Path | Metadata Fields |
|---|---|---|
| `premise_location_map` | `docs/seri-melaka/location-map.pdf` | premise_name |
| `company_profile` | `docs/seri-melaka/company-profile.pdf` | company_name |
| `ssm_certificate` | `docs/seri-melaka/ssm.pdf` | company_name, registration_no |
| `pbt_license` | `docs/seri-melaka/dbkl-license.pdf` | expiry_date, license_holder |
| `kkm_food_premise_registration` | `docs/seri-melaka/kkm-food-premise-registration.pdf` | expiry_date, premise_name |
| `menu_description` | `docs/seri-melaka/menu.pdf` | menu_name |
| `ingredient_list` | `docs/seri-melaka/menu-ingredient-list.pdf` | menu_name |
| `supplier_list` | `docs/seri-melaka/supplier-list.pdf` | - |
| `financial_statement` | `docs/seri-melaka/financial-statement.pdf` | - |
| `ingredient_halal_certificate` | `docs/seri-melaka/supplier-c-stock-cert.pdf` | certificate_no, covers, expiry_date, issuing_body, supplier_name |

## Requirement Matrix

| Requirement | Status | Severity | Evidence Class | Source | Missing Kinds |
|---|---|---|---|---|---|
| `MY-HALAL-APP-COMPANY-001` Company profile | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-APP-SSM-001` Company or business registration | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-APP-PBT-001` PBT license or government support letter | `pass` | `required` | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | - |
| `MY-HALAL-FOODPREM-MENU-001` Menu for certification | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-INGREDIENTS-001` Ingredient or raw material list | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-SUPPLIER-001` Ingredient supplier or manufacturer details | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-INGREDIENT-CERT-001` Ingredient halal certificates or critical ingredient specifications | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-PREMISE-MAP-001` Premise or factory location map | `pass` | `required` | `official_guidance` | [S1](https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27) | - |
| `MY-HALAL-FINANCIAL-001` Latest company financial statement | `pass` | `required` | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | - |
| `MY-HALAL-KKM-FOODPREM-001` KKM food premise registration | `pass` | `required` | `official_guidance` | [S2](https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement) | - |

## Document Metadata Checks

| Document | Field | Declared | Status | As Of |
|---|---|---|---|---|
| `docs/seri-melaka/dbkl-license.pdf` | `expiry_date` | 2027-03-31 | `valid` | 2026-05-14 |
| `docs/seri-melaka/kkm-food-premise-registration.pdf` | `expiry_date` | 2027-05-31 | `valid` | 2026-05-14 |
| `docs/seri-melaka/supplier-c-stock-cert.pdf` | `expiry_date` | 2027-01-31 | `valid` | 2026-05-14 |

## OCR Metadata Verification

| Document | Status | Field | Declared | Observed | Confidence |
|---|---|---|---|---|---|
| `docs/seri-melaka/location-map.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/company-profile.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/ssm.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/dbkl-license.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/kkm-food-premise-registration.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/menu.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/menu-ingredient-list.pdf` | `not_evaluable` | - | - | - | - |
| `docs/seri-melaka/supplier-c-stock-cert.pdf` | `match` | `supplier_name` | Supplier C Sdn Bhd | Supplier C Sdn Bhd | 0.93 |
| `docs/seri-melaka/supplier-c-stock-cert.pdf` | `match` | `certificate_no` | JAKIM-2026-010 | JAKIM-2026-010 | 0.91 |
| `docs/seri-melaka/supplier-c-stock-cert.pdf` | `match` | `issuing_body` | JAKIM | JAKIM | 0.89 |
| `docs/seri-melaka/supplier-c-stock-cert.pdf` | `match` | `expiry_date` | 2027-01-31 | 2027-01-31 | 0.86 |
