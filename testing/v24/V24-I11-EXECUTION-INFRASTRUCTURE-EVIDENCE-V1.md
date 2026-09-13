# V24 I11 Execution Infrastructure Evidence V1

This artifact records GitHub Actions execution-state evidence only. It is **not** a WDPC scientific result and does not alter any case adjudication.

## Exact scientific frontier

- Pre-scientific frontier: `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`
- Frontier tree: `f9de48189b7d304f50f169277dc1b4dceb642546`
- Frozen design: `db9e4b349fd26e128f4486878a4af64929000a7c`
- Frozen I10 subject: `9836dc3ff233cca582f485434fc1c6494cf7eb05`

## Observed Actions states

### Cluster A — scientific execution succeeded

- Branch: `testing/v24-i11-scientific-cluster-a-v1`
- Execution SHA: `86f85ac17ea88e7cb95d7271e5e9cea6d3bc84c4`
- Run: `34748563045`
- Job reached runner and completed successfully.
- Scientific result is separately preserved/adjudicated; WDPC-454 is RED.

### Cluster B — first attempt never reached a runner

- Branch: `testing/v24-i11-scientific-cluster-b-v1`
- SHA: `da62eb8a49d5afbd18e0ea87c59e1ad16d9ac79e`
- Run: `34748667569`
- Terminal Actions conclusion: `startup_failure`
- Jobs observed: `0`
- Scientific interpretation: **NO CASE EXECUTED / NO SCIENTIFIC RESULT**.

### Cluster B — clean retry queued with zero jobs

- SHA: `72bb198933cc2aca3c4b719daccf6d3040b84b3f`
- Run: `34748809624`
- State when recorded: `queued`
- Jobs observed: `0`
- Scientific interpretation: **NOT EXECUTED**.

### Clusters C-H reference sweep queued with zero jobs

- Branch: `testing/v24-i11-scientific-reference-sweep-c-h-v1`
- SHA: `25e576e2f54ee1af18e33d3d880e73d03bbd97be`
- Run: `34748771053`
- State when recorded: `queued`
- Jobs observed: `0`
- Scientific interpretation: **NOT EXECUTED**.

### Historical accidental non-scientific harness commit run

- Accidental commit: `3671d085c80435841426972cb66b0f024a829a75`
- Run: `34748501222`
- Display title: `noop`
- State when recorded: `queued`
- Jobs observed: `0`
- This commit is not a scientific subject and was excluded from Cluster A execution. Its queued state is preserved only as infrastructure evidence.

## Interpretation boundary

Cluster A reached a hosted runner while the older `noop` run was already queued. Therefore the stale `noop` run alone is not sufficient evidence that it caused later queueing/startup failure.

No queued/startup-failure state may be normalized into `PASS`, `FAIL_CODE_DEFECT`, `FAIL_HARNESS_DEFECT`, `FAIL_FIXTURE_DEFECT`, or `INSUFFICIENT_EVIDENCE` for a WDPC case. A case receives a scientific result only after its exact-bound harness actually runs and produces the required observation/evidence record.

No reviewer API calls were used.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
