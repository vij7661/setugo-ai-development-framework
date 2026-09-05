# Platform-Enforced Scoped Correction Status

Validated implementation SHA: `0282715081618bfc6aa927859af19f2d8af1e201`

Exact-head GitHub Actions run: `33990193476` — **SUCCESS**.

## Enforced contract

Scoped correction is no longer a model instruction alone.

Before R1 receives a correction invocation, the platform now requires every retained material correction target to be machine-localizable to one exact claim scope in the frozen artifact:

- exactly one `claim:*` affected scope;
- a non-empty `first_invalid_claim` exact text anchor;
- the anchor must occur exactly once in the frozen artifact;
- distinct anchors may not overlap;
- artifact-wide, empty, ambiguous, absent, or otherwise unbound scopes fail closed;
- a claim anchor that would authorize replacement of the entire artifact fails to human rather than granting a full-artifact rewrite capability.

The platform derives `EXACT_CLAIM_ANCHOR_REPLACEMENT_V1` and sends that capability metadata to R1. After R1 returns, the platform independently checks that every byte of text outside the authorized anchor ranges remains present verbatim and in order. An out-of-scope rewrite is rejected before R3 is invoked.

## Evidence events

The session chain now distinguishes:

- `SCOPED_CORRECTION_REJECTED` — no correction invocation occurred because scope could not be safely bound;
- `SCOPED_CORRECTION_AUTHORIZED` — a platform-derived exact claim replacement capability was issued;
- `SCOPED_CORRECTION_ASSESSED` — the returned revision was independently checked against that capability;
- `R1_REVISED` — emitted only after the revision passes the platform scope guard.

## Falsification coverage

Direct and orchestrator/system regressions cover:

- valid exact localized replacement;
- stable prefix mutation;
- stable suffix mutation;
- mutation of text between two authorized claims;
- repeated/ambiguous anchors;
- missing anchors;
- absent anchors;
- overlapping anchors;
- artifact-wide scopes;
- empty scopes;
- whole-artifact claim anchors;
- no-op correction;
- unbound finding never invoking correction;
- out-of-scope R1 rewrite never reaching R3;
- persistent memory + evidence-chain + blinded R3 integration with the new scope events.

## Non-claims

This v1 capability is intentionally conservative and text-based. It does not infer semantic sections, AST nodes, database rows, code symbols, or arbitrary structured-document scopes. Those require separately typed platform-owned scope adapters. A reviewer/model cannot self-declare a broader scope to obtain rewrite authority.
