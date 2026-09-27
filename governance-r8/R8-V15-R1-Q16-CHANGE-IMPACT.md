# Q16 Change-Impact Record

## Lineage and state boundary

Q16 is constructed only from frozen Q15 commit `8ce8226818407924d81cee98a2800fc64d1797b1` (tree `a571f49f66f0543ac2f12bdf5b39db99d537a02c`). Candidate-local state is construction state and remains `PRE_FREEZE_READY`; it is not evidence of either a completed freeze or the absence of an external freeze. A post-freeze fact is represented only by an external v2 attestation. Review/merge evidence tooling requires that external attestation and does not accept the candidate-local queue or manifest as freeze proof.

## Finding dispositions and closure

### C-01 — REJECTED_UNSAFE_OR_OUT_OF_SCOPE

- Files changed: `standards/candidate-lifecycle-state-separation.md`, `tools/r8_work_queue.py`, `tools/test_r8_work_queue.py`, `governance-runtime/q15_review_merge_gate.py`.
- Root-cause family: prevented candidate-local post-freeze self-reference and made external lifecycle state a separate record.
- Cross-component effects: queue validation preserves pre-freeze construction state while the merge evidence gate requires an external v2 attestation.
- API effect: `CONTROL_PLANE_ONLY`; provider request schema and execution behavior unchanged.
- Preserved behavior: an externally frozen predecessor may remain internally pre-freeze without contradiction.
- Regression: malformed candidate-local/external lifecycle conflation is rejected; the merge gate cannot operate without external evidence.
- New defect check: no candidate-local file claims Q16 was frozen.

### H-01 — ACCEPTED_AS_PROPOSED

- Files changed: `tools/r8_v15_r1_independent_review_parser.py`, `tools/test_r8_v15_r1_independent_review_parser.py`, `governance-runtime/q15_review_merge_gate.py`, `governance-runtime/test_q15_review_merge_gate.py`.
- Root-cause family: the A-J review identity is structurally parsed and bound to expected identity, both execution statements, and the external attestation.
- Cross-component effects: baseline, candidate commit/tree, changed-file count, packet run/job, and Linux run/job must agree across all evidence layers.
- API effect: `EVIDENCE_ONLY`.
- Preserved behavior: valid negative reviews remain valid evidence but are never merge-eligible.
- Regression: cross-candidate commit, cross-baseline transition, stale run/job, and mismatched packet statement all fail.
- New defect check: matching bounded-pass evidence remains eligible only after external freeze verification.

### H-02 — ACCEPTED_AS_PROPOSED

- Files changed: `governance-runtime/provider_api_request_contract.py`, `governance-runtime/platform_candidate_review.py`, `governance-runtime/test_provider_api_request_contract.py`.
- Root-cause family: the real Gemini transport is derived from the canonical non-secret semantic specification.
- Cross-component effects: endpoint, method, payload, timeout, retry, streaming, and prompt/model inputs have one source of truth.
- API effect: `CONTROL_PLANE_ONLY`; `NO_API_REQUEST_SCHEMA_CHANGE`; `NO_API_EXECUTION_BEHAVIOR_CHANGE`.
- Preserved behavior: existing Gemini endpoint, POST, payload/generation parameters, 180-second timeout, one attempt, non-streaming response interpretation.
- Regression: mutations of URL, payload, timeout, or retry fail exact wire/projection comparison.
- New defect check: authentication remains transport-only and outside the projection.

### H-03 — ACCEPTED_WITH_ALTERNATIVE_SOLUTION

- Files changed: `governance-runtime/candidate_execution_evidence.py`, `governance-runtime/freeze_attestation.py`, `governance-runtime/test_candidate_execution_evidence.py`, `governance-runtime/test_freeze_attestation.py`, `governance-runtime/q15_review_merge_gate.py`, `governance-runtime/test_q15_review_merge_gate.py`.
- Root-cause family: external freeze attestation v2 binds independently hashed Linux and packet statements to the full candidate transition without equating workflow head and candidate SHA.
- Cross-component effects: later authorized evidence workflows can detach the candidate and emit run/job, workflow, baseline, commit/tree, changed-count, conclusion, and artifact digest.
- API effect: `EVIDENCE_ONLY`.
- Preserved behavior: the Q14 v1 attestation remains verifiable; no provider/model call is made.
- Regression: changed candidate, tree, baseline, count, run/job, digest, or statement hash fails.
- New defect check: Linux and packet statements must bind the same transition.

### H-04 — ACCEPTED_NARROWED

- Files changed: `.github/workflows/r8-v15-r1-post-sg1-integration-invariant-gate.yml`, `tools/verify_q16_invariant_workflow.py`, `tools/test_verify_q16_invariant_workflow.py`.
- Root-cause family: the active successor workflow explicitly executes every governed family and checks its own required command inventory.
- Cross-component effects: Q16 branch CI covers parsers, preflight, semantic inventory, runtime safety, evidence, queue, provider contract, delivery/materialization/integrity, attestation/gate, and syntax/clean-tree checks.
- API effect: `CONTROL_PLANE_ONLY`.
- Preserved behavior: workflow PASS grants no authority (`AUTHORITY_EFFECT=NONE`).
- Regression: deleting any required test command makes the workflow self-check fail.
- New defect check: the adversarial self-check itself is committed and run.

