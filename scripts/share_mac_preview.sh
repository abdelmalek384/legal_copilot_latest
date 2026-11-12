#!/usr/bin/env bash
# Temporary, email-restricted Cloudflare Quick Tunnel for a local fictional-data preview.
set -euo pipefail

if [[ "${COPILOT_ENV:-}" == "production" || "${COPILOT_ENV:-}" == "prod" ]]; then
  echo "Refusing to publish an app configured as production." >&2
  exit 2
fi

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared is required. On macOS with Homebrew, install it with: brew install cloudflared" >&2
  exit 2
fi

cloudflared_help="$(cloudflared tunnel --help 2>&1 || true)"
if [[ "$cloudflared_help" != *"--allowed-mail"* ]]; then
  echo "This cloudflared build does not advertise --allowed-mail. Update cloudflared before sharing." >&2
  exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to check the local application." >&2
  exit 2
fi

if ! curl --silent --show-error --fail --max-time 5 --output /dev/null http://127.0.0.1:8000/; then
  echo "Legal Copilot is not responding at http://127.0.0.1:8000." >&2
  echo "Start it first in another Terminal window with ./start_mac.command." >&2
  exit 2
fi

printf '\nEnter the exact email address(es) allowed through Cloudflare email PIN verification.\n'
printf 'For multiple addresses, separate them with commas and no spaces.\n'
read -r -p "Allowed email(s): " allowed_emails

if [[ -z "$allowed_emails" || "$allowed_emails" == *[[:space:]]* ]]; then
  echo "A non-empty comma-separated email list without spaces is required." >&2
  exit 2
fi

case "$allowed_emails" in
  ,*|*,|*,,*)
    echo "The email list contains an empty entry." >&2
    exit 2
    ;;
esac

cat <<'WARNING'

IMPORTANT — TEMPORARY PREVIEW ONLY
- Use fictional test matters and synthetic documents only.
- Do not enter real client data, confidential case files, passwords, or production secrets.
- The visitor must pass Cloudflare email PIN verification AND the Legal Copilot sign-in.
- This temporary URL changes when the tunnel restarts and has no uptime guarantee.
- Keep this Mac awake and connected while the lawyer tests.
- Press Ctrl+C here to stop external access; stop the app separately in its Terminal window.

Type SHARE FICTIONAL DATA to continue.
WARNING

read -r -p "> " confirmation
if [[ "$confirmation" != "SHARE FICTIONAL DATA" ]]; then
  echo "Cancelled. No tunnel was started."
  exit 0
fi

exec cloudflared tunnel --url http://127.0.0.1:8000 --allowed-mail "$allowed_emails"
