"""Provider boundary for future WhatsApp Business delivery.

The current product uses user-initiated wa.me links; no message is sent by this module.
FakeWhatsAppProvider exists for deterministic tests and integration development.
"""
from __future__ import annotations

from typing import Protocol


class WhatsAppProviderError(ValueError):
    """Raised when a WhatsApp recipient or message is invalid."""


class WhatsAppProvider(Protocol):
    def send_text(self, recipient: str, message: str) -> dict:
        """Submit a text message through an explicitly configured provider."""


def normalize_whatsapp_recipient(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WhatsAppProviderError("recipient phone number is required")
    digits = "".join(character for character in value if character.isdigit())
    if digits.startswith("00"):
        digits = digits[2:]
    elif digits.startswith("0"):
        # Local Egyptian mobile numbers are accepted as a convenience.
        digits = "20" + digits[1:]
    if not digits or digits.startswith("0") or not 8 <= len(digits) <= 15:
        raise WhatsAppProviderError("recipient must be an international phone number")
    return "+" + digits


def validate_message(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise WhatsAppProviderError("message must contain 1 to 4096 characters")
    return value.strip()


class FakeWhatsAppProvider:
    """In-memory fake; never opens a socket or contacts WhatsApp."""

    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def send_text(self, recipient: str, message: str) -> dict:
        normalized = normalize_whatsapp_recipient(recipient)
        text = validate_message(message)
        record = {"recipient": normalized, "message": text}
        self.messages.append(record)
        return {"status": "accepted_by_fake_provider", "message_id": str(len(self.messages))}
