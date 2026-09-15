# V16 Slice 2 Construction RED 007

## Status

`RED_PRESERVED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Exact failed attempt

- Workflow: `Review Safe Evidence V16 Slice 2 Independence V6`
- Run: `34996050667`
- Job: `104472428668`
- Candidate commit: `ab52366bfadea960fd803128e74274624720cf67`
- Candidate tree: `dc0be78c89326470434a1c89a8ee58afd11ca8b4`

The intended behavioral tests and mutation-isolation checks were reached:

- exact governed pre-test blobs matched;
- the governed checkout was clean;
- the root-owned execution snapshot was readable but not writable by the test principal;
- all 77 current mandatory tests ran and unittest reported `OK`;
- the execution snapshot remained byte-equal to the governed source;
- the governed checkout remained clean;
- all governed post-test blobs still matched their exact expected values.

The run nevertheless failed before construction evidence acceptance because the final source/manifest/execution reconciliation derived executed test identities by applying a regular expression to merged human-formatted unittest stdout/stderr. The parser found 76 records although unittest had run 77 tests.

## Classification

`HARNESS_DEFECT_BEFORE_FINAL_EVIDENCE_ACCEPTANCE`

One successful test emitted a Git diagnostic between unittest's human-formatted test prefix and the final `ok` token:

`warning: unable to access '/home/runner/.config/git/attributes': Permission denied`

The affected test was `test_current_baseline_manifest_is_semantic_revision_two_and_blob_bound`. The warning split the normally single-line verbose unittest result, so the log regular expression did not recognize that successful execution. The behavioral suite itself remained 77/77 green, but the governed evidence endpoint correctly failed because the execution-receipt mechanism could not prove 77 exact executions from its chosen representation.

## Additional adversarial implication exposed by this RED

The human console log is candidate-controlled diagnostic output, not an authoritative execution receipt. A candidate test can emit strings shaped like other unittest success lines. Therefore merely making the regular expression tolerate this warning would leave a false-green class: source/manifest/execution equality could be influenced by test-produced text rather than by a trusted parent process's knowledge of which exact test it invoked and what exit status that invocation returned.

## Narrow repair

- Do not use parsed unittest stdout/stderr as the authoritative execution-identity source.
- Derive the exact expected test IDs independently from the exact current manifests/source set before child execution.
- Have a trusted parent harness invoke each exact test ID separately under the non-writer principal and record the invoked ID plus child return code itself.
- Treat child stdout/stderr only as diagnostics; hash and preserve it if useful, but never infer test identity or success from printed `... ok` lines.
- Require one successful parent receipt row for every expected test ID, no duplicates, no omissions, no extras, and no skipped/failed/error child invocation.
- Include an adversarial harness probe proving forged unittest-looking child output cannot create a receipt for a test ID that the parent did not invoke.
- Re-run pre/post snapshot and governed-byte attestation unchanged.

This RED remains preserved even if a later trusted-receipt harness is green.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
