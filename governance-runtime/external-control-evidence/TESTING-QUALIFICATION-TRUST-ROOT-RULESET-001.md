# TESTING Qualification Trust-Root External Control Evidence 001

Status: `EXTERNAL_CONTROL_OBSERVED`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`
Related finding: `MR-005 — CANDIDATE_MODIFIABLE_TRUST_ROOT`

## External repository state observed after manual remediation

GitHub repository: `vij7661/setugo-ai-development-framework`
Ruleset ID: `22736961`
Ruleset name: `phase/testing`
Enforcement: `active`
Target: `refs/heads/phase/testing`

Observed rules:

- deletion protection enabled;
- non-fast-forward / force-push protection enabled;
- pull request required before update;
- one approving review required;
- Code Owner review required;
- review-thread resolution required;
- unattributed changes require extra approval;
- strict required status checks enabled;
- required status check context: `falsify-qualification-boundary`;
- bypass actors: none;
- current user bypass capability: `never`.

## Scientific interpretation

This external control materially changes the MR-005 threat model: candidate-controlled repository content can still propose a trust-root replacement, but it cannot directly update the protected `phase/testing` ref without satisfying repository-enforced review/status requirements. The external ruleset is not stored in the candidate revision and therefore is not mutable merely by editing candidate code, the PEM, the in-repo fingerprint, or the workflow in a direct push.

This does not prove that every future human approval is correct. It does establish an external trust-boundary control against unilateral candidate mutation, which was absent when MR-005 was exposed.

## Chronology defect preserved

The live GitHub ruleset was created manually after preregistration 004 but before the frozen external-state regression artifact was committed. Therefore there is no post-freeze live RED for the exact ruleset endpoint. The pre-repair RED condition is nevertheless independently preserved by earlier GitHub evidence showing `phase/testing` as unprotected with required status-check enforcement off and the repository ruleset collection empty.

This chronology must not be rewritten as though the frozen regression preceded the manual external repair.

## Remaining falsification requirement

The ruleset must be checked as live external state during qualification. Missing ruleset state, wrong target, inactive enforcement, missing pull-request approval, missing Code Owner review, missing strict required status checks, missing `falsify-qualification-boundary`, or any bypass actor must fail closed for MR-005 qualification.

This evidence grants no terminal authority and does not establish RELEASE or PRODUCTION qualification.
