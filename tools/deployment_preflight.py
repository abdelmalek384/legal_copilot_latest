#!/usr/bin/env python3
"""Read-only deployment configuration checks; never prints secret values."""
import argparse
import ipaddress
import math
import os
import re
import stat
import sys
from pathlib import Path
from urllib.parse import urlsplit

from cryptography.fernet import Fernet


def valid_llm_endpoint(value):
    """Require HTTPS remotely; plain HTTP is allowed only for loopback model services."""
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value.strip())
        host = parsed.hostname
        if (parsed.scheme not in {"https", "http"} or not host or parsed.username or parsed.password
                or parsed.query or parsed.fragment):
            return False
        _ = parsed.port
        if parsed.scheme == "https":
            return True
        if host.lower().rstrip(".") == "localhost":
            return True
        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False
    except (TypeError, ValueError):
        return False


def valid_trusted_hosts(value):
    """Validate explicit hostnames/IPs and optional subdomain wildcards."""
    if not isinstance(value, str) or not value.strip():
        return False
    label_pattern = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
    for raw in value.split(","):
        host = raw.strip().lower()
        if not host or host == "*" or "://" in host or "/" in host or "@" in host:
            return False
        wildcard = host.startswith("*.")
        candidate = host[2:] if wildcard else host
        if "*" in candidate or not candidate:
            return False
        if candidate.startswith("[") and candidate.endswith("]"):
            try:
                ipaddress.IPv6Address(candidate[1:-1])
            except ValueError:
                return False
            if wildcard:
                return False
            continue
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            labels = candidate.split(".")
            if not labels or any(not label_pattern.fullmatch(label) for label in labels):
                return False
        else:
            if wildcard:
                return False
    return True


