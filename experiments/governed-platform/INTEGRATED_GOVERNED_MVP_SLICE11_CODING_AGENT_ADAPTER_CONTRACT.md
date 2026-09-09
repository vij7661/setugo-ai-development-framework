# Integrated Governed MVP Slice11 — Coding Agent Adapter Contract

Status: TESTING PHASE / FROZEN CONTRACT

## Objective

Introduce a provider-neutral `CodingAgentAdapter` boundary so any coding agent can be attached without changing governance semantics. The agent may decide how to perform coding work inside the governed task boundary; governance alone decides whether its result is acceptable.

This is a testing/falsification contract for release-quality code. It is not a production-readiness claim.

## Nonclaims

This Slice does not claim:
- support for every real coding-agent API or CLI;
- production credential, IAM, deployment, or release readiness;
- that an agent result is trustworthy because the agent reports success;
- that agent consensus is authority;
- that a coding agent may merge, release, deploy, alter phase state, or self-adjudicate.

## Stable adapter model

Every adapter must expose a provider-neutral descriptor:
- `adapter_id`
- `agent_id`
- `agent_family`
- `agent_version`
- `capabilities`

Every governed task must bind:
- `task_id`
- `candidate_sha`
- `goal`
- `allowed_paths`
- `forbidden_paths`
- `acceptance_criteria`
- `required_tests`
- `forbidden_changes`
- `stop_conditions`

Every normalized result must contain:
- `task_id`
- `candidate_sha`
- adapter/agent identity
- `completion_state`
- `changed_artifacts`
- `commands_run`
- `test_results`
- `failure_classification`
- `execution_events`
- `authority_effect = NONE`

## Completion states

Allowed normalized states:
- `COMPLETED`
- `FAILED`
- `BLOCKED`
- `REQUIREMENT_UNRESOLVED`
- `CANCELLED`

## Failure classifications

Allowed failure/root-cause classes:
- `NONE`
- `CODE DEFECT`
- `FIXTURE-DATA DEFECT`
- `TEST DEFECT`
- `ENVIRONMENT-TOOLING DEFECT`
- `REQUIREMENT UNRESOLVED`
- `AGENT_ADAPTER_DEFECT`
- `SCOPE_VIOLATION`

## Frozen invariants

- **S11-I01 Provider neutrality:** governance logic must not branch on Codex, Claude Code, Gemini, OpenHands, Cursor, or any named coding agent.
- **S11-I02 Exact candidate binding:** task and result must bind the same exact 40-character lowercase Git SHA.
- **S11-I03 Stable task contract:** the adapter receives explicit goal, scope, acceptance, tests, forbidden changes, and stop conditions.
- **S11-I04 Scope containment:** changed artifacts outside `allowed_paths`, inside `forbidden_paths`, or matching explicit `forbidden_changes` are rejected.
- **S11-I05 Governance immutability boundary:** governance/evidence/phase-control files are denied by default unless the task explicitly authorizes the exact path and the caller enables governance mutation for that task.
- **S11-I06 Test integrity:** an agent may not silently modify required tests or acceptance artifacts merely to manufacture green. Any such modification must be explicitly authorized and returned as a material change for adjudication.
- **S11-I07 Result normalization:** arbitrary agent-native output must be translated into one governed schema before use.
- **S11-I08 No self-authority:** agent success, confidence, approval, review, or consensus never grants merge/release/deploy/promotion authority.
- **S11-I09 Requirement ambiguity stop:** when the contract is contradictory or insufficient, the normalized state must be `REQUIREMENT_UNRESOLVED`; the adapter must not invent the missing requirement.
- **S11-I10 Secret containment:** raw secrets/tokens/credential values must not be persisted in normalized task/result/event data.
- **S11-I11 Auditability:** commands, changed artifacts, test results, and execution events must be retained in normalized form sufficient for deterministic adjudication.
- **S11-I12 Failure preservation:** a failed execution remains evidence and cannot be rewritten as a clean success by a later adapter retry.
- **S11-I13 Adapter capability validation:** a task requiring capabilities the selected adapter does not advertise must fail closed before execution.
- **S11-I14 Idempotent result ingestion:** the same execution/result ID may be ingested repeatedly only if the normalized binding/content is identical; conflicting reuse is rejected.
- **S11-I15 Agent interchangeability:** two different adapters satisfying the same capabilities may execute the same governed task without changing the task/governance contract.
- **S11-I16 Phase policy inheritance:** in `TESTING`, coding-agent execution does not trigger external reviewer API calls; review remains manual by default and is requested separately when needed.
- **S11-I17 Terminal actions prohibited:** no adapter API exposed by this Slice can merge, release, deploy, promote phase state, or grant terminal authority.
- **S11-I18 Abrupt-stop continuity:** execution state must be resumable/reconcilable from durable normalized state rather than conversational/model memory.

## Acceptance cases

At minimum, executable tests must cover:
1. generic adapter registration and descriptor validation;
2. two differently named fake adapters executing the same task contract;
3. exact SHA mismatch rejection;
4. missing required capability rejection before dispatch;
5. allowed-path change accepted;
6. out-of-scope change rejected;
7. forbidden-path/governance mutation rejected by default;
8. required-test mutation rejected unless explicitly authorized;
9. `REQUIREMENT_UNRESOLVED` preservation;
10. raw secret detection/sanitization in result/event payloads;
11. agent-declared merge/release/deploy authority ignored/rejected;
12. duplicate identical result ingestion accepted idempotently;
13. conflicting execution/result ID reuse rejected;
14. failed history retained after later success;
15. malformed/native output rejected before governance use;
16. deterministic normalized result schema independent of agent provider/name;
17. resume/reconcile from durable execution record;
18. no external reviewer/API dispatch as a side effect of coding-agent execution in TESTING.

## Testing pass criterion

A Slice11 `TESTING_BOUNDED_PASS` requires all frozen acceptance cases and relevant Slice1–10 regressions to pass on one exact candidate SHA, with all observed failures classified and preserved. A bounded pass means only that the generic coding-agent adapter boundary is ready to remain in the testing workstream; it does not mean release- or production-qualified.
