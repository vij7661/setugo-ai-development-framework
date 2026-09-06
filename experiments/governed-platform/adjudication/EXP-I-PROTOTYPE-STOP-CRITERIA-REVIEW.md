# EXP-I Prototype Stop-Criteria Review

## Decision

**STOP AUTOMATIC SAME-HOST EXP-I PILOT EXPANSION AFTER PILOT 19.**

Pilot 19 closes the current hand-authored, same-host crash-consistency sequence unless a later systematic analysis or integration failure produces a concrete counterexample that requires an isolated reproduction pilot.

This is not a claim that EXP-I is complete, production-ready, independently certified, distributed-fault-tolerant, or Byzantine-safe. It is a decision that the next highest-value evidence should come from a different method and a broader integration surface rather than automatically creating Pilot 20.

## Evidence entering this review

- P14 through P19 have bounded-pass adjudications across root rotation, root-rotation crash consistency, isolated trusted-minimum authority, isolated recovery signing, signer crash consistency, and issuance-ledger/anti-rollback-anchor crash consistency.
- P19's exact frozen SHA `6514f9f8530c97a3d10d4027857bfdb1b8656a8a` passed every frozen P19-01..P19-16 vector explicitly in job `101552270700` and the same job concluded `Ran 1106 tests` / `OK`.
- The pilot chain has repeatedly preserved external authority, fail-closed ambiguity, exact replay identity, non-rebinding, monotonic trust state, and clean liveness after the tested crashes.
- The tested environment remains primarily same-host Ubuntu/Python/SQLite/OpenSSL with process-level isolation and software-backed keys.
- External adversarial review identified material methodological limits: program-level self-adjudication, hand-authored interleaving coverage, same-host/common-admin failure correlation, and the risk of protocol depth outpacing end-to-end product integration.
- Current budget constraints favor methods that increase evidence without requiring paid HSM infrastructure or a paid security audit at this stage.

## Stop criteria

The same-host pilot phase should stop when all of the following are true:

1. **Known local authority boundaries have bounded evidence.** The current chain covers capability/qualification foundations plus recovery/minimum/root/signer/anchor crash boundaries at the tested layer.
2. **The nearest important unknown requires a different failure model.** Remaining high-value gaps include unknown crash interleavings, independent administrative/storage domains, network partitions, malicious/Byzantine components, clock/epoch races, resource exhaustion, and end-to-end orchestration.
3. **Another hand-authored vector set would have diminishing evidentiary return.** Passing another 16 manually selected cases would not address the criticism that the missing defect may be an interleaving not anticipated by the author.
4. **Product breadth is now a material unknown.** The governance kernel has deeper evidence than the integrated operator/product workflow that must use it.
5. **Stronger claims require infrastructure not represented by the current substrate.** Same-host process isolation cannot establish independent cloud/admin trust domains, KMS/HSM custody properties, remote atomicity, or correlated-storage-failure resistance.

All five criteria are satisfied after Pilot 19.

## Exception rule

A new same-host EXP-I pilot may be opened only when at least one of these is true:

- systematic state-space exploration finds a concrete counterexample that needs implementation-level reproduction;
- integrated product testing exposes a new authority boundary that is not covered by an existing experiment;
- an independent external reviewer identifies a falsifiable local mechanism defect with a materially different endpoint;
- a previously supported bounded claim is invalidated by new evidence.

A new pilot must not be opened merely because another crash location can be imagined.

## Transition Track A — Zero-Cost Systematic State-Space / Fault Analysis

### Goal

Attack the exact methodological gap left by hand-authored vectors: unknown operation interleavings.

### First target

Model the Pilot 19 issuance-ledger / anti-rollback-anchor protocol as a small deterministic state machine and exhaustively explore bounded sequences containing:

- ledger transaction begin/insert/commit;
- anchor temporary write;
- atomic anchor replace;
- reconciliation receipt persistence;
- response loss;
- crash/restart at every transition;
- duplicate/replayed requests;
- two concurrent reconcilers;
- stale ledger substitution;
- stale anchor substitution;
- same-generation conflicting anchor material;
- recovery followed by clean next-generation issuance.

### Frozen invariants for the analysis

