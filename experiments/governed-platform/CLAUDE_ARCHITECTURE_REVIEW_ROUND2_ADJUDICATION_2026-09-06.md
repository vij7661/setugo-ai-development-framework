# Independent Adjudication — Claude Architecture Review Round 2

Date: 2026-09-06
Status: **ACCEPTED WITH NARROWING — operational contracts must be made explicit**

This document independently adjudicates the second Claude review of the revised Governed AI Development Platform architecture. The review is evidence, not authority. It confirms several fixes from round 1 and identifies remaining ambiguity in deployment isolation, revocation freshness, content-level intent binding, concurrent change coordination, human-gate decoupling, evidence anchoring, and worker identity lifecycle.

## Executive result

The second review does **not** reopen the core external-authority architecture. It mainly shows that several controls exist conceptually but still need precise operational contracts.

### Accepted as already materially fixed

1. Monotonic epoch/fence semantics address the original unbounded stale-capability race.
2. Sender-constrained capability envelopes close naive capability replay by a different worker/session.
3. Durable evidence spool + cleanup barrier closes the ephemeral-worker evidence-loss window.
4. Exact MCP server/tool/schema pinning closes permissive discovery/enforcement drift.
5. No-single-verifier policy prevents a scanner PASS from becoming release authority by itself.

### High-priority clarifications / changes

1. **Authority Kernel must be a genuinely separate deployable security boundary.** “Isolated” is not allowed to mean only an in-process module boundary. It needs independent rollout, scaling, rollback and SLOs from analytical Governance Services.
2. **Revocation/freshness must be a versioned risk-tier policy with an explicit maximum stale-authority window.** The platform cannot claim instantaneous revocation under partition. A bounded freshness lease is the actual revocation SLA for cached enforcement.
3. **Action Intent Guard must be content/effect-aware, not merely action-category-aware.** The platform must bind consequential effects to a frozen plan/effect contract and validate the actual proposed diff/parameters before authoritative external mutation or release.
4. **Change Claims must be preventive and independent of evidence partitions.** A live Claim Registry is consulted before execution; final integration revalidation remains mandatory even when claims do not conflict textually.

### Additional accepted hardening

5. **Selection waits for an authoritative decision/version, not a stale/default policy projection.** The transactional outbox is dispatch/propagation; it is not permission to route from stale derived state.
6. **Human gates are asynchronous workflow states.** Independent low-risk subtasks may continue if separately authorized; the gated consequential action stays blocked.
7. **Evidence checkpoint interval is an explicit tamper-detection-latency policy.** The independent anchor must be a separate trust domain with independent administrative credentials, not merely another bucket under the same root account.
8. **Worker restart causes capability re-issuance.** Sender-constrained capability envelopes are never transferred to a replacement worker identity.

## Finding-by-finding adjudication

