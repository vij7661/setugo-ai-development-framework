# Governed Platform — Architecture Decision Log

Status: **Candidate decisions derived from current falsification evidence**

These decisions define the default product direction. A future change should record the evidence/reason for superseding a decision rather than silently drifting the architecture.

## ADR-001 — Authority remains external to models

**Decision:** Models may diagnose, recommend, request, and execute within a platform-issued scope, but they cannot mint, widen, renew, or infer consequential authority.

**Why:** Model output is probabilistic/untrusted. Authority must remain deterministic, auditable, revocable and policy-owned.

**Consequence:** Every consequential action requires platform-issued capability plus use-time validation. Model-declared scope is behavioral evidence only.

**Status:** Accepted architecture invariant; deterministic enforcement is experimental and under active falsification.

## ADR-002 — Governed sequence is explicit and ordered

**Decision:** The platform follows:

`Diagnosis → Determine permissible artifact/action → Select qualified model → Issue scoped capability → Agent executes → Independent verification evidence → Approval/regression/release gate.`

**Why:** Combining diagnosis, authority and execution in one model step allows wrong-artifact correction and self-authorization.

**Consequence:** The orchestrator owns stage transitions. Models cannot skip stages because they are confident or successful.

## ADR-003 — Modular monolith control plane first

**Decision:** Build the first product control plane as a modular monolith backed by PostgreSQL, with isolated execution workers as a separate process/security boundary.

**Why:** Governance decisions require strong transactional consistency across state, event, idempotency, policy and capability data. Premature microservices increase distributed-state failure modes without demonstrated scale need.

**Consequence:** Internal modules have explicit ownership/contracts but share a transactional database initially. Split services only for demonstrated scaling, isolation, regulatory or ownership reasons.

## ADR-004 — Workers and queues are never authoritative

**Decision:** Queue messages and worker-local state are dispatch mechanisms only.

**Why:** Delivery can duplicate, reorder or fail. A worker completion cannot safely become authoritative merely by arriving.

**Consequence:** Workers emit authenticated result/evidence events. The Governor independently decides whether authoritative state advances.

## ADR-005 — Authoritative event + idempotency + state transition are atomic

**Decision:** Accepting a consequential intent must atomically record the actor/idempotency key, append the authoritative event and advance the state version in one database transaction.

**Why:** Prevents duplicate side effects, split-brain transitions and racing writers.

**Consequence:** Use optimistic state versioning/CAS plus database uniqueness constraints. Dispatch work through a transactional outbox after commit.

## ADR-006 — Routing qualification is task- and execution-path-specific

**Decision:** Qualification binds at least provider + model + SKU + deployment/execution path + role + task class + policy/privacy context.

**Why:** Provider/model names alone do not capture routing behavior, privacy, capacity, aliasing, account/path configuration or qualification lineage.

**Consequence:** A different provider path or account path is not automatically equivalent. Failover requires its own current qualification.

## ADR-007 — Reasoning qualification and operational eligibility are separate

**Decision:** Persist model/route reasoning qualification separately from runtime availability, quota and capacity.

**Why:** Pilot 8 showed quota exhaustion can make a qualified route temporarily unusable without saying anything about reasoning quality.

**Consequence:** Routing uses both dimensions. Quota failure does not automatically revoke qualification; it changes operational eligibility.

## ADR-008 — Runtime provider/model response labels are metadata, not proof

**Decision:** Never treat provider-returned model/provider strings as cryptographic identity authority.

**Why:** Labels can be proxied, aliased, misconfigured or spoofed.

**Consequence:** Qualification depends on platform routing records and out-of-band evidence. Stronger runtime attestation is an open research/integration question.

## ADR-009 — Public benchmarks discover candidates; internal evidence qualifies them

**Decision:** External leaderboards/benchmarks may nominate candidate models but cannot directly create production routing eligibility.

**Why:** Product tasks, policies, tools, privacy and failure modes differ from public benchmark conditions.

**Consequence:** Each role/task/risk scope requires retained platform qualification evidence and expiry/requalification rules.

