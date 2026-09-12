# Frozen ECC Capability and Governance Audit — V1

Status: **AUDIT COMPLETE — RESEARCH EVIDENCE ONLY — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Exact bindings

External subject:

- Repository: `affaan-m/ECC`
- Exact audited commit: `b6ddd13a9f6ec2ccf55bc1773d52391c5afc05ab`

Comparison baseline:

- Repository: `vij7661/setugo-ai-development-framework`
- Exact V18 baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`
- V18 tree: `ccf60849f455be1a45c2a1096e83291519cc5d43`

This audit does not modify, supersede, qualify, freeze, or promote V18. It is preserved on a separate research branch only.

## 2. Audit scope and completeness statement

The frozen ECC repository surface was reconciled against the exact commit rather than sampled from README descriptions.

Canonical inventory:

- 292 canonical `skills/*/SKILL.md` entries;
- 94 canonical `commands/*.md` entries;
- 68 canonical `agents/*.md` entries;
- 24 configured hook lifecycle entries across the active hook configuration, plus their dispatcher/bootstrap child execution paths;
- workflow/orchestration code;
- install/consent and cross-harness capability code;
- MCP inventory/configuration code;
- GitHub coordination and release-gate code;
- session/memory/learning code;
- consequential side-effect skills including publishing, messaging, payment, review, PR/release, and autonomous-loop surfaces.

Every canonical skill/command/agent identity was catalog-reconciled and risk-triaged. A full behavioral read was then performed for surfaces capable of one or more of the following: state mutation, model invocation, permission/configuration change, persistence, memory/learning promotion, review/approval, merge/release/publish, external side effect, credential use, or multi-agent orchestration.

Ordinary language/framework/domain guidance such as React, Django, Kotlin, database, styling, and similar implementation-pattern skills was catalog-reconciled but was not treated as equivalent in governance risk to authority-bearing runtime surfaces. This report therefore does **not** claim a line-by-line semantic review of every ordinary domain skill; it claims complete inventory reconciliation plus exhaustive risk-directed review of consequential control surfaces.

## 3. Overall disposition

**ECC contains many strong worker-level safety, evidence, review, isolation, and operational patterns, but it does not implement one uniform platform-wide evidence/authority model.**

The repository is internally heterogeneous:

- some components carefully distinguish evidence from authority and fail closed;
- some components treat model agreement, text state, confidence, or workflow status as sufficient for consequential progression;
- some hook/runtime components are deliberately availability-first and fail open on internal enforcement failures;
- some documentation claims stronger enforcement than the executable path can guarantee.

The governed platform should therefore **adapt selected ECC mechanisms behind the existing governor** rather than adopt ECC workflow semantics wholesale.

The audit found no reason to mutate V18 directly. Most ECC authority failures are already blocked by V18 or inherited platform contracts. The additive value is concentrated in enforcement-surface attestation, cross-harness capability qualification, capability-change consent, configuration drift attestation, and declared-vs-executable control equivalence.

## 4. Classification vocabulary

- `ALREADY_COVERED` — the governed platform already contains a materially stronger or equivalent rule.
- `IMPROVES_EXISTING` — ECC exposes a useful strengthening or implementation dimension for an existing platform concept.
- `NEW_REQUIREMENT_CANDIDATE` — materially useful behavior not yet explicit enough in the active platform contract; still evidence only.
- `IMPLEMENTATION_INSPIRATION` — useful implementation/UX pattern that does not itself require a new governance rule.
- `REJECT_AS_AUTHORITY_SHORTCUT` — behavior may be acceptable inside a local worker workflow but must never satisfy governed authority.

## 5. Capability-by-capability findings

| ECC capability / pattern | Classification | Audit conclusion |
|---|---|---|
| `operator-approval-loop` exact draft/hash/epoch/destination binding, reservation before dispatch, unknown-delivery handling | `IMPLEMENTATION_INSPIRATION` / `ALREADY_COVERED` | Strong local implementation pattern. The platform Slice 10 external side-effect gateway is already stronger systemically through exact intent, deterministic idempotency, use-time authority, reconciliation, and outcome-unknown states. |
| `orch-review` multi-dimensional reviewers + finding dedup + adversarial verification of HIGH/CRITICAL | `IMPLEMENTATION_INSPIRATION` | Useful evidence enrichment. Raw reviewer provenance and disagreement must remain preserved; verifier/model outcomes remain evidence only. |
| `council-multi-model` external critique only, user decides, provider relationship labeled, transfer consent required | `IMPROVES_EXISTING` | Strong review-egress and provider-diversity honesty pattern. Useful for future runtime review transport, not for current manual-only testing. |
| `council` raw dissent preserved, fresh subagents, user decides | `IMPLEMENTATION_INSPIRATION` | Good decision-support UX but not independent manual-review evidence. |
| `santa-method` dual model PASS => NICE => SHIP | `REJECT_AS_AUTHORITY_SHORTCUT` | Model consensus cannot mint shipping authority. Dual review may be retained only as engineering evidence. |
| Continuous Claude PR loop auto-fix + auto-merge + model completion signal | `REJECT_AS_AUTHORITY_SHORTCUT` | Merge/release/completion authority cannot come from CI green or a model magic phrase. |
| Ralphinho/DAG worktree isolation and merge-queue eviction context | `IMPLEMENTATION_INSPIRATION` / `ALREADY_COVERED` | Good execution ergonomics. Existing repository gateway, fencing, lineage, parent-child/workshare controls remain the authority boundary. |
| `multi-execute` single-writer filesystem sovereignty | `IMPROVES_EXISTING` | Single-writer mutation ownership is useful; model-specific “backend authority” / “frontend authority” terminology must remain non-governance role labeling only. |
| `code-review` GitHub APPROVE/REQUEST_CHANGES with operator override flags | `REJECT_AS_AUTHORITY_SHORTCUT` | Operator action may exist, but override must be an authenticated scoped authority object bound to exact candidate; findings and authority are separate. |
| GitHub coordination `applyReview` / `applyPublish` text state | `REJECT_AS_AUTHORITY_SHORTCUT` / `ALREADY_COVERED` | Self-asserted `approved` state is insufficient. V18/inherited anti-self-grant and exact-binding controls already cover this class. |
| GitHub coordination issue claim with best-effort refetch, no CAS | `ALREADY_COVERED` | Existing atomicity/fencing/idempotency controls are materially stronger. Keep as corroborating falsification evidence. |
| release approval gate parses Markdown owner decision rows | `REJECT_AS_AUTHORITY_SHORTCUT` / `ALREADY_COVERED` | Static `approved` text is not authenticated principal authority and is not exact-SHA approval evidence. |
| `delivery-gate` deterministic facts only | `IMPLEMENTATION_INSPIRATION` | Strong fact-vs-judgment separation. Appropriate for local preflight facts. |
| `eval-harness` containment honesty; refuses unsupported secure-execution claim | `IMPLEMENTATION_INSPIRATION` | Strong claim-boundary discipline and negative-evidence handling, aligned with Slice 4 nonclaims. |
| `skill-comply` competing-prompt compliance tests and tool traces | `IMPROVES_EXISTING` | Strong falsification harness pattern. LLM grader/classifier is evidence, not authority. |
| `spec-miner` enforcement/test/commit anchors and explicit uncertainty | `IMPLEMENTATION_INSPIRATION` | Useful provenance-rich spec mining. Generated specs remain proposals until governed acceptance. |
| `living-docs-governance` one canonical owner, untrusted linked docs, correction history | `ALREADY_COVERED` / `IMPLEMENTATION_INSPIRATION` | Strongly corroborates source precedence, history preservation, and anti-laundering rules already present in EXP-J/EXP-K/continuity. |
| `unified-memory` untrusted/unreviewed/create-only memory | `ALREADY_COVERED` | Consistent with EXP-K and continuity standard: memory is advisory context, never authority. |
| session-start/session-end summaries and learned-instinct injection | `ALREADY_COVERED` | Useful continuity convenience only. It must lose to governed durable state on conflict or interruption. |
| continuous-learning confidence/repetition and automatic application | `IMPROVES_EXISTING` / `REJECT_AS_AUTHORITY_SHORTCUT` | Learning output may propose behavior; repetition, lack of correction, or model agreement cannot promote policy/requirements. |
| `/evolve --generate` commands/skills/agents from confidence clusters | `IMPROVES_EXISTING` | Generated artifacts must be typed `PROPOSAL`, independently validated, and cannot become active rules by generation alone. |
| x402 payment budget/limit checks owned by orchestrator | `IMPLEMENTATION_INSPIRATION` | Good local budget boundary. Any real payment remains behind platform terminal/credential/side-effect authority. |
| email/messages/social publishing/billing skills | `ALREADY_COVERED` | Consequential effects belong behind Slice 10; successful provider action never grants completion authority. |
| cross-harness Native / Adapter-backed / Instruction-backed / Reference-only capability classification | `NEW_REQUIREMENT_CANDIDATE` | Strong missing abstraction: enforcement parity must be qualified explicitly, not inferred from installing the same instructions. |
| hook installation capability disclosure + explicit consent | `NEW_REQUIREMENT_CANDIDATE` | Enabling mutation/egress/persistence/process-control powers should require exact capability-manifest consent. |
| canonical MCP inventory + secret redaction + cross-harness drift detection | `NEW_REQUIREMENT_CANDIDATE` | Tool/MCP config should be attested and drift should stale dependent capability qualification. |
| hook config plus fail-open wrappers/bootstrap | `NEW_REQUIREMENT_CANDIDATE` | `HOOK_CONFIGURED` is not evidence of `HOOK_EXECUTED` or `HOOK_ENFORCED`; enforcement status must be explicit and fail closed when policy requires the control. |
| `chief-of-staff` claim that hook enforcement makes skipping physically impossible | `NEW_REQUIREMENT_CANDIDATE` | Declared control strength must be mechanically consistent with executable failure semantics. Documentation cannot upgrade fail-open code into a blocking guarantee. |
| provider relationship labeling in `council-multi-model` | `IMPROVES_EXISTING` | Same-provider critique must not be represented as heterogeneous independence. Existing provider telemetry can carry this extension but currently focuses on execution telemetry rather than review-diversity authority. |

## 6. Existing platform controls confirmed by ECC adversity

### 6.1 Consensus does not create authority

ECC Santa-style dual PASS and multi-model role labels demonstrate why the existing rule remains necessary: agreement is evidence, not authority. The active platform external-evidence standard already makes missing deterministic evidence non-bypassable by Researcher/Judge/model agreement.

### 6.2 Conversational/session memory cannot be authoritative

ECC session summaries, learned instincts, and memory vaults are useful convenience layers. The active continuity and conversational-drift standards already require durable governed reconstruction and explicitly subordinate conversation, summary, and memory to authoritative state.

### 6.3 External side effects require intent-first durable state and reconciliation

ECC operator approval and x402 patterns support the same design direction as Slice 10. The platform already requires durable intent before dispatch, deterministic external idempotency, outcome-unknown reconciliation, use-time authority/lease checks, response integrity, and non-duplication.

### 6.4 Tool success is not terminal authority

ECC autonomous loops and release flows show why a worker/CI/model success signal cannot become release/completion state. Slice 4 and later terminal/side-effect slices already separate execution result from terminal authority.

### 6.5 Self-granted review/approval state must fail

ECC GitHub coordination and Markdown approval gates expose a direct false-green pattern: text state says `approved`, then later logic treats that as a gate. V18 root-governed anti-self-grant, exact binding, append-only lineage, and threshold controls are materially stronger and should remain authoritative.

### 6.6 Non-atomic coordination is not sufficient

ECC explicitly documents a best-effort issue-claim collision guard without server-side CAS. V18 and inherited platform mechanisms already require stronger atomicity, crash/retry non-amplification, durable idempotency, fencing, and lineage.

## 7. New / improved requirement candidates

These are **not accepted requirements**. They are candidate deltas for a future revision after the current V18 review sequence completes.

### ECC-AUD-REQ-01 — Enforcement Execution Attestation

A configured control is not equivalent to an executed control.

For any hook, adapter, gateway precondition, policy interceptor, or other enforcement mechanism that is required by a governed transition, retain an explicit lifecycle such as:

`CONTROL_CONFIGURED -> CONTROL_INVOCATION_ATTEMPTED -> CONTROL_EXECUTED -> CONTROL_VERIFIED`

with adverse states including:

- `CONTROL_BYPASSED`
- `CONTROL_FAILED_OPEN`
- `CONTROL_EXECUTION_FAILED`
- `CONTROL_ENFORCEMENT_UNKNOWN`
- `CONTROL_STALE`

A policy predicate requiring the control may be satisfied only by evidence proving the required execution/verification state for the exact action/candidate/runtime generation. Presence in config, installation receipt, or a wrapper exit code is insufficient.

### ECC-AUD-REQ-02 — Declared-vs-Executable Enforcement Equivalence

Any material claim such as “cannot skip”, “always blocks”, “physically enforced”, or “mandatory” must be traceable to the executable control and its failure semantics.

If the runtime has a fail-open path for missing script, parser error, oversized input, bootstrap failure, disabled hook, exception, unavailable shell/runtime, or similar condition, documentation may not describe that control as unconditionally blocking.

Mismatch must produce an explicit non-green state such as `DECLARED_ENFORCEMENT_RUNTIME_MISMATCH` and invalidate any qualification claim that depends on the stronger declaration.

### ECC-AUD-REQ-03 — Qualified Harness Capability Envelope

For every supported harness/provider/runtime, maintain a governed capability envelope that distinguishes at least:

- `NATIVE_ENFORCEMENT`
- `ADAPTER_ENFORCEMENT`
- `INSTRUCTION_ONLY`
- `REFERENCE_ONLY`
- `UNSUPPORTED`

The envelope should bind exact harness/runtime/adapter version, relevant configuration digest, required tools/hooks, isolation properties, limitations, qualification evidence, freshness/expiry, and supersession state.

A policy requiring native or adapter enforcement must fail closed when only instruction-level parity exists. Installing the same prompt/rules across Claude/Codex/Gemini/other harnesses must not be treated as proof of equivalent enforcement.

### ECC-AUD-REQ-04 — Capability Activation / Power-Surface Consent

Introducing or materially widening a runtime capability that can mutate source, launch processes, persist state, access tools/MCP, transmit transcripts/data to another provider, or perform external side effects should require a governed activation record bound to the exact capability manifest and version.

The activation record should identify what powers are enabled, egress/persistence implications, scope, approving principal, effective sequence, expiry/revocation where applicable, and exact configuration digest.

Silent installation or upgrade must not widen authority.

### ECC-AUD-REQ-05 — Cross-Harness Tool/MCP Configuration Attestation

Maintain a canonical, secret-safe tool/MCP inventory across supported harnesses. Bind logical server/tool identity, transport/type, non-secret configuration digest, credential-profile identity without secret value, harness exposure, capability envelope generation, and currentness.

Material drift must stale dependent capability qualification until revalidated. Secret values must not appear in comparison evidence.

### ECC-AUD-REQ-06 — External Review Egress and Provider-Relationship Binding

For future automated/runtime reviewer transport only, an outbound review packet should bind:

- exact packet digest;
- exact destination/provider class;
- allowed data classes;
- user/admin consent when required by policy;
- provider relationship classification (`cross-provider`, `same-provider`, `unverified`);
- tool/isolation envelope used by the external reviewer;
- explicit result class when the external critique is absent or unverifiable.

Same-provider invocation must never be counted as provider diversity merely because it is a separate process/session.

This candidate does **not** change the current testing rule: testing remains manual-review transport only unless the user explicitly changes that policy.

### ECC-AUD-REQ-07 — Learned-Artifact Proposal Boundary

If the product later supports continuous learning that generates reusable rules, skills, hooks, commands, agents, policies, or workflow changes, every generated artifact begins as a non-authoritative proposal.

Confidence, repetition, absence of correction, clustering, or multiple-model agreement may prioritize a proposal but may not promote it into governed active policy. Promotion must use the applicable semantic evidence, source/provenance, falsification, change-control, and authority rules.

This is largely implied by EXP-J/EXP-K but should become explicit if auto-learning becomes a product feature.

## 8. Proposed falsification vectors for the candidates

These are audit-derived future cases only; they are not added to V18 by this report.

- `ECC-AUD-F01`: security hook appears in configuration but script is missing; governed action must not count the control as enforced.
- `ECC-AUD-F02`: required hook throws internally and wrapper exits success; governor must record failed-open/unknown and block any transition requiring that hook.
- `ECC-AUD-F03`: hook input exceeds wrapper limit and the wrapper suppresses execution; required enforcement cannot become green.
- `ECC-AUD-F04`: bootstrap path resolution/runtime failure causes no-op success; control qualification becomes insufficient, not PASS.
- `ECC-AUD-F05`: harness exposes only instruction-backed safety while policy requires native/adapter enforcement; transition denied.
- `ECC-AUD-F06`: qualified adapter version changes outside its tested envelope; capability becomes stale until requalification.
- `ECC-AUD-F07`: hook/tool installation silently enables transcript egress or source mutation without a matching activation record; capability denied.
- `ECC-AUD-F08`: MCP/tool configuration changes while logical name stays the same; dependent capability qualification is invalidated.
- `ECC-AUD-F09`: documentation claims “cannot skip” while an executable fail-open path exists; declared-vs-runtime equivalence check fails.
- `ECC-AUD-F10`: same-provider second invocation is labeled independent cross-provider review; diversity claim rejected.
- `ECC-AUD-F11`: external reviewer packet is sent to a provider outside the approved egress binding; result remains inadmissible for the governed gate.
- `ECC-AUD-F12`: high-confidence learned instinct generates a new rule and attempts direct activation; artifact remains proposal-only and cannot alter authority.
- `ECC-AUD-F13`: control executes successfully but against a different candidate/runtime/config digest; enforcement evidence is stale/mismatched.
- `ECC-AUD-F14`: observability/telemetry records control configuration but no execution receipt; dashboard must show unknown/not-executed rather than infer enforcement.
- `ECC-AUD-F15`: fully qualified native control executes against the exact candidate/configuration and verified receipt is present; legitimate transition remains live and is not overblocked.

## 9. ECC patterns explicitly rejected as governance authority

The following may exist as local worker behaviors but cannot satisfy a governed terminal transition:

1. two model reviewers PASS, therefore ship;
2. model or CI success, therefore auto-merge;
3. repeated model completion magic phrase, therefore complete;
4. a Markdown row says `approved`, therefore release;
5. a workflow state field is set to `approved` by the same automation being evaluated;
6. provider HTTP success, credential possession, or reviewer agreement, therefore completion;
7. a high-confidence learned instinct becomes active policy automatically;
8. a named model is assigned “backend authority” or “frontend authority”, therefore its judgment has governance authority;
9. a hook is present in configuration, therefore it ran;
10. a session summary or memory entry says a stage is complete, therefore the durable workflow advanced.

## 10. ECC mechanisms worth adapting behind the governor

High-value implementation inspirations include:

- operator approval exact-effect binding and reservation-before-dispatch;
- finding-level adversarial verification in `orch-review`;
- deterministic-vs-model-vs-human grader separation in eval tooling;
- explicit “containment not proven” behavior rather than weak sandbox claims;
- tool-call timeline capture for compliance falsification;
- enforcement-point/test/commit anchors in spec mining;
- one-canonical-owner and correction-history discipline in living docs;
- untrusted/create-only memory vault semantics;
- provider relationship labeling and minimal-packet review transfer;
- single-writer filesystem sovereignty in multi-model execution;
- worktree isolation and conflict/eviction context in DAG execution;
- canonical secret-redacted MCP inventory and configuration drift detection;
- install-time capability disclosure and explicit consent.

These should be integrated only through platform-owned contracts. ECC skill prose, command names, model labels, or local state files must not become authority objects themselves.

## 11. Comparison to active V18 and inherited platform contracts

The active platform baseline already covers the main authority classes exposed by ECC:

- V18 atomic threshold commit/recovery, root-governed ledger mutation, prospective reuse, dependency revalidation, anti-rollback/fork and witnessed lineage;
- conversation/session/device interruption as non-authoritative and durable checkpoint reconstruction;
- EXP-K separation of hypotheses, claims, accepted decisions and governed requirements, with consensus/repetition explicitly non-evidentiary;
- external semantic evidence contracts that prevent model/Judge agreement from bypassing missing primary/functional evidence;
- exact tool-runner contract/manifest binding, environment minimization, durable idempotency and explicit nonclaims;
- external side-effect durable intent, deterministic idempotency, reconciliation-before-retry, outcome-unknown handling, current authority/lease checks, secret safety, and provider-success/terminal-authority separation;
- provider-neutral review telemetry with preserved retries and authority isolation;
- scoped capabilities that are platform-issued, use-time revalidated, revocable and non-widenable by models.

Therefore the ECC audit does not justify reopening solved V18 mechanisms merely because ECC expresses similar concepts with different names.

## 12. Final audit disposition

**ECC_FROZEN_AUDIT_COMPLETE**

The audit supports the following bounded conclusion:

1. ECC is a valuable source of worker-level implementation patterns, especially around adversarial review, approval-loop mechanics, memory hygiene, tool isolation honesty, cross-harness support disclosure, and configuration inventory.
2. ECC is not suitable as a direct authority model for the governed platform because consequential semantics vary across subsystems and include multiple consensus/text-state/confidence/auto-merge shortcuts.
3. The governed platform is already materially stronger on authority/evidence separation, exact candidate binding, terminal authority, side-effect ambiguity, continuity, root governance, threshold lineage and anti-self-grant.
4. The most material additive ECC insight is **enforcement-surface assurance**: configured controls, adapters and hooks must prove that the expected enforcement actually executed under the exact qualified runtime/configuration rather than relying on installation/configuration presence.
5. Seven requirement candidates and fifteen falsification vectors are retained above as research evidence only. None is promoted by this audit.
6. V18 remains unchanged and requires its existing review/qualification path.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
