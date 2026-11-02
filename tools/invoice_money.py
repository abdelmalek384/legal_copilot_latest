"""Exact EGP amount parsing and formatting using integer piasters only."""
from __future__ import annotations

import re

_EGP_AMOUNT = re.compile(r"^(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,2})?$")


class InvoiceMoneyError(ValueError):
    pass


def egp_to_piasters(value: str) -> int:
    if not isinstance(value, str) or not _EGP_AMOUNT.fullmatch(value.strip()):
        raise InvoiceMoneyError("amount must be a non-negative EGP decimal with at most two places")
    whole, dot, fraction = value.strip().partition(".")
    piasters = int(whole) * 100 + int((fraction + "00")[:2] if dot else "00")
    if piasters > 9_000_000_000_000_000:
        raise InvoiceMoneyError("amount exceeds the supported limit")
    return piasters


def piasters_to_egp(value: int) -> str:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvoiceMoneyError("piasters must be a non-negative integer")
    return f"{value // 100}.{value % 100:02d}"
