# Q15 Change-Impact Record

Source: issue #63 implementer adjudication. This is construction evidence only. It grants no freeze, merge, activation, runtime, release, deployment, production, policy, constitutional, root, or terminal authority.

## F-01 — ACCEPTED_NARROWED

- Files: `governance-runtime/platform_candidate_review_v2.py`, `governance-runtime/reviewer_evidence_delivery.py`, `.github/workflows/governance-candidate-platform-review.yml`, `governance-runtime/test_platform_candidate_review_delivery_integration.py`, `governance-runtime/test_platform_candidate_review_v2_materialization.py`, `governance-runtime/test_reviewer_evidence_delivery.py`.
- Invariant closed: the real materialization-v2 path requires an access manifest and binds provider identity, delivery mode, exact candidate commit, exact review request id/hash, and the complete set of materialized mandatory evidence identities before provider invocation.
- Cross-component effect: workflow trigger resolution, corpus materialization, delivery validation, and provider admission are connected; legacy materialization of file/history/ci_run remains fail-closed.
- API request effect: `API_ADMISSION_EFFECT`; admitted provider request semantics are unchanged.
- Preserved behavior: supported evidence still materializes byte-exactly; unsupported evidence still fails before provider invocation.
- Regression: real-path tests prove omitted manifest, URL_ONLY, incomplete delivery, candidate mismatch, and request mismatch never invoke the provider.

## F-02 — ACCEPTED_WITH_ALTERNATIVE_SOLUTION

- Files: `tools/r8_v15_r1_independent_review_parser.py`, `tools/test_r8_v15_r1_independent_review_parser.py`, `governance-runtime/q15_review_merge_gate.py`, `governance-runtime/test_q15_review_merge_gate.py`.
- Invariant closed: an independent A-J grammar requires exact ordered headings, structurally validates all four severity sections and the exact final gate, and separates valid evidence from bounded-merge eligibility.
- Cross-component effect: negative dispositions remain preserved review evidence but cannot become a clean gate result.
- API request effect: `CONTROL_PLANE_ONLY`.
- Preserved behavior: `tools/r8_v15_r1_review_contract_parser.py` and its A-H activation semantics are unchanged.
- Regression: adversarial duplicate/missing/reordered heading, malformed finding, final-field, disposition, and eligibility cases; preserved Q14 review 001 parses as `CHANGES_REQUIRED`.

## F-03 — ACCEPTED_WITH_ALTERNATIVE_SOLUTION

- Files: `governance-r8/freeze-attestations/Q14-FREEZE-ATTESTATION.json`, `governance-runtime/freeze_attestation.py`, `governance-runtime/test_freeze_attestation.py`, `governance-runtime/q15_review_merge_gate.py`, `governance-runtime/test_q15_review_merge_gate.py`.
- Invariant closed: an external attestation binds candidate commit/tree, frozen ref resolution, Linux run/job, packet run/job, authority NONE, fallback ACTIVE, and six-slice NOT_RESTORED without changing the frozen candidate.
- Cross-component effect: review/merge evidence eligibility now requires successful external freeze verification.
- API request effect: `EVIDENCE_ONLY`.
- Preserved behavior: candidate-internal pre-freeze state is not rewritten into a self-referential post-freeze claim.
- Regression: exact-ref/tree verification succeeds; identity, authority, fallback, and cadence tampering fails.

## F-04 — ACCEPTED_NARROWED

- Files: `governance-runtime/provider_api_request_contract.py`, `governance-runtime/platform_candidate_review.py`, `governance-runtime/test_provider_api_request_contract.py`.
- Invariant closed: forbidden governance keys are recursively rejected in structured provider parameters and structured message/tool/adapter objects.
- Cross-component effect: the check is exercised by the actual Gemini adapter-facing semantic projection.
- API request effect: `API_ADMISSION_EFFECT`; no schema or execution behavior change.
- Preserved behavior: arbitrary natural-language user/system content may mention governance-key words.
- Regression: nested `governance_review_blob`, `candidate_sha`, and `authority_effect` fail; prose containing those strings remains valid.

