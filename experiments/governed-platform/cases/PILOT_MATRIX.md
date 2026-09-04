# EXP-A/B/C Pilot Corpus Matrix

Status: **CONTROLLED PILOT — EXPANSION IN PROGRESS**

The pilot corpus is intentionally small first. It exists to test the harness and estimate effect sizes, not to claim general model rankings.

| Case | Experiment | Controlled challenge | Risk | Expected evidence role |
|---|---|---|---|---|
| EXP-A-001 | A | concurrent acceptance / double-success race | HIGH | compare marginal reviewer/tool detection |
| EXP-B-001 | B | inclusive/exclusive boundary false-green | MEDIUM | compare contract-only vs intent/invariant arms |
| EXP-B-002 | B | role omitted from authorization check / over-permission | HIGH | semantic over-permission detection |
| EXP-B-003 | B | omitted settlement condition | HIGH | omitted-condition detection |
| EXP-C-001 | C | mutated persistent fixture reused as prior lifecycle state | HIGH | fixture-data diagnosis + authority |
| EXP-C-002 | C | incorrect test expectation against explicit rounding contract | MEDIUM | test-defect diagnosis + authority |
| EXP-C-003 | C | conflicting refund statements | HIGH | REQUIREMENT UNRESOLVED / no corrective authority |

## Before Pilot #1 is considered runnable

- protected ground truth exists for every case outside model-visible repository content;
- blinded adjudication instructions are frozen/versioned;
- at least one deterministic verification mechanism is defined where applicable;
- at least two independently configured reasoning mechanisms are available for EXP-A/B where resource policy permits;
- runtime identities and cost/latency capture are enabled;
- exact-head harness CI is green.

## Coverage still to add before a larger evaluation

- clean/no-defect controls;
- CODE DEFECT case for EXP-C;
- ENVIRONMENT-TOOLING DEFECT case for EXP-C;
- mixed primary + contributing cause;
- semantic under-permission;
- terminology/vocabulary shift;
- hidden test-input selection false-green;
- cases from domains other than marketplace/business workflows.

These are expansion requirements, not permission to invent results or thresholds.
