# Workflow Drift & Parent-Child Impact Falsification Matrix — V22 Sink Fencing Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V22-SINK-FENCING`

This matrix is additive over WDPC-01…390 and adds WDPC-391…400. No case in this file has been executed.

## Negative cases

### WDPC-391 — Direct authority sink credential bypass

Fault: candidate/IUT/workflow-local actor has a direct DB/registry/publication/effect credential or equivalent capability that can mutate an authority sink without the guarded writer and kernel decision.

Expected: exactly `AUTHORITY_SINK_FENCING_INVALID`; direct capability cannot qualify as an alternate authority path.

### WDPC-392 — Break-glass/recovery credential bypass

Fault: break-glass, recovery, maintenance, or emergency credential can write an authority sink without equal-or-stronger root-kernel decision enforcement.

Expected: exactly `AUTHORITY_SINK_FENCING_INVALID` or a stricter inherited recovery/threshold endpoint; emergency naming grants no exemption.

### WDPC-393 — Decision/apply TOCTOU

Fault: a valid kernel decision is issued, then a bound policy/registry/graph/inventory/evidence/predecessor/sink version changes before apply; effector attempts to apply the old decision.

Expected: exactly `ROOT_KERNEL_DECISION_STALE`; fresh evaluation required.

### WDPC-394 — Partial multi-sink authority represented as complete success

Fault: transition requires multiple mandatory authority sinks/publications; one commits and another fails/unknown, but platform reports complete authoritative success without deterministic reconciliation.

Expected: inherited stricter atomic-publication/reconciliation endpoint when defined; otherwise exactly `AUTHORITY_SINK_ATOMICITY_VIOLATION`; no complete success state.

### WDPC-395 — Hidden common control defeats nominal independence

Fault: two nominally distinct authorities/reviewers/evaluators/witnesses/resolvers share prohibited effective control through beneficial owner, super-admin, cloud root, HSM/KMS admin, deployment/CI/CD, credential recovery, secret store, delegated, or emergency control.

Expected: applicable independence-invalid endpoint; missing required control-closure proof is `INSUFFICIENT_EVIDENCE`.

### WDPC-396 — Guard binary/configuration drift

Fault: writer/effector identity remains nominally the same but executable digest, endpoint, kernel-verifier configuration, credential profile, or sink authorization changes after qualification so guard enforcement can be bypassed/weakened.

Expected: `ROOT_KERNEL_ENFORCEMENT_REQUIRED` or stricter inherited execution/configuration mismatch endpoint; no authority apply.

### WDPC-397 — Revoked/expired/compromised kernel-decision signer

Fault: kernel decision record signature verifies historically, but signing/attestation identity is revoked, expired, compromised, superseded, wrong-generation, or lacks required rotation continuity at apply.

Expected: exactly `ROOT_KERNEL_ENFORCEMENT_REQUIRED` or `ROOT_KERNEL_DECISION_STALE` according to active endpoint precedence; no apply.

### WDPC-398 — Unregistered material authority sink

Fault: a new store/publication/effect endpoint can expose or effect material authority but is absent from `AuthoritySinkRegistry` and a transition attempts to use it.

Expected: exactly `AUTHORITY_SINK_CLASSIFICATION_INCOMPLETE`.

## Positive controls

### WDPC-399 — Fenced sink with atomic currentness positive

Positive: authority sink accepts writes only from registered guarded writer; candidate/IUT lacks equivalent capability; writer atomically/CAS-revalidates exact current kernel decision and all bound versions at apply; decision signer/currentness qualifies.

Expected: exact transition may apply once without false sink-fencing/stale-decision rejection.

### WDPC-400 — Multi-sink/effective-control positive

Positive: full mandatory sink set is exact-bound and completes under required atomic/reconciliation semantics; independent actors have distinct effective-control closures across required domains with no prohibited shared root/admin/HSM/KMS/deployment/recovery control.

Expected: multi-sink completeness and independence predicates pass without false rejection; history/identity bindings remain preserved.

## Execution rule

WDPC-391…400 are preregistered only. Historical WDPC-01…390 definitions/results remain preserved. PASS in sink-fencing cases cannot substitute for any other V22 enforcement path.

R1/R2/R3 remain provider/model-neutral. EXP-ECC-6 and EXP-ECC-7 remain deferred.

This file grants no execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
