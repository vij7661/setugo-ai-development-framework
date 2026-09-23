# R8 v15-r1 — Executable Schema Freeze Preregistration V2

Status: **SCHEMA_FREEZE_CANDIDATE_V2 — NON_AUTHORITATIVE**
Authority effect: **NONE**

Frozen semantic candidate:
- `c721b38cf8b00294797300b526596ce723a47ff8`

Accepted design-review state:
- normalized design review: `BOUNDED_PASS`;
- targeted H-1/M-1 evidence closure: `EVIDENCE_CLOSURE_PASS`.

V2 supersedes schema-freeze candidate V1 before external review because V1 failed to carry forward inherited schema-freeze-process obligations. Semantic design is unchanged.

## 1. Non-negotiable freeze boundary

Schema construction may encode the frozen semantics but may not:
- add, remove, weaken, reinterpret or broaden authority;
- invent a weaker liveness fallback;
- turn missing authority evidence into a default;
- make an authority-bearing field optional unless frozen design explicitly makes absence/null meaningful;
- treat schema validity as authorization.

Unknown source details remain opaque IDs/digests/references rather than invented semantics.

## 2. Required schema/contract inventory

V2 must freeze:

1. runtime authority contracts:
   - T0/MTR/BTW;
   - canonical identity/revocation;
   - GGS/LAS hard state and LASAuthorityStateRoot;
   - rotation/STC;
   - AIEP/AIG boundary;
   - CSM-5 / SemanticEntry / AIM / ANYScopePermission / AIMScopePolicy;
   - ResolverPolicy / RIR / RCS;
   - SRTT / SREP;
   - AuthorityReadSet / DecisionPresealContext / time / VerifiedStateSeal;
   - EffectIntent/effect states;
   - evidence/migration/recovery.
2. GuardRegistry / CaseRegistry schemas.
3. SRTT-4 RuleRegistry and total-table schemas.
4. BSP-5 grammar schema.
5. NCG structured-closure schema.
6. guard-omission evidence/manifest schemas.
7. GCP-RVM-2 schema + frozen vector manifest.
8. RPS-1 schema + frozen review-presentation classification.
9. CaseProofContract schema + generated G001..G156 contracts and FP0..FP6 requirements.
10. SPM-1 provenance schema + per-schema-element provenance manifest.
11. SchemaProvenanceGenerator contract/runtime-manifest binding.
12. deterministic SchemaFreezeValidator contract.
13. schema-freeze traceability for NORM-001..043 plus inherited freeze-process rules.

## 3. Inherited freeze-process rules restored

### SFG-001 — SPM-1 mandatory provenance
Every machine-readable schema element entering final freeze has an SPM-1 record containing:
- schema artifact ID/digest;
- JSON pointer / field / rule ID;
- semantic purpose;
- authoritative source design IDs;
- source commit/blob;
- transformation/generator identity;
- generator RuntimeManifest digest;
- reviewer status where required.

Source: R8V7-I030.

### SFG-002 — RG-1 provenance enforcement
Freeze fails with `UNAUTHORIZED_SEMANTIC_SOURCE` when:
- any schema element has no SPM-1 entry;
- its only source is PR #39/#40 or another NON_AUTHORITATIVE artifact;
- a manual/generated rule has no governed incorporation source.

Source: R8V7-I031.

### SFG-003 — qualified SchemaProvenanceGenerator
Any generator emitting schema artifacts or SPM entries must be enrolled as SchemaProvenanceGenerator and bind:
- generator identity;
- executable/artifact digest;
- RuntimeManifest;
- WorkloadAttestation policy/proof;
- allowed input design artifacts;
- allowed output schema classes;
- signing credential;
- revocation state.

Drift/revocation/unregistered generator -> output not final-freeze eligible.

Source: R8V8-I020..I022.

### SFG-004 — GCP-RVM-2
Freeze includes canonical-output vectors and rejection vectors with frozen source trace and independently reproducible positive digests.

