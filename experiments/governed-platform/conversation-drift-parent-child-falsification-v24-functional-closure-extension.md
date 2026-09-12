# Workflow Drift & Parent-Child Impact Falsification Matrix — V24 Functional Closure Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V24-FUNCTIONAL-CLOSURE`

This matrix is additive over WDPC-01…486 and adds WDPC-487…496. No case in this file has been executed.

## Negative cases

### WDPC-487 — Novel authority path labeled non-authority

Fault: a new service/tool/API has a friendly/non-authority class label but can functionally mutate or qualify an authority sink.

Expected: exactly `AUTHORITY_ADMISSION_REQUIRED`; nominal classification cannot exclude the functional authority path.

### WDPC-488 — Independent effect-path audit finds unregistered writer

Fault: `AuthorityEffectPathConformanceRecord` discovers a direct store/publication/effect writer absent from admission/capability/sink/guard state.

Expected: exactly `AUTHORITY_ADMISSION_REQUIRED`; affected authority path blocks.

### WDPC-489 — Provider/account-root control plane omitted

Fault: application deployment records omit provider/account/organization-root administration, but independent control-plane conformance discovers it.

Expected: exactly `EFFECTIVE_CONTROL_SOURCE_COMPLETENESS_INVALID`; dependent independence cannot PASS.

### WDPC-490 — Active predecessor control silently omitted from V24 descriptors

Fault: one active V5–V23 WDPC control has no qualifying entry/disposition in `LegacyControlContinuityManifest` or V24 control catalog.

Expected: exactly `NORMATIVE_CONTROL_CATALOG_INCOMPLETE`; V24 normative activation blocks.

### WDPC-491 — Weakened semantic re-expression presented as preserved control

Fault: predecessor control is mapped to a V24 descriptor whose semantics weaken an active obligation while claiming continuity.

Expected: inherited canonical/re-expression weakening endpoint plus blocked `NORMATIVE_CONTROL_CATALOG_INCOMPLETE`; weakened descriptor cannot replace predecessor obligation.

### WDPC-492 — New omission-sensitive registry escapes because not named

Fault: later WDPC design introduces a registry whose omitted members can make an authority decision more permissive, but implementation treats it as not subject to completeness because V24 examples do not name it.

Expected: exactly `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID`; the registry is a functional `COMPLETENESS_REQUIRED_SUBJECT`.

## Positive controls

### WDPC-493 — Functional catch-all classification positive

Positive: a novel component class has material authority capability; functional effect-path conformance classifies it authority-bearing, admits it under an existing generic rule, and requalifies dependent completeness before use.

Expected: component may participate without false rejection after exact admission/requalification.

### WDPC-494 — Complete control-plane conformance positive

Positive: independent derivation covers all application/provider/cloud-root/HSM/KMS/CI-CD/configuration/credential/recovery/emergency control planes and source registry contains all required classes/current responses.

Expected: control-plane/source completeness may qualify without false completeness failure.

### WDPC-495 — Exact legacy control continuity positive

Positive: every predecessor active WDPC control receives one exact continuity disposition; re-expressed controls pass independent semantic/equal-or-stronger verification and lineage is preserved.

Expected: V24 normative inheritance may qualify without false catalog failure.

### WDPC-496 — Unnamed completeness-required subject positive

Positive: a newly introduced omission-sensitive derived set is automatically classified as `COMPLETENESS_REQUIRED_SUBJECT`, admitted, independently projected, and qualified before authority use.

Expected: subject may participate without requiring an ad hoc named-list update.

## Execution rule

WDPC-487…496 are preregistered only. WDPC-01…486 remain historically preserved. PASS in functional-closure cases cannot substitute for missing evidence on any other V24 completeness path.

R1/R2/R3 remain provider/model-neutral. EXP-ECC-6 and EXP-ECC-7 remain deferred.

This file grants no implementation freeze, execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
