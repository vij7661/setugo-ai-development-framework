# Ruflo R2 Source Appendix B

Exact source excerpts/full files used by the R2 selective-adoption review.

These sources are contextual evidence only. Ruflo-declared status does not confer authority in this project.


---

# SOURCE: v3/docs/adr/ADR-327-federated-concurrent-development-harness.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `c61fa9efe8a9a3719809f1090720480f16c4b7d6`

# ADR-327: Federated Concurrent Development Harness

**Status**: Proposed — generator guidance and in-memory conformance references implemented; distributed enforcement pending  
**Date**: 2026-07-28  
**Decision owners**: Ruflo Codex, claims, policy, and developer-experience maintainers  
**Related**: ADR-320, ADR-324, ADR-325, ADR-326

## Executive decision

Ruflo will support repository-local development harnesses as adapters into its
policy-governed concurrent workflow.

The useful primitives observed in the cognitum.one website harness are adopted:

- explicit sessions;
- path and named-resource leases;
- lease heartbeats;
- agent-to-agent handoff messages;
- isolated development ports;
- test and release receipts; and
- dry-run deployment with release gates.

Those primitives are coordination evidence, not authorization. They supplement
but never replace Ruflo's stronger invariant that every writing agent uses a
distinct Git worktree.

Ruflo will define one versioned harness contract with:

- canonical repository and source-state identity;
- linearizable leases with monotonically increasing fencing tokens;
- separate authorization capabilities;
- durable, acknowledged messages;
- immutable test and release receipts; and
- compatibility adapters for existing local harnesses.

Generator and AGENTS guidance will teach Codex to discover and join a tracked
repository harness without weakening the worktree or policy rules. Distributed
lease enforcement remains proposed until the acceptance tests pass.

### Implemented reference scope

The Codex package now includes source/build evidence capture plus
`InMemoryFencedLeaseReference`, `InMemoryInboxReference`, and
`InMemoryRunReceiptReference`. These are deliberately unsigned, non-persistent,
single-process conformance/debug references:

- their descriptors are statically restricted to `observe` and `advisory`;
- legacy normalization cannot upgrade them to enforce or release authority;
- canonical uint64 parsing, length-framed inbox identity, portable
  case-collision refusal, version checks, replay convergence, and contention
  semantics are tested;
- Git-visible source state and separately declared unsigned build inputs can
  be captured and recomputed.

They do not implement a CP lease service, durable inbox/outbox, signed
hash-chained ledger, restart recovery, or release-decision composer. An
external-authority adapter satisfying the normative sections below remains
required for enforcement and release.

## Current-state audit

The cognitum.one website harness currently provides a practical, file-backed
coordination layer:

- a mutex plus atomic rename protects local JSON lease updates;
- path claims reject option-like scope values and overlapping ancestors or
  descendants;
- named resource claims cover deployment and shared services;
- heartbeats, not PIDs, represent lease liveness;
- sessions carry inbox messages and development ports;
- test receipts bind a command, scope, result, and Git SHA;
- deployment is dry-run by default and checks release receipts.

This is useful local coordination, but the live audit found:

- multiple writing agents share one dirty website worktree;
- a receipt that records only `HEAD` cannot identify which dirty source state
  was tested;
- ignored JSON sessions, leases, messages, and receipts are mutable and
  unsigned;
- any local process can impersonate a session or alter coordination state;
- leases have no fencing token, so an expired writer cannot be rejected by a
  protected side effect;
- liveness is not bound to repository, worktree, branch, host, or workload
  identity;
- the inbox keeps a bounded tail rather than a durable acknowledged stream;
- an eight-hour TTL can retain stale ownership for a long period; and
- the local mutex cannot coordinate multiple hosts.

The harness correctly treats a missing PID as insufficient proof of death.
Lease expiry and heartbeat are the right liveness abstraction, but production
concurrency requires fencing and exact source-state receipts.

## Security and correctness invariants

1. Every writing agent has a distinct Git worktree.
2. A path lease prevents overlapping intent; it does not make shared dirty
   state safe.
3. A repository lease coordinates ownership; it does not grant authorization.
4. A session identity is not a workload identity or product capability.
5. Every successful lease acquisition returns a monotonically increasing
   fencing token.
6. Protected writes reject a stale fencing token after expiry, release, steal,
   or reacquisition.
7. `HEAD` alone is not an exact source-state identity when a worktree is dirty.
8. Test, release, and deployment receipts bind the exact source state.
9. Message delivery is durable and idempotent; reading a bounded tail is not
   acknowledgement.
10. Harness unavailability may stop protected mutation but never silently
    expand authority.

## Decision

### 1. Define a repository harness adapter

Ruflo discovers a harness only through tracked repository configuration:

```ts
interface RepositoryHarnessAdapter {
  describe(): Promise<HarnessDescriptor>;
  start(request: StartSessionRequest): Promise<HarnessSession>;
  acquire(request: LeaseRequest): Promise<FencedLease>;
  renew(lease: FencedLease): Promise<FencedLease>;
  release(lease: FencedLease): Promise<void>;
  send(message: HarnessMessage): Promise<MessageReceipt>;
  receive(cursor?: string): AsyncIterable<HarnessMessage>;
  acknowledge(messageId: string): Promise<void>;
  recordRun(run: RunEvidence): Promise<RunReceipt>;
  authorizeRelease(request: ReleaseRequest): Promise<ReleaseDecision>;
  end(sessionId: string): Promise<void>;
}
```

Repository scripts remain the preferred local user interface. Ruflo does not
replace a project's custom harness or invent commands. The adapter reads its
declared capabilities and invokes only supported operations.

If no tracked harness exists, Ruflo uses its local claims and policy providers.
If an explicitly selected harness is unavailable, protected operations fail
closed.

### 2. Retain one worktree per writer

The parent agent creates or assigns a distinct worktree before a writing worker
acquires paths. A lease then provides fine-grained ownership inside that
worktree and across agents:

```text
isolated worktree
  + non-overlapping path/resource lease
  + narrow authorization capability
  + current fencing token
  = eligible protected write
```

Read-only agents may share a checkout if they acquire no writing lease. One
designated integration agent owns shared manifests and lockfiles.

Legacy shared-worktree harnesses remain observable in compatibility mode, but
Ruflo does not describe them as isolated or receipt-complete. Their dirty
source state cannot authorize release.

### 3. Canonically identify repository and source state

A repository identity binds at least:

```ts
interface RepositoryIdentity {
  repositoryId: string;
  canonicalRemote?: string;
  gitCommonDirId: string;
  rootTreeId: string;
}
```

Paths are repository-relative, Unicode-normalized, separator-normalized, free
of `.` and `..`, checked after symlink resolution, and compared with the
platform's case behavior. Option-like values are rejected.

The preferred source state is a clean, committed worktree:

```text
SourceStateID = sha256(repositoryId || commit || tree)
```

When a local test intentionally covers uncommitted work, the receipt also
binds:

- the base commit;
- the binary-safe tracked patch digest;
- an untracked file manifest with mode, length, and content digest;
- submodule and large-file pointer state;
- generator inputs and relevant lockfile digests.

Such a local receipt may support debugging. A release receipt still requires a
clean committed state unless a project policy explicitly defines an equally
strong immutable snapshot mechanism.

### 4. Use CP leases and fencing tokens

The lease authority performs compare-and-swap transactions:

```ts
interface FencedLease {
  leaseId: string;
  repositoryId: string;
  sessionId: string;
  ownerWorkloadId: string;
  worktreeId: string;
  kind: 'path' | 'resource';
  scopes: string[];
  epoch: bigint;
  version: bigint;
  issuedAt: string;
  expiresAt: string;
}
```

Acquire, renew, release, and steal validate the expected version and current
owner. Every successful new ownership period increments `epoch`, including
reacquisition by the same session.

Filesystem adapters provide single-host compatibility. Distributed workflows
use a linearizable authority. Protected integrations, deployment drivers, and
shared generators compare the presented epoch with the authority before a side
effect. An old holder cannot continue merely because it still has local files.

Heartbeat proves current lease intent; PID is diagnostic only. A long-running
operation uses bounded renewable leases and cannot declare a mutex stale solely
because a fixed wall-clock duration elapsed.

### 5. Keep leases and authorization separate

A lease answers, "which worker currently owns this coordination scope?" A
grant answers, "may this identity perform this action?"

The ADR-324/325 decision request includes both:

```text
subject and workload identity
repository and source state
action and exact resource
lease ID, scope, epoch, and expiry
authorization grant
budget/concurrency/delegation envelope
policy version
```

No lease, session, message, test result, or agent role can synthesize a
deployment, network, spend, secret, administrative, or product capability.

### 6. Make messages durable

Harness messages use stable IDs, issuer and audience, correlation and causation
IDs, sequence, expiry, content digest, and acknowledgement state.

Delivery is at least once. The receiver deduplicates by issuer, message ID, and
content digest. A repeated ID with different content is quarantined. A bounded
UI view may show the most recent messages, but durable storage retains
unacknowledged handoffs and supports cursor resume.

Messages communicate observations, requests, conflicts, and handoffs. They do
not transfer path ownership or authority unless the corresponding lease or
grant transaction separately succeeds.

### 7. Bind run, release, and deployment receipts

A run receipt includes:

```ts
interface HarnessRunReceipt {
  receiptId: string;
  repositoryId: string;
  sourceStateId: string;
  sessionId: string;
  workloadId: string;
  commandDigest: string;
  scope: string;
  profile: 'focused' | 'integration' | 'release';
  startedAt: string;
  completedAt: string;
  exitCode: number;
  evidenceDigest: string;
  policyReceiptId: string;
  leaseEpochs: Record<string, string>;
}
```

Receipts are recursively canonicalized, content-addressed, signed, and
append-only. Retrying a command creates another execution ID; it does not
rewrite history.

A release decision requires:

- an allowed policy decision;
- a clean exact source state matching the candidate release;
- all project-required run profiles passing for that same state;
- valid leases and current fencing epochs for integration and release scopes;
- artifact and provenance digests;
- an authorized release capability; and
- no unresolved higher-priority refusal or stale dependency.

Deploy remains dry-run unless the user and policy authorize execution. A
passing run receipt is evidence, not deployment authority.

### 8. Federate across repositories through handoffs

Cross-repository work uses explicit producer and receiver ownership:

```text
producer commit and evidence
  -> signed handoff referencing exact source state
  -> receiver acknowledges
  -> receiver acquires its own local paths and capability
  -> receiver implements and verifies its side
```

One agent does not write into another dirty repository merely because both
participate in the same swarm. Contract changes identify the receiving owner,
compatibility window, and validation evidence.

This is especially important for Cognitum website to Meta-LLM structured
output, Cog release provenance, Comms event delivery, and RuView edge contracts.

## Codex workflow integration

Generated AGENTS guidance follows ADR-329's complete implementation loop:
recall, inspect, route, plan, execute, test, validate, benchmark, optimize,
receipt, handoff, and independently authorized publish. Harness-specific
actions occur inside that loop:

1. assign one worktree to each writer during routing;
2. start the tracked harness, inspect claims, and acquire exact scopes during
   planning;
3. renew leases and check acknowledged inbox messages during execution;
4. bind focused/integration results to exact source/build inputs during
   validation and receipt;
5. release claims and reconcile handoffs before the integration owner evaluates
   an external-authority release decision.

Ruflo coordinates this flow. Codex still performs the implementation and
verification work.

## Compatibility and migration

1. Existing repository harness commands and JSON schemas remain unchanged.
2. Ruflo first uses an `observe` adapter that imports session, lease, message,
   port, and run evidence without authorizing privileged actions.
3. Existing path leases map to epoch `0` and are advisory. They cannot
   authorize release.
4. New adapters dual-write durable lease and receipt records while projects
   retain their local UI.
5. Projects move to `enforce` only after writers use isolated worktrees,
   protected resources validate fencing tokens, and exact-source receipts pass.
6. Older Ruflo installations ignore the new optional adapter and retain local
   behavior.
7. Removing the adapter never grants broader access; protected federated
   operations become unavailable.

## Normative acceptance tests

1. One hundred concurrent acquisitions of the same scope produce one owner and
   one current epoch.
