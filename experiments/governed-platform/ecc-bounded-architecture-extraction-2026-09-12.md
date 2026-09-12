# ECC Bounded Architecture Extraction — 2026-09-12

Status: **EVIDENCE_ONLY / NOT_PROMOTED / NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This artifact refines `experiments/governed-platform/ecc-competitive-falsification-baseline.md`. It does not replace that baseline, modify the V17 WDPC candidate, or promote any ECC capability into an authoritative platform requirement.

## 1. Frozen comparison identities

### External system

- Repository: `affaan-m/ECC`
- Frozen `main` commit: `1ed03ecf2ec91aac77f3c98094d7d1136e89b4d4`
- Frozen tree: `f9faf8e9c7d3013831ae5f2e6ac9484d4c195be9`
- Current public package/release line observed during research: `2.2.1`

### Governed platform

- Main baseline commit containing the competitive falsification baseline: `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`
- Current WDPC V17 candidate used for architecture comparison: `da39da9ea02af6915d4283f6a09c6d18212fa4ed`
- Integrated governed MVP contract: `experiments/governed-platform/INTEGRATED_GOVERNED_MVP_CONTRACT.md`
- External evidence validation: `standards/external-evidence-semantic-validation.md`
- Continuity standard: `standards/conversation-continuity-and-resumption-control.md` on the continuity branch
- Existing ECC competitive baseline: `experiments/governed-platform/ecc-competitive-falsification-baseline.md`

## 2. Classification vocabulary

- `ALREADY_COVERED` — the governed platform already has the requirement/invariant, generally with equal or stronger authority semantics.
- `IMPROVES_EXISTING` — ECC supplies a useful implementation/UX/evidence pattern for a requirement already present.
- `NEW_REQUIREMENT_CANDIDATE` — ECC exposes a capability not yet clearly represented as a first-class governed-platform requirement. Candidate only; no promotion occurs here.
- `REJECT_FOR_GOVERNANCE` — the ECC behavior is acceptable as a worker/productivity mechanism but must not be accepted as authority or qualification in the governed platform.
- `INSUFFICIENT_EVIDENCE` — primary-source evidence is not enough to claim the capability as implemented/enforced at the frozen revision.

## 3. Bounded capability extraction

