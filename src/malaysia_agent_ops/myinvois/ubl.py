"""UBL 2.1 JSON in the shape MyInvois expects (every value wrapped as [{"_": value, ...attributes}]).

`build_document` returns the unsigned document. `serialize` gives the exact bytes that are hashed,
signed, base64-encoded and submitted, so the same bytes are used at every step.
"""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from .invoice import InvoiceInput, Party, Totals, compute_totals

NS = {
    "_D": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "_A": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "_B": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def v(value: Any, **attrs: Any) -> list[dict[str, Any]]:
    """Wrap a scalar the MyInvois JSON way."""
    return [{"_": value, **attrs}]


def amount(value: Decimal, currency: str) -> list[dict[str, Any]]:
    return v(float(value), currencyID=currency)


def _party(party: Party, *, supplier: bool) -> dict[str, Any]:
    identifications = [
        {"ID": v(party.tin, schemeID="TIN")},
        {"ID": v(party.id_value, schemeID=party.id_type)},
        {"ID": v(party.sst_number or "NA", schemeID="SST")},
        {"ID": v(party.tourism_tax_number or "NA", schemeID="TTX")},
    ]
    address: dict[str, Any] = {
        "CityName": v(party.address.city),
        "CountrySubentityCode": v(party.address.state_code),
        "AddressLine": [{"Line": v(line)} for line in party.address.lines],
        "Country": [{"IdentificationCode": v(party.address.country_code, listID="ISO3166-1", listAgencyID="6")}],
    }
    if party.address.postcode:
        address["PostalZone"] = v(party.address.postcode)
    contact: dict[str, Any] = {"Telephone": v(party.phone)}
    if party.email:
        contact["ElectronicMail"] = v(party.email)
    body: dict[str, Any] = {}
    if supplier:
        body["IndustryClassificationCode"] = v(party.msic_code, name=party.business_activity)
    body.update(
        {
            "PartyIdentification": identifications,
            "PostalAddress": [address],
            "PartyLegalEntity": [{"RegistrationName": v(party.name)}],
            "Contact": [contact],
        }
    )
    return {"Party": [body]}


def _tax_category(tax_type: str, exemption_reason: str | None) -> dict[str, Any]:
    category: dict[str, Any] = {
        "ID": v(tax_type),
        "TaxScheme": [{"ID": v("OTH", schemeID="UN/ECE 5153", schemeAgencyID="6")}],
    }
    if tax_type == "E" and exemption_reason:
        category["TaxExemptionReason"] = v(exemption_reason)
    return category


def build_document(invoice: InvoiceInput, issued_at: datetime, totals: Totals | None = None) -> dict[str, Any]:
    totals = totals or compute_totals(invoice)
    cur = invoice.currency
    issued = issued_at.astimezone(timezone.utc)
    doc: dict[str, Any] = {
        "ID": v(invoice.code_number),
        "IssueDate": v(issued.strftime("%Y-%m-%d")),
        "IssueTime": v(issued.strftime("%H:%M:%SZ")),
        "InvoiceTypeCode": v(invoice.document_type, listVersionID=invoice.version),
        "DocumentCurrencyCode": v(cur),
        "TaxCurrencyCode": v("MYR"),
    }
    if cur != "MYR" and invoice.exchange_rate is not None:
        doc["TaxExchangeRate"] = [
            {
                "SourceCurrencyCode": v(cur),
                "TargetCurrencyCode": v("MYR"),
                "CalculationRate": v(float(invoice.exchange_rate)),
            }
        ]
    if invoice.billing_period:
        period: dict[str, Any] = {
            "StartDate": v(invoice.billing_period.start.isoformat()),
            "EndDate": v(invoice.billing_period.end.isoformat()),
        }
        if invoice.billing_period.frequency:
            period["Description"] = v(invoice.billing_period.frequency)
        doc["InvoicePeriod"] = [period]
    if invoice.original_document:
        doc["BillingReference"] = [
            {
                "InvoiceDocumentReference": [
                    {
                        "ID": v(invoice.original_document.code_number),
                        "UUID": v(invoice.original_document.uuid),
                    }
                ]
            }
        ]
    doc["AccountingSupplierParty"] = [_party(invoice.supplier, supplier=True)]
    doc["AccountingCustomerParty"] = [_party(invoice.buyer, supplier=False)]
    if invoice.payment_mode:
        doc["PaymentMeans"] = [{"PaymentMeansCode": v(invoice.payment_mode)}]
    if invoice.payment_terms:
        doc["PaymentTerms"] = [{"Note": v(invoice.payment_terms)}]
    doc["TaxTotal"] = [
        {
            "TaxAmount": amount(totals.tax, cur),
            "TaxSubtotal": [
                {
                    "TaxableAmount": amount(sub.taxable, cur),
                    "TaxAmount": amount(sub.tax, cur),
                    "TaxCategory": [_tax_category(sub.tax_type, sub.exemption_reason)],
                }
                for sub in totals.tax_subtotals
            ],
        }
    ]
    doc["LegalMonetaryTotal"] = [
        {
            "LineExtensionAmount": amount(totals.line_extension, cur),
            "TaxExclusiveAmount": amount(totals.tax_exclusive, cur),
            "TaxInclusiveAmount": amount(totals.tax_inclusive, cur),
            "PayableAmount": amount(totals.payable, cur),
        }
    ]
    doc["InvoiceLine"] = [
        _line(index, item, line_totals, cur)
        for index, (item, line_totals) in enumerate(zip(invoice.lines, totals.lines, strict=True), start=1)
    ]
    return {**NS, "Invoice": [doc]}


def _line(index: int, item: Any, totals: Any, cur: str) -> dict[str, Any]:
    line: dict[str, Any] = {
        "ID": v(str(index)),
        "InvoicedQuantity": v(float(item.quantity), unitCode=item.unit_code),
        "LineExtensionAmount": amount(totals.line_extension, cur),
    }
    if item.discount_amount:
        line["AllowanceCharge"] = [
            {
                "ChargeIndicator": v(False),
                "AllowanceChargeReason": v("Discount"),
                "Amount": amount(item.discount_amount, cur),
            }
        ]
    subtotal: dict[str, Any] = {
        "TaxableAmount": amount(totals.line_extension, cur),
        "TaxAmount": amount(totals.tax, cur),
        "TaxCategory": [_tax_category(item.tax_type, item.tax_exemption_reason)],
    }
    if item.tax_amount is None:
        subtotal["Percent"] = v(float(item.tax_rate))
    line["TaxTotal"] = [{"TaxAmount": amount(totals.tax, cur), "TaxSubtotal": [subtotal]}]
    line["Item"] = [
        {
            "CommodityClassification": [{"ItemClassificationCode": v(item.classification_code, listID="CLASS")}],
            "Description": v(item.description),
        }
    ]
    line["Price"] = [{"PriceAmount": amount(item.unit_price, cur)}]
    line["ItemPriceExtension"] = [{"Amount": amount(totals.subtotal, cur)}]
    return line


def serialize(document: dict[str, Any]) -> bytes:
    """Minified UTF-8 JSON. These exact bytes are hashed, signed and submitted."""
    return json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def submission_entry(document_bytes: bytes, code_number: str) -> dict[str, str]:
    """One element of the `documents` array in a Submit Documents request."""
    return {
        "format": "JSON",
        "document": base64.b64encode(document_bytes).decode(),
        "documentHash": sha256_hex(document_bytes),
        "codeNumber": code_number,
    }
