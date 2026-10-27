# Production release gate

Run the aggregate gate before any production launch:

    PYTHONPATH=. python tools/production_release_gate.py --out reports/production-release-gate.json

It combines three independent checks:

1. **Deployment configuration:** the strict deployment preflight must have no errors or warnings, including separate control-plane, per-firm, and shared legal-corpus database paths, secure public-origin/host settings, valid backup encryption, and administrator MFA policy.
2. **Legal corpus:** every candidate registry version must pass the read-only legal release readiness gate, including explicit collection and commercial-reuse permission evidence, original-file and extracted-text hashes, review evidence, and article/decision completeness checks.
3. **Lawyer-reviewed benchmark:** at least 94 questions spanning at least 10 practice areas must be lawyer-approved, each with a qualified Egyptian-counsel reviewer role, HTTPS review-evidence URL, non-future review date, expected answer, source IDs, and pin citations. Every expected source ID must have exactly one release-ready version active on the question's as-of date, and every expected pin cite must match an article/decision anchor recorded for that active version. Overlapping active versions are a release blocker. The benchmark must contain no unreviewed draft questions.

The current 94-question file is explicitly a draft for lawyer review, so the gate is expected to block release until a separate approved benchmark is created. Candidate registry files are also expected to remain blocked when permissions or legal-review evidence is missing. Do not edit the draft markers just to make the gate pass.

The gate is read-only with respect to legal documents, database schemas, and case data. It writes only the optional report file. It does not download law, contact rights holders, run the application, or send notifications.

A passing report means only that the recorded structural gates passed. It does not prove that the benchmark is statistically sufficient, a reviewer is qualified, permission evidence is authentic, or the application is legally correct or secure. The gate is a release checklist, not a substitute for legal review, independent penetration testing, backup-restore drills, and a controlled pilot.
