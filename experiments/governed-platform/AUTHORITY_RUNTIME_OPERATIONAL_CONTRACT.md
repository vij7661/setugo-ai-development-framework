# Governed Platform — Authority Runtime Operational Contract

Status: **Architecture Candidate / Operational Contract**

This contract converts the resilient-authority architecture into explicit runtime rules. It is intentionally stricter than a diagram: every enforcement point, worker adapter and MCP gateway must be able to answer the same questions deterministically.

## 1. Deployment boundary

The **Authority Kernel is a separate deployable security boundary** from the Governance Backend.

Authority Kernel responsibilities only:
- capability issuance/signing;
- policy/authority epoch management;
- revocation;
- resource fences;
- freshness/lease renewal;
- high-risk online authorization;
- signing-key rotation and verification metadata.

It has its own:
- deployment artifact;
- rollout pipeline;
- rollback path;
- autoscaling/resource budget;
- SLO/error budget;
- security identity/credentials;
- availability and audit telemetry.

Heavy impact analysis, context building, reporting, review summarization and observability aggregation are not allowed to run inside this service.

## 2. Freshness classes

Every capability contains `freshness_class` and `max_cached_authority_age_ms`.

Candidate pre-production values:

| Class | Max cached age | Offline behavior after expiry | External authoritative effect |
|---|---:|---|---|
| `READ_ONLY` | 60,000 ms | refresh or policy-defined fail closed | none |
| `WORKSPACE_MUTATION` | 15,000 ms | pause/fail closed until refreshed | forbidden |
| `EXTERNAL_MUTATION` | 0 cached authorization for final effect | fail closed | online authority required |
| `RELEASE_OR_PRODUCTION` | 0 | fail closed | online authority + current fence required |

These are design defaults for test environments, not production SLO claims. Promotion requires latency, availability and revocation testing.

The enforcement point must record:
- capability epoch;
- local epoch snapshot;
- snapshot age;
- resource fence;
- freshness class;
- decision timestamp;
- whether an online refresh/check was required;
- allow/deny reason.

## 3. Cache behavior

A local enforcement point follows exactly:

1. Verify capability signature and sender constraint.
2. Verify task/project/execution/tool-profile bindings.
3. Compare current local epoch/fence snapshot.
4. If snapshot age <= permitted freshness, continue local checks.
5. If stale and origin reachable, refresh and reevaluate.
6. If stale and origin unavailable:
   - `READ_ONLY`: only policy-explicit bounded reads may continue;
   - `WORKSPACE_MUTATION`: pause/fail closed after lease expiry;
   - `EXTERNAL_MUTATION`: deny;
   - `RELEASE_OR_PRODUCTION`: deny.
7. Never downgrade freshness class because origin is unavailable.

## 4. Plan-Step Effect Contract

Each consequential plan step has a frozen platform-owned effect contract:

```json
{
  "effect_contract_id": "effect_...",
  "task_id": "task_...",
  "plan_step_id": "step_...",
  "requirement_refs": ["req_17"],
  "invariant_refs": ["inv_auth_3"],
  "allowed_action_classes": ["WRITE_WORKSPACE"],
  "allowed_resources": ["repo:owner/repo:path:src/auth/**"],
  "forbidden_resources": ["repo:owner/repo:path:infra/prod/**"],
  "allowed_external_targets": [],
  "destructive_effect_allowed": false,
  "base_sha": "...",
  "max_changed_files": 8,
  "required_evidence_classes": ["PROJECT_TEST", "INDEPENDENT_REVIEW"],
  "effect_contract_hash": "sha256:..."
}
```

The contract is authoritative platform state. A model may propose amendments, but amendments require a new accepted contract version.

## 5. Action Effect Manifest

Before a high-impact action crosses an authoritative effect boundary, freeze the actual proposed effect:

```json
{
  "action_effect_id": "ae_...",
  "effect_contract_id": "effect_...",
  "execution_id": "exec_...",
  "tool_id": "git.push_branch",
  "parameter_hash": "sha256:...",
  "target_resources": ["repo:owner/repo:branch:task-123"],
  "patch_digest": "sha256:...",
  "changed_files": ["src/auth/session.go"],
  "changed_symbols": ["ValidateSession"],
  "base_sha": "...",
  "provenance_refs": ["content_..."],
  "side_effect_preview_ref": "evidence_..."
}
```

