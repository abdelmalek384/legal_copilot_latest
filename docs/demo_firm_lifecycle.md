# Demo firm lifecycle

Demo firms are synthetic evaluation tenants, not customer workspaces. The provisioning command marks the firm with `is_demo=1`, creates fictional Arabic sample matters, and keeps it out of platform pilot aggregates and firm-admin exports. Never put real client or matter data in a demo firm.

## Create

Run in the profile-separated local or approved test environment:

```bash
python manage.py demo-firm create --owner-name "Demo Owner" --owner-email demo-owner@example.test
```

The command prompts for the demo owner's password. It prints the generated firm ID; retain that ID for removal. Sample records are explicitly fictional.

## Remove

```bash
python manage.py demo-firm remove --firm-id FIRM_ID --confirm-remove
```

Removal is deliberately destructive and requires explicit confirmation. It refuses firms not marked as demo, unsafe tenant database paths, unsafe SQLite sidecars, and any tenant whose original-file metadata cannot be verified or still contains an original-file object. The last guard prevents deleting the tenant database while leaving staged, ready, or quarantined original binaries orphaned in local or external storage.

If original-file objects remain, stop. Complete the approved firm-admin deletion request/independent approval and the applicable storage purge/reconciliation process first. Do not manually delete S3 objects or bypass legal holds. Re-run demo removal only after the tenant's original-file object table is empty and the normal retention/recovery requirements have been satisfied.

A successful demo removal revokes the firm's memberships, removes its tenant SQLite database and safe SQLite sidecars, and disables its tenant catalog entry. The control-plane firm record remains as a disabled `is_demo=1` record for lifecycle traceability. This command is not a general client-data erasure workflow and must never be used for a real firm.

## Safety boundaries

- Demo firms are excluded from firm exports and platform usage aggregates.
- Ordinary firm disablement preserves the tenant database and historical data; demo removal is a separate destructive operation restricted to `is_demo=1`.
- The removal command does not claim live S3/KMS production acceptance or perform an unreviewed object-store purge.
