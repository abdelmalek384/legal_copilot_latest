

## Machine validation of recorded evidence

The checklist above remains a human-run test. To prevent incomplete or mismatched records from being counted as acceptance, validate each completed JSON evidence record (or JSONL/array of records) with:

```bash
python tools/validate_device_browser_acceptance.py --input device-acceptance.json
```

A structurally valid record may still contain `NOT_TESTED` or `BLOCKED`; this command reports that state and does not turn it into a pass. For a release gate, require every listed check to pass and bind the evidence to the exact candidate commit:

```bash
python tools/validate_device_browser_acceptance.py \
  --input device-acceptance.json \
  --expected-commit FULL_40_CHARACTER_COMMIT_SHA \
  --require-pass
```

Each passing record must include evidence paths. Failed or blocked checks must reference defect IDs. Duplicate records for the same commit/environment/locale are rejected. This validator checks evidence structure and recorded outcomes only; it cannot independently verify screenshots, device behavior, tester identity, or the truth of a manually entered PASS.
