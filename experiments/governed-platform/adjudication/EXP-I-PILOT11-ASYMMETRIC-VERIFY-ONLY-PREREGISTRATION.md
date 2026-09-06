# EXP-I Pilot 11 — Asymmetric Verify-Only Composite Checkpoint Authentication

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Parent evidence
- Parent: EXP-I Pilot 10 — isolated composite-checkpoint signing authority.
- Parent adjudication commit: `90ff38e6274b5523bd919d9e6c9ef538d04fa3f4`.
- Pilot 10 bounded result: P10-01..P10-16 passed; full governor suite 962/962.
- Pilot 10 explicitly did not prove asymmetric verify-only separation or private-key nonextractability.

## Scientific question
Can checkpoint verification be separated from checkpoint minting so that writers and verifiers require only a public key, never the private signing key and never online signer availability, while the isolated signing authority still independently binds current governed state and preserves monotonic issuance/replay rules?

## Frozen hypothesis
For the tested same-host prototype, a distinct signer process must hold the only private checkpoint-signing key. Writer and verifier processes must receive only the corresponding public verification key and must be able to authenticate exact signed checkpoints without any signing capability. A public key, prior valid checkpoint, signer response, or verifier success must never be sufficient to mint or semantically widen a checkpoint. The signer must continue to independently derive governed state, enforce generation/predecessor/issuance identity/replay/rebinding rules, and fail closed on signing unavailability. Verification may remain live during signer outage for already-issued material.

## Frozen architecture
- Signature scheme: Ed25519 using a fixed preregistered key identity for this bounded prototype.
- Signer process owns the private key and a distinct durable issuance ledger.
- Writer/verifier receive only the public key and fixed key id.
- Canonical signed statement binds: schema/version, key id, scope, issuance id, generation, predecessor digest, permit-ledger digest, reconciliation-ledger digest, permit-authority epoch, and checkpoint body digest.
- Signer independently derives all governed-state fields except the narrow issuance identity and requested generation.
- Verification is local/public-key-only and performs canonical decoding, signature verification, key-id match, scope/version match, predecessor/generation checks, and current-state checks where required by use-time policy.
- Private-key retrieval/export is absent from writer/verifier APIs.
- A signer outage may block new issuance but must not block cryptographic verification of already-issued material.

## Frozen primary falsifiers
Exactly sixteen primary cases must exist before first scientific execution.

### P11-01 — signer owns private key; writer/verifier do not
Expected: signer process has the private key; writer/verifier construction, env, argv, request and object surfaces do not.

### P11-02 — public key cannot mint
Expected: writer/verifier using only public material cannot create any checkpoint accepted as signer-authenticated.

### P11-03 — clean generation-1 issue and offline verify
Expected: signer derives current governed bindings, signs generation 1, writer persists it, and a verifier authenticates it using only the public key.

### P11-04 — verifier succeeds while signer is unavailable
Expected: already-issued valid checkpoint remains cryptographically verifiable with signer stopped; no new issuance is possible.

### P11-05 — signer outage blocks new writer mutation
Expected: no new CURRENT generation is persisted when private signer is unavailable.

### P11-06 — private-key substitution denied
Expected: checkpoint signed by an unrelated private key is rejected even if structurally valid.

### P11-07 — public-key/key-id substitution denied
Expected: altered key id or verifier key substitution cannot authenticate a checkpoint under the frozen key identity.

### P11-08 — signed-field mutation denied
Expected: mutation of any canonical bound field invalidates the signature.

### P11-09 — writer-supplied governed semantic fields rejected
Expected: writer cannot choose ledger digests, epoch, predecessor, scope, key id, signature or arbitrary signed body.

### P11-10 — exact replay idempotent
Expected: exact same issuance identity/generation/current state yields the same accepted checkpoint without duplicate CURRENT rows.

### P11-11 — same-generation competitor denied
Expected: distinct issuance identity cannot obtain a second accepted issuance for the already-issued generation.

### P11-12 — rollback and generation skip denied
Expected: after generation N, requests for N-1 or N+2 are denied; only exact next generation is eligible.

### P11-13 — signer restart preserves monotonicity and replay
Expected: restart does not erase generation, predecessor, issuance identity or replay memory.

### P11-14 — stale valid signature cannot become current after governed-state drift
Expected: cryptographic validity alone is insufficient to promote stale material after current ledger/epoch state changes.

### P11-15 — model/reviewer/writer/verifier authority remains zero
Expected: valid signatures or verifier success grant no production, release, merge, approval or self-issued mutation authority.

### P11-16 — clean generation-2 liveness after signer/verifier restart
Expected: after valid generation 1 and governed-state change, signer restarts, independently derives current state, signs exact generation 2 once, and a fresh public-key-only verifier validates the correct lineage.

## Primary endpoints
1. private-key possession outside signer;
2. successful mint using public material only;
3. dependency on online signer for verification of prior valid material;
4. fail-open issuance during signer outage;
5. acceptance under wrong key/key id;
6. signed-field mutation acceptance;
7. writer control over governed semantic fields;
8. rollback/skip/conflict/rebinding acceptance;
9. stale cryptographically valid material promoted as current after state drift;
10. clean restart and higher-generation liveness.

Any observed private-key possession by writer/verifier, successful public-key-only mint, wrong-key acceptance, fail-open issuance during signer outage, accepted signed-field mutation, semantic rebinding, duplicate CURRENT generation, or stale-state promotion falsifies Pilot 11 on the exercised path.

## Evidence and repair rules
- All P11-01..P11-16 execute in the first scientific run.
- No endpoint or expected outcome may be removed or weakened after execution.
- First-run failures are preserved verbatim and classified before repair.
- Repairs require the smallest authorized artifact scope.
- Full governed-platform regression suite reruns after any repair.
- Workflow SUCCESS is operational evidence only, never scientific approval by itself.

## Explicit non-claims
A Pilot 11 pass will not prove HSM/KMS private-key nonextractability, protection from host-admin/kernel/hypervisor compromise, multi-signer threshold authority, independent administrative trust domains, networked remote signer security, key rotation/revocation at production scale, hardware-backed attestation, physical power-loss durability, multi-host consensus, production/release authority, or universal reviewer correctness.

## Authority rule
The signer is platform authority only for narrowly bound checkpoint signing. The verifier proves signature validity; it does not confer production/release authority. Models, reviewers, writers and verifiers remain non-authoritative execution/reasoning components beneath the governance layer.
