# TESTING Qualification Boundary — External Test Harness Preregistration 009

Status: `FROZEN_BEFORE_REPAIR`
Authority effect: `NONE_EVIDENCE_ONLY`
Exposed candidate SHA: `61e98ba0ca8fc461b407e91e4f60ffc687fc784e`
Trigger: strengthened independent R8 review returned `CHANGES_REQUIRED` and exposed a new HIGH false-green path in the external checker test harness.

## Frozen finding R9-01 — candidate-controlled qualification tests

The external checker MUST NOT treat unpinned candidate-controlled unittest files as authoritative qualification evidence. Every candidate test module whose success contributes to external qualification MUST either:

1. be independently pinned by exact Git blob SHA before execution; or
2. be replaced by checker-owned adversarial tests whose code is outside the candidate repository.

Changing, weakening, skipping, deleting, or substituting any qualification-contributing candidate test while leaving the pinned production implementation unchanged MUST fail external qualification.

The frozen invoked candidate test set at exposure is:

- `test_phase_policy.py`
- `test_manual_authority_verifier.py`
- `test_manual_authority_signed_attestation.py`
- `test_external_governance_root.py`
- `test_external_root_policy_binding.py`
- `test_external_trust_root_control.py`
- `test_qualification_boundary_unittest_bridge.py`
- `test_review_protocol.py`
- `test_review_semantics.py`
- `test_review_classification.py`
- `test_single_file_review_container.py`
- `test_platform_candidate_review_request_integrity.py`

## R9-02 — checker revision residual

GitHub required-status rules bind context plus App integration ID, not check-run `external_id`. Therefore the system MUST NOT claim the branch rule itself pins an exact checker SHA. The protected checker repository, protected credential environment, exact checker SHA recorded in the check run, and independent review evidence may bound this residual, but a future mechanism must fail closed if candidate-controlled code can select or alter the checker revision. Unknown materiality fails closed.

## Successor lineage requirement

The eventual repaired candidate MUST be a distinct exact SHA from `61e98ba0...`. Its exact SHA must be recorded only after it exists, then receive fresh candidate CI, fresh external qualification under the repaired harness, and fresh independent re-falsification. No prior PASS may be replayed.

All evidence remains `NONE_EVIDENCE_ONLY`; no terminal authority is created by this repair.