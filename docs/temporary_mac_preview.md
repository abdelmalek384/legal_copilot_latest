# Temporary Mac preview for a lawyer (fictional data only)

**Purpose:** let one or a few invited testers open the existing web app from their own browser without buying hosting or opening an inbound firewall port. This is a temporary development preview, not a production deployment.

## What this does

- Runs Legal Copilot on the owner's Mac using the existing local launcher.
- Keeps Uvicorn bound to `127.0.0.1:8000`; the application port is not opened to the LAN or Internet.
- Uses a Cloudflare Quick Tunnel with its email allowlist (`--allowed-mail`) to require a one-time email PIN before a visitor reaches the app.
- Still requires the visitor to sign in to Legal Copilot with their own firm account.
- Requires no domain or Cloudflare account for the temporary Quick Tunnel.

Cloudflare documents Quick Tunnels as testing/development only. The hostname is random and changes on restart, the tunnel stops when its process stops, and it has no uptime guarantee. It supports up to 200 in-flight requests and does not support Server-Sent Events. See [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

## Strict safety boundary

- **Fictional data only.** Do not enter real client identities, confidential matters, real case files, credentials, or production data.
- Do not enable external LLM processing. Keep `LLM_DATA_PROCESSING_APPROVED` and `LLM_FIRM_DATA_PROCESSING_APPROVED` unset.
- Do not use this as a production firm service, permanent URL, backup solution, or evidence of security certification.
- The Mac is the application host and database store. It must remain awake, online, and running both processes.
- Cloudflare's email PIN is an extra access gate, not a replacement for Legal Copilot authentication, firm membership, MFA policy, or application authorization.
- A user who passes the email gate can reach the login page. Only invite known testers and retain the application's own account controls.
- Stop the tunnel immediately after the test. Stop the app in its own Terminal window.
- Do not install the PWA for ongoing use from a temporary URL; the hostname changes on restart.

## One-time setup on the Mac

Use a **separate clean clone** so this preview cannot reuse or modify an existing development checkout, local owner configuration, or private database files:

```bash
git clone --branch feat/protected-mac-preview-tunnel --single-branch https://github.com/abdelmalek384/legal_copilot_latest.git legal-copilot-preview
cd legal-copilot-preview
```

Install Cloudflare's connector with Homebrew:

```bash
brew install cloudflared
cloudflared --version
```

The helper checks that the installed `cloudflared` command advertises the `--allowed-mail` option. If it does not, update it before proceeding. The email-restricted Quick Tunnel option was added in cloudflared 2026.9.3; see the official Quick Tunnel documentation.

## Start a temporary preview

**Terminal 1 — start Legal Copilot locally:**

```bash
./start_mac.command
```

Complete the first-firm bootstrap with a dedicated synthetic test firm and test-owner account. Keep this terminal open. The app should report that it is listening on `http://127.0.0.1:8000`.

**Terminal 2 — start the restricted tunnel:**

```bash
bash scripts/share_mac_preview.sh
```

Enter only the tester's exact email address (or a comma-separated list of exact addresses, without spaces). Confirm the explicit fictional-data warning. The script checks the local app, then starts Cloudflare's temporary tunnel. Share the generated `https://….trycloudflare.com` URL only with those testers.

The tester must:
1. Open the temporary URL.
2. Complete the Cloudflare email PIN check using an allowlisted address.
3. Sign in to Legal Copilot using their own test account and firm membership.
4. Use fictional clients, matters, documents and research questions only.

## Stop and clean up

1. Press Ctrl+C in Terminal 2 to terminate the tunnel and remove external reachability.
2. Press Ctrl+C in Terminal 1 to stop Legal Copilot.
3. Keep the synthetic test database only if it is useful for another controlled test; otherwise follow the reviewed demo-firm cleanup procedure. Do not delete database files manually.

## What this does not solve

This gives a temporary URL, not a reliable hosted service. It does not provide a stable domain, uptime, managed backups, production object storage, independent security review, privacy-counsel approval, verified Egyptian legal content, or production operations. The production deployment remains blocked until the documented S3/KMS, accepted database manifest, secrets, SMTP, backup/restore, security, privacy and legal gates are completed. See [Deploy Legal Copilot](DEPLOY.md), [the production checklist](production_deployment_checklist.md), and [the PWA installation/privacy limits](pwa_installation.md).

The PWA can be installed only after the app is served over HTTPS, but installation does not make the app offline or remove its dependency on this Mac and tunnel.
