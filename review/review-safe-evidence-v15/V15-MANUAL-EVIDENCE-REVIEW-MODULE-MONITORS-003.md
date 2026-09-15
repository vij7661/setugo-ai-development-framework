# V15 Manual Independent Evidence Review — Monitor Module — 003

Status: **MANUAL EXTERNAL EVIDENCE / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Reviewer result

- `MODULE_REVIEWED = review_safe_evidence_v15_monitors.py`
- `MODULE_COVERAGE = COMPLETE`
- `V15_EXISTING_CRITICAL = CONFIRMED`

## New Critical findings

### C-MON-001 — Coverage certificate not bound to the monitor bundle it certifies

Function: `validate_hidden_evidence_coverage_certificate`.

The reviewer found that `monitor_bundle_digest` is only checked for SHA-256 format and is not compared against the actual monitor bundle's `bundle_digest`. The function also consumes a caller-provided `monitor_result` mapping rather than recomputing the result from the bundle.

Concrete false-green: a caller can supply a fabricated `monitor_result={"valid": True, "reopen_required_obligations": []}` plus any well-formed unrelated digest and obtain a valid certificate with `promotion_blocked=False` without proving that `validate_hidden_monitor_bundle` ever ran on the referenced records.

Required repair: pass the actual bundle (or a verifier-computed digest/result derived from it), recompute validation internally, and require exact `record["monitor_bundle_digest"] == bundle["bundle_digest"]` binding.

### C-MON-002 — Entire monitor quorum is fabricatable with self-consistent records

Functions: `validate_independently_rooted_proof`, `validate_monitor_record`, `validate_hidden_monitor_bundle`.

The reviewer found that monitor identity, control domain, implementation identity/domain, independence proofs, currentness and `NO_REOPEN_FOUND` outcomes are all caller-asserted/self-hashed and are not authenticated against an independently maintained authority/ancestry/runtime-execution source.

Concrete false-green: fabricate >=3 monitor descriptors, >=2 domains, >=2 implementation roots, fabricated `INDEPENDENT` proofs, and a complete monitor×obligation set of `NO_REOPEN_FOUND` records. The bundle can validate and return `promotion_blocked=False` without any real monitor execution.

Required repair: recompute independence from an independently maintained ancestry/ownership graph; authenticate monitor authorities/implementations; bind monitor outputs to actual execution over the referenced raw-evidence root and obligation; do not accept a bare result enum plus digest as proof of execution.

## New High findings

### H-MON-001 — Coverage-certificate verifier independence is asserted, not proven

Function: `validate_hidden_evidence_coverage_certificate`.

`verifier_independence_result` is accepted as the string `INDEPENDENT` without a cross-checked independence proof tying the verifier's control domain to candidate and monitor domains.

Required repair: resolve verifier authority through the current role-authority registry and require independently verified control-domain ancestry/proofs against all prohibited domains.

### H-MON-002 — `expected_obligations` is caller-controlled and not bound to the authoritative obligation set

Functions: `validate_hidden_monitor_bundle`, `validate_hidden_evidence_coverage_certificate`.

A caller can pass a truncated obligation list, causing silence detection and certificate coverage to operate over only the narrowed set.

Required repair: derive the required obligation set from the authoritative obligation/materiality registry or bind an exact authoritative obligation-set digest and reject mismatch.

## Medium / Low findings

### M-MON-001 — Threshold field is not actual per-obligation quorum semantics

`threshold_control_domains` is only compared with configured domain count; per-obligation decision logic is full-mesh plus any-dissent-blocks. This is stricter, but the field name and contract are misleading.

### L-MON-001 — Implementation-diversity floor allows majority reuse

Only two distinct implementation identities/domains are required. A majority of monitors can still share one implementation while satisfying the diversity floor.

## Systemic assessment

This module does not mitigate the previously confirmed root-of-trust/authenticity defect. It repeats the self-hash pattern and introduces a concrete laundering path from fabricated monitor outputs into a valid coverage certificate.

`NEXT_MODULE_RECOMMENDED = review_safe_evidence_v15_review.py`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
