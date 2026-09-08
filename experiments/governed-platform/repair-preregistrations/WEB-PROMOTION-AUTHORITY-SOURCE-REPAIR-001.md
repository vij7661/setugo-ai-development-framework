# WEB-PROMOTION-AUTHORITY-SOURCE-REPAIR-001

## Trigger
Post-R2 adversarial inspection of candidate `bb2a591d6fa9d6da507d6ff6aa8f444784a57651` found a real authority-source false green after authenticated R2 PASS.

## Defect
The v1 gate validated equality of caller-supplied `credential_domain` and `current_head_sha`, and allowed construction of a Production Authorization from an arbitrary nonempty `authorization_evidence_digest`. These values looked authoritative without proving they originated in platform-owned authority state.

## Frozen repair boundary
1. Preserve v1 implementation and R2 PASS history; do not rewrite them.
2. Add v2 rather than weakening tests.
3. Introduce a platform-owned authority registry using deterministic HMAC attestations under a key unavailable to untrusted caller/model input.
4. Production evaluation must require a valid signed current-head attestation bound to the exact source SHA.
5. Production evaluation must require a valid signed production-credential attestation; raw `credential_domain="production"` is no longer an authority input.
6. Production Authorization must be issued by the registry, bind the exact RC manifest/source/artifact, and require a bound `PRODUCTION_AUTHORIZATION` evidence object rather than an arbitrary digest string.
7. Caller-fabricated or tampered head, credential, authorization, or evidence records must fail closed.
8. Model/reviewer claims remain evidence only.
9. Rollback eligibility must require a signed prior PRODUCTION receipt created only from a successful production-eligible decision, not mere possession of an unused authorization.
10. Preserve build-once/same-artifact, exact evidence binding, expiry, ordered transition, replay/non-rebind, and bounded nonclaims.

## New falsification cases
- PB2-01 valid signed head + production credential + bound authorization permits exact RC.
- PB2-02 caller string `credential_domain=production` has no API path to production authority.
- PB2-03 forged head attestation denied.
- PB2-04 head attestation for another SHA denied.
- PB2-05 forged production credential attestation denied.
- PB2-06 testing credential attestation denied.
- PB2-07 forged production authorization denied.
- PB2-08 authorization evidence for another artifact denied at issuance.
- PB2-09 authorization rebinding/tampering denied.
- PB2-10 expired authorization denied.
- PB2-11 head drift denied even with otherwise valid authorization.
- PB2-12 model/reviewer production claim cannot bypass missing platform authority.
- PB2-13 production receipt can only be minted from an eligible exact production decision.
- PB2-14 rollback accepts a signed prior production receipt for the exact artifact.
- PB2-15 unused authorization alone cannot authorize rollback.
- PB2-16 forged/tampered production receipt cannot authorize rollback.
- PB2-17 all original PB-01..PB-16 semantics remain regression-clean where applicable.
- PB2-18 deterministic outputs remain stable for identical trusted inputs.

## Nonclaim
HMAC registry is a deterministic reference trust boundary, not an HSM/KMS/secret-manager or production key-custody proof. Real production key custody remains future infrastructure work.
