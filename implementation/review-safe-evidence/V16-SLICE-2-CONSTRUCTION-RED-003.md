# V16 Slice 2 Construction RED 003

## Status

`RED_PRESERVED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Exact failed attempt

- Workflow: `Review Safe Evidence V16 Slice 2 Independence V6`
- Run: `34994966606`
- Job: `104468794656`
- Candidate commit: `8a429781c3283fe03b130d2aec5ad4dc4867d7da`
- Candidate tree: `9a03767683141d4026e33abce7fa19b4dac27b6a`
- Intended endpoint: 77 mandatory Slice 2 adversarial tests under a principal unable to write the governed repository, followed by post-test worktree/blob re-attestation and strict manifest/source/execution reconciliation.

## Classification

`HARNESS_DEFECT_BEFORE_INTENDED_ENDPOINT`

The failure occurred before any intended Slice 2 behavioral assertion executed. All six unittest modules failed during test-module import with `ModuleNotFoundError`. The pre-test exact-blob checks, dependency installation, syntax compilation, clean-worktree check, and non-writer write probe had already passed.

The harness switched execution to `nobody` while retaining the repository checkout as the import location and invoking `python` through `sudo`. That does not establish that the unprivileged principal can traverse/read the hosted runner workspace using the same interpreter environment. The resulting import failure is therefore a harness/isolation setup defect, not evidence that the Slice 2 mechanism failed its intended behavioral endpoint.

## Narrow repair

- Materialize an exact read-only execution copy under a path traversable/readable by the unprivileged principal, outside the governed checkout.
- Root-own that copy and remove write permission for the test principal.
- Verify the execution copy against the governed source bytes before test launch.
- Invoke the exact configured Python interpreter by absolute path rather than relying on `sudo` PATH resolution.
- Continue to keep the original governed checkout non-writable and re-attest its clean state and exact blobs after execution.
- Preserve this RED regardless of any later green run.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
