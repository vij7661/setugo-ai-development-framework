# TESTING Qualification Trust-Root Post-Merge RED 001

Status: `PRESERVED_GENUINE_RED`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`

## Exact candidate

`6fb96bb8fd0dd4c5ed9c065a2e4350eec0e0cf67`

This is the GitHub merge commit for PR #27 (`Repair TESTING trust-root external control boundary`) into `phase/testing`.

## Workflow evidence

Workflow run: `34449284629`
Job: `falsify-qualification-boundary`
Conclusion: `FAILURE`

The workflow checked out the exact candidate SHA and then failed in the live external trust-root ruleset verification step with:

```text
FAIL_CLOSED: at least one approving review is required
```

The remaining governance and terminal-authority test steps were skipped because the external trust-root control gate failed first.

## Why this RED is scientifically meaningful

Before merge, the repository ruleset had been manually weakened from one required approving review to zero required approving reviews in order to avoid the GitHub self-approval deadlock for a single-account repository owner. The frozen external-control verifier still required at least one approving review. The post-merge workflow therefore failed closed rather than silently accepting the weakened external control.

This is not a flaky CI failure and not a verifier defect. It demonstrates that the qualification gate detected that the live repository control no longer satisfied the preregistered external trust-root protection floor.

## Governance consequence

`MR-005 — CANDIDATE_MODIFIABLE_TRUST_ROOT` remains OPEN and blocks TESTING qualification.

A code change that simply lowers the verifier requirement from one approving review to zero would weaken the preregistered qualification boundary after exposure and is therefore prohibited unless a different independently enforced external mechanism is first specified and falsified.

## Preserved chronology

- preregistration 004 committed before the trust-root repair mechanism;
- ruleset initially created with one required approval and no bypass actors;
- single-author GitHub self-approval was correctly unavailable;
- required approval was manually changed from 1 to 0;
- PR #27 became mergeable and was manually merged;
- merge commit `6fb96bb8fd0dd4c5ed9c065a2e4350eec0e0cf67` triggered run `34449284629`;
- live external-control verification produced the RED above.

## Nonclaims

This preserved RED does not itself repair MR-005, does not authorize promotion, and does not imply that zero-review PR protection is equivalent to independent approval.
