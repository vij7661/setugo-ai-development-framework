# V24-I11-V6-R15 — Focused Path-Normalization Construction Evidence

Status: **FOCUSED CONSTRUCTION PASS / FULL SUCCESSOR CONSTRUCTION STILL REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Frozen candidate

- candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- predecessor R14 candidate: `5a1fb005e9c58e30b1dcfaa473d603dde90df72c`
- predecessor R14 tree: `6e65609ac09b78bcffefb6d6560b640ba7696521`
- predecessor R14 falsification run: `34775597496`
- predecessor R14 classification: `FAIL_CODE_DEFECT`

## Historical RED preserved

Run `34775801974` is preserved as `PROBE_OBSERVABILITY_DEFECT_BEFORE_INTENDED_ENDPOINT_PROOF`.

The R15 observer compiled and a normal request passed. All seven attacks returned non-zero and emitted no authenticated observation, but the inherited R14 child wrapper hid the underlying audit exception behind generic import failure. Because the run could not prove the rejection occurred at the intended R15 path-policy endpoint, it was not accepted as mechanism evidence. The enforcement requirement was not weakened.

See `V24-I11-V6-R15-CONSTRUCTION-RED-001.md`.

## Corrected focused construction PASS

- workflow run: `34775884988`
- workflow head: `25793d77fbc305a7eca786d6e8877fa73e0f6638`
- workflow: `V24 V6 R15 Path Normalization Construction`
- conclusion: `SUCCESS`
- R15 native observer source blob: `bfd16c1f3b7103b25c2f1abee536ebceb199e295`

The corrected observer emits a deterministic native diagnostic at the exact normalized-path rejection point while preserving fail-closed enforcement.

Passed endpoints:

1. exact R15 candidate and external-authority separation;
2. R15 native observer compilation using CPython 3.12.14;
3. normal governed request still succeeds;
4. all seven mandatory path/memory regressions reject at the exact R15 audit-policy endpoint;
5. no rejected attack emits an authenticated `R14_NATIVE_OBSERVATION=` payload;
6. exact R14 bytes-path `/proc/self/mem` false-green replay is rejected.

## Mandatory path/memory regressions

All seven returned non-zero, emitted no authenticated native observation, and exposed `R15_AUDIT_FORBIDDEN_NORMALIZED_PATH` from trusted native audit code:

- `PROC_SELF_MEM_UNICODE_PATH_REJECTED`
- `PROC_SELF_MEM_BYTES_PATH_REJECTED`
- `PROC_SELF_MAPS_BYTES_PATH_REJECTED`
- `OS_OPEN_PROC_SELF_MEM_BYTES_REJECTED`
- `IO_FILEIO_PROC_SELF_MEM_BYTES_REJECTED`
- `DEV_MEM_UNICODE_PATH_REJECTED`
- `DEV_MEM_BYTES_PATH_REJECTED`

## Artifact binding

- artifact ID: `10324150158`
- artifact name: `v24-v6-r15-path-normalization-construction-evidence`
- outer artifact SHA-256: `414278485fc973f6f3eab1dca1e67ecea292e1bd348fa4cecac20d22bb0a692f`
- downloaded outer bytes: `717`
- contained evidence object: `V24-I11-V6-R15-PATH-REGRESSION.json`
- contained evidence bytes: `2718`
- contained evidence SHA-256: `3960cd3319049b9583fbc6c75eac7d44cc769a582d46132dee87b253ad9a71ff`
- independent post-download outer digest recomputation: `VERIFIED`
- independent contained-object digest recomputation: `VERIFIED`

## Boundary

This evidence proves only the focused R15 representation-complete path controls tested above. It does **not** by itself establish the full R15 successor construction, external exact-file pinset, all R14/R13 native-boundary regressions, all six external oracle checks, manual successor-review readiness, scientific execution, or runtime qualification.

Next required construction step: rerun the full external exact-file/native-observer/external-oracle construction surface against the exact R15 candidate and bind this focused regression evidence into that construction record.

- scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- runtime qualification: `NOT_CLAIMED`
- automated external reviewer/provider calls: `PROHIBITED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
