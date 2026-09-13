# V24-I11-V6-R15 — Construction RED 002

Status: **PRESERVED RED / FULL-CONSTRUCTION WORKFLOW ARGUMENT MISMATCH BEFORE ORACLE ENDPOINT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow run: `34776044993`
- workflow head: `c866b4200cd33b1023fae9a15afb60b03dcbeaff`
- candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`

## Passed before RED

The run completed successfully through:

1. exact candidate / external authority separation;
2. R15 native observer compilation and identity binding;
3. 190-file external pinset generation, source verification, staging and sandbox equality;
4. production/support/unpinned/symlink substitution rejection;
5. interpreter/environment digest binding;
6. normal frozen candidate native request;
7. all historical R13 native-boundary attacks rejected;
8. all seven R15 path/memory attacks rejected at the exact R15 policy endpoint;
9. oracle-launcher no-isolation and optimized-interpreter probes rejected.

## Failure endpoint

The six external-oracle step invoked the inherited trusted oracle with CLI options that are not part of that oracle's contract:

- `--native-runtime-binding-source-git-blob-sha1`
- `--child-python-home`
- `--child-python-program`
- `--child-python-program-sha256`
- `--child-python-version`

The exact trusted oracle blob in this run was `9b9e2714ef9f71aefe99ceb62e8eac25319fdf10`. Its CLI intentionally accepts the native observer source/binary/compiler identities and oracle identity; the additional CPython-home bindings are construction-record/environment bindings, not oracle arguments.

`argparse` rejected the invocation before any oracle scenario executed. Therefore the six oracle checks, candidate evidence validation, binary-substitution check, post-execution sandbox check, construction record, and artifact upload remain unexecuted for this run and are not inferred PASS.

## Classification

`FULL_CONSTRUCTION_WORKFLOW_ARGUMENT_MISMATCH_BEFORE_ORACLE_ENDPOINT`

No production/candidate/R15 audit enforcement is changed by the repair. Rerun the full construction with only the unsupported oracle CLI arguments removed, while retaining those identities in the environment digest and final construction record.

Scientific execution remains closed. Runtime qualification remains not claimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
