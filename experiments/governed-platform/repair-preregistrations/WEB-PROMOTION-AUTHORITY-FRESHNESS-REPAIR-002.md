# WEB-PROMOTION-AUTHORITY-FRESHNESS-REPAIR-002

## Trigger
Post-R2-002 adversarial challenge found that signed authority records in v2 prove origin/integrity but not currentness.

## Defect
- old signed HEAD_ATTESTATION can be replayed after authoritative head movement;
- credential attestations have no expiry/revocation epoch;
- authorization expiry is compared to caller-supplied `now_iso`, enabling clock rollback;
- caller-supplied source/artifact values remain unnecessary identity inputs when the RC already binds them.

## Frozen repair
1. Preserve v1/v2 and both false-green records.
2. Add v3 with platform-owned mutable authority state: monotonic `authority_epoch`, authoritative `current_time`, authoritative `current_head_sha`, and revoked credential identities.
3. Evaluation derives source SHA/artifact from the RC manifest and derives time/head from registry state; no caller `current_head_sha`, `credential_domain`, or `now_iso` authority inputs.
4. Current head, credential and production-authorization records bind the current authority epoch. Old-epoch records fail closed after any authority-state advance.
5. Credential record binds expiry; registry state supports revocation. Expiry/revocation checked against platform-owned time.
6. Authorization expiry checked against platform-owned time.
7. Head attestation must match registry current head and current epoch.
8. Production receipts are historical signed evidence and may remain valid for rollback across later epochs; receipt minting still requires a previously eligible production decision.
9. Same-artifact/build-once/evidence/ordered-transition/model-non-authority semantics remain unchanged.
10. This is still a deterministic reference trust boundary; durable registry persistence, KMS/HSM/key custody and distributed clock correctness are nonclaims.

## New cases
- PB3-01 exact current-epoch authority permits production eligibility.
- PB3-02 old head attestation rejected after head movement/epoch advance.
- PB3-03 old credential attestation rejected after epoch advance.
- PB3-04 revoked credential denied.
- PB3-05 expired credential denied using platform-owned time.
- PB3-06 caller cannot supply an alternate clock to rescue expired authorization.
- PB3-07 old production authorization rejected after epoch advance.
- PB3-08 fresh reissued authority after epoch advance works for current head only.
- PB3-09 RC source/artifact identity is derived, not caller-selected.
- PB3-10 epoch rollback is rejected.
- PB3-11 head changes require epoch advance.
- PB3-12 forged epoch fields fail signature verification.
- PB3-13 testing credential still denied.
- PB3-14 model/reviewer claim still has no authority.
- PB3-15 receipt minting requires eligible current decision.
- PB3-16 signed prior production receipt remains valid rollback evidence after later epoch advance.
- PB3-17 forged receipt remains invalid.
- PB3-18 original PB and PB2 suites remain regression-clean.
- PB3-19 deterministic decision stable within identical registry state.
- PB3-20 bounded nonclaims remain explicit.