def inspect_environment(env=None, *, require_separate=False):
    env = os.environ if env is None else env
    production = env.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}
    require_separate = bool(require_separate or production)
    errors, warnings, passed = [], [], []

    if env.get("ALLOW_UNLINKED_LEGACY_LAW_SEARCH", "").strip() == "1":
        errors.append("ALLOW_UNLINKED_LEGACY_LAW_SEARCH=1 enables unreviewed legacy-law retrieval and is not allowed for deployment.")
    else:
        passed.append("Unlinked legacy-law search override is disabled.")

    token = env.get("ADMIN_TOKEN", "")
    weak_markers = ("change-me", "changeme", "example", "placeholder", "test-token", "your-secret")
    if len(token) < 32 or any(marker in token.lower() for marker in weak_markers):
        errors.append("ADMIN_TOKEN must be a non-placeholder secret of at least 32 characters.")
    else:
        passed.append("ADMIN_TOKEN is present and meets the basic length/placeholder check.")

    allowed_hosts = env.get("COPILOT_ALLOWED_HOSTS", "").strip()
    if allowed_hosts:
        if valid_trusted_hosts(allowed_hosts):
            passed.append("COPILOT_ALLOWED_HOSTS contains valid explicit host patterns.")
        else:
            errors.append("COPILOT_ALLOWED_HOSTS must be a comma-separated list of explicit hostnames or IP addresses, not URLs or wildcard-all.")
    else:
        message = "COPILOT_ALLOWED_HOSTS is required in production; Host-header allowlisting must be enabled."
        if production:
            errors.append(message)
        else:
            warnings.append("COPILOT_ALLOWED_HOSTS is unset; Host-header allowlisting is disabled.")

    if env.get("COPILOT_SECURE_COOKIES", "").strip() == "1":
        passed.append("Secure cookies and HSTS are explicitly enabled for HTTPS/proxy deployment.")
    else:
        if production:
            errors.append("COPILOT_SECURE_COOKIES=1 is required in production when the public endpoint is HTTPS.")
        else:
            warnings.append("COPILOT_SECURE_COOKIES=1 is not set; if TLS terminates at a reverse proxy, session cookies may lack Secure and HSTS may be omitted. Set it only when the public endpoint is HTTPS.")

    # Identity lifecycle (verification, invitation, and recovery) depends on
    # outbound email. Catch incomplete/insecure SMTP configuration before release;
    # this is configuration validation, not a live delivery test.
    if production:
        smtp_host = env.get("COPILOT_EMAIL_SMTP_HOST", "").strip()
        smtp_from = env.get("COPILOT_EMAIL_FROM", "").strip()
        smtp_security = env.get("COPILOT_EMAIL_SMTP_SECURITY", "starttls").strip().lower()
        smtp_username = env.get("COPILOT_EMAIL_SMTP_USERNAME", "").strip()
        smtp_password = env.get("COPILOT_EMAIL_SMTP_PASSWORD", "")
        try:
            smtp_port = int(env.get("COPILOT_EMAIL_SMTP_PORT", "587"))
        except ValueError:
            smtp_port = 0
        if not smtp_host or any(char in smtp_host for char in "\r\n"):
            errors.append("COPILOT_EMAIL_SMTP_HOST must be configured as a valid SMTP hostname.")
        if not smtp_from or any(char in smtp_from for char in "\r\n") or "@" not in smtp_from:
            errors.append("COPILOT_EMAIL_FROM must be configured as a valid sender address.")
        if not 1 <= smtp_port <= 65535:
            errors.append("COPILOT_EMAIL_SMTP_PORT must be an integer from 1 to 65535.")
        if smtp_security not in {"starttls", "ssl"}:
            errors.append("Production identity email requires COPILOT_EMAIL_SMTP_SECURITY=starttls or ssl.")
        if bool(smtp_username) != bool(smtp_password):
            errors.append("COPILOT_EMAIL_SMTP_USERNAME and COPILOT_EMAIL_SMTP_PASSWORD must be configured together.")
        if smtp_host and smtp_from and 1 <= smtp_port <= 65535 and smtp_security in {"starttls", "ssl"} and bool(smtp_username) == bool(smtp_password):
            passed.append("Production identity email has complete encrypted SMTP configuration; live delivery remains unverified.")

    public_origin = env.get("COPILOT_PUBLIC_ORIGIN", "").strip()
    if public_origin:
        try:
            parsed_origin = urlsplit(public_origin)
            valid_origin = (parsed_origin.scheme == "https" and bool(parsed_origin.netloc)
                            and not parsed_origin.username and not parsed_origin.password
                            and parsed_origin.path in {"", "/"} and not parsed_origin.query and not parsed_origin.fragment)
        except ValueError:
            valid_origin = False
        if valid_origin:
            passed.append("COPILOT_PUBLIC_ORIGIN is a fixed HTTPS origin suitable for reverse-proxy origin checks.")
        else:
            errors.append("COPILOT_PUBLIC_ORIGIN must be an HTTPS origin only, without credentials, path, query, or fragment.")
    elif production:
        errors.append("COPILOT_PUBLIC_ORIGIN must be set to the public HTTPS origin in production.")
    elif env.get("COPILOT_SECURE_COOKIES", "").strip() == "1":
        warnings.append("COPILOT_PUBLIC_ORIGIN is unset; if the app sees internal HTTP behind a TLS proxy, browser Origin checks may reject HTTPS requests.")

    llm_url = env.get("LLM_URL", "").strip()
    if llm_url:
        if valid_llm_endpoint(llm_url):
            passed.append("LLM_URL uses HTTPS or a loopback-only HTTP endpoint and contains no URL credentials/query/fragment.")
        else:
            errors.append("LLM_URL must use HTTPS for remote endpoints or loopback HTTP for local model services; credentials, query strings, fragments, and other HTTP hosts are not allowed.")

    raw_score = env.get("MIN_SCORE", "0.3")
    try:
        score = float(raw_score)
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError
        passed.append("MIN_SCORE is a finite number between 0 and 1.")
    except (TypeError, ValueError):
        errors.append("MIN_SCORE must be a finite number between 0 and 1.")

    separate_names = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB")
    configured = {name: env.get(name, "").strip() for name in separate_names}
    has_separate = any(configured.values())

    def inspect_database_path(label, path):
        if not path.is_absolute():
            errors.append(f"{label} must be an absolute path.")
        if path.is_symlink():
            errors.append(f"{label} must not be a symbolic link.")
            return
        parent = path.parent
        if not parent.exists() or not parent.is_dir():
            errors.append(f"{label} parent directory does not exist or is not a directory.")
        elif not os.access(parent, os.W_OK | os.X_OK):
            errors.append(f"{label} parent directory is not writable/searchable by this process.")
        if path.exists():
            if not path.is_file():
                errors.append(f"{label} exists but is not a regular file.")
            elif not os.access(path, os.R_OK | os.W_OK):
                errors.append(f"{label} exists but is not readable and writable by this process.")
            else:
                passed.append(f"{label} exists and is readable/writable.")
            try:
                mode = stat.S_IMODE(path.stat().st_mode)
                if os.name == "posix" and mode & 0o077:
                    errors.append(f"{label} permissions {mode:04o} allow group/other access.")
            except OSError:
                errors.append(f"Could not inspect {label} permissions.")
        else:
            warnings.append(f"{label} does not exist yet; this check does not create or initialize it.")
        if os.name == "posix":
            for suffix in ("-wal", "-shm", "-journal"):
                sidecar = Path(str(path) + suffix)
                if sidecar.is_symlink():
                    errors.append(f"SQLite sidecar {sidecar.name} must not be a symbolic link.")
                    continue
                if not sidecar.exists():
                    continue
                if not sidecar.is_file():
                    errors.append(f"SQLite sidecar {sidecar.name} is not a regular file.")
                    continue
                try:
                    mode = stat.S_IMODE(sidecar.stat().st_mode)
                    if mode & 0o077:
                        errors.append(f"SQLite sidecar {sidecar.name} permissions {mode:04o} allow group/other access.")
                except OSError:
                    errors.append(f"Could not inspect SQLite sidecar {sidecar.name} permissions.")

    if production:
        backup_key = env.get("BACKUP_KEY", "").strip()
        try:
            Fernet(backup_key.encode("ascii"))
        except (ValueError, TypeError, UnicodeError):
            errors.append("BACKUP_KEY must be a valid Fernet key in production; the secret value is never printed.")
        else:
            passed.append("BACKUP_KEY is a valid Fernet key; its value is not printed.")

    # Original matter binaries are confidential tenant data. A local filesystem
    # adapter is useful for development but is not a production storage boundary.
    # Keep this allowlist empty until a KMS-backed remote adapter is implemented
    # end-to-end, including backup, restore, reconciliation, and purge acceptance.
    production_object_storage_backends = frozenset({"s3"})
    object_storage_backend = env.get("COPILOT_OBJECT_STORAGE_BACKEND", "local").strip().lower()
    if production or require_separate:
        if object_storage_backend not in production_object_storage_backends:
            errors.append(
                "Production/release preflight requires COPILOT_OBJECT_STORAGE_BACKEND=s3; "
                "the local filesystem and unknown backends are not approved."
            )
        else:
            missing_s3 = [
                name for name in ("COPILOT_S3_BUCKET", "COPILOT_S3_REGION", "COPILOT_S3_KMS_KEY_ID")
                if not env.get(name, "").strip()
            ]
            if missing_s3:
                errors.append(
                    "S3/KMS production configuration is incomplete; set "
                    "COPILOT_S3_BUCKET, COPILOT_S3_REGION, and COPILOT_S3_KMS_KEY_ID."
                )
            else:
                passed.append(
                    "S3/KMS backend and bucket/region/key settings are configured; "
                    "live provider acceptance remains a separate mandatory gate."
                )
    elif object_storage_backend == "s3":
        missing_s3 = [
            name for name in ("COPILOT_S3_BUCKET", "COPILOT_S3_REGION", "COPILOT_S3_KMS_KEY_ID")
            if not env.get(name, "").strip()
        ]
        if missing_s3:
            warnings.append(
                "S3/KMS backend is selected but bucket/region/key configuration is incomplete."
            )
        else:
            passed.append("S3/KMS backend and bucket/region/key settings are configured.")
    elif object_storage_backend != "local":
        warnings.append("An unknown object-storage backend is configured.")

    mfa_mode = env.get("MFA_ENFORCEMENT", "optional").strip().lower()
    if mfa_mode not in {"optional", "admins_required", "all_required"}:
        errors.append("MFA_ENFORCEMENT must be optional, admins_required, or all_required.")
    elif production and mfa_mode == "optional":
        errors.append("MFA_ENFORCEMENT must require MFA for administrators in production.")
    else:
        passed.append("MFA_ENFORCEMENT uses an explicitly supported policy.")
    if production or mfa_mode in {"admins_required", "all_required"}:
        mfa_key = env.get("MFA_ENCRYPTION_KEY", "").strip()
        try:
            Fernet(mfa_key.encode("ascii"))
        except (ValueError, TypeError, UnicodeError):
            errors.append("MFA_ENCRYPTION_KEY must be a valid dedicated Fernet key when MFA is required; the secret value is never printed.")
        else:
            if mfa_key == env.get("BACKUP_KEY", "").strip():
                errors.append("MFA_ENCRYPTION_KEY must be separate from BACKUP_KEY.")
            else:
                passed.append("MFA_ENCRYPTION_KEY is a valid dedicated Fernet key; its value is not printed.")
    elif not env.get("MFA_ENCRYPTION_KEY", "").strip():
        warnings.append("MFA_ENCRYPTION_KEY is unset; MFA enrollment will remain unavailable until a dedicated key is configured.")

    if has_separate:
        missing = [name for name, value in configured.items() if not value]
        if missing:
            errors.append("Separate database mode requires all three paths: " + ", ".join(missing) + ".")
        else:
            control = Path(configured["COPILOT_CONTROL_DB"]).expanduser()
            tenant_root = Path(configured["COPILOT_TENANT_DB_ROOT"]).expanduser()
            corpus = Path(configured["COPILOT_CORPUS_DB"]).expanduser()
            if control.resolve() == corpus.resolve():
                errors.append("Control-plane and legal-corpus database paths must be different.")
            if control.resolve() == tenant_root.resolve() or corpus.resolve() == tenant_root.resolve():
                errors.append("A database file path cannot equal the tenant storage directory.")
            try:
                control.resolve().relative_to(tenant_root.resolve())
                errors.append("Control-plane database must be outside tenant storage.")
            except ValueError:
                pass
            try:
                corpus.resolve().relative_to(tenant_root.resolve())
                errors.append("Legal-corpus database must be outside tenant storage.")
            except ValueError:
                pass
            if tenant_root.is_symlink():
                errors.append("COPILOT_TENANT_DB_ROOT must not be a symbolic link.")
            elif tenant_root.exists():
                if not tenant_root.is_dir():
                    errors.append("COPILOT_TENANT_DB_ROOT exists but is not a directory.")
                elif not os.access(tenant_root, os.R_OK | os.W_OK | os.X_OK):
                    errors.append("COPILOT_TENANT_DB_ROOT is not readable, writable, and searchable.")
                else:
                    passed.append("Tenant storage root exists and has required access.")
                if os.name == "posix":
                    try:
                        mode = stat.S_IMODE(tenant_root.stat().st_mode)
                        if mode & 0o077:
                            errors.append(f"Tenant storage root permissions {mode:04o} allow group/other access.")
                    except OSError:
                        errors.append("Could not inspect tenant storage root permissions.")
            else:
                warnings.append("COPILOT_TENANT_DB_ROOT does not exist yet; this check does not create it.")
            inspect_database_path("COPILOT_CONTROL_DB", control)
            inspect_database_path("COPILOT_CORPUS_DB", corpus)
            passed.append("Separate control-plane, per-firm storage, and shared legal-corpus paths are configured.")

    else:
        errors.append(
            "All three profile-separated database paths are required; the shared COPILOT_DB runtime is retired."
        )
    if env.get("COPILOT_DB", "").strip():
        errors.append("COPILOT_DB is retired and must be unset in every environment.")
    return passed, warnings, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero if any warning remains; suitable for a release gate",
    )
    parser.add_argument(
        "--require-separate",
        action="store_true",
        help="fail unless control-plane, per-firm storage, and shared corpus paths are all configured",
    )
    args = parser.parse_args(argv)
    passed, warnings, errors = inspect_environment(require_separate=args.require_separate)

    for item in passed:
        print(f"PASS: {item}")
    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"FAIL: {item}")

    if errors or (args.strict and warnings):
        print("Preflight failed. Resolve the reported issues before deployment.")
        return 1
    if warnings:
        print("Preflight completed with warnings; use --strict for a release gate.")
    else:
        print("Preflight passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
