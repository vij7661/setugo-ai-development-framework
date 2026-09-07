# Setugo AI Development Framework

A public, reusable framework for disciplined software discovery, architecture, implementation, validation, and AI-assisted execution, developed through the Setugo build journey.

## What this repository contains

- `prompt-framework/` — Setugo AI Development Prompt Framework v1.6 in public/shareable form.
- `skills/failure-triage/` — native failure-triage skill source from the Claude experiment.
- `claude-code/` — native Claude Code safeguards and configuration examples.
- `standards/` — executable-governance-oriented standards, including external evidence semantic validation and conversational-drift/contamination control.
- `experiments/governed-platform/` — falsification designs for the governed AI-development platform, including EXP-J semantic evidence gating and EXP-K conversational drift/evidence contamination.

## Core idea

Do not treat the current implementation, current test, current fixture, current documentation, external claim, conversational repetition, model consensus, or Judge verdict as automatically correct. Establish the intended contract first, then judge each artifact against that contract and require the evidence needed for promotion.

The broader operating model is:

**Conversation → Prompt → Agent → Skill → Test/CI Rule → Executable Guard → Human Gate**

The framework is designed to help teams move through:

**Research → Architecture → Technical Requirements → Development → Independent Testing → Codex Execution**

## How to use it

Start with the prompt framework. Individual prompts may reference Core Standards A–E. When a prompt is used independently, include every Core Standard it references. Do not execute a prompt with an unresolved Core Standard reference and do not reconstruct missing standards from memory.

The Claude artifacts are included as native files rather than converted PDFs so developers can inspect, adapt, and use them directly. They are intended as examples of turning reasoning rules into executable safeguards, not as universal drop-in policy for every repository.

For external research/evidence, lexical similarity is discovery evidence only. Before a material external finding is promoted, verify the actual domain, intended users, inputs, outputs, workflow/capabilities, claimed overlap, and authoritative support. A researcher or Judge verdict cannot substitute for missing mandatory evidence.

For long-running or multi-agent work, conversation is not an authoritative database. Material claims should carry durable provenance and status, and downstream contexts should be reconstructed from governed state: verified claims, accepted decisions, unresolved hypotheses, retractions, and requirements. Repetition or model consensus does not upgrade evidentiary status. When a parent claim is retracted, dependent claims, decisions, and requirements must be traced and reassessed rather than silently preserved or rewritten.

## Relationship to Setugo

This repository contains the reusable AI-development framework and supporting developer artifacts created while building Setugo. It does **not** contain the Setugo product source code, credentials, private configuration, production data, or internal business secrets.

## Contributions and feedback

Use the framework, challenge it, and report where it fails. Useful feedback includes ambiguous rules, failure modes, unnecessary complexity, places where a human decision is still required, and rules that should become automated checks.

## License

No open-source license has been selected yet. Until a license is added, normal copyright rules apply. A license will be added only after an explicit project decision.
