"""The invoice an agent describes, validated and totalled before any UBL is generated.

The model covers the fields MyInvois marks mandatory plus the common optional ones. Field-level checks
here catch the documented pitfalls (TIN format, state codes, missing references on notes) before a
submission burns rate limit.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from . import codes

CENT = Decimal("0.01")
_TIN = re.compile(r"^(?:IG\d{9,11}|EI\d{11}|(?:C|CS|D|E|F|FA|PT|TA|TC|TN|TR|TP|J|LE)\d{8,12})$")
_PHONE = re.compile(r"^\+?\d{8,15}$")

Money = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def normalise_tin(value: str) -> str:
    return re.sub(r"[\s-]", "", value).upper()


def is_valid_tin(value: str) -> bool:
    return bool(_TIN.match(normalise_tin(value)))


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Address(_Strict):
    lines: list[str] = Field(min_length=1, max_length=3, description="1-3 address lines.")
    city: str = Field(min_length=1, max_length=50)
    postcode: str | None = Field(default=None, max_length=10)
    state_code: str = Field(description="MyInvois state code, 01-17 (14 = Kuala Lumpur, 17 = not applicable).")
    country_code: str = Field(default="MYS", description="ISO 3166-1 alpha-3.")

    @field_validator("state_code")
    @classmethod
    def _state(cls, v: str) -> str:
        if v not in codes.STATE_CODES:
            raise ValueError(f"unknown state code {v!r}; use 01-17")
        return v

    @field_validator("country_code")
    @classmethod
    def _country(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Z]{3}", v.upper()):
            raise ValueError("country_code must be ISO 3166-1 alpha-3, e.g. MYS")
        return v.upper()


class Party(_Strict):
    name: str = Field(min_length=1, max_length=300, description="Registered name.")
    tin: str = Field(description="LHDN TIN, e.g. C25845632020 or IG12345678901. General TINs start with EI.")
    id_type: Literal["BRN", "NRIC", "PASSPORT", "ARMY"]
    id_value: str = Field(description="12-digit SSM number for BRN, 12-digit NRIC, or passport/army number.")
    sst_number: str = Field(default="NA", description="SST registration number, or NA.")
    tourism_tax_number: str = Field(default="NA", description="Tourism tax registration number, or NA.")
    address: Address
    phone: str = Field(description="Contact number, digits with optional leading +. NA only for general TINs.")
    email: str | None = None
    msic_code: str | None = Field(default=None, description="5-digit MSIC code. Required for the supplier.")
    business_activity: str | None = Field(default=None, description="Business activity description. Supplier only.")

    @field_validator("tin")
    @classmethod
    def _tin(cls, v: str) -> str:
        v = normalise_tin(v)
        if not _TIN.match(v):
            raise ValueError(f"{v!r} is not a valid TIN format")
        return v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        v = re.sub(r"[\s()-]", "", v)
        if v.upper() == "NA":
            return "NA"
        if not _PHONE.match(v):
            raise ValueError("phone must be 8-15 digits with an optional leading +")
        return v

    @field_validator("msic_code")
    @classmethod
    def _msic(cls, v: str | None) -> str | None:
        if v is not None and not re.fullmatch(r"\d{5}", v):
            raise ValueError("msic_code must be 5 digits")
        return v

    @model_validator(mode="after")
    def _ids(self) -> Party:
        general = self.tin in codes.GENERAL_TINS
        value = re.sub(r"[\s-]", "", self.id_value).upper()
        if value == "NA" or (general and value in ("000000000000", "")):
            if not general:
                raise ValueError("id_value NA is only allowed with a general TIN (EI...)")
        elif self.id_type in ("BRN", "NRIC") and not re.fullmatch(r"\d{12}", value):
            raise ValueError(f"{self.id_type} must be 12 digits (new SSM format for BRN)")
        self.id_value = value
        if self.phone == "NA" and not general:
            raise ValueError("phone NA is only allowed with a general TIN")
        return self


class LineItem(_Strict):
    description: str = Field(min_length=1, max_length=300)
    classification_code: str = Field(description="MyInvois classification code 001-045 (022 = Others).")
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=6)
    unit_price: Decimal = Field(ge=0, max_digits=18, decimal_places=6)
    unit_code: str = Field(default="C62", description="UN/ECE rec 20 unit code; C62 = one (unit).")
    discount_amount: Money = Decimal("0")
    tax_type: str = Field(
        default="06", description="01 sales, 02 service, 03 tourism, 04 HVGT, 05 LVG, 06 n/a, E exempt."
    )
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, description="Percent, e.g. 8 for 8%.")
    tax_amount: Money | None = Field(default=None, description="Override for fixed-rate taxes (e.g. tourism tax).")
    tax_exemption_reason: str | None = Field(default=None, max_length=300)

    @field_validator("classification_code")
    @classmethod
    def _class(cls, v: str) -> str:
        if v not in codes.CLASSIFICATION_CODES:
            raise ValueError("classification_code must be 001-045")
        return v

    @field_validator("tax_type")
    @classmethod
    def _tax_type(cls, v: str) -> str:
        if v not in codes.TAX_TYPES:
            raise ValueError(f"unknown tax_type {v!r}")
        return v

    @model_validator(mode="after")
    def _exemption(self) -> LineItem:
        if self.tax_type == "E" and not self.tax_exemption_reason:
            raise ValueError("tax_exemption_reason is required when tax_type is E")
        if self.discount_amount > self.quantity * self.unit_price:
            raise ValueError("discount_amount exceeds the line subtotal")
        return self


class BillingPeriod(_Strict):
    start: date
    end: date
    frequency: str | None = Field(default=None, description="e.g. Monthly")

    @model_validator(mode="after")
    def _order(self) -> BillingPeriod:
        if self.end < self.start:
            raise ValueError("billing period ends before it starts")
        return self


class DocumentReference(_Strict):
    code_number: str = Field(description="The original document's invoice number.")
    uuid: str = Field(description="The original document's MyInvois UUID (use NA if it was never e-invoiced).")


class InvoiceInput(_Strict):
    document_type: str = Field(
        default="01", description="01 invoice, 02 credit, 03 debit, 04 refund; 11-14 self-billed."
    )
    version: str = Field(default="1.0", description="1.0 unsigned, 1.1 signed; 1.2/1.3 for SVDP catch-up only.")
    code_number: str = Field(min_length=1, max_length=50, description="Your invoice number.")
    issued_at: datetime | None = Field(default=None, description="Defaults to now. Must be within 72h of submission.")
    currency: str = Field(default="MYR", min_length=3, max_length=3)
    exchange_rate: Decimal | None = Field(default=None, gt=0, description="MYR per unit; required if currency != MYR.")
    supplier: Party
    buyer: Party
    lines: list[LineItem] = Field(min_length=1, max_length=1000)
    billing_period: BillingPeriod | None = None
    original_document: DocumentReference | None = Field(default=None, description="Required for notes (02-04, 12-14).")
    payment_mode: str | None = Field(default=None, description="01 cash ... 08 others.")
    payment_terms: str | None = Field(default=None, max_length=300)

    @field_validator("document_type")
    @classmethod
    def _doctype(cls, v: str) -> str:
        if v not in codes.DOCUMENT_TYPES:
            raise ValueError(f"unknown document_type {v!r}")
        return v

    @field_validator("version")
    @classmethod
    def _version(cls, v: str) -> str:
        if v not in codes.VERSIONS:
            raise ValueError("version must be 1.0, 1.1, 1.2 or 1.3")
        return v

    @field_validator("currency")
    @classmethod
    def _currency(cls, v: str) -> str:
        return v.upper()

    @field_validator("payment_mode")
    @classmethod
    def _payment_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in codes.PAYMENT_MODES:
            raise ValueError("payment_mode must be 01-08")
        return v

    @model_validator(mode="after")
    def _rules(self) -> InvoiceInput:
        if self.currency != "MYR" and self.exchange_rate is None:
            raise ValueError("exchange_rate is required when currency is not MYR")
        if self.document_type in codes.ADJUSTMENT_TYPES and self.original_document is None:
            raise ValueError("original_document is required for credit, debit and refund notes")
        if not self.supplier.msic_code or not self.supplier.business_activity:
            raise ValueError("supplier.msic_code and supplier.business_activity are required")
        if self.issued_at is not None and self.issued_at.tzinfo is None:
            self.issued_at = self.issued_at.replace(tzinfo=timezone.utc)
        return self

    @property
    def is_self_billed(self) -> bool:
        return self.document_type in codes.SELF_BILLED_TYPES

    @property
    def issuer_tin(self) -> str:
        """The party that issues (and submits) the document: the buyer when self-billed."""
        return self.buyer.tin if self.is_self_billed else self.supplier.tin


@dataclass(frozen=True)
class LineTotals:
    subtotal: Decimal  # quantity x unit price, before discount
    line_extension: Decimal  # after discount, before tax
    tax: Decimal


@dataclass(frozen=True)
class TaxSubtotal:
    tax_type: str
    rate: Decimal
    taxable: Decimal
    tax: Decimal
    exemption_reason: str | None = None


@dataclass(frozen=True)
class Totals:
    lines: list[LineTotals]
    line_extension: Decimal
    tax_exclusive: Decimal
    tax: Decimal
    tax_inclusive: Decimal
    payable: Decimal
    tax_subtotals: list[TaxSubtotal] = field(default_factory=list)


def compute_totals(invoice: InvoiceInput) -> Totals:
    lines: list[LineTotals] = []
    groups: dict[tuple[str, Decimal], list[Decimal]] = defaultdict(lambda: [Decimal("0"), Decimal("0")])
    reasons: dict[tuple[str, Decimal], str | None] = {}
    for item in invoice.lines:
        subtotal = money(item.quantity * item.unit_price)
        extension = money(subtotal - item.discount_amount)
        if item.tax_amount is not None:
            tax = money(item.tax_amount)
        elif item.tax_type in ("06", "E"):
            tax = Decimal("0.00")
        else:
            tax = money(extension * item.tax_rate / 100)
        lines.append(LineTotals(subtotal=subtotal, line_extension=extension, tax=tax))
        key = (item.tax_type, item.tax_rate)
        groups[key][0] += extension
        groups[key][1] += tax
        reasons.setdefault(key, item.tax_exemption_reason)
    line_extension = money(sum((t.line_extension for t in lines), Decimal("0")))
    tax_total = money(sum((t.tax for t in lines), Decimal("0")))
    inclusive = line_extension + tax_total
    subtotals = [
        TaxSubtotal(tax_type=k[0], rate=k[1], taxable=money(v[0]), tax=money(v[1]), exemption_reason=reasons[k])
        for k, v in groups.items()
    ]
    return Totals(
        lines=lines,
        line_extension=line_extension,
        tax_exclusive=line_extension,
        tax=tax_total,
        tax_inclusive=inclusive,
        payable=inclusive,
        tax_subtotals=subtotals,
    )
