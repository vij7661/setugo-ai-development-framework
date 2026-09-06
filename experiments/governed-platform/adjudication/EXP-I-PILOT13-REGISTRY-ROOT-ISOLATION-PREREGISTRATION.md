# EXP-I Pilot 13 — Trust-Registry Root Isolation and Compromise Containment

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Parent evidence
- Parent: EXP-I Pilot 12 — checkpoint signer key rotation and revocation.
- Parent adjudication commit: `16c2ed8ff69ec22feab659d16d17c3737936a0a0`.
- Pilot 12 evaluated SHA: `5ef36d6af3861ffa5ac69a21d1e4e8fe255d5f81`.
- Pilot 12 bounded result: P12-01..P12-16 passed; full governor suite 994/994.
- Pilot 12 explicitly did not prove integrity after compromise of the trust-registry authority/key itself, HSM/KMS custody, independent trust domains, or distributed consensus.

## Scientific question
Can trust-registry history remain fail-closed against coherent rollback/rewrite, old-valid replay and root/key substitution when registry transition signing is isolated from ordinary registry access and verifiers enforce a pinned public root plus a monotonic trusted-minimum trust epoch?

## Frozen hypothesis
For the tested same-host prototype, the trust-registry private signing key must exist only inside a distinct authority subprocess boundary. Ordinary registry database writers/readers, checkpoint signers, checkpoint verifiers, models and reviewers receive no private root key and no root-mutation API. Every registry transition is signed by the isolated root authority and bound to exact predecessor digest, trust epoch, active key identity/fingerprint, activation generation and transition type. Verification must use a pinned root public key and a durable monotonic minimum trust epoch external to the mutable registry database. A mathematically valid historical registry chain below that minimum, a coherently rewritten database, or a substituted root must not restore revoked checkpoint-signing keys to current eligibility.

## Frozen architecture
- Signature scheme remains Ed25519.
- Registry transition signer is a distinct subprocess with its own durable issuance/monotonic state and private root PEM inaccessible through ordinary registry surfaces.
- Registry database contains signed transition events only; it does not contain the root private key.
- Registry reader receives only pinned root public key material.
- A separate trusted-minimum store records the minimum acceptable trust epoch and corresponding event digest; ordinary registry mutation cannot lower it.
- Registry events bind: registry version, trust epoch, event type, prior key id/status, active key id, active public key fingerprint/material, activation generation, predecessor event digest, signer root id.
- Exact replay of an already committed transition is idempotent; semantic rebinding of an issuance identity/epoch is denied.
- Verification requires a complete chain from GENESIS through current event, valid root signatures, exact predecessor linkage, unique epochs/key ids, fingerprint integrity, and satisfaction of the trusted minimum.
- Historical cryptographic validity is not equivalent to current trust eligibility.
- Root-authority outage blocks new trust transitions but must not prevent public-key verification of already committed history above the trusted minimum.
- No registry or checkpoint signature grants production/release/merge/approval authority.

## Frozen primary falsifiers
Exactly sixteen primary cases must exist before first scientific execution.

### P13-01 — root signer process is distinct and private key is absent from ordinary surfaces
Expected: registry DB/reader/checkpoint signer/verifier/model/reviewer surfaces expose no root private key or root-signing mutation method.

### P13-02 — clean inherited K3 baseline verifies above trusted minimum
Expected: a valid Pilot-12-style trust history through K3 is accepted when signed by the pinned isolated root and minimum epoch/digest match.

### P13-03 — coherent registry rollback to old valid epoch is denied
Expected: replacing current registry DB with an older fully valid signed chain below trusted minimum fails closed.

### P13-04 — coherent registry rewrite with locally consistent fields but no current root signature is denied
Expected: attacker cannot rewrite active key/fingerprint/epoch/predecessor and recompute local digests into acceptance.