### M-01 — ACCEPTED_NARROWED; L-01 — ACCEPTED_AS_PROPOSED

- Files changed: `governance-runtime/provider_api_request_contract.py`, `governance-runtime/reviewer_evidence_delivery.py`, `governance-runtime/test_provider_api_request_contract.py`, `governance-runtime/test_reviewer_evidence_delivery.py`.
- Root-cause family: structured metadata keys are trim/case/hyphen normalized and recursively checked for governance and auth/secret variants.
- Cross-component effects: provider parameters, adapter/tool objects, and reviewer access manifests share fail-closed structured-secret handling.
- API effect: `API_ADMISSION_EFFECT`; admitted request wire semantics unchanged.
- Preserved behavior: ordinary natural-language message content is opaque and may contain those words.
- Regression: nested normalized governance keys and authorization/API-key/token/PAT/password variants fail; auth changes do not alter the semantic fingerprint.
- New defect check: secrets cannot persist in semantic evidence.

### M-02 — ACCEPTED_NARROWED

- Files changed: `governance-runtime/platform_candidate_review_v2.py`, `governance-runtime/reviewer_evidence_delivery.py`, `governance-runtime/test_platform_candidate_review_delivery_integration.py`.
- Root-cause family: the materializing/inlining platform v2 path accepts only `PLATFORM_MATERIALIZED_CONTENT`.
- Cross-component effects: MCP, provider URL context, and URL-only claims fail before provider invocation on this path.
- API effect: `API_ADMISSION_EFFECT`; no admitted logical request changes.
- Preserved behavior: complete platform-materialized requests still reach the mocked provider path.
- Regression: every mismatched mode, omitted manifest, incomplete delivery, or candidate/request mismatch proves zero provider calls.
- New defect check: delivery claims cannot exceed the integration actually used.

### M-03 — ACCEPTED_NARROWED; L-02 — ACCEPTED_AS_PROPOSED

- Files changed: `governance-runtime/reviewer_evidence_delivery.py`, `governance-runtime/platform_candidate_review_v2.py`, `governance-runtime/test_reviewer_evidence_delivery.py`, `governance-runtime/test_platform_candidate_review_delivery_integration.py`, `tools/verify_r8_v15_r1_post_sg1_integration_invariants.py`.
- Root-cause family: logical subject, source path, repository, immutable commit, object/blob ID, content digest, and byte count are distinct mode-specific fields.
- Cross-component effects: equal bytes from a wrong source path/object cannot satisfy delivery identity.
- API effect: `API_ADMISSION_EFFECT`.
- Preserved behavior: exact materialized corpus data and valid mode-specific manifests remain accepted.
- Regression: wrong source with matching bytes, incomplete MCP identity, mutable URL, and URL context without verified digest/bytes fail.
- New defect check: synthetic subject IDs no longer substitute for source-object identity.

### M-04 — REJECTED_UNSAFE_OR_OUT_OF_SCOPE

- Files changed: `standards/candidate-lifecycle-state-separation.md`, `governance-runtime/q15_review_merge_gate.py`.
- Root-cause family: the proposed in-tree `FROZEN` mutation is rejected because it recreates self-reference.
- Cross-component effects: external lifecycle evidence is mandatory for review/merge eligibility.
- API effect: `CONTROL_PLANE_ONLY`.
- Preserved behavior: candidate-local construction truth remains stable after the candidate SHA/tree is fixed.
- Regression: v2 external attestation is mandatory; candidate-local pre-freeze state cannot be used as post-freeze proof or disproof.
- New defect check: none; the rejected proposal is not implemented.

### I-01 — ACCEPTED_WITH_ALTERNATIVE_SOLUTION (implementer-discovered HIGH)

- Files changed: `tools/r8_v15_r1_independent_review_parser.py`, `tools/test_r8_v15_r1_independent_review_parser.py`.
- Root-cause family: bounded finding IDs support `C-01`, `H-01`, `M-01`, `L-01`, and generic `F-01`; the final candidate gate and identity labels are explicitly parameterized.
- Cross-component effects: the exact preserved Q15 review parses as `CHANGES_REQUIRED`; candidate labels bind to expected task identity.
- API effect: `EVIDENCE_ONLY`.
- Preserved behavior: ordered A-J grammar, severity row validation, uniqueness, and negative-disposition non-eligibility remain fail-closed.
- Regression: wrong candidate label, malformed/duplicate IDs, ID/severity mismatch, missing/reordered sections, negative dispositions, cross-candidate identity, and final-gate mismatch are exercised.
- New defect check: legacy A-H activation parsing is untouched and remains separately tested.

## Authority and stop boundary

Authority effect is `NONE`. Fallback-to-3 remains `ACTIVE`. Six-slice cadence is `NOT_RESTORED`. Q16 is not frozen; no Q16 Linux qualification evidence, review packet, external independent review, merge, activation, runtime qualification, release, deployment, or production action is performed by this construction record.
