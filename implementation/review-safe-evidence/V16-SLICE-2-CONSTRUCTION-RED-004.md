# V16 Slice 2 Construction RED 004

## Status

`RED_PRESERVED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Exact failed attempt

- Workflow: `Review Safe Evidence V16 Slice 2 Independence V6`
- Run: `34995236745`
- Job: `104469700710`
- Candidate commit: `e953091550ac2423a3e8c0c04f04ae2f36aa7080`
- Candidate tree: `166c6a7adebee97aa93b35a0e967fbad4d2ccd3e`
- Intended endpoint was reached: all 77 mandatory tests were discovered and executed under the root-owned, non-writable execution snapshot using the exact configured Python interpreter.

## Classification

`FIXTURE_EXPECTATION_DRIFT`

75 tests passed and 2 failed. Both failures are stale expectations in the pre-IAR5 IAR4 test source after the current manifest system was deliberately expanded:

1. `test_same_predecessor_id_with_different_content_is_rejected` expected the legacy baseline error token `HISTORICAL_BASELINE_BLOB_MISMATCH`, while the generalized historical-binding validator emitted `BASELINE_HISTORICAL_BLOB_MISMATCH`.
2. `test_valid_current_manifest_set_passes_strictly_but_remains_nonauthoritative` expected the then-current manifest-set count `69`; the IAR5 source-bound IAR1/IAR2 successors plus the eight IAR5 tests make the governed current count `77`.

This is not a green result and it does not erase RED 003. The non-writer isolation repair did reach the intended test endpoint: the execution snapshot was readable but non-writable by `nobody`, the exact configured Python interpreter ran the suite, and all eight new IAR5 tests passed. The run stopped before post-test re-attestation because the two stale IAR4 expectations failed.

## Narrow repair

- Preserve the original IAR4 manifest and test source as historical evidence rather than silently rewriting their meaning.
- Introduce a source-bound semantic successor for IAR4 with a new module/manifest identity.
- Keep the legacy baseline predecessor error token stable in the public compatibility wrapper where feasible.
- Update only the successor IAR4 expectation for the enlarged current test count.
- Extend the strict current-manifest index and historical content bindings to include the exact superseded IAR4 manifest/test relationship.
- Re-run the full suite under the same non-writer execution isolation and continue to post-test worktree/blob re-attestation only if all tests pass.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
