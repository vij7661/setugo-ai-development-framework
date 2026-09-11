# RELEASE R3 — Release Trust-Root Publication Preregistration

Status: FROZEN_BEFORE_PUBLICATION
Authority effect: NONE_EVIDENCE_ONLY

## Subject

Exact RELEASE candidate SHA under qualification:
`ffec566022fcd221fb4ab7569ed3bc245f75b546`

## Exposed defect being repaired

The existing pinned external trust root `SETUGO_MANUAL_GOVERNANCE_ED25519_V1` is explicitly scoped to TESTING verification only, while candidate policy v6 permits RELEASE terminal authority classes. Reusing the TESTING root for RELEASE authority would exceed the published trust-root scope.

## Frozen repair boundary

A distinct RELEASE-scoped Ed25519 public trust root will be published before any RELEASE terminal attestation is accepted.

The RELEASE root must:

1. have a distinct trust-root ID;
2. contain public verification material only;
3. be stored outside the candidate repository;
4. be bound to the exact published repository identity and immutable commit;
5. declare RELEASE authority scope only for `HUMAN_RELEASE_AUTHORITY` terminal decisions;
6. never contain or receive the private signing key;
7. preserve the existing TESTING root unchanged;
8. require successor policy and verifier logic to select the trust root by phase/authority scope rather than silently widening the TESTING root;
9. fail closed when a TESTING root is supplied for RELEASE authority or a RELEASE root is supplied for TESTING authority;
10. require fresh exact-SHA qualification after the successor policy/verifier repair.

## Public key supplied for the RELEASE root

Algorithm: Ed25519

SubjectPublicKeyInfo DER (Base64):
`MCowBQYDK2VwAyEAbjtVTgMo4352bmjD7YBb+m6ywoUzqvkGJx+Nsrl952Q=`

DER SHA-256:
`91355cf1049a27aac52ea56f5ba1664054aded93500203cd23d557a710b0444c`

This is public verification material. No private key material is recorded here.

## Acceptance rule

No `MERGE_RELEASE_CANDIDATE` attestation may be generated or treated as valid until the RELEASE-scoped root publication, successor policy/verifier repair, negative-control tests, and exact-SHA requalification are complete.
