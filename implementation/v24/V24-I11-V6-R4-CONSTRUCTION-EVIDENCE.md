# V24 I11 V6 R4 — Decision/Apply Latch Construction Evidence

Status: **CONSTRUCTION COMPLETE / QUALIFICATION NOT GRANTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Lineage

Branch: `implementation/v24-i11-v6-r4-decision-apply-latch`

Validated construction head: `f96346ee66fdc136a398b5753141c11b58720dc3`

Validated tree: `66a05c0896863d172eee3e07fbf56a3f271cfd7a`

The branch descends from validated R3 construction evidence and ultimately frozen I10 `9836dc3ff233cca582f485434fc1c6494cf7eb05`.

## Implemented mechanisms

- qualified/current/independent revalidation snapshot-source contract;
- canonical one-snapshot digest over endpoint table, applicability, evaluator registry, condition registry, evidence registry, predicate-coverage qualification, material observation head, completeness ledger head, material surface, sink, writer, and guard;
- mixed-snapshot rejection;
- exact decision-to-current-snapshot binding comparison;
- any load-bearing digest/head drift requires a new exact current reevaluation before apply;
- stale decision cannot be used as a permissive compatibility fallback;
- reevaluated decision must bind the exact current snapshot and remain qualified;
- material writer/effect-path closure is checked against the same current observation head;
- selected endpoint must be `ALLOW` before effect;
- typed `DecisionApplyLatchRecord` material and deterministic latch digest;
- successor R4 interface has no caller-controlled `material_discovery_pending` input.

## CI

Workflow: `V24 V6 R4 Decision Apply Latch`

Run: `34754000494`

Result: **SUCCESS**

Environment: exact Python `3.12.7`.

Passed:
- R4 construction tests: 13/13;
- R1 governance-foundation regression;
- R2 endpoint-projection regression;
- R3 material-surface regression;
- inherited I9 `test_integrated_governed_mvp_v24_apply.py` regression;
- anti-case-specific / anti-caller-discovery-boolean gate;
- construction-only authority assertion.

## Historical I9 compatibility note

The frozen I9 guard still contains the legacy caller-controlled `material_discovery_pending` field. R4 does not mutate or retroactively rewrite that frozen implementation. The inherited regression remains green only to demonstrate that the successor work did not accidentally break unrelated frozen I9 behavior.

The R4 successor path derives material-discovery authority from R3 observation/surface state and the current revalidation snapshot. It does not accept `material_discovery_pending`.

## Scientific status

No WDPC scientific case was rerun.

Historical V24 I11 results remain unchanged and append-only. In particular WDPC-478 remains the historical RED against frozen I10; R4 construction does not retroactively convert it to PASS.

WDPC-469 and WDPC-495 remain blocked by I1 semantic qualification. WDPC-503 remains static/manual unresolved.

## Disposition

`R4_CONSTRUCTION = PASS`

`R4_RUNTIME_QUALIFICATION = NOT_CLAIMED`

`V24_I11_SUCCESSOR_SCIENTIFIC_EXECUTION = NOT_PERMITTED_YET`

Next implementation workstream under exact V6 approval: **R5 — independent normative-clause structural projection and governed semantic disposition**.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
