# V24 I11 V6 R3 — Material Surface Construction Evidence

Status: **CONSTRUCTION COMPLETE / QUALIFICATION NOT GRANTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Lineage

Branch: `implementation/v24-i11-v6-r3-material-surface`

Validated construction head: `3d2833106aedcfaf6d1cea4bab322d7350950d0c`

Validated tree: `e21e67e2bc3b30f3c0e0d06addb0c8531ff32c76`

The branch descends from validated R2 evidence and ultimately frozen I10 `9836dc3ff233cca582f485434fc1c6494cf7eb05`.

## Implemented mechanisms

- append-only material observation record sequence and predecessor chaining;
- durable observation head / anchor / independent witness validation;
- fork/rollback fail-closed checks;
- two independently controlled material-surface derivations by default;
- candidate-self-report-only derivation rejection;
- divergence rejection;
- current independent materiality classifications;
- material effect-path closure over writer admission, capability, sink admitted writers, dependencies, guards, control-plane evidence, surface membership, and observation head;
- authoritative discovery latch from real observations to admission state;
- observed-but-unadmitted material path emits typed `AUTHORITY_ADMISSION_REQUIRED` condition;
- no caller `material_discovery_pending` boolean exists in the R3 production interface.

## CI history

### Preserved construction failure

Run `34753748375`: **FAILURE**.

14/15 R3 tests passed. The single failure was a test-expectation defect: the implementation correctly returned `MATERIAL_SURFACE_DERIVATION_DIVERGENCE:1`; the test additionally demanded `MATERIAL_SURFACE_OBSERVED_MEMBER_OMITTED:PATH-B`, even though PATH-B remained present in the first derivation and therefore was not independently omitted from the derived reference set.

Production code was not changed. Only the invalid extra test assertion was removed.

### Validated run

Run `34753801274`: **SUCCESS**.

Environment: exact Python `3.12.7`.

Passed:
- R3 material-surface construction tests;
- R1 governance-foundation regression;
- R2 endpoint-projection regression;
- anti-case-specific / anti-caller-discovery-boolean gate;
- construction-only authority assertion.

## Scientific status

No WDPC case was rerun.

Historical scientific REDs remain append-only. In particular, WDPC-478 remains the historical evidence that the frozen I10 caller-controlled discovery boolean was unsafe; R3 construction does not retroactively change that result.

`R3_CONSTRUCTION = PASS`

`R3_RUNTIME_QUALIFICATION = NOT_CLAIMED`

Next implementation workstream: **R4 — qualified revalidation snapshot source, DecisionApplyLatchRecord, ApplyGuardVerifier, and stale-state re-evaluation before effect**.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
