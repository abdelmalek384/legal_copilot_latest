"""Dedicated at-rest encryption for TOTP secrets.

Never reuse BACKUP_KEY. MFA_ENCRYPTION_KEY must be generated and managed separately.
"""
from __future__ import annotations

import os
from typing import Mapping

from cryptography.fernet import Fernet, InvalidToken


class MFAConfigurationError(RuntimeError):
    """Raised when the dedicated MFA encryption key is unavailable or invalid."""


def _fernet(environ: Mapping[str, str] | None = None) -> Fernet:
    env = os.environ if environ is None else environ
    raw = env.get("MFA_ENCRYPTION_KEY", "")
    if not isinstance(raw, str) or not raw.strip():
        raise MFAConfigurationError("MFA_ENCRYPTION_KEY must be configured before MFA can be used")
    try:
        key = raw.strip().encode("ascii")
        return Fernet(key)
    except (ValueError, TypeError, UnicodeEncodeError) as exc:
        raise MFAConfigurationError("MFA_ENCRYPTION_KEY is invalid") from exc


def encrypt_totp_secret(secret: str, *, environ: Mapping[str, str] | None = None) -> str:
    if not isinstance(secret, str) or not secret:
        raise MFAConfigurationError("TOTP secret is invalid")
    return _fernet(environ).encrypt(secret.encode("ascii")).decode("ascii")


def decrypt_totp_secret(ciphertext: str, *, environ: Mapping[str, str] | None = None) -> str:
    if not isinstance(ciphertext, str) or not ciphertext:
        raise MFAConfigurationError("Encrypted TOTP secret is invalid")
    try:
        return _fernet(environ).decrypt(ciphertext.encode("ascii")).decode("ascii")
    except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError) as exc:
        raise MFAConfigurationError("Encrypted TOTP secret cannot be decrypted with the configured MFA key") from exc
