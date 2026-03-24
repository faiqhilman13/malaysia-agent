from __future__ import annotations


BUSINESS_FIXTURES = [
    {
        "tin": "C1234567801",
        "registration_no": "202401000001",
        "name": "ACME TRADING SDN BHD",
        "industry": "Accounting software",
        "tax_active": True,
        "business_registry_status": "active",
        "aliases": ["Acme", "Acme Trading"],
    },
    {
        "tin": "C1234567802",
        "registration_no": "201901234567",
        "name": "PENANG ELECTRONICS SDN BHD",
        "industry": "Manufacturing",
        "tax_active": True,
        "business_registry_status": "active",
        "aliases": ["Penang Electronics", "PESB"],
    },
    {
        "tin": "C1234567803",
        "registration_no": "202201112233",
        "name": "BARAKAH FOODS MANUFACTURING SDN BHD",
        "industry": "Food manufacturing",
        "tax_active": True,
        "business_registry_status": "active",
        "aliases": ["Barakah Foods", "Barakah Manufacturing"],
    },
    {
        "tin": "C1234567804",
        "registration_no": "201801998877",
        "name": "NUSA LOGISTICS SDN BHD",
        "industry": "Logistics",
        "tax_active": True,
        "business_registry_status": "active",
        "aliases": ["Nusa Logistics", "Nusa"],
    },
    {
        "tin": "C1234567805",
        "registration_no": "201701122334",
        "name": "LEGACY SUPPLIES SDN BHD",
        "industry": "Wholesale trade",
        "tax_active": False,
        "business_registry_status": "struck_off",
        "aliases": ["Legacy Supplies"],
    },
]


HALAL_FIXTURES = [
    {
        "certificate_ref": "JAKIM-2025-0001",
        "company_tin": "C1234567803",
        "company_name": "BARAKAH FOODS MANUFACTURING SDN BHD",
        "status": "active",
        "expiry_date": "2027-06-30",
        "products": ["Instant curry paste", "Frozen ready meals"],
    },
    {
        "certificate_ref": "JAKIM-2024-0110",
        "company_tin": "C1234567801",
        "company_name": "ACME TRADING SDN BHD",
        "status": "active",
        "expiry_date": "2026-12-31",
        "products": ["Food packaging"],
    },
    {
        "certificate_ref": "JAKIM-2023-0999",
        "company_tin": "C1234567805",
        "company_name": "LEGACY SUPPLIES SDN BHD",
        "status": "expired",
        "expiry_date": "2025-01-31",
        "products": ["Gelatine additive"],
    },
]


TRADE_DOC_RULES = {
    "import_k1": [
        "commercial_invoice",
        "packing_list",
        "hs_code",
        "consignee",
        "country_of_origin",
    ],
    "export_k2": [
        "commercial_invoice",
        "packing_list",
        "hs_code",
        "consignee",
        "incoterm",
    ],
    "permit_application": [
        "commercial_invoice",
        "packing_list",
        "hs_code",
        "permit_type",
    ],
}


HALAL_REQUIRED_SUPPORTING_DOCUMENTS = [
    "business_registration",
    "product_specification",
    "ingredient_declarations",
]


HALAL_FRAMEWORK_RULES = {
    "IHCS": [
        "halal_policy",
        "ingredient_register",
        "supplier_certificate_control",
        "traceability_log",
        "staff_training",
    ],
    "HAS": [
        "halal_policy",
        "halal_committee",
        "ingredient_register",
        "supplier_certificate_control",
        "traceability_log",
        "internal_audit_program",
        "corrective_action_register",
        "staff_training",
    ],
}


HALAL_WORKFLOW_STAGES = [
    "intake",
    "supplier_registry",
    "ingredient_review",
    "evidence_assembly",
    "internal_review",
    "audit_queries",
    "ready_for_submission",
    "submitted",
    "certified",
]