### P13-05 — old valid root-signed chain cannot reactivate revoked K1
Expected: historical K1/K2-valid records remain auditable but cannot become current after minimum advanced through K3.

### P13-06 — substituted root public key is denied
Expected: verifier configured with an unrelated or attacker-generated public root cannot authenticate the registered lineage under the pinned-root policy.

### P13-07 — root-id/public-key binding substitution is denied
Expected: changing root id while retaining key, or key while retaining root id, does not preserve trust eligibility.

### P13-08 — trusted-minimum epoch rollback is denied
Expected: lowering minimum epoch without matching external authority is rejected and cannot re-enable stale registry state.

### P13-09 — trusted-minimum event-digest substitution is denied
Expected: same-or-higher epoch with wrong minimum event digest cannot authorize a different chain.

### P13-10 — registry event deletion/reordering/duplicate epoch is denied
Expected: deletion, reordering, duplicate epoch, predecessor break or key-id reuse fails closed.

### P13-11 — exact transition replay is idempotent
Expected: exact same transition identity and bound semantics returns the same committed event without duplicate epoch/current state.

### P13-12 — same transition identity semantic rebinding is denied
Expected: same identity/epoch cannot be reused for a different active key, fingerprint, generation or predecessor.

### P13-13 — root-authority outage blocks mutation but not verification
Expected: no new registry transition can commit while root signer is unavailable; already committed current history remains publicly verifiable.

### P13-14 — root-authority restart preserves monotonicity and replay memory
Expected: restart does not permit lower epoch, duplicate conflicting epoch, or forgotten replay binding.

### P13-15 — signer/registry collusion attempt has no root or production authority
Expected: checkpoint signer plus mutable registry DB access, without isolated root private key/current minimum authority, cannot mint accepted trust history; models/reviewers gain zero authority.

### P13-16 — clean K3→K4 transition liveness
Expected: isolated root signs exact-next trust epoch, K3 is revoked/retired by frozen policy, K4 activates at exact next generation, trusted minimum advances, and current verification succeeds across restart exactly once.

## Primary endpoints
1. private root-key leakage to ordinary surfaces;
2. old-valid registry rollback acceptance;
3. coherent unsigned/re-signed registry rewrite acceptance;
4. revoked-key reactivation from historical history;
5. root/public-key substitution acceptance;
6. trusted-minimum rollback/substitution acceptance;
7. event deletion/reorder/duplicate/rebinding acceptance;
8. mutation during root outage;
9. monotonic/replay loss after root restart;
10. clean next-rotation liveness.

Any private root-key exposure outside the isolated authority, accepted old-valid rollback below minimum, accepted coherent rewrite without current root authority, root substitution, minimum rollback, post-restart monotonicity loss, unauthorized trust mutation or broken clean K3→K4 liveness falsifies Pilot 13 on the exercised path.

## Evidence and repair rules
- All P13-01..P13-16 execute in the first scientific run.
- No endpoint or expected outcome may be removed, weakened or reworded after exposure.
- First-run failures are preserved and classified before any repair.
- Repair scope is diagnosis-bound and minimal.
- Full governed-platform regression suite reruns after any repair.
- Workflow SUCCESS is operational evidence only, never scientific approval by itself.

## Explicit non-claims
A Pilot 13 pass will not prove HSM/KMS private-key nonextractability, protection from same-user/host-admin/kernel/hypervisor compromise, secure recovery after actual theft of the isolated root private key, independent administrative trust domains, threshold/multi-party registry authority, cross-host distributed consensus, secure remote signer transport, hardware attestation, physical power-loss durability, production CA/PKI correctness, production/release authority, or universal reviewer correctness.

## Authority rule
Only the isolated platform trust-root authority may sign new trust transitions, and only the external trusted-minimum authority may advance the minimum accepted trust epoch/digest. Neither may infer authority from model/reviewer output. Checkpoint signers, registry readers, verifiers, models and reviewers have zero trust-mutation, production, release, merge or approval authority.
