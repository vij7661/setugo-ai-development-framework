# Setugo Governed AI Development Platform

A governed AI-assisted software-development platform for using LLMs in research, architecture, implementation, review, testing, and execution **without allowing model output, model consensus, conversation history, or a green CI result to become authority by itself**.

This repository began as a reusable AI-development framework during the Setugo build, but it has evolved beyond a prompt library. The core project is now the **governed platform/runtime**: deterministic controls that decide what evidence is valid, what may be promoted, when independent review is required, what an AI may execute, and which decisions must remain external to the model.

> **Core principle:** models may propose, analyze, review, and generate evidence. They do not grant themselves authority.

---

## What problem this project is solving

LLM-assisted development can fail in ways that are easy to miss:

- a plausible external claim is repeated until it is treated as fact;
- multiple models agree on an unsupported conclusion;
- a reviewer returns `PASS` without proving required evidence;
- a green test or CI workflow is mistaken for release/completion authority;
- a new chat resumes from stale conversational memory instead of the real project state;
- a model or agent widens its own permissions;
- evidence for one candidate is accidentally reused for another;
- a review packet, workflow, or artifact is internally consistent but not bound to the actual GitHub run, revision, or source object;
- a platform control exists in code but is not wired into the real execution path.

The platform is designed to make these failure modes **observable, falsifiable, and fail-closed**.

---

## What this repository actually contains

This is not only a collection of prompts.

### 1. Governed runtime

`governance-runtime/` contains the operational governance layer, including:

- live conversation governance;
- deterministic execution handoff and resume rules;
- review request and review-evidence handling;
- provider/model review orchestration;
- evidence materialization and request-integrity checks;
- candidate/revision binding;
- review provenance and reviewer-identity controls;
- provider review telemetry;
- fail-closed promotion logic;
- evidence and lifecycle handling.

Key starting points:

- [Live Conversation Governance](governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md)
- [Execution Handoff Protocol](governance-runtime/EXECUTION-HANDOFF-PROTOCOL.md)
- [Provider Review Telemetry Contract](governance-runtime/PROVIDER-REVIEW-TELEMETRY-CONTRACT.md)

### 2. Governed platform / execution architecture

`experiments/governed-platform/` contains the platform architecture, execution slices, adversarial tests, falsification work, and integrated governed MVP components.

The governed execution model separates:

**intent → evidence → review → deterministic validation → capability/authority gate → isolated execution → evidence/state → external terminal authority**

The model may produce a proposal or result, but consequential authority is held by platform controls outside the model.

Start with:

- [Integrated Governed MVP Contract](experiments/governed-platform/INTEGRATED_GOVERNED_MVP_CONTRACT.md)

### 3. Evidence and semantic governance

`standards/` contains durable rules for preventing unsupported information from entering authoritative project state.

Examples:

- [External Evidence Semantic Validation](standards/external-evidence-semantic-validation.md)
- [Conversational Drift and Evidence Contamination Control](standards/conversational-drift-contamination-control.md)

These standards enforce rules such as:

- keyword similarity is discovery evidence, not proof;
- a Judge/reviewer verdict cannot replace missing evidence;
- model agreement does not increase evidentiary status;
- retracted claims must trigger reassessment of dependent requirements;
- conversation and memory are not authoritative state.

### 4. Falsification experiments

The platform is developed by trying to break its own governance assumptions.

Examples include:

- **EXP-J — Semantic Evidence Gate Falsification**
- **EXP-K — Conversational Drift / Contamination Control**
- integrated governed MVP slice falsification;
- provider/reviewer-path falsification;
- candidate and evidence identity attacks;
- stale/replayed evidence tests;
- terminal-authority and side-effect boundary tests.

The objective is not merely to make tests pass. It is to expose false-green paths before a claim is promoted.

### 5. Prompt and agent-support artifacts

The repository still contains the reusable prompt and agent material that helped originate the platform:

- `prompt-framework/`
- `skills/`
- `claude-code/`

These are useful interaction and implementation layers, but they are **not the governance authority boundary**.

---

## Platform design principles

### Model output is evidence, not authority

An LLM can propose a decision, code change, review result, or action. The platform decides whether that output is admissible and whether any consequential action may occur.

### Independent review is necessary but not sufficient

A reviewer can identify defects and return a disposition, but review content does not establish its own provenance and cannot override missing deterministic evidence.