| ID | ECC capability at frozen revision | Primary ECC evidence | Governed-platform mapping | Classification | Bounded disposition |
|---|---|---|---|---|---|
| ECC-01 | Cross-harness packaging/adapters across Claude Code, Codex, OpenCode/Cursor/Gemini/Zed/Kimi and related workflows | `README.md`; `docs/releases/2.0.0/release-notes.md`; package/plugin manifests | Model/provider/harness independence is already a platform principle, but packaging/adapters are less mature | `IMPROVES_EXISTING` | Adapt adapter/conformance ideas beneath the governor; never let harness-specific state become governance authority |
| ECC-02 | Blueprint planning with dependency graph, cold-start step briefs, rollback strategy and plan mutation protocol | `skills/blueprint/SKILL.md` | Continuity/checkpoint and workflow-state governance already exist conceptually | `IMPROVES_EXISTING` | Use self-contained step briefs and dependency graphs as worker planning artifacts bound to authoritative workflow state |
| ECC-03 | Fresh-context review / isolated steps using separate agent contexts | `README.md`; `skills/autonomous-loops/SKILL.md`; `skills/blueprint/SKILL.md` | Reviewer isolation/clean-room rules in WDPC are stricter and authority-aware | `ALREADY_COVERED` | ECC fresh-context pattern may improve implementation ergonomics but cannot substitute for reviewer-independence evidence |
| ECC-04 | Eval-driven development with capability/regression evals, deterministic/model/human graders, pass@k/pass^k and versioned evals | `skills/eval-harness/SKILL.md` | Governed platform already uses preregistered falsification, hidden expectations, deterministic gates and manual review | `IMPROVES_EXISTING` | Adapt developer-facing eval ergonomics and metrics; PASS labels remain evidence only unless governor requirements are satisfied |
| ECC-05 | Hash-linked local capsule journal with predecessor links, canonical envelopes, projections and verification | `docs/architecture/eval-harness-frameworks.md`; `skills/eval-harness/SKILL.md` | Append-only evidence/GEL/WAS and preserved-history concepts already exist | `IMPROVES_EXISTING` | Consider capsule as worker-local evidence adapter, never as sole authoritative governance ledger |
| ECC-06 | Content-addressed replay fixtures and explicit effect classes `SE0..SE4` | `docs/architecture/eval-harness-frameworks.md` | Deterministic replay and consequential-effect gating already exist in platform architecture | `IMPROVES_EXISTING` | Reuse taxonomy/tooling concepts if mapped to platform capability and side-effect authority; declarations alone are not permissions |
| ECC-07 | Offline receipts over capsule/artifact/gate digests with verification and detached-signature interface | `docs/architecture/eval-harness-frameworks.md` | Platform already requires exact artifact/evidence binding and immutable references | `IMPROVES_EXISTING` | Useful evidence transport/verification primitive if bound into platform authority lineage |
| ECC-08 | Candidate execution is disabled because no verified OS containment backend exists; trust flags cannot enable it | `docs/architecture/eval-harness-frameworks.md`; `examples/eval-harness/README.md` | Fail-closed execution and external authority are already core platform rules | `ALREADY_COVERED` | Strong alignment; preserve the same anti-false-green posture for any future worker sandbox |
| ECC-09 | Session save/resume files, deterministic candidate ranking, preserved failed approaches and explicit user confirmation before work resumes | `commands/resume-session.md`; session hooks/docs | Conversation continuity standard already says conversation is not authority and durable state wins | `ALREADY_COVERED` | ECC session briefing is useful UX, but session files remain advisory unless bound to authoritative checkpoints |
| ECC-10 | Project-scoped continuous-learning observations become confidence-scored instincts and may evolve/promote into skills/agents | `skills/continuous-learning-v2/SKILL.md` | Platform has evidence/promotion governance but no equally explicit learned-behavior lifecycle | `NEW_REQUIREMENT_CANDIDATE` | Create a governed learning-proposal lifecycle where observations/instincts are evidence only until qualified; retain project scope and contamination controls |
| ECC-11 | Confidence/repetition/no-correction can increase instinct confidence; multi-project recurrence can trigger promotion candidates | `skills/continuous-learning-v2/SKILL.md` | EXP-J/EXP-K prohibit consensus/repetition/confidence from becoming authority | `REJECT_FOR_GOVERNANCE` | Confidence may rank proposals but cannot authorize policy/skill promotion or widen authority |
| ECC-12 | Learned/imported skill provenance schema requires `source`, `created_at`, `confidence`, `author` | `schemas/provenance.schema.json` | Governed platform requires much richer candidate/evidence/authority/supersession bindings | `REJECT_FOR_GOVERNANCE` | Accept only as non-authoritative metadata; insufficient for governed provenance or promotion |
| ECC-13 | AgentShield scans agent/harness configuration, hooks, MCP, permissions, secrets and prompt-injection risks; supports CI/report formats | `skills/security-scan/SKILL.md`; AgentShield architecture/roadmap references | Platform has authority/credential/security gates but no equally productized AI-harness configuration scanner | `NEW_REQUIREMENT_CANDIDATE` | Add an AI-agent configuration security evidence source; scanner results can block or escalate under policy but scanner PASS is never qualification by itself |
| ECC-14 | Red/blue/auditor model pipeline for deeper security analysis | `skills/security-scan/SKILL.md` | Platform already separates model judgment from deterministic evidence/authority | `REJECT_FOR_GOVERNANCE` | Use outputs as engineering evidence only; multi-model agreement cannot grant security qualification |
| ECC-15 | Worktree-lifecycle service provides deterministic conflict prediction and safe cleanup for parallel agent worktrees | `docs/releases/2.0.0/release-notes.md`; `scripts/lib/worktree-lifecycle/` | WDPC governs workflow drift/concurrency authority but does not yet expose a first-class physical worktree-conflict lifecycle | `NEW_REQUIREMENT_CANDIDATE` | Add authority-neutral worktree/session collision evidence and lease/conflict state for parallel workers |
| ECC-16 | Harness-neutral control-plane view joins sessions, working sets, proximity, lanes, events and declared coordination inventory | current `main` control-plane commit/docs; `ecc.session.v1` release notes | Platform has governance state but not a comparable live multi-agent collision/proximity surface | `NEW_REQUIREMENT_CANDIDATE` | Add multi-agent collision telemetry as evidence/advisory; governor remains sole authority for blocking/rerouting consequential work |
| ECC-17 | Planned TCAS-style pre-edit hook can steer/pause overlapping agents using centrally computed right-of-way | current-head `TCAS-HOOK.md` diff in commit `1ed03ecf...` | Potential execution-coordination mechanism | `INSUFFICIENT_EVIDENCE` | At frozen head the hook document explicitly says design-only; additionally planned error handling fails open, so it cannot be treated as authoritative coordination evidence yet |
| ECC-18 | Normalized MCP inventory across harnesses with fragmentation/drift detection and secret redaction | `docs/releases/2.0.0/release-notes.md` | Platform has provider/plugin concepts but no first-class cross-harness MCP/config drift inventory located in reviewed contracts | `NEW_REQUIREMENT_CANDIDATE` | Add governed inventory of agent/harness external-tool configuration, identity, drift and redacted secret exposure as security/continuity evidence |
| ECC-19 | Autonomous sequential/PR/DAG loops with worktrees, CI repair, model routing and fresh-context passes | `skills/autonomous-loops/SKILL.md` | Platform already supports replaceable workers and governed execution concepts | `IMPROVES_EXISTING` | Use as worker/orchestration pattern only under externally issued capabilities and terminal-authority separation |
| ECC-20 | Auto-merge after CI and model-generated completion signals in example autonomous-loop patterns | `skills/autonomous-loops/SKILL.md` | Platform explicitly separates execution success from RELEASE/DEPLOY/MERGE/completion authority | `REJECT_FOR_GOVERNANCE` | Never allow CI green, completion phrases or worker-loop state to self-grant merge/release/completion authority |
| ECC-21 | Evidence-first research ops separates sourced fact, supplied evidence, inference and recommendation | `skills/research-ops/SKILL.md` | EXP-J external semantic-evidence validation is already stricter and promotion-gated | `ALREADY_COVERED` | ECC format is useful UX, but platform evidence contracts and source hierarchy remain authoritative |
| ECC-22 | Multi-agent orchestration/DAG/worktree patterns and dynamic workflow teams | `skills/autonomous-loops/SKILL.md`; `docs/releases/2.0.0/release-notes.md` | Parent/child/workflow governance exists but execution-layer parallelization can be improved | `IMPROVES_EXISTING` | Adapt orchestration ergonomics while retaining parent/child authority, exact candidate binding and conflict controls |

