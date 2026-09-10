# Trust Boundary Consolidation — R7 through R11

Status: DESIGN_BASELINE
Authority effect: NONE_EVIDENCE_ONLY
Applies to: TESTING qualification governance

## Purpose

Consolidate the trust-boundary lessons exposed by R7–R11 so future mechanism work begins from an explicit trusted-computing model rather than discovering one hidden assumption at a time.

## Core rule

No component gains authority merely because it produced green evidence. Every material decision must identify separately:

1. what code/data is being evaluated,
2. who can modify it,
3. what external control constrains that modification,
4. how the exact version is identified,
5. what executable verifies it,
6. how that verifier itself is identified and constrained,
7. what evidence proves execution,
8. what actor is allowed to adjudicate or authorize the next phase.

Missing or materially unknown information fails closed.

## Trusted-computing boundary

### Candidate repository

Candidate code is untrusted input to qualification. The candidate may contain production code, tests, workflows, fixtures, policy text, evidence records, or imports designed accidentally or deliberately to create a false green. Therefore candidate-controlled content cannot define its own qualification truth merely by being present in the repository.

### Candidate local CI

Candidate GitHub Actions output is evidence only. Required local checks must bind to the exact candidate SHA. Workflow trigger coverage must include all governance-relevant paths. Mutable third-party action tags are a residual supply-chain risk and should be exact-SHA pinned.

### External checker repository

The external checker is a distinct enforcement component. It must:

- run from its own protected revision,
- expose its exact checker SHA,
- use checker-owned collection/execution logic,
- fail closed on unknown command shapes or test runners,
- reject candidate import/stdlib shadowing,
- independently pin every qualification-contributing candidate file that can alter the result,
- publish evidence under the dedicated governance GitHub App,
- bind the emitted check to both exact candidate SHA and exact checker SHA.

The checker is still evidence-producing infrastructure, not terminal authority.

### External governance root

The public trust root is stored outside the candidate repository and pinned by repository identity, repository ID, exact commit, public/archived state, trust-root ID, and public-key fingerprint. The private key remains outside all repositories. Public verification material grants no authority by itself.

### GitHub ruleset / control plane

The protected TESTING branch requires strict status checks, including the GitHub Actions local check and the dedicated governance App check. Bypass state must be empty/none according to the relevant evidence contract. The live ruleset is external platform state and must not be inferred solely from candidate files.

### Human governance authority

Human-signed governance attestations are separate from CI/reviewer/model evidence. A signature must bind the exact candidate SHA, authority class, scope, policy material, trust-root identity, and evidence reference required by the current policy. Possession of the public key is not authority; private-key possession alone is not sufficient to broaden scope beyond the signed contract.

### Independent reviewer

Independent reviewer output is evidence. Reviewer identity, transport, reviewed candidate/checker/root SHAs, and disposition must be recorded without converting model/reviewer confidence into terminal authority. `INSUFFICIENT_EVIDENCE` and `CHANGES_REQUIRED` remain preserved history even after later bounded/pass evidence.

## Dependency-closure rule

Any file whose content can materially influence qualification outcome is either:

- independently pinned by the external checker,
- checker-owned and bound to the exact checker SHA,
- platform state independently verified at use time,
- externally signed/bound according to policy,
- or explicitly classified non-material with a documented reason.

Unknown materiality is `REQUIREMENT_UNRESOLVED` and blocks qualification.

This applies recursively to imports, bridge modules, test fixtures, helper scripts, workflows, collection logic, runtime policy modules, generated manifests, and evidence parsers.

## Execution-isolation rule

Candidate qualification must not rely on ambient interpreter behavior that grants candidate-controlled paths precedence over the standard library or checker-owned code. Candidate test execution must use a checker-owned isolated path with explicit modules and fail closed on:

- stdlib/module namespace collisions,
- pytest/conftest/plugin discovery unless explicitly governed,
- implicit discovery,
- unsupported async/generator/awaitable test shapes,
- zero-test modules,
- unknown runner/command shapes,
- missing expected files,
- blob mismatches.

## Exact-SHA lifecycle

Qualification evidence is scoped to one exact candidate SHA. PR-head evidence does not automatically qualify the merge SHA. Merge successors require fresh exact-SHA local evidence, fresh exact-SHA external evidence, and fresh independent review whenever policy requires it. Stale evidence may remain historical but cannot be replayed as current qualification.

## Failure-history rule

Failures, false greens, reviewer objections, and insufficient-evidence outcomes are append-only scientific history. A later repair may supersede the current blocking status but must never erase the prior failure path or misdescribe reconstructed material as verbatim source evidence.

## Evidence vs authority

The following do not independently authorize promotion:

- green CI,
- passing unit tests,
- passing external checker,
- dedicated App check,
- reviewer PASS/BOUNDED_PASS,
- model consensus,
- signatures outside their exact allowed scope,
- archived/public repositories,
- policy labels.

Authority is separately governed by phase policy and human authority rules.

## Current R11 bounded residuals

The independent R11 reviewer classified three items as non-blocking hardening:

1. extend bridge-import execution semantics so future async/generator/awaitable bridge tests fail closed dynamically;
2. pin candidate local workflow third-party actions by exact commit SHA;
3. decide whether the external checker should independently pin/execute the candidate experiment terminal-authority test and candidate live-boundary script, or formally document why the checker-owned equivalent verification is sufficient.

These must not be silently promoted to blocking or silently ignored. Any future material change affecting them requires preregistration before mechanism repair.

## Future-change checklist

Before changing a qualification mechanism, answer all of the following in the preregistration:

- What exact exposed SHA is being falsified?
- What attack/failure path is frozen before repair?
- Which component owns the mechanism?
- Can the evaluated candidate modify that component or its inputs?
- What is the complete dependency closure?
- How is the verifier exact revision bound?
- How is the execution environment isolated?
- What negative control proves fail-closed behavior?
- What positive control proves legitimate behavior still works?
- What exact-SHA evidence is required after merge?
- What review is required, and who can adjudicate it?
- What remains evidence only and what, if anything, has terminal authority?

This checklist is intended to reduce repeated discovery of hidden trust assumptions while preserving the falsification-first process.
