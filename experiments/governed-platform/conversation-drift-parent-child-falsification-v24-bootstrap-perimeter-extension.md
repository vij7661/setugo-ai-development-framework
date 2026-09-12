# Workflow Drift & Parent-Child Impact Falsification Matrix — V24 Bootstrap and Perimeter Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V24-BOOTSTRAP-PERIMETER`

This matrix is additive over WDPC-01…496 and adds WDPC-497…506. No case in this file has been executed.

## Negative cases

### WDPC-497 — Discovery-only admission with unadmitted direct sink access

Fault: inventory/discovery reports a closed authority universe, but a non-admitted principal still possesses direct material sink write/effect capability outside the guarded admission path.

Expected: affected authority qualification remains `INSUFFICIENT_EVIDENCE` or inherited stricter sink-fencing failure; no authority apply may qualify.

### WDPC-498 — Admission perimeter IAM drift after qualification

Fault: qualifying perimeter record exists, then a new service account/credential/recovery principal is granted material sink capability before authority apply without requalification.

Expected: kernel decision becomes stale and apply is blocked; exact endpoint `ROOT_KERNEL_DECISION_STALE` unless a stricter sink/admission endpoint fails earlier.

### WDPC-499 — Completeness IUDA self-bootstraps recursively

Fault: initial IUDA qualification depends on a V24 completeness record that itself requires that same IUDA to be qualified.

Expected: exactly `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE` or `INSUFFICIENT_EVIDENCE` according to whether the circularity is in genesis configuration or later qualification; no completeness PASS.

### WDPC-500 — Operational root relabeled as independent bootstrap completeness authority

Fault: root operational principals are placed into the bootstrap completeness authority set and counted as the required external independent domain solely by relabeling.

Expected: exactly `INSUFFICIENT_EVIDENCE`; required external independence is not satisfied.

### WDPC-501 — Bootstrap completeness authority uses candidate as sole source

Fault: bootstrap completeness authority derives its universe only from the candidate registry/table it is qualifying.

Expected: exactly `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID`; circular candidate-self-source cannot qualify completeness.

### WDPC-502 — Hidden/null-parent IUDA lineage reset

Fault: an ordinary IUDA is introduced with no traceable bootstrap or governed predecessor lineage and is used for a material completeness proof.

Expected: applicable governance lineage/reset rejection; absent qualifying lineage yields `INSUFFICIENT_EVIDENCE` and the IUDA cannot count.

### WDPC-503 — In-generation bootstrap completeness power broadening

Fault: active bootstrap completeness authority expands permitted subject classes or independence powers inside the same generation without successor-generation constitutional change.

Expected: applicable root/kernel/meta-policy weakening or in-place mutation rejection; broadened authority never activates.

### WDPC-504 — Sink lacks independently enforceable deny-by-default boundary

Fault: a material authority sink cannot technically/equivalently deny unadmitted direct writers, yet design attempts to treat inventory/discovery completeness as closed-world enforcement.

Expected: exactly `INSUFFICIENT_EVIDENCE`; sink cannot qualify as a V24 authority sink until an equivalent unavoidable guard exists.

## Positive controls

### WDPC-505 — Enforced admission perimeter positive

Positive: material sink accepts authority writes/effects only from admitted guarded writer set, independent perimeter record confirms IAM/capability denial for unadmitted principals, and apply revalidates current record/admissions atomically.

Expected: perimeter may qualify without false admission/perimeter failure.

### WDPC-506 — Non-circular bootstrap completeness authority positive

Positive: genesis record binds external bootstrap completeness authority set and independent source contracts via out-of-band trust ceremony; initial authority does not depend on descendant V24 completeness machinery, and later IUDA rotations use active V24 rules.

Expected: bootstrap completeness path may qualify as an explicit residual trust boundary without false recursive/self-grant rejection.

## Execution rule

WDPC-497…506 are preregistered only. WDPC-01…496 remain historically preserved. PASS here cannot substitute for missing evidence on any other V24 completeness path.

R1/R2/R3 remain provider/model-neutral. EXP-ECC-6 and EXP-ECC-7 remain deferred.

This file grants no implementation freeze, execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
