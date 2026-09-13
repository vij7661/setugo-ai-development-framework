# V24 I11 Scientific Root-Cause Consolidation

Status: **DETERMINISTIC/REFERENCE FALSIFICATION RED — ROOT CAUSES FROZEN BEFORE REPAIR**

Exact pre-scientific frontier: `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`
Frozen I10 implementation: `9836dc3ff233cca582f485434fc1c6494cf7eb05`
Frozen I10 tree: `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`
Reviewed plan: V8
Runtime for scientific Actions executions: Python `3.12.7`, `PYTHONHASHSEED=0`, UTC.

This document consolidates already-preserved scientific results. It does not rewrite any case result and makes no implementation repair.

## 1. Executed deterministic/reference surface

Total executed cases: **44**

PASS: **8**
- WDPC-433
- WDPC-446
- WDPC-447
- WDPC-453
- WDPC-463 (reference mechanism-only positive)
- WDPC-481
- WDPC-482
- WDPC-490

`FAIL_CODE_DEFECT`: **36**

Cluster A preserved adjudication commit: `4e6e68262b8d217d1a9b10d17c88d5b4f9701f66`.

Cluster B scientific execution run: `34749496950`, execution SHA `0c4857f35c8d6c3b3e3c96b857285284584ff5a0`, adjudication commit `274e7b2f6a6bb2ed143dad680a4d23459d5c25ef`.

Clusters C–H reference execution run: `34749374558`, execution SHA `3f925c2ad69f4be722de00ddd544aea07c4a08e4`, adjudication commit `dfad8fd82db86930e17d938779f53164de70a7b5`.

## 2. Root-cause family RC-1 — governed endpoint projection is incomplete

Family ID:
`GOVERNED_ENDPOINT_PROJECTION_INCOMPLETE_ACROSS_V24_VALIDATORS`

Affected executed cases: **26**

WDPC-431, 432, 434, 435, 436, 437, 438, 439, 440, 441, 442, 445, 448, 450, 451, 452, 455, 456, 457, 459, 471, 479, 483, 499, 501, 502.

### Evidence shape

For 25 of these cases the frozen implementation produced one or more internal `problems[]` entries that identify the injected fault but returned only a coarse module state such as:

- `EFFECTIVE_CONTROL_INCOMPLETE`
- `I6_CONSTRUCTION_INCOMPLETE`
- `AGGREGATE_BUDGET_INCOMPLETE`
- `GENERATION_MIGRATION_INCOMPLETE`
- `AUTHORITY_UNIVERSE_INCOMPLETE`
- `COMPLETENESS_BOOTSTRAP_INCOMPLETE`
- `V24_APPLY_BLOCKED`

rather than the exact implementation-emitted governed endpoint required by reviewed V8.

WDPC-434 is the same projection-layer failure even though `problems[]` is empty: the aggregate validator deterministically computes an unresolved `INSUFFICIENT_EVIDENCE` reconciliation outcome and correctly prevents authority success, but exposes only `AGGREGATE_BUDGET_CONSTRUCTION_VALID` instead of the preregistered `AGGREGATE_BUDGET_OUTCOME_UNKNOWN` governed state.

The reviewed harness is correct to reject diagnostic/state normalization. A remediation must add an authoritative endpoint-selection/projection layer; it must not make the harness accept coarse construction states.

## 3. Root-cause family RC-2 — material facts outside named schemas are not closed-world/fail-closed

Family ID:
`MATERIAL_AUTHORITY_SURFACE_CLOSURE_NOT_DERIVED_OR_ENFORCED`

Affected executed cases: **10**

WDPC-444, 454, 473, 475, 476, 478, 480, 487, 488, 492.

These cases differ from RC-1 because the relevant frozen validator did not merely choose the wrong endpoint. It accepted/ignored the injected material condition or otherwise returned a valid/ready state without detecting the condition.

### RC-2 manifestations

