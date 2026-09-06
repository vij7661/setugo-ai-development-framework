# EXP-I Pilot 12 — Checkpoint Signer Key Rotation and Revocation

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Parent evidence
- Parent: EXP-I Pilot 11 — asymmetric verify-only composite checkpoint authentication.
- Parent adjudication commit: `5af7c814c9a940a1aec6870a324d43a5b0f741b6`.
- Pilot 11 bounded result: P11-01..P11-16 passed; full governor suite 978/978.
- Pilot 11 explicitly did not prove production-scale key rotation, revocation, compromise recovery, HSM/KMS custody, or protection after signer-key compromise.

## Scientific question
Can checkpoint signing-key trust move from K1 to K2, and later to K3, without allowing a cryptographically valid but revoked/stale key to regain authority, without allowing the signer to modify its own trust status, and without breaking clean checkpoint lineage/liveness?

## Frozen hypothesis
For the tested same-host prototype, checkpoint-key trust must be issued by a platform trust-registry authority separate from signer, writer and verifier. The registry binds an exact trust epoch, key id, public-key fingerprint, activation generation and status. Signers may sign only under a currently authorized key but cannot create, activate, revoke, retire, roll back or widen their own trust records. Verifiers must distinguish cryptographic validity from semantic trust eligibility: a signature under revoked or stale K1 may still be mathematically valid but must not become CURRENT after the frozen revocation/rotation boundary. Trust-registry rollback, stale cache, key-id substitution, public-key substitution and mixed-key lineage must fail closed. Clean K1→K2 and K2→K3 rotation must remain live.

## Frozen architecture
- Signature scheme remains Ed25519.
- Trust registry is a durable SQLite authority store distinct from signer issuance ledger and writer journal.
- Registry mutation is exposed only through a platform trust-authority object/process; signer, writer and verifier receive read/verify surfaces only.
- Each trust record binds: registry schema/version, trust epoch, key id, SHA-256 public-key fingerprint, activation generation, status (`ACTIVE`, `RETIRED`, `REVOKED`), predecessor trust-record digest, and record digest/authentication.
- Exactly one key may be ACTIVE for a trust epoch/current issuance generation range.
- Checkpoint signed statement binds both `key_id` and `trust_epoch`.
- Signer independently reads the current trust registry before issuance and may sign only when its key id/fingerprint is ACTIVE for the requested exact-next generation.
- Verifier independently reads the trust registry at use time. Signature validity is necessary but insufficient; key id/fingerprint/trust epoch/status/generation eligibility must all match.
- Rotation K1→K2 is platform-authorized: K1 becomes RETIRED or REVOKED according to the frozen transition and K2 becomes ACTIVE atomically in one registry transaction. For this pilot, the security revocation case uses `REVOKED` for K1.
- Old checkpoint history may remain cryptographically auditable, but a revoked key cannot authorize new CURRENT promotion or use-time trust after its revocation boundary.
- Signer has zero API to mutate registry trust records.

## Frozen primary falsifiers
Exactly sixteen primary cases must exist before first scientific execution.

### P12-01 — trust registry is distinct and signer cannot mutate it
Expected: registry is a distinct durable authority store; signer/writer/verifier cannot call activate/revoke/rollback or directly obtain registry mutation authority.

### P12-02 — clean K1 baseline
Expected: trust epoch 1 authorizes exact K1 fingerprint; generation 1 signed by K1 verifies and becomes CURRENT.

### P12-03 — clean atomic K1→K2 revocation/rotation
Expected: one platform-authorized transition advances trust epoch exactly once, revokes K1 and activates K2 with the frozen activation generation; no interval exposes two active keys.

### P12-04 — cryptographically valid K1 rejected after revocation
Expected: an authentic K1 signature remains mathematically verifiable but is semantically ineligible for CURRENT/use-time trust after K1 revocation.

### P12-05 — new K1 issuance blocked after revocation
Expected: K1 signer cannot issue generation 2 or later after the registry activates K2.