| Round-2 issue | Decision | Severity | Architecture response |
|---|---|---:|---|
| Authority Kernel may still share one deployable | **ACCEPTED** | High | Make Authority Kernel its own deployable/service boundary with independent pipeline, SLO, scaling and rollback. Governance backend may remain modular-monolith internally without the kernel. |
| Epoch propagation under partition | **ACCEPTED / TRADE-OFF MUST BE EXPLICIT** | Critical contract | Version freshness by risk. Cached authority is allowed only within bounded lease. Expiry means fail closed for mutation. External/release operations require current online authority. |
| Need one universal TTL number | **NARROWED** | High | Do not use one TTL for all actions. Use risk-tier freshness budgets. Record the chosen budget on the capability/tool profile so the enforcement decision is auditable. |
| Partitioned ledger conflicts with overlap detection | **ACCEPTED** | High | Overlap detection comes from a separate strongly consistent/live Change Claim Registry, not evidence-ledger queries. Evidence remains for audit/review. |
| Outbox consumer lag may cause stale selection | **ACCEPTED** | High | Routing/selection requires an authoritative policy/task decision version. Derived projections may optimize reads but never authorize a stale/default route. |
| Local authority check changes latency substantially | **AGREED** | Medium | Normal low-risk checks are local signature/profile/freshness validation. Network check is reserved for cache miss/freshness renewal/high-risk actions. Measure actual p50/p95/p99 later; do not claim unmeasured latency. |
| Human gate still end-to-end blocking | **ACCEPTED** | Medium | Use async HUMAN_REQUIRED state and continuation events. Other independent subtasks may proceed only with their own scopes. Required gated action cannot proceed. |
| Intent guard may be category-level only | **ACCEPTED** | Critical contract | Add Plan-Step Effect Contract + frozen Action Effect Manifest. Validate exact resource/parameter/diff constraints and require content-level semantic verification before external integration/release where deterministic checks cannot establish intent correspondence. |
| Merkle interval = tamper-detection window | **ACCEPTED** | High | Explicit checkpoint cadence/SLO; smaller windows for high-risk evidence. Record checkpoint lag. Anchor in a separately administered trust domain. |
| “Independent anchor” may not be independent | **ACCEPTED** | High | Separate credentials/admin root; preferably separate account/provider or public transparency service for high assurance. Same-root storage is not classified as independent. |
| Worker identity churn / capability re-binding | **ACCEPTED** | High | Replacement worker gets new workload identity and newly issued sender-bound capability; old capability is revoked/expired and cannot be transferred. |

## Concrete policy decisions

### Authority freshness classes

Freshness is an explicit field in the capability/tool profile, not an undocumented cache behavior.

Candidate pre-production defaults (to be measured and calibrated before production promotion):

- `READ_ONLY`: maximum cached authority age **60 seconds**; after that, refresh or fail closed for the read if policy requires current state.
- `WORKSPACE_MUTATION`: maximum cached authority age **15 seconds**, with a short-lived lease and resource/task fence; after expiry, local workspace mutation pauses until refreshed. Workspace remains non-authoritative.
- `EXTERNAL_MUTATION`: **online current-authority check required at effect time** unless a future narrowly scoped policy is independently qualified. No serve-stale fallback.
- `RELEASE_OR_PRODUCTION`: **online current-authority + current resource fence required**. No cached/offline release authority.

These are architecture-candidate defaults, **not measured SLO claims**. Production values must come from risk analysis, revocation experiments, availability testing and latency measurements.

### Cache-miss / stale behavior

- valid and within freshness lease: local verify and proceed if all other checks pass;
- cache miss while origin reachable: refresh, then reevaluate;
- cache miss/stale and origin unavailable:
  - READ_ONLY: policy-defined bounded behavior only;
  - WORKSPACE_MUTATION: pause/fail closed after lease expires;
  - EXTERNAL_MUTATION: fail closed;
  - RELEASE_OR_PRODUCTION: fail closed.

No policy may silently downgrade to a weaker freshness class because the authority service is unavailable.

### Content/effect-level intent binding

A consequential proposal is bound to a frozen **Plan-Step Effect Contract** containing:
- authoritative requirement/invariant refs;
- allowed operation classes;
- allowed resource/path patterns;
- forbidden/protected resource patterns;
- expected artifact classes;
- allowed external targets;
- explicit destructive-effect flag;
- parameter bounds where deterministic (row limits, environment, branch, service, schema, etc.);
- base artifact/SHA/state version;
- required evidence/reviewer class.

Before authoritative external mutation or integration, the platform freezes an **Action Effect Manifest** containing:
- tool + exact parameters hash;
- actual target resources;
- proposed patch/diff/content digest;
- changed-file/module/symbol inventory where available;
- external side-effect preview where available;
- provenance refs that influenced the proposal;
- plan-step/effect-contract ref.

The guard performs deterministic correspondence checks first. Where semantic correspondence cannot be proven deterministically, a separately qualified verifier/reviewer evaluates the frozen effect manifest against the authoritative plan. That review remains evidence; the Governor owns the final gate.

