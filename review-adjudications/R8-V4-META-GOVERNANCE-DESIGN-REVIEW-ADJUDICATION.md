# R8 v4 Independent Design Review - Adjudication

Status: **CHANGES_REQUIRED - SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- R8 v4 commit: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v4 blob: `8597233a08c77c0ab928868eaec4c13c425a2eac`

Independent review evidence:
- preserved at `review-evidence/R8-V4-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `dfdc25266a8c7d21c3dd669d84be196c94a1855863f7ba0c91a6cf87af5171f8`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v4 correctly introduced an explicit T0 trust axiom, external controller attestations, a witness-backed anchor model, atomic-intent CAS operations, qualified evidence producers, and mechanism-proof contracts. However, implementation must still not begin because six design-level blockers remain:

1. the T0/EBA bootstrap manifest and trust-root replacement path are not frozen;
2. BTW-1 is not itself pinned to T0;
3. BootstrapAuthorization is not byte-complete over the genesis it authorizes;
4. CAS_APPEND lacks a concrete linearization/commit-certificate model;
5. the constitutional semantic-artifact set is incomplete;
6. verify-before-authority is not TOCTOU-safe.

R8 v4 remains preserved unchanged as the reviewed exposure.

## 2. Critical findings accepted

### V4-C1 - T0/EBA provisioning and replacement
**ACCEPTED - BLOCKER**

R8 v5 must freeze an immutable `T0BootstrapManifest` containing the EBA trust key set, EBA policy digest, BTW trust key/policy, initial trusted witness tree head, crypto profile, and trust-root generation.

EBA/BTW rotation or replacement must require a T0 successor certificate signed under the currently trusted T0 root and must be rollback protected.

### V4-C2 - BTW trust root
**ACCEPTED - BLOCKER**

BTW receipts/tree heads cannot be self-authenticating.

R8 v5 must bind BTW verification keys, witness policy, initial signed tree head and consistency rules into the T0 manifest. CAS_GENESIS must reject receipts or STH chains that do not extend the pinned T0 witness state.

### V4-C3 - BootstrapAuthorization to genesis binding
**ACCEPTED - BLOCKER**

BootstrapAuthorization must commit the complete authorized `GenesisDescriptorDigest` and expiry. CAS_GENESIS must verify:
- current T0 generation;
- authorization signature/quorum;
- unexpired authorization;
- unused authorization serial;
- valid BTW inclusion/consistency proof;
- exact `genesis_digest == authorized_genesis_digest`;
- exact initial semantic/registry/config digests.

### V4-C4 - CAS_APPEND linearization
**ACCEPTED - BLOCKER**

R8 v5 must define an explicit authority ledger service/reference mechanism with:
- one linearization point per stream;
- atomic compare-and-swap over head generation/sequence/digest;
- commit certificate schema;
- signer/service identity;
- idempotency key behavior;
- retry semantics;
- equivocation detection.

The anchor layer records committed history; it is not itself the linearization mechanism.

### V4-C5 - Constitutional semantic closure
**ACCEPTED - BLOCKER**

The constitutional semantic manifest must include every load-bearing semantic/configuration artifact, including:
- stream schemas;
- commutative markings/merge functions;
- recovery trigger schemas;
- T0/EBA/BTW policies;
- state-root computation spec;
- materiality masks/extractors;
- guard catalog;
- CaseProofContract schema;
- runtime/compiler/crypto dependency attestation policy;
- GCP reference vectors;
- tenant/checkpoint migration schemas.

Unknown or absent semantic artifact -> no authority.

### V4-C6 - TOCTOU-safe authority use
**ACCEPTED - BLOCKER**

Authority decisions must consume a `VerifiedStateSeal` binding exact store heads/state roots/schema digests. The consequential commit must atomically revalidate that seal against current heads; stale seals fail with `STATE_CHANGED`.

## 3. High findings adopted into R8 v5

R8 v5 must also freeze:

- constitution/tenant/role-instance scope inside ControllerAttestation;
- canonical controlling-lineage proof format and admin-domain registry semantics;
- anchor-controller rotation and witness STH freshness/anti-rollback;
- time-authority rotation and challenge-nonce uniqueness;
- issuer key rotation, parent compromise cascade, and revocation-undo lifecycle;
- QualifiedEvidenceProducer revocation/compromise temporal semantics;
- exact materiality field-mask digests and dependency-extractor digests;
- tenant namespace/migration/reassignment semantics;
- recovery-trigger schemas in the constitutional semantic manifest;
- explicit new-constitution non-inheritance enforcement.

## 4. Medium findings adopted

R8 v5 must additionally freeze:

- exact GCP escape mapping;
- absent/null rules;
- whitespace rules;
- extension-map rules;
- set-vs-array schema discrimination;
- canonical reference-vector SHA-256 digests before implementation;
- CAS retry/idempotency semantics;
- Channel X provider/service attestation requirements;
- bounded liveness behavior for EBA/witness/reviewer outage without authority bypass.

## 5. Guard-catalog closure

R8 v5 must expand the guard catalog to cover:
- T0 generation/rotation/rollback;
- BTW split-view, initial STH pinning, stale STH and witness outage;
- anchor-controller rotation;
- CAS linearization/idempotency/split-brain;
- runtime/compiler/crypto dependency drift;
- TOCTOU verified-state seal;
- issuer rotation and parent compromise;
- producer revocation/compromise temporal effects;
- tenant migration/cross-tenant replay;
- recovery-quorum semantic self-modification;
- new-constitution non-inheritance.

Every new guard must have:
- one frozen valid positive control;
- at least one adversarial case;
- target-guard proof;
- prohibited earlier guards;
- independent fault proof where applicable.

## 6. Bounded interpretation

The independent review is design evidence only; no implementation exists.

The successor must not claim to prove the honesty of T0 external parties. It must prove only that software accepts authority according to the frozen T0 trust configuration and cannot silently replace or weaken it.

## 7. Successor rule

Create R8 v5 as a new preregistered design.

Do not mutate R8 v4.

R8 v5 must receive a fresh blind independent design review before executable-schema freeze or implementation preparation.

Until then:
- R8 v1 = `CHANGES_REQUIRED`
- R8 v2 = `CHANGES_REQUIRED`
- R8 v3 = `CHANGES_REQUIRED`
- R8 v4 = `CHANGES_REQUIRED / NOT_IMPLEMENTED`
- R8 v5 = not yet reviewed
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
