# ECC-Derived V4 Mandatory Candidate-Boundary Ledger

## Status

- Program state: `V4_REFERENCE_MECHANISM_GREEN_PENDING_EXTERNAL_ENGINEERING_REVIEW`
- Authority effect: `NONE_EVIDENCE_ONLY`
- Manual-review threshold contribution: `0`
- Requirement adoption: `NONE`
- Production integration: `NOT_CLAIMED`
- Governed impact adjudication: `NOT_YET_PERFORMED`
- V18 baseline remains unchanged: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Parent review

V4 was opened from the exact reviewed V3 candidate:

`351f08c7f5236f73bec37f62ec53085af48d15c7`

The preserved V3 external AI engineering review returned:

- `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- EXP-ECC-1 through EXP-ECC-5: `NARROWING_STILL_REQUIRED`
- EXP-ECC-6 and EXP-ECC-7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- `DO_NOT_FREEZE_V3_EXPERIMENT_EVIDENCE`
- `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

Primary V3 finding addressed by V4: strict evaluation existed only when a caller voluntarily supplied `requirement_candidate=True`; the legacy path remained caller-selectable and the V3 trust manifest was not runtime-enforced. A shared implementation could also correlate false greens across experiments.

## V4 frozen falsification assertions

The V4 assertions were frozen before repair at:

`08a3ab7c4809722d6e149895e3d79c34554be93d`

The frozen V4 file is:

`experiments/ecc_derived/test_ecc_governance_v4_mandatory_boundary.py`

V4 adds 18 executable assertions to the prior 153-test suite. The assertions require:

1. all seven legacy evaluation paths to emit `evaluation_class = HISTORICAL_REFERENCE`;
2. seven strict-only candidate entrypoints with no caller-selectable `requirement_candidate` parameter;
3. candidate-result eligibility to reject historical and unclassified outputs;
4. runtime verification of the exact trust-boundary manifest;
5. positive strict candidate controls so the boundary is not block-all; and
6. independent favorable-result cross-checks for EXP-ECC-1 through EXP-ECC-5 so one shared-core false green cannot itself satisfy candidate eligibility.

The V4 assertion file was not modified during the repair sequence.

## Preserved RED history

### V4 RED-001 — mandatory boundary absent

- Exact candidate: `2c6664c591605d23172d410442eae9964eea9d54`
- Workflow run: `34691517124`
- Job: `103547476519`
- Result: `171 tests; 18 failures; 0 errors`
- Prior 153-test suite: `PASS`
- Evidence: `experiments/ecc-derived/evidence/V4-MANDATORY-BOUNDARY-RED-001.json`

Observed failure classes:

- legacy results were not explicitly historical;
- mandatory candidate boundary was absent;
- candidate class gate was absent;
- runtime trust-manifest enforcement was absent; and
- independent cross-checks for EXP-ECC-1 through EXP-ECC-5 were absent.

### V4 RED-002 — strict boundary added, trust binding intentionally still absent

Stage A added `experiments/ecc_derived/ecc_candidate_boundary.py` at:

`0fbc855486e36f13543b9a8eba993fc7bff6b522`

That module introduced strict-only candidate entrypoints, candidate-class eligibility, runtime-policy verification hooks, positive candidate paths, and independent cross-check logic for EXP-ECC-1 through EXP-ECC-5.

- Workflow run: `34691697986`
- Job: `103547967933`
- Result: `171 tests; 14 failures; 0 errors`
- Prior 153-test suite: `PASS`
- Evidence: `experiments/ecc-derived/evidence/V4-MANDATORY-BOUNDARY-RED-002.json`

The strict-only entrypoint and class-gate tests passed. Remaining failures were deliberately isolated to:

- legacy results still lacking `HISTORICAL_REFERENCE`;
- V4 runtime trust manifest not yet bound; and
- independent cross-check execution blocked by the unbound runtime policy.

## Stage B deterministic repair

Stage B was applied by a deterministic repo-local repair workflow. The repair input was:

`46c0e7a5b8455dc460004dd5e29e7caaad4a00eb`

Repair workflow:

- run: `34691762267`
- job: `103548139153`

The repair-generated mechanism commit was:

`40bf5f64971e8e4587d846f69aa86ccc734b6b8b`

Only these mechanism/trust files were changed by the repair commit:

- `experiments/ecc_derived/ecc_governance.py`
- `experiments/ecc_derived/ecc_governance_trust_manifest.json`

The repair produced:

- core SHA-256: `298d36a2e5d513fd1c17624fa0dee0e9b14c6804afbf35845185403eea5c59ae`
- core Git blob: `16689d1e916bf31ba070499e0412e05b37ad8e05`
- candidate-boundary SHA-256: `1453c063d180cb0e897b678b871cfaa185c597159dac190456aa0a66617f82f8`
- candidate-boundary Git blob: `a84ee40f9c143d6d25d92edf1509727f6efc8d21`

The runtime trust manifest now binds both modules and declares:

