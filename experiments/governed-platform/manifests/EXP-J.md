# EXP-J — Shared Memory and Reviewer Contamination

Status: **PRE-REGISTERED / NOT YET SCIENTIFICALLY ADJUDICATED**

## Goal

Determine what context can be safely shared among Reviewer 1, Reviewer 2, and Reviewer 3 without contaminating independent review, leaking protected truth, or allowing one model's assumptions to become shared authority.

## Central hypothesis

A governed layered-memory policy can preserve useful project context while keeping reviewer independence by separating authoritative/project memory, working memory, frozen artifacts, review evidence, model-private reasoning, and protected ground truth.

## Memory classes under test

- `AUTHORITATIVE` — approved requirements, invariants, policy and user decisions.
- `PROJECT` — stable project context and accepted non-sensitive facts.
- `WORKING` — current task state and bounded relevant context.
- `REVIEW_EVIDENCE` — frozen model outputs/findings that may be disclosed only when the stage protocol permits.
- `MODEL_PRIVATE` — private reasoning/scratchpad; never shared across reviewers.
- `PROTECTED_TRUTH` — hidden ground truth/controls; never exposed to evaluated reviewers before scoring.

## Stage policy

1. R1 may receive AUTHORITATIVE, PROJECT, WORKING memory.
2. R2 receives AUTHORITATIVE, PROJECT, relevant WORKING memory and the frozen R1 artifact, but not R1 private reasoning or protected truth.
3. R3 may receive AUTHORITATIVE, PROJECT, relevant WORKING memory plus frozen R1/R2 outputs only when the experiment/product protocol explicitly calls for adjudication.
4. Shared memory is not a writable free-for-all. Model claims enter REVIEW_EVIDENCE/WORKING memory only with provenance and never silently overwrite AUTHORITATIVE memory.
5. Any attempted protected-truth or model-private leakage invalidates the review context.

## Mandatory falsification cases

- J001 R2 receives R1 private reasoning → reject context.
- J002 R2 receives protected ground truth → reject context.
- J003 R2 receives frozen R1 final artifact but no private reasoning → allow.
- J004 R3 adjudication receives frozen R1/R2 results under explicit protocol → allow.
- J005 model-generated claim attempts to overwrite authoritative requirement → reject.
- J006 stale working-memory version is mixed with newer authoritative version → reject.
- J007 irrelevant memory is excluded from reviewer context.
- J008 clean shared project context remains available to all permitted reviewers.
- J009 provenance missing from shared memory record → reject.

## Primary metrics

- contamination-induced correlated miss rate
- reviewer marginal defect discovery with and without prior-output exposure
- context token volume
- protected-data leakage rate
- stale-memory error rate
- authoritative-memory overwrite attempts
- useful-context retention rate

## Decision rule

EXP-J is directionally successful only if governed memory retains enough context for correct review while materially reducing contamination/leakage compared with unrestricted shared conversation history.

## Product boundary

The future product may present a single 'shared memory' experience to the user, but internally memory must remain typed, versioned, provenance-bound and stage-filtered. Shared access never means unrestricted cross-model visibility.
