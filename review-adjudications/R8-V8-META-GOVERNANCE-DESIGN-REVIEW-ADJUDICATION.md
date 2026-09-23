# R8 v8 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed effective candidate:
- R8 v4 commit: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5 commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6 commit: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7 commit: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8 commit: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v8 blob: `9990ae39ac4508a031860075c1178a94386c8aaa`

Independent review evidence:
- preserved at `review-evidence/R8-V8-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `f25b7da3cc2503650c5491bc188dd5b9340a570073d3d0debeb07687774f415f`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v8 closed the prior T0 reservation, MTR replay, GGS rotation, AIG attestation, decision-preseal, schema-generator, effect-executor, migration freshness, and packet-completeness gaps. However executable-schema freeze remains blocked by one critical semantic-resolution inconsistency, two high configuration-rotation/falsification gaps, and three medium definition/completeness gaps.

R8 v8 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blocker

### V8-C1 — CSRULE-1 revoked-specific fallback
**ACCEPTED — BLOCKER**

R8V8-I024 resolves only among ACTIVE entries and therefore can select a lower-specificity ACTIVE entry after a higher-specificity entry in the same semantic lineage becomes REVOKED. R8V8-I025 prohibits that outcome, but the prohibition is not part of the mechanical resolution algorithm.

Successor requirement:
- resolution must examine the highest matching specificity across the semantic lineage before ACTIVE filtering;
- a REVOKED higher-specificity entry creates an explicit `SEMANTIC_SCOPE_REVOKED` blocking state;
- no lower-specificity ACTIVE rule may be selected unless a constitutionally valid successor explicitly re-establishes the revoked scope;
- explicit falsification cases must cover revoked-specific + active-general and revoked-specific + ANY-general scenarios.

## 3. Accepted high findings

### V8-H1 — LAS rotation idempotency ledger continuity
**ACCEPTED — BLOCKER**

LAS configuration rotation must transfer and attest the idempotency/deduplication ledger together with term/index/head state.

A replacement/new replica without that exact ledger is non-voting.

Add a replay case using a previously consumed idempotency key with a different event digest after rotation.

### V8-H2 — Racing JOINT configuration proposals
**ACCEPTED — BLOCKER**

GGS and LAS configuration transition streams require an explicit single-predecessor CAS/linearization rule for entering JOINT state.

Two different new-configuration proposals racing from the same old configuration must yield exactly one committed JOINT transition; the loser must receive a conflict and cannot form an alternate configuration branch.

Add dedicated GGS and LAS falsification cases rather than relying only on inferred coverage.

## 4. Accepted medium findings

### V8-M1 — Schema-generator historical-validity policy undefined
**ACCEPTED**

Define a CSM-bound `SchemaGeneratorHistoricalValidityPolicy` with:
- revocation/compromise effective sequence;
- pre-effective historical-validity rule;
- post-effective invalidity;
- retrospective invalidation event semantics;
- schema requalification trigger;
- no silent inheritance after generator replacement.

### V8-M2 — ANY scope misuse untested
**ACCEPTED**

Define an explicit constitutional `ANYScopePermission` set per semantic class.

If a class does not permit ANY at a tuple component, an entry using ANY there is invalid at registration.

Add explicit misuse and revoked-specific + ANY-general cases.

### V8-M3 — Independent reconciler/executor criteria weak
**ACCEPTED**

Define reconciler independence using the same canonical identity machinery as controller independence:
- distinct canonical_subject_id from the compromised/revoked executor;
- non-overlapping root delegation lineage where required;
- distinct credential/workload identity;
- distinct admin_domain_id where the effect class requires administrative diversity;
- current workload attestation and revocation status.

## 5. Accepted low traceability issue

Formally name the effective authority sequencer version `LAS-3` in canonical design text and bind its configuration/version identity in CSM so review terminology and semantic-artifact versioning cannot drift.

## 6. Bounded interpretation

The review explicitly found no material bypass in:
- T0/MTR/GGS reservation/freshness design;
- controller/admin-domain identity;
- AIEP/AIG;
- universal revocation;
- DPS-2 time context;
- migration freshness;
- trust-loss handling;
- packet completeness;
- fail-closed liveness posture.

Those are retained unless superseded by a stronger v9 rule.

The reviewer independently confirmed that canonical v4-v8 texts and inherited case semantics are present in the v8 packet. This does not grant qualification authority.

## 7. Successor rule

Create R8 v9 as a new successor overlay.

Do not mutate v4-v8.

R8 v9 must receive a fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v8 = `CHANGES_REQUIRED`
- R8 v9 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
