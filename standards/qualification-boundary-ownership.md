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
4. acceptance-boundary preregistration requirements and post-exposure immutability;
5. material root-cause and reviewer-finding adjudication authority;
6. phase applicability and defer/block classification;
7. phase-promotion criteria;
8. terminal-authority issuer classes and permitted action scope.

A candidate may supply facts or evidence consumed by these policies, but it may not lower the resulting floor. Candidate-authored labels, booleans, dimensions, matrix definitions, phase labels, waivers, or authority claims are advisory unless independently reproduced by a platform-owned mechanism.

## Policy identity and binding

Every material qualification decision MUST record:

- `qualification_policy_id`;
- `qualification_policy_version`;
- deterministic `qualification_policy_hash`;
- exact candidate SHA;
- applicable phase;
- applicable review policy/profile;
- applicable adversarial-matrix policy/profile where phase completion is claimed.

Changing policy content changes the policy hash and invalidates prior qualification for any decision that depended on the prior policy.

## Review-required ownership

Whether review is REQUIRED is determined by platform-owned policy from trusted or independently reproduced facts. Caller, proposer, reviewer, or candidate declarations may escalate review conservatism but may never lower a platform-owned review requirement.

Unknown or unresolved materiality at a consequential boundary fails closed to REQUIRED review rather than NONE.

Interaction mode controls only how a required review is initiated. It does not alter whether the review is required.

In TESTING, reviews are manual-only and external reviewer APIs are prohibited. User approval or an API boundary being under test does not override that prohibition.

## Mandatory review-dimension ownership

Mandatory review dimensions are resolved from a platform-owned review profile. A review request may contain the resolved dimensions for portability, but acceptance MUST verify that the dimensions exactly match the bound policy profile.

A requester may add extra dimensions. It may not delete a policy dimension, downgrade a mandatory dimension, change its semantic description to narrow scope, or substitute another profile without changing the policy binding.

PASS requires every policy-mandatory dimension to be `TESTED_SUPPORTED` with concrete evidence. `BOUNDED_PASS` may leave only policy-declared non-mandatory dimensions bounded.

## Adversarial-matrix ownership

A TESTING-complete claim MUST bind to an explicit platform-owned adversarial matrix profile with a stable matrix ID/version/hash and required case IDs.

The evaluated actor may add cases but may not remove required cases or mark them optional. Missing, skipped, unavailable, or rebound required cases make TESTING completion unsupported.

## Acceptance-boundary ownership

The platform determines which artifact and contract classes require preregistration. An evaluated actor cannot waive that requirement for itself.

Once a governed acceptance boundary has been exposed to implementation or test execution, its material binding is immutable within that lineage. A changed boundary requires a new preregistration lineage rather than rewriting the prior one.

Acceptance approval is a privileged decision. A naked string such as `HUMAN_GOVERNANCE_OWNER` is content, not authority. The decision must consume a trusted platform-issued authority binding scoped to the exact candidate SHA, current qualification-policy identity/hash, decision scope, authority class, and durable manual-governance evidence reference.

## Root-cause and finding-adjudication ownership

For a material failure, the evaluated actor cannot terminally classify its own root cause merely by supplying an allowed classifier label. Material classification requires an authority binding for the independent governance adjudication scope plus the bound failure evidence.

A reviewer finding remains evidence until adjudicated. Candidate, reviewer, model, agent, or orchestrator content cannot self-appoint the adjudicator. Material finding adjudication requires the exact candidate SHA, preserved raw finding, and a trusted authority binding for the review-finding adjudication scope.

In TESTING, the trusted source represented by such a binding is a manual governance attestation. The runtime binding prevents naked candidate content from directly becoming an authority assertion; it does not claim cryptographic proof of human identity.

## Phase-classification ownership

A caller does not decide whether a defect belongs to TESTING, RELEASE, or PRODUCTION by supplying a phase label.

The caller identifies the violated governed rule or contract. Platform policy resolves that governed identifier to its owning phase. Only a platform-mapped later-phase rule may produce `DEFERRED_TO_RELEASE` or `DEFERRED_TO_PRODUCTION`.

A missing, unknown, unmapped, or merely caller-selected phase claim fails closed as `REQUIREMENT_UNRESOLVED`. A material violation mapped to the current TESTING contract blocks TESTING.

## Terminal-authority ownership

"External authority" is not sufficient by itself. Terminal authority MUST be represented by a platform-owned authority policy naming permitted issuer classes, phase, action scope, and use-time validity requirements.

Self-declared model/reviewer/agent/candidate authority, an unknown issuer class, missing issuer provenance, stale authorization, or action outside the bound scope MUST fail closed.

TESTING evidence may establish readiness to begin RELEASE qualification. It cannot issue RELEASE, DEPLOY, MERGE-to-protected-release, or PRODUCTION authority unless the bound terminal-authority policy explicitly permits that action and phase.

## Evidence versus authority

Evidence can support a policy decision but cannot redefine the policy that judges the evidence. Green CI, reviewer consensus, PASS tokens, model confidence, and candidate-supplied policy metadata are evidence only.

A platform-created in-process capability is also not, by itself, proof that a human acted. It is valid only as a runtime representation of already-recorded trusted manual governance evidence and only within its exact SHA/policy/scope binding.

## Failure preservation

A discovered qualification-boundary ownership defect is a `GOVERNANCE-PROCESS DEFECT`. The first RED/falsification evidence must be preserved. A later repair or PASS must not erase the earlier failure.

Test-harness defects that silently omit intended falsification tests are material when they can produce a governance false-green. The false-green run and the later genuine RED must both remain in history.

## Completion rule

A repair is not closed merely because the new policy code and tests are green. Closure requires exact-SHA requalification against frozen adversarial cases and independent manual re-falsification where the TESTING policy requires independent review.
