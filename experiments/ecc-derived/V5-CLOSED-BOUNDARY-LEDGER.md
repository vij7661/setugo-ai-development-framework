# ECC-Derived V5 Closed Candidate-Boundary Ledger

Status: `V5_BOUNDED_REFERENCE_GREEN_PROVENANCE_FALSIFICATION_REQUIRED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen for impact adjudication, or granted authority by this ledger.

## Parent evidence

- V4 frozen candidate: `8cc79ed23e825f6971e6268b9524e9ed91138028`
- V4 AI re-review disposition: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- V4 freeze recommendation: `DO_NOT_FREEZE_V4_EXPERIMENT_EVIDENCE`
- AI re-review manual threshold contribution: `0`
- EXP-ECC-1..5 at V4: `NARROWING_STILL_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`

## V5 hypothesis

V5 tests whether the caller-selectable strict-mode bypass can be structurally closed at the reference-mechanism layer without pretending that live platform attestations already exist.

The V5 target requires:

1. public `ecc_governance.py` is historical-only and exposes no `requirement_candidate` mode;
2. strict candidate semantics live in a separate internal module;
3. `ecc_candidate_boundary.py` is the only public route intended to issue candidate-eligible reference evidence;
4. eligibility requires an explicit boundary marker, a candidate kind, and a favorable status allowlist;
5. EXP-ECC-1..5 favorable candidate results require a separate reference-evidence source rather than merely rechecking the same caller fixture;
6. imported module identities and selected in-memory function code are bound by runtime policy verification;
7. runtime policy is rechecked immediately before candidate eligibility is issued;
8. EXP-ECC-6/7 remain deferred and cannot become candidate-eligible through the reference mechanism.

This remains a reference-mechanism experiment. A repository-bound reference evidence registry is not a substitute for live signed platform evidence and does not satisfy the later live-integration evidence boundary.

## Frozen assertions

- V5 assertion commit: `dbbfbdb6771fc4a57fc73665fa73bc2cebac4270`
- V5 supersession-aware runner commit: `8ba2ebc66e6d3449de5dbafdd99de6fa5a1736a7`
- V5 workflow-enabled pre-repair SHA: `2c839baad99f220cbe1537820a835be3e7720e28`

The V5 assertion file was frozen before mechanism repair and was not modified during repair.

## RED-001

- exact candidate: `2c839baad99f220cbe1537820a835be3e7720e28`
- workflow run: `34692576280`
- job: `103550334507`
- result: `144 tests; 33 failures; 0 errors`
- V1/V2 active prior suites: `PASS`
- classification: `EXPECTED_PRE_REPAIR_RED`

Primary RED classes: direct public strict access, alias/partial/wrapper bypass, bare strict-class eligibility, missing private strict core, missing separate reference evidence source, same-fixture false independence, absent boundary eligibility marker, imported-module identity weakness, in-memory monkeypatch weakness, and missing final policy recheck.

## Deterministic repair

- repair input SHA: `ec60882d699461f9dfd74b7a3a5625256531c9f0`
- repair workflow run: `34692787449`
- repair job: `103550905667`
- repair-generated mechanism SHA: `0c36b0af0e802a4e0461b594a86b91df9909d466`
- repair test-assertion modification: `NONE`

Generated module SHA-256 values:

- public core: `4817db8e7f7496c288431c5220b4f559c9757b0b0a12ecc9507bf0f95a3ceb51`
- strict core: `2519065974e911adbedd55f645984ff3bf7f7e84d924204b74e659a328d4e7b2`
- candidate boundary: `5e6d452a30522380d8fbb52ebf9567b59fe2699c6f7a293deec56d4c592726f1`
- reference evidence: `ffbe5fd4974e99ddd9d70bd3084e12704038510c267f263d75d5013864f441c7`
- trust manifest: `e10cb5cac1b86ac8644e59ca0af62c0476869ab6d170cb823913f64e477b0f60`

Trust-source classification is explicitly `REFERENCE_REPO_BOUND_SIMULATION_ONLY`. The manifest declares `live_attestation_claimed = false` and `independent_production_trust_root_claimed = false`.

## GREEN-002

- exact tested candidate: `64fa2ac71442d38a2127bcc4c7de688fbac46714`
- workflow run: `34692826791`
- job: `103551010321`
- result: `144/144 PASS`
- V1/V2 active prior suites: `PASS`
- V5 frozen assertions: `PASS`

V5 GREEN establishes only the bounded reference-mechanism properties exercised by the frozen assertions. It does not establish live platform attestation, an independent production trust root, qualifying manual review, production readiness, or requirement adoption.

## Historical test supersession

V3 and V4 test modules remain immutable historical evidence. V5 does not rewrite or delete them. They are excluded from the active V5 runner because the external V4 re-review invalidated specific semantics they encoded:

- V3 required a caller-selectable strict shared-core mode; V5 specifically tests removal of that mode.
- V4 treated a bare strict class as candidate-eligible and used same-fixture cross-checks; the V4 re-review identified both as false-green paths.

Supersession changes active semantics only. It does not erase prior RED/GREEN history.

## Newly exposed provenance boundary

V5 closes the reviewed syntactic eligibility defects, but its `candidate_result_eligible()` predicate still accepts a caller-constructed dictionary when all of the following are syntactically present:

- `evaluation_class = REQUIREMENT_CANDIDATE`
- `candidate_eligible = true`
- a recognized `candidate_kind`
- a favorable status for that kind.

Therefore V5 has not yet proven that the eligibility marker itself was issued by the governed candidate boundary. A caller can forge the result object without executing the boundary at all. This is a distinct higher-order false-green path discovered after V5 GREEN and is not retroactively treated as a V5 test failure.

Open risk: `V5-OPEN-ELIGIBILITY-PROVENANCE-001 — CALLER_FORGEABLE_CANDIDATE_ELIGIBILITY_MARKER`.

Required next step: a separate provenance falsification family must test boundary-issued result provenance, replay/substitution, serialization, direct strict-core result laundering, and forged result construction before any freeze or bounded impact-adjudication claim.

## Current disposition

- EXP-ECC-1..5: `REFERENCE_MECHANISM_NARROWING_GREEN_BUT_PROVENANCE_FALSIFICATION_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- V5 freeze: `DO_NOT_FREEZE_PENDING_PROVENANCE_FALSIFICATION_AND_EXTERNAL_REREVIEW`
- Manual-review threshold contribution from AI review: `0`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
