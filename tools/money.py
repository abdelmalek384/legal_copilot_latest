"""Exact Egyptian-pound/piaster conversion helpers.

Persist and calculate money as integer piasters. Decimal strings are accepted
at input boundaries; binary floating-point values are deliberately rejected.
"""
from __future__ import annotations

import re


_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def egp_to_piasters(value: str | int) -> int:
    """Convert an EGP decimal string (or whole-pound integer) to piasters."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise TypeError("EGP amount must be a decimal string or whole-pound integer")
    raw = str(value).translate(_ARABIC_DIGITS).strip()
    if not raw:
        raise ValueError("EGP amount is required")
    # Commas are accepted only as correctly grouped thousands separators.
    if "," in raw:
        if not re.fullmatch(r"[+-]?\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?", raw):
            raise ValueError("Invalid thousands grouping")
        raw = raw.replace(",", "")
    match = re.fullmatch(r"([+]?(?:0|[1-9]\d*))(?:\.(\d{1,2}))?", raw)
    if not match:
        raise ValueError("Amount must be a non-negative EGP value with at most 2 decimals")
    pounds = int(match.group(1))
    fraction = (match.group(2) or "").ljust(2, "0")
    return pounds * 100 + int(fraction or "0")


def require_piasters(value: int) -> int:
    """Validate an integer piaster amount for persistence/calculation."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Money must be stored as integer piasters")
    if value < 0:
        raise ValueError("Money amount cannot be negative")
    return value


def piasters_to_egp(value: int) -> str:
    """Format integer piasters as a fixed two-decimal EGP amount."""
    amount = require_piasters(value)
    return f"{amount // 100}.{amount % 100:02d}"