1. **No authority from ambiguity:** unresolved or conflicting state never authorizes trusted-minimum mutation.
2. **No ledger-only authority:** a committed ledger row without required reconciled anchor correspondence cannot authorize use.
3. **No anchor-only authority:** anchor state without exact committed ledger correspondence cannot authorize use.
4. **Monotonic trust:** accepted generation/issuance state never moves backward.
5. **No semantic rebinding:** one recovery identity never maps to two target semantics.
6. **At-most-once consequential advancement:** retries/crashes do not create two authoritative advancements for one intent.
7. **Deterministic reconciliation:** uniquely derivable divergence converges to one exact state independent of caller preference.
8. **Fail-closed conflict:** non-uniquely derivable divergence does not auto-reconcile.
9. **Liveness from safe states:** after a uniquely recoverable crash, a clean next generation can eventually advance exactly once.
10. **External authority:** model/reviewer/caller data cannot choose trusted reconciliation state.

### Method

Start with a repository-local, dependency-light exhaustive state explorer so this work can run in existing CI at zero infrastructure cost. A TLA+/TLC specification may be added as a second independent formalization if useful, but the initial deliverable must not depend on paid cloud services.

### Acceptance

- every reachable bounded state is checked against the frozen invariants;
- a counterexample is preserved with its exact transition trace before repair;
- no counterexample is dismissed by weakening an invariant;
- if a counterexample reflects the production mechanism, it becomes a diagnosis-bound implementation repair and, where necessary, an isolated reproduction experiment;
- if no counterexample is found, the result is reported only for the explored state bound/model abstraction, not as a universal proof.

## Transition Track B — Independent Evidence Review

Create an immutable evidence bundle for milestone claims containing preregistration, frozen SHA, exact workflow/job identity, relevant source/diff, test correspondence, regression total, supported claims and nonclaims.

External reviewers must receive the frozen bundle independently and must not receive another reviewer's verdict before producing their own report. Their reports are evidence inputs, not production/release authority.

At minimum, future milestone review should distinguish:

- project-internal adjudication;
- independent model review (for example Claude and DeepSeek, isolated from each other);
- human third-party security review when funding and product maturity justify it.

No model, including an external reviewer, gains authority to deploy/release merely by returning PASS.

## Transition Track C — Integrated Governed-Platform MVP

Begin proving that the governance kernel works in a real end-to-end development workflow rather than only in isolated protocol experiments.

Minimum integrated path:

`request -> diagnosis -> permissible-action decision -> task-specific model qualification -> scoped capability issuance -> Builder execution -> independent evidence collection -> Judge/reviewer verification -> governed approval gate -> retained audit/continuation state`

MVP integration should cover:

- model/provider/deployment registry and qualification evidence;
- policy and capability service;
- Builder/Judge separation;
- evidence correspondence and immutable artifact binding;
- review engine and retrieval seam without granting retrieval authority;
- failure classification and bounded repair loop;
- operator-visible status/evidence/recovery workflow;
- explicit release/deploy authority outside models.

## Transition Track D — Later Real Trust-Domain Validation

Paid infrastructure is deferred until it materially changes the evidence.

The production key requirement is:

> Production authority keys must use an externally operated hardware-backed key-management trust boundary whose properties satisfy the frozen production threat model. Dedicated HSM infrastructure is required only if managed KMS does not satisfy that threat model or an applicable compliance requirement.

Sequence when credits/resources become available:

1. managed KMS-backed authority keys;
2. genuinely separated cloud/admin identities and hosts;
3. separate storage/failure domains for witness/anchor where required;
4. network-partition and remote-retry testing;
5. only then determine whether dedicated HSM/CloudHSM is actually required;
6. paid third-party audit only at release-candidate maturity or when required by a stakeholder/compliance target.

## New risk items added by stop review

- correlated same-host/common-admin failure;
- unknown crash/recovery interleavings beyond hand-authored vectors;
- malicious/Byzantine-but-live component behavior;
- cross-host clock skew and time-bound capability TOCTOU;
- qualification/policy epoch transition while work is in flight;
- dependency/supply-chain compromise of trust-critical libraries and build inputs;
- adversarial cost/quota exhaustion of independent review paths;
- organizational/key-person bus factor;
- over-investment in protocol research before end-to-end product validation.

## Cost guardrail

No CloudHSM purchase and no paid security audit are required to continue the current roadmap. Local systematic analysis and MVP integration are the immediate work. Managed KMS / separated-domain testing should first use available free tiers, startup credits or minimal short-lived resources. Infrastructure spend is justified only by a frozen claim that cannot be tested meaningfully without it.

## Authoritative next action

**Do not create EXP-I Pilot 20 now.**

Start Transition Track A with the zero-cost systematic state-space/fault-analysis harness while preserving Pilot 19 as the terminal same-host hand-authored pilot for the current chain. In parallel, define the integrated MVP slice from Transition Track C. External independent evidence review should be applied to the next milestone bundle before stronger public/production claims.
