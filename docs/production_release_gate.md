# Production release gate

Run the aggregate gate before any production launch. It is read-only with respect to application data and corpus artifacts; it reads controlled evidence files and writes only the optional report.

Provide the exact commit being released and the restricted manual device/browser evidence file:

    COPILOT_RELEASE_COMMIT=<full-40-character-release-sha> \
    COPILOT_DEVICE_ACCEPTANCE_FILE=/secure/release/device-acceptance.json \
    PYTHONPATH=. python tools/production_release_gate.py --out reports/production-release-gate.json

The same inputs can be passed explicitly with `--release-commit` and `--device-acceptance`. The gate fails closed if either is missing, the evidence is malformed, any required check is not PASS, records refer to another commit or mixed environments, or the minimum desktop/phone × Arabic/English matrix is incomplete. See [the manual device/browser acceptance runbook](device_browser_acceptance_runbook.md) and [validator guide](device_browser_acceptance_validator.md).

It combines four independent checks:

1. **Deployment configuration:** the strict deployment preflight must have no errors or warnings, including separate control-plane, per-firm, and shared legal-corpus database paths, secure public-origin/host settings, valid backup encryption, and administrator MFA policy.
2. **Database operational acceptance:** the controlled manifest must document required original-file storage, backup/restore, retention-policy, identity-email, privileged-recovery, and independent security-review evidence.
3. **Legal corpus:** every candidate registry version must pass the read-only legal release readiness gate, including explicit collection and commercial-reuse permission evidence, original-file and extracted-text hashes, review evidence, and article/decision completeness checks.
4. **Lawyer-reviewed benchmark:** at least 94 questions spanning at least 10 practice areas must be lawyer-approved, each with a qualified Egyptian-counsel reviewer role, HTTPS review-evidence URL without credentials, query strings, or fragments, non-future review date, expected answer, source IDs, and pin citations. Every expected source ID must have exactly one release-ready version active on the question's as-of date, and every expected pin cite must match an article/decision anchor recorded for that active version. Overlapping active versions are a release blocker.

5. **Manual device/browser acceptance:** the evidence records must bind to the exact release commit and one environment, include desktop and phone in both supported locales (ar-EG and en-US), and show PASS for every mandatory workflow in every record. The evidence validator checks structure and recorded outcomes; it cannot prove that the tester actually performed the checks or that screenshots are authentic.

The current 94-question file is explicitly a draft for lawyer review, so the gate is expected to block release until a separate approved benchmark is created. Candidate registry files are also expected to remain blocked when permissions or legal-review evidence is missing. Device acceptance is also expected to block release until real manual evidence is collected. Do not edit draft markers or fabricate device evidence just to make the gate pass.

The gate is read-only with respect to legal documents, database schemas, and case data. It does not download law, contact rights holders, run the application, or send notifications. It validates recorded evidence only.

A passing report means only that the recorded structural gates passed. It does not prove that a reviewer is qualified, permission evidence is authentic, the manual device tests were truthfully performed, the benchmark is statistically sufficient, or the application is legally correct or secure. The gate is a release checklist, not a substitute for legal review, independent penetration testing, backup-restore drills, and a controlled pilot.
