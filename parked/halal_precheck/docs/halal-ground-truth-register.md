# Halal Ground Truth Register

## Purpose

This register keeps the halal product direction tied to evidence instead of assumptions.

Every halal workflow, CLI action, checklist, and demo object should map to one of these evidence classes:

- `official_requirement`: stated by JAKIM, Halal Malaysia, MYeHALAL, MAIN, JAIN, HDC, or another competent authority.
- `official_guidance`: operational guidance or announcements from an official or regulator-adjacent source.
- `interview_observation`: learned from halal consultants, applicants, auditors, manufacturers, food premises, or authority-side operators.
- `product_assumption`: a working hypothesis that has not yet been validated.

The product should not present `product_assumption` items as official requirements.

## Product Scope Decision

Current scope:

- halal dossier preparation and internal pre-check for Malaysian halal certification workflows
- applicant-side evidence readiness for manufacturers and food premises
- reviewer-style query and response loops for internal pre-check
- Malaysia tax and e-invoicing workflows through LHDN/MyInvois as the adjacent compliance rail

Out of core scope:

- CIDB/construction workflows
- claims of sanctioned MYeHALAL write-side integration
- claims of replacing JAKIM, MAIN, JAIN, or official certification decisions

CIDB may remain as an adapter experiment, but it should not be treated as a product pillar while the core wedge is halal plus tax.

## Source Register

| ID | Source | Type | Notes |
|---|---|---|---|
| S1 | Halal Malaysia Portal, procedure page: https://myehalal.halal.gov.my/portal-halal/v1/index.php?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D&utama=panduan&view=%27 | official_guidance | Lists eligible applicant categories, online application route, key application documents, and food-premise definitions. |
| S2 | Halal Malaysia Portal, 2021 document filing announcement: https://myehalal.halal.gov.my/portal-halal/v1/index.php?content_id=20210310604821a5189e3&data=bW9kdWxlcy9jb250ZW50X2RldGFpbHM7Ozs%3D&page_title=Announcement | official_guidance | Gives a concrete supporting-document filing sequence for JAKIM-reviewed SPHM applications. |
| S3 | JAKIM media statement on MyHALALINGREDIENTS, 14 August 2025: https://www.islam.gov.my/en/media-statement/4798-kenyataan-media-jabatan-kemajuan-islam-malaysia-jakim-berkenaan-pelaksanaan-myhalalingredients | official_guidance | Announces MyHALALINGREDIENTS effective 15 August 2025 for raw-material data recording and evaluation, integrated with MYeHALAL. |
| S4 | JAKIM media statement on SPHM e-Cert, 8 May 2025: https://www.islam.gov.my/en/media-statement/4704-kenyataan-media-ketua-pengarah-jabatan-kemajuan-islam-malaysia-berkenaan-pelaksanaan-sijil-pengesahan-halal-malaysia-sphm-secara-elektronik-e-cert | official_guidance | Announces electronic SPHM issuance for approvals from 5 May 2025 onward. |
| S5 | JAKIM media statement on SPHM processing clarification, 25 July 2025: https://www.islam.gov.my/ms/kenyataan-media/4780-kenyataan-media-jabatan-kemajuan-islam-malaysia-jakim-berkenaan-dakwaan-kelewatan-pemprosesan-permohonan-sijil-pengesahan-halal-malaysia-sphm-yang-timbul-susulan-laporan-ketua-audit-negara | official_guidance | Highlights the importance of company-side PIC readiness and training in certification operations. |

## Officially Grounded Product Objects

