# V16 Slice 1 — Construction Evidence 002

Status: **GREEN CONSTRUCTION EVIDENCE / NON-AUTHORITATIVE / RED HISTORY PRESERVED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Exact run binding

- workflow: `Review Safe Evidence V16 Slice 1 Trust Foundation`
- workflow run: `34978199943`
- run number: `5`
- job: `trust-foundation-construction`
- job id: `104411292295`
- branch: `implementation/review-safe-evidence-v16`
- candidate commit: `3ec1d2b4ba8e5b404d46a68fde2cadff753cb547`
- candidate tree: `adb6b996fb5bb3a69f2f8e10ca0c1bee53aa9f11`
- event: `push`
- conclusion: `success`

## Observed environment

- GitHub Actions runner version: `2.337.0`
- runner image: `ubuntu-24.04`
- image version: `20260907.300.1`
- OS: `Ubuntu 24.04.5 LTS`
- Git: `2.55.0`
- CPython: `3.12.14`
- `actions/checkout` exact SHA: `11d5960a326750d5838078e36cf38b85af677262`
- `actions/setup-python` exact SHA: `a26af69be951a213d495a4c3e4e4022e16d87065`
- `cryptography`: `46.0.4`
- observed transitive packages: `cffi 2.1.1`, `pycparser 3.0`

## Mandatory adversarial proof

Raw workflow output records:

- `Ran 38 tests in 0.015s`
- `OK`
- `V16_SLICE1_MANDATORY_TESTS_VERIFIED=38`
- `V16_SLICE1_SOURCE_MANIFEST_EXECUTION_SET_EQUALITY=PASS`

The workflow required exact equality among:

1. the 38 IDs in `REVIEW-SAFE-EVIDENCE-V16-SLICE1-MANDATORY-TESTS-002`;
2. the 38 test methods statically present in the Slice 1 test source;
3. the 38 test IDs observed as `... ok` in the raw unittest output.

No skipped or failed test was accepted.

## Repaired adversarial mechanisms covered

The 38-test set includes regressions for the first internal-adversarial review findings, including:

- duplicate bootstrap public-key rejection;
- root/trust-set/key/control-domain identity binding in bootstrap signatures;
- newly introduced registry-key backdating rejection;
- governance-generation identifier reuse rejection;
- stale-generation/current-registry rejection;
- current-generation/current-registry success;
- strict serialized-ingress duplicate-key rejection;
- canonical integer range restrictions.

## Preserved RED history

This green run does not erase the earlier construction failures preserved in `V16-SLICE-1-CONSTRUCTION-RED-001.md`:

- run `34977136315` — implementation/test-fixture API transition mismatch;
- run `34977289133` — 38 passing mechanism tests but stale 30-test manifest/workflow gate;
- run `34978155073` — 38 passing mechanism tests and 38-entry manifest but stale workflow hard-count.

## Construction boundary

The successful workflow emitted:

- `V16_SLICE1_AUTHENTICATED_TRUST_FOUNDATION=CONSTRUCTION_TESTS_PASS_NONAUTHORITATIVE`
- `V16_SLICE1_TRUST_ANCHOR_PROVISIONING=OUT_OF_BAND_NOT_PROVEN`
- `V16_SLICE1_DOWNSTREAM_MIGRATION=NOT_STARTED`
- `IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`
- `RUNTIME_QUALIFICATION=NOT_CLAIMED`
- `SCIENTIFIC_AUTHORITY=NOT_CLAIMED`
- `AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

This is construction evidence only. Internal adversarial review remains open and no downstream V16 slice may interpret this green run as independent review or qualification.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
