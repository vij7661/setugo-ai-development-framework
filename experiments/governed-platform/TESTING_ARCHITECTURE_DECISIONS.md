# Governed Platform — Testing Architecture Decisions

Status: **Candidate architecture decisions**

These decisions complement the main architecture decision log and govern adaptive testing/verification.

## TADR-001 — Verification strategy belongs to the platform

**Decision:** The platform determines required verification layers and evidence sufficiency. Builder agents may recommend or create tests, but cannot self-certify their work.

**Why:** Allowing the implementation author to define its own sufficient evidence creates a direct false-green path.

**Consequence:** A platform-owned Verification Planner creates the frozen Verification Plan Manifest used by the evidence/release gate.

## TADR-002 — Preserve adequate project-native testing stacks by default

**Decision:** When a repository already has a healthy qualified testing framework for a required layer, use it rather than replacing it based on agent preference.

**Why:** Unnecessary framework churn increases dependencies, migration risk, maintenance cost and test-semantic drift.

**Consequence:** New frameworks are introduced only to close an evidenced verification gap or when the existing mechanism is incompatible/unhealthy. Persistent adoption may require human approval according to project policy.

## TADR-003 — Select verification layers before selecting framework brands

**Decision:** The planner first determines what properties/layers must be verified from requirements, risk and changed artifacts; it then selects eligible tools/frameworks from the Verification Tool Registry.

**Why:** Framework-driven planning can confuse tool availability with actual verification need.

**Consequence:** Unit, integration, contract, E2E, security, migration, performance, resilience, manual-QA and other layers are policy concepts independent of specific tools.

## TADR-004 — Protected acceptance evidence is outside Builder mutation scope

**Decision:** Protected acceptance tests/oracles and authoritative verification requirements cannot be changed by a Builder while implementing the production-code task they evaluate.

**Why:** Changing implementation and acceptance oracle together can manufacture a green result while violating authoritative intent.

**Consequence:** Builder-generated tests, project regression tests, protected acceptance tests and independent-verifier tests are separate evidence classes with separate mutation permissions.

## TADR-005 — Test failures require diagnosis before corrective authority

**Decision:** A failing test does not imply production code should be changed, nor that the test should be changed. The platform classifies the failure first.

**Why:** Failures can arise from code, fixtures/data, tests, environment/tooling or unresolved requirements.

**Consequence:** Corrective capability is issued only for the artifact class supported by evidence-based diagnosis. Agents cannot weaken tests/fixtures/CI merely to obtain green execution.

## TADR-006 — Test tools/frameworks are qualified mechanisms

**Decision:** Test frameworks and verifier adapters are registered and qualified by version/execution path where material; popularity alone does not qualify them.

**Why:** Result parsing, timeout behavior, reproducibility, sandbox compatibility and evidence fidelity can vary by tool/version/adapter.

**Consequence:** Verification Tool Registry records qualification evidence, epoch/expiry, supported layers, compatibility and operational status.

## TADR-007 — Green tests and coverage are evidence, not release authority

**Decision:** A green suite or high coverage number cannot independently authorize completion/release.

**Why:** Tests can be incomplete, correlated with the implementation, stale, or semantically wrong.

**Consequence:** Release requires the current Verification Plan's complete admissible evidence plus any independent review/manual gates required by policy.