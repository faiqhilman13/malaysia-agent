"""Monthly consolidated e-invoice for B2C sales where buyers did not ask for an e-invoice.

Rules applied:
- Buyer is the general public (TIN EI00000000010) and every line uses classification 004.
- Since 1 Jan 2026, a single transaction above RM10,000 cannot be consolidated; it needs its own e-invoice.
- Submit within 7 days after the end of the month.
"""

from __future__ import annotations

import calendar
import math
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from pydantic import Field

from . import codes
from .invoice import Address, BillingPeriod, InvoiceInput, LineItem, Money, Party, _Strict

MAX_LINES = 1000


class Receipt(_Strict):
    reference: str = Field(min_length=1, max_length=50, description="Receipt or transaction number.")
    issued_on: date
    amount: Money = Field(description="Amount before tax, in MYR.")
    tax_type: str = Field(default="06")
    tax_amount: Money = Decimal("0")

    @property
    def gross(self) -> Decimal:
        return self.amount + self.tax_amount


@dataclass(frozen=True)
class ConsolidationPlan:
    invoice: InvoiceInput | None
    individual_required: list[Receipt]
    period_start: date
    period_end: date
    submit_by: date


def general_public_buyer() -> Party:
    return Party(
        name="General Public",
        tin=codes.GENERAL_TIN_PUBLIC,
        id_type="BRN",
        id_value="NA",
        address=Address(lines=["NA"], city="NA", state_code="17"),
        phone="NA",
    )


def plan(
    *,
    month: str,
    receipts: list[Receipt],
    supplier: Party,
    code_number: str,
    version: str = "1.0",
) -> ConsolidationPlan:
    year, mon = (int(part) for part in month.split("-"))
    start = date(year, mon, 1)
    end = date(year, mon, calendar.monthrange(year, mon)[1])
    outside = [r.reference for r in receipts if not start <= r.issued_on <= end]
    if outside:
        raise ValueError(f"receipts outside {month}: {', '.join(outside[:10])}")

    limit = Decimal(codes.CONSOLIDATION_LIMIT_MYR)
    individual = [r for r in receipts if r.gross > limit]
    eligible = sorted((r for r in receipts if r.gross <= limit), key=lambda r: (r.issued_on, r.reference))

    invoice = None
    if eligible:
        invoice = InvoiceInput(
            document_type="01",
            version=version,
            code_number=code_number,
            supplier=supplier,
            buyer=general_public_buyer(),
            billing_period=BillingPeriod(start=start, end=end, frequency="Monthly"),
            lines=_lines(eligible),
        )
    return ConsolidationPlan(
        invoice=invoice,
        individual_required=individual,
        period_start=start,
        period_end=end,
        submit_by=end + timedelta(days=7),
    )


def _lines(receipts: list[Receipt]) -> list[LineItem]:
    # One line per receipt when possible; otherwise contiguous ranges, keeping each tax type separate.
    by_tax: dict[str, list[Receipt]] = {}
    for receipt in receipts:
        by_tax.setdefault(receipt.tax_type, []).append(receipt)
    total = len(receipts)
    group_size = max(1, math.ceil(total / MAX_LINES))
    lines: list[LineItem] = []
    for tax_type, group in by_tax.items():
        for i in range(0, len(group), group_size):
            chunk = group[i : i + group_size]
            label = chunk[0].reference if len(chunk) == 1 else f"{chunk[0].reference} - {chunk[-1].reference}"
            lines.append(
                LineItem(
                    description=f"Receipt {label}" if len(chunk) == 1 else f"Receipts {label}",
                    classification_code=codes.CLASSIFICATION_CONSOLIDATED,
                    quantity=Decimal("1"),
                    unit_price=sum((r.amount for r in chunk), Decimal("0")),
                    tax_type=tax_type,
                    tax_amount=sum((r.tax_amount for r in chunk), Decimal("0")),
                    tax_exemption_reason="Consolidated exempt sales" if tax_type == "E" else None,
                )
            )
    return lines
