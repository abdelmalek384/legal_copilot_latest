"""Provider boundary for subscription billing; no real payment network calls.

Amounts use integer minor units (piasters for EGP). The interface deliberately
accepts no PAN, CVV, expiry, bank credentials, or other cardholder secrets.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Mapping, Protocol


@dataclass(frozen=True)
class PaymentRequest:
    provider_reference: str
    merchant_reference: str
    amount_minor: int
    currency: str
    status: str
    metadata: Mapping[str, str]


class BillingProvider(Protocol):
    def create_payment_request(
        self,
        *,
        merchant_reference: str,
        amount_minor: int,
        currency: str,
        metadata: Mapping[str, str] | None = None,
    ) -> PaymentRequest: ...

    def get_payment_request(self, provider_reference: str) -> PaymentRequest | None: ...


class FakeBillingProvider:
    """In-memory provider for development/tests; it never charges or transfers."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._next_id = 1
        self._requests: dict[str, PaymentRequest] = {}

    def create_payment_request(
        self,
        *,
        merchant_reference: str,
        amount_minor: int,
        currency: str,
        metadata: Mapping[str, str] | None = None,
    ) -> PaymentRequest:
        if not isinstance(merchant_reference, str) or not merchant_reference.strip():
            raise ValueError("Merchant reference is required")
        if isinstance(amount_minor, bool) or not isinstance(amount_minor, int) or amount_minor <= 0:
            raise ValueError("Amount must be a positive integer in minor units")
        if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
            raise ValueError("Currency must be a three-letter code")
        safe_metadata = dict(metadata or {})
        allowed_metadata_keys = {
            "firm_id", "plan", "plan_code", "subscription_id",
            "invoice_id", "transfer_reference",
        }
        if any(not isinstance(k, str) or not isinstance(v, str) for k, v in safe_metadata.items()):
            raise TypeError("Payment metadata must contain string keys and values")
        if any(k not in allowed_metadata_keys for k in safe_metadata):
            raise ValueError("Payment metadata contains an unsupported field")
        if any(len(v) > 200 or any(ord(char) < 32 for char in v) for v in safe_metadata.values()):
            raise ValueError("Payment metadata values must be bounded plain text")
        with self._lock:
            provider_reference = f"fake_{self._next_id:08d}"
            self._next_id += 1
            request = PaymentRequest(
                provider_reference=provider_reference,
                merchant_reference=merchant_reference.strip(),
                amount_minor=amount_minor,
                currency=currency.upper(),
                status="pending",
                metadata=safe_metadata,
            )
            self._requests[provider_reference] = request
            return request

    def get_payment_request(self, provider_reference: str) -> PaymentRequest | None:
        with self._lock:
            return self._requests.get(provider_reference)

    def mark_paid_for_test(self, provider_reference: str) -> PaymentRequest:
        """Simulate an external provider confirmation in tests only."""
        with self._lock:
            current = self._requests.get(provider_reference)
            if current is None:
                raise KeyError("Unknown fake payment request")
            if current.status != "pending":
                raise ValueError("Only pending requests can be marked paid")
            updated = PaymentRequest(
                provider_reference=current.provider_reference,
                merchant_reference=current.merchant_reference,
                amount_minor=current.amount_minor,
                currency=current.currency,
                status="paid",
                metadata=dict(current.metadata),
            )
            self._requests[provider_reference] = updated
            return updated
