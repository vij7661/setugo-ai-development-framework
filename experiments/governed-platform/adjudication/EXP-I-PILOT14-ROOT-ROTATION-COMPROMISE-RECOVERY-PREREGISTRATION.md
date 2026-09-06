# EXP-I Pilot 14 — Trust-Registry Root-Key Rotation and Compromise Recovery

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Parent evidence
- Parent: EXP-I Pilot 13 — trust-registry root isolation and rollback containment.
- Parent adjudication commit: `bf91bc40100fb65242cd5c0c3014c943d34b3829`.
- Evaluated Pilot 13 head: `1d251a52b8c2f7913b746de414f707bfbb9728fd`.
- Pilot 13 bounded result: P13-01..P13-16 passed; full governor suite 1010/1010.
- Pilot 13 explicitly did not prove protection after root private-key compromise, root-key rotation/revocation, secure compromised-root recovery, threshold/multi-root authority, HSM/KMS custody, or independent administrative trust domains.

## Scientific question
Can the trust-registry root itself move from R1 to R2 and later R3 while preventing a historically valid but revoked/compromised prior root from authorizing current registry transitions, restoring stale trust history, or rewriting the root lineage?

## Frozen hypothesis
For the tested same-host prototype, root eligibility must be governed by a durable platform root-trust authority separate from every root signer and from the checkpoint-signing trust registry. Root signers may sign registry transitions only while their exact root id, public-key fingerprint and root epoch are currently ACTIVE. A root signer has no API or credential that can activate, revoke, rotate, roll back or widen its own root eligibility. Readers must verify both the registry-event signature and the externally governed root lineage/current eligibility. Cryptographic validity under a revoked R1 remains historical evidence only and cannot authorize current trust-registry mutation or current eligibility after R2 activation. Exact transition replay remains idempotent; semantic rebinding, root-epoch rollback, stale-root replay and root identity/key substitution fail closed. Clean R1→R2→R3 rotation remains live.

## Frozen architecture
- Root signature scheme remains Ed25519.
- Root signers are distinct subprocesses with separate durable signing/replay stores.
- A separate durable `PlatformRootTrustAuthority` controls root eligibility; no root signer receives its mutation surface.
- Root-trust records form an authenticated append-only chain binding: schema/version, root epoch, transition id, prior root id/status, active root id, active public-key fingerprint/public material, activation registry epoch, predecessor root-record digest, and record authentication.
- Exactly one root is ACTIVE for current root epoch in this bounded pilot.
- Trust-registry transition statements additionally bind `root_epoch` and `root_record_digest` as well as root id.
- Before signing a registry transition, a root signer independently reads the current root-trust view and may sign only if its id/fingerprint is ACTIVE at the exact current root epoch.
- Registry readers independently read current root trust at use time. Signature math under an old root is necessary for historical audit but insufficient for current eligibility.
- Root rotation is one platform-authorized atomic root-trust transition: prior root becomes REVOKED and next root becomes ACTIVE.
- Root-trust mutation remains external to models, reviewers, checkpoint signers, registry writers/readers/verifiers and root signers.
- The existing Pilot 13 trusted-minimum registry authority remains in force; Pilot 14 does not weaken it.

## Frozen primary falsifiers
Exactly sixteen primary cases must exist before first scientific execution.

### P14-01 — root trust authority is distinct and roots cannot self-rotate
Expected: R1/R2/R3 root signers have no root-trust mutation methods or root-trust private authority; only the external platform root-trust authority can mutate eligibility.

### P14-02 — clean R1 baseline
Expected: root epoch 1 authorizes the exact R1 id/fingerprint and an R1-signed trust-registry transition verifies under current root eligibility.

### P14-03 — clean atomic R1→R2 rotation
Expected: one external platform transition advances root epoch exactly once, revokes R1, activates R2 and binds the exact predecessor root record; no current view exposes two active roots.

### P14-04 — cryptographically valid R1 rejected for new current transition after revocation
Expected: an authentic post-rotation R1 signature may be mathematically valid but is semantically ineligible to authorize a new current trust-registry transition.