Source: R8V4-I026..I029; R8V5-I028..I034; R8V7 GCP rejection vectors; R8V8-I034/I035.

### SFG-005 — RPS-1
Every review packet type classifies displayed fields as:
- `REVIEW_SEMANTIC`; or
- `DISPLAY_NON_SEMANTIC`.

Unknown display fields default REVIEW_SEMANTIC.
DISPLAY_NON_SEMANTIC may not encode status, severity, identity, evidence quality, ordering priority, recommendation or substantive claim, and may not alter ordering/evidence association.

Source: R8V7-I038/I039.

### SFG-006 — CaseProofContracts
Every current GuardRegistry guard G001..G156 has:
- at least one positive control;
- all registered negative controls;
- exact FP0..FP6 class for each negative;
- preserved case source lineage.

Source: R8V7-I044/I045 and schema-freeze gates v7-v13, extended by current GuardRegistry.

### SFG-007 — independent schema review
Final executable-schema freeze requires a fresh blind independent review bound to the exact schema candidate.

Source: inherited schema-freeze gates v7-v13.

## 4. Generator qualification boundary

A manually constructed candidate may be used only to prepare/falsify schema semantics.

It is **not final-freeze eligible** until SFG-003 is satisfied by a qualified generator execution whose exact output matches the candidate artifacts or regenerates a semantically identical successor that receives review.

No ChatGPT/model statement, Git commit, CI green check or reviewer pass substitutes for qualified SchemaProvenanceGenerator identity.

## 5. Deterministic validator obligations

V1 SFV-01..SFV-34 remain in force.

V2 adds:

- **SFV-35** SPM coverage: every semantic schema element has exactly one or explicitly equivalent non-conflicting provenance record.
- **SFV-36** SPG qualification: final freeze requires qualified generator RuntimeManifest/workload attestation and exact generator artifact digest.
- **SFV-37** GCP positive vectors: recompute every positive canonical-byte SHA-256 and require exact match.
- **SFV-38** GCP rejection vectors: every frozen rejection input must reject under the named source rule; no canonical output may be accepted.
- **SFV-39** CaseProofContract closure: exactly G001..G156, every registered positive/negative case present, no extras/missing, FP classes match GuardRegistry.
- **SFV-40** fault-proof legend: FP0..FP6 meanings exactly preserved.
- **SFV-41** RPS coverage: every review packet displayed field classified; unknown defaults REVIEW_SEMANTIC.
- **SFV-42** RPS non-semantic safety: DISPLAY_NON_SEMANTIC cannot influence decision semantics, ordering or evidence association.
- **SFV-43** process-source authority: no freeze rule/schema element is sourced only from non-authoritative PR #39/#40 or ungoverned artifacts.
- **SFV-44** exact schema artifact digest binding: SPM/freeze manifest/review packet must bind the same artifact bytes.
- **SFV-45** independent schema review: exact frozen schema candidate must have a qualifying review disposition before final freeze.

## 6. Freeze-state taxonomy

- `SCHEMA_CANDIDATE_INTERNAL`: schemas exist but not all freeze gates close.
- `SCHEMA_CANDIDATE_REVIEWABLE`: semantic/mechanical checks close and SPG qualification is satisfied; ready for independent schema review.
- `EXECUTABLE_SCHEMA_FROZEN`: exact schema candidate passed qualified generation, provenance, validator recomputation and independent schema review.
- `IMPLEMENTATION_AUTHORIZED`: **not granted by this phase**.

## 7. Current V2 start state

At V2 start:
- semantic design change: **NO**;
- V1 external review: **NOT USED**;
- SPM-1: **PENDING**;
- qualified SPG-1 generation: **PENDING**;
- GCP-RVM-2: **being added**;
- RPS-1: **being added**;
- CaseProofContracts G001..G156: **being added**;
- executable-schema final freeze: **BLOCKED**;
- authority effect: **NONE**.
