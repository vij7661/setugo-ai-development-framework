# V15 Package/Test/RED Boundary Review — Adjudication 008

Status: **ACCEPTED WITH NARROW CLASSIFICATION CORRECTIONS / V15 IMPLEMENTATION REMAINS REJECTED / SUCCESSOR SCOPE NOT YET FROZEN**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Accepted findings

The supplemental DeepSeek review correctly identifies three still-unclosed stopping-rule families: complete load-bearing review-universe derivation, stable mandatory-test execution proof, and complete RED/failure-history derivation. It also identifies real package-generation and run-binding weaknesses.

## Adjudication corrections

### A. Changed-file universe finding — accepted, but examples require exact-candidate correction

The package builder does define the review universe by `git diff --name-only BASE CANDIDATE` and exactly 30 paths. That is not, by itself, proof of the complete load-bearing dependency universe.

However, several examples in the external review are not omitted for this exact candidate: the core `review_safe_evidence_v15.py`, the V15 schema registry, the V15 standard, all nine V15 construction workflows, runtime slice modules, and their tests are among the 30 changed candidate files. The Critical is therefore accepted as a **universe-derivation proof gap**, not as proof that those specific named files were absent.

Before successor-scope freeze, the repository must explicitly derive all unchanged/runtime/environment/repository dependencies and prove inclusion or justified exclusion.

### B. Mandatory-test-manifest finding — accepted Critical

`Ran 199 tests` is aggregate evidence, not proof that every contract-mandated adversarial case executed. A stable manifest is required with exact IDs, test source identity, execution result and no-skip/no-rename closure.

### C. RED-history completeness — accepted Critical as a stopping-rule proof gap

The existing candidate RED and package-builder RED are preserved, but the mechanism enumerates known runs/records manually. There is no complete derivation proving that no relevant RED/failure run is omitted. Later green evidence therefore cannot satisfy the preservation stopping rule until a failure-history universe is independently derived.

### D. Construction-run identity — accepted Critical with repair corrected

The builder checks conclusions but does not validate each run against its exact expected commit/tree/workflow/test-source identity. Earlier construction runs intentionally correspond to earlier slice commits, so the repair must **not** require every run to have `head_sha ==` the final frozen candidate. Instead, each run must bind to an explicit expected per-run commit/tree, workflow path+digest, test source digest, event/ref, job identity and ordered construction lineage. The final accumulated run must bind to the final frozen candidate.

### E. Package-generation mutability — accepted Critical

Candidate freeze and package-generation freeze are distinct. Review-side instructions/builder/workflow/freeze metadata/RED inputs require an independently versioned package-generation generation so a later package for the same candidate cannot silently change its review contract.

## High findings adjudication

- Same-account GitHub metadata/log authenticity: accepted as a residual/authenticity limitation; largely part of the already-confirmed root-of-trust family and must not be double-counted as a new independent root defect.
- Package workflow path filters: accepted.
- Binding JSON: accepted in substance, but the binding record should remain external to the inner ZIP if embedding it would create self-reference. It must instead be independently recomputable and cryptographically/externally bound to the artifact.
- Mutable actions/runner/toolchain: accepted.
- `automated_external_reviewer_api_calls=False`: accepted as a non-load-bearing assertion today; if promoted into a qualification condition it requires enforceable network/process evidence.
- Missing raw package-builder RED evidence: accepted. Include/bind all non-self-referential package-generation failure evidence.

## Required closure before V16 scope freeze

Create and independently review three review-side closure artifacts without modifying the frozen V15 candidate:

1. `V15-LOAD-BEARING-REVIEW-UNIVERSE` — exact candidate/runtime/workflow/schema/standard/environment/repository/package dependencies with source of derivation and inclusion/exclusion rationale.
2. `V15-MANDATORY-ADVERSARIAL-TEST-MANIFEST` — contract requirement -> stable test ID -> test source digest -> run/job/result mapping; fail on missing/skipped/renamed cases.
3. `V15-RED-FAILURE-HISTORY-UNIVERSE` — derived relevant workflow/run history, every failure/RED, correction lineage, raw evidence and explicit classification.

These artifacts are evidence-side closure work only. They do not repair V15 and cannot grant implementation/runtime/scientific authority.

## State

- `V15_IMPLEMENTATION_ACCEPTANCE = REJECTED`
- `V15_SUCCESSOR_REQUIRED = true`
- `V15_SUCCESSOR_SCOPE_FROZEN = false`
- `V15_REVIEW_UNIVERSE_CLOSURE_REQUIRED = true`
- `V15_MANDATORY_TEST_MANIFEST_REQUIRED = true`
- `V15_RED_HISTORY_UNIVERSE_REQUIRED = true`
- `IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`
- `RUNTIME_QUALIFICATION = NOT_CLAIMED`
- `SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
