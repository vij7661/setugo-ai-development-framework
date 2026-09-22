# R8 Meta-Governance Design Review — Adjudication

Status: **CHANGES_REQUIRED — DESIGN REVISION REQUIRED**

Authority effect: **NONE**

Reviewed candidate:
- R8 preregistration commit: `d7d4876781fb82bcf8df43cf15bbe069acf33a0a`
- R8 preregistration blob: `1cd69adbe924660d8dbc71826e9366b3e6e46b5c`

Independent review request:
- `01be837b5db8fa718d90d985de0440e61e5989e0`

External review artifact:
- user-provided review SHA-256: `b3d3eb9be68654fedb85600257617a40a4c9ef8ccdf7ca7d0a6f9203173716b9`
- review disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- implementation/runtime verification: none
- authority effect: none

## 1. Overall adjudication

The review is materially valid. R8 v1 is not sufficient for implementation freeze because multiple load-bearing controls terminate in undefined trust roots or undefined transition authorities.

No R8 v1 invariant or falsification case is weakened or deleted to obtain closure. R8 v1 remains preserved as the first preregistration exposure.

A successor R8 v2 must close the design classes below before implementation begins.

## 2. Accepted critical design gaps

### R8V2-G01 — Constitutional/root bootstrap

Accepted.

R8 v1 did not define:
- the first trust anchor;
- first meta-governor configuration;
- first invariant registry;
- first issuer/revocation registry;
- first policy registry;
- first classifier registry;
- separation between bootstrap, normal mutation, recovery, and root replacement.

Required correction:
Introduce a separately anchored Constitutional Root Authority and immutable genesis manifest. The meta-governor may consume constitutional state but may not create or amend its own constitutional authority.

### R8V2-G02 — Meta-governor self-amendment

Accepted.

Required correction:
Meta-governor validation predicates, constitutional registry schemas, root authority, and non-overridable invariant lifecycle require a higher-order constitutional amendment path that cannot be approved solely by the same meta-governor being changed.

### R8V2-G03 — Recovery/root replacement

Accepted.

Required correction:
Define an independently authorized Recovery Authority, exact recovery scope, quorum, audit trail, root-replacement ceremony, and prohibition on weakening non-overridable invariants through recovery.

### R8V2-G04 — Invariant lifecycle authority

Accepted.

Required correction:
Platform invariants require append-only lineage and explicit lifecycle operations. Deletion is forbidden. Retirement, supersession, or overridable-state changes require constitutional authority and preserve prior states.

### R8V2-G05 — Issuer/revocation trust

Accepted.

Required correction:
Define issuer enrollment, scope expansion, key rotation, suspension, revocation, revocation undo, and use-time revocation lookup. Revocation-state unavailability fails closed for authority-bearing actions.

### R8V2-G06 — Continuity/history anchor

Accepted.

Required correction:
Define integrity anchor, anti-replay sequence, predecessor linkage, fork detection, authoritative history anchor, and governed repository/mirror migration.

### R8V2-G07 — Evidence transition authority

Accepted.

Required correction:
Evidence classes require an explicit transition table. Only the meta-governor may authorize transitions, based on verified provenance and policy. Metadata-only relabeling cannot upgrade authority.

### R8V2-G08 — Policy composition closure

Accepted.

Required correction:
Define canonical representation, parser/schema rules, same-level ordering, scope intersection, conflict ontology, cycles, rollback, migration, semantic weakening checks, and exact policy snapshot bytes.

## 3. Accepted high/medium gaps

The following are adopted into R8 v2:

- reviewer principal/alias/delegation identity model;
- structural isolation covering shared memory, cache, session, prompt history, and packet contamination;
- governance object-class registry and authenticated dependency metadata;
- PLATFORM_POLICY issuer enrollment separated from the actor it can later authorize;
- tenant-scoped namespaces and ID lifecycle;
- authoritative time/sequence rules;
- fail-closed behavior when revocation/time authority is unavailable;
- registry rollback protection;
- policy rollback/migration;
- repository history/mirror migration and divergence handling;
- observable blocked states with governed escalation;
- additional decision states for bootstrap, constitutional amendment, issuer enrollment, registry rollback, evidence transition, tenant mismatch, and time uncertainty.

## 4. Falsification-matrix adjudication

Accepted reviewer criticism:
R8 v1 is too negative-path heavy. A constant-rejection implementation could satisfy many cases.

R8 v2 must add positive controls proving at least:
- valid bootstrap;
- valid constitutional amendment;
- valid policy composition;
- valid material review;
- valid independent reviewer assignment;
- valid issuer enrollment;
- valid authority mint/use;
- valid revocation-aware denial and valid unrevoked use;
- valid continuity resume;
- valid evidence transition;
- valid tenant-isolated operation;
- valid recovery;
- valid repository/history migration.

Tests must exercise load-bearing mechanisms rather than only compare result labels.

Where a fault claim is load-bearing, the fault must be independently demonstrated rather than inferred from the final denial state.

## 5. Reviewer claims requiring bounded interpretation

The independent reviewer has no implementation/runtime access. Findings are therefore adjudicated as design gaps, not proof that a future implementation contains the exploit.

No design finding grants or denies production qualification outside the reviewed R8 design scope.

## 6. Successor rule

R8 v1 remains:
- `PREREGISTERED_DESIGN`
- `NOT_IMPLEMENTED`
- `CHANGES_REQUIRED`
- authority effect `NONE`

R8 v2 may be drafted only as a successor preregistration. It must receive fresh independent design review before implementation begins.

PR #39 and PR #40 remain non-authoritative.
