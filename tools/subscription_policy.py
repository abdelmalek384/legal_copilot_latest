"""Subscription policy primitives without persistence or payment credentials.

Plan seat limits and trial duration are explicit configuration inputs: this
module deliberately does not invent prices, seat counts, or a trial duration.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


PLAN_CODES = frozenset({"solo", "small_firm"})
SUBSCRIPTION_STATES = frozenset(
    {"trialing", "pending_payment", "active", "past_due", "expired", "canceled"}
)
_ALLOWED_TRANSITIONS = {
    "trialing": frozenset({"pending_payment", "active", "expired", "canceled"}),
    "pending_payment": frozenset({"trialing", "active", "past_due", "canceled"}),
    "active": frozenset({"past_due", "canceled"}),
    "past_due": frozenset({"active", "canceled"}),
    "expired": frozenset({"pending_payment", "active", "canceled"}),
    "canceled": frozenset(),
}


@dataclass(frozen=True)
class PlanPolicy:
    code: str
    seat_limit: int
    trial_days: int

    def __post_init__(self) -> None:
        if self.code not in PLAN_CODES:
            raise ValueError("unsupported subscription plan")
        if isinstance(self.seat_limit, bool) or not isinstance(self.seat_limit, int) or self.seat_limit < 1:
            raise ValueError("seat_limit must be a positive integer")
        if isinstance(self.trial_days, bool) or not isinstance(self.trial_days, int) or not 0 <= self.trial_days <= 90:
            raise ValueError("trial_days must be an integer from 0 to 90")


def _aware_datetime(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def trial_end_at(started_at: datetime, trial_days: int) -> datetime:
    start = _aware_datetime(started_at, "started_at")
    if isinstance(trial_days, bool) or not isinstance(trial_days, int) or not 0 <= trial_days <= 90:
        raise ValueError("trial_days must be an integer from 0 to 90")
    return start + timedelta(days=trial_days)


def evaluate_subscription_status(
    state: str,
    now: datetime,
    *,
    trial_ends_at: datetime | None = None,
    paid_through: datetime | None = None,
) -> str:
    """Resolve expiry from trusted timestamps; never trust a client-supplied state."""
    current = _aware_datetime(now, "now")
    if state not in SUBSCRIPTION_STATES:
        raise ValueError("unsupported subscription state")
    if state == "trialing":
        if trial_ends_at is None:
            raise ValueError("trial_ends_at is required for a trial")
        return "trialing" if current < _aware_datetime(trial_ends_at, "trial_ends_at") else "expired"
    if state == "active":
        if paid_through is None:
            raise ValueError("paid_through is required for an active subscription")
        return "active" if current < _aware_datetime(paid_through, "paid_through") else "past_due"
    return state


def seat_capacity_available(active_seats: int, seat_limit: int, requested: int = 1) -> bool:
    for value, label in ((active_seats, "active_seats"), (seat_limit, "seat_limit"), (requested, "requested")):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{label} must be an integer")
    if active_seats < 0 or seat_limit < 1 or requested < 1:
        raise ValueError("seat counts must be non-negative and requested/limit positive")
    return active_seats + requested <= seat_limit


def can_transition_subscription(current: str, target: str) -> bool:
    if current not in SUBSCRIPTION_STATES or target not in SUBSCRIPTION_STATES:
        raise ValueError("unsupported subscription state")
    return target in _ALLOWED_TRANSITIONS[current]


def validate_transfer_reference(reference: str) -> str:
    """Validate a bank/InstaPay transfer reference, not account/card credentials."""
    if not isinstance(reference, str):
        raise TypeError("transfer reference must be text")
    normalized = reference.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{5,79}", normalized):
        raise ValueError("transfer reference must be 6-80 safe reference characters")
    return normalized
