# TESTING Qualification Boundary Ownership — Review Adjudication

Candidate reviewed: `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`
Reviewer disposition: `TESTING_RULES_BOUNDED_PASS`
Adjudication authority effect: `NONE_EVIDENCE_ONLY`
Phase: `TESTING`

## Adjudication posture

The independent review is preserved as raw evidence and is not terminal authority. Green CI and reviewer confidence do not authorize promotion. This adjudication preserves the review findings while independently classifying their effect against the TESTING qualification-boundary contract.

## Finding dispositions

### F-01 — Missing real signed-attestation fixture in review bundle

Disposition: `VALID_EVIDENCE_GAP`
Severity for TESTING: `MEDIUM`
Effect: `BLOCKS_FULL_REVIEW_CLOSURE_UNTIL_EVIDENCE_REPAIRED`

The bundle omitted the actual signed-attestation fixture required by `test_manual_authority_signed_attestation.py`, so the reviewer could not independently verify the real production-signed artifact. This is a packaging/evidence defect, not a demonstrated runtime control failure.

### F-02 — Candidate-SHA mismatch between packet claim and bundled signed-attestation test fixture

Disposition: `VALID_EVIDENCE_INCONSISTENCY`
Severity for TESTING: `HIGH`
Effect: `BLOCKS_FULL_REVIEW_CLOSURE_UNTIL_RECONCILED`

The reviewer correctly identified that the bundled signed-attestation regression remained bound to `ed265f37487bccffcc5f4463f5f3b62ee9f2b713` while the manual packet claimed a human-signed attestation for `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`. A fresh manual signature for `f81eb5f3...` was subsequently supplied by the human governance owner, but that evidence was not included in the review bundle. Therefore the reviewer's uncertainty was valid at review time and must not be rewritten away.

### F-03 — Trust-root pin is candidate-modifiable and lacks an external trust anchor

Disposition: `VALID_FINDING_ESCALATED`
Reviewer severity: `LOW_MEDIUM`
Adjudicated severity: `CRITICAL`
Effect: `BLOCK_TESTING`
Governance ID: `MR-005`

The reviewer identified that the committed PEM and its pinned DER hash constant can be changed together. Independent repository-state inspection confirms that `phase/testing` is currently unprotected and repository rulesets are empty. Therefore a candidate/evaluated actor with write capability can replace the public trust root and matching hash constant with an attacker-controlled keypair, sign its own privileged attestation, and have the verifier accept it. A runtime self-check comparing the PEM to the in-repo constant does not solve this simultaneous-replacement attack because both values are in the same candidate-controlled trust domain.

This violates the core invariant: the evaluated actor can effectively redefine the authority root controlling its own qualification. The narrow repair must anchor the trust root outside the candidate-modifiable revision or place its mutation behind independently enforced repository/platform controls that the evaluated actor cannot bypass.

### F-04 — Missing CI-referenced tests/terminal-authority suite from review bundle

Disposition: `VALID_EVIDENCE_GAP`
Severity for TESTING: `MEDIUM`
Effect: `BLOCKS_FULL_INDEPENDENT_HARNESS_VERIFICATION`

The reviewer could not independently inspect or execute the omitted review-protocol and terminal-authority tests. This does not contradict the observed CI execution but prevents full independent verification of the cited surface.

## QO adjudication

QO-01: `TESTED_SUPPORTED`
QO-02: `TESTED_SUPPORTED`
QO-03: `TESTED_SUPPORTED`
QO-04: `TESTED_SUPPORTED_BUT_MR005_BLOCKS_CLOSURE`
QO-05: `TESTED_SUPPORTED_BUT_EVIDENCE_INCOMPLETE`
QO-06: `TESTED_SUPPORTED`
QO-07: `TESTED_SUPPORTED`
QO-08: `TESTED_SUPPORTED`

The reviewer's bounded-pass disposition remains preserved as reviewer evidence. Platform adjudication is stricter because MR-005 exposes a candidate-controlled root-of-trust replacement path. Therefore TESTING qualification-boundary ownership remains `OPEN_BLOCKED` and must not be promoted.

## External-state evidence

As observed after the review:

- `phase/testing` exact SHA: `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`
- branch protection: disabled
- required status checks enforcement: off
- repository rulesets: none

These facts materially strengthen F-03 into MR-005.

## Nonclaims

- This adjudication does not grant TESTING terminal authority.
- It does not authorize RELEASE or PRODUCTION.
- It does not erase the reviewer's bounded pass or earlier failure history.
- A repository-only trust-root hash check is defense in depth only and is insufficient to close MR-005.
