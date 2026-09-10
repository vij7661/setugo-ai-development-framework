# Independent re-falsification evidence — exact candidate 2fee17ad

Status: `USER_RELAYED_EXTERNAL_REVIEW_EVIDENCE`
Authority effect: `NONE_EVIDENCE_ONLY`
Candidate SHA: `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1`
Reviewer provenance: user reports this was returned by DeepSeek after reviewing the exact-candidate text packet. This file preserves the relayed content as evidence; it does not independently authenticate provider/model identity and does not grant authority.

## Relayed disposition

`CHANGES_REQUIRED`

## Relayed findings

### Finding 1 — CRITICAL: Terminal authority can be self-granted without signed binding

- Failure path: `qualification_boundary_policy_v4.terminal_authority_allowed()` accepts caller-supplied `issuer_class`, `provenance_verified=True`, and `current=True`. A caller can pass `issuer_class="HUMAN_GOVERNANCE_OWNER"`, `phase="TESTING"`, `action="READY_TO_BEGIN_RELEASE_QUALIFICATION"` and receive `True`. No exact candidate SHA, policy hash, evidence ref, or Ed25519 attestation is checked. The test suite itself asserts this path returns True.
- Affected rule/mechanism: Terminal-authority ownership; QO-04; `TERMINAL_AUTHORITY_POLICY`.
- Evidence needed to close: Terminal authority must consume `verify_authority_binding` or equivalent signed manual-governance attestation scoped to exact SHA, policy identity/hash, phase, action, issuer class, and use-time validity. Add frozen regression proving naked `HUMAN_GOVERNANCE_OWNER` plus booleans cannot grant terminal authority.

### Finding 2 — CRITICAL: External trust-root pointer and policy constants are candidate-modifiable

- Failure path: `external_governance_root.py` defines `EXTERNAL_REPOSITORY`, `EXTERNAL_REPOSITORY_ID`, `EXTERNAL_ROOT_COMMIT`, and `EXPECTED_PUBLIC_KEY_DER_SHA256` inside the candidate revision. `_policy_material()` imports these into the policy hash. A candidate can change these constants to point to an attacker-controlled public archived repo/commit/key, recompute the policy hash, sign a new attestation with that key, and have verification accept it. No external immutable anchor pins the root identity outside candidate-modifiable code.
- Affected rule/mechanism: External trust-root substitution/rebinding; policy-hash rebinding; authority self-grant.
- Evidence needed to close: Anchor the external repository identity, commit, and DER fingerprint outside the candidate revision, e.g. protected CI/environment configuration, separate governance repo, or signed policy artifact. Add frozen test that candidate-local constant replacement cannot redirect verification to an attacker-controlled root.

### Finding 3 — CRITICAL: Required status check is produced by candidate-modifiable workflow

- Failure path: The ruleset requires context `falsify-qualification-boundary`, but that context is emitted by `.github/workflows/testing-qualification-boundary-ownership.yml`, which is in the candidate repository. A candidate PR can modify the workflow to echo success under the same job name without running the real falsification suite. The protected branch ruleset checks only the status context, not the workflow content.
- Affected rule/mechanism: Candidate-controlled rule weakening; harness false-green; completion rule.
- Evidence needed to close: The qualification workflow and falsification harness must be externally pinned or protected so candidate changes cannot alter the executed tests. Provide evidence that modifying candidate workflow/tests cannot produce the required status context.

### Finding 4 — HIGH: Archived-root assumption relies on mutable GitHub API state

- Failure path: `validate_repository_metadata()` accepts the root if GitHub reports `archived=True`. The external repo is owned by the same user/org as the candidate repo. An owner or compromised owner credential can unarchive, force-push, delete, or rebind the external repo. Pinning a commit does not make the repo cryptographically immutable, and if the candidate also changes the constants, verification can be redirected.
- Affected rule/mechanism: Archived-root assumptions; external trust-root substitution.
- Evidence needed to close: Use a cryptographically immutable trust anchor or externally protected configuration not dependent solely on GitHub’s archived flag. Add fail-closed evidence for unarchive, deletion, force-push, and repository rebinding.

### Finding 5 — HIGH: Policy hash is computed from candidate-controlled material

- Failure path: `qualification_policy_hash()` is derived from `_policy_material()` in candidate code. A candidate can weaken policy material, recompute the hash, and mint a new attestation if it also controls the external root pointer/key. Historical v4 rejection does not prevent a newly self-consistent v5 self-grant.
- Affected rule/mechanism: Policy-hash rebinding; stale-attestation acceptance.
- Evidence needed to close: Bind the policy hash to an externally anchored policy artifact. Add frozen test that candidate policy material changes cannot be made without external governance authorization.

### Finding 6 — MEDIUM/HIGH: Phase deferral mapping is candidate-modifiable

- Failure path: `phase_disposition()` resolves `violated_rule_id` through `GOVERNED_RULE_PHASES`, a dict in candidate policy code. A candidate can remap a TESTING rule to RELEASE/PRODUCTION to produce `DEFERRED_TO_*` instead of `BLOCK_TESTING`.
- Affected rule/mechanism: Phase deferral; QO-08.
- Evidence needed to close: Externally anchor the governed rule-to-phase mapping. Add frozen regression that candidate changes to the mapping cannot defer a current-phase material defect.

Reviewer-stated authority effect: `NONE_EVIDENCE_ONLY`.