### P14-05 — stale pre-rotation R1 root-trust snapshot cannot restore R1
Expected: a coherent old root-trust database/view below the current independently trusted root minimum cannot re-enable R1.

### P14-06 — root epoch rollback denied
Expected: after root epoch 2, a caller/verifier/signer view claiming epoch 1 cannot authorize current mutation or verification.

### P14-07 — root-id substitution denied
Expected: an R1 signature labeled R2 or an R2 signature labeled R1 is rejected.

### P14-08 — root public-key/fingerprint substitution denied
Expected: replacing public key/fingerprint beneath a registered root id cannot authenticate or authorize the registry transition.

### P14-09 — revoked-root exact old signature cannot be rebound to new registry semantics
Expected: a valid historical R1 signature cannot be replayed against changed registry epoch, key identity, activation generation, predecessor or transition id.

### P14-10 — transition-id replay remains idempotent across root rotation
Expected: exact replay of a previously committed registry transition returns the original result without a duplicate registry event or root-trust mutation.

### P14-11 — same transition identity semantic rebinding denied across rotation
Expected: reusing an existing transition id with changed registry semantics or a different root is rejected.

### P14-12 — concurrent R1 issuance versus R1→R2 rotation has one authoritative outcome
Expected: racing an R1 registry transition with R1 revocation/R2 activation cannot produce two accepted current outcomes; post-rotation eligibility is deterministic and fail closed.

### P14-13 — R1 outage blocks R1 mutation but does not block verification of valid historical material
Expected: unavailable R1 cannot mint; already committed valid R1 history remains historically auditable subject to current root-trust semantics.

### P14-14 — R2 restart preserves active-root and replay enforcement
Expected: restarting R2 does not erase root-epoch eligibility, exact-transition replay memory, monotonic registry-transition memory or predecessor binding.

### P14-15 — compromised/revoked R1 plus registry-writer collusion has zero current root or production authority
Expected: possession/use of R1 signing capability plus mutable registry storage after R1 revocation cannot create a current trusted registry history without current root eligibility. No model/reviewer/writer/verifier/root signature confers release/production/merge/approval authority.

### P14-16 — clean R2→R3 second rotation liveness
Expected: after valid R1→R2 and at least one R2-authorized registry transition, external platform root trust advances to epoch 3, revokes R2, activates R3, and an exact next R3-authorized registry transition succeeds once with correct root and registry predecessor lineage across restarts.

## Primary endpoints
1. unauthorized root-trust mutation;
2. simultaneous active-root ambiguity;
3. current acceptance of revoked-root signatures;
4. root-epoch rollback/stale-root reactivation;
5. root identity/public-key substitution;
6. historical-signature semantic rebinding;
7. duplicate registry transition under replay/race;
8. clean two-step root rotation liveness.

Any root self-authorization, accepted revoked-root current transition, stale-root rollback, identity/key substitution, semantic rebind, duplicate current transition, or broken clean R1→R2→R3 liveness falsifies Pilot 14 on the exercised path.

## Evidence and repair rules
- All P14-01..P14-16 execute in the first scientific run.
- No endpoint or expected outcome may be removed, weakened or reworded after exposure.
- First-run failures are preserved and classified before repair.
- Repair scope is diagnosis-bound and minimal.
- Full governed-platform regression suite reruns after any repair.
- Workflow SUCCESS is operational evidence only, never scientific approval by itself.
- Pilot 13 ResourceWarning cleanup debt is not a Pilot 14 scientific endpoint and must not be silently mixed into root-rotation claims.

## Explicit non-claims
A Pilot 14 pass will not prove HSM/KMS private-key nonextractability, recovery from simultaneous compromise of both the active root and the external root-trust authority, independent administrative trust domains, threshold/multi-root authorization, secure remote root transport, hardware attestation, physical power-loss durability, multi-host or Byzantine consensus, production CA/PKI correctness, production/release authority, or universal reviewer correctness.

## Authority rule
Only the external platform root-trust authority may change root eligibility. Root signers authenticate registry-transition content only while externally eligible and cannot self-authorize or modify their own trust. Registry/root signatures and verification results are evidence inputs only and do not confer production, release, merge or approval authority.
