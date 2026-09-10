# TESTING Qualification Trust-Root Construction Evidence 002

Status: `CONSTRUCTION_GREEN_PENDING_HUMAN_PR_APPROVAL_AND_POST_MERGE_REQUALIFICATION`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`
Related finding: `MR-005 — CANDIDATE_MODIFIABLE_TRUST_ROOT`

## External control state

Repository ruleset `22736961` is active for `refs/heads/phase/testing`. Authorized governance inspection observed deletion protection, non-fast-forward protection, pull-request review requirements, strict `falsify-qualification-boundary` required status checks, no bypass actors, and `current_user_can_bypass: never`.

A direct repository write attempted after ruleset activation was rejected by GitHub with `409 Repository rule violations found — Changes must be made through a pull request`.

## Frozen live-check RED

PR: `#27`
Head at first live-check run: `01160fac7e92ce06c95aa3309b1b2d6ad80c911e`
Workflow run: `34447805827`
Conclusion: `FAILURE`

Exact failure:

```text
FAIL_CLOSED: ruleset bypass state is missing
```

This demonstrated that the GitHub Actions token could not observe admin-only bypass configuration and that the verifier failed closed instead of assuming it.

## Narrow repair

The external-control verifier now distinguishes:

- runner-visible ruleset semantics, checked live in CI; and
- admin-only bypass state, qualified by separately preserved authorized repository-governance evidence.

Strict validation still rejects missing bypass state when admin visibility is claimed. Runner-visible validation does not claim that visibility and still rejects a non-empty bypass list if the field is present.

## Construction green

PR: `#27`
Repair-branch head: `317c17013b2b7722b403a4a5a085c9306e83060f`
Synthetic PR merge candidate tested by GitHub: `1d6f865581ae7f2bf3420b40666691a71276b80a`
Workflow run: `34447998994`
Conclusion: `SUCCESS`

The run recorded:

```text
PASS_BOUNDED_EVIDENCE_ONLY: externally visible TESTING trust-root rules satisfy the frozen runner-visible contract
ADMIN_BYPASS_STATE: qualified separately by authorized repository-governance evidence; runner token does not claim visibility
```

Governance suite:

```text
Ran 92 tests
OK
```

Terminal-authority suite:

```text
Ran 26 tests
OK
```

The 92-test governance run explicitly executed the external trust-root regressions for inactive ruleset, wrong target, bypass actors, missing PR rule, zero approvals, missing review-thread resolution, missing deletion/force-push protections, non-strict status checks, missing qualification check, strict missing-bypass failure, runner-visible bounded mode, and simultaneous candidate-local PEM/pin replacement.

## Current blocker

The protected `phase/testing` branch requires a human PR approval. No PR review is currently present. Construction green therefore does not authorize merge.

After an authorized human approval and merge, the resulting exact `phase/testing` SHA must run the qualification workflow again. That post-merge exact SHA is the candidate that can be considered for subsequent manual authority attestation and independent refalsification.

## Nonclaims

This evidence does not close MR-005 scientifically by itself, does not grant terminal authority, and does not establish RELEASE or PRODUCTION qualification. The preserved RED remains part of the evidence history.