## F-05 — ACCEPTED_WITH_ALTERNATIVE_SOLUTION

- Files: `governance-runtime/provider_api_request_contract.py`, `governance-runtime/platform_candidate_review.py`, `governance-runtime/test_provider_api_request_contract.py`.
- Invariant closed: the real Gemini semantic projection contains endpoint/method/model/message/parameters/timeout/retry semantics and excludes authentication by construction.
- Cross-component effect: the adapter validates this projection before adding its API key to transport-only headers.
- API request effect: `CONTROL_PLANE_ONLY`; the HTTP payload, endpoint, method, timeout, and response handling remain unchanged.
- Preserved behavior: the existing Gemini invocation path and semantic payload are unchanged.
- Regression: the projection contains no auth/API-key fields, produces a stable fingerprint independently of credentials, and normalizes any non-secret semantic headers.

## F-06 — ACCEPTED_NARROWED

- Files: `governance-r8/CODEX-WORK-QUEUE-51.json`, `tools/r8_work_queue.py`, `tools/test_r8_work_queue.py`.
- Invariant closed: Q14 records its implementation branch separately from exact frozen candidate identity and attestation; Q15 is represented with explicit pre-freeze/review state.
- Cross-component effect: queue loading verifies the Q14 external attestation and exact identity equality, rather than checking Q-number membership only.
- API request effect: `EVIDENCE_ONLY`.
- Preserved behavior: the historical Q14 implementation branch retains its original meaning.
- Regression: Q14 state/commit/tree/ref/review state and Q15 runnable identity are asserted; disagreement with the attestation fails queue loading.

## F-07 — ACCEPTED_AS_PROPOSED

- Files: `governance-runtime/reviewer_evidence_delivery.py`, `governance-runtime/test_reviewer_evidence_delivery.py`.
- Invariant closed: mandatory `PROVIDER_URL_CONTEXT` objects require independently checked content SHA-256 and byte count in addition to an immutable locator.
- Cross-component effect: URL context without fetched-content identity cannot pass real-path delivery admission and must use materialized content instead.
- API request effect: `API_ADMISSION_EFFECT`.
- Preserved behavior: valid authenticated read-only and platform-materialized modes remain supported; URL_ONLY remains non-promotable.
- Regression: a commit-addressed URL without fetched-content identity is rejected.

## Operating boundary

### Pre-freeze Linux validation repair

- Candidate tested by Linux validation: commit `d7cf234653b9264d03d472b351b125f35a446a6b`, tree `a9a1b528c9952751e983c28a93bdcba533ad4dcc`.
- Preserved runs: `36270975410 / 108484736168`, `36271088620 / 108485055943`, and corrected exhaustive run `36271206089 / 108485381693`.
- Finding: the permanent-invariant verifier mechanically computed 53 baseline-to-candidate changed paths while the candidate manifest retained Q14's stale expected count of 37.
- Repair: `governance-r8/R8-V15-R1-POST-SG1-CONVERGENCE-MANIFEST.json` now declares the exact Q15 count, `53`.
- Mechanical invariant preserved: `tools/verify_r8_v15_r1_post_sg1_integration_invariants.py` continues to recompute the changed-path set and compare its length to the manifest; no hard-coded verifier bypass was added.
- Classification: `EVIDENCE_ONLY`; no provider API request schema or execution behavior effect.
- Closure proof: the permanent-invariant verifier must pass against the repaired exact Q15 HEAD, and the complete local matrix must remain green before push.

- `AUTHORITY_EFFECT = NONE`
- Fallback-to-3 remains `ACTIVE`.
- Six-slice cadence remains `NOT_RESTORED`.
- Q15 remains pre-freeze; no Q15 Linux qualification, packet generation, external review, merge, activation, runtime qualification, release, deployment, or production action was performed.
