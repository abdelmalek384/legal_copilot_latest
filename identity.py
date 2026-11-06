"""Canonical email normalization shared by authentication and legacy-data audits."""
from __future__ import annotations

import unicodedata


def normalize_email(value: str) -> str:
    """Trim, Unicode-normalize, and case-fold an email for global identity matching.

    This deliberately does not merge or repair existing accounts. The fresh
    control-plane schema enforces uniqueness on this canonical key. If legacy
    identities are ever imported, normalized collisions must be surfaced and
    resolved through an explicit, auditable identity workflow before import.
    """
    if not isinstance(value, str):
        raise TypeError("email must be a string")
    return unicodedata.normalize("NFC", value.strip()).casefold()
