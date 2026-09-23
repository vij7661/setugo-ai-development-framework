# R8 v12 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- R8 v12 design commit: `8250f35acb371ce85e818c5ecdf9a11250fa1430`
- R8 v12 design blob: `f8c8e979271c242e8a87c254cbe6c9d46385dd84`
- GCC-1 generated catalog commit: `39dd1c1873a0c3b2276eab581a081f2c0afc99a1`
- GCC-1 catalog blob: `cef6d45ecfda5dc780a339f1795c140082f62583`
- v12 blind TXT packet commit: `4f8f0bfe4d088e13a6c718704ea73a82ddab0658`
- v12 blind TXT packet blob: `00aa51ecf7910c2dbde16bfbab4dc6e463ee0daa`

Independent review evidence:
- `review-evidence/R8-V12-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- preserved commit: `d8cef283c71ad1e4df39e67f713d96b5a5a0aa02`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v12 materially improved blindness, current-state semantic binding, resolver-time ANY enforcement, semantic-state sealing, rotation freeze semantics, and guard catalog generation. However executable-schema freeze remains blocked by two critical design gaps, three high gaps, and several medium clarity/consistency gaps.

R8 v12 remains immutable as the reviewed exposure.

## 2. Accepted critical blockers

### V12-C1 — ResolverPolicy has no authoritative implementation allowlist
**ACCEPTED — BLOCKER**

R8 v13 must define a CSM-bound `ResolverImplementationRegistry` that explicitly maps each active ResolverPolicy version/digest to the exact allowed:
- resolver implementation digest(s);
- runtime manifest digest(s);
- workload-attestation policy;
- conformance-vector set digest;
- activation and retirement sequence;
- lifecycle state.

Passing conformance vectors or presenting a policy digest is insufficient unless the implementation/runtime pair is ACTIVE in the registry for the exact ResolverPolicy.

DPS/seal verification must bind and verify the exact registry record.

### V12-C2 — ScopeReplacementTruthTable incomplete
**ACCEPTED — BLOCKER**

R8 v13 must freeze a complete machine-readable truth table, not merely enum names.

The truth table must explicitly determine:
- exact old-scope match;
- exact/mapped new-scope match;
- permitted ANY components;
- current ANY permission;
- mapping effective sequence;
- whether the decision is within the revoked old scope;
- whether the mapping may replace only exact old scope or mapped scope;
- whether a broader destination would accidentally unblock decision scopes outside the authorized replacement set;
- result/error for every branch.

Reference vectors must cover both allowed and denied replacement patterns.

## 3. Accepted high findings

### V12-H1 — REVOKED + ACTIVE coexistence at Smax
**ACCEPTED**

R8 v13 must define:
- if any applicable Smax entry is REVOKED, revoked-branch traversal dominates ordinary ACTIVE selection;
- unrelated ACTIVE entries at Smax cannot bypass the revoked scope;
- only an explicitly linked valid successor/mapping may discharge the revoked branch;
- ambiguous competing successor paths fail closed.

### V12-H2 — conflicting inherited guard table
**ACCEPTED**

The design must not expose multiple contradictory guard identities as co-authoritative.

R8 v13 must create one CSM-bound `GuardRegistry-1` with a unique record for each guard ID.

For G001-G130, bind the corrected GCC-1 generated catalog identity and explicitly supersede legacy manually consolidated guard tables as review/index artifacts where they conflict.

Canonical case semantics remain sourced from their canonical design sections.

A guard-registry conflict or duplicate semantic definition fails packet generation.

### V12-H3 — AIM-3 applicability underspecified
**ACCEPTED**

R8 v13 must freeze an AIM applicability tuple and deterministic resolver:
- semantic_input_id;
- semantic class;
- decision scope;
- descriptor scope;
- effective sequence;
- lifecycle;
- predecessor/successor chain.

Specificity/matching is derived, not caller-selected.

Exactly one highest-specificity ACTIVE descriptor may resolve; blocker/conflict rules are explicit.

## 4. Accepted medium findings

### V12-M1 — semantic_state_sequence explicit in state root
**ACCEPTED**

Add `semantic_state_sequence_i` as an explicit GCP-1 field in LASAuthorityStateRoot, even though it is derivable from committed log index.

### V12-M2 — BSP-2 version-aware residual scan
**ACCEPTED**

Freeze exact residual-scan behavior:
- current_candidate_version is an explicit input;
- outcome terms attached to versions < current_candidate_version are forbidden;
- current candidate status is retained;
- semantic references to outcome words inside guard/test definitions are not mistaken for review outcomes.

### V12-M3 — barrier error taxonomy
**ACCEPTED**

Freeze:
- same rotation_id + same config/STC -> idempotent replay;
- same rotation_id + different config or STC -> `IDEMPOTENCY_CONFLICT`;
- different rotation_id on already reserved barrier -> `BARRIER_ALREADY_RESERVED`;
- two contradictory valid reservations observed -> `STC_EQUIVOCATION`.

### V12-M4 — conformance-vector generation/runtime verification
**ACCEPTED**

Before schema freeze, the design must freeze:
- vector manifest format;
- vector generator/artifact digest;
- expected-output digest;
- execution/runtime identity;
- pass/fail evidence contract.

This becomes part of resolver implementation qualification.

## 5. Bounded interpretation

The reviewer found the following v12 areas directionally or materially sound:
- BSP-2 blindness posture;
- CSM-5 named-head/current snapshot model;
- current semantic_state_sequence concept;
- resolver-time ANY revalidation;
- RBP-2 freeze scope;
- DPS-v3/seal TOCTOU binding;
- no material inherited-control regression;
- fail-closed liveness posture.

These observations grant no qualification authority.

## 6. Successor rule

Create R8 v13 as a new successor overlay.

Do not mutate v4-v12.

R8 v13 must receive a fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v12 = `CHANGES_REQUIRED`
- R8 v13 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- authority effect = `NONE`
