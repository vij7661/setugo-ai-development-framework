# V24-I11-V6 Successor-4 — Root Attestation Materialization Amendment

Status: **PREREGISTRATION AMENDMENT / IMPLEMENTATION STAGE 1**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Preserved predecessor

The original Successor-4 design remains preserved at:

- `implementation/v24/V24-I11-V6-SUCCESSOR-4-ROOT-TRUST-REPAIR-DESIGN.md`
- original public-root branch: `trust/v24-v6-construction-root-attestation-v1`
- original public-root blob: `a82495c2486f6c25a4aeca01473ea45f818364a7`
- original key id: `V24-V6-CONSTRUCTION-ROOT-ATTESTATION-V1`

No earlier RED, GREEN, manual-review disposition, or root-of-trust finding is reclassified.

## 2. Materialization gap

Before production wiring, implementation inspection found that V1 contained the public verification key but no materialized pre-signed deterministic proof-context attestations. The V1 private signing half is intentionally unavailable to candidate/implementation Python and is not committed.

Therefore V1 could not satisfy the preregistered positive-control requirement without either:

1. reintroducing a signing secret into the candidate/repository, or
2. pretending that unsigned construction fixtures were externally attested.

Both shapes are prohibited.

This is classified as a **preregistration materialization gap**, not a mechanism PASS and not a reason to weaken the asymmetric-root invariant.

## 3. Replacement construction root

Replacement trust branch:

`trust/v24-v6-construction-root-attestation-v2`

Public artifact:

`trust/v24-v6-construction-root-attestation-v2.json`

Exact Git blob:

`5708cdd000474a305100f8736a7386c9f4e3aeb5`

Key identity:

`V24-V6-CONSTRUCTION-ROOT-ATTESTATION-V2`

Algorithm:

`RSA-PKCS1-v1_5-SHA256`

Public-key DER SHA-256:

`fe0f6526541361070cd4e609f49dfe9d2153fb599157ef25e0dda442a099ae65`

The V2 private half was generated and used transiently only to issue deterministic construction fixture signatures. It is not committed and must not be present in candidate-readable state.

## 4. Stage-1 invariant

The construction verifier must:

- pin V2 key identity and public key in production code;
- reject caller-selected modulus, exponent, key digest, callback, or verification key;
- reject unsigned contexts;
- reject a signature issued for a different exact context digest;
- reject generation or genesis-scope substitution;
- ignore the old mutable environment anchor as an authority source;
- preserve `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`;
- preserve `RUNTIME_QUALIFICATION = NOT_CLAIMED`.

Stage 1 proves only the cryptographic construction-root primitive. It does not yet claim that R2-R8 or the integrated successor have been migrated to require the attestation.

## 5. Mandatory progression after Stage 1

Before Successor-4 may be frozen for manual review:

1. wire the attestation verifier into `validate_proof_context`;
2. remove the old environment digest from the authority-bearing path;
3. migrate deterministic R1-R9 construction fixtures to externally pre-signed attestations;
4. retain permanent same-process anchor rewrite, unsigned, wrong-signature, caller-key, and scope-substitution regressions;
5. rerun full R1-R9/proof-resolution and inherited V24 suites;
6. bind the exact V2 root artifact blob in the integrated successor manifest/freeze;
7. run exact final-head verification;
8. package only the frozen exact bytes for independent manual review.

Scientific/runtime execution remains closed throughout this amendment.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
