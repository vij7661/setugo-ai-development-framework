# V16 Slice 2 Construction RED 008

## Classification

`HARNESS_ENVIRONMENT_DEFECT_BEFORE_INTENDED_ENDPOINT`

This record preserves a failed V16 Slice 2 construction run. It is historical evidence and MUST NOT be erased, replaced, or reclassified as a PASS by a later successful run.

## Bound candidate

- branch: `implementation/review-safe-evidence-v16-iar5-repair`
- candidate commit: `3954fcb071ce2ade0c1ae9a4156e0d6e515bd140`
- candidate tree: `f6221c9ba4fc33f050313738781a54f8acccb028`
- workflow: `Review Safe Evidence V16 Slice 2 Independence V7`
- workflow run: `34996615595`
- job: `104474343502`

## Observed result

V7 successfully reached the trusted-parent receipt mechanism and did not accept child console text as execution identity.

- exact governed blob pre-check: PASS
- immutable root-owned/read-only execution snapshot: PASS
- declared mandatory test IDs: 77
- AST-discovered test IDs: 77
- declared/source set equality: PASS
- workflow-owned strict single-test child runner: PASS
- forged-console execution-identity probe: PASS
- parent-controlled per-test receipt mechanism: ACTIVE
- child stdout/stderr authority: DIAGNOSTIC_ONLY
- successful parent receipts before final acceptance: 76/77

Exactly one invocation failed:

`seq=59`

`test_review_safe_evidence_v16_independence_iar3.Slice2IAR3Tests.test_current_baseline_manifest_is_semantic_revision_two_and_blob_bound`

The child returned `rc=70` because the test invokes `git hash-object` while the child process inherited the workflow checkout as its current working directory. The child principal is intentionally `nobody`, and that principal cannot stat/traverse the runner checkout path. Git therefore failed before the test could complete with:

`fatal: failed to stat '/home/runner/work/setugo-ai-development-framework/setugo-ai-development-framework': Permission denied`

The strict child runner then correctly converted the resulting unittest error into non-success rather than allowing a false green.

## Adjudication

This failure is a construction-harness/environment defect, not evidence of a Slice 2 candidate behavior defect. The source/test/manifest objects were not changed by the failing execution, and the failure arose because the harness launched the non-writer child from an inaccessible inherited current working directory rather than from the intentionally readable read-only snapshot.

The run did **not** reach the intended final evidence-acceptance endpoint. Therefore it is not a construction PASS and cannot be used to claim qualification.

The parent-controlled receipt design introduced for IAR6 remains directionally correct: it detected and preserved the actual child failure, while forged child console output could not manufacture a trusted parent receipt.

## Narrow successor repair

The next harness revision must preserve the exact candidate source/tests/manifests and change only the execution environment:

1. invoke each child with current working directory set to the root-owned read-only execution snapshot;
2. prove the non-writer child can read the snapshot and execute `git hash-object` there;
3. prove the non-writer child still cannot mutate the snapshot or access/use the repository checkout as an authority surface;
4. preserve parent-controlled per-exact-test receipts and diagnostic-only child stdout/stderr;
5. rerun all 77 mandatory exact test IDs and require exact receipt/source/manifest equality.

## Authority boundary

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