| Object | Evidence Class | Source | Product Implication |
|---|---|---|---|
| Applicant company | official_guidance | S1, S2 | The CLI needs a company profile object and business registration evidence. |
| Application/dossier | official_guidance | S1, S2 | The main workflow object should be the dossier/application, not only a company or product. |
| Manufacturer/producer applicant type | official_guidance | S1 | The first demo can credibly target a food manufacturer product dossier. |
| Food premise applicant type | official_guidance | S1 | A restaurant or food-service pre-check is a valid secondary workflow. |
| Product/menu to be certified | official_guidance | S1, S2 | The model must support both product-level and menu/food-premise certification contexts. |
| Ingredients/raw materials | official_guidance | S1, S2, S3 | The CLI should model ingredient lists and raw-material evidence as first-class data. |
| Supplier/manufacturer details | official_guidance | S1 | Supplier identity and supplier location should be linked to ingredients. |
| Ingredient halal certificate or specification | official_guidance | S1, S2 | Evidence checks should flag missing supplier certificates or specs for critical ingredients. |
| Packaging material and product label | official_guidance | S1, S2 | Packaging and label artifacts belong in the dossier evidence map. |
| Manufacturing process or process flow | official_guidance | S1, S2 | A product dossier needs a process-flow artifact, especially for manufacturing. |
| Premise/factory location map | official_guidance | S1 | Premise and location evidence should be separate from company evidence. |
| SSM/business registration | official_guidance | S2 | The dossier should include business registration checks and file presence. |
| PBT license or government support letter | official_guidance | S2 | Food-premise and product workflows need a local-license evidence slot. |
| Muslim worker identity / employer confirmation by scheme | official_guidance | S2 | Do not hard-code the rule globally; model it as scheme-specific evidence to validate through interviews. |
| Financial statement | official_guidance | S2 | A document slot exists, but the product should validate the exact requirement by scheme and applicant type. |
| OEM agreement | official_guidance | S2 | OEM/private-label manufacturing should become a later workflow branch. |
| KKM food-premise registration | official_guidance | S2 | Restaurant and food-premise workflows need a KKM registration evidence slot. |
| MyHALALINGREDIENTS raw-material record | official_guidance | S3 | Ingredient registry and repeated-document reduction are real product opportunities. |
| SPHM e-Cert | official_guidance | S4 | Certification status and post-approval certificate retrieval/printing should be tracked, but not claimed as a current connector. |
| Company-side PIC / halal executive readiness | official_guidance | S5 | Discovery should test whether PIC readiness, training, and handover are recurring workflow pain points. |

## CLI Action Implications

These are product direction candidates, not all current implementation claims.

| Candidate Action | Evidence Class | Why It Exists |
|---|---|---|
| `halal.dossiers.create` | official_guidance | Applications are submitted with supporting documents and should be represented as a workflow object. |
| `halal.dossiers.validate` | official_guidance | Required documents can be checked before official submission or internal review. |
| `halal.documents.attach` | official_guidance | The official process depends on supporting document completeness. |
| `halal.ingredients.register` | official_guidance | MyHALALINGREDIENTS makes raw-material recording a clear product primitive. |
| `halal.suppliers.verify` | official_guidance | Supplier/manufacturer details and ingredient halal status are required application inputs. |
| `halal.bom.graph.generate` | product_assumption | Useful for manufacturing traceability, but the exact graph shape must be validated with consultants and applicants. |
| `halal.precheck.restaurant` | official_guidance + product_assumption | Food premises are official applicant types; the actual restaurant readiness checklist needs interview validation. |
| `halal.reviewer.query.create` | product_assumption | Query/response loops are likely useful, but the actual authority-side workflow needs interview validation. |
| `halal.reviewer.query.respond` | product_assumption | Same as above; keep framed as internal pre-check until validated. |
| `halal.dossiers.export` | official_guidance + product_assumption | Document filing and e-Cert direction support structured output; exact export format needs interview validation. |

## Discovery Backlog

Use this backlog before adding new halal product behavior.

### Consultants

- Which documents are most often missing for food manufacturers?
- Which documents are most often missing for restaurants or food premises?
- How do consultants currently map raw materials to supplier certificates?
- How do consultants detect expired or mismatched supplier certificates?
- What is the most painful MYeHALAL step before submission?
- What evidence is usually duplicated across repeat applications?
- How does MyHALALINGREDIENTS change the current workflow in practice?
- What does a useful pre-check report look like before a client submits?

### Applicants

- Who owns the halal application internally?
- How are company, premise, product, supplier, ingredient, and label documents stored today?
- How often do supplier certificates need refreshing?
- What causes rework after submission?
- Which parts are handled by staff versus external consultants?
- For restaurants, how does menu change management affect certification readiness?

### Authority-Side Or Reviewer-Side Operators

- What makes an application obviously incomplete?
- What are common query categories?
- Which evidence fields should be standardized before review?
- What should an internal pre-check never claim to decide?
- Which reviewer notes or decisions must remain outside third-party software?

## Guardrails

- Do not claim the product submits to MYeHALAL unless sanctioned access or a permitted integration path is confirmed.
- Do not claim the product determines halal status; it can prepare, validate, organize, and pre-check evidence.
- Do not hard-code one checklist across all schemes. Manufacturer, food premise, OEM, logistics, cosmetics, and slaughterhouse workflows differ.
- Keep tax/MyInvois as an adjacent compliance rail, not a reason to dilute the halal workflow model.
- Keep CIDB out of core product positioning unless the project direction changes again.

## Next Product Step

Build the first validated demo around:

`one food manufacturer preparing a product halal dossier for internal pre-check`

Secondary demo:

`one restaurant or food premise running halal readiness pre-check before official application`

Both demos should emit an evidence report where every requirement is tagged with its source class.
