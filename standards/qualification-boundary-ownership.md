# Qualification Boundary Ownership Standard

## Status

Active governance standard for TESTING and all later phases.

## Core invariant

No evaluated actor may define, weaken, waive, reinterpret, or appoint the authority controlling a material part of its own qualification criteria.

An evaluated actor includes a candidate implementation, proposer, reviewer, model, coding agent, CI job, adapter, worker, orchestrator, or any process whose output is being qualified.

## Platform-owned qualification surfaces

The following are governance inputs, not candidate inputs:

1. review-required policy and minimum review level;
2. mandatory review dimensions and their mandatory/non-mandatory status;
3. adversarial matrix identity, required cases, and completion rule;
4. phase-promotion criteria;
5. terminal-authority issuer classes and permitted action scope.

A candidate may supply facts or evidence consumed by these policies, but it may not lower the resulting floor. Candidate-authored labels, booleans, dimensions, matrix definitions, waivers, or authority claims are advisory unless independently reproduced by a platform-owned mechanism.

## Policy identity and binding

Every material qualification decision MUST record:

- `qualification_policy_id`;
- `qualification_policy_version`;
- deterministic `qualification_policy_hash`;
- exact candidate SHA;
- applicable phase;
- applicable review policy/profile;
- applicable adversarial-matrix policy/profile where phase completion is claimed.

Changing the policy content changes the policy hash and invalidates prior qualification for any decision that depended on the prior policy.

## Review-required ownership

Whether review is REQUIRED is determined by platform-owned policy from trusted or independently reproduced facts. Caller, proposer, reviewer, or candidate declarations may escalate review conservatism but may never lower a platform-owned review requirement.

Unknown or unresolved materiality at a consequential boundary fails closed to REQUIRED review rather than NONE.

Interaction mode controls only how a required review is initiated. It does not alter whether the review is required.

## Mandatory review-dimension ownership

Mandatory review dimensions are resolved from a platform-owned review profile. A review request may contain the resolved dimensions for portability, but acceptance MUST verify that the dimensions exactly match the bound policy profile.

A requester may add extra dimensions. It may not delete a policy dimension, downgrade a mandatory dimension, change its semantic description to narrow scope, or substitute another profile without changing the policy binding.

PASS requires every policy-mandatory dimension to be `TESTED_SUPPORTED` with concrete evidence. `BOUNDED_PASS` may leave only policy-declared non-mandatory dimensions bounded.

## Adversarial-matrix ownership

A TESTING-complete claim MUST bind to an explicit platform-owned adversarial matrix profile with a stable matrix ID/version/hash and required case IDs.

The evaluated actor may add cases but may not remove required cases or mark them optional. Missing, skipped, unavailable, or rebound required cases make TESTING completion unsupported.

## Terminal-authority ownership

"External authority" is not sufficient by itself. Terminal authority MUST be represented by a platform-owned authority policy naming permitted issuer classes, phase, action scope, and use-time validity requirements.

Self-declared model/reviewer/agent/candidate authority, an unknown issuer class, missing issuer provenance, stale authorization, or action outside the bound scope MUST fail closed.

TESTING evidence may establish readiness to begin RELEASE qualification. It cannot issue RELEASE, DEPLOY, MERGE-to-protected-release, or PRODUCTION authority unless the bound terminal-authority policy explicitly permits that action and phase.

## Evidence versus authority

Evidence can support a policy decision but cannot redefine the policy that judges the evidence. Green CI, reviewer consensus, PASS tokens, model confidence, and candidate-supplied policy metadata are evidence only.

## Failure preservation

A discovered qualification-boundary ownership defect is a `GOVERNANCE-PROCESS DEFECT`. The first RED/falsification evidence must be preserved. A later repair or PASS must not erase the earlier failure.

## Completion rule

A repair is not closed merely because the new policy code and tests are green. Closure requires exact-SHA requalification against frozen adversarial cases and independent re-falsification where the testing policy requires independent review.
