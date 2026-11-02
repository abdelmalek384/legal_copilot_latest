"""Provider boundary and zero-cost WhatsApp click-to-chat links.

The browser uses wa.me so no WhatsApp API credentials or server-side delivery
are required. A future Business Platform adapter can implement WhatsAppProvider.
"""
from __future__ import annotations

import re
from typing import Protocol
from urllib.parse import quote


class WhatsAppProvider(Protocol):
    """Transport interface for a future WhatsApp Business Platform adapter."""

    def send_text(self, phone: str, message: str) -> dict:
        """Send a plain-text message and return a provider-neutral outcome."""
        ...


def normalize_international_phone(phone: str) -> str:
    if not isinstance(phone, str):
        raise ValueError("phone must be a string")
    digits = re.sub(r"\D", "", phone)
    if not 8 <= len(digits) <= 15 or digits.startswith("0"):
        raise ValueError("phone must include an international country code")
    return digits


def build_wa_me_url(phone: str, message: str) -> str:
    if not isinstance(message, str) or not message.strip() or len(message) > 2000:
        raise ValueError("message must contain 1 to 2000 characters")
    number = normalize_international_phone(phone)
    return f"https://wa.me/{number}?text={quote(message, safe='')}"


class FakeWhatsAppProvider:
    """Deterministic provider fake; never makes a network request."""

    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def send_text(self, phone: str, message: str) -> dict:
        number = normalize_international_phone(phone)
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must not be empty")
        self.messages.append({"phone": number, "message": message})
        return {"status": "accepted_by_fake_provider", "message_index": len(self.messages) - 1}
