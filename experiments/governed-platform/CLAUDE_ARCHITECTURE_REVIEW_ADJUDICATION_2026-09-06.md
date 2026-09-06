# Independent Adjudication — Claude Architecture Falsification Review

Date: 2026-09-06
Status: **ACCEPTED WITH CLASSIFICATION — architecture changes required**

This document independently adjudicates the supplied Claude review of the Governed AI Development Platform high-level architecture. The review is treated as adversarial evidence, not as authority. Findings are accepted, narrowed, or rejected based on the current repository architecture.

## Executive result

The review identified several real gaps. The most important are not arguments against external authority; they show that the external-authority design needs a stronger distributed enforcement and provenance model.

### Critical / architecture-blocking

1. **Partition-safe authority enforcement is underspecified.** Current architecture requires use-time authorization but does not define fencing, freshness bounds, or partition behavior. A stale enforcement point could honor a capability after governance has revoked or narrowed it.
2. **Intent-to-action correspondence / untrusted-content containment is missing.** Tool results from browsers, GitHub, issues, PRs, documentation, or external systems can contain instructions. Capability scope alone does not prove that an in-scope action is justified by the authoritative task.
3. **Ephemeral-worker evidence durability is underspecified.** Evidence generation and durable evidence commit are separated; cleanup must not occur before evidence is durably persisted and acknowledged.
4. **Destructive/high-blast-radius tools require stronger controls than ordinary MCP tools.** Database, deployment, secret, migration, and protected-branch actions cannot share only a generic authorization recipe.

### High

5. **Evidence ledger topology needs redesign.** The current conceptual schema uses a BIGSERIAL sequence and previous-record hash, which reads as a global ordered chain. A global chain is an unnecessary scaling bottleneck and has no independent external checkpoint/anchor.
6. **Concurrent task integration needs explicit overlap/conflict governance.** Isolated workspaces prevent direct races but do not prevent two independently valid patches from becoming semantically incompatible when combined.
7. **Capability bearer semantics need to be explicit.** Capability IDs must not themselves be sufficient bearer credentials; authorization needs cryptographic and execution/subject/resource bindings.
8. **Control-plane availability and workload isolation need to be explicit.** A modular monolith is a code/transactional architecture choice, not permission to colocate CPU-heavy analysis with the low-latency authority hot path in one unisolated process.
9. **MCP discovery/enforcement version drift must fail closed deterministically.** Exact tool/server/schema versions must be pinned in the issued tool profile.

### Medium / clarification required

10. **Per-tool-call latency estimate is not established by the diagram.** The review assumes 5–6 network hops. The intended implementation can and should collapse policy enforcement into a local gateway/sidecar and keep catalog discovery off the invocation hot path. The review is directionally useful but its numeric latency estimate is not an observed result.
11. **Human-gate latency is a product/SLA issue, not a logical contradiction.** Human review must be risk-based and asynchronous where possible. For changes requiring human approval, safety wins over raw merge speed; the platform should state this explicitly instead of claiming uniform velocity improvement.
12. **Scanner-as-oracle risk is valid but partly addressed by complementary verification.** The architecture must state explicitly that no scanner or single verifier is authoritative truth and that evidence sufficiency is multi-source/risk-based.

## Finding-by-finding adjudication

