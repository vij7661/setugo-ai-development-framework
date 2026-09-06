# EXP-I Pilot 10 — Isolated Composite-Checkpoint Signing Authority

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Parent evidence
- Parent: EXP-I Pilot 9 — external subprocess termination around composite-checkpoint issuance and recovery.
- Parent adjudication commit: `598eac5da910e4e0607984964e46a01be3c40147`.
- Pilot 9 bounded result: P9-01..P9-14 passed on the exact `DurableCompositeJournalAuthority.issue()` path after preserving the first-run harness correspondence defect; full governor suite 946/946.
- Pilot 9 explicitly did not prove that the writer process lacks composite-checkpoint signing/authentication material.

## Scientific question
Can composite-checkpoint minting authority be removed from the writer process so that a compromised, restarted, duplicated, or stale writer cannot independently mint an authenticated checkpoint, while exact issuance/replay/recovery remains live through a separate platform-owned authority process?

## Frozen hypothesis
For the tested same-host prototype, the writer process must possess no composite checkpoint signing key and no API for raw-key retrieval. A distinct signer authority process must own the key and a separate durable issuance ledger, independently derive the current permit/reconciliation/epoch bindings from platform-owned durable state, enforce monotonic generation, predecessor, issuance identity, replay and semantic-rebinding rules, and return only narrowly bound signed checkpoint material. Signer unavailability or ambiguity must fail closed. A writer may persist signer-authorized material but may not manufacture or widen it.

## Frozen architecture
### Isolated signer authority
A distinct Python subprocess:
- owns the raw composite HMAC key only in its child environment;
- owns a separate SQLite signer ledger, distinct from the composite journal database path;
- has read access to the platform state database needed to derive the current permit-ledger digest, reconciliation-ledger digest and permit-authority epoch itself;
- derives the required predecessor from the durable signer lineage rather than trusting a writer-supplied predecessor;
- accepts only a narrow request containing operation, issuance identity and requested generation plus expected scope/version metadata;
- constructs the canonical checkpoint statement itself;
- commits its issuance record before returning a positive issue response;
- rejects generation rollback, skipped predecessor lineage, same-generation conflict, issuance semantic rebinding and scope/version substitution;
- exact replay of the same issuance identity/generation/bound state is idempotent;
- retains monotonic issuance memory across signer restart;
- supports verification of a presented signed checkpoint without exposing the raw key;
- exposes no production/release/merge/approval authority.

### Writer
The writer:
- receives no composite signing key in argv, environment, request payload or object attributes;
- cannot call a local signing primitive with the composite key;
- requests signed checkpoint material from the signer;
- persists only exact signer-issued material into the composite journal;
- uses a conditional/unique durable journal write so duplicate/replayed writers cannot create two CURRENT rows for one generation;
- must fail closed if the signer is unavailable, denies the request, or returns malformed/binding-mismatched material;
- may not infer authority from prior signer success after current platform state has drifted.

### Verification/recovery
- Current-checkpoint verification requiring authentication goes through the signer authority path in this bounded symmetric-key experiment.
- A fresh writer/signer pair may replay an exact previously committed issuance after restart.
- This pilot does not claim verify-only asymmetric cryptographic separation; writer non-possession is process isolation, not HSM/KMS custody.

## Frozen primary falsifiers
Exactly sixteen primary cases must exist before first scientific execution.

### P10-01 — distinct signer process and store
Expected: signer PID differs from writer/test process and signer issuance store path differs from composite journal path.

### P10-02 — writer has no composite signing key
Expected: raw key absent from writer env/argv/request/object surface; no key-return operation exists.

### P10-03 — clean signer-derived generation-1 issuance
Expected: signer independently derives exact current ledger/epoch bindings and predecessor, signs generation 1, writer persists one CURRENT row, verification succeeds.

### P10-04 — writer-supplied semantic fields are not accepted
Expected: request attempts to supply/override permit digest, reconciliation digest, epoch, predecessor, tag or arbitrary checkpoint body are rejected rather than signed.

