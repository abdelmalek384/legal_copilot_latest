# Device/browser acceptance evidence validator

The checklist remains a human-run test. To prevent incomplete or mismatched records from being counted as acceptance, validate each completed JSON evidence record (or JSONL/array of records) with:

    python tools/validate_device_browser_acceptance.py --input device-acceptance.json

A structurally valid record may still contain NOT_TESTED or BLOCKED; this command reports that state and does not turn it into a pass. For a release gate, require every listed check to pass, cover desktop and phone in both supported locales, and bind all records to the exact candidate commit:

    python tools/validate_device_browser_acceptance.py \
      --input device-acceptance.json \
      --expected-commit FULL_40_CHARACTER_COMMIT_SHA \
      --require-pass

The release gate requires four device-class/locale cells: desktop/ar-EG, desktop/en-US, phone/ar-EG, and phone/en-US. All records must refer to one commit and one environment. Additional OS/browser coverage in the manual runbook is still tracked separately.

Each passing record must include evidence paths. Failed or blocked checks must reference defect IDs. Duplicate records for the same commit/environment/locale/device/browser/viewport are rejected. This validator checks evidence structure and recorded outcomes only; it cannot independently verify screenshots, device behavior, tester identity, or the truth of a manually entered PASS.

For a `--require-pass` run, every evidence path is resolved relative to the evidence manifest's directory. Each path must identify an existing, non-empty regular file; absolute paths, parent-directory traversal, and symlinks are rejected. Keep the manifest and its evidence files together inside the restricted evidence workspace.
