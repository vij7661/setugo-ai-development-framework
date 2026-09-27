# Q15 — Q14 Review Remediation Successor

Tracker: GitHub issue #63

Exact frozen predecessor:
- commit: 01ec3651c9c0764e69944cd5718b07e4d30623b4
- tree: a61f1b0686c65719a83e0b065f5ac632f88cba96
- frozen ref: frozen/r8-v15-r1-q14-permanent-invariants-2026-09-27

Independent review:
- governance-r8/R8-V15-R1-Q14-INDEPENDENT-REVIEW-001.txt
- disposition: CHANGES_REQUIRED
- Critical: NONE
- High: F-01, F-02, F-03
- Medium: F-04, F-05, F-06
- Low: F-07

Codex must follow the adjudication in issue #63 exactly.

This task is one successor, not a return to multi-PR remediation.

Required:
- implement all accepted/narrowed/alternative fixes in issue #63;
- preserve the legacy SG1 A-H activation parser semantics;
- add a separate structural A-J independent-review parser/gate;
- wire reviewer evidence delivery into the real governed review path;
- add external freeze attestation/verification rather than mutating an already-frozen candidate;
- bind API request preservation to the real adapter-facing semantic request without changing provider request semantics;
- repair Q14/Q15 queue state/identity semantics;
- strengthen PROVIDER_URL_CONTEXT fetched-content identity;
- add family-level regressions and integration tests;
- no external provider API calls.

Stop before:
- freeze,
- qualification/evidence execution,
- fresh independent review,
- merge,
- activation,
- runtime qualification,
- release/deployment/production,
- any authority transition.

AUTHORITY_EFFECT = NONE.
Fallback-to-3 remains ACTIVE.
Six-slice cadence remains NOT restored.