2. A stale writer is rejected after lease expiry and reacquisition.
3. Renew and release with an old version or epoch are rejected.
4. Ancestor, descendant, symlink, case, separator, Unicode, traversal, and
   option-like path collisions are detected.
5. The same relative path in two different repositories does not collide.
6. Two writing agents are refused when configured to use one worktree.
7. A clean commit and a dirty worktree at the same `HEAD` produce different
   source-state identities.
8. A one-byte tracked or untracked change invalidates the run receipt.
9. A message reconnect resumes without loss; replay produces no duplicate
   side effect.
10. A message ID paired with different content is quarantined.
11. A lease holder without an action grant cannot deploy, spend, access a
    secret, or mutate an external product.
12. A grant holder without the current lease epoch cannot mutate a protected
    coordination scope.
13. Fault injection at every lease, receipt, inbox, and outbox boundary
    recovers to one valid state.
14. A release attempt using passing tests from a different source state is
    rejected.
15. A passing test receipt without release authority remains dry-run.
16. A cross-repository handoff cannot modify the receiver until its local owner
    acknowledges and acquires the target scope.
17. Local single-agent workflows behave as before when no harness adapter is
    configured.

## Consequences

### Positive

- Ruflo can cooperate with existing repository harnesses instead of replacing
  them.
- Worktree isolation and fine-grained leases cover different failure modes.
- Fencing prevents stale workers from affecting protected resources.
- Test and release evidence becomes attributable to exact source.
- Cross-repository work has an explicit receiving owner.

### Negative

- Protected local writes need an enforcement hook to validate fencing tokens.
- Exact dirty-state hashing is more expensive than recording `HEAD`.
- Multi-host coordination requires a linearizable service.
- Legacy shared-worktree sessions remain advisory until migrated.

## Review trigger

Review this ADR when Git changes its worktree identity model, a repository
harness adds distributed leases, Ruflo supports a new source-control system, or
production evidence demonstrates a different lease or receipt requirement.


---

# SOURCE: v3/docs/adr/ADR-329-ruflo-capability-brain-mcp-guidance.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `89095e3fd9b2917974dee00bf1c884d0b2d0d6d6`

# ADR-329: Ruflo Capability Brain for MCP Guidance

**Status:** Accepted  
**Date:** 2026-07-28  
**Owners:** Ruflo CLI, Guidance, Security, and Release Maintainers  
**Related:** ADR-150, ADR-176, ADR-320, ADR-322, ADR-324, ADR-325, ADR-327, ADR-328

## Context

Ruflo exposes a broad system through MCP tools, CLI commands, agents, skills,
packages, and plugins. The previous guidance catalog described 16 hand-written
areas and referenced 99 tool names. An audit of the current server found:

- 353 unique live tools when the optional raw-browser runtime is installed;
- 330 always-registered tools without that conditional runtime;
- only 61 of the 353 live tools referenced by the old catalog;
- 292 live tools omitted from that catalog;
- 38 catalog references that no longer resolve to live tool names;
- one exported `testgen_tdd_repair` tool that is not registered by the MCP
  client;
- plugin skills, `.agents/skills`, package ownership, plugin ownership,
  authority, risk, degraded behavior, and implementation-loop placement absent
  from discovery.

This created two failures. Users could not discover most of Ruflo, and agents
could mistake catalog text or MCP registration for proof that a provider was
configured, reachable, healthy, and authorized.

## Decision

Ruflo will ship a capability brain behind `guidance_brain` and enhance the
existing guidance tools without removing their compatibility surface.

The brain is generated from the completed live MCP registry. A static domain
definition supplies semantics; it does not supply runtime presence. The MCP
client injects its registry into guidance after all conditional and filtered
tools have been registered. This avoids a circular import and makes silent
catalog drift testable.

### Truth model

Every domain reports these facts independently:

| Fact | Meaning |
|---|---|
| `catalogued` | This Ruflo version describes the capability. |
| `registered` | The tool exists in this MCP process. |
| `configured` | Required settings/providers are present. |
| `reachable` | A non-mutating dependency probe succeeds. |
| `healthy` | The dependency satisfies its health contract. |
| `authorized` | Current subject may perform the exact action on the resource. |

Only `registered` can be derived from the MCP registry. The other dimensions
remain `unknown` until their dedicated adapters evaluate them. No single
“available” badge may collapse these dimensions.

### Complete capability surface

`guidance_brain` exposes:

1. every live registered MCP tool, assigned exactly once;
2. domain, owner, maturity, authority, risk flags, side-effect class,
   availability mode, implementation-loop phases, and verification guidance;
3. all 52 top-level CLI commands;
4. installed agents and skills from `.claude`, `.agents`, and plugin roots;
5. package and plugin manifests;
6. coverage gaps, duplicates, and fallback classifications;
7. task recommendations filtered to tools actually registered in this process.

The major domains deliberately distinguish:

- policy authorization from exclusive work claims;
- AIDefence content-safety evidence from authorization;
- memory recall from validated memory commit;
- MetaHarness/Darwin/Flywheel evaluation from promotion;
- consensus from authority;
- worktree leases from product or release authority;
- local/runtime capabilities from network and external-service actions.

The compatibility `guidance_capabilities` response remains available, but its
old string catalog is labeled compatibility-only and each legacy reference is
marked registered or unregistered. New routing consumes the live brain.

### Identity and OAuth guidance

The brain includes Ruflo's implemented Cognitum identity lifecycle from
[ADR-306](ADR-306-cognitum-authentication-account-linking.md) as a distinct
control-plane domain:

- `ruflo auth login` uses loopback PKCE on an interactive desktop;
- `ruflo auth login --no-browser` uses the implemented OOB/manual-paste flow;
- noninteractive login refuses unless `--token-stdin` is explicit;
- `ruflo auth status` is offline-safe, while `--check` may perform
  demand-driven keychain refresh;
- scopes remain bound to local consent receipts; `account.create` does not
  imply hosted memory, routing, telemetry, deployment, IAM, or billing;
- local logout clears session/profile/keychain state but does not claim
  server-side revocation, because the currently proven identity surface does
  not expose that operation.

RFC 8628 polling, a new Ruflo-specific OAuth client registration, automatic
existing-install prompts, and hosted memory/device-flow contracts remain
upstream work. Guidance must report those as unavailable rather than inventing
endpoints or silently broadening scope. Authenticated identity is still
independent of service configuration, reachability, health, and action
authorization.

### Capability metadata

The v1 brain uses domain-derived metadata for tools:

```text
name
domain
packageOwner
pluginOwner
availabilityMode
authority
risk
riskFlags
loopPhases
health.registered
health.configured
health.reachable
health.healthy
health.authorized
```

Availability modes are `always-local`, `conditional-registration`,
`registered-degraded`, `configured-remote`, and `policy-filtered`.

Risk flags cover read, local write, memory poisoning, process execution,
network, credentials/PII, spending, concurrency, destructive actions,
approval, and promotion. V1 supplies conservative domain defaults. A future
generated per-tool descriptor may narrow those defaults, but may never
silently lower risk.

### Normative implementation loop

Guidance recommendations and generated `AGENTS.md` files use this loop:

1. **Recall** prior memory and ADR constraints.
2. **Inspect** source, runtime, dependency, policy, and health state.
3. **Route** to the smallest capable topology, agents, skills, and tools.
4. **Plan** acceptance criteria, safety envelope, ownership, and validation.
5. **Execute** in isolated scopes; Ruflo coordinates while an executor works.
6. **Test** focused, regression, and failure paths.
7. **Validate** types, security, policy, compatibility, and artifact integrity.
8. **Benchmark** a source-bound candidate against a source-bound baseline.
9. **Optimize** only measured bottlenecks without weakening safety.
10. **Receipt** claims and evidence against exact source/build inputs.
11. **Handoff** and reconcile concurrent ownership and limitations.
12. **Publish** only through a separately authorized release gate.

Self-learning follows `recall → propose/branch → evaluate/critique →
commit-validated`. A memory or policy mutation requires a content digest and
validation receipt. No memory, neural, MetaHarness, Darwin, Flywheel, claims,
or consensus tool may authorize its own promotion.

## MCP contract

`guidance_brain` supports:

| Mode | Result |
|---|---|
| `overview` | Truth model, coverage, commands, registered domains, loop |
| `capabilities` | Full domain/tool descriptors, optionally one domain |
| `coverage` | Exact tool-to-domain assignments and gaps |
| `ecosystem` | Agents, skills, plugins, packages, and commands |
| `recommend` | Task-ranked live capabilities and guarded loop |
| `implementation-loop` | Normative stages, evidence, mutation class, invariants |

`guidance_discover` also discovers agents, skills, plugins, and packages.

## Backward compatibility

- The five existing guidance tool names and input modes remain.
- `guidance_brain` is additive.
- The old catalog is retained as an explicitly deprecated compatibility view.
- Conditional browser registration remains conditional.
- Optional packages remain registered-degraded where their handlers already
  implement that contract.
- Policy administration remains absent from remote MCP; only evaluation and
  status are registered.
- `testgen_tdd_repair` is catalogued but honestly reports unregistered until a
  separate decision registers it.

## Security and authority invariants

1. Registration never implies configuration, health, or authorization.
2. Recommendation is advisory and cannot invoke a tool.
3. A work claim cannot grant product, network, billing, IAM, or release access.
4. A score, signature, receipt, consensus vote, or memory does not authorize
   itself.
5. A degraded or fallback evaluator cannot promote unless an independent
   policy explicitly permits that exact substitution.
6. External writes, spending, destructive actions, credentials/PII, and
   promotion require explicit risk and approval handling.
7. Publication binds immutable artifacts to exact source/build evidence.

## Validation

Acceptance tests must prove:

1. every live registered tool is assigned exactly once;
2. no duplicate live tool names exist;
3. fallback classifications are reported and fail the repository coverage
   gate until assigned;
4. a catalogued but unregistered capability reports `registered: false`;
5. the five health/authority dimensions remain independent;
6. every recommendation returns the complete implementation loop;
7. publication is the final external-mutation stage and requires independent
   authorization;
8. filesystem discovery covers `.claude`, `.agents`, packages, and plugins;
9. missing optional providers remain degraded/unknown, not “available”;
10. policy authorization, work claims, and content safety remain separate.

The initial implementation classifies all 353 tools observed on Node 22/Linux
with the browser runtime installed, with no fallback classifications or
duplicates. This count is an environment observation, not a fixed protocol
constant; the coverage invariant is percentage and exact assignment.

## Performance budget

Brain construction and recommendation are local metadata operations. The
benchmark profile must measure the maximum live registry, report median and
tail latency, and fail if a future catalog change introduces an accidental
network call or tool execution. Filesystem ecosystem discovery is measured
separately because it performs bounded local I/O.

## Consequences

Users and agents can now ask Ruflo what it can actually do, receive safe
workflow guidance, and see capability gaps without reading hundreds of source
files. The cost is a maintained semantic domain map and mandatory coverage
tests. Service-specific health and authorization probes remain adapter work;
the brain exposes those unknowns instead of inventing a positive answer.


---

# SOURCE: v3/docs/adr/ADR-352-mcp-tool-permission-attestation.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `a226e7cbff444ab9ef0fa4cab6e88f46827072e2`

# ADR-352: MCP Tool Permission Attestation (Min-Privilege Contract)

- **Status**: Proposed
- **Authors**: claude (dream-cycle agent, 2026-06-26)
- **Date**: 2026-06-26
- **Dream Cycle Issue**: TBD (filed same night)

---

## Context

The 2026-06-26 Dream Cycle SOTA sweep surfaced two converging evidence streams that identify MCP tool-call boundaries as the primary unguarded attack surface in LLM agent systems:

1. **ShareLock (arXiv 2026, Grade A)** — Achieves >90% poisoning ASR on MCP-connected agents via Shamir's threshold scheme distributed across multiple benign-looking tool servers. The attack exploits the absence of tool-level permission declarations: any server can inject arbitrary behaviour if the agent does not enforce a privilege contract at dispatch time.

2. **ToolPrivBench (arXiv 2026, Grade A)** — 64.9% of Qwen3-8B tool calls escalate to higher-privilege tools than the task requires (OPUR metric). Post-training with privilege-aware objectives reduces OPUR to 27.02%. The benchmark formalises 544 scenarios across 8 domains and 5 risk patterns.