| Review issue | Decision | Severity | Required architecture response |
|---|---|---:|---|
| Modular monolith is an org-wide SPOF | **PARTIALLY ACCEPTED** | High | Keep modular control-plane code/transaction model for MVP, but isolate the latency-critical Authority Kernel, run it redundantly, move heavy graph/context/observability work off the authorization hot path, and use safe rollout/canary/config validation. |
| MCP Policy Gateway / Use-Time Gate SPOF | **ACCEPTED** | Critical | Use replicated/local enforcement points, signed sender-constrained capabilities, monotonic fencing/authority epochs, bounded-freshness policy snapshots, and risk-tiered online checks. No bypass fallback. |
| Global immutable ledger scaling ceiling | **ACCEPTED** | High | Replace global chain with partitioned evidence chains + Merkle checkpointing. Maintain global query indexes as non-authoritative projections. |
| Stale capability under partition | **ACCEPTED** | Critical | Add monotonic fencing tokens/authority epochs, lease TTL/freshness bounds, and fail-closed rules when a mutation-grade enforcement point cannot establish sufficiently current authority. |
| Evidence loss before ledger commit | **ACCEPTED** | Critical | Add durable evidence spool/WAL and a worker state barrier: workspace cleanup is forbidden until required artifacts are content-addressed and evidence receipt is durably acknowledged. |
| MCP discovery/enforcement drift | **ACCEPTED** | High | Issue exact MCP profile with server/tool/version/schema hashes; unknown or changed tool surfaces are denied until re-approved. Default deny. |
| Concurrent agents with no artifact coordination | **ACCEPTED** | High | Add change claims/leases, base-state versioning, overlap detection, revalidation against current authoritative head, and combined-patch regression/semantic checks before acceptance. |
| 5–6 synchronous policy hops latency | **PARTIALLY ACCEPTED** | Medium | Do not implement architecture boxes as mandatory remote calls. Collapse hot-path checks locally; catalog lookup happens at profile issuance, not each call. Measure before setting SLOs. |
| Human gate destroys velocity | **NARROWED** | Medium | Human gates only where policy/risk requires; asynchronous escalation. State explicitly that safety/required approval takes precedence for high-risk changes. |
| Capability confused-deputy / IDOR risk | **ACCEPTED** | High | Capability ID is a reference only. Actual authority is signed/sender-constrained and binds tenant/project/task/execution/subject/audience/action/resource/tool-profile/policy/epoch/expiry. |
| Prompt injection / untrusted tool content | **ACCEPTED** | Critical | Introduce Content Provenance & Trust Labels plus an Action Intent Guard. Untrusted content is data, never authority. High-impact actions must bind to an authoritative task/requirement/action-plan reference. |
| DB tools treated like browser tools | **ACCEPTED** | Critical | Add tool-class-specific safety recipes: read replicas, transaction preview, row/change bounds, migration dry-run/shadow DB, rollback evidence, dual/human authorization for protected/destructive production changes. |
| Security scanner treated as oracle | **ACCEPTED / ALREADY PARTIAL** | Medium | Make no-single-verifier rule explicit; scanners contribute evidence but cannot alone authorize release. Require complementary evidence by risk. |
| No external anchor for evidence chain | **ACCEPTED** | High | Periodically sign and anchor Merkle roots/checkpoints in a separate trust domain / WORM store or transparency service with independent credentials. |

## Revised architectural principles

1. **External authority remains non-negotiable, but enforcement is distributed.** Authority is issued by the platform; enforcement can be local/replicated as long as it cannot widen authority.
2. **Use-time authorization means enforcement at the effect boundary, not a mandatory remote round-trip to one central service.**
3. **Revocation semantics are risk-tiered and explicit.** Stronger actions require stronger freshness guarantees.
4. **Untrusted content cannot create intent.** Web pages, PR comments, issue bodies, code comments, tool output, logs, and model text are evidence/data unless explicitly promoted by an authorized platform transition.
5. **Every consequential action must have both authority scope and intent binding.** Being allowed to WRITE does not mean every WRITE is legitimate.
6. **Evidence must be durable before ephemeral state can disappear.**
7. **No single verifier is an oracle.** Evidence sufficiency is policy- and risk-dependent.
8. **Tool safety is blast-radius-specific.** Read, workspace mutation, external mutation, and production/release operations have different enforcement recipes.
9. **Parallelism must converge against current authoritative state, not only each task's stale base.**
10. **Availability mechanisms may replicate governance; they may never bypass it.**

## Architecture work authorized by this adjudication

This review justifies architecture-only changes in new/additive design documents and ADRs. It does not authorize modifying the frozen EXP-N Pilot 8 execution dependencies or changing any pre-registered Pilot 8/9 scientific endpoint.

Required follow-up architecture changes:
- define a Resilient Authority Kernel and risk-tiered enforcement modes;
- add monotonic fencing/authority epoch semantics;
- define signed sender-constrained capability envelope;
- define Content Provenance / Action Intent Guard;
- define durable evidence spool and cleanup barrier;
- redesign evidence ledger as partitioned chains + Merkle checkpoints + independent anchor;
- define MCP profile pinning and schema drift failure behavior;
- define blast-radius-specific tool policies, especially database/deployment/secrets;
- define concurrent change claims and integration revalidation;
- define hot-path vs analytical workload deployment isolation.

## Conservative conclusion

Claude's review does **not** falsify the core governed-platform premise. It falsifies the sufficiency of the first high-level deployment/security drawing. The external-authority model remains the correct trust direction, but the product architecture must add distributed enforcement, fencing, intent binding, durable evidence handoff, risk-specific tool controls, and independently anchored evidence before it is credible as a production control plane.
