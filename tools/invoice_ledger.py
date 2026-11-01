"""Integer-piaster invoice arithmetic and receivables helpers.

No database schema or legal/tax policy is assumed here. Persistence and
numbering scope remain a separate, tenant-owned migration decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from collections.abc import Iterable


MAX_PIASTERS = 9_000_000_000_000_000


def _positive_int(value: int, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer")
    if value < (0 if allow_zero else 1) or value > MAX_PIASTERS:
        raise ValueError(f"{label} is outside the supported range")
    return value


@dataclass(frozen=True)
class InvoiceLine:
    description: str
    quantity: int
    unit_amount_piasters: int

    def total_piasters(self) -> int:
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Invoice line description is required")
        quantity = _positive_int(self.quantity, "quantity")
        unit = _positive_int(self.unit_amount_piasters, "unit amount", allow_zero=True)
        total = quantity * unit
        if total > MAX_PIASTERS:
            raise ValueError("Invoice line total exceeds supported range")
        return total


def invoice_total_piasters(lines: Iterable[InvoiceLine]) -> int:
    items = tuple(lines)
    if not items:
        raise ValueError("At least one invoice line is required")
    total = sum(line.total_piasters() for line in items)
    if total > MAX_PIASTERS:
        raise ValueError("Invoice total exceeds supported range")
    return total


def outstanding_piasters(total_piasters: int, payment_amounts: Iterable[int]) -> int:
    total = _positive_int(total_piasters, "invoice total", allow_zero=True)
    paid = sum(_positive_int(value, "payment amount", allow_zero=True) for value in payment_amounts)
    if paid > total:
        raise ValueError("Payments cannot exceed invoice total")
    return total - paid


def invoice_payment_status(total_piasters: int, payment_amounts: Iterable[int]) -> str:
    total = _positive_int(total_piasters, "invoice total", allow_zero=True)
    balance = outstanding_piasters(total, payment_amounts)
    if balance == 0:
        return "paid"
    if balance == total:
        return "unpaid"
    return "partially_paid"


def receivables_aging_bucket(due_date: str, as_of: str) -> str:
    """Classify an unpaid balance by whole calendar days past due."""
    try:
        due = date.fromisoformat(due_date)
        today = date.fromisoformat(as_of)
    except (TypeError, ValueError) as exc:
        raise ValueError("due_date and as_of must be valid ISO calendar dates") from exc
    days_past_due = (today - due).days
    if days_past_due <= 0:
        return "current"
    if days_past_due <= 30:
        return "1_30"
    if days_past_due <= 60:
        return "31_60"
    return "61_plus"


def format_document_number(kind: str, year: int, sequence: int) -> str:
    """Format a firm-scoped sequence supplied by persistence (INV/RCT)."""
    if kind not in {"invoice", "receipt"}:
        raise ValueError("kind must be invoice or receipt")
    if isinstance(year, bool) or not isinstance(year, int) or not 2000 <= year <= 9999:
        raise ValueError("year must be a four-digit calendar year")
    sequence = _positive_int(sequence, "sequence")
    prefix = "INV" if kind == "invoice" else "RCT"
    return f"{prefix}-{year:04d}-{sequence:06d}"
