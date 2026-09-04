# EXP-C — Corrective Authority

Status: **PRE-REGISTERED PILOT — NOT YET RUN**

## Hypothesis

Evidence-verified differential diagnosis plus artifact-scoped corrective authority will reduce wrong-artifact modification and false-green repair compared with an unguided `fix this failure` workflow.

## Operational cause classes

- CODE DEFECT
- FIXTURE-DATA DEFECT
- TEST DEFECT
- ENVIRONMENT-TOOLING DEFECT
- REQUIREMENT UNRESOLVED

Cases may contain primary and contributing causes. `UNCERTAIN` is a decision state and grants no corrective authority.

## Arms

A. **Control:** `Fix this failing test/build/workflow.`

B. **Diagnosis gate:** classify the failure before correction; authority is routed by diagnosed class.

C. **Differential evidence + scoped authority:** taxonomy coverage, candidate hypotheses, alternative-hypothesis challenge, supporting/contradictory evidence, requirement-source check where applicable, then scope-limited correction and regression.

## Primary outcome

Wrong-artifact modification rate.

## Secondary outcomes

- Root-cause / cause-class accuracy.
- False-green rate.
- Test weakening.
- Silent requirement mutation.
- Fixture mutation used to hide a product defect.
- Successful correction rate.
- Mixed-cause detection.
- `UNCERTAIN` used appropriately.
- Cost, latency and tool/model usage.

## Authority invariants

- CODE DEFECT does not authorize weakening requirements/tests/fixtures.
- TEST DEFECT authorizes only the affected verification artifact unless a separately established cause grants additional scope.
- FIXTURE-DATA DEFECT authorizes controlled test-data/fixture scope, not product behavior changes.
- ENVIRONMENT-TOOLING DEFECT authorizes environment/config/tooling scope appropriate to evidence.
- REQUIREMENT UNRESOLVED grants no corrective implementation authority until the contract is resolved.

## Pilot discipline

Use deliberately broken cases with hidden/local ground truth. Include ambiguous and mixed-cause cases. Do not choose a fixed sample-size or success threshold until pilot effect sizes and error distributions are observed.
