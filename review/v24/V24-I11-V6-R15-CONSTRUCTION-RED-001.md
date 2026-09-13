# V24-I11-V6-R15 — Construction RED 001

Status: **PRESERVED RED / POLICY REJECTION OBSERVED BUT INTENDED ENDPOINT NOT PROVEN**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow run: `34775801974`
- review head: `30c1747bcc52c8ea2b4e674a6d0ff11d0b03e30c`
- candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- R15 native observer source blob: `127b91016fb50bda08be684fa54561f12aedc92f`
- compiled native observer SHA-256: `7c6817c5327f615535d3b2503bf1d665479849db3dff55a4a2f0e89b6ecf1f27`
- compiler digest: `40b27e8f730f40152b3155cc7d05aa5ebbf1ea74563d6cea8e980fac12ac43ee`

## What passed before RED

1. exact R15 candidate and external-authority separation;
2. R15 native observer compilation with bound CPython 3.12.14 home;
3. normal governed request through the R15 observer.

## RED endpoint

All seven path attacks returned non-zero and emitted no `R14_NATIVE_OBSERVATION=` frame, but the workflow deliberately required proof that the rejection occurred at the intended R15 normalized-path audit endpoint.

For all seven attacks stderr contained only:

- `R14_CHILD_CANDIDATE_IMPORT_FAILED`
- `R14_NATIVE_CHILD_NOT_CLEAN_EXIT`

The inherited R14 child wrapper collapses the underlying Python import/audit exception to a generic child failure before the R15 audit diagnostic becomes externally visible.

Therefore the run cannot distinguish:

- correct R15 normalized-path policy rejection; from
- another unrelated candidate import failure.

The skipped exact R14 replay and artifact-upload steps are not inferred PASS.

## Classification

`PROBE_OBSERVABILITY_DEFECT_BEFORE_INTENDED_ENDPOINT_PROOF`

This is not evidence that any of the seven forbidden path accesses were accepted. It is also not accepted as proof that they were rejected by the intended policy.

## Narrow repair

Keep the enforcement unchanged and emit a deterministic R15 diagnostic from the native audit hook at the exact moment a forbidden normalized path is rejected. Then rerun all seven attacks and require:

- non-zero native observer exit;
- no authenticated native observation;
- exact intended R15 path-policy diagnostic;
- successful normal governed request.

Scientific execution remains closed and runtime qualification is not claimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