## ADR-010 — Evidence is retained immutably and can become stale without being erased

**Decision:** Store evidence and large artifacts by immutable content hash; maintain a tamper-evident evidence ledger.

**Why:** Later passes, policy changes or artifact changes must not erase historical failures or rewrite what was observed.

**Consequence:** Evidence lifecycle states include current/stale/revoked rather than destructive overwrite/delete. Invalidation records the causal event.

## ADR-011 — Completion/release is distinct from execution success

**Decision:** `RUN SUCCESS`, `EVIDENCE COMPLETE`, `ADJUDICATED PASS`, and `RELEASE/COMPLETE AUTHORIZED` are different states.

**Why:** Green execution only means the mechanism finished. It does not establish correctness, evidence sufficiency, or release authority.

**Consequence:** Dashboards and APIs must represent these states separately. Only an explicit release/completion gate may transition authoritative state to COMPLETE.

## ADR-012 — Review policy belongs to the platform

**Decision:** The platform determines whether R2, R3 or human review is required.

**Why:** A model should not be able to opt out of independent review because it believes its answer is correct.

**Consequence:** Risk, materiality, evidence completeness, contradiction, semantic instability, reviewer availability and policy determine escalation.

## ADR-013 — Reviewer consensus does not create authority

**Decision:** Agreement, majority, prestige, senior titles or confidence scores are evidence/context only and cannot authorize mutation, completion or release.

**Why:** Correlated models can agree and still be wrong; authority and truth are separate concepts.

**Consequence:** Convergence is governed adjudication, not majority voting. Dissent is retained when material.

## ADR-014 — Reviewer independence includes foundation lineage, not provider names alone

**Decision:** High-risk review independence must track foundation/model lineage separately from provider/deployment-path diversity.

**Why:** Different providers can expose the same or closely related underlying model family.

**Consequence:** Registry records foundation lineage, and independence policy can require distinct lineages for higher-risk review.

## ADR-015 — Memory is typed and visibility-controlled

**Decision:** Separate AUTHORITATIVE, PROJECT, WORKING, REVIEW_EVIDENCE, MODEL_PRIVATE and PROTECTED_TRUTH memory classes.

**Why:** A unified conversation/memory pool can leak protected truth, prior conclusions or private reasoning and contaminate reviewers.

**Consequence:** Context is constructed per role/stage. Model-private reasoning and protected truth are never passed as ordinary reviewer context.

## ADR-016 — Change impact invalidates evidence transitively but does not infer semantics by graph alone

**Decision:** Use dependency/impact graphs for deterministic propagation after a changed relationship is established, not as a semantic reasoning substitute.

**Why:** Graph reachability can show dependency but cannot prove natural-language semantic compatibility.

**Consequence:** Semantic analysis and authoritative change acceptance remain separate governance steps; impacted evidence is marked stale and re-verification is scheduled.

## ADR-017 — Event-driven continuation is primary

**Decision:** Trustworthy source events/webhooks/callbacks drive continuation; polling/schedules are fallback mechanisms.

**Why:** The platform cannot depend on a model/chat staying active, and polling introduces latency/repetition/race risks.

**Consequence:** Events are authenticated, deduplicated, scope-bound and state-version checked before continuation.

## ADR-018 — Secret material never becomes model context or evidence

**Decision:** Provider/tool credentials live in a dedicated secret boundary and are leased/mounted to execution workers, never included in prompts, evidence payloads or audit content.

**Why:** Model context and retained evidence have wider visibility and longer retention than credentials should.

**Consequence:** Credential references may be audited; credential values are redacted and non-retained.

## ADR-019 — Consequential execution occurs through controlled gateways

**Decision:** Repository writes, shell execution, browser/network actions, deployments and external system mutations must pass through platform-controlled gateways rather than ambient agent permissions.

**Why:** Scoped capabilities are ineffective if the model can bypass them through unrestricted tools.

**Consequence:** Sandbox/tool gateways are P0/P1 product boundaries. Each consequential call performs use-time authorization.