HALAL_FNB_PILOT_DATASET = {
    "pilot_id": "barakah-fnb-pilot",
    "sector": "Food and beverage",
    "applicant": {
        "name": "Barakah Foods Manufacturing Sdn Bhd",
        "company_size": "medium",
        "scheme": "food_and_beverage",
        "framework": "HAS",
        "product_name": "Instant curry paste",
        "product_sku": "ICP-450",
        "target_markets": ["United Arab Emirates", "Indonesia", "Singapore"],
        "supporting_documents": [
            "business_registration",
            "product_specification",
            "ingredient_declarations",
            "halal_policy",
            "traceability_log",
        ],
        "completed_controls": [
            "halal_policy",
            "halal_committee",
            "ingredient_register",
            "supplier_certificate_control",
            "traceability_log",
            "internal_audit_program",
            "corrective_action_register",
            "staff_training",
        ],
    },
    "suppliers": [
        {
            "supplier_id": "pilot:seri-rasa-spice",
            "supplier_tin": "C1234567810",
            "supplier_name": "Seri Rasa Spice Industries Sdn Bhd",
            "certificate_ref": "JAKIM-PILOT-1001",
            "certificate_status": "active",
            "expiry_date": "2026-10-15",
            "products": ["Spice blend", "Chili concentrate"],
            "notes": "Primary spice concentrator for the curry paste line.",
        },
        {
            "supplier_id": "pilot:santan-nusantara",
            "supplier_tin": "C1234567811",
            "supplier_name": "Santan Nusantara Ingredients Sdn Bhd",
            "certificate_ref": "JAKIM-PILOT-1002",
            "certificate_status": "active",
            "expiry_date": "2026-08-31",
            "products": ["Coconut milk powder"],
            "notes": "Secondary ingredient supplier with upcoming renewal risk.",
        },
        {
            "supplier_id": "pilot:acme-packaging",
            "supplier_tin": "C1234567801",
            "supplier_name": "ACME TRADING SDN BHD",
            "certificate_ref": "JAKIM-2024-0110",
            "certificate_status": "active",
            "expiry_date": "2026-12-31",
            "products": ["Food packaging"],
            "notes": "Packaging supplier already present in seeded halal directory.",
        },
    ],
    "bom": [
        {
            "ingredient": "Spice blend",
            "ingredient_code": "ING-SPICE-01",
            "supplier_tin": "C1234567810",
            "supplier_name": "Seri Rasa Spice Industries Sdn Bhd",
        },
        {
            "ingredient": "Coconut milk powder",
            "ingredient_code": "ING-COCO-02",
            "supplier_tin": "C1234567811",
            "supplier_name": "Santan Nusantara Ingredients Sdn Bhd",
        },
        {
            "ingredient": "Retort pouch packaging",
            "ingredient_code": "ING-PACK-03",
            "supplier_tin": "C1234567801",
            "supplier_name": "ACME TRADING SDN BHD",
        },
    ],
    "audit_query": {
        "query_title": "Upload latest coconut ingredient declaration",
        "query_text": "Provide the refreshed ingredient declaration and updated renewal acknowledgement for coconut milk powder.",
        "requested_documents": [
            "coconut_ingredient_declaration",
            "renewal_acknowledgement_letter",
        ],
        "severity": "medium",
    },
    "audit_response": {
        "response_summary": "Updated coconut ingredient declaration and renewal acknowledgement provided.",
        "attachments": [
            "coconut_ingredient_declaration_v2.pdf",
            "renewal_acknowledgement_letter.pdf",
        ],
    },
    "document_share": {
        "share_target": "oem_partner",
        "documents": ["export_dossier.pdf", "supplier_matrix.xlsx", "audit_response_bundle.zip"],
        "recipients": ["quality@oem.example", "ops@oem.example"],
        "channel": "secure_link",
        "note": "Pilot dossier shared with OEM quality and operations teams.",
    },
}
