#!/usr/bin/env python3
"""Database-independent MFA primitives. These helpers do not enable MFA in the app."""
from __future__ import annotations
import base64, hashlib, hmac, math, re, secrets, struct, time
from urllib.parse import quote, urlencode

TOTP_DIGITS = 6
TOTP_PERIOD_SECONDS = 30
TOTP_ALGORITHM = "SHA1"
RECOVERY_CODE_COUNT_DEFAULT = 10
_RECOVERY_CODE_PATTERN = re.compile(r"^[A-F0-9]{10}$")
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1
_SCRYPT_DKLEN, _SCRYPT_SALT_BYTES = 32, 16
_SCRYPT_MAXMEM = 64 * 1024 * 1024


class MFAPrimitivesError(ValueError):
    """Raised for invalid MFA setup input."""


def _decode_secret(secret: object) -> bytes:
    if not isinstance(secret, str) or not secret.strip() or not re.fullmatch(r"[A-Z2-7]+=*", secret.strip().upper()):
        raise MFAPrimitivesError("TOTP secret must be a valid Base32 string")
    normalized = secret.strip().upper().rstrip("=")
    try:
        return base64.b32decode(normalized + "=" * ((8 - len(normalized) % 8) % 8), casefold=False)
    except (ValueError, base64.binascii.Error) as exc:
        raise MFAPrimitivesError("TOTP secret must be a valid Base32 string") from exc


def generate_totp_secret() -> str:
    """Generate a 160-bit Base32 secret; callers must show it only during enrollment."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def build_totp_uri(secret: str, account_name: str, issuer: str = "Legal Copilot") -> str:
    _decode_secret(secret)
    for value, label in ((account_name, "account_name"), (issuer, "issuer")):
        if not isinstance(value, str) or not value.strip() or any(ord(ch) < 32 for ch in value):
            raise MFAPrimitivesError(f"{label} must be a non-empty printable string")
    label = quote(issuer.strip(), safe="") + ":" + quote(account_name.strip(), safe="")
    query = urlencode({"secret": secret.strip().upper().rstrip("="), "issuer": issuer.strip(),
                       "algorithm": TOTP_ALGORITHM, "digits": str(TOTP_DIGITS),
                       "period": str(TOTP_PERIOD_SECONDS)})
    return f"otpauth://totp/{label}?{query}"


def _totp_at_step(secret_bytes: bytes, step: int) -> str:
    digest = hmac.new(secret_bytes, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{binary % (10 ** TOTP_DIGITS):0{TOTP_DIGITS}d}"


def verify_totp(secret: str, code: str, *, now: float | int | None = None,
                window: int = 1, last_accepted_step: int | None = None) -> int | None:
    """Return matching time step or None; caller must persist the step atomically."""
    secret_bytes = _decode_secret(secret)
    if not isinstance(code, str) or not re.fullmatch(r"\d{6}", code.strip()):
        return None
    if type(window) is not int or not 0 <= window <= 2:
        raise MFAPrimitivesError("window must be an integer from 0 through 2")
    if last_accepted_step is not None and (type(last_accepted_step) is not int or last_accepted_step < 0):
        raise MFAPrimitivesError("last_accepted_step must be a non-negative integer or None")
    timestamp = time.time() if now is None else now
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)) or not math.isfinite(timestamp) or timestamp < 0:
        raise MFAPrimitivesError("now must be a finite non-negative Unix timestamp")
    current_step = int(timestamp) // TOTP_PERIOD_SECONDS
    matches = []
    supplied = code.strip()
    for step in range(max(0, current_step - window), current_step + window + 1):
        candidate = _totp_at_step(secret_bytes, step)
        if hmac.compare_digest(candidate, supplied) and (last_accepted_step is None or step > last_accepted_step):
            matches.append(step)
    return max(matches) if matches else None


def _normalize_recovery_code(code: object) -> str | None:
    if not isinstance(code, str):
        return None
    normalized = code.strip().upper().replace("-", "").replace(" ", "")
    return normalized if _RECOVERY_CODE_PATTERN.fullmatch(normalized) else None


def hash_recovery_code(code: str) -> str:
    """Return a salted scrypt hash; never store or log the plaintext code."""
    normalized = _normalize_recovery_code(code)
    if normalized is None:
        raise MFAPrimitivesError("recovery code must contain exactly 10 hexadecimal characters")
    salt = secrets.token_bytes(_SCRYPT_SALT_BYTES)
    digest = hashlib.scrypt(normalized.encode("ascii"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R,
                            p=_SCRYPT_P, dklen=_SCRYPT_DKLEN, maxmem=_SCRYPT_MAXMEM)
    encode = lambda value: base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${encode(salt)}${encode(digest)}"


def verify_recovery_code(code: str, encoded_hash: str) -> bool:
    """Verify one hash; caller must consume a matching code atomically."""
    normalized = _normalize_recovery_code(code)
    if normalized is None or not isinstance(encoded_hash, str):
        return False
    parts = encoded_hash.split("$")
    if len(parts) != 6 or parts[0] != "scrypt":
        return False
    try:
        n, r, p = (int(parts[index]) for index in (1, 2, 3))
        if (n, r, p) != (_SCRYPT_N, _SCRYPT_R, _SCRYPT_P):
            return False
        decode = lambda value: base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))
        salt, expected = decode(parts[4]), decode(parts[5])
        if len(salt) != _SCRYPT_SALT_BYTES or len(expected) != _SCRYPT_DKLEN:
            return False
        actual = hashlib.scrypt(normalized.encode("ascii"), salt=salt, n=n, r=r, p=p,
                                dklen=len(expected), maxmem=_SCRYPT_MAXMEM)
    except (ValueError, TypeError, base64.binascii.Error):
        return False
    return hmac.compare_digest(actual, expected)


def generate_recovery_codes(count: int = RECOVERY_CODE_COUNT_DEFAULT) -> dict:
    """Return plaintext codes for one-time display and salted hashes for storage."""
    if type(count) is not int or not 1 <= count <= 20:
        raise MFAPrimitivesError("count must be an integer from 1 through 20")
    codes = [secrets.token_hex(5).upper() for _ in range(count)]
    return {"codes": codes, "hashes": [hash_recovery_code(code) for code in codes]}
