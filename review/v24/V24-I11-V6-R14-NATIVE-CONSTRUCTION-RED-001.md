# V24-I11-V6-R14 — Native Boundary Construction RED 001

Status: **PRESERVED RED / FAIL-CLOSED NORMAL-CANDIDATE IMPORT DEFECT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow run: `34775029524`
- workflow head: `5d7a012aa04a0a02a2b2e5d589dce0940adac922`
- workflow tree: `350d03191c029cae9835ca642fb0df835dc84270`
- frozen candidate commit: `5a1fb005e9c58e30b1dcfaa473d603dde90df72c`
- frozen candidate tree: `6e65609ac09b78bcffefb6d6560b640ba7696521`
- external pinset admitted files: `189`
- external pinset SHA-256: `669b2387738cf53a15d67aad149f93a7fee726368ace3fa7824cd3a53057c42d`
- native observer source Git blob: `59916850a7b81b0d2ba77ce51198536277615555`
- native observer binary SHA-256: `5544064d341aadf64a38cad4f247672cb1e54b70afaaf55343ecd87fbdb029f6`
- compiler digest: `08139dce56febfadfc5427dab9308145c5242084b0cceb48a70dee7d80a77a46`
- interpreter contract digest: `eed7733f7032dd1f588cd048469130e52487335d2a7f32d2016cbc1d883d206b`
- environment digest: `dd97f2e02ad71401856218cd40b5268a4410afd2256c821865cc81035b503d7d`

## Completed before failure

The following gates passed before the RED endpoint:

1. exact frozen candidate identity and candidate/review-authority separation;
2. native observer compilation and binary/compiler binding;
3. external 189-file pinset generation;
4. exact source verification and sandbox staging;
5. exact pre-execution sandbox verification;
6. production-byte substitution rejected;
7. support-object substitution rejected;
8. added unpinned file rejected;
9. symlink substitution rejected;
10. actual isolated interpreter/environment digest construction;
11. all seven native-boundary attack probes rejected without an authenticated observation:
   - historical R13 `sys._getframe()` path;
   - direct `os._exit(0)`;
   - file-descriptor junk/frame injection;
   - `ctypes` memory escape;
   - `/proc/self/mem` access;
   - `sys.settrace` mutation;
   - thread escape;
12. launcher without required isolation rejected;
13. optimized (`-O`) launcher rejected.

The seven-attack result object had `all_rejected = true` and SHA-256:

`2adf483fda9c6c1a96d44fd9e145dcbf8d61f3623d15d3e5d0ecd4a4c51da7a9`

These are bounded construction/falsification observations only. They do not qualify R14.

## Failure endpoint

Step: `Execute six external oracle checks through native observations`.

The first unmodified candidate request failed before a native observation was emitted:

- native observer return code: `2`
- child diagnostic: `R14_CHILD_CANDIDATE_IMPORT_FAILED`
- parent diagnostic: `R14_NATIVE_CHILD_NOT_CLEAN_EXIT`

The workflow therefore stopped before:

- six-check oracle evidence completion;
- candidate structural validation of the external evidence;
- native-binary substitution evidence test;
- post-execution exact sandbox verification;
- construction record creation;
- artifact upload.

None of those skipped endpoints may be inferred PASS.

## Classification

`FAIL_CLOSED_NORMAL_CANDIDATE_IMPORT_DEFECT`

The run does **not** demonstrate a false-green path: the native parent emitted no authenticated observation for the failing normal candidate. The defect is that the R14 child execution policy or embedded-interpreter path is too restrictive or otherwise incompatible with the frozen candidate's legitimate import path.

The exact underlying Python exception was not printed by this revision of the native observer, so the narrower cause is not yet adjudicated. The next step is diagnostic-only: expose the underlying child import exception without weakening any audit restriction or accepting any result.

## Posture

- R14 remains under construction.
- scientific execution remains `CLOSED_PENDING_SUCCESSOR_REVIEW`.
- runtime qualification remains `NOT_CLAIMED`.
- no automated external reviewer/provider API was called.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
