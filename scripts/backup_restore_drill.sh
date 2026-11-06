#!/usr/bin/env bash
# Witnessed encrypted tenancy backup/verify/restore drill.
# Run from the repository root with the application quiesced and BACKUP_KEY
# supplied by the protected secret manager. No credentials are generated here.
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/backup_restore_drill.sh BACKUP_DIR RESTORE_PARENT RESTORE_NAME

BACKUP_KEY must already be securely injected from the protected secret manager.\n\nExample paths (replace them; do not use production paths for a rehearsal):
  ./backups/drill  ./recovery-drills  restored-2026-11-06

The restore target must be a new, non-existent child of RESTORE_PARENT.
The operator must stop all application/background writers for the full backup
snapshot window and keep the original application pointed at its original data.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then usage; exit 0; fi
if [[ $# -ne 3 ]]; then usage >&2; exit 2; fi
if [[ -z "${BACKUP_KEY:-}" ]]; then
  echo "ERROR: BACKUP_KEY must be injected from the protected secret manager." >&2
  exit 2
fi

backup_dir=$1
restore_parent=$2
restore_name=$3

if [[ ! -d "$backup_dir" || -L "$backup_dir" ]]; then
  echo "ERROR: BACKUP_DIR must be an existing real directory." >&2
  exit 2
fi
if [[ ! -d "$restore_parent" || -L "$restore_parent" ]]; then
  echo "ERROR: RESTORE_PARENT must be an existing real directory." >&2
  exit 2
fi
if [[ "$restore_name" == "" || "$restore_name" == "." || "$restore_name" == ".." || "$restore_name" == */* ]]; then
  echo "ERROR: RESTORE_NAME must be one plain directory name." >&2
  exit 2
fi

restore_target="$restore_parent/$restore_name"
if [[ -e "$restore_target" || -L "$restore_target" ]]; then
  echo "ERROR: restore target already exists; choose a new destination." >&2
  exit 2
fi

echo "WITNESS CHECK: confirm all application and background writers are stopped."
read -r -p "Type QUIESCED to confirm the complete snapshot window is write-paused: " answer
if [[ "$answer" != "QUIESCED" ]]; then
  echo "Aborted: quiescence was not confirmed." >&2
  exit 2
fi

backup_log=$(mktemp)
trap 'rm -f "$backup_log"' EXIT

echo "[1/4] Creating encrypted tenancy bundle..."
python manage.py backup-tenancy "$backup_dir" --quiesced | tee "$backup_log"
bundle=$(sed -n 's/^Encrypted database bundle created: //p' "$backup_log" | tail -n 1)
if [[ -z "$bundle" || ! -f "$bundle" || -L "$bundle" ]]; then
  echo "ERROR: backup command did not identify a regular bundle file." >&2
  exit 1
fi

echo "[2/4] Verifying encrypted bundle before restore..."
python manage.py verify-backup-tenancy "$bundle"

echo "[3/4] Restoring to a new isolated directory..."
python manage.py restore-tenancy "$bundle" --target-root "$restore_target"

# The repository verifier performs a second isolated restore and checks SQLite
# integrity, foreign keys, tenant routing and original-object reconciliation.
export COPILOT_BACKUP_FERNET_KEY="$BACKUP_KEY"
echo "[4/4] Running full isolated recovery verification..."
python tools/run_database_recovery_drill.py --bundle "$bundle" --temp-parent "$restore_parent"

echo
echo "DRILL COMMANDS COMPLETED."
echo "Restored copy: $restore_target"
echo "WITNESS REQUIRED: inspect the restored profile inventory and SQLite integrity,"
echo "then rehearse startup against the restored paths in an isolated process."
echo "Do not switch production paths or claim recovery acceptance from this script alone."
