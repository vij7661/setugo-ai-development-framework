# Workflow Drift & Parent-Child Impact Falsification Matrix — V17 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V17`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V17 inherits WDPC-01…260 as mandatory regressions under composite V5→V17 rules.

V17 adds WDPC-261…WDPC-272.

## 2. New cases

### WDPC-261 — Recheck-to-threshold race after apparently valid detached proof

Mechanisms: `MECH-THRESHOLD-ATOMIC-COMMIT-ONLY`
Profiles: `EP-BASE + EP-THRESHOLD-ATOMIC-COMMIT-ONLY`

Fault: a fresh recheck succeeds and emits a detached proof, then a bound governance/control state changes before threshold commit.

Expected: detached proof is ineligible; only atomic in-transaction revalidation may count. `REVIEW_THRESHOLD_ATOMIC_COMMIT_FAILED`; threshold contribution zero.

### WDPC-262 — NRVA and RPAA formal-record collusion through undeclared control path

Mechanisms: `MECH-NRVA-REGISTRY`, `MECH-NRVA-RPAA-JOINT-INDEPENDENCE`
Profiles: `EP-BASE + EP-NRVA-REGISTRY + EP-NRVA-RPAA-JOINT-INDEPENDENCE`

Fault: formal independence records appear valid, but NRVA and RPAA share an undeclared recovery, credential, identity, HSM/cloud-root, beneficial-owner, alias, or super-admin control path.

Expected: independently sourced control facts conflict with declarations; `NRVA_RPAA_JOINT_INDEPENDENCE_REJECTED`; qualification blocked.

### WDPC-263 — Canonical collision/equivalence evidence conflict

Mechanisms: `MECH-CANONICAL-CONFLICT-PRECEDENCE`
Profiles: `EP-BASE + EP-CANONICAL-CONFLICT-PRECEDENCE`

Fault: active collision-resistance evidence classifies a clause pair as distinct while active equivalence evidence classifies the same pair as semantically equivalent.

Expected: `CANONICAL_SEMANTIC_CONFLICT`; no permissive precedence; qualification `INSUFFICIENT_EVIDENCE` until new governed proof generation.

### WDPC-264 — Endpoint export replay with identical tree/schema/registry digest but different candidate commit

Mechanisms: `MECH-ENDPOINT-EXPORT-EXACT-COMMIT`
Profiles: `EP-BASE + EP-ENDPOINT-EXPORT-EXACT-COMMIT`

Fault: authoritative endpoint export from candidate A is replayed for candidate B where tree/schema/registry/tuple digests are identical but commit differs.

Expected: exact-commit mismatch; `REVIEW_ENDPOINT_EXPORT_REPLAY_REJECTED`; qualification blocked.

### WDPC-265 — Cross-gate threshold double count without explicit reuse policy

Mechanisms: `MECH-THRESHOLD-CONSUMPTION-LEDGER`, `MECH-CROSS-GATE-REUSE-POLICY`
Profiles: `EP-BASE + EP-THRESHOLD-CONSUMPTION-LEDGER + EP-CROSS-GATE-REUSE-POLICY`

Fault: same review evidence/snapshot is counted once for gate A and then submitted to gate B or another policy version without an exact allow rule.

Expected: default deny; `REVIEW_THRESHOLD_REUSE_NOT_AUTHORIZED`; second count zero.

### WDPC-266 — Packet generation reset/fork after supersession

Mechanisms: `MECH-PACKET-GENERATION-ANTI-FORK`
Profiles: `EP-BASE + EP-PACKET-GENERATION-ANTI-FORK`

Fault: after a current packet generation exists, a null-predecessor or sibling generation is created and presented as current.

Expected: append-only lineage detects reset/fork; `REVIEW_PACKET_GENERATION_FORK_REJECTED`.

### WDPC-267 — NRVA independence stale before atomic threshold commit