3. **ControlPlane paper (arXiv 2026, Grade A)** — Fewer than 1% of coding agents declare explicit permission boundaries, making over-privilege the default posture.

Ruflo's current security module (`@claude-flow/security`) provides `SafeExecutor` (command injection), `InputValidator` (Zod), and `PathValidator` (traversal). None operate at the MCP tool registration or dispatch layer. Tool calls are forwarded without a declared min-privilege contract.

---

## Decision

Introduce a **MCP Tool Permission Attestation** layer with two integration points:

### 1. Tool Registration Contract

Every MCP tool registration (server-side and client-side stub) must carry a `permissions` manifest:

```typescript
interface ToolPermissionContract {
  toolName: string;
  minPrivilege: {
    filesystem?: 'none' | 'read' | 'write' | 'execute';
    network?: 'none' | 'outbound' | 'inbound' | 'full';
    process?: 'none' | 'spawn' | 'kill';
    memory?: 'none' | 'read' | 'write';
    agentScope?: 'none' | 'self' | 'team' | 'global';
  };
  declaredAt: string;   // ISO date of contract signature
  trustLevel: 'official' | 'community' | 'unverified';
}
```

Tools without a `permissions` field are assigned `trustLevel: 'unverified'` and routed through a stricter sandbox.

### 2. Dispatch-Time Enforcement

`SafeExecutor` is extended with a `McpPermissionGuard` that runs before every tool dispatch:

```
Request → McpPermissionGuard → {
  if call.escalatesAbove(tool.minPrivilege) → REJECT (log + alert)
  if tool.trustLevel === 'unverified' && call.privilege > 'read' → BLOCK
  else → forward to SafeExecutor → execute
}
```

Rejection emits a structured event to the security audit log; repeated escalation triggers a circuit-breaker (ADR-097 pattern).

---

## Target Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| OPUR (over-privilege usage rate) | ~64.9% (ToolPrivBench Qwen3-8B baseline) | ≤ 30% |
| ShareLock-style poisoning ASR | >90% (no defence) | < 10% |
| Tools with declared contracts | 0% | 100% of official tools; ≥ 80% of community tools |

---

## Consequences

**Positive:**
- Closes the primary attack vector identified by ShareLock
- Provides a measurable ToolPrivBench-equivalent baseline for continuous monitoring
- Composable with ADR-093 (MCP audit) and ADR-131 (tool output guardrail)

**Negative / Risk:**
- Breaking change for tool servers that currently omit `permissions` — requires migration period
- OPUR measurement requires a ToolPrivBench-compatible evaluation harness (new test infrastructure)
- Unverified tools silently downgraded to read-only scope — may surprise plugin authors

## Alternatives Considered

- **Prompt-level privilege hints only** (rejected): Relies on model compliance; ToolPrivBench shows models ignore prompts under tool-failure pressure
- **Runtime syscall tracing** (deferred): Effective but requires platform-specific instrumentation; out of scope for v3.7 timeframe
- **Output-only guardrail** (existing ADR-131/146): Insufficient — output sanitisation does not prevent the upstream tool invocation

## References

- ShareLock: arXiv 2026 (MCP threshold poisoning, >90% ASR)
- ToolPrivBench: arXiv 2026 (64.9% OPUR baseline, 27.02% post-training)
- ControlPlane: arXiv 2026 (<1% agents declare permission boundaries)
- ADR-092: MCP tool validation bugfixes
- ADR-093: MCP audit May 2026 remediation
- ADR-097: Federation budget circuit-breaker (reused pattern)
- ADR-131/146: Tool output guardrail


---

# SOURCE: v3/docs/adr/ADR-145-plugin-supply-chain-integrity-memory-governance.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `d0e98af91ff3cae481cc9c4bc8d10718cea16f62`

# ADR-145 — Plugin Supply-Chain Integrity and Memory Namespace Governance

