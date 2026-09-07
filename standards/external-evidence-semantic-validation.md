# External Evidence Semantic Validation Standard

## Purpose

Prevent lexical or branding similarity from being promoted into a governed conclusion without evidence that the external item actually performs the claimed function.

This standard was added after the Archify incident, where a product in physical architecture/interior/exterior design was incorrectly treated as a software-architecture tool because the term "architecture" was interpreted semantically without verifying the product domain and workflow.

## Governing rule

**Do not rely only on keyword or name matches. Inspect and verify the actual functional capability and concept before an external item may influence platform requirements, competitive conclusions, architecture decisions, or evidence-backed completion.**

## Required evidence contract

Before an external finding can enter `PROMOTED`, the evidence record must contain independently checkable support for all applicable fields:

1. `identity` — exact product/project/paper/tool and version/date when relevant.
2. `primary_source` — authoritative source inspected where reasonably available.
3. `domain` — actual problem/domain being addressed.
4. `intended_users` — who the item is designed for.
5. `inputs` — what it consumes.
6. `outputs` — what it produces or changes.
7. `functional_workflow` — what the system actually does, not what its name suggests.
8. `claimed_overlap` — the precise capability alleged to overlap with the governed platform.
9. `claim_support` — source evidence that directly supports that overlap.
10. `independent_judgment` — a Judge disposition that is separate from the researcher/Builder conclusion where the claim is material.

If a required field is absent, contradicted, unsupported, or sourced only from a snippet that the primary source disproves, promotion must be blocked.

## Enforcement model

Model instructions are guidance, not the enforcement boundary. The governor must make `PROMOTED` unreachable unless the evidence contract is satisfied.

A model saying `RELEVANT`, a researcher and Judge agreeing, or several models reaching the same conclusion is not sufficient if required evidence is missing or contradictory.

Suggested state flow:

`DISCOVERED -> SOURCE_VERIFIED -> SEMANTICALLY_CLASSIFIED -> OVERLAP_SUPPORTED -> INDEPENDENTLY_JUDGED -> PROMOTED`

Failure/hold states include:

- `DOMAIN_MISMATCH`
- `FUNCTION_MISMATCH`
- `PRIMARY_SOURCE_CONTRADICTION`
- `INSUFFICIENT_EVIDENCE`
- `AMBIGUOUS`
- `UNSUPPORTED_CLAIM`
- `RETRACTED`

## Semantic-collision risk

Treat overloaded terms as high-risk signals, including but not limited to: `architecture`, `agent`, `judge`, `workflow`, `verification`, `model`, `design`, `factory`, `governance`, and `orchestration`.

Lexical similarity may trigger investigation. It must never by itself satisfy relevance.

## Claim-to-source traceability

Every promoted external claim must retain a link from the claim to the authoritative evidence that substantiates it. If later evidence falsifies the interpretation, the system must preserve the original finding and correction history, retract the unsupported evidence, and reassess derived requirements for independent support rather than silently rewriting history.

## Authority boundary

A Judge is fallible. Judge approval cannot override missing mandatory evidence. Deterministic evidence requirements bound the Judge's authority.

This creates the intended separation:

**LLM judgment proposes a disposition; the governor decides whether that disposition is legally promotable under the evidence contract.**
