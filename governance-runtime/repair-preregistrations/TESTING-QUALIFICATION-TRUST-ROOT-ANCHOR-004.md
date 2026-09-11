# TESTING Qualification Trust-Root Anchor Repair Preregistration 004

Status: `PREREGISTERED_BEFORE_MECHANISM_CHANGE`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`

## Trigger

Independent manual falsification of candidate `f81eb5f3cbde819d60c134ba73287dedc6b67e0b` identified that the Ed25519 public trust root and its pinned DER hash constant are both stored in candidate-modifiable repository content. Follow-up platform inspection confirmed:

- `phase/testing` branch protection is disabled.
- required status-check enforcement is off.
- repository rulesets are empty.

Therefore the evaluated actor can replace both the PEM and the matching in-repo pin with an attacker-controlled keypair and then self-sign a privileged attestation. A runtime comparison between the PEM and the in-repo constant is insufficient because both are in the same candidate-controlled trust domain.

Governance finding: `MR-005 — CANDIDATE_MODIFIABLE_TRUST_ROOT`
Severity: `CRITICAL`
Current disposition: `BLOCK_TESTING`

## Frozen failure hypothesis

The qualification boundary is falsified if an evaluated actor with ordinary candidate/repository write capability can change the authority trust root or its authoritative fingerprint without an independently enforced control outside the candidate revision, then produce a verifier-accepted privileged attestation using the replacement key.

## Required repair properties

1. The authoritative manual-governance trust anchor must be outside the candidate-modifiable source revision, or its mutation must be protected by an independently enforced platform/repository control the candidate cannot bypass.
2. Candidate code must remain verification-only; no private signing key or privileged issuer may enter the repository or candidate runtime.
3. The repository PEM may remain as verifier material only if it is validated against an external authoritative anchor before privileged authority can be accepted.
4. Simultaneous replacement of repository PEM plus in-repo fingerprint/policy constant must fail closed.
5. Unknown/missing external anchor state must fail closed.
6. Trust-root changes must require explicit human governance action and must not be authorized by green CI, reviewer output, model output, or candidate assertions.
7. Exact-SHA, authority-class, scope, policy binding, manual-only TESTING review policy, and preserved failure history remain mandatory.
8. No repair may weaken frozen MR-001 through MR-004 regressions.

## Acceptance tests to freeze before repair

The repair is not complete until a frozen adversarial test or external-state qualification demonstrates all of the following:

- attacker-generated keypair + replaced repo PEM + replaced in-repo fingerprint cannot yield accepted privileged authority;
- unchanged authorized trust root can still verify a valid human-signed attestation;
- missing external trust-anchor evidence fails closed;
- mismatched external trust-anchor fingerprint fails closed;
- candidate cannot disable/bypass the external trust-anchor check merely by changing candidate code/workflow;
- existing role-string, issuer, SHA-replay, scope-escalation, policy-rebinding, trust-root-ID-rebinding, phase-label, and harness regressions continue to pass.

## External control options allowed for investigation

Any chosen mechanism must satisfy the invariant above. Candidate approaches include, but are not limited to:

- protected branch/ruleset requiring independently controlled review for trust-root paths;
- trusted CI/environment configuration containing the authoritative trust-root fingerprint and protected from candidate modification;
- a separate governance repository or immutable/signed trust-root registry controlled outside the candidate repository;
- a signed trust-root chain anchored in an external human-controlled root.

No option is accepted merely because it is convenient; it must be falsified against candidate bypass.

## Evidence chronology to preserve

- prior candidate-callable issuer RED: `5897ffae47f0cb17b06c0c13ee9095bc351516ba`, workflow `34439769044`;
- verifier-only repair construction green: `ed265f37487bccffcc5f4463f5f3b62ee9f2b713`, workflow `34441388601`;
- signed-attestation harness false-green: `2585c7e20674cbc56c97f6342ecde6ba426badc1`, workflow `34441874259`;
- corrected signed-attestation construction green: `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`, workflow `34441939120`;
- independent reviewer disposition at `f81eb5f3...`: `TESTING_RULES_BOUNDED_PASS`, with trust-root replacement finding F-03;
- platform adjudication escalates F-03 to `MR-005 / CRITICAL / BLOCK_TESTING` because the branch is unprotected and no rulesets exist.

## Nonclaims

This preregistration does not itself repair MR-005, does not authorize promotion, and does not establish independent acceptance. The next mechanism change must occur only after this preregistration is committed.
