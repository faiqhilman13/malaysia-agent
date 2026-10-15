"""MyInvois code lists (from the LHDN SDK code tables). Re-check against the SDK when LHDN updates them."""

from __future__ import annotations

DOCUMENT_TYPES: dict[str, str] = {
    "01": "Invoice",
    "02": "Credit Note",
    "03": "Debit Note",
    "04": "Refund Note",
    "11": "Self-billed Invoice",
    "12": "Self-billed Credit Note",
    "13": "Self-billed Debit Note",
    "14": "Self-billed Refund Note",
}
# Types that adjust an earlier document and must reference it.
ADJUSTMENT_TYPES = {"02", "03", "04", "12", "13", "14"}
SELF_BILLED_TYPES = {"11", "12", "13", "14"}

# Document versions (InvoiceTypeCode listVersionID). 1.1 and the signed SVDP version need a digital signature.
# SVDP versions (added July 2026) are only for the Special Voluntary Disclosure Programme, 7 Jul 2026 - 31 Dec 2027.
VERSIONS: dict[str, dict[str, bool]] = {
    "1.0": {"signed": False, "svdp": False},
    "1.1": {"signed": True, "svdp": False},
    "1.2": {"signed": False, "svdp": True},
    "1.3": {"signed": True, "svdp": True},
}

TAX_TYPES: dict[str, str] = {
    "01": "Sales Tax",
    "02": "Service Tax",
    "03": "Tourism Tax",
    "04": "High-Value Goods Tax",
    "05": "Sales Tax on Low Value Goods",
    "06": "Not Applicable",
    "E": "Tax exemption (where applicable)",
}

STATE_CODES: dict[str, str] = {
    "01": "Johor",
    "02": "Kedah",
    "03": "Kelantan",
    "04": "Melaka",
    "05": "Negeri Sembilan",
    "06": "Pahang",
    "07": "Pulau Pinang",
    "08": "Perak",
    "09": "Perlis",
    "10": "Selangor",
    "11": "Terengganu",
    "12": "Sabah",
    "13": "Sarawak",
    "14": "Wilayah Persekutuan Kuala Lumpur",
    "15": "Wilayah Persekutuan Labuan",
    "16": "Wilayah Persekutuan Putrajaya",
    "17": "Not Applicable",
}

ID_TYPES = {"BRN", "NRIC", "PASSPORT", "ARMY"}

PAYMENT_MODES: dict[str, str] = {
    "01": "Cash",
    "02": "Cheque",
    "03": "Bank Transfer",
    "04": "Credit Card",
    "05": "Debit Card",
    "06": "e-Wallet / Digital Wallet",
    "07": "Digital Bank",
    "08": "Others",
}

# Classification codes run 001-045 in the SDK table. Only the ones this code relies on are named here.
CLASSIFICATION_CONSOLIDATED = "004"
CLASSIFICATION_OTHERS = "022"
CLASSIFICATION_CODES = {f"{n:03d}" for n in range(1, 46)}

# General TINs for parties without a Malaysian TIN.
GENERAL_TIN_PUBLIC = "EI00000000010"
GENERAL_TIN_FOREIGN_BUYER = "EI00000000020"
GENERAL_TIN_FOREIGN_SUPPLIER = "EI00000000030"
GENERAL_TIN_GOVERNMENT = "EI00000000040"
GENERAL_TINS = {GENERAL_TIN_PUBLIC, GENERAL_TIN_FOREIGN_BUYER, GENERAL_TIN_FOREIGN_SUPPLIER, GENERAL_TIN_GOVERNMENT}

# Intermediary permissions, mirroring the toggles a director grants in the MyInvois portal.
PERMISSIONS = ("view_documents", "submit_documents", "cancel_documents", "reject_documents")

# Since 1 Jan 2026 a single transaction above this amount needs its own e-invoice, not a consolidated one.
CONSOLIDATION_LIMIT_MYR = 10_000

# Cancel (supplier) and reject (buyer) are only possible within 72 hours of validation.
CANCEL_WINDOW_HOURS = 72
# The issue date-time must be no more than 72 hours before submission.
ISSUE_WINDOW_HOURS = 72

# Submission limits from the SDK.
MAX_DOCUMENTS_PER_SUBMISSION = 100
MAX_DOCUMENT_BYTES = 300 * 1024
MAX_SUBMISSION_BYTES = 5 * 1024 * 1024
