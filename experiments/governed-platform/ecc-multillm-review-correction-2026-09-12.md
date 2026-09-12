# ECC Multi-LLM Review Capability Correction — 2026-09-12

Status: **EVIDENCE_ONLY / CORRECTION / NOT_PROMOTED / NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## Why this correction exists

The earlier bounded ECC extraction understated ECC's review/orchestration capability. Primary-source re-check against the same frozen ECC commit `1ed03ecf2ec91aac77f3c98094d7d1136e89b4d4` confirms that ECC already contained an explicit dual independent multi-model review workflow and a separate external Codex critique path.

This correction does not change V17/V18 candidate authority and does not promote ECC behavior into governed-platform policy.

## Confirmed ECC capabilities at frozen revision

### 1. Santa Loop — dual independent multi-model review/convergence

`commands/santa-loop.md` specifies:

- two independent reviewers in parallel;
- Reviewer A = Claude Opus;
- Reviewer B = first available external Codex or Gemini CLI, with Claude Opus fallback if neither external CLI is installed;
- same rubric and same reviewed files;
- no shared review context;
- structured PASS/FAIL JSON;
- both reviewers must PASS for `NICE`;
- if either FAILs, findings are fixed and both fresh reviewers run again;
- maximum 3 rounds, then manual escalation;
- Codex review is read-only;
- after NICE, the command proceeds to `git push`.

This is a genuine multi-model adversarial review engine/workflow, not merely a multi-agent brainstorming pattern.

### 2. Santa Method — reusable dual-review verification architecture

`skills/santa-method/SKILL.md` defines generator -> dual independent reviewers -> verdict gate -> fix-until-convergence, explicitly requiring context isolation, identical rubric, same inputs and structured verdicts. It also states that both reviewers must pass and recommends fresh reviewers each round.

### 3. Council Multi-Model — external critique, not decision authority

`skills/council-multi-model/SKILL.md` adds one optional isolated external Codex critique after the normal decision council. It explicitly states that this adds no voting, automatic judge or new decision authority; the user decides. It also labels same-provider vs cross-provider critique and fails closed when the tested Codex isolation boundary is unavailable.

### 4. Model routing

`commands/model-route.md` routes work among Haiku/Sonnet/Opus tiers by complexity/risk/budget, and the broader ECC autonomous-loop documentation supports assigning different models to research/implementation/review stages.

## Corrected comparison against the governed platform

### ECC is closer to our review engine than the earlier extraction stated

Shared ideas include:

- multi-model reviewers;
- parallel independent review;
- context isolation;
- same-input/same-rubric comparison;
- structured reviewer verdicts;
- convergence/fix/re-review loop;
- external model fallback;
- explicit manual escalation after repeated failure;
- read-only external review path in at least one integration.

### Material differences remain

ECC Santa Loop is still an engineering review workflow, not the same governance architecture as our review engine. At the frozen revision it does not demonstrate the same set of platform-level guarantees for:

- exact immutable candidate/revision binding for review qualification;
- reviewer evidence-class accounting (AI engineering feedback vs qualifying manual review);
- reviewer authority kept external to model PASS/consensus;
- deterministic clean-room provenance beyond prompt/process isolation;
- durable preservation of every raw review as immutable evidence tied to candidate identity;
- independent reviewer qualification/identity/authority contracts;
- threshold-consumption ledger / atomic review-count semantics;
- anti-replay / anti-double-count review evidence consumption;
- explicit separation of review PASS from MERGE/RELEASE/DEPLOY/completion authority;
- semantic-evidence promotion gates such as EXP-J;
- correction/retraction propagation through downstream governed requirements;
- cross-session authoritative workflow reconstruction from governance state rather than review/session files;
- provider/model/runtime identity qualification equivalent to the governed platform's stricter evidence contract.

A particularly important distinction is that Santa Loop states `both PASS -> NICE -> push`, whereas the governed platform treats model reviewer agreement as evidence only and requires separately governed authority for consequential transitions.

## Revised classification

Add the following capability to the extraction:

`ECC-23 — Dual independent multi-model adversarial review/convergence engine`

Classification: **IMPROVES_EXISTING**

Rationale: ECC has a real and useful multi-model review engine that substantially overlaps our reviewer orchestration layer. It should be treated as a strong comparator and possible worker/review-adapter design input. However, its reviewer consensus/gate must not be imported as terminal or qualifying authority.

Add:

`ECC-24 — External isolated cross-provider critique adapter`

Classification: **IMPROVES_EXISTING**

Rationale: the Codex critique adapter demonstrates useful isolation, provider labeling, transfer consent, tool suppression, exact tested CLI-boundary checks and fail-closed absence handling. These are useful implementation patterns for reviewer adapters.

## New falsification questions prompted by this correction

1. Can ECC Santa Loop PASS both reviewers on the wrong candidate/revision?
2. Can a reviewer rubric be weakened at runtime and still produce NICE?
3. Can both model reviewers agree while mandatory non-model evidence is missing?
4. Can the Claude-only fallback be mistaken for real provider diversity?
5. Can reviewer PASS directly cause push/ship despite a separate mandatory authority gate being unsatisfied?
6. Are reviewer outputs durably bound and non-replayable across candidate changes?
7. Can a prior contaminated premise reach both isolated reviewers through their shared input/rubric?
8. Can a changed reviewer model/version silently alter qualification semantics?
9. Can review evidence be counted twice across repeated runs?
10. Does failure/retry history remain preserved after eventual NICE?

## Corrected disposition

ECC has **real multi-LLM orchestration and a genuine dual-review convergence engine**. The earlier extraction understated this capability.

This does **not** currently falsify the governed-platform differentiation. The strongest remaining distinction is not "we have multiple LLM reviewers and ECC does not." That differentiation is invalid.

The stronger differentiation is:

> **ECC orchestrates multiple reviewers for engineering quality; the governed platform attempts to make review evidence, reviewer independence, authority, exact candidate binding, threshold consumption, correction/retraction and consequential state transitions non-self-granting and fail-closed.**

Future competitive claims must use that narrower distinction.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