- `legacy_path_policy = HISTORICAL_REFERENCE_ONLY`
- `historical_result_class = HISTORICAL_REFERENCE`
- `candidate_path_policy = MANDATORY_STRICT_EVALUATION`
- `candidate_boundary_policy = STRICT_ONLY_NO_CALLER_MODE_SWITCH`
- independent cross-check coverage for EXP-ECC-1 through EXP-ECC-5.

Because GitHub does not recursively trigger another workflow from a `GITHUB_TOKEN` workflow push, an evidence-only commit was added on top of the repair-generated commit to trigger normal falsification. No mechanism or frozen test changed in that trigger commit.

## V4 GREEN-003

Exact tested candidate:

`ae01a6d96d5b385e9747b43e00fc9b085f7552de`

- Workflow run: `34691848982`
- Job: `103548379655`
- Result: `171/171 PASS`
- Prior 153-test suite: `PASS`
- V4 assertions: `18/18 PASS`
- Evidence: `experiments/ecc-derived/evidence/V4-MANDATORY-BOUNDARY-GREEN-003.json`

The green run demonstrates, at the bounded reference-mechanism level, that:

- legacy compatibility outputs are explicitly historical;
- the new candidate API has no caller-selectable mode flag;
- historical or unclassified results are ineligible as candidate evidence;
- the candidate boundary fails closed when its exact runtime trust policy is invalid;
- EXP-ECC-1 through EXP-ECC-5 favorable shared-core results are independently revalidated; and
- valid strict positive controls still succeed.

## Bounded per-experiment disposition pending external re-review

### EXP-ECC-1

`MANDATORY_BOUNDARY_REFERENCE_PASS_PENDING_REVIEW`

Supported only as a reference-mechanism claim: a new candidate entering the V4 candidate boundary cannot voluntarily select the historical execution-attestation path, and a forged favorable shared-core result is independently cross-checked.

Not proven: live platform enforcement-point attestation, live process identity, production execution interception, or end-to-end TOCTOU resistance.

### EXP-ECC-2

`MANDATORY_BOUNDARY_REFERENCE_PASS_PENDING_REVIEW`

Supported only as a reference-mechanism claim: strict machine/runtime evidence requirements cannot be bypassed by choosing legacy candidate mode through the V4 candidate API, and favorable shared-core equivalence is independently cross-checked.

Not proven: live executable extraction, complete production path discovery, or independently sourced runtime evidence.

### EXP-ECC-3

`MANDATORY_BOUNDARY_REFERENCE_PASS_PENDING_REVIEW`

Supported only as a reference-mechanism claim: strict harness-envelope evaluation is mandatory through the V4 candidate API, remains provider-neutral, and favorable shared-core qualification is independently cross-checked.

Not proven: live platform harness-registry attestation or independent runtime identity qualification. Current attestation fields remain fixture/reference inputs.

### EXP-ECC-4

`MANDATORY_BOUNDARY_REFERENCE_PASS_PENDING_REVIEW`

Supported only as a reference-mechanism claim: strict authority/project/sequence checks are mandatory through the V4 candidate API and favorable shared-core activation is independently cross-checked.

Not proven: platform-issued authenticated approval objects, live revocation propagation, or production TOCTOU semantics.

### EXP-ECC-5

`MANDATORY_BOUNDARY_REFERENCE_PASS_PENDING_REVIEW`

Supported only as a reference-mechanism claim: strict configuration attestation/equality checks are mandatory through the V4 candidate API and favorable shared-core configuration results are independently cross-checked.

Not proven: live cryptographic configuration attestation, production DNS/rebinding resistance, or authoritative unreadable-config handling.

### EXP-ECC-6

`DEFER_PENDING_INTEGRATION_EVIDENCE`

V4 ensures the legacy result is explicitly historical and provides a strict-only candidate entrypoint, but it does not establish real provider/gateway identity, authenticated manual-review evidence, or qualifying manual-review transport. AI review evidence remains zero-credit.

### EXP-ECC-7

`DEFER_PENDING_INTEGRATION_EVIDENCE`

V4 ensures the legacy result is explicitly historical and provides a strict-only candidate entrypoint, but it does not establish integration with the actual governed claim/dependency/retraction pipeline or a live promotion boundary.

## Remaining epistemic limits

V4 does not retroactively change the fact that the original V1 86-case broad coverage harness was added after the initial mechanism existed. V4's strongest evidence is therefore the preregistered V4 boundary-hardening sequence and its preserved RED → partial RED → GREEN progression, not a claim that every original EXP-ECC hypothesis was prospectively falsified from inception.

The V4 independent cross-checks reduce one shared-core correlation path for favorable EXP-ECC-1 through EXP-ECC-5 results, but they are still code in the same repository/process and are not equivalent to live independent platform evidence or a separately administered trust root.

## Next permitted transition

The V4 reference mechanism may be submitted for a targeted external engineering re-review of the exact ledger-head candidate after the ledger-head test passes.

That review may recommend whether EXP-ECC-1 through EXP-ECC-5 are sufficiently narrowed to enter a separate bounded governed impact-adjudication step. It cannot itself adopt, promote, release, merge, or grant authority to any requirement.

EXP-ECC-6 and EXP-ECC-7 remain deferred pending integration/live evidence.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
