# TESTING-QUALIFICATION-OWNERSHIP-001 — Qualification Boundary Ownership

## Status

`PREREGISTERED_BEFORE_MECHANISM_CHANGE`

## Phase

`TESTING`

## Source evidence

Independent TESTING/FALSIFICATION review of the governed platform rules pack returned `TESTING_RULES_BOUNDED_PASS` and identified unresolved ownership of load-bearing qualification terms. The review itself remains evidence only and does not establish authority.

The full eight-finding reviewer artifact is not currently present in the authoritative repository or available to this repair execution. Therefore this preregistration freezes only the defects that can be independently reconstructed from the supplied review summary. Unseen findings MUST remain open and MUST NOT be represented as repaired or closed.

## Defect class

`GOVERNANCE-PROCESS DEFECT`

## General falsification hypothesis

A candidate, proposer, reviewer, coding agent, CI job, or orchestrator can create a false-green if it can define, weaken, waive, reinterpret, or appoint the authority controlling a material part of its own qualification criteria.

## Frozen ownership defects

### QO-01 — Review-required decision can be candidate-influenced

Current rule language says review occurs "when needed" without naming the owner of that determination. Runtime review classification also consumes trigger/transition/path facts supplied by callers. A candidate-controlled caller must not be able to lower a platform-owned review floor by choosing benign labels or omitting material facts.

**Required falsification:** demonstrate that proposer/reviewer/caller declarations cannot lower a deterministic platform review requirement.

### QO-02 — Mandatory review dimensions lack an authoritative owner

A review request may currently carry caller-supplied `required_review_dimensions`, including caller-supplied `mandatory` flags. Structural validation proves only that the field is present and normalized; it does not prove the candidate did not choose its own grading dimensions.

**Required falsification:** demonstrate that review dimensions and mandatory flags used for qualification are resolved from a platform-owned policy identified by immutable policy identity/hash, not accepted from the evaluated actor.

### QO-03 — Standard adversarial matrix lacks an authoritative owner

The TESTING pass criteria require the "standard adversarial matrix" to be exercised but the rule pack does not identify the authoritative matrix definition, version, owner, or immutable binding.

**Required falsification:** demonstrate that TESTING completion binds to one explicit platform-owned adversarial-matrix policy/version/hash and fails closed when cases are missing or rebound.

### QO-04 — Terminal authority is described as external but not fully named

Rules correctly deny terminal authority to models/agents/reviewers/CI/orchestrators, but "external" alone does not identify who or what may issue terminal authorization.

**Required falsification:** demonstrate that terminal authority is represented by an explicit authority class/issuer policy with permitted actions and phase scope, and that absence/unknown/self-declared authority cannot authorize a terminal action.

## Durable repair invariant

> No evaluated actor may define, weaken, waive, reinterpret, or appoint the authority controlling a material part of its own qualification criteria.

This includes the review trigger floor, mandatory review dimensions, adversarial acceptance matrix, phase-promotion criteria, and terminal-authority issuer.

## Required repair shape

1. Create a platform-owned qualification policy with immutable policy identity and deterministic content hash.
2. Resolve mandatory review dimensions from that policy; caller-provided dimensions are advisory evidence only and cannot lower or replace the policy floor.
3. Resolve TESTING adversarial cases from that policy and require exact policy binding for a TESTING-complete claim.
4. Resolve terminal-authority issuer/action scope from that policy; unknown, absent, candidate-authored, reviewer-authored, or model-authored authority fails closed.
5. Add executable negative tests for self-definition, dimension deletion/downgrade, matrix omission/rebinding, and terminal-authority self-appointment.
6. Preserve the original bounded-review disposition and all unresolved findings until re-falsification.

## Scientific acceptance rule

Construction green after this repair is not sufficient. The exact repaired candidate SHA must be independently re-falsified against these frozen cases before QO-01 through QO-04 can be closed. The remaining findings from the original eight-finding review remain open until their full evidence is recovered and adjudicated.