## 4. New requirement candidates — not promoted

The extraction exposes four candidate requirement families worth separate falsification. They remain `DISCOVERED / NOT_PROMOTED`.

### NR-ECC-01 — Multi-agent physical work collision and deconfliction evidence

Potential requirement:

> The platform should maintain an authority-neutral, exact-worktree-bound view of active worker working sets and detect overlap/dependency/collision risk before conflicting consequential writes. Collision telemetry may trigger a governed hold/reroute/review decision but cannot itself grant or revoke authority.

Needed falsification before promotion:

- stale working-set telemetry;
- two sessions racing before telemetry refresh;
- advisory producer compromised or unavailable;
- false-positive overlap causing permanent block;
- false-negative dependency collision;
- actor relabels files/tasks to evade collision detection;
- authoritative governor disagrees with advisory;
- crash/restart preserves or safely invalidates collision state.

### NR-ECC-02 — Parallel worktree/session lifecycle registry

Potential requirement:

> Parallel workers should have durable worktree/session identity, ownership/lease state, base/candidate binding, conflict state, heartbeat/liveness and safe cleanup semantics. Cleanup/advisory logic must not delete or rewrite evidence needed by governance.

Needed falsification before promotion:

- stale worker cleanup while still active;
- worktree reused by another worker;
- base branch changed under worker;
- conflicting cleanup and merge/review operations;
- abandoned worker with uncommitted governed evidence;
- lease/fencing failure and split-brain ownership.

### NR-ECC-03 — AI-harness configuration inventory and security evidence

Potential requirement:

> The platform should maintain a normalized, versioned inventory of installed agent/harness configuration surfaces—including MCP/tool servers, hooks, permissions, external commands, agent/skill definitions and relevant secret references—and produce governed drift/security evidence when they materially change.

Needed falsification before promotion:

- scanner misses configuration outside known paths;
- config alias/symlink bypass;
- secret redaction removes evidence needed for adjudication;
- scanner PASS launders unsafe runtime behavior;
- stale inventory after harness update;
- scanner/candidate self-modification;
- multi-harness semantic mismatch for equivalent permissions.

### NR-ECC-04 — Governed learning-proposal lifecycle

Potential requirement:

