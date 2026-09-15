# V15 Manual Evidence Review — Package/Test/RED Boundary 008

`SURFACE_REVIEWED = V15_EVIDENCE_PACKAGE_TEST_MANIFEST_RED_HISTORY_BOUNDARY`

`SURFACE_COVERAGE = COMPLETE`

`V15_EXISTING_CRITICAL = CONFIRMED`

## New Critical findings

1. **Review universe derived only from changed files.** `build_independent_evidence_package.py::main()` defines the candidate review universe as `git diff --name-only BASE CANDIDATE` and requires exactly 30 paths. This can omit unchanged but load-bearing dependencies while still producing a deterministic byte-correct package. Repair: derive and bind a complete load-bearing universe, not merely changed paths.

2. **Mandatory adversarial execution is inferred from aggregate test count and log markers.** The builder checks `Ran 199 tests`, `33/33` and hard-coded run IDs rather than a stable mandatory-test manifest. Missing/skipped/renamed mandatory cases can therefore be invisible. Repair: stable mandatory test IDs plus machine-readable execution proof; fail on missing/skipped IDs.

3. **RED-history completeness is not derived.** `RUNS`, `RAW_LOG_RUNS`, freeze metadata and copied RED records enumerate known failures manually. Other relevant failures could be omitted. Repair: discover the relevant workflow/run lineage and bind every RED/failure/correction record and raw evidence.

4. **Construction runs are accepted by conclusion without full run identity binding.** The builder checks only `run_obj.conclusion` against the expected value. `head_sha` is recorded but not validated against the intended per-run commit/workflow/test source. Repair: bind each run to its expected commit/tree, workflow identity/digest, event/ref, job identity and test-source digest.

5. **Package-generation inputs are mutable after candidate freeze.** Review instructions, freeze record, builder, workflow and RED record are copied from the current review branch. A new package can therefore be built for the same candidate with different review-side inputs. Repair: separately freeze/version/package-generation inputs and bind their exact digests/generation.

## New High findings

1. GitHub Actions metadata/logs are fetched under the same repository/account token and do not provide an independent authenticity root. Keep package integrity distinct from authority; use independently verifiable attestations/transparency evidence when authority is needed.
2. V2 package workflow path filters cover only the builder and workflow, so changes to other package inputs do not force a rebuild. Include all package inputs or fail on digest drift.
3. `V15-INDEPENDENT-EVIDENCE-PACKAGE-BINDING.json` is not itself recomputed/verified by the builder. Bind artifact/manifest/run/count identities through a separate externally verifiable binding record; avoid self-referential packaging.
4. Package-generation action tags/runner image remain mutable (`actions/checkout@v4`, `actions/setup-python@v5`, `ubuntu-latest`). Pin immutable identities for reproducible package evidence.
5. `automated_external_reviewer_api_calls=False` is asserted rather than machine-proven. If this claim becomes load-bearing, enforce network isolation/allowlisting and audit process/network activity.
6. The review package omits some review-side evidence such as the raw package-builder RED log. The external binding record cannot simply be embedded self-referentially, but all non-self-referential review-relevant package-generation evidence must be included or separately bound.

## Medium / Low

- Exact changed-file count is brittle; assert a path/digest universe rather than count only.
- Review instructions equate `expected changed candidate files: 30` with scope; distinguish changed files from complete load-bearing universe.
- Manifest payload is computed before manifest creation; document and bind manifest self-exclusion explicitly.
- Construction run lineage is hard-coded rather than independently derived.
- No workflow concurrency/current-package guard exists.

## Review disposition

- `CANDIDATE_FILE_UNIVERSE_COMPLETE = NO`
- `MANDATORY_TEST_EXECUTION_PROVEN = NO`
- `RED_HISTORY_COMPLETENESS_PROVEN = NO`
- `PACKAGE_CONTENT_INTEGRITY_PROVEN = PARTIAL`
- `PACKAGE_AUTHENTICITY_AUTHORITY_PROVEN = NO`
- `SUCCESSOR_SCOPE_FREEZE_RECOMMENDATION = DO_NOT_FREEZE`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
