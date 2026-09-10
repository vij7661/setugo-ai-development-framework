# TESTING Qualification Trust-Root Live Ruleset RED 001

Status: `PRESERVED_RED`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`
Related finding: `MR-005 — CANDIDATE_MODIFIABLE_TRUST_ROOT`

## Frozen regression state

The live external-control verifier and its deterministic regressions were committed before this run on repair branch `repair/testing-trust-root-anchor-004`.

Pull request: `#27`
Head candidate: `01160fac7e92ce06c95aa3309b1b2d6ad80c911e`
Workflow run: `34447805827`
Job: `falsify-qualification-boundary`
Result: `FAILURE`

## Exact failure

The workflow reached the new live external trust-root check and failed closed with:

```text
FAIL_CLOSED: ruleset bypass state is missing
```

The remaining governance and terminal-authority suites were skipped after the fail-closed external-state check.

## Root-cause classification

`GOVERNANCE_PROCESS_DEFECT / EXTERNAL_EVIDENCE_VISIBILITY_GAP`

The GitHub Actions `GITHUB_TOKEN` used by the workflow has `Contents: read` and `Metadata: read`, but the repository-ruleset response visible to that token does not expose `bypass_actors`. The separately observed repository ruleset detail, obtained through an authorized governance inspection path, does expose `bypass_actors: []` and `current_user_can_bypass: never`.

The RED is therefore not evidence that the ruleset is absent or weak. It is evidence that the first live verifier required a field unavailable to the qualification runner and correctly failed closed rather than assuming it.

## Scientific handling

This RED must remain preserved. The regression must not be weakened by pretending an unobservable field is observable. Any repair must distinguish:

1. externally visible rules that the CI token can re-check live; and
2. governance-admin state (such as bypass configuration) that requires separately preserved authorized inspection evidence.

The candidate must still be unable to directly update `phase/testing`; a direct write attempted after ruleset activation was rejected by GitHub with `409 Repository rule violations found — Changes must be made through a pull request`.

No green result may erase this RED.
