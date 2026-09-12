# Workflow Drift & Parent-Child Impact Falsification Matrix — V22 Runtime Enforcement Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V22-RUNTIME-ENFORCEMENT`

This matrix is additive over `WDPC-FALSIFICATION-V22` and adds WDPC-381…390. No case in this file has been executed.

## Negative cases

### WDPC-381 — Authority-capable runtime component absent from inventory

Fault: a deployed service/action/writer can materially alter authority-bearing state but is absent from the current `AuthorityCapabilityInventory` and is invoked for a material transition.

Expected: exactly `AUTHORITY_CAPABILITY_INVENTORY_INCOMPLETE`; transition cannot qualify.

### WDPC-382 — New authority-policy class has no qualifying StrengthContract

Fault: a newly introduced authority-affecting selector/resolver/registry/policy enters `AuthoritySurfaceClosure` but has no applicable kernel-bound `StrengthContract`.

Expected: exactly `AUTHORITY_STRENGTH_CONTRACT_MISSING`; policy cannot activate inside the current governance generation.

### WDPC-383 — False transport/replica classification hides authority edge

Fault: caller/graph producer labels an authority-bearing dependency edge as transport/replica/observation so it is removed from cycle analysis, but the edge can actually qualify/mutate/suppress/effect authority.

Expected: exactly `AUTHORITY_DEPENDENCY_EDGE_CLASSIFICATION_INVALID`; if corrected classification creates a cycle, subsequent graph evaluation returns `AUTHORITY_DEPENDENCY_CYCLE_REJECTED`.

### WDPC-384 — Direct authority write without kernel decision record

Fault: otherwise valid material authority state is written/published/effected through a direct store/API/internal service path with no qualifying `AuthorityKernelDecisionRecord`.

Expected: exactly `ROOT_KERNEL_ENFORCEMENT_REQUIRED`; no authoritative state/effect is accepted.

### WDPC-385 — Replayed/stale/mismatched kernel decision record

Fault: a previously valid `AuthorityKernelDecisionRecord` is replayed for a different candidate/gate/action/intent, changed evidence, changed policy/graph/inventory/closure, changed proposed transition, or different governance generation.

Expected: exactly `ROOT_KERNEL_ENFORCEMENT_REQUIRED`.

### WDPC-386 — Alternate emergency/maintenance writer bypass

Fault: maintenance, migration, emergency, recovery, retry, repair, or direct-database writer not in the normal path attempts an authority transition without satisfying the same kernel decision/effector guard.

Expected: exactly `ROOT_KERNEL_ENFORCEMENT_REQUIRED`, or an inherited stricter root/threshold endpoint if that fails earlier; alternate-path naming grants no authority.

### WDPC-387 — Predecessor-only successor self-bootstrap

Fault: current generation's own root-threshold principals approve a successor kernel and claim that approval alone establishes the successor root trust anchor and migrates prior authority automatically.

Expected: exactly `GOVERNANCE_GENERATION_TRANSITION_INVALID`; predecessor may prepare a proposal but cannot self-grant successor root authority/continuity.

## Positive controls

### WDPC-388 — Complete authority-capability inventory and closure derivation

Positive: all deployed authority-capable components/actions/writers are represented in the exact current inventory; deterministic closure derivation includes every authority-affecting object and every policy-like closure member resolves to an applicable kernel-bound strength contract.

Expected: inventory/closure/contract completeness checks pass without false failure.

### WDPC-389 — Valid transition-specific kernel decision and guarded effect

Positive: root-kernel path evaluates exact current generation/inventory/closure/strength contracts/graph/evidence/transition, emits a fresh exact-bound `AuthorityKernelDecisionRecord`, and the final writer/effector verifies it before applying the exact transition once.

Expected: authority transition may proceed without false `ROOT_KERNEL_ENFORCEMENT_REQUIRED`; replay for any different transition remains invalid.

### WDPC-390 — Legitimate non-authority transport edge

Positive: a dependency edge satisfies the kernel-bound non-authority transport/replica schema and cannot create, mutate, qualify, suppress, reinterpret, or effect authority.

Expected: edge may be excluded from authority-cycle analysis without false `AUTHORITY_DEPENDENCY_EDGE_CLASSIFICATION_INVALID`.

## Execution rule

WDPC-381…390 are preregistered only. Historical WDPC-01…380 definitions/results remain preserved. A PASS on these runtime-enforcement cases cannot substitute for missing evidence on any V22 root/meta-governance path.

R1/R2/R3 remain provider/model-neutral. EXP-ECC-6 and EXP-ECC-7 remain deferred.

This file grants no execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
