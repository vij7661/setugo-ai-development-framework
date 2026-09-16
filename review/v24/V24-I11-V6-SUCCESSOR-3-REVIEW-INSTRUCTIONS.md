# V24-I11-V6-INTEGRATED-SUCCESSOR-3 — Independent Manual Re-Review Instructions

## Review subject

Review only the frozen candidate identified by the package binding:

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-3`
- commit: `b4b91dcf5855ae2bb7162c0b94d1a79a8a64e171`
- tree: `a81204c73016243556c6eefd711bc91c37adda49`

The predecessor successor-2 review concluded `CHANGES_REQUIRED`. Successor-3 claims narrow systemic repairs to three blocking findings: PRC-1, DA-1, and NCP-1. Do not assume those repairs are correct because CI is green. Re-falsify them from the frozen bytes.

This is a **manual independent engineering review**. Do not call external reviewer APIs. Your output is review evidence only and cannot grant runtime/scientific/deployment/release authority.

## Required posture

Assume false-green until disproven. Distinguish exact content integrity from semantic authority. Treat labels, hashes, PASS states, and CI success as evidence only unless the authority-bearing relationship they claim is independently established.

## Priority 1 — PRC-1 repair: external trusted-boundary anchor

Inspect `v24_v6_proof_reference_closure.py`, `v24_v6_test_proof_context.py`, all production call sites, and tests.

Try to defeat the repair by constructing a new proof context/genesis scope and matching `trusted_boundary` while the separately established external anchor remains unchanged. Verify that this fails closed. Check missing/invalid/mismatched external anchor behavior. Determine whether production code can synthesize or mutate the anchor, directly or indirectly. Distinguish the explicit trust assumption that the invocation environment owns the anchor from a candidate-controlled input. Check cross-context, cross-generation, stale-context, and same-genesis/different-context replay.

If the environment variable mechanism itself leaves a concrete candidate-controlled self-grant path, report it with a reproducible path; do not merely object that external trust exists, because an external residual root is intentional in the approved design.

## Priority 2 — DA-1 repair: exact decision → effect-path/target join

Inspect `v24_v6_decision_apply.py`, R3/R6 consumers, fixtures, and tests.

Attempt to use a qualified ALLOW decision for path A against a different current path B while preserving generation-wide sink/writer/guard/surface bindings. Try substitutions of `path_id`, `path_content_digest`, `effect_class_id`, decision context, endpoint projection, reevaluated decision, and current snapshot. Verify the decision qualification closes over recomputed canonical decision content containing the authorized path identity/content/effect class and that apply-time comparison uses the active (including reevaluated) decision.

Look for any route where individually valid decision and path objects can still be combined without an exact semantic join.

## Priority 3 — NCP-1 repair: clause → control binding

Inspect `v24_v6_normative_clause_projection.py`, descriptor construction, downstream consumers, and tests.

Attempt to change only `control_id` while retaining candidate clause/artifact/span identity and stale proof. Attempt clause substitution, control substitution, binding-ID substitution, binding-content substitution, duplicate/multi-map cases, and a newly self-created binding proof. Verify the canonical binding covers `(candidate_clause_id, control_id, artifact_sha256, normative_artifact_blob_sha, candidate_span_digest)` and that its own governed qualification is required.

Determine whether a descriptor can reach qualified catalog coverage without an independently proof-closed clause→control relationship.

## Cross-cutting review

After the three repairs, repeat the systemic pattern search: Object A qualified + Object B qualified must not imply A→B unless the relationship itself is bound. Check root→context, clause→control, predicate→evaluator, decision→projection, decision→effect path, path→effect class, registry-result→consumer, atomic proof→snapshot/transaction, trace→mechanism, case-universe→result, and successor→candidate identity.

Also inspect whether the repairs introduced new weaknesses: mutable global state, stale-anchor reuse, canonicalization ambiguity, proof fields excluded from semantic digests, test-only helpers leaking into production, fixture-specific behavior, or circular/self-issued qualifications.

## Scope boundary

Construction-reviewable here: proof closure, content/digest recomputation, completeness/set equality, decision/apply latch semantics, normative mapping semantics, effect/ledger validators, atomic proof gating, qualification-summary logic, exact freeze/package integrity.

Still not runtime-proven here: actual durable external writes, real concurrency fencing, real idempotency/partial-commit behavior, external verifier semantic correctness, durable evidence-store retention across processes, provider behavior, and scientific WDPC outcomes. Do not convert construction evidence into runtime claims.

## Historical evidence

Preserve classifications exactly:

- `35070903107` — genuine pre-fix mechanism RED reproducing PRC-1, DA-1, NCP-1.
- `35071250976` — tooling/preflight failure only: malformed patch; no production mutation.
- `35071608899` — tooling/preflight failure only: exact-source transformation ambiguity guard; no production mutation.
- `35071757663` — narrow systemic repair GREEN.
- `35071849800` — pre-refreeze all-up GREEN.
- `35072081665` — R9 migration GREEN.
- `35072181274` — exact final-head GREEN.

No later GREEN may rewrite an earlier RED/failure.

## Required final output

Return one artifact with:

1. `PASS`, `CHANGES_REQUIRED`, or `INSUFFICIENT_EVIDENCE`.
2. Exact candidate family/commit/tree and package/binding identity.
3. Critical, High, Medium, Low findings with concrete failure path, why controls fail, narrow repair, and blocking status.
4. Explicit adjudication of whether PRC-1, DA-1, and NCP-1 are actually closed.
5. Positive attacks that failed.
6. Evidence/runtime limitations.
7. Final progression statement.

Any Critical or High finding keeps scientific execution closed and requires another repair/refreeze/re-review cycle. A PASS is construction-review evidence only; it does not itself open scientific execution or grant runtime authority.