### Conversation is not the project database

Chat history, summaries, model memory, and repeated statements are advisory context. Material project state must be reconstructed from governed Git/evidence/checkpoints.

### Green CI is not terminal authority

A successful workflow proves only the bounded property that workflow tested. It does not automatically authorize merge, release, deployment, production, or completion.

### Evidence is candidate-bound

Evidence must remain tied to the exact candidate, revision, request, source object, and execution context it actually tested. Stale or cross-candidate evidence must fail closed.

### Authority is separated from execution

Capabilities and execution gates may authorize a narrowly scoped action, but terminal decisions such as merge, release, deployment, or production require separate governed authority.

### History is preserved

Failures, rejected findings, superseded candidates, retractions, and review history are retained rather than rewritten to make the project appear cleaner than it was.

---

## High-level architecture

```text
User / Project Intent
        |
        v
Research / Architecture / Code Proposal
        |
        v
Claim + Evidence Governance
        |
        v
Review Request / Independent Reviewer
        |
        v
Deterministic Review + Evidence Validation
        |
        v
Capability / Qualification / Policy Gates
        |
        v
Isolated Execution Gateway
        |
        v
Evidence + Authoritative State / Audit Trail
        |
        v
External Human / Terminal Authority Gate
```

Cross-cutting controls include:

- candidate and revision binding;
- source/object identity;
- reviewer provenance;
- semantic evidence validation;
- conversation-drift containment;
- deterministic handoff;
- immutable/frozen evidence;
- retry/idempotency and replay controls;
- telemetry that never grants authority.

---

## Current project status

This repository is under active engineering and falsification.

A number of governance mechanisms, runtime components, workflows, and integrated slices are implemented and tested. However, the project deliberately distinguishes **implemented/tested mechanisms** from **production or terminal authority claims**.

Do **not** interpret this repository as claiming:

- autonomous production deployment;
- unrestricted shell/repository authority for an LLM;
- production-ready distributed correctness;
- release authority from model or reviewer consensus;
- that every experimental result generalizes beyond its exact tested scope.

Where a gate has not been proven or explicitly authorized, the intended behavior is to fail closed.

Exact candidate status, review state, and promotion eligibility are determined by governed evidence and bound revisions—not by this README.

---

## How to read this repository

If you are new to the project, use this order:

1. Read this README for the product-level model.
2. Read [Live Conversation Governance](governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md).
3. Read the [Execution Handoff Protocol](governance-runtime/EXECUTION-HANDOFF-PROTOCOL.md).
4. Read the [Integrated Governed MVP Contract](experiments/governed-platform/INTEGRATED_GOVERNED_MVP_CONTRACT.md).
5. Read the standards under `standards/`.
6. Inspect the falsification experiments and tests under `experiments/governed-platform/`.
7. Treat prompt-framework and agent files as supporting layers, not the definition of the platform.

---

## Relationship to Setugo

The repository was created from the engineering work around Setugo, but this repository is the **reusable governed AI-development platform**, not the Setugo product application.

It does **not** contain:

- Setugo production application source code;
- production credentials or secrets;
- private business configuration;
- production customer data.

The goal is to make the governance architecture reusable across software projects, not to make it specific to one marketplace or one application.

---

## What this project is not

This is not:

- a prompt collection with governance terminology added around it;
- a wrapper that trusts an LLM's own `PASS` or confidence score;
- a multi-agent voting system where consensus becomes truth;
- an autonomous deployment bot;
- a claim that models can safely self-authorize;
- a marketing benchmark that hides failed experiments.

The project is intentionally designed around the opposite assumption: **models, reviewers, workflows, and even our own governance code can be wrong and must be falsifiable.**

---

## Contributions and feedback

Useful contributions are those that expose false-green paths or make a governed rule more deterministic.

Examples:

- a bypass that allows evidence from the wrong candidate;
- a reviewer or provider identity ambiguity;
- a workflow that appears green without executing the intended control;
- a stale-state or chat-resume failure;
- a rule that exists only in prose but is not wired into the real path;
- unnecessary complexity that can be replaced by a narrower deterministic invariant.

When reporting an issue, include the exact revision, failure path, and the narrowest reproducible case where possible.

---

## License

No open-source license has been selected yet. Until a license is added, normal copyright rules apply. A license will be added only after an explicit project decision.