## ADR-020 — Unsafe model behavior is evidence even when action is blocked

**Decision:** If a model attempts to widen scope, claim release authority or report unauthorized changes, preserve the behavioral output when structurally/transport eligible while blocking its effect.

**Why:** Scrubbing unsafe attempts creates false-green evidence and prevents reviewer/model qualification from learning about authority behavior.

**Consequence:** Behavioral safety metrics and structural enforcement metrics remain separate.

## ADR-021 — Pre-registered scientific endpoints cannot be repaired by post-hoc substitution

**Decision:** For controlled experiments, provider/model/path substitutions after results are observed are not allowed into the primary endpoint unless pre-registered.

**Why:** Post-hoc substitution contaminates causal interpretation and can select favorable outcomes.

**Consequence:** Runtime-ineligible slots use frozen replacement-only policies; successful/behaviorally valid samples are retained. Different-account/path evidence is supplemental unless explicitly qualified/pre-registered.

## ADR-022 — Architecture promotion is evidence-gated

**Decision:** Experimental mechanisms become architecture-required only through deterministic invariant protection, controlled behavioral evidence, or an explicit conservative safety rationale.

**Why:** A large green test suite proves implementation consistency, not universal behavioral correctness.

**Consequence:** Architecture docs distinguish invariants, experimental mechanisms and open questions. CI success alone never promotes a behavioral hypothesis.

## ADR-023 — Coding agents are replaceable runtimes above the model layer

**Decision:** Codex, Claude Code and future coding agents are represented in an Agent Runtime Registry separate from the Model & Execution-Path Registry.

**Why:** A coding-agent product may add its own planning, terminal, repository, memory and tool orchestration and may use one or more underlying models. Treating it as merely a model name loses material execution provenance.

**Consequence:** Agent-runtime qualification is role/task-specific. When underlying model/path identity is observable and material, its qualification is checked separately. The platform may add or replace agent products without changing the governance contract.

## ADR-024 — MCP is a governed tool fabric, not an authority source

**Decision:** MCP may be used as the common tool-discovery/invocation protocol for heterogeneous agents, but every agent-facing MCP path is filtered or mediated by a platform-owned MCP Policy Gateway.

**Why:** Tool availability and authorization are different concepts. An MCP server exposing a write/deploy/delete tool must not make that action permissible merely because an agent can discover it.

**Consequence:** The platform maintains an MCP Server/Tool Catalog, task-specific MCP Tool Profiles, tool risk/side-effect classes, and use-time capability validation before consequential invocation.

## ADR-025 — Agents do not receive unrestricted ambient tool credentials

**Decision:** Agent runtimes receive scoped tool channels/profiles and references, not broad long-lived credentials for GitHub, terminal infrastructure, databases, cloud platforms or other systems.

**Why:** Direct ambient credentials would let an autonomous agent bypass capability scope and make revocation/audit incomplete.

**Consequence:** The MCP/tool gateway resolves protected secret references or short-lived leases only after use-time authorization. Credential values remain outside model context and evidence.

## ADR-026 — Concurrent coding agents use isolated workspaces

**Decision:** Parallel Builders operate on separately bound workspaces/worktrees from the same frozen base contract/SHA. They do not concurrently mutate one authoritative working tree.

**Why:** Shared mutable workspaces make provenance, race handling, rollback, comparison and independent adjudication unreliable.

**Consequence:** A platform-owned integration step compares/finalizes selected diffs, validates invariants, runs regression, and creates the next authoritative artifact/SHA. No agent self-merges its proposal into the authoritative branch.

## ADR-027 — Agent completion is operational evidence only

**Decision:** Vendor/runtime states such as Codex completed or Claude Code finished normalize to agent-result events; they never directly mean governed task COMPLETE.

**Why:** Runtime completion does not establish requirement correctness, evidence completeness, independent review, or release authority.

**Consequence:** Agent adapters emit normalized events/evidence. The Governor remains the only component that advances authoritative workflow state.
