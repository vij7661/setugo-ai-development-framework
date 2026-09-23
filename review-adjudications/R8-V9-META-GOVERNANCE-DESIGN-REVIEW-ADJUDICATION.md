# R8 v9 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed effective candidate:
- R8 v4: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v9: `0948ed0e83d9de128ca9c12df5784286f15af9eb`

Independent review evidence:
- preserved at `review-evidence/R8-V9-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `9beaadf89e0bd1c7a690e7ee30fb3a22c7324bb4ae4644fb4e4e5ef3a1f896e3`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v9 successfully closed the revoked-specific fallback logic itself, LAS replay-state continuity intent, CTS-1 race intent, schema-generator history, and reconciler independence. But executable-schema freeze remains blocked because the inherited CSM-2 envelope cannot represent CSRULE-2, and sequencer rotation continuity is not cryptographically bound into ENTER_JOINT/ACTIVATE.

R8 v9 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blocker

### V9-C1 — CSM-2 envelope conflicts with CSRULE-2
**ACCEPTED — BLOCKER**

R8 v10 must replace inherited CSM-2 uniqueness by semantic_input_id with a canonical multi-entry semantic registry model supporting:
- semantic_entry_id;
- semantic_input_id;
- semantic_lineage_id;
- scope tuple;
- lifecycle state;
- version;
- predecessor/successor relation;
- ANYScopePermission reference;
- constitutional source/binding.

Duplicate rejection must apply to the canonical semantic entry key, not semantic_input_id alone.

CSRULE resolution and AIM-to-CSM resolution must consume this same structure.

## 3. Accepted high blockers

### V9-H1 — State-transfer continuity not bound into configuration transition
**ACCEPTED — BLOCKER**

R8 v10 must define:
- `LASStateTransferCertificate`;
- `GGSStateTransferCertificate`;
- exact term/index/log-prefix/head/idempotency/certificate-chain/config-generation bindings;
- old-config attestation;
- new-config acceptance attestation;
- JOINT and ACTIVATE references to the exact transfer certificate;
- state-transfer mismatch rejection.

During JOINT, configuration-transition commands require both old and new quorum.

### V9-H2 — Missing mandatory falsification cases
**ACCEPTED — BLOCKER**

R8 v10 must add explicit cases for:
- valid constitutional successor re-establishing revoked scope;
- cross-lineage fallback blocked without constitutional mapping;
- project/org policy attempting to broaden ANYScopePermission;
- ACTIVATE not matching committed JOINT certificate;
- state-transfer mismatch across log/head/idempotency/certificate-chain/config generation.

## 4. Accepted medium findings

### V9-M1 — CTS-1 JOINT quorum semantics
**ACCEPTED**

Define current valid configuration precisely:
- before JOINT: old quorum;
- after ENTER_JOINT and before ACTIVATE: both old and new quorums;
- after ACTIVATE: new quorum only, from the exact activation index/sequence.

### V9-M2 — Replacement-scope specificity
**ACCEPTED**

A successor re-establishing a revoked scope must either:
1. preserve the exact revoked scope and therefore the same specificity; or
2. carry an explicit constitutional ScopeReplacementMapping that defines old scope, new scope, lineage transition, and replacement specificity semantics.

Without the mapping, changed-scope successor is ineligible to unblock the revoked scope.

### V9-M3 — Same-Smax non-successor registration
**ACCEPTED**

An ACTIVE entry at the same semantic lineage/scope as a REVOKED entry must explicitly identify the revoked predecessor or a constitutionally mapped predecessor.

Otherwise registration returns `SEMANTIC_SUCCESSOR_REQUIRED`; misleading ACTIVE state is not admitted.

### V9-M4 — Blind-packet hygiene
**ACCEPTED AS PACKAGING FIX**

The v10 blind review packet will remove adjudication-hash metadata from canonical inherited design presentation while preserving exact canonical source content separately in the repository.

The packet may identify candidate commits/blobs but must not expose prior review/adjudication dispositions.

## 5. Bounded interpretation

The reviewer explicitly found no new critical bypass in inherited T0/MTR/GGS/AIEP/time/provenance areas and found SPG/reconciler/effect logic adequate at design level.

Those findings are not promoted to qualification; they simply do not require v10 changes unless needed for consistency.

## 6. Successor rule

Create R8 v10 as a new successor overlay.

Do not mutate v4-v9.

R8 v10 must receive a fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v9 = `CHANGES_REQUIRED`
- R8 v10 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
