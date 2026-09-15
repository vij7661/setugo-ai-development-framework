# V15 Independent Manual Evidence Review — Evidence Module 005

Status: **EXTERNAL MANUAL REVIEW EVIDENCE / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

`MODULE_REVIEWED = review_safe_evidence_v15_evidence.py`

`MODULE_COVERAGE = COMPLETE`

`V15_EXISTING_CRITICAL = CONFIRMED`

## New Critical findings

### C-EVIDENCE-01 — N/A challenge resolution can be fabricated

Function: `validate_na_challenge`.

`state="RESOLVED_SUPPORTED"` requires only a SHA-256-shaped `resolution_evidence_digest` and non-empty `resolution_verifier_id`; neither is bound to a real evidence artifact or verifier-authority registry. `verifier_independence_result` is also accepted as a caller assertion.

False-green path: fabricate a `RESOLVED_SUPPORTED` challenge, arbitrary format-valid resolution evidence digest and verifier ID, recompute `challenge_digest`; validation returns valid and `promotion_blocked=False`.

Required repair: bind resolution evidence to independently retrievable evidence and resolve the resolution verifier through a governed authority registry distinct from proof authority/verifier and challenger, with independently verified control-domain separation.

### C-EVIDENCE-02 — NOT_APPLICABLE_WITH_GOVERNED_PROOF is fully fabricatable

Function: `validate_not_applicable_proof`.

Proof/verifier identities and control domains are caller strings without role-registry resolution; `result`, `contradiction_state`, and challenge evidence digests are caller-provided. The independence subject cross-check is self-satisfiable by the same fabricator.

False-green path: invent distinct domain strings, fabricate an `INDEPENDENT` proof, set `result="NOT_APPLICABLE_SUPPORTED"`, `contradiction_state="NONE"`, `candidate_self_authored=False`, and format-valid challenge evidence digests. The proof validates without real evidence or authority.

Required repair: resolve proof authority/verifier through current role authority; derive result/contradiction from independently supplied evidence rather than caller labels; verify challenge evidence content.

## New High findings

### H-EVIDENCE-01 — Caller-controlled expected obligation universe

Function: `validate_evidence_registry`.

`expected_obligations` is caller supplied and not bound to the authoritative universe/obligation graph. Omitted obligations disappear from completeness checks.

Required repair: derive or exact-match the expected obligation set against the authoritative generation-bound obligation universe.

### H-EVIDENCE-02 — Raw evidence capture is unauthenticated

Function: `validate_raw_evidence_record`.

`capture_authority_id`, `capture_control_domain_id`, `source_identity`, `candidate_self_captured`, `source_digest`, and `payload_digest` are not tied to a role registry or actual source/payload bytes.

Required repair: resolve the capture authority through current governed roles and independently recompute evidence digests from real captured source bytes.

## Medium / Low

- Medium: N/A proof/challenge sequence expiry uses caller/orchestrator integers without authoritative clock/currentness binding.
- Low: `GENESIS`-rooted evidence-chain integrity is only self-consistency and is not anchored to prior authoritative registry state.

## Reviewer conclusion

The evidence/N/A subsystem does not mitigate the already-confirmed root-of-trust defect. It additionally allows the adversarial N/A challenge itself to be self-certified closed, collapsing the intended check-and-balance.

`NEXT_MODULE_RECOMMENDED = review_safe_evidence_v15_projection.py`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
