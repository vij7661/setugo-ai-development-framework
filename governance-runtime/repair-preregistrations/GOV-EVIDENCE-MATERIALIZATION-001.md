# GOV-EVIDENCE-MATERIALIZATION-001 — Non-file Review Evidence Materialization Repair

Status: PREREGISTERED BEFORE REPAIR

## Observed defect

IQR1 R2 and R3 independently identified that `governance-runtime/platform_candidate_review.py::build_corpus` silently ignores every declared `evidence_ref` whose `type` is not `file` via `if ref.get("type") != "file": continue`. The active REV-GOV-PR11-003 request includes `ci_run` and `history` evidence refs, so the candidate review path can omit declared evidence without failing closed.

## Frozen repair contract

1. No declared evidence ref may be silently ignored.
2. Supported non-file evidence types must be explicitly materialized into the reviewer corpus with stable identity and content.
3. Unsupported or malformed evidence types must fail closed before provider invocation.
4. `file` evidence behavior must remain exact-candidate bound.
5. `ci_run` evidence must bind the referenced GitHub Actions run to the reviewed candidate SHA and retain run identity/conclusion as data, not semantic authority.
6. `history` evidence must be materialized as the exact frozen request text and explicitly typed `history`; it cannot self-authenticate or override Git evidence.
7. Materialization failures must prevent provider invocation.
8. Regression tests must prove file, ci_run, history, unsupported-type, malformed-ref, candidate-mismatch, and provider-not-called-on-materialization-failure cases.
9. This repair does not authorize PR11 promotion by itself; a fresh candidate-bound review through the qualified path remains mandatory.

## Success condition

All frozen regression cases pass with zero silent ref drops and fail-closed behavior for unsupported/malformed/non-candidate-bound evidence. PR11 remains blocked pending fresh independent review.
