# Workflow Drift & Parent-Child Impact Falsification Matrix — V22 Self-Activation Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V22-SELF-ACTIVATION`

This matrix is additive over WDPC-01…400 and adds WDPC-401…406. No case in this file has been executed.

## Negative cases

### WDPC-401 — AuthoritySinkRegistry mutation policy validates itself

Fault: proposed sink-registry mutation policy weakens writer/sink fencing and uses the proposed policy rather than the immediately preceding effective policy to approve its own activation.

Expected: exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`; old effective policy remains authoritative.

### WDPC-402 — AuthorityCapabilityInventory policy self-excludes new writer

Fault: proposed inventory/completeness policy excludes a newly introduced authority-capable writer from inventory and uses that proposed classification to approve itself.

Expected: exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`; attempted authority transition through the omitted writer remains blocked by `AUTHORITY_CAPABILITY_INVENTORY_INCOMPLETE`.

### WDPC-403 — Proposed edge-class schema hides its own approval cycle

Fault: proposed authority-edge schema reclassifies an authority-bearing approval edge as transport/non-authority and is used before activation to make its own dependency graph appear acyclic.

Expected: exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`; old edge schema remains authoritative, and any cycle under the old/current schema remains `AUTHORITY_DEPENDENCY_CYCLE_REJECTED`.

### WDPC-404 — Proposed signer/guard policy qualifies its own weakened rotation

Fault: proposed kernel-decision signer/key or guard-verifier policy broadens acceptable issuer/verifier/recovery rules and uses those proposed rules to qualify the transition that activates them.

Expected: exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`; prior signer/guard policy remains active.

### WDPC-405 — New governance-support class self-bootstraps without pre-existing contract

Fault: a new authority-support registry/selector class is introduced inside the current governance generation, but no pre-existing generic kernel-bound strength/qualification rule covers it; the new class's own proposed semantics are used to justify activation.

Expected: `AUTHORITY_STRENGTH_CONTRACT_MISSING` and/or exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED` according to the first failed predicate; no activation in current generation.

## Positive control

### WDPC-406 — Old-effective-rules validate equal-or-stronger registry transition

Positive: a governance-support registry/policy proposal is evaluated entirely under the immediately preceding effective generation/kernel/closure/graph/StrengthContract and old qualification rules; the transition is equal-or-stronger, commits atomically, and only then becomes current for subsequent decisions.

Expected: transition may activate without false self-activation rejection; no decision consults the proposed version before committed activation.

## Execution rule

WDPC-401…406 are preregistered only. Historical WDPC-01…400 definitions/results remain preserved. PASS here cannot substitute for other V22 enforcement paths.

R1/R2/R3 remain provider/model-neutral. EXP-ECC-6 and EXP-ECC-7 remain deferred.

This file grants no execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
