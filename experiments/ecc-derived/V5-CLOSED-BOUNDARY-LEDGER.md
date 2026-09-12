# ECC-Derived V5 Closed Candidate-Boundary Ledger

Status: `V5_PRE_REPAIR_RED_PRESERVED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, or granted authority by this ledger.

## Parent evidence

- V4 frozen candidate: `8cc79ed23e825f6971e6268b9524e9ed91138028`
- V4 AI re-review disposition: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- V4 freeze recommendation: `DO_NOT_FREEZE_V4_EXPERIMENT_EVIDENCE`
- AI re-review manual threshold contribution: `0`
- EXP-ECC-1..5: `NARROWING_STILL_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`

## V5 hypothesis

V5 tests whether the caller-selectable strict-mode bypass can be structurally closed at the reference-mechanism layer without pretending that live platform attestations already exist.

The V5 target requires:

1. public `ecc_governance.py` is historical-only and exposes no `requirement_candidate` mode;
2. strict candidate semantics live in a separate internal module;
3. `ecc_candidate_boundary.py` is the only public route to candidate-eligible reference evidence;
4. eligibility requires an explicit boundary-set marker, a candidate kind, and a favorable status allowlist;
5. EXP-ECC-1..5 favorable candidate results require a separate reference-evidence source rather than merely rechecking the same caller fixture;
6. imported module identities and selected in-memory function code are bound by runtime policy verification;
7. runtime policy is rechecked immediately before candidate eligibility is issued;
8. EXP-ECC-6/7 remain deferred and cannot become candidate-eligible through the reference mechanism.

This remains a reference-mechanism experiment. A repository-bound reference evidence registry is not a substitute for live signed platform evidence and does not satisfy the later live-integration evidence boundary.

## Frozen assertions

- V5 assertion commit: `dbbfbdb6771fc4a57fc73665fa73bc2cebac4270`
- V5 supersession-aware runner commit: `8ba2ebc66e6d3449de5dbafdd99de6fa5a1736a7`
- V5 workflow-enabled pre-repair SHA: `2c839baad99f220cbe1537820a835be3e7720e28`

The V5 assertion file must remain unchanged during mechanism repair unless a test defect is separately preserved and adjudicated.

## RED-001

- exact candidate: `2c839baad99f220cbe1537820a835be3e7720e28`
- workflow run: `34692576280`
- job: `103550334507`
- result: `144 tests; 33 failures; 0 errors`
- V1/V2 active prior suites: `PASS`
- classification: `EXPECTED_PRE_REPAIR_RED`

Primary RED classes: direct public strict access, alias/partial/wrapper bypass, bare strict-class eligibility, missing private strict core, missing separate reference evidence source, same-fixture false independence, absent boundary eligibility marker, imported-module identity weakness, in-memory monkeypatch weakness, and missing final policy recheck.

## Historical test supersession

V3 and V4 test modules remain immutable historical evidence. V5 does not rewrite or delete them. They are excluded from the active V5 runner because the external V4 re-review invalidated specific semantics they encoded:

- V3 required a caller-selectable strict shared-core mode; V5 specifically tests removal of that mode.
- V4 treated a bare strict class as candidate-eligible and used same-fixture cross-checks; the V4 re-review identified both as false-green paths.

Supersession changes active semantics only. It does not erase prior RED/GREEN history.

## Current disposition

`V5_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
