# SLICE3-SLICE4-RECEIPT-COMPATIBILITY-001

## Discovery
The new real Slice1→Slice5 composition test on candidate `c5829e6f5c9306d6a381c5c400013cccff99b375` failed after accepted Slice1-4 regressions passed. The failure showed that the real Slice3 `RepositoryMutationGateway` result omits `project_id`, `task_id`, `execution_id`, and `plan_step_id`, while Slice4 `ToolRunnerGateway._verify_slice3` requires those fields. Existing Slice4 tests used a synthetic Slice3 receipt and therefore did not expose this interface mismatch.

## Classification
`CROSS_SLICE_RECEIPT_INTERFACE_DEFECT / PRIOR_FALSE_GREEN_COVERAGE_GAP`.

## Frozen narrow repair
- Do not change Slice4 acceptance requirements.
- Extend successful Slice3 result/evidence only with lineage already deterministically verified by Slice3:
  - `project_id` from verified Slice2 capability lineage;
  - `task_id` from verified Slice2 capability lineage;
  - `execution_id` from verified Slice2 effect identity;
  - `plan_step_id` from the validated Slice3 effect contract.
- Do not mint any new authority; terminal/release authority remain false.
- Preserve existing Slice3 idempotency/durable row semantics and all prior tests.
- The real S1→S5 composition test must consume the actual Slice3 receipt without synthesizing the missing fields.
- Rerun Slice1-5 regressions plus the new composition test on the repaired exact SHA.
- Fresh R2/R3 required after repair.