### P10-05 — forged checkpoint made with unrelated/writer material is rejected
Expected: writer cannot manufacture an accepted checkpoint without signer-held key.

### P10-06 — issuance identity semantic rebinding denied
Expected: same issuance identity cannot be rebound to a different generation or changed current platform state.

### P10-07 — same-generation competing issuance denied
Expected: distinct issuance identity cannot obtain another valid signer issuance for an already issued generation.

### P10-08 — generation rollback and skip denied
Expected: after generation N, N-1 and N+2 requests are denied; only exact next generation is eligible.

### P10-09 — exact replay is idempotent
Expected: same issuance identity/generation/current bindings returns the exact same signed material and writer journal count remains one.

### P10-10 — signer restart preserves monotonicity and replay memory
Expected: restart does not permit rollback, conflict or rebinding and exact replay remains stable.

### P10-11 — signer unavailable fails closed before writer mutation
Expected: no new CURRENT journal row is created when signer is unavailable.

### P10-12 — platform state drift invalidates stale signer material for new use
Expected: old signed material cannot be rebound or treated as current after permit/reconciliation/epoch state changes; a new generation must derive the new state.

### P10-13 — signer response mutation/substitution rejected
Expected: writer/verification path rejects altered generation, issuance id, scope, predecessor, ledger digests or authentication tag.

### P10-14 — duplicate/concurrent writers cannot create duplicate CURRENT generation
Expected: signer plus journal constraints yield at most one CURRENT row for a generation under concurrent/replayed writer attempts.

### P10-15 — model/reviewer/writer authority remains zero
Expected: signer evidence or CURRENT checkpoint grants no production, release, merge, approval or self-issued mutation authority to model, reviewer or writer.

### P10-16 — clean higher-generation liveness across signer/writer restart
Expected: after valid generation 1, restart signer/writer, derive current changed platform state and issue exact generation 2 once; both lineage/predecessor and current verification are correct.

## Primary endpoints
1. writer possession of checkpoint-minting material;
2. unauthorized checkpoint forgery acceptance;
3. signer acceptance of writer-supplied semantic authority fields;
4. generation rollback/skip/conflict issuance;
5. issuance semantic-rebinding acceptance;
6. signer restart loss of monotonic/replay memory;
7. signer-unavailable fail-open mutation;
8. stale signer-material reuse after state drift;
9. duplicate CURRENT generation under writer concurrency/replay;
10. clean restart/higher-generation liveness.

Any observed writer possession of the raw key, successful unauthorized mint, fail-open signer outage, accepted semantic rebinding, accepted rollback/skip/conflict, duplicate CURRENT generation, or stale-state promotion falsifies Pilot 10 on the exercised path.

## Evidence and repair rules
- All P10-01..P10-16 execute in the first scientific run.
- The no-key test inspects the actual writer construction, child launch surfaces and request schema.
- Signer state derivation is tested against independently computed platform-state digests.
- First-run failures are preserved verbatim.
- No endpoint or expected outcome may be removed/weakened after execution.
- Repairs require diagnosis and the smallest authorized artifact scope.
- Full governed-platform regression suite reruns after any repair.
- Workflow SUCCESS is operational evidence only, never scientific approval by itself.

## Explicit non-claims
A Pilot 10 pass will not prove asymmetric public-key verify-only separation, OS privilege isolation against a same-user debugger, container/VM boundary isolation, HSM/KMS key custody or nonextractability, protection after signer process/key compromise, multi-signer threshold authority, administratively independent trust domains, physical power-loss durability, multi-host consensus, production/release authority, or universal reviewer correctness.

## Authority rule
The signer is a platform authority component only for the bounded checkpoint-authentication operation defined here. It does not confer production/release authority. Models, reviewers and writers remain replaceable execution/reasoning components beneath the governance layer and cannot infer or mint their own authority.