Mechanisms: `MECH-NRVA-REGISTRY`, `MECH-NRVA-RPAA-JOINT-INDEPENDENCE`, `MECH-THRESHOLD-ATOMIC-COMMIT-ONLY`
Profiles: `EP-BASE + EP-NRVA-REGISTRY + EP-NRVA-RPAA-JOINT-INDEPENDENCE + EP-THRESHOLD-ATOMIC-COMMIT-ONLY`

Fault: NRVA independence is valid at qualification snapshot creation, then an admin/recovery/ownership/control change occurs before threshold commit.

Expected: same atomic transaction observes stale predicate and rejects; old snapshot cannot count.

### WDPC-268 — Canonical positive corpus stale/compromised

Mechanisms: `MECH-CANONICAL-CORPUS-LIVENESS`
Profiles: `EP-BASE + EP-CANONICAL-CORPUS-LIVENESS`

Fault: active semantic-equivalence corpus is stale, superseded, contradicted, tampered with, or contains retracted fixtures.

Expected: `CANONICAL_SEMANTIC_CORPUS_STALE`; qualification evidence invalidated until revalidated.

### WDPC-269 — Atomic threshold consumption positive control

Mechanisms: `MECH-THRESHOLD-ATOMIC-COMMIT-ONLY`, `MECH-THRESHOLD-CONSUMPTION-LEDGER`
Profiles: `EP-BASE + EP-THRESHOLD-ATOMIC-COMMIT-ONLY + EP-THRESHOLD-CONSUMPTION-LEDGER`

Positive control: all bound predicates remain current and the authoritative transaction atomically revalidates and writes one threshold consumption.

Expected: exactly one eligible count commits; retry resolves idempotently without double count.

### WDPC-270 — Explicitly authorized cross-gate reuse positive control

Mechanisms: `MECH-CROSS-GATE-REUSE-POLICY`, `MECH-THRESHOLD-CONSUMPTION-LEDGER`
Profiles: `EP-BASE + EP-CROSS-GATE-REUSE-POLICY + EP-THRESHOLD-CONSUMPTION-LEDGER`

Positive control: root-governed reuse policy explicitly permits the exact evidence class/scope/source gate/destination gate/policy versions and maximum reuse count.

Expected: separately recorded authorized reuse may count once for the destination gate; no implicit authority beyond the policy.

### WDPC-271 — Clean canonical conflict-free corpus positive control

Mechanisms: `MECH-CANONICAL-CONFLICT-PRECEDENCE`, `MECH-CANONICAL-CORPUS-LIVENESS`
Profiles: `EP-BASE + EP-CANONICAL-CONFLICT-PRECEDENCE + EP-CANONICAL-CORPUS-LIVENESS`

Positive control: current audited corpus classifies equivalent paraphrases consistently and distinct obligations separately with no conflict.

Expected: canonical predicates may pass without false block.

### WDPC-272 — Valid monotonic packet-lineage positive control

Mechanisms: `MECH-PACKET-GENERATION-ANTI-FORK`
Profiles: `EP-BASE + EP-PACKET-GENERATION-ANTI-FORK`

Positive control: new packet generation points to the exact current predecessor and advances the append-only sequence once.

Expected: new generation becomes current; predecessor remains preserved and superseded; no false fork rejection.

## 3. Prior-case tightening

- WDPC-237,250,257 require all active V17 predicates.
- WDPC-246,251 no longer permit a detached recheck fallback.
- WDPC-252,258 require root-governed NRVA registry and joint-independence proof.
- WDPC-253 requires conflict precedence and current corpus.
- WDPC-256 requires exact-commit replay resistance.
- WDPC-259 requires packet-generation anti-fork lineage.
- WDPC-240 and WDPC-244 remain `DUPLICATIVE_BUT_USEFUL` and count as one unique enforcement path.

## 4. Freeze rule

V17 remains `NOT EXECUTED`.

No execution freeze while unresolved Critical/High design findings remain. No detached recheck proof, duplicate/unauthorized review reuse, colluding or stale NRVA assurance, canonical semantic conflict, stale corpus, wrong-commit endpoint export, or forked packet generation may satisfy qualification.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
