# V16 Slice 2 — IAR4 Repair Contract

Status: **FROZEN NARROW REPAIR SCOPE / CONSTRUCTION ONLY**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This contract repairs the three High findings recorded in `V16-SLICE-2-INTERNAL-ADVERSARIAL-REVIEW-004.md`. It does not expand Slice 2 into runtime qualification or effect authority.

## R1 — Single owned graph snapshot per public validation path

Every public Slice 2 wrapper operation that combines graph validation with signer qualification, candidate-control, independence, or registry authority MUST derive one fail-closed plain owned snapshot of `graph_chain` at the public boundary and use that same owned snapshot for all downstream graph-dependent checks in that call.

The implementation MUST NOT re-read caller-owned graph dictionaries/lists after the snapshot. Non-string mapping keys and non-plain containers fail closed.

Mandatory adversarial proof: mutation of the original caller graph after snapshot acquisition cannot change the validated/qualified relation or create a `construction_binding_valid=true` result for a graph different from the pinned/bound graph.

## R2 — Exact historical predecessor content binding

Current baseline manifest `REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-002` MUST bind:

- predecessor manifest ID `REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001`; and
- exact predecessor Git blob `27983a245408589ec39681aa69da3a003294ddd8`.

The current manifest index MUST carry the same historical ID→blob relation. The canonical workflow MUST recompute the historical file's Git blob and reject same-ID/different-content substitution.

Historical v1 content remains unchanged.

## R3 — Strict duplicate-free exact-schema JSON

Canonical manifest/index loading MUST reject duplicate JSON object keys before semantic validation.

Exact top-level field sets MUST be enforced for:

- current baseline manifest v2;
- IAR1 manifest;
- IAR2 manifest;
- IAR3 manifest;
- current-manifest index;
- each test entry.

Unknown top-level or test-entry fields fail closed. Duplicate keys fail closed. Required scalar types remain exact where applicable.

## Stable test identity

Add a separately versioned IAR4 test manifest. Existing 61 tests remain mandatory and unchanged. New IAR4 tests MUST have new requirement IDs and prove at minimum:

1. caller graph mutation after owned snapshot cannot alter the exact validated graph relation;
2. historical predecessor blob matches the frozen v1 content;
3. same predecessor ID with different content is rejected by lineage verification;
4. duplicate top-level manifest key is rejected;
5. duplicate per-test key is rejected;
6. unknown top-level manifest field is rejected;
7. unknown per-test field is rejected;
8. valid current manifest/index set passes strict loading while qualification/effect authority remains blocked.

The next canonical workflow must use a new V5 harness, exact-bind all current source/test revisions, verify current manifests through strict duplicate-free exact-schema logic, and preserve every earlier RED/PASS record.

## Stopping rule

A green construction run does not close Slice 2. After repair execution, perform another internal adversarial review. Freeze is allowed only when that review identifies zero open Critical/High findings in Slice 2 construction semantics.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
