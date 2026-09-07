# Conversational Drift and Evidence Contamination Control

## Purpose

Prevent unverified or false claims introduced in one research or agent step from becoming treated as authoritative facts in later steps merely through repetition, consensus, summarization, or conversational inheritance.

Conversation is not authority. Repetition is not evidence. Consensus is not truth. Only provenance-backed, policy-valid evidence may enter authoritative platform state.

## Threat Model

A common failure chain is:

`R1 introduces plausible false claim -> R2 inherits it as context -> R3 derives a requirement -> later agents treat the requirement as established fact`

The conversation can become internally coherent while drifting away from external reality.

## Required State Separation

Maintain separate stores/state classes for:

1. Working hypotheses
2. Unverified claims
3. Source-verified claims
4. Independently verified claims
5. Accepted decisions
6. Governed requirements
7. Retracted/superseded claims

Raw conversation transcripts, summaries, model memory, and agent-to-agent messages are not authoritative stores.

## Claim Provenance Contract

Every material claim must carry a durable identifier and at minimum:

- claim_id
- exact claim text or normalized proposition
- status
- source identity
- source version/date when material
- primary/authoritative-source verification status
- producing agent/researcher
- independent reviewer/Judge result
- allowed uses
- prohibited uses
- parent claims
- derived claims/decisions/requirements
- retraction/supersession metadata

Recommended lifecycle:

`UNVERIFIED -> SOURCE_VERIFIED -> INDEPENDENTLY_VERIFIED -> PROMOTABLE -> ACCEPTED`

Non-authoritative states include:

`AMBIGUOUS`, `INSUFFICIENT_EVIDENCE`, `CONTRADICTED`, `DOMAIN_MISMATCH`, `FUNCTION_MISMATCH`, `RETRACTED`, `NEEDS_REASSESSMENT`.

## Context Compartmentalization

Agents must receive authoritative context reconstructed from governed state rather than inheriting the entire raw conversation as if every prior sentence were true.

A resumed or downstream agent should receive, at minimum:

- accepted requirements
- verified claims
- unresolved hypotheses
- active contradictions
- retractions
- decisions with provenance

Unverified claims may be supplied for investigation but must be visibly typed as unverified and prohibited from direct promotion.

## Non-Propagation Rule

An unverified claim may trigger research but may not be used as the sole basis for:

- a governed requirement
- a release decision
- a competitive conclusion
- a corrective action with consequential authority
- a model qualification decision
- an accepted architecture decision

Downstream agents must preserve the claim status rather than laundering uncertainty through paraphrase.

## Consensus Is Not Evidence

Agreement among R1, R2, R3, multiple models, or Researcher + Judge does not increase a claim's evidentiary status unless new independent evidence is added.

If three agents repeat the same unsupported claim, the claim remains unsupported.

## Derived-Claim Invalidation

When a parent claim is falsified, contradicted, or retracted, the governor must traverse its dependency graph and mark every dependent artifact for reassessment.

Required flow:

`parent claim retracted -> locate dependent claims -> locate decisions -> locate requirements -> mark NEEDS_REASSESSMENT -> block affected promotion/release paths until individually adjudicated`

Do not automatically delete downstream requirements: some may have independent support. Reassess each one.

## Grounding Checkpoints

Long-running research and multi-agent workflows must periodically rebuild working context from authoritative governed state.

A grounding checkpoint must not simply summarize prior conversation. It must reconstruct from verified claims, accepted decisions, requirements, unresolved hypotheses, and retractions.

Suggested triggers:

- after N research hops
- before requirement promotion
- before architecture promotion
- before corrective authority issuance
- before release/completion adjudication
- when a contradiction or retraction occurs
- when execution resumes after a context-window/chat/session boundary

## Drift Detection Signals

The platform should detect and flag at least:

- unsupported claim repeated across multiple agents
- status loss during paraphrase/summarization
- claim promoted without source verification
- downstream artifact depending on retracted evidence
- consensus without evidence diversification
- authoritative context containing RETRACTED or CONTRADICTED claims
- requirements whose only provenance traces to conversation/model assertion
- summary text that upgrades `possible/maybe/unverified` into factual language

## Governor Boundary

LLMs may identify drift, but the non-propagation, promotion eligibility, retraction propagation, and reassessment requirements must be enforced by deterministic platform mechanisms.

A Judge may recommend ACCEPT, REJECT, or REASSESS, but cannot override missing provenance or invalid parent-claim state.

## Relationship to External Evidence Validation

This standard complements `standards/external-evidence-semantic-validation.md`.

External semantic validation controls whether a source claim is valid enough to enter the system. Conversational drift control governs how claims propagate after entry and how contamination is contained if a claim later proves wrong.

## Historical Integrity

Corrections must preserve history. Do not silently rewrite R1/R2/R3 outputs to make them appear correct after the fact. Store the original claim, the later contradiction, the retraction, affected descendants, and the final adjudication.