**Status**: Proposed
**Date**: 2026-06-02
**Issue**: [ruvnet/ruflo#2254](https://github.com/ruvnet/ruflo/issues/2254)
**Related**: ADR-004 (Plugin Architecture), ADR-006 (Unified Memory), ADR-015 (Unified Plugin System), ADR-131 (ToolOutputGuardrail — content layer), ADR-144 (Authorization Propagation — runtime layer)

## Context

ADR-131 closed the content boundary and ADR-144 closes the runtime action boundary. Both assume the *code that's about to run* is trustworthy in the first place. Two Grade A papers published April–May 2026 demonstrate that assumption is broken under current Ruflo defenses.

### Threat: plugin supply-chain attacks

**Semantic Compliance Hijacking — SCH** (arXiv:2605.14460, May 14, 2026, Grade A): Eliminates the recognizable payload entirely. Instead of injecting malicious code, SCH wraps malicious intent in natural-language "compliance rule" text within plugin descriptions. The LLM agent reads the rule and **generates the harmful code itself at runtime**. Benchmark: **77.67% confidentiality breach, 67.33% RCE success, 0.00% scanner detection**. Signature-based defenses are completely blind because there is no static payload to sign against.

**DDIPE** (arXiv:2604.03081, Apr 3, 2026, Grade A): Document-Driven Implicit Payload Execution embeds malicious logic in plugin documentation and configuration templates. Tested across 4 frameworks, 5 models, 1,070 adversarial skills covering 15 MITRE ATT&CK categories. **Bypass rate 11.6–33.5%; 2.5% of adversarial skills evade both detection and alignment systems.** Four CVEs were disclosed from this research.

Ruflo's current plugin install path (`v3/@claude-flow/cli/src/plugins/store/discovery.ts`) fetches manifests from IPFS via Pinata. It carries **no signature verification** and **no semantic intent analysis**.

### Threat: memory-namespace poisoning

**MINJA** (arXiv:2601.05504, Jan 2026, Grade A): Query-only memory injection achieves **95% success under idealized conditions; 28–38% on production-deployed strong models**. The realistic-production number is still unacceptable for a system where compromised memory steers future agent behavior.

**Plan Injection** (arXiv:2506.17318, Jun 2026, Grade A): Context-chained memory attacks achieve **3× higher attack success** than prompt-based injection and **+17.7% exfiltration gain** by creating logical bridges between unrelated memory entries. The fix is **namespace isolation with explicit write grants** — agents cannot poison a namespace they have no business writing to.

**Mnemonic Sovereignty survey** (arXiv:2604.16548, Apr 2026, Grade A): Catalogs nine governance primitives required for secure long-term agent memory. No existing published architecture satisfies all nine. The Ruflo gap: the shared `collaboration` namespace (and all AgentDB namespaces) accepts writes from any agent with no per-namespace authorization. ADR-131 catches *what gets read out*; this ADR catches *who is allowed to write in*.

### Why this is architectural

Distinct from existing security ADRs:

| Layer | ADR | Concern |
|---|---|---|
| Install-time integrity | **this ADR (Part A)** | Is the plugin code trustworthy enough to load? |
| Memory write authority | **this ADR (Part B)** | Is this agent allowed to write to this namespace? |
| Runtime action authority | ADR-144 | Is this agent allowed to call this tool right now? |
| Tool/memory output content | ADR-131 | Does this content contain hijacking instructions? |

ADR-145 introduces two new trust boundaries, two new module surfaces, a protocol addition to the IPFS plugin registry manifest format, and an API addition to AgentDB. All four are architectural.

## Decision

### Part A — `PluginIntegrityVerifier`

Add `PluginIntegrityVerifier` to `@claude-flow/security` with two verification stages run at `plugins install` time.

**Stage 1 — Signature verification** (blocks DDIPE's static-payload variants):

- Every plugin published to the IPFS registry MUST carry a detached **Ed25519 signature** over its manifest hash. The signature lives alongside the manifest in IPFS; the registry index records the signing key's fingerprint.
- `discovery.ts` MUST refuse to install unsigned plugins when `CLAUDE_FLOW_STRICT_PLUGINS=true` (default: warn-only for backwards compatibility).
- Trust anchors (publisher keys we vouch for) live in `v3/@claude-flow/cli/src/plugins/trust/trust-anchors.json`. Edits are gated on CODEOWNERS review.

**Stage 2 — Semantic intent scan** (blocks SCH):

- During `plugins install`, the verifier pipes every natural-language field (description, README excerpt, "compliance rules", any field that ends up in agent context) through a lightweight intent classifier.
- The classifier scores against a taxonomy of malicious-intent categories: credential exfiltration, RCE, data poisoning, privilege escalation, persistence.
- Install blocks if confidence exceeds `CLAUDE_FLOW_PLUGIN_SCH_THRESHOLD` (default `0.8`).
- Fallback: LLM-free pattern rules covering the top-5 SCH families from arXiv:2605.14460 (Table 3 of the paper). The pattern fallback is what makes this safe to run during `plugins install` in environments without LLM credentials.

**Implementation targets**:
- `v3/@claude-flow/security/src/plugins/integrity-verifier.ts` (new)
- `v3/@claude-flow/cli/src/plugins/store/discovery.ts` — verification hook on install
- `v3/@claude-flow/cli/src/plugins/trust/trust-anchors.json` (new)

### Part B — Memory namespace write ACLs

Address governance primitives 1–3 from the Mnemonic Sovereignty taxonomy (write authorization, read authorization, update authorization). Primitives 4–9 (retention, decay, audit, etc.) deferred for a future ADR.

- Every agent spawn receives an explicit `writeNamespaces: string[]` grant.
- AgentDB enforces grants at the storage boundary — **not** by convention in the calling code.
- Agents not in the grant list for a namespace receive `MemoryWriteDenied` on write attempt.
- Read access remains open by default (read-time poisoning is caught at ADR-131's guardrail layer).
- A `readNamespaces` grant is *optional* in v1 and becomes required in v4 (matching the strict-mode escalation in ADR-144).

**Implementation targets**:
- `v3/@claude-flow/memory/src/namespaces/authorization.ts` (new)
- `v3/@claude-flow/memory/src/agent-db.ts` — grant enforcement
- `v3/@claude-flow/cli/src/agent/spawn.ts` — `writeNamespaces` parameter

### Integration plan (phased — P1 is the first PR)

| Phase | Scope | Where |
|---|---|---|
| **P1** | `PluginIntegrityVerifier` skeleton + Stage-1 signature path; trust-anchors file with the existing official-plugin keys | `@claude-flow/security/src/plugins/`, `@claude-flow/cli/src/plugins/trust/` |
| P2 | Stage-2 semantic scan (pattern fallback first, classifier opt-in) | same files |
| P3 | Memory namespace ACL primitives 1–3 in AgentDB | `@claude-flow/memory/src/namespaces/` |
| P4 | `agent spawn --write-namespaces` plumbing through every spawn callsite | `@claude-flow/cli/src/agent/spawn.ts`, hooks |
| P5 | Strict-mode flips to default in v4.0; legacy mode requires explicit env var to re-enable | release docs + breaking-change ADR |

### Backwards compatibility

- Plugin verification defaults to **warn-only** (`CLAUDE_FLOW_STRICT_PLUGINS=false`). Existing unsigned plugins continue to install with a warning.
- Memory namespace ACLs are **additive**: agents spawned without `writeNamespaces` retain legacy full-access until `CLAUDE_FLOW_STRICT_MEMORY=true` is set.
- Both strict modes become default in v4.0.0. The next-major release will be the breaking change.
- The two new env vars are documented escape hatches and MUST be registered in `audit-env-var-precedence.mjs` with rationale.

## Alternatives considered

**Pattern-matching SCH at content boundary (ADR-131 extension).** SCH attacks succeed against content screening because the malicious content *is* the description — there's no instruction-shaped hijack to match. Catching it requires semantic intent classification at install, before the description ever enters agent context.

**Per-plugin sandboxing instead of signing.** Process-level sandboxing buys defense-in-depth but doesn't solve SCH: the malicious behavior is generated by the host model, not by sandboxed plugin code. Signing addresses the trust question; sandboxing addresses the blast-radius question — both belong on the roadmap, but signing closes the more urgent gap.

**Skip Part B; rely on ADR-131 for memory.** ADR-131 catches read-side injection. Plan Injection (arXiv:2506.17318) shows that allowing arbitrary writes lets attackers stage payloads that look innocuous individually but compose into a hijack across multiple reads — content screening cannot catch that compositional pattern. Write authorization is the missing piece.

## Consequences

**Positive**:
- Closes the **77.67% breach / 0.00% detection** SCH gap (arXiv:2605.14460) at the semantic layer.
- Closes DDIPE static-payload variants via Stage-1 signature check.
- Reduces memory-poisoning propagation across agent boundaries (write ACLs are the only mechanism that scales with namespace count).
- Positions Ruflo's memory governance ahead of every 2026 competitor surveyed — none satisfy more than 4 of the 9 Mnemonic Sovereignty primitives.

**Negative / risks**:
- Plugin publishers must generate Ed25519 keypairs and sign manifests (new workflow). The ruflo-plugin-creator skill MUST be updated to scaffold the signing step.
- Semantic intent scan adds **~50–200 ms** to `plugins install` — acceptable at install time, would be unacceptable at runtime.
- Write-ACL migration requires updating every existing `agent_spawn` callsite that uses shared namespaces. Existing pipelines fail open in legacy mode until v4.

**Telemetry / observability**:
- Each verification decision (`pass`, `signature-missing`, `signature-invalid`, `sch-blocked`) MUST be logged with plugin id, publisher fingerprint, and category.
- Each `MemoryWriteDenied` MUST be logged with agent id, namespace, and the granted-namespaces set at spawn time.
- Both feed the security dashboard as adoption metrics.

## Validation

P1 lands with:
- Unit tests covering signature verification against the existing official-plugin keys (round-trip sign → verify; tamper-flips fail).
- Smoke test: `plugins install ./unsigned-plugin` warns by default, errors under `CLAUDE_FLOW_STRICT_PLUGINS=true`.
- Pattern-fallback test corpus drawn from arXiv:2605.14460's Table 3 examples.
- Integration test: agent spawned with `writeNamespaces: ['a']` cannot `memory_store` to namespace `b` under strict-memory mode; legacy mode allows it with a warning log.

## References

- arXiv:2605.14460 — *Exploiting LLM Agent Supply Chains via Payload-less Skills* (SCH)
- arXiv:2604.03081 — *Supply-Chain Poisoning Attacks Against LLM Coding Agent Skill Ecosystems* (DDIPE)
- arXiv:2601.05504 — *Memory Poisoning Attack and Defense on Memory-Based LLM Agents* (MINJA)
- arXiv:2506.17318 — *Plan Injection: Context-Chained Memory Attacks*
- arXiv:2604.16548 — *A Survey on the Security of Long-Term Memory in LLM Agents: Toward Mnemonic Sovereignty*


---

# SOURCE: v3/docs/adr/ADR-169-benchmark-reporting-integrity-standard.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `6ee60178a102ee3a5adddf21979e7f453bd71035`

# ADR-169: Benchmark Reporting Integrity Standard — Strict-EM Headlines, View-Labeled Scaling, Disclosed Gaps

**ID**: ADR-169
**Status**: Accepted — the FRAMES ablation (metaharness, n=50, seed 42, 2026-06-28) already complies; this ADR makes the discipline binding for every benchmark number ruflo publishes
**Date**: 2026-07-03
**Authors**: rUv (drafted with Claude Code)
**Related ADRs**:
- ADR-167 (GAIA submission integrity — audits a *submission* against exploit vectors)
- ADR-168 (GAIA harness evidence recording — makes the evidence *exist*)
- ADR-133/135/136 (GAIA harness, tracks, hardness routing)
**Source evidence**: FRAMES/GAIA ablation integrity self-audit vs the Berkeley RDI
vectors (`runs/summary.json`, scored by `score-gaia.mjs`) — every verdict below
was measured from committed artifacts, not asserted.

---

## 1. Context

ADR-167 and ADR-168 cover *earning* integrity: was the score obtained by
solving tasks, and is the evidence recorded. This ADR covers the third leg —
**reporting** integrity: given honestly-earned numbers, are they *presented*
in a way that survives the Berkeley RDI lens?

RDI's April 2026 study broke eight major benchmarks not only through harness
exploits but through **reporting artifacts that inflate scores without any
cheating in the run itself**: relaxed/substring metrics presented as accuracy
(normalization collisions), undisclosed best-of-N presented as single-attempt
scores, no-work passes hidden in aggregates, and unreproducible cherry-picked
runs.

The metaharness FRAMES ablation self-audit demonstrated that these vectors are
cheap to close *by construction* — and that the same discipline was already
implicitly present in the ablation's artifacts. What is missing is a binding
standard so future numbers (GAIA, FRAMES, terminal-bench, whatever comes next)
can't regress.

## 2. Decision

Every benchmark number ruflo publishes — README, release notes, leaderboard
submission, gist, blog — MUST satisfy five rules. `summary.json`-style scored
artifacts are the enforcement point.

### R1 — Strict exact-match is the only headline

The reported number is strict (gaia-style normalized) exact-match, tagged
`view: "primary"` in the artifact. Relaxed metrics (gold-tokens ⊆ prediction
or any substring-containment variant) MAY be computed as diagnostics but are
**never the reported number**, and if shown must carry the literal label
*"relaxed (substring-contained) — diagnostic, not the score."* Rationale:
substring containment is the normalization-collision vector RDI used to
inflate GAIA; `score-gaia.mjs` computes `acc_relaxed` for diagnosis and the
FRAMES audit confirms it never leaks into a headline.

### R2 — Test-time scaling is view-labeled, always

Any best-of-N, self-consistency, majority-vote, or verifier-reranked arm
carries an explicit `view` label (`majority`, `verifier-bon`, `ps-bon`,
`sc-curve`, …) in the artifact, and the label travels with the number into
prose. A scaled score quoted without its label is a reporting violation even
when the underlying run was honest. (FRAMES example: deepseek base 0.50 is
quotable as base; 0.56 exists only as `view: "majority"` and must say so.)

### R3 — No-work signatures are disclosed, not hidden

Artifacts report `mean_steps` (with min > 0 for any correct answer) and
`empty_rate` per arm. A correct-with-zero-work record anywhere in the run
fails the artifact (this is AUD-2's reporting-side mirror).

### R4 — Reproducibility block is mandatory

Seed, n, and confidence intervals (Wilson) in the artifact header; the
dataset revision/split named. A number without its reproducibility block is
not publishable.

### R5 — Retrieval-grounded benchmarks state what they cannot prove

Where the benchmark is retrieval-grounded (FRAMES: Wikipedia; GAIA: open web),
retrieving the answer text can be *legitimate* — the integrity question is
whether the artifact can distinguish reasoning-over-retrieval from verbatim
surfacing. Until the ADR-168 evidence contract (serialized tool outputs,
secret-redacted, size-bounded) reaches the benchmark's harness, its reports
MUST carry the honest gap statement rather than an implied clean bill
("answer-leakage: not provable from the artifact"). Turning that ⚠️ into ✅
happens by recording evidence (ADR-168), never by softening the statement.

## 3. Enforcement

1. **Scorer contract**: `score-gaia.mjs` (and successor scorers) keep emitting
   `view`, `mean_steps`, `empty_rate`, seed/n/CI — these fields are the
   machine-checkable surface of R1–R4.
2. **Audit hook**: a reporting-integrity check family in `gaia-audit.mjs`
   (ADR-167's registry) validates a scored artifact against R1–R4 before
   `/gaia submit` packages it: headline view is `primary`; every non-primary
   view labeled; no zero-step corrects; reproducibility block present.
   Fail-closed, same posture as the existing checks.
3. **Prose discipline**: release notes / gists quoting benchmark numbers link
   the artifact and preserve view labels. (Process rule — CLAUDE.md already
   carries the measured-vs-unverified discipline for perf claims; this extends
   it to benchmark accuracy claims.)

## 4. Consequences

- Headline numbers get smaller and honester: strict EM under-reads vs relaxed
  metrics, and scaled arms can't masquerade as base capability. That is the
  point — RDI made the inflated alternative worthless.
- The FRAMES ablation needs zero rework (audited compliant on every vector it
  can currently check); its answer-leakage ⚠️ resolves via ADR-168's contract
  applied to the FRAMES harness (upstream issue ruvnet/ruflo#2544 / #2548).
- One more check family in the ADR-167 audit; a few fields the scorers
  already emit become load-bearing contract.


---

# SOURCE: v3/docs/adr/ADR-384-generalized-bounded-evolution-methodology.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `78e5f53fc1fbc2c3468570e13b8b583dd232c5ff`

# ADR-384 — Generalized Bounded-Evolution Methodology (Darwin+Flywheel) with Error-Control Proof

**Status:** Proposed
**Date:** 2026-08-15
**Deciders:** ruflo-watermark maintainers, darwin-mode / agent-harness-generator maintainers, integration owner
**Supersedes/relates:** ADR-072/073/075 (Darwin cost/reproducibility/archive), ADR-099/101/102/106 (sandbox manifold + Tier2), ADR-112 (FDR small-n caveat), ADR-153/155 (bench suites, security harness), ADR-322 (flywheel receipts/promotion), ADR-381 (sequential-evidence e-process). In-crate instance: `crates/ruflo-watermark/src/{evolve.rs, align.rs}`.

---

## Context

Two systems in this monorepo implement the *same* bounded-evolution methodology with *zero shared code*:

1. **Darwin-mode harness-evolution** (`agent-harness-generator/packages/darwin-mode/src`, TypeScript): evolves a 7-file agent-harness genome (`planner/contextBuilder/reviewer/retryPolicy/toolPolicy/memoryPolicy/scorePolicy`), grades variants with a frozen 6-term scorer, promotes only through a 4-clause gate plus an optional statistical layer (bootstrap child-vs-parent, Benjamini-Hochberg FDR demote-only, monotonic SGM risk budget), and retains a whole-archive lineage.

2. **ruflo-watermark detector-tuning** (`crates/ruflo-watermark/src/{evolve.rs, align.rs}`, Rust): a `(1+λ)` elitist strategy over a 3-field numeric genome (`AlignParams{band, gap_penalty, null_replays}`), a frozen `IndelBenchmark`, a frozen scalar fitness (`margin = mean_pos_z − max_neg_z`), one honest reference (`selfsync_reference`), full seeded determinism, retained lineage, and promotion deliberately left to the caller.

Both already assert the identical invariants — **frozen fitness declared before the run, bounded budget, retained lineage including failures, no auto-promotion, evaluation ≠ promotion**. The generic *back half* of Darwin (selection zoo, BH-FDR / bootstrap / SGM statistics, whole-archive lineage) already operates on abstract `(variant, score, traces)`. The *front half* (genome, environment, fitness, reference, sandbox) is domain-welded in both. As a result the watermark crate cannot reuse a line of Darwin, and Darwin cannot express a numeric-parameter search.

We want one governed framework in which "evolve a 7-surface harness" and "tune a detector's parameters" are literal instances, and we want to state — honestly — exactly what error-control the framework buys and where the guarantees are only approximate.

**This ADR was written against a full adversarial statistical review and an implementation review.** Both are load-bearing. The central finding of the statistical review is uncomfortable and is stated up front rather than buried:

> **The shipped watermark crate does not currently possess the headline "bounded false-promotion" property.** Its only promotion guard is a single point comparison `best.margin > selfsync.margin` (`evolve.rs:143`) — no null, no variance, no error rate. The error-control machinery the proof relies on (ADR-381's e-process, or the meta-null permutation) is *not wired in*. The proof below certifies an **abstract tuner** and specifies what must be built; the crate as of this ADR is a partial instance. The implementation plan (Phase 0) is what makes the guarantee real for the watermark instance.

---

## Decision

Introduce a domain-agnostic bounded-search framework — **`ruflo-evolve`** (Rust) with a mirror **`@claude-flow/evolve`** (TypeScript) — whose contract is six abstractions plus a generic driver. Both flagship systems re-express themselves as thin adapters. The framework **coordinates and evaluates; it never promotes.** Promotion is a separate, signable, human-gated artifact.

The generic *back half* (selection strategies, statistics, lineage, driver) is shared as a specification realized twice (Rust value-typed + byte-deterministic; TypeScript async because the evaluator may be out-of-process/paid). The *front half* is injected per domain through traits.

### The six abstractions (Rust; TS mirror in Applicability)

```rust
pub type GenomeId = [u8;32];
pub type EvaluatorId = [u8;32];

// Deterministic PRNG addressed by (run_seed, generation, child).
// All SEARCH randomness flows through this (see revised invariant 5).
pub struct Prng(u64);
impl Prng { pub fn at(seed:u64, gen:u32, child:u32) -> Self; pub fn u01(&mut self)->f64; }

// (1) GENOME — unifies AlignParams(numeric) and the 7 policy surfaces(structured).
pub trait Genome: Clone + Send + Sync + 'static {
    fn seed() -> Self;                         // incumbent/default, deterministic
    fn mutate(&self, rng:&mut Prng) -> Self;   // clamps into feasible region for numeric reps
    fn is_feasible(&self) -> bool;             // load-bearing only when mutate cannot self-clamp (TS surfaces: compiles?)
    fn id(&self) -> GenomeId;                  // content hash → lineage id + dedup
}

// (2) METRIC — replaces the frozen 6-term scorer AND the scalar margin.
// Diagnostics live HERE (typed), NOT in a stringly-typed side channel (review finding 6).
pub trait Metric: Clone + Send + Sync + 'static {
    fn scalar(&self) -> f64;             // total order for elitism / best()
    fn dominates(&self, o:&Self) -> bool; // Pareto — NO DEFAULT (review finding 9)
}

// Unified cost — the seam that makes iteration-count and paid spend one thing.
#[derive(Default,Clone)]
pub struct Cost { pub evals:u64, pub wall_s:f64, pub usd:f64, pub tokens:u64 }

// Immutable per-candidate evidence, retained whole; carries evaluator_id (frozen-env proof).
pub struct Receipt<G:Genome, M:Metric> {
    pub genome:G, pub genome_id:GenomeId, pub metric:M,
    pub evaluator_id:EvaluatorId, pub cost:Cost, pub coords:(u32,u32) /*gen,child*/,
}

// (3) FITNESS EVALUATOR (FROZEN) — replaces IndelBenchmark AND the three sandboxes.
pub trait FitnessEvaluator: Send + Sync {
    type G: Genome; type M: Metric;
    // Reserve → run → settle so a paid out-of-process judge is metered correctly
    // (review finding 2 — debit-before-work strands partial evals).
    fn reserve(&self, g:&Self::G, b:&mut Budget) -> Result<Ticket, Exhausted>;
    fn settle(&self, t:Ticket, g:&Self::G) -> Receipt<Self::G, Self::M>; // &self: never sees a verdict
    fn fingerprint(&self) -> EvaluatorId;                       // declared-before-run proof
    fn references(&self, b:&mut Budget) -> Vec<Receipt<Self::G,Self::M>>; // a LADDER, not one ref
}

// (4) LINEAGE STORE — generalizes the Archive; failures included, never dropped.
pub trait LineageStore { type G:Genome; type M:Metric;
    fn record(&mut self, r:Receipt<Self::G,Self::M>);   // called BEFORE any comparison
    fn all(&self) -> &[Receipt<Self::G,Self::M>];
    fn best(&self) -> Option<&Receipt<Self::G,Self::M>>;
}

// (5) PROMOTION GATE — first-class, signable, SEPARATE from search.
pub enum Verdict { Promote, Retain(String) }

// Null evidence is NOT replay-shaped by contract (review finding 5): the metaharness
// instance clears winner's-curse with bootstrap/FDR, which has no null_mean/null_sd.
pub enum NullEvidence {
    Replayed(Standardized),                 // watermark: wrong-key / meta-null z
    Bootstrap { q:f64, method:&'static str },// metaharness: BH-FDR / bootstrap
    Absent { reason:&'static str },         // must be justified; a Promote with Absent is a policy error
}

pub struct PromotionReceipt {
    pub genome_id:GenomeId, pub evaluator_id:EvaluatorId, pub gate_seed:u64, pub verdict:Verdict,
    pub evidence: serde_json::Value,        // margins-vs-refs, null evidence, FDR q, SAFETY-FLOOR result
    pub signature: Option<[u8;64]>,         // Ed25519; ONLY on a policy-authorized promote
}
pub trait PromotionGate { type G:Genome; type M:Metric;
    // PURE. Never mutates a running incumbent. MUST evaluate a declared safety floor
    // (review finding M) in addition to beats-references + null-cleared + statistical checks.
    fn safety_floor(&self, cand:&Receipt<Self::G,Self::M>) -> Result<(), String>;
    fn admit(&self, cand:&Receipt<Self::G,Self::M>,
             refs:&[Receipt<Self::G,Self::M>],
             null:&NullEvidence, stats:&serde_json::Value) -> PromotionReceipt;
}
```

### (6) The lifted primitive — EmpiricalNullCalibrator + NuisancePreservingNull

The watermark's wrong-key replay and the missing winner's-curse guard are one contract: *recompute the selection statistic under a signal-destroying, nuisance-preserving perturbation, then standardize.* Factor it out of `detect_gumbel_aligned` so both levels reuse it, and make it accept a **pluggable null estimator** (replay OR bootstrap/analytic surrogate — review finding 8):

```rust
pub trait NuisancePreservingNull { type Ctx;
    fn perturb(&self, base:&Self::Ctx, replica:u32) -> Self::Ctx; } // identical nuisance, zero signal

pub struct Standardized { pub observed:f64, pub null_mean:f64, pub null_sd:f64, pub z:f64, pub p_perm:f64 }

pub struct EmpiricalNullCalibrator;
impl EmpiricalNullCalibrator {
    pub fn calibrate<C>(&self, base:&C, observed:f64,
        stat: impl Fn(&C)->f64, null:&impl NuisancePreservingNull<Ctx=C>, replays:u32) -> Standardized;
}
```

### Driver (the generic back half — structurally cannot promote)

```rust
pub struct EvolutionOutcome<G:Genome,M:Metric> {
    pub best:Receipt<G,M>, pub references:Vec<Receipt<G,M>>,
    pub lineage:Vec<Receipt<G,M>>, pub meta_null:NullEvidence,
}
pub fn evolve<E,S>(ev:&E, store:&mut dyn LineageStore<G=E::G,M=E::M>,
    strat:&S, budget:Budget) -> EvolutionOutcome<E::G,E::M>
where E:FitnessEvaluator, S:SelectionStrategy<G=E::G,M=E::M>;
// seed → reserve/settle → record; per gen: strat.parents(store.all());
// child = parent.mutate(Prng::at(seed,gen,child)); skip if !feasible;
// reserve/settle or halt on Exhausted; record EVERY child incl. losers;
// stop on budget.exhausted(); compute references + meta_null. NEVER calls a PromotionGate.
```

`Budget` is the single place iteration-count and spend unify — a monotonic, non-refillable ledger with `reserve → settle` two-phase accounting.

---

## Formal Properties & Proof

We formalize the abstract tuner `(Θ, D, E, f, b, Search, Gate)` and prove three properties. **Every assumption is stated; every approximation is flagged.** The running instance is the watermark crate; the guarantees hold for the *abstract tuner once Phase 0 is built*, not for the crate as shipped today.

The abstract object: Θ genome space; `E=(P positives, N negatives)` a benchmark drawn **once** from D and **frozen** before any candidate exists; `f:Θ→ℝ` a **pure** function of `(θ,E)` a candidate cannot alter; reference `b` scored on the same E; `Δ(θ)=f(θ)−f(b)` a **paired** contrast; Search bounded and seed-deterministic — `mutate` reads only `(seed,gen,child)`, never a fitness value; winner `θ* = argmax_k f(θ_k)`, stream length `M=1+G·C`; Gate separate from search.

### Claim 1 — frozen fitness + held-out benchmark bounds over-optimism of the *pos_mean* term of the selected candidate

**Assumptions.** (A1) E frozen, independent of the mutation operator; (A2) `f` pure in `(θ,E)` — no self-grading; (A3) per-positive-stream contributions concentrate (see flag G below).

**Key move (load-bearing, and its limits).** Because `mutate` deltas depend on the **seed, not on fitness**, the set of *reachable* candidates is finite and **E-independent**, fully determined by `budget.seed`: `|R_reach| = O(C^G)`, `log N_reach ≈ 8` at G=4,C=6. Seeded determinism is therefore *part of the proof*, not just reproducibility hygiene. A union bound over the E-independent `R_reach` gives, w.p. ≥ 1−δ:

`F_pos(θ*) ≥ f_pos(θ*;E) − σ·√(2 log(N_reach/δ)/|P|)`.

Elitism additionally gives `f(θ*) ≥ f(baseline)` deterministically (no in-sample regression).

**Flags / approximations (adversarial points E→H, K, F, G).**

- **[FLAG — scope; adversarial F].** This bound covers **only the `pos_mean` term** (a mean of iid streams). It does **not** cover `neg_max_z`, the safety-critical FP term: `neg_max_z(θ*) = max over the negative *set*` at an adaptively-selected θ*, which is itself a selection statistic. **Neither Claim 1 (a mean bound) nor Claim 2 (a per-stream null) bounds `E[neg_max_z(θ*)] − true`.** The one quantity the safety gate (`neg_max_z < 4.0`) depends on has *no analytic over-optimism control*. This is closed operationally by the independent-gate split (Claim 3 / Phase 0): `neg_max_z` is re-measured on an independent seed B and the `< 4.0` clause is enforced on B, where selection did not act on it. We state plainly: **the analytic bound does not reach the safety term; only the split does, and the split gives an unbiased estimate, not a closed-form certificate.**

- **[FLAG — assumption conflict; adversarial G].** A3's σ-sub-Gaussian assumption **contradicts** Claim 2's admission that the per-stream z's are a Gaussian standardization of a right-skewed extreme (heavier-than-Gaussian tails). We cannot have both. Resolution: replace A3 with a **bounded-support / empirical-Bernstein** concentration — post-calibration z is clamped to a finite range in practice, and we use `σ̂` estimated with its own inflation term. The bound then carries a variance-of-variance correction and is **weaker than the clean sub-Gaussian form.** We do not claim the sub-Gaussian constant.

- **[FLAG — numerically empty at deployed sizes; adversarial H/I].** At `|P|≈20`, `δ=0.05`, `log N_reach≈8`: slack `≈ σ·√(22/20) ≈ 1.05σ` — comparable to the margins themselves (order 1); at `|P|=6` (the ADR-112 floor) it is `≈1.9σ`. **The analytic certificate is asymptotically sound and empirically vacuous at the sizes the system runs.** Therefore Claim 1 is *not* the operative guarantee. The operative guarantee is the empirical independent-gate split + the corrected meta-null permutation (Claims 3). Claim 1 is retained as a qualitative statement (over-optimism grows only `√(log N_reach) = O(√(G log C))` in search effort) and as motivation for keeping the seed E-independent — not as a numeric bound we rely on.

- **[FLAG — per-seed; adversarial K].** `R_reach` is per-seed. Running M seeds and reporting best-across-seeds is uncontrolled optional stopping that widens the bound to `log(M·N_reach)`. **Mitigation (governed):** the run seed is pre-registered and persisted in the `PromotionReceipt.gate_seed`, exactly as the k-index is persisted for Claim 3; seed-shopping is a policy violation, not a free move. The meta-null (which *requires* B reruns with varied seeds) uses a fixed, declared seed schedule.

### Claim 2 — empirical-null (wrong-key replay) gives a valid null; the per-stream z/p is not (badly) anti-conservative

The statistic `T(θ;key)=local_align_max(centered_scores(tokens,key))` is a max-over-alignment-paths quantity whose naive null is right-skewed. Calibration recomputes `T` under `K=null_replays` wrong keys (nuisance-preserving: identical tokens/marginal law/band/gap; signal-destroying), then standardizes.

**Assumptions.** (i) under H0 the stream is independent of all K+1 keys (true for a genuine null stream); (ii) **hash idealization** — `mix64`/`context_seed` as a random oracle.

**Exact result.** Under (i)+(ii), `(T_obs, T_1,…,T_K)` are **exchangeable**, so the permutation p-value `p_perm = (1 + #{r: T_r ≥ T_obs})/(K+1)` satisfies `P_{H0}(p_perm ≤ α) ≤ α` **exactly** (finite-sample).

**Flags / approximations (adversarial E).**

- **[FLAG — as-coded ≠ as-proved].** The code uses a Gaussian standardization + `normal_upper_tail(z)`, **not** `p_perm`. This corrects the first two moments (removes the dominant max-over-paths inflation) but leaves residual far-tail miscalibration from (a) finite K estimating (mean,sd) with K−1 dof and (b) Gaussianizing a skewed extreme — so `z` is mildly inflated deep in the tail. **Exact α-testing requires `K ≥ 1/α − 1`** (default K=24 floors at p=1/25). Phase 0 emits `p_perm` alongside `z` and the gate consumes `p_perm` (or a fitted Gumbel/GPD tail) for the promotion decision; the evolved `z` remains only a ranking signal.

- **[FLAG — frozen-kernel is overclaimed for this instance; adversarial E, review finding 1].** `null_replays` is an **evolvable genome field** consumed directly to compute `(mean_null, sd_null)`. "A variant cannot re-grade itself" is true only of the *formula*; the candidate selects the *calibration* fed into it, and `argmax margin` will preferentially pick genomes whose fixed-seed `(K, replay-seeds)` realization yields a lucky-low `sd_null`. **This is a live selection-of-calibration-noise channel Claim 2 does not bound, and it is a correctness bug in the shipped crate, not merely a design nicety.** Fix (Phase 0, mandatory): the promotion gate **re-scores the winner and every reference at a fixed, pre-registered `k*`** (e.g. 48) — nearly free because caching already holds all `r<48` wrong-key vectors. The frozen-kernel invariant is restated honestly as *frozen formula + frozen gate-time calibration*, and `null_replays` may vary during *search* but not at the *gate*.

### Claim 3 — family-wise false-promotion control under an adaptively-chosen candidate stream

Two routes. **Both require the independent-gate split** — this resolves the contradiction the two source documents left open (adversarial C): the efficiency lemma says the split is mandatory; the naive Claim-3 statement applied the e-process to the shared E. **We adopt the split as mandatory.** Select on seed A; gate on independent seed B ⟂ selection.

**Route A — sequential e-process (ADR-381), applied on B.** Per candidate k, an anytime-valid e-process bets `(1+λ)` on candidate-wins / `(1−λ)` on baseline-wins over discordant McNemar pairs *drawn from seed B*. Under the **sign null** `H0^k: P(discordant pair favors candidate) ≤ ½`, `(E_k^t)` is a non-negative supermartingale with `E[E_k^0]=1` w.r.t. the filtration including all prior candidates' B-data. Ville's inequality ⇒ per-candidate type-I ≤ α_k under *any* stopping rule. Basel allocation `α_k = α_total·6/(π²k²)` with `Σα_k = α_total` and an independence-free union bound ⇒ `P(∃ false promotion) ≤ α_total`.

**Route B — meta-null permutation (the corrected nuisance-preserving form).** Re-run the *whole* bounded evolution B times against a nuisance-preserving, signal-free benchmark; `p_meta = (1+#{null-best ≥ real-best})/(B+1)` is an exact permutation test of the global "the gain is chance" null for the single selection, provided identical budget/seed discipline per rerun and provided the null is genuinely nuisance-preserving.

**Flags / approximations (adversarial B, C, D, I, J, L, N) — stated explicitly.**

- **[FLAG — wrong functional; adversarial B].** Route A controls the **sign/win-rate null**, which is **orthogonal to the safety-critical worst-case FP** encoded in `neg_max_z`. A candidate can win >½ of discordant pairs (legitimately clearing Route A) while being *worse* on one catastrophic negative. **The e-process alone is insufficient for a detector.** The `PromotionGate::safety_floor` predicate is therefore **not optional**: the watermark gate must enforce `neg_max_z(best on B) < 4.0` as a hard clause *in addition to* the FWER test. We do not claim the e-process bounds the worst-case FP; it does not.

- **[FLAG — martingale breaks under benchmark reuse; adversarial C — RESOLVED by making the split mandatory].** Applying the e-process to the *same* E used for selection violates the conditional-½ assumption (testing on the training set). This ADR **removes that unsoundness by requiring seed B ⟂ selection.** Any implementation that scores the e-process on the selection benchmark is out of contract.

- **[FLAG — α-allocation is power-adverse; adversarial D].** Basel `α_k∝1/k²` gives the *least* budget to *late* candidates — which, in an evolutionary loop, are the *most likely genuine wins*. Validity survives; **usable power collapses for exactly the improvements we want.** The "fix" of reusing/resetting k is the α-double-spend the proof forbids. Consequence we accept: for the watermark's single-selection question, **prefer Route B** (the meta-null permutation), which spends α once on the whole selection and is not subject to the position-dependent starvation. Route A is retained for metaharness's genuinely sequential candidate stream where per-candidate control is the right shape; its power limitation is documented, not denied.

- **[FLAG — meta-null is NOT nuisance-preserving as originally specified; adversarial I — this is the deepest correction].** A "positive built without the watermark key" is an **unwatermarked-then-attacked** stream, whose token marginal differs from a **watermarked-then-attacked** stream — because watermarking *is* a shift of the sampling distribution. So the naive signal-free benchmark draws from a different token law, and `p_meta` becomes an exact test of the *wrong* null (potentially anti-conservative). **Correction adopted here:** build the meta-null by **holding the real watermarked-then-attacked positives fixed and replacing the detector's key with wrong keys at the meta level** — i.e., run the entire evolution scoring against *wrong-key readings of the genuine positive streams*. This preserves the token law exactly (the streams are still watermarked+attacked) while destroying the detector's access to signal — the wrong-key-replay principle lifted correctly to the meta level. This is the watermark-domain-valid meta-null; the "unwatermarked positives" construction is rejected. **Even so, `p_meta` remains conditional on the hash idealization (ii) and on B being finite (quantile uncertainty ~1/B); we report B and use a conservative high quantile.**

- **[FLAG — self-calibration fails under a signal-adaptive proposer; adversarial J].** The meta-null "self-calibrates to whatever selection intensity the optimizations create" **only for a signal-independent proposer** (blind seeded mutation). A surrogate (EI over lineage) fits a real gradient on the real benchmark and pure noise on the null — its induced selection intensity differs, so the null under-reproduces the real funnel. **Consequence:** the calibrated guarantee is claimed **only when the proposer is signal-independent** (Phase 0/1). The surrogate (Phase 3) ships behind the split, and its meta-null is generated with the *same surrogate and same seed schedule* as a best-effort match, with the residual mismatch flagged as an **open question**, not a proven guarantee.

- **[FLAG — generalization dissolves f-purity; adversarial L].** Claims 1–3 assume `f(θ;E)` is a **pure, deterministic** real number (Claim 2's exchangeability treats the K+1 T-values as deterministic given the stream; Claim 1 union-bounds over a finite genome set). A metaharness **paid out-of-process judge is stochastic per call.** Then `R_reach` is no longer the covering object, `fingerprint()` proves *nothing* about grading stability (a stable fingerprint with varying grading is possible), and permutation exactness is gone. **We therefore state which guarantees hold where:** the exact permutation/finite-sample results hold **only for the watermark's pure in-process f**; for metaharness, invariant 5 relaxes to "seeded + variance-bounded", Claim 2's exactness degrades to a **bootstrap/variance-bounded approximation**, and Claim 3 uses BH-FDR/bootstrap (`NullEvidence::Bootstrap`) rather than replay. The "one framework, two instances" thesis holds at the level of *the specification and the gate interface*; it does **not** claim the watermark's exact statistics transfer unchanged to a stochastic judge.

- **[FLAG — safety-of-selection, not safety-of-detection; adversarial N].** Every bound is conditional on `E ~ D`. A deployment attacker is adaptive and free to attack outside E's support. **"Bounded false promotion" means "bounded probability of promoting a detector that fails to beat baseline *on E*" — a selection guarantee, not a deployment guarantee.** Under an adaptive attacker the entire edifice is vacuous regardless of statistical tightness. Mitigation (adversarial-benchmark refresh) is real work but **out of scope for the error-control proof** and is listed under Open Questions.

**Integration.** Claim 1 (qualitatively) bounds over-optimism of the pos_mean term and motivates seed-determinism, but is numerically empty at deployed |P|. Claim 2 makes each per-stream statistic a validly-calibrated null (exact via `p_perm`; approximate as-coded via `z`). Claim 3 — on the *independent gate seed B*, with a mandatory `neg_max` safety floor, via the corrected wrong-key meta-null (watermark) or bootstrap/FDR (metaharness) — converts "best on frozen E" into a governed promotion whose family-wise false-promotion probability ≤ α_total *for the selection question on E*. The crate acquires this property only after Phase 0.

---

## Optimization

Every optimization touches only the **proposer** (what to try), the **scheduler** (order/parallelism), or a **memoization** of the pure evaluator — **never the grader**. Two safety classes:

- **EXACT** — value-identical to sequential by referential transparency or an unbiased-difference estimator. Cannot bias the comparison or inflate FP.
- **SELECTION-ONLY** — may only prune/reorder; an error costs optimality, never correctness, **provided the final gate runs at full fidelity on the independent split B.**

The five techniques and their proofs-of-no-bias:

1. **Successive halving / early stopping — SELECTION-ONLY.** Cheap rung → richer rung. Reported margins of survivors + references are full-fidelity. **Two hard constraints:** (a) **subsample positives only, never negatives** — `margin` uses `neg_max`, and max-over-subset ≤ max-over-full biases margin *upward for exactly the FP-risky candidates the safety clause exists to catch*; (b) rung item-subsets are seed-determined a priori, never chosen from observed scores.
2. **Empirical-null variance reduction.** (2a) **CRN — EXACT, already latent:** the wrong-key seed `mix64(cfg.key.0 ^ (0xA5A5_0000 ^ r))` is candidate-independent and prefix-stable in `r`, so all candidates share null draws → cross-candidate margin differences are low-variance. (2b) **Control variate — EXACT iff β pre-registered:** use the closed-form self-sync sum (analytic null mean) as a proxy; in-sample β injects O(1/k) bias, so β is frozen before the run. (2c) **Adaptive replays — SELECTION-ONLY in pruning only:** data-dependent K at the *gate* is optional stopping; the gate re-scores at the fixed pre-registered `k*` (finding 1 / Claim 2 fix), neutralizing both the optional-stopping channel and the calibration-noise-selection channel.
3. **Surrogate-assisted proposal — PROPOSER-ONLY.** Fewer full evals to a given margin. **The real hazard:** denser search = stronger winner's curse + noise-exploitation. Neutralized **only** by the mandatory independent-gate split + a meta-null generated through the *same* surrogate pipeline. Without the split the surrogate *will* inflate false promotion. (Residual mismatch under a signal-adaptive proposer: see Claim 3 flag J — open.)
4. **Parallel-across-candidates with deterministic seeds — EXACT.** `fitness` reads only immutable bench data + params + pure seed derivations; parallelize across candidates, index lineage by `(gen,child)`, keep **intra-candidate folds fixed-order** (a nondeterministic parallel float sum breaks byte-repro — a stated safety property).
5. **Per-item caching of `centered_scores` — EXACT, highest-value.** `centered_scores(tokens,key,h)` is `AlignParams`-independent; cache per `(item, key-role ∈ {real, wrong_r})` once. Per-candidate cost collapses to the O(n·band) DP; the O(n·H) hashing is paid once for the whole run. Prefix-stable seeds mean one `r<48` cache serves every `null_replays` value and delivers CRN (2a) for free. Cache key must include every value-affecting input, guarded by an equality assertion against a freshly recomputed reference on a sampled item.

**Increment order (the framework is NOT a prerequisite for the speedups — review finding 3):**
`{5, 4, 2a, 2b}` (EXACT, in-crate, byte-safe) → `{fixed-k* gate + independent-gate split + corrected meta-null}` (semantic; Phase 0) → `{1, 2c-pruning, 3}` (SELECTION accelerators, only after the split exists).

The R× meta-null cost is affordable for the pure in-crate watermark precisely because 4+5 make each run cheap (note: the per-item cache does **not** transfer across the B meta-null benchmarks, since each null run reads different key-roles — caching helps *within* a run). For the paid metaharness judge, R× full evolutions is prohibitive, so the calibrator there uses a bootstrap/analytic surrogate, not replay — same *interface slot* (`NullEvidence`), different calibrator per cost regime.

---

## Applicability

The two flagship systems are literal instances of the same six abstractions.

**ruflo-watermark (pure, in-process, deterministic — the exact-guarantee instance):**
- `Genome = AlignParams` (`mutate` = existing clamped perturbations `evolve.rs:153-162`; `is_feasible` dead-but-true because numeric `mutate` self-clamps).
- `Metric = ScalarMargin{margin, pos_mean_z, neg_max_z}` (typed diagnostics live in `M`, no JSON side channel); `scalar()=margin`; `dominates` = scalar (single-objective).
- `FitnessEvaluator = IndelBenchmark`, `Cost{evals:1}`, `fingerprint = hash(cfg,vocab,seed,streams)`, `references = [default-params baseline, self-sync]`.
- `PromotionGate = MarginGate`: `safety_floor` = `neg_max_z < 4.0` (hard); `admit` Promote iff margin > every reference on **seed B** AND `NullEvidence::Replayed` (meta-null) clears threshold AND no-regression re-checked on B.
- Calibrator level-1 = wrong-key replay (extracted from `align.rs:139-150`); level-2 = **corrected wrong-key meta-null over the genuine positives** (closes the winner's-curse gap; nuisance-preserving by construction).

**metaharness harness-evolution (out-of-process, paid, stochastic — the approximate-guarantee instance):**
- `Genome = SevenSurfaces` (`mutate` = regex perturb; `is_feasible` = importable/compiles / Tier2 `--experimental-strip-types` check — here `is_feasible` is load-bearing because `mutate` cannot self-clamp).
- `Metric = Graded{tpr, fpr, patch_pass, cost}` with a **real** `dominates` (Pareto — no default) + a declared scalarization for elitism.
- `FitnessEvaluator` = test command / paid model judge → `Cost{wall_s, usd, tokens}` (this is why `reserve/settle` and the spend budget exist); `references = [B0 static, B1 LLM-single, B2 fixed-agent, B3 prior champion]`.
- `PromotionGate = FlywheelGate`: `safety_floor` = FPR/unsafe clauses; `admit` = BH-FDR (demote-only) + bootstrap child-vs-parent + SGM monotonic risk budget + Ed25519 signed-promote; `NullEvidence::Bootstrap`.
- Calibrator = bootstrap/FDR over the ≥5-task corpus (the existing empirical-null audit dashboard), not replay.

The anti-substitution rule (`evolve.rs:2-9` — refusing to shell to metaharness-darwin because it would "evolve the wrong thing") is *satisfied*: the shared artifact is the **methodology (traits)**, not a shared evaluator. Neither crate pulls the other's domain code.

**Honest scope of "one framework" (review finding 4):** it is **one specification, two implementations** sharing no compiled artifact (Rust crate + separate TS package). Of the six invariants, **byte-determinism (5) and fingerprint-frozen-fitness (2) are structurally enforced only in Rust**; in TypeScript they degrade to convention (interfaces cannot enforce record-before-compare, Prng-only randomness, or verdict-blindness), and for a stochastic paid judge determinism relaxes to "seeded + variance-bounded". The framework's value is **contingent on both adopters implementing the traits** — if darwin-mode keeps its bespoke TS loop, `ruflo-evolve` is indirection for a single caller. This is why the framework extraction (Phase 2) is gated on a darwin-mode commitment, and the exact speedups + Phase-0 correctness fixes land first, independent of any abstraction.

---

## Security / Governance

- **Evaluation ≠ promotion, structurally.** `evolve()` returns an `EvolutionOutcome` and *cannot* mutate an incumbent. Only a separate `PromotionGate::admit()` produces a `PromotionReceipt`. Wiring the winner in is a human decision.
- **No auto-promotion.** No code path signs a `PromotionReceipt` without a policy-authorized promote step; a `Verdict::Promote` carrying `NullEvidence::Absent` is a policy error and is rejected.
- **Human gate.** Signing is Ed25519 with a policy-held key (the flywheel signed-promote model, ADR-322). Darwin, Flywheel, MetaHarness, and this framework may propose and evaluate; they cannot self-promote or widen tools/network/secrets/spend/concurrency.
- **Frozen evaluator, verdict-blind.** `evaluate` takes `&self`; `fingerprint()` stamps every receipt; the driver asserts all receipts in a run share one `evaluator_id`. The evaluator never receives a verdict — a candidate cannot re-grade itself. **Caveat (adversarial L):** `fingerprint()` catches accidental drift, **not** a stable-fingerprint stochastic judge; for paid judges this is a "seeded + variance-bounded" posture, not a cryptographic freeze.
- **Mandatory safety floor.** `PromotionGate` must implement `safety_floor` (review finding M): the FP-critical axis is checked *outside* the scalar score, because elitism's no-regression is on `Metric::scalar()` and a Pareto metric can improve the scalar while regressing FPR. The floor is re-checked on the independent seed B.
- **Governed seeds.** Run seed and gate seed B are persisted in the receipt; seed-shopping across runs is a policy violation (adversarial K).
- **Bounded resource use.** Non-refillable `Budget` ledger; the driver halts on `exhausted()` or the first `Exhausted` from `reserve`.

---

## Evaluation plan

Each phase ships behind **tests + a frozen benchmark** (byte-reproducible fixture; no wall-clock in any graded quantity).

1. **Exact-speedup equivalence.** Golden-master test: `{5,4,2a,2b}` produce **byte-identical** `margin`/`neg_max_z`/promoted-verdict to the current sequential loop on a frozen `IndelBenchmark` seed. Fail on any float divergence.
2. **Calibration validity (Claim 2).** Feed genuine null streams; assert `p_perm` controls type-I at α (`P(p_perm ≤ α) ≤ α` over ≥10k trials); assert the as-coded `z`-path is *not worse than* `p_perm` in the body and record its far-tail anti-conservatism as a measured caveat.
3. **Winner's-curse control (Claim 3, Route B).** On a signal-free (**wrong-key-over-genuine-positives**) meta-benchmark, measure empirical false-promotion rate of the full pipeline (incl. halving) at `p_meta ≤ α`; require ≤ α + quantile slack; report B.
4. **Split necessity (adversarial C).** Ablation: run the gate on the selection benchmark vs seed B; demonstrate the shared-E gate inflates false promotion and the split restores control.
5. **Safety-floor orthogonality (adversarial B/F).** Construct a candidate that wins >½ discordant pairs but regresses `neg_max_z`; assert the FWER test *passes* and the `safety_floor` *rejects* — proving the floor is load-bearing.
6. **FDR small-n (ADR-112).** Below 5 tasks, assert the gate falls back to conservative non-promotion, not a mis-calibrated pass.
7. **Metaharness parity.** The darwin adapter reproduces the existing ADR-099 empirical-FDR audit (FDR≈0.049 at q=0.05 on true-null uniform p-values) through the new `PromotionGate`/`NullEvidence::Bootstrap` path.
8. **Adopter drill.** `ruflo-watermark` and `darwin-mode` both compile against the traits; a CI job asserts the watermark crate's bespoke loop is deleted and re-expressed as an adapter.

---

## Consequences

**Positive.** One governed methodology; the watermark crate acquires real winner's-curse control it lacks today; the `neg_max` safety term gets an explicit floor; the exact speedups make the R× meta-null affordable; the frozen-kernel claim is made honest (fixed-k* gate); Darwin and the watermark tuner share statistics without sharing domain code.

**Negative / accepted.** The analytic Claim 1 is numerically empty at deployed |P| and is demoted to motivation, not certificate. The FWER guarantee is over the sign null, not the worst-case FP — the floor, not the e-process, protects safety. Basel α-allocation is power-adverse for late (best) candidates, pushing the watermark toward Route B. The meta-null is exact only under the hash idealization and the corrected wrong-key construction; under a signal-adaptive surrogate self-calibration is best-effort, not proven. The "one framework" is one spec / two implementations; structural enforcement is Rust-only; value is contingent on darwin-mode adopting the traits. All guarantees are safety-of-selection-on-E, **not** safety-of-detection under an adaptive attacker.

---

## Alternatives

1. **Do nothing / copy-paste.** Keep two welded implementations. Rejected: no shared statistics, and the watermark crate keeps its zero-meta-level-control and its calibration-noise bug.
2. **Shell the watermark tuner to darwin-mode.** Rejected by the anti-substitution rule — it would evolve TS surfaces, not detector params.
3. **Framework-first (extract traits before fixing the crate).** Rejected: the fixed-k* gate, the split, and the corrected meta-null are correctness fixes the crate needs regardless; bundling them with a six-trait rewrite delays a bug fix behind an abstraction whose payoff is contingent.
4. **Keep `null: Standardized` in the gate contract.** Rejected: leaks the replay shape; metaharness has no `null_mean/null_sd` — hence `NullEvidence`.
5. **`Metric::dominates` default = scalar.** Rejected: silently collapses metaharness's Pareto front (review finding 9); no default.
6. **Analytic-only guarantee (rely on Claim 1).** Rejected: vacuous at deployed |P|; the empirical split + meta-null is the operative control.

---

## Rollback

- **Phase 0 (in-crate correctness) rollback:** the fixed-k* gate, split, and meta-null are additive and feature-flagged (`WATERMARK_GOVERNED_GATE`); disabling reverts to `beats_selfsync()` point comparison (the current, weaker-but-known behavior). No data migration.
- **Speedups (1)** are byte-equivalence-tested; rollback = revert commits; no semantic change to undo.
- **Framework (2):** `ruflo-evolve` is a new crate; the watermark adapter can be reverted to the bespoke loop (kept behind a `git tag` snapshot) without touching consumers. The workspace `Cargo.toml` addition is the only shared-manifest change and is trivially revertible.
- **TS mirror / darwin adapter (4):** separate PRs in `agent-harness-generator`; abandon the PRs — no effect on ruflo. If darwin-mode declines the traits, Phase 2's extraction is retained for the single watermark caller only if a second Rust consumer materializes; otherwise revert the extraction and keep the crate-local governed loop.

---

## Open Questions

1. **Signal-adaptive proposer meta-null (adversarial J).** Can the meta-null be made provably selection-intensity-matched under a surrogate proposer, or must the calibrated guarantee be restricted to signal-independent proposers? (Currently: restricted; surrogate ships behind the split with a flagged residual.)
2. **Worst-case FP control (adversarial B/F).** Is there a valid sequential/permutation test *for the `neg_max` extreme functional itself*, so the FWER guarantee and the safety functional coincide, rather than relying on a separate hard floor?
3. **Hash idealization (adversarial, Claim 2 (ii)).** Can exchangeability be established without treating `mix64`/`context_seed` as a random oracle, or is the guarantee inherently heuristic outside that idealization?
4. **Stochastic-judge covering object (adversarial L).** What is the right complexity measure for a stochastic paid evaluator to recover a Claim-1-analogue, and what variance bound makes `fingerprint()` meaningful for grading stability?
5. **Adaptive-attacker benchmark refresh (adversarial N).** How to keep `E ~ D` under an adaptive watermark attacker so the selection guarantee approximates a deployment guarantee — an adversarial-benchmark cadence, out of scope for the error-control proof.
6. **darwin-mode adoption.** Will darwin-mode implement the TS traits? The framework's "one methodology" value is contingent on it (review finding 4); until then the guarantee is realized only for the watermark instance.
7. **Reserve/settle over-charge.** Does the two-phase ledger correctly settle a paid judge that charges on a mid-eval budget cross, or does a reservation strand real spend (review finding 2)?

---

## Implementation Plan

**Concurrency rule (load-bearing).** Concurrent multi-agent implementation into **`agent-harness-generator`** (which carries heavy pre-existing WIP) **must use isolated git worktrees + separate PRs — never parallel writers in one checkout.** Only the integration owner edits shared manifests (`Cargo.toml` workspace members, `v3/` `package.json`, `ruflo/package.json` overrides, lockfiles). Read-only agents may share a checkout; writing agents may not. Every phase binds its tests/benchmarks to an exact clean commit or an immutable dirty-worktree snapshot. Every phase ships **behind tests + a frozen benchmark**.

Legend: **[WT-ISO]** = worktree-isolated, safe for a dedicated writing agent in its own worktree · **[INT-OWNER]** = touches shared manifests, integration-owner-only.

### Phase 0 — In-crate correctness + wire the guarantee for the watermark instance **[WT-ISO — `crates/ruflo-watermark`]**
Addresses adversarial A, C, E, F, I, K and review finding 1. Ships independently of any abstraction.
- `crates/ruflo-watermark/src/align.rs`: extract `EmpiricalNullCalibrator` from `detect_gumbel_aligned` (lines 139-150); emit `p_perm` alongside `z`.
- `crates/ruflo-watermark/src/evolve.rs`:
  - **Independent-gate split** — add a distinct **gate seed B** to `Budget`; `score_with` gains a select/gate distinction; select on A, re-score winner + all references on B.
  - **Fixed-k\* gate re-score** — gate re-scores at a pre-registered `k*` (default 48), neutralizing the `null_replays` calibration-noise-selection channel (finding 1); `null_replays` remains evolvable during search only.
  - **Corrected meta-null** — new `signal_free_meta_null()`: re-run the whole evolution B times scoring against **wrong-key readings of the genuine watermarked-then-attacked positives** (nuisance-preserving); return `p_meta`.
  - **Governed promotion** — replace the informal `beats_selfsync()` decision with a first-class `PromotionReceipt`-shaped struct carrying `neg_max_z(B) < 4.0` **safety floor** + margin-vs-references(B) + `p_meta`; persist run seed + gate seed B. Feature-flag `WATERMARK_GOVERNED_GATE`.
- **Tests + frozen benchmark:** Evaluation-plan items 2, 3, 4, 5, 6 as `#[test]`s over a frozen `IndelBenchmark` seed; assert byte-repro of the governed verdict.

### Phase 1 — Exact speedups in the crate **[WT-ISO — `crates/ruflo-watermark`]**
Addresses optimizations {5, 4, 2a, 2b}. No semantic change.
- `align.rs`: per-item cache of `centered_scores` keyed by `(item, key-role)` (opt 5) with equality-assertion guard; state/exploit CRN (opt 2a); pre-registered control-variate β using the self-sync analytic proxy (opt 2b).
- `evolve.rs`: parallelize evaluation **across candidates** indexed by `(gen,child)`; keep intra-candidate folds fixed-order (opt 4).
- **Tests + frozen benchmark:** golden-master byte-equivalence (Evaluation item 1) — any float divergence fails CI.

### Phase 2 — Extract `ruflo-evolve` crate (six traits + driver + calibrator + budget) **[INT-OWNER for workspace manifest; WT-ISO for crate contents]**
Gated on a darwin-mode adoption commitment (Open Question 6).
- New crate `crates/ruflo-evolve`: `Genome`, `Metric` (no `dominates` default — finding 9), `FitnessEvaluator` with `reserve/settle` (finding 2), `LineageStore`, `PromotionGate` with mandatory `safety_floor`, `NullEvidence` enum (finding 5), `NuisancePreservingNull` + `EmpiricalNullCalibrator` (pluggable null estimator — finding 8), `Cost`/`Budget`, `Prng` (invariant relaxed to *search* randomness — finding 7), `SelectionStrategy`, `evolve()`.
- **[INT-OWNER]** add `crates/ruflo-evolve` to the workspace `Cargo.toml` members.
- **[WT-ISO]** re-express `ruflo-watermark` as an adapter implementing the six traits over `AlignParams`; delete the bespoke loop (kept behind a `git tag` for rollback).
- **Tests + frozen benchmark:** adapter reproduces Phase-0/1 governed verdicts byte-identically; Evaluation item 8 (bespoke-loop-deleted CI assertion).

### Phase 3 — Selection accelerators behind the split **[WT-ISO — `crates/ruflo-watermark` + `crates/ruflo-evolve`]**
Only after Phase 0's split + meta-null exist. Addresses optimizations {1, 2c-pruning, 3}.
- Successive halving (positives-only subsampling; full negatives — opt 1); adaptive replays in pruning only, fixed-k* at gate (opt 2c); surrogate EI proposer as a `SelectionStrategy` (opt 3) with its meta-null generated through the same surrogate + seed schedule.
- **Tests + frozen benchmark:** Evaluation item 3 re-run with halving in the pipeline; assert false-promotion ≤ α; record the surrogate self-calibration residual (Open Question 1) as a measured caveat, not a pass.

### Phase 4 — TS mirror `@claude-flow/evolve` + darwin-mode adapter **[agent-harness-generator: WT-ISO worktrees + SEPARATE PRs; INT-OWNER for shared TS manifests]**
Heavy WIP repo — **isolated worktrees + separate PRs mandatory; no parallel writers in one checkout.**
- New package `@claude-flow/evolve` (TS): the six interfaces (async `FitnessEvaluator` — evaluator may be out-of-process/paid), `NullEvidence`, `calibrate`, `evolve`. Structural invariants documented as *convention* (interfaces cannot enforce them — review finding 4); byte-determinism and fingerprint-freeze explicitly marked Rust-only.
- `packages/darwin-mode/src` adapter (one agent per file, each in its own worktree/PR): `types.ts` → `Genome`/`Metric(Graded, Pareto dominates)`; `generator.ts`+sandboxes (`mock-sandbox.ts`, `tier2-sandbox.ts`) → `FitnessEvaluator` with `Cost{usd,tokens}` + `reserve/settle`; `archive.ts` → `LineageStore`; `scorer.ts` gate + `bench/{runner,stats,risk}.ts` → `PromotionGate` with `NullEvidence::Bootstrap` + BH-FDR + SGM + signed-promote; `evolve.ts` → thin driver call.
- **[INT-OWNER]** `v3/` `package.json` + `ruflo/package.json` overrides for the new package.
- **Tests + frozen benchmark:** Evaluation item 7 (reproduce the ADR-099 empirical-FDR audit through the new gate path).

### Phase 5 — Governance wiring **[WT-ISO per repo; INT-OWNER for signing-key policy]**
- Ed25519 `PromotionReceipt` signing behind the policy-held key (ADR-322 model) in both `ruflo-evolve` (Rust) and `@claude-flow/evolve` (TS); human-gate CLI surface; `NullEvidence::Absent`-on-Promote rejected at the gate.
- **Tests + frozen benchmark:** a Promote without valid `NullEvidence` and without passing `safety_floor` is refused; signed receipts verify against the public key.

**Cross-phase discipline:** bind every test/benchmark to an exact clean commit or immutable snapshot; only the integration owner reconciles overlapping changes or edits shared manifests; continue independent local work after spawning agents and wait only on real dependencies (Phase 2 depends on 0/1; Phase 3 depends on 0; Phase 4 depends on 2's spec but not its Rust code; Phase 5 depends on 2 and 4).

---

# SOURCE: plugins/ruflo-metaharness/README.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `3fa2ca154675ab6baa38353349c885845ec4f982`

# ruflo-metaharness

MetaHarness integration plugin for ruflo. Surfaces the upstream `metaharness` / `harness` / `@metaharness/darwin` CLIs through eleven ruflo skills, honoring [ADR-150](../../v3/docs/adr/ADR-150-metaharness-integration-surfaces.md)'s architectural constraint that MetaHarness must remain a removable augmentation — never a required runtime dependency.

## ADR-150 architectural constraint (load-bearing)

**Ruflo remains operational if every MetaHarness package is removed.** Every code path in this plugin satisfies four rules:

1. **Removable** — no static `import '@metaharness/*'` outside the optional-router path in `v3/@claude-flow/cli/src/ruvector/neural-router.ts`.
2. **Optional in package.json** — `metaharness` is in `optionalDependencies`, never `dependencies`.
3. **Graceful degradation** — every script catches `MODULE_NOT_FOUND`/network failure and emits `{ degraded: true, reason: 'metaharness-not-available' }` JSON, exits 0. The graceful path is the default behavior, not a special case.
4. **CI gate** — `no-metaharness-smoke.yml` runs the plugin smoke with `npm install --no-optional` and asserts the contract still passes.

## Skills

| Skill | Usage | Description |
|-------|-------|-------------|
| `harness-score` | `/harness-score [--path .] [--alert-on-fit-below 70]` | 5-dim readiness scorecard (harnessFit/compile/coverage/safety/memory + cost) |
| `harness-genome` | `/harness-genome [--path .] [--alert-on-risk-above 0.5]` | 7-section categorical report (repo_type/topology/risk/mcp/test/publish) |
| `harness-mcp-scan` | `/harness-mcp-scan [--path .] [--fail-on high]` | Static MCP security findings — pure-read, no dispatch |
| `harness-threat-model` | `/harness-threat-model [--path .] [--fail-on high]` | Enterprise-grade threat model (clean/low/medium/high + findings) |
| `harness-mint` | `/harness-mint --name <id> --template <id> [--confirm]` | Scaffold a custom harness; DRY-RUN by default; refuses project-root writes |
| `harness-similarity` | `/harness-similarity --a a.json --b b.json [--per-dimension] [--alert-below 0.5]` | ADR-152 §3.1 weighted similarity between two harness fingerprints (cosine + categorical + jaccard) |
| `harness-oia-audit` | `/harness-oia-audit [--path .] [--alert-on-worst high] [--dry-run]` | Composite Phase-2 audit (oia-manifest + threat-model + mcp-scan) into `metaharness-audit` namespace |
| `harness-drift-from-history` | `/harness-drift-from-history [--baseline-since 7d] [--threshold 0.95]` | 1-command drift detection — composes audit-list + oia-audit + audit-trend |
| `harness-bench` | `/harness-bench --op create\|verify --repo <path>` | Manage `@metaharness/darwin` bench suites — fixed evaluation corpora for `harness-evolve` |
| `harness-evolve` | `/harness-evolve --repo <path> [--generations 3] [--sandbox real\|mock\|agent]` | Run `@metaharness/darwin evolve` — mutate seven policy surfaces, sandbox-score variants, promote measured wins |
| `harness-security-bench` | `/harness-security-bench [--population 2] [--cycles 1] [--alert-on-fail]` | "Darwin Shield" / ADR-155 — evolve a security-detection harness against a 10-vuln corpus |
| `harness-learn` | `/harness-learn --host <h> --model <m> --slice <manifest> [--repo <checkout>] [--run]` | metaharness@0.3.0 / upstream ADR-235 — GEPA learning run; $0 dry-run default, `--run` to spend; needs a metaharness repo checkout |
| `harness-gepa` | `/harness-gepa --op genome\|validate\|render\|analyze [--path <genome.json>]` | darwin@0.8.0 GEPA library surface — genome load/validate/render + transcript failure analysis; `gepaOptimize` stays library-only |

## Phase-0 baseline (ruflo itself, 2026-06-16)

```json
{
  "harnessFit": 82,
  "compileConfidence": 100,
  "taskCoverage": 79,
  "toolSafety": 100,
  "memoryUsefulness": 40,
  "estCostPerRunUsd": 0.048,
  "recommendedMode": "CLI + MCP",
  "archetype": "typescript-sdk-harness",
  "template": "vertical:coding",
  "scaffoldReady": true,
  "risk_score": 0.27,
  "publish_readiness": 0.9
}
```

## Architecture

All skills use subprocess invocation through the `_harness.mjs` shared helper:

```
skills/X/SKILL.md → scripts/X.mjs → scripts/_harness.mjs → spawnSync('npx', ['metaharness', …])
                                                  ↘ on MODULE_NOT_FOUND → emit degraded JSON, exit 0
```

This means:
- No library import overhead on ruflo's boot path
- 60s hard timeout per subprocess (bounded blast radius)
- `--json` flag forced for structured parsing
- Graceful degradation is a single helper used by every skill

## Cross-links

- [ADR-150](../../v3/docs/adr/ADR-150-metaharness-integration-surfaces.md) — decision + architectural constraint
- [Issue #2399](https://github.com/ruvnet/ruflo/issues/2399) — phase rollout tracker
- [Research dossier](https://gist.github.com/ruvnet/19d166ff9acf368c9da4172d91ac9113) — full graded-evidence sourcing
- [Upstream](https://github.com/ruvnet/agent-harness-generator) — `metaharness` source
- ADR-148/149 — `@metaharness/router` cost-optimal routing (sibling integration)