- **WDPC-444 — divergent independent universe projections:** the authority-universe implementation consumes one singular `independent_universe_projection`; a second qualifying projection can be present without a reconciliation/divergence check.
- **WDPC-454 — uncatalogued normative prose:** normative completeness is bounded by caller-declared locator inventory, allowing a new normative-looking clause outside that inventory to be defined away.
- **WDPC-473 — unanchored completeness result:** a completeness record marked as process-memory-only is accepted because durable `CompletenessQualificationLedger` storage/anchoring is not part of the construction validator's enforced schema.
- **WDPC-475 — shared IUDA source path:** two nominally independent projections can share one prohibited source path because IUDA projection-source provenance is not consumed by effective-control validation.
- **WDPC-476 — deployment self-report attestation:** `measurement_source=DEPLOYMENT_SELF_REPORT_ONLY` is ignored; the validator verifies digest agreement/attestor domains but not independent measurement provenance.
- **WDPC-478 — suppressed material discovery observation:** a runtime-observed unadmitted material path is ignored when caller-controlled `material_discovery_pending` is false; apply returned `V24_APPLY_READY`, `allowed=true`. Separate finding commit: `a8029b1655bae388c6b0c8df7ff73c4e62fd0c94`.
- **WDPC-480 — unsigned/unbound universe derivation:** no `UniverseDerivationDecisionRecord` is required/consumed by completeness construction, so absence of the decision record is not detected.
- **WDPC-487 — functional authority path labeled non-authority:** path source/writer capability is not reconciled against the sink's admitted writer set, allowing a materially authority-capable path to remain construction-valid.
- **WDPC-488 — independent audit finds unregistered writer:** the effect-path set can contain a material direct writer without enforcing writer admission/capability/sink/guard closure.
- **WDPC-492 — future omission-sensitive registry:** completeness-required subject kinds are a fixed named set, so a newly introduced omission-sensitive registry can escape automatic completeness classification.

### Generalized defect

Across these surfaces, candidate-owned or manually named schema/inventory boundaries are being treated as the universe of material facts. V24's design requires the opposite: material authority capability/evidence/completeness surfaces must be independently derived or generically classified, and unknown/unmodeled material inputs must fail closed.

The repair must therefore be systemic rather than ten case-specific `if` statements.

## 4. Failure-history invariants

The following remain immutable scientific history:

- WDPC-454 stays RED even after repair.
- The 35 Cluster B/C–H REDs stay RED even after repair.
- Earlier Actions startup/queue failures remain infrastructure evidence, not scientific case results.
- No successful successor rerun may overwrite these records; successor results append new evidence.

## 5. Evidence-gated and blocked cases

External/manual evidence cases remain `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED` until qualifying evidence exists. Evidence manifest is on branch `testing/v24-i11-external-evidence-manifest-v1` and is exact-bound to the frozen V8/I10 subject.

WDPC-469 and WDPC-495 remain `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION`.

WDPC-503 remains static/manual unresolved. Frozen standards specify the expected in-generation mutation rejection, but the frozen I10 tree does not itself establish the required exact implementation endpoint; design text is not substituted for implementation evidence.

Positive controls whose same-mechanism negative prerequisites failed remain `BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE`; they are not false PASSES.

## 6. Remediation boundary

The deterministic/reference falsification phase has now produced enough evidence to freeze two systemic repair families:

1. **Canonical governed-endpoint projection/precedence from typed failure conditions**, without diagnostic-string normalization in the test harness.
2. **Generic closed-world material-surface discovery/classification and evidence provenance enforcement**, so new/unknown material authority facts cannot disappear outside manually named schemas.

WDPC-478 additionally requires an authoritative discovery-event latch/sequence into the apply boundary rather than a caller-controlled boolean alone.

No repair should be scoped as “make WDPC-N pass.” Repair must satisfy these generalized contracts and then be refalsified against the affected cases plus inherited regression.

Inherited WDPC-01…430 regression execution has not yet begun.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