### P12-06 — key-id substitution denied
Expected: K1 signature labeled as K2, or K2 signature labeled as K1, is rejected.

### P12-07 — public-key fingerprint substitution denied
Expected: replacing the registered public key/fingerprint beneath an existing key id does not authenticate or authorize the checkpoint.

### P12-08 — trust-epoch rollback denied
Expected: after trust epoch 2, a registry or verifier view claiming trust epoch 1 cannot re-enable K1 for current use.

### P12-09 — stale registry/cache cannot re-enable revoked K1
Expected: verifier restart or cached prior-positive K1 verification cannot substitute for a fresh current trust-registry read when current eligibility is required.

### P12-10 — mixed-key lineage substitution denied
Expected: generation-2 K2 checkpoint must bind the exact generation-1 predecessor; an unauthorized Kx or mismatched-key predecessor cannot manufacture a valid lineage.

### P12-11 — exact K2 replay is idempotent
Expected: exact same K2 issuance identity/generation/current governed state returns the same checkpoint without duplicate CURRENT rows.

### P12-12 — concurrent rotation versus issuance has one authoritative outcome
Expected: racing K1 issuance with K1→K2 rotation cannot produce two accepted current trust outcomes; post-commit eligibility is deterministic and fail closed.

### P12-13 — signer restart preserves active-key and trust-epoch enforcement
Expected: restart does not cause signer to use stale K1 after K2 activation and does not erase replay/monotonic issuance state.

### P12-14 — verifier restart uses current registry, not stale positive proof
Expected: a fresh verifier rejects post-revocation K1 for current eligibility even when an earlier verifier had positively authenticated the same signature before revocation.

### P12-15 — authority separation remains zero outside platform trust authority
Expected: models, reviewers, writers, verifiers and checkpoint signers cannot alter trust records or gain production/release/merge/approval authority from key status, signatures or verification results.

### P12-16 — clean K2→K3 second rotation liveness
Expected: after valid K1→K2 transition and generation 2, platform advances to trust epoch 3, revokes/retires K2 according to policy, activates K3 for exact next generation, and generation 3 signs/verifies once with correct predecessor and trust lineage across restarts.

## Primary endpoints
1. unauthorized registry mutation;
2. simultaneous active-key ambiguity;
3. acceptance of revoked K1 for current use;
4. post-revocation issuance by K1;
5. key-id/fingerprint substitution acceptance;
6. trust-epoch rollback acceptance;
7. stale verifier/cache promotion;
8. mixed-key predecessor/lineage acceptance;
9. duplicate CURRENT generation during replay/race;
10. clean two-step rotation liveness.

Any unauthorized trust mutation, accepted revoked-key CURRENT/use-time trust, post-revocation K1 issuance, trust-epoch rollback, stale-cache reactivation, key/fingerprint substitution, duplicate active trust outcome, or broken clean K1→K2→K3 liveness falsifies Pilot 12 on the exercised path.

## Evidence and repair rules
- All P12-01..P12-16 execute in the first scientific run.
- No endpoint or expected outcome may be removed, weakened or reworded after exposure.
- First-run failures are preserved and classified before repair.
- Repair scope is diagnosis-bound and minimal.
- Full governed-platform regression suite reruns after any repair.
- Workflow SUCCESS is operational evidence only, never scientific approval by itself.

## Explicit non-claims
A Pilot 12 pass will not prove HSM/KMS private-key nonextractability, secure recovery after an actually compromised active private key, protection from same-user/host-admin/kernel/hypervisor compromise, independent administrative trust domains, threshold/multi-signer authority, secure remote trust-registry transport, distributed consensus, production CA/PKI correctness, hardware attestation, physical power-loss durability, production/release authority, or universal reviewer correctness.

## Authority rule
Only the external platform trust-registry authority may change signing-key eligibility. A signer may authenticate checkpoint content only under current registry authorization and may not self-authorize its own key. A verifier reports cryptographic/trust eligibility only. None of these artifacts alone confer production, release, merge or approval authority.
