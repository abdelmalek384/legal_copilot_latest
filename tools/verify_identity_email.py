#!/usr/bin/env python3
"""Send one controlled SMTP acceptance message through the configured identity-email path.

This proves SMTP submission only. A human must verify mailbox receipt, spam placement,
link integrity, and end-to-end invitation/recovery behavior in the controlled mailbox.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

from identity_email import IdentityEmailError, send_identity_email


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", required=True, help="Controlled staging/production mailbox")
    parser.add_argument(
        "--confirm-controlled-mailbox", action="store_true",
        help="Confirm the recipient is an approved mailbox controlled by the operator",
    )
    parser.add_argument(
        "--confirm-production-send", action="store_true",
        help="Explicitly authorize sending a probe from the production deployment",
    )
    args = parser.parse_args(argv)
    if not args.confirm_controlled_mailbox:
        parser.error("explicitly confirm the recipient is a controlled acceptance mailbox")
    environment = os.environ.get("COPILOT_ENV", "").strip().lower()
    if environment not in {"staging", "prod", "production"}:
        parser.error("COPILOT_ENV must identify the staging or production deployment")
    if environment in {"prod", "production"} and not args.confirm_production_send:
        parser.error("production SMTP probes require --confirm-production-send")
    security = os.environ.get("COPILOT_EMAIL_SMTP_SECURITY", "starttls").strip().lower()
    if security not in {"starttls", "ssl"}:
        parser.error("SMTP acceptance requires STARTTLS or implicit TLS")
    probe_id = uuid.uuid4().hex
    subject = f"Legal Copilot SMTP acceptance probe {probe_id[:12]}"
    body = (
        "This is a controlled SMTP acceptance probe.\n"
        f"Probe ID: {probe_id}\n"
        "No client, matter, password, invitation, or recovery data is included.\n"
        "Please verify receipt, sender identity, spam placement, and message integrity."
    )
    try:
        send_identity_email(args.recipient, subject, body)
    except IdentityEmailError:
        print(json.dumps({
            "status": "failed",
            "probe_id": probe_id,
            "smtp_submission_accepted": False,
            "mailbox_receipt_verified": False,
        }, sort_keys=True))
        return 1
    print(json.dumps({
        "status": "smtp_submission_accepted",
        "probe_id": probe_id,
        "smtp_submission_accepted": True,
        "mailbox_receipt_verified": False,
        "manual_mailbox_verification_required": True,
        "environment": "production" if environment in {"prod", "production"} else "staging",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
