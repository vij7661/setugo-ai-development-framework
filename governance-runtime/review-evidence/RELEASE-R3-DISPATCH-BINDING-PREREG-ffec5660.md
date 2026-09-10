# RELEASE R3 — External Workflow Dispatch Binding Preregistration

Status: `FROZEN_BEFORE_MECHANISM`
Authority effect: `NONE_EVIDENCE_ONLY`
Exact RELEASE candidate: `ffec566022fcd221fb4ab7569ed3bc245f75b546`
Trigger: independent RELEASE R2 finding `R2-02`.

## Frozen defect statement

The external checker workflows accept a manual `candidate_sha` input. The protected `phase/release` ruleset currently prevents a check on a different SHA from satisfying PR #37, but the workflow itself does not prove that the supplied SHA is the head of the open PR targeting `phase/release`.

## Frozen repair objective

Before publishing a RELEASE qualification or entry check, the checker must independently query GitHub for PR #37 (or the configured exact RELEASE PR), and fail closed unless all are true:

- PR is open;
- PR base ref is exactly `phase/release`;
- PR head SHA exactly equals the supplied candidate SHA;
- supplied candidate SHA exactly equals the frozen RELEASE candidate SHA;
- published check head SHA equals that verified PR head.

Negative controls must reject a wrong SHA, closed PR, wrong base, or PR-head mismatch. This validation is additive; it must not weaken existing exact-SHA, App identity, ancestry, or falsification controls.

The repair does not grant terminal authority and does not authorize merge.