Deterministic guard checks include:
- target/resource subset;
- action class allowed;
- base SHA/state current;
- forbidden resources untouched;
- changed-file/parameter bounds;
- required preview/dry-run evidence present;
- provenance labels current;
- resource fence current;
- required gates satisfied.

When semantic correspondence between the actual content and requirement cannot be established deterministically, the effect remains non-authoritative until a separately qualified verifier evaluates the frozen diff/effect manifest against the authoritative requirement/invariant set.

## 6. Preventive Change Claim Registry

The Change Claim Registry is a live authoritative coordination service/table, **not an evidence-ledger projection**.

Claim key examples:
- `repo:path:src/auth/**`
- `api:identity/session-v2`
- `db-schema:customer`
- `deploy:prod/payment-api`
- `iam:role:release-bot`
- `invariant:authentication-session-validity`

A Builder must obtain its required claim disposition before execution:
- `EXCLUSIVE_GRANTED`
- `PARALLEL_PROPOSAL_GRANTED`
- `SHARED_READ_GRANTED`
- `WAITING_CONFLICT`
- `HUMAN_REQUIRED`

Every claim records base SHA/state version and claim epoch.

Parallel proposal mode permits isolated work but does not grant integration authority. Final current-head integration/rebase + impact analysis + combined verification are mandatory.

## 7. Selection barrier

Selection may query fast projections, but dispatch requires an authoritative binding record containing:
- task state version;
- contract version/hash;
- policy hash/version;
- routing policy version;
- agent runtime qualification ref;
- model/execution-path qualification ref when applicable;
- verification-plan hash;
- claim-registry disposition/epoch;
- capability epoch.

If any authoritative dependency is unavailable or version-mismatched, dispatch waits or fails closed. No stale/default route is allowed.

## 8. Async human gate

Human approval is an event-driven state transition, not a synchronous request thread.

When `HUMAN_REQUIRED`:
- freeze the gated effect/action;
- create approval request with evidence manifest;
- release compute resources that are not needed to preserve evidence;
- allow unrelated task-graph nodes to continue only if independently authorized and unable to bypass the gate;
- resume gated state only from an authenticated approval/rejection event.

Human wait time is visible separately from machine execution latency.

## 9. Evidence checkpoint policy

Each evidence partition publishes signed checkpoints.

Candidate pre-production cadence:
- normal evidence: <= 60 seconds or <= 1,000 new records;
- high-risk/release/security/authority evidence: <= 10 seconds or <= 100 new records.

The earlier threshold wins.

Observability records:
- oldest uncheckpointed record age;
- records since last checkpoint;
- last checkpoint signature status;
- anchor receipt status;
- anchor age.

A missed checkpoint does not rewrite history into PASS; it produces degraded evidence-integrity state and may block release by policy.

## 10. Independent anchor definition

An anchor is `INDEPENDENT` only when compromise of the primary platform administrative root is insufficient to rewrite both primary evidence and the anchor.

Acceptable high-assurance patterns:
- separate cloud/provider account with separate root admins and credentials;
- separately administered WORM/compliance store;
- third-party/public transparency log;
- equivalent independent trust domain.

A second bucket/database under the same root identity is redundancy, not an independent anchor.

## 11. Worker restart / identity churn

Capability transfer across worker identities is forbidden.

On worker restart/reschedule:
1. old worker identity is terminated/revoked where possible;
2. durable spool is reconciled;
3. execution continuation point is validated;
4. current task state/claim/fence/epoch is rechecked;
5. replacement worker receives a new workload identity/key;
6. Authority Kernel issues a new sender-constrained capability;
7. execution resumes only from an authorized durable checkpoint.

The old capability is never copied into the new worker.

## 12. Verification obligations

Before production promotion, falsify at least:
- stale-epoch behavior during partitions;
- freshness expiry races;
- cache-miss behavior by risk class;
- capability replay from wrong worker identity;
- worker crash/restart re-binding;
- claim conflicts across concurrent tasks;
- stale projection dispatch attempts;
- prompt-injection attempts that stay within action category but alter parameters/content;
- checkpoint/anchor lag and rewrite attempts;
- authority-kernel independent deploy/rollback failure modes;
- human-gate continuation without bypass.

## 13. Outcome

The operational contract is:

**Separate Authority Kernel → signed sender-bound capability → risk-tier freshness lease → local effect-boundary enforcement → content/effect intent binding → preventive change claims → durable/anchored evidence → independent verification → release gate.**

This preserves the external-authority principle while making partition, latency, identity, concurrency and tamper-detection behavior explicit and testable.