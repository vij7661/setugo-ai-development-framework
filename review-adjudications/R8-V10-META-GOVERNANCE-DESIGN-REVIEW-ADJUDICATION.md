# R8 v10 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed effective candidate:
- R8 v4: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v9: `0948ed0e83d9de128ca9c12df5784286f15af9eb`
- R8 v10: `2e85384f759318a17c2ec14b1781dc689a864618`

Independent review evidence:
- preserved at `review-evidence/R8-V10-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `9adac75d8b787c3605ba69235243224f619b112e2ff23b107decc93c2c95d3a7`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v10 closed the CSM-2 representability conflict and added state-transfer certificate structure, but executable-schema freeze remains blocked because:
1. cross-lineage mappings are not traversed by the resolver;
2. STC snapshots are not linearized against subsequent old-config commits;
3. ANY-permission reevaluation is not integrated into Smax lifecycle semantics;
4. the v10 scope tuple narrows inherited authority dimensions without an explicit supersession mapping;
5. successor-chain, AIM/CSM, STC uniqueness, and blind-packet hygiene remain incomplete.

R8 v10 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blockers

### V10-C1 — Cross-lineage mapping not integrated
**ACCEPTED — BLOCKER**

R8 v11 must define a single resolver algorithm that:
- begins from the source lineage and decision scope;
- consults active constitutional SemanticLineageMapping records;
- gathers eligible mapped destination candidates;
- prevents implicit cross-lineage fallback;
- defines lineage-map ordering, uniqueness, effective sequence, and conflict behavior;
- binds all mapping objects into the canonical semantic registry digest.

### V10-C2 — STC snapshot race
**ACCEPTED — BLOCKER**

R8 v11 must linearize rotation through a sequencer barrier:
- commit a `ROTATION_PREPARE` event in the same authoritative log;
- freeze authority-bearing commits for the rotating sequencer after that barrier;
- certify STC from the exact barrier state;
- commit STC as a unique configuration-stream event;
- ENTER_JOINT must consume the exact prepared/STC state;
- any stale/different state invalidates rotation.

### V10-C3 — ANY permission reevaluation ambiguity
**ACCEPTED — BLOCKER**

`SCOPE_PERMISSION_REEVALUATION_REQUIRED` must be a first-class lifecycle state:
- it participates in Smax computation;
- at Smax it blocks lower-specificity fallback;
- it cannot be treated as ACTIVE;
- resolution returns a specific blocking result until revalidation/supersession;
- revalidation authority and effective sequence are explicit.

### V10-C4 — Scope regression
**ACCEPTED — BLOCKER**

The canonical scope tuple must restore all authority dimensions required by inherited semantics:
- trust_domain_id;
- constitution_id;
- root_namespace;
- tenant_id;
- organization_id;
- project_id;
- experiment_or_release_id;
- object_class;
- action_class.

No dimension may be implicitly absorbed by another identifier.

## 3. Accepted high findings

### V10-H1 — Successor chain
**ACCEPTED**

Define an acyclic successor graph with:
- one current eligible successor path per source entry/scope decision;
- explicit effective sequence;
- monotonically increasing semantic_version;
- cycle rejection;
- multi-successor conflict;
- mapped-scope semantics.

### V10-H2 — AIM/CSM closure wording
**ACCEPTED**

R8 v11 explicitly supersedes inherited “one active CSM entry” wording.

All AIM resolution is defined as CSRULE-3 over CSM-4.

### V10-H3 — STC uniqueness
**ACCEPTED**

STC certification itself becomes one committed non-commutative configuration-stream event tied to one ROTATION_PREPARE barrier.

Multiple STCs for one barrier are rejected/equivocation.

### V10-H4 — Blind packet hygiene
**ACCEPTED**

R8 v11 review packets will be built from a reviewer projection that:
- includes semantic bodies;
- excludes administrative prior-review/adjudication reference lines;
- runs a deterministic residual-pattern scan for `adjudication`, `review evidence`, and known prior-review metadata patterns;
- fails packet construction if such metadata remains.

## 4. Accepted medium findings

- ScopeReplacementMapping and SemanticLineageMapping become first-class canonical CSM-4 mapping objects with deterministic lookup order.
- STC state-root computation becomes explicit and sequencer-specific.
- ANY permission revalidation path and authority become explicit.
- New falsification cases are added for cross-lineage resolution, ANY drift at Smax, post-snapshot/pre-JOINT race, and residual blind metadata.

## 5. Successor rule

Create R8 v11 as a new successor overlay.

Do not mutate v4-v10.

R8 v11 must receive a fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v10 = `CHANGES_REQUIRED`
- R8 v11 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
