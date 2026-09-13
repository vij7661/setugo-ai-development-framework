# V24 I11 WDPC-478 Scientific Finding

Status: **RED — SUBSTANTIVE DISCOVERY/APPLY COUPLING DEFECT**

Case: `WDPC-478 — Material authority discovery event suppressed`
Execution run: `34749496950`
Execution SHA: `0c4857f35c8d6c3b3e3c96b857285284584ff5a0`
Frozen I10 subject: `9836dc3ff233cca582f485434fc1c6494cf7eb05`
Reviewed V8 expected endpoint: `AUTHORITY_ADMISSION_REQUIRED`

## Preregistered fault

Runtime observes an unadmitted authority-capable component/edge/source/control, but the discovery event is dropped or ignored and normal authority processing continues. The affected authority path must block.

## Observed result

The scientific fixture supplied a runtime-observed unadmitted material path while `material_discovery_pending` was false. The frozen apply guard returned:

- `state = V24_APPLY_READY`
- `allowed = true`
- `problems = []`

Scientific result: `FAIL_CODE_DEFECT`.

## Root cause

The frozen `evaluate_v24_apply()` guard consumes only the caller-supplied `material_discovery_pending` boolean for discovery state. It does not consume, bind, or independently reconcile an observed discovery-event/material-path record. Therefore an observation can exist while the boolean remains false, and the apply path proceeds.

This is not merely a governed-endpoint projection defect. The candidate allowed the apply path under the preregistered suppressed-discovery condition.

Defect family:
`MATERIAL_DISCOVERY_OBSERVATION_NOT_AUTHORITATIVELY_LATCHED_TO_APPLY_GUARD`

No implementation repair is made during the falsification sweep.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
