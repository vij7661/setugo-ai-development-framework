# V24-I11-V6 Successor-4 — External Root Attestation Repair Design

Status: **PREREGISTERED AFTER PRESERVED RED / IMPLEMENTATION NOT YET QUALIFIED**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Predecessor and falsification

Frozen predecessor:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-3`
- commit: `b4b91dcf5855ae2bb7162c0b94d1a79a8a64e171`
- tree: `a81204c73016243556c6eefd711bc91c37adda49`
- manual review disposition: `CHANGES_REQUIRED`

Successor-4 preserved RED:
- workflow run: `35318618058`
- test: `test_same_process_caller_cannot_self_update_anchor_and_self_grant`
- observed false-green: attacker-created proof context + attacker-created trusted boundary + attacker rewrite of `V24_V6_TRUSTED_BOUNDARY_ANCHOR_SHA256` returned `qualified=True`, `PROOF_REFERENCE_CLOSED`, no problems.

The RED is a genuine mechanism defect. It is not a fixture defect and must never be relabeled as PASS.

## 2. Root cause

Successor-3 replaced a context-derived boundary with an environment-provided SHA-256 digest. That is still symmetric and caller-mintable:

`attacker_boundary -> exported digest function -> caller-writable environment -> validator accepts`

The candidate therefore did not have a root of trust; it had a self-consistency check across two caller-controlled values.

## 3. Required successor-4 invariant

A proof context may contribute to construction qualification only if its exact context identity is attested by a root authority the candidate/caller cannot mint.

The authority-bearing attestation MUST bind at least:
- attestation schema/version;
- fixed root key identity;
- governance generation ID;
- exact proof-context digest;
- exact genesis trusted-scope digest;
- cryptographic signature over the canonical attestation material.

The validator MUST use one pinned public verification key. The caller may not select or replace that key.

## 4. Construction root artifact

Separate trust branch:
`trust/v24-v6-construction-root-attestation-v1`

Public artifact:
`trust/v24-v6-construction-root-attestation-v1.json`

Exact Git blob:
`a82495c2486f6c25a4aeca01473ea45f818364a7`

Key identity:
`V24-V6-CONSTRUCTION-ROOT-ATTESTATION-V1`

Algorithm:
`RSA-PKCS1-v1_5-SHA256`

Public-key DER SHA-256:
`8f28d28b8a81b33393107e9b18b7a0a4e85227c5f2f537e357fd9181d1c99c01`

The private signing half is not committed and must not be available to candidate Python.

This key is construction-only. It does not claim production key lifecycle, HSM/KMS custody, runtime process isolation, release authority, or scientific authority.

## 5. Prohibited repair shapes

The following do not close PRC-1:
- another environment variable;
- a caller-supplied expected digest;
- a caller-supplied public key;
- a caller-supplied verification callback;
- HMAC/MAC verification using a secret readable by candidate Python;
- a test helper that silently grants arbitrary contexts;
- documentation-only separation;
- checking only genesis ID/digest pairs while leaving the entire proof context unauthenticated.

## 6. Test-fixture strategy

Current R2-R8 construction tests dynamically build deterministic proof contexts. Successor-4 may use pre-signed deterministic construction fixture contexts, but:
- only exact pre-attested context digests may pass;
- no signing private key may exist in the repository or candidate process;
- an unknown/resealed context must fail unless it has a separately issued external signature;
- fixture signatures are evidence for construction tests only and cannot be runtime authority;
- the signer/private key must not be callable from candidate production functions.

## 7. Mandatory permanent regressions

At minimum:

1. `SAME_PROCESS_ANCHOR_REWRITE_REJECTED`
   - attacker builds proof context;
   - attacker builds trusted boundary;
   - attacker computes the old SHA-256 boundary digest;
   - attacker sets the old environment variable to that exact digest;
   - production resolver must reject.

2. `UNSIGNED_CONTEXT_REJECTED`
   - exact structurally valid context and boundary, no external attestation -> reject.

3. `WRONG_CONTEXT_SIGNATURE_REJECTED`
   - reuse a valid signature from context A on context B -> reject.

4. `CALLER_SELECTED_PUBLIC_KEY_REJECTED`
   - caller supplies its own key/signature pair -> reject.

5. `ATTESTATION_SCOPE_SUBSTITUTION_REJECTED`
   - signed context digest paired with different genesis scope/generation -> reject.

6. `SIGNED_CONTEXT_POSITIVE`
   - exact pre-attested deterministic construction fixture -> proof closure succeeds.

7. Existing DA-1 and NCP-1 regressions remain mandatory under the externally attested root.

## 8. R9/freeze impact

The root-attestation verifier becomes a new load-bearing shared production dependency and MUST be included in the integrated successor freeze.

The successor manifest must also bind the exact public-root artifact identity. Final-head CI must independently fetch the trust branch and verify that exact public artifact before the candidate can be packaged for manual review.

The old environment anchor must not appear in the authority path.

## 9. Relationship to R14/R16 design work

R14/R16 already established the stronger runtime principle:
- candidate Python is untrusted execution;
- authority material must live outside candidate mutable Python state/address space;
- no authority secret may be candidate-readable;
- a trusted parent/oracle derives authority-bearing evidence externally.

Successor-4 construction attestation adopts the same direction but does **not** claim that runtime/native isolation is solved merely by adding asymmetric context signatures.

Runtime/scientific progression remains blocked until the external/native authority boundary is separately qualified.

## 10. Progression rule

Successor-4 may be frozen for manual review only after:
- preserved RED remains historical;
- all six root-attestation regressions are GREEN;
- full R1-R9/proof-resolution suite is GREEN;
- inherited V24 suite is GREEN;
- R9 dependency freeze includes the new root-attestation verifier;
- exact public-root artifact is independently verified;
- scientific execution remains closed;
- runtime qualification remains unclaimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
