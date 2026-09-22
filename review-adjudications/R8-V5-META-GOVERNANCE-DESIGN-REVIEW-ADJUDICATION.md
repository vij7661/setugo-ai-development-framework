# R8 v5 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- R8 v5 commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v5 blob: `bb3049b9dd4ba5c1691f518b9903900dea65711b`

Independent review evidence:
- preserved at `review-evidence/R8-V5-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `28b737dc5da7e5e3c7fb0ba3de0a725a06cd7ed88a96ea7300af3c8f9b4a8296`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v5 significantly tightened T0, BTW, LAS, runtime semantics, GCP, revocation/time, producer lifecycle, materiality, tenant migration, and TOCTOU handling. However, implementation and executable-schema freeze must not begin because the design still leaves seven load-bearing closure gaps:

1. genesis linearization across constitution namespace + authorization state;
2. atomic CAS_APPEND validation/head advancement;
3. durable LAS term/index/vote anti-rollback;
4. complete multi-store VerifiedStateSeal coverage + atomic consequential commit;
5. rollback-resistant T0 pin/high-water persistence;
6. default-deny enumeration of all authority-consumed semantic inputs;
7. explicit adjudication of permanent T0/EBA/BTW recovery deadlock.

R8 v5 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blockers

### V5-C1 — Genesis namespace race
**ACCEPTED — BLOCKER**

Successor must linearize genesis in one authority sequencer transaction that consumes:
- constitution namespace vacancy;
- bootstrap authorization UNUSED state;
- exact authorized GenesisDescriptor digest;
- current T0/BTW proof state.

At most one genesis may commit for a constitution_id.

### V5-C2 — CAS_APPEND atomicity
**ACCEPTED — BLOCKER**

Validation of expected predecessor, majority acceptance, commit-certificate issuance, and authoritative head advancement must be one linearizable state transition.

Detection of later equivocation remains necessary but cannot substitute for prevention.

### V5-C3 — LAS anti-rollback
**ACCEPTED — BLOCKER**

Each LAS replica must maintain rollback-resistant persistent state for:
- highest accepted term;
- highest committed index;
- last committed head digest;
- per-term vote/leader state where applicable.

Old state replay must not restore signing power.

### V5-C4 — VerifiedStateSeal completeness/multi-store atomicity
**ACCEPTED — BLOCKER**

The authority decision must declare the complete authority-read set. Consequential commit must atomically compare every sealed mutable dependency before committing the effect or produce STATE_CHANGED.

Unnamed mutable state cannot be consumed by an authority predicate.

### V5-C5 — T0 rollback resistance
**ACCEPTED — BLOCKER**

T0 pin + accepted-generation high-water mark require a monotonic external/attested persistence mechanism. Ordinary writable storage cannot be the sole rollback defense.

### V5-C6 — Semantic dependency default-deny
**ACCEPTED — BLOCKER**

Any semantic/configuration/input read by an authority predicate must be represented in the constitutional semantic dependency manifest.

Unregistered authority input = SEMANTIC_DEPENDENCY_UNBOUND.

### V5-C7 — Permanent recovery deadlock
**ACCEPTED AS EXPLICIT SAFETY STATE, REQUIRES DESIGN DECLARATION**

The platform must explicitly define a terminal bounded state for simultaneous loss of all lawful T0/EBA/BTW recovery paths.

No weaker emergency trust root may be invented after failure.

A new independent constitution may be created only as a new trust domain and cannot inherit authority.

## 3. Accepted high findings

R8 v6 must additionally define:
- exact T0 activation condition without circular dependency on ordinary time;
- split-view-resistant BTW first-seen persistence;
- constrained ControllerAttestation wildcard semantics;
- attestation revocation effective sequence;
- canonical lineage graph/cycle-resolution rules;
- formal commutative proof artifact + verifier identity;
- hardware/workload attestation binding for RuntimeManifest where claimed;
- GCP NFC/key-collision and extension-map closure;
- anchor-controller revocation effective sequence;
- monotonic time nonce ledger;
- monotonic revocation high-water tracking + revocation undo state machine;
- strong-evidence producer executable mismatch and weak-to-strong no-laundering guard inheritance;
- review-influence materiality for fields consumed by humans/downstream tools;
- exact tenant migration RequalificationProof;
- Channel H signed review identity and bounded provider-memory claim;
- authority-read-set enforcement preventing consumption of unsealed derived values.

## 4. Accepted medium findings

R8 v6 must also:
- freeze the CSM envelope/canonical digest algorithm;
- bind reference vectors to a frozen reference implementation/artifact;
- close Unicode noncharacter/key-collision rules;
- constrain EBA admin-domain lifecycle;
- define time-source status resolution at sequence;
- bind recovery trigger evidence to recovery_context_digest + nonce;
- remove "where relevant" discretion from independent fault proof by defining it per guard;
- require anti-constant-reject positive control for every guard;
- explicitly classify total T0/BTW/recovery loss as bounded unrecoverable;
- add a schema-freeze reconciliation gate that rejects semantics from non-authoritative PR #39/#40 unless separately incorporated by constitutional design.

## 5. Bounded interpretation

This review proves design gaps only. No implementation exists to validate or exploit.

The successor should not attempt to "solve" real-world trust beyond the explicit T0 assumption. It must instead make rollback resistance, atomicity, semantic-read closure, and trust-loss behavior mechanically explicit and falsifiable.

## 6. Successor rule

Create R8 v6 as a new preregistered successor.

R8 v5 remains immutable and CHANGES_REQUIRED.

R8 v6 must receive fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v5 = CHANGES_REQUIRED
- R8 v6 = not yet reviewed
- PR #39 = NON_AUTHORITATIVE
- PR #40 = NON_AUTHORITATIVE
- holistic governance = CHANGES_REQUIRED
- authority effect = NONE
