# V24 I11 V6 R9 Successor-2 — Independent Manual Review Instructions

## Review subject

Review **only** the frozen candidate identified below and the evidence packaged with it:

- Candidate family: `V24-I11-V6-INTEGRATED-SUCCESSOR-2`
- Candidate commit: `68edfc00fdaa4dc08e36aca172158d59a361e0d0`
- Candidate tree: `acc760e20e5133f878237e40083376414de2ed9b`
- Dedicated verification run: `35010792550`
- All-up proof-resolution run: `35010792664`
- Integration binding digest: `e08d8996b076b77714ba5a56552e6136ed81f52e9b1316544c2333887ae682b0`

The former candidate `88cba7e1224ecbd5a8264ba4c31c4c264fc24fef` and its old review package are superseded and are **not** the review subject.

## Review posture

Perform an independent **manual architecture / governance falsification review**. Do not treat CI success, construction tests, SHA shape, labels such as `QUALIFIED/CURRENT`, model agreement, or this package itself as authority.

Assume false-green until the exact mechanism and evidence chain proves otherwise. The reviewer should look for a concrete path by which a candidate, caller, fixture, reviewer, test, diagnostic, stale proof, unbound dependency, bootstrap actor, or mutable artifact can manufacture or preserve authority that the V6 design intended to require independently.

No external reviewer API execution is part of this review gate. This packet is intended for manual independent review.

## Required review coverage

At minimum, inspect:

1. **Proof-reference closure** — every authority-bearing qualification/currentness/independence reference must resolve to the exact subject/object/content and cannot terminate through labels, opaque digests, fabricated result objects, or circular/self-created proof.
2. **Root/bootstrap trust** — genesis/bootstrap termination must remain narrowly scoped and cannot let the governed candidate create the authority that validates itself.
3. **Endpoint and predicate projection** — completeness, applicability, evaluator, condition, evidence and endpoint precedence must be deterministic, omission-sensitive and exact-bound.
4. **Material authority surface** — discovery, observation, writer/effect-path closure, currentness, independent witnesses, rollback/fork and materiality must remain fail-closed.
5. **Decision/apply** — no stale decision, mixed snapshot, caller boolean, alternate writer, or unbound guard may produce an effect.
6. **Normative projection** — structural enumeration, semantic disposition, artifact bytes and descriptor coverage must not permit candidate-selected omission or semantic false-green.
7. **Effect-class and durable-ledger closure** — registered-to-registered substitution, stale currentness, fabricated registry results, unanchored/local state, witness dependence or incomplete source surfaces must fail closed.
8. **Atomic binding** — contract/mechanism admission, registry completeness, verifier authority, proof schema, proof material and currentness must be exact and non-substitutable.
9. **Qualification integrity** — anti-false-green gate, production source, runtime trace, case universe, result record, qualification basis and summary compiler must not accept caller-declared authority.
10. **Freeze/dependency closure** — verify that the 19-file bound surface is sufficient and that no other mutable local/runtime/deployment dependency can change the semantics of R1-R8 without invalidating the freeze.
11. **Historical failure preservation** — earlier RED/failure evidence must remain append-only and must not be silently rewritten by later success.
12. **Authority boundary** — construction evidence must remain `NONE_EVIDENCE_ONLY`; runtime qualification is `NOT_CLAIMED`; scientific WDPC execution remains `CLOSED_PENDING_SUCCESSOR_REVIEW`.

## Known preserved falsifications that must remain closed

The review should specifically attempt to re-open, generalize, or find siblings of the preserved false-greens, including:

- opaque proof labels opening an authority path;
- fabricated witness/parser/gate authority labels;
- stale subject/content proof reuse;
- registered effect-class substitution reusing stale path currentness;
- opaque atomic-binding contract/mechanism authority;
- fabricated registry result / self-consistent proof substitution;
- opaque anti-false-green gate/source/trace authority;
- invalid result records contributing PASS;
- shared load-bearing production dependency mutation escaping the R9 freeze.

The R9 shared-dependency omission RED is preserved in run `35007589595`. The stale freeze-manifest failure is preserved in run `35008375917`; it demonstrated that exact binding mismatches fail closed.

## Required reviewer output

Return a structured review with:

- **Overall disposition:** `PASS`, `CHANGES_REQUIRED`, or `INSUFFICIENT_EVIDENCE`.
- Findings ordered by severity: `Critical`, `High`, `Medium`, `Low`.
- For each material finding: finding ID, affected file/function/contract, concrete false-green or trust-boundary failure path, why current controls are insufficient, and the narrowest systemic repair.
- Explicit statement on whether any Critical or High finding remains.
- Explicit statement on whether the exact frozen candidate may proceed to the next gate.

A `PASS` means only that this manual architecture review found no blocking defect in the frozen construction candidate. It does **not** itself grant runtime qualification, deployment authority, terminal authority, or scientific PASS.

## Stop condition

If any Critical or High finding is identified, scientific execution remains closed. Repair must occur on the remediation line, the exact candidate must be re-frozen/revalidated, and a new review package must be produced.

If the manual review returns `PASS` with no Critical/High findings, its adjudication must still be bound to this exact candidate commit/tree before any separate decision is made about opening scientific WDPC execution.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
