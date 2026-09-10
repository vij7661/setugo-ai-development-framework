# Independent Manual Falsification Packet — TESTING Qualification Boundary Ownership

## Review posture

Phase: `TESTING`
Review mode: `MANUAL_ONLY`
External reviewer APIs: `PROHIBITED`
Candidate SHA: `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`
Required reviewer posture: assume false-green until disproven.
Authority effect of reviewer output: `EVIDENCE_ONLY_UNTIL_ADJUDICATED`

Do not review RELEASE/PRODUCTION readiness. Review only whether the TESTING qualification-boundary ownership contract is falsified at this exact candidate SHA.

## Core invariant

No evaluated actor may define, weaken, waive, reinterpret, or appoint the authority controlling a material part of its own qualification criteria.

## Mandatory attack matrix

The reviewer must independently attack all eight cases:

- `QO-01` Candidate declarations cannot lower a platform review requirement.
- `QO-02` Mandatory review dimensions cannot be deleted, downgraded, rebound, or semantically narrowed by the candidate.
- `QO-03` Required TESTING adversarial cases cannot be omitted, replaced, or weakened by the candidate.
- `QO-04` Candidate/model/reviewer/agent cannot self-appoint terminal authority.
- `QO-05` Evaluated actor cannot waive preregistration or rewrite an exposed acceptance boundary.
- `QO-06` Evaluated actor cannot terminally classify its own material failure using a self-asserted privileged role.
- `QO-07` Evaluated actor or reviewer cannot terminally adjudicate reviewer evidence about itself.
- `QO-08` Evaluated actor cannot relabel a TESTING defect as RELEASE/PRODUCTION to defer it.

## Additional required falsification targets

1. Attempt to mint privileged authority from candidate-callable code.
2. Attempt raw role-string impersonation.
3. Attempt replay of a valid authority attestation to another candidate SHA.
4. Attempt authority-class escalation.
5. Attempt decision-scope escalation.
6. Attempt attestation payload tampering.
7. Attempt signature tampering.
8. Attempt policy-hash/version rebinding.
9. Attempt trust-root rebinding.
10. Attempt contradictory caller phase labels.
11. Attempt to exploit missing/unknown governed-rule mappings.
12. Verify the test harness actually executes the intended adversarial tests; do not infer coverage from a green workflow alone.

## Candidate implementation to inspect

- `governance-runtime/qualification_boundary_policy.py`
- `governance-runtime/qualification_boundary_policy_v4.py`
- `governance-runtime/manual_authority_verifier.py`
- `governance-runtime/trust-roots/governance-public.pem`
- `governance-runtime/phase_policy.py`
- `governance-runtime/review_protocol.py`
- `.github/workflows/testing-qualification-boundary-ownership.yml`
- `standards/qualification-boundary-ownership.md`

## Frozen/adversarial tests to inspect

- `governance-runtime/test_qualification_boundary_policy.py`
- `governance-runtime/test_manual_review_authority_spoofing_regression.py`
- `governance-runtime/test_manual_review_authority_ingress_regression.py`
- `governance-runtime/test_manual_authority_verifier.py`
- `governance-runtime/test_manual_authority_signed_attestation.py`
- `governance-runtime/test_qualification_boundary_unittest_bridge.py`
- `governance-runtime/test_phase_policy.py`

## Preserved failure history the reviewer must not erase

- Earlier ownership construction green was later found to be a harness false-green because top-level `test_*` functions were not collected by `python -m unittest`.
- Corrected harness produced genuine RED at candidate `d415d60cbb29d1943ef926fea384aa91c9be2043`, workflow `34438867816`, with four frozen spoofing/phase failures.
- A later manual attack produced RED at `5897ffae47f0cb17b06c0c13ee9095bc351516ba`, workflow `34439769044`, exposing candidate-callable authority issuance and contradictory phase-label behavior.
- MR-004 contradictory phase-label path was repaired.
- Candidate-callable issuer was replaced by verification-only Ed25519 trust-root verification.
- Workflow `34441939120` on exact candidate `f81eb5f3cbde819d60c134ba73287dedc6b67e0b` completed successfully after the signed-attestation tests were made actually discoverable; it ran 77 governance tests plus 26 terminal-authority tests.

Green CI is evidence only, not proof of correctness.

## Manual authority evidence

A human-controlled Ed25519 private key exists outside the repository and candidate runtime. Only the public key is committed. The exact candidate has a separately stored signed attestation with:

- candidate SHA: `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`
- authority class: `HUMAN_GOVERNANCE_OWNER`
- decision scope: `ACCEPTANCE_BOUNDARY_APPROVAL`
- policy ID: `QUALIFICATION_BOUNDARY_OWNERSHIP`
- policy version: `4`
- policy hash: `43465a69dd7bacd1626fb18412e6e972aa7b522dff24b601c9a74bf9d176a668`
- trust root: `SETUGO_MANUAL_GOVERNANCE_ED25519_V1`

This attestation is evidence for acceptance-boundary approval only. It is not independent-review adjudication, RELEASE authority, or PRODUCTION authority.

## Required reviewer output

Return:

1. `Disposition`: one of `TESTING_RULES_PASS`, `TESTING_RULES_BOUNDED_PASS`, `CHANGES_REQUIRED`, `INSUFFICIENT_EVIDENCE`.
2. For every finding: finding ID, severity, affected QO case/rule, concrete failure path, why current mechanism does not block it, reproducible attack steps, phase classification, and narrow repair.
3. Explicit result for each `QO-01` through `QO-08`: `TESTED_SUPPORTED`, `CONTRADICTED`, or `NOT_TESTED`.
4. Explicit statement whether the reviewer independently verified that the intended adversarial tests are actually executed.
5. Explicit statement that reviewer output is evidence only and grants no terminal authority.

A PASS or bounded pass is invalid if any mandatory QO case is `NOT_TESTED` or `CONTRADICTED`.