> Session observations and repeated successful patterns may create scoped learning proposals, but frequency, confidence, model consensus or absence of correction must never directly promote a skill, policy, rule or authority. Promotion requires governed evidence, exact scope, provenance, conflict/retraction handling and policy-defined independent review where material.

Needed falsification before promotion:

- repeated wrong pattern gains confidence;
- malicious session poisons a project instinct;
- project-specific rule promoted globally;
- inherited/imported skill lacks authoritative source;
- correction fails to retract derived learned behavior;
- same model produces observation and approval;
- user silence treated as approval;
- stale learned rule survives architecture/policy change.

## 5. Important adoption candidates that are not new governance requirements

The following are strong implementation candidates but do not currently justify a new governance invariant:

1. ECC capsule + receipt format as a worker-local evidence adapter.
2. Content-addressed fixture replay and effect-class ergonomics.
3. Blueprint cold-start plans and dependency/rollback briefs.
4. Eval-harness developer UX and pass@k/pass^k reporting.
5. Multi-harness install/adapter conformance tooling.
6. Session-resume briefings that explicitly preserve failed approaches.

Any implementation adoption must map outputs into existing governed evidence/authority contracts rather than treating ECC labels or receipts as self-authorizing.

## 6. Rejected authority translations

The following patterns must not be imported as governance authority:

- instinct confidence or repetition -> policy authority;
- multi-project recurrence -> global rule authority;
- model-based grader/reviewer agreement -> qualification authority;
- AgentShield grade/PASS -> security qualification;
- CI success -> merge/release authority;
- model completion phrase -> completion authority;
- local session summary -> authoritative workflow state;
- hash-linked capsule by itself -> tamper-proof global governance ledger;
- declared effect class -> permission to perform the effect;
- planned TCAS fail-open hook -> authoritative write-conflict gate.

## 7. Evidence limitations observed in ECC

Primary-source inspection also found explicit ECC limitations that matter to the comparison:

- candidate execution in the eval harness is intentionally unavailable pending a separately reviewed OS containment backend;
- effect classes are declarations, not OS permissions;
- the local capsule has no transaction/exactly-once/power-loss guarantee and cannot prevent replacement of the whole log;
- witnessed transparency is described as a later/optional layer;
- some security capabilities are static/configuration-focused rather than a complete runtime governance boundary;
- the TCAS pre-edit hook in the frozen latest commit is design-only, not implemented;
- cross-harness support is not full feature parity.

These limitations are not criticisms by themselves; several show strong non-overclaiming discipline and align with the governed platform's anti-false-green posture.

## 8. Recommended next experiments

These are proposed research/falsification tasks only.

### EXP-ECC-A — Worker-local capsule evidence adapter

Test whether ECC-style capsule/receipt/replay artifacts can be ingested as `EVIDENCE_ONLY` by the governed platform while the platform ledger remains authoritative.

Hard negatives:

- locally valid capsule from wrong candidate;
- replaced whole capsule with recomputed local chain;
- duplicate event after ambiguous acknowledgement;
- stale replay fixture;
- effect-class declaration inconsistent with real requested platform capability.

### EXP-ECC-B — Multi-agent collision telemetry

Prototype an authority-neutral collision evidence object inspired by ECC worktree/proximity data. The governor decides `ALLOW | HOLD | REROUTE | HUMAN_REQUIRED`; telemetry itself has no transition authority.

### EXP-ECC-C — Harness configuration inventory/security evidence

Run a bounded static inventory/security pass over governed development configuration and map findings to evidence classes. Test false negatives, stale inventory, scanner self-modification and PASS laundering.

### EXP-ECC-D — Governed learning proposals

Create session-derived pattern proposals but require deterministic scope/provenance checks and independent promotion policy. Inject repeated false patterns and contradictory corrections.

## 9. Effect on existing competitive baseline

The existing ECC competitive baseline remains valid and `NOT_EXECUTED`.

This extraction strengthens the reason to run that benchmark, but it does not establish that ECC is safer, less safe, superior, inferior, or equivalent to the governed platform in live execution. It only establishes capability overlap and candidate lessons at the frozen source revision.

## 10. Current disposition

- ECC as replacement for governed authority layer: **NOT_SUPPORTED**
- ECC/ECC-style harness as replaceable worker/execution layer: **SUPPORTED AS A DESIGN DIRECTION, NOT QUALIFIED**
- New requirement candidates discovered: **4**
- Automatic requirement promotion performed: **NO**
- V17 candidate modified: **NO**
- Competitive baseline execution status: **NOT_EXECUTED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
