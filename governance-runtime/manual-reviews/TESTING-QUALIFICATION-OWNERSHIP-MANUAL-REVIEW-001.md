# Manual TESTING Re-falsification — Qualification Boundary Ownership

Review ID: `TESTING-QUALIFICATION-OWNERSHIP-MANUAL-REVIEW-001`
Review mode: **MANUAL ONLY — NO EXTERNAL REVIEWER API**
Reviewed candidate: `9cbc803e13aa12ee198a498a4afaf90af8ad8637`
Phase: `TESTING`
Disposition: `CHANGES_REQUIRED`
Authority effect: `NONE_REVIEW_EVIDENCE_ONLY`

## Scope

Manual falsification of the eight qualification-boundary ownership cases QO-01 through QO-08 after the ownership repair. Green CI is treated as execution evidence only.

## Finding MR-001 — Authority-role labels are caller-asserted content, not verified authority

Severity: **CRITICAL**
Material: **true**
Phase classification: `BLOCK_TESTING`
Affected cases: `QO-05`, `QO-06`, `QO-07`

### Concrete failure path

The repaired functions compare caller-provided strings against privileged role names:

- `acceptance_boundary_record(... approved_by="HUMAN_GOVERNANCE_OWNER")`
- `root_cause_classification_allowed(... classifier_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR")`
- `reviewer_finding_adjudication_allowed(... adjudicator_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR")`

The function receives the privileged identity label from the same call boundary that may be influenced by the evaluated actor. No trusted provenance object, issuer binding, exact-candidate authority evidence, or independent verifier is required before those strings become authoritative inputs.

Therefore an evaluated actor can self-label itself with the permitted role and satisfy the repaired gate. The code prevents *wrong labels*, but not *false claims of the right label*.

### Why current tests false-green

The tests prove that strings such as `CANDIDATE`, `REVIEWER`, and `CODING_AGENT` are rejected. They do not falsify spoofing of the accepted privileged string by an untrusted caller. Thus construction green does not establish authority provenance.

### Required narrow repair

Privileged role names must not be accepted as naked caller strings. The gate must require a platform-created authority binding that is:

1. bound to exact candidate SHA;
2. bound to the governing policy hash/version;
3. bound to action/decision scope;
4. identifies authority class;
5. records a trusted/manual evidence source distinct from candidate content;
6. is verified before use;
7. cannot be replaced by a candidate-supplied boolean or role string.

In TESTING, the acceptable source is a **manual governance attestation** entered through the governed manual-review/adjudication path. This does not claim cryptographic human identity; it only prevents raw candidate content from directly becoming an authority assertion.

## Finding MR-002 — Phase deferral still trusts caller-supplied violated-contract phase

Severity: **CRITICAL**
Material: **true**
Phase classification: `BLOCK_TESTING`
Affected case: `QO-08`

### Concrete failure path

`phase_disposition(current_phase, violated_contract_phase, material, uncertainty=False)` derives deferral correctly *after* accepting `violated_contract_phase` from the caller. A candidate with a material TESTING defect can submit `violated_contract_phase="RELEASE"`; the function then returns `DEFERRED_TO_RELEASE`.

The new code moved the deferral rule into platform policy, but did not move ownership of the factual contract-applicability determination out of candidate-controlled input.

### Required narrow repair

The phase of the violated contract must come from a platform-owned contract/rule identifier mapping, not a caller-selected phase label. The caller may identify the violated governed rule/contract ID; platform policy resolves that ID to its owning phase. Unknown or unmapped rule IDs must fail closed as `REQUIREMENT_UNRESOLVED`.

## Cases not defeated by this manual pass

QO-01 through QO-04 were not defeated by the specific attacks above. That is **not** a PASS claim for those cases; full manual re-falsification remains required after the material MR-001/MR-002 repair because the exact candidate SHA will change.

## Preserved conclusion

Candidate `9cbc803e13aa12ee198a498a4afaf90af8ad8637` is **not qualified** for TESTING completion. Existing green CI remains preserved as construction evidence, but the manual review demonstrates two material governance-process defects. Repair must expose executable regressions for privileged-role spoofing and caller-selected phase deferral before mechanism changes are accepted.