This means “WRITE is allowed” never means “any WRITE parameters/content are allowed.”

### Preventive Change Claim Registry

The platform maintains a live, low-latency claim registry separate from the evidence ledger.

Before Builder execution starts, a task declares/acquires claims over relevant scopes such as:
- repository/path/module;
- API/schema/contract;
- migration stream;
- deployment target;
- protected branch;
- secret/IAM resource;
- named invariant/domain component.

Policy decides overlap behavior:
- `EXCLUSIVE`: second task waits/blocks;
- `PARALLEL_PROPOSAL`: both may work in isolated workspaces, but neither can integrate until combined revalidation;
- `SHARED_READ`: no mutation conflict;
- `ESCALATE`: human/architect decision required.

Claim acquisition is preventive. Final rebase/current-head impact analysis and combined verification remain mandatory and are not replaced by the claim registry.

### Authoritative selection barrier

Selection & Qualification may use projections for speed, but execution cannot start until it is bound to an authoritative tuple:

`task_state_version + contract_version + policy_hash + routing_policy_version + qualification_ref + capability_epoch`

If the projection is behind, the task waits for/reads authoritative state. There is no permissive default route.

### Human gate async continuation

`HUMAN_REQUIRED` blocks only the gated transition/action. The task graph may continue independent subtasks whose own capabilities remain valid and whose outputs cannot bypass the pending gate. Human decision arrives as an authenticated continuation event and advances only the permitted state transition.

### Evidence checkpoint and anchor policy

Checkpoint cadence is risk-tiered. Candidate starting targets:
- ordinary project/task evidence: checkpoint at least every **60 seconds or 1,000 records**, whichever comes first;
- release/security/high-risk authority evidence: checkpoint at least every **10 seconds or 100 records**, whichever comes first.

Checkpoint lag is observable and treated as tamper-detection latency. These values are candidate defaults, not measured production SLOs.

An `INDEPENDENT` anchor must use a different administrative trust root from the primary evidence store. Preferred high-assurance options include a separate cloud account/provider, dedicated WORM system with separate administrators, or public/third-party transparency log. Same-account/same-root storage is only a redundant copy, not an independent anchor.

### Worker restart rule

Sender-constrained capability transfer is forbidden.

On worker loss/restart:
1. freeze/retain durable spool evidence from old execution if available;
2. invalidate or allow expiry of old worker capability according to incident/restart policy;
3. increment/revalidate execution/authority epoch when required;
4. create replacement worker with a new workload identity/key;
5. issue a new capability bound to the replacement identity and current task/resource fences;
6. resume only from an authorized durable checkpoint.

## Deployment clarification

The architecture is revised to:

- **Governance Backend:** modular monolith for contracts, orchestration, review policy, memory, impact coordination and projections.
- **Authority Kernel:** separate minimal deployable/security boundary with independent rollout, scaling, rollback, SLO and signing/revocation dependencies.
- **Execution Domains:** independently scalable isolated workers with local enforcement points.
- **Analytical Worker Pools:** impact/context/observability work off the authority hot path.

Therefore a bad Governance Backend rollout must not automatically kill existing local authorization checks that remain within their freshness lease, while a compromised/unavailable backend also must not widen authority. New/renewed mutation authority still requires the Authority Kernel according to risk class.

## Conservative conclusion

Round 2 improves precision rather than changing direction. The highest-value outcome is that the architecture now exposes its real trade-offs instead of implying zero-cost safety:

- revocation is bounded by explicit freshness policy under partition;
- low-risk enforcement is local for latency;
- high-risk effects fail closed without current authority;
- intent binding is content/effect-aware at authoritative effect boundaries;
- overlap control is preventive through a live claim registry;
- evidence tamper detection has an explicit checkpoint window and separate trust anchor;
- ephemeral worker identity is never allowed to transfer authority.

These architecture changes remain additive and must not modify the frozen EXP-N Pilot 8/Pilot 9 execution dependencies or pre-registered scientific endpoints.