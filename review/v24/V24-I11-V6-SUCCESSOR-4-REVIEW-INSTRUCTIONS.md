# V24-I11-V6-INTEGRATED-SUCCESSOR-4 — Independent Manual Re-Review Instructions

## Review subject

Review only the frozen candidate:

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-4`
- commit: `ef30eba1dfbe5ccf0ec6edb9e8d1295da5c70ddb`
- tree: `bfbf49021514240668b24612d53ea790bcdf0baa`
- exact final-head run: `35324254339`
- integration binding digest: `f55d1354bb3c012d59711b4cd2dac6a7fb334387adc38ed506ee2f595043e348`

The Successor-3 independent review concluded `CHANGES_REQUIRED`. Its blocking systemic finding was PRC-1: the alleged external root was a digest stored in caller-writable process environment, so a caller could build a forged proof context/boundary, compute the matching digest, rewrite `V24_V6_TRUSTED_BOUNDARY_ANCHOR_SHA256`, and self-grant proof closure. DA-1 and NCP-1 were locally repaired but remained transitively exposed through PRC-1.

Successor-4 claims a narrow construction-level repair: exact proof contexts must carry a detached asymmetric root attestation verifiable under one pinned public key whose private signing half is absent from candidate/test Python.

This is a **manual independent engineering review**. Do not call external reviewer APIs. Review output is evidence only and grants no runtime, deployment, release, or scientific authority.

## Required posture

Assume false-green until disproven. Do not infer authority from CI green, labels, hashes, signatures, or a documented ceremony alone. Verify the exact relationship each mechanism is supposed to establish, and actively attempt self-grant, substitution, replay, canonicalization, and cross-object composition attacks.

## Priority 1 — PRC-1 asymmetric root repair

Inspect at minimum:

- `governance-runtime/v24_v6_root_attestation.py`
- `governance-runtime/v24_v6_proof_reference_closure.py`
- `governance-runtime/v24_v6_test_proof_context.py`
- `governance-runtime/fixtures/v24-v6-construction-root-attestation-v3.json`
- `governance-runtime/fixtures/v24-v6-construction-context-signatures-v3.json`
- `governance-runtime/test_v24_v6_successor4_external_anchor_red.py`
- `governance-runtime/test_v24_v6_successor4_root_attestation.py`
- the exact external trust artifacts supplied in the review package.

The pinned external trust identity is:

- trust branch: `trust/v24-v6-construction-root-attestation-v3`
- commit: `2515582a5e2f0e1041bf5cc83523ffa732620724`
- tree: `1c2a1d0f60d3e2a62a2355831dc46f76ff72df7e`
- public-root blob: `7722a5725324fb805283bce9764b2d151a774ec2`
- signature-bundle blob: `b16e2a2bfac013e6e600cf9944595a88eefd2ca8`
- signing-ceremony blob: `cc2d8bec17b6775392094920f9549ca2e5174d44`
- public-key DER SHA-256: `fbb2cea7474505f0c0d8f77be81c97a949d4ea70eb38b7caef4ffd0e9606f61c`

Reproduce or independently reason through these attacks:

1. same-process rewrite of the old environment anchor;
2. structurally valid but unsigned context;
3. valid signature from context A reused on context B;
4. caller-supplied modulus/exponent or caller-selected verification key;
5. signed context combined with another generation or genesis trusted scope;
6. malformed or ambiguity-exploiting RSA/PKCS#1 v1.5 encoding;
7. signature/canonical-material mismatch caused by omitted or differently normalized fields;
8. a production route that bypasses `validate_root_attestation`;
9. candidate/test code obtaining or synthesizing signing authority;
10. stale or cross-context replay that still reaches `PROOF_REFERENCE_CLOSED`.

The existence of an external residual root is intentional. Report a blocker only when there is a concrete path for the frozen candidate/caller to mint, replace, bypass, or mis-bind that root, or when the evidence is insufficient to establish the claimed construction property.

## Priority 2 — trust/evidence separation

Confirm that the private signing key is not committed, not embedded in candidate/test Python, and not reconstructed from committed material. Confirm the local public-root and signature-bundle fixtures are byte-identical to the pinned external trust blobs.

Determine whether the final-head verification genuinely checks the external trust commit/tree/blob identities rather than merely checking candidate-local copies.

Treat the signing-ceremony record as evidence, not proof of production HSM/KMS custody. Successor-4 claims construction-only trust; it does not claim a production key-lifecycle or runtime isolation solution.

## Priority 3 — DA-1 and NCP-1 under repaired PRC-1

Re-test the previous compound attacks now that the root path is asymmetric.

For DA-1, try to qualify a decision for one effect path and apply it to another path/target/effect class, including creation of a fresh attacker-selected qualification. Verify the exact decision → effect-path relationship remains bound once PRC-1 self-grant is unavailable.

For NCP-1, try `control_id` reassignment, clause/control substitution, stale binding reuse, and creation of a fresh attacker-selected binding qualification. Verify the exact clause → control relationship remains proof-closed once PRC-1 self-grant is unavailable.

Do not mark DA-1 or NCP-1 closed solely because their isolated stale-proof tests pass.

## Cross-cutting systemic review

Repeat the relationship-binding search across root→context, clause→control, predicate→evaluator, decision→projection, decision→effect path, path→effect class, registry-result→consumer, atomic proof→snapshot/transaction, trace→mechanism, case-universe→result, and successor→candidate identity.

Look specifically for:

- individually valid objects combined without a proof of their relationship;
- mutable or caller-selected trust inputs;
- production imports of test fixture authority;
- self-issued qualifications;
- excluded semantic fields in canonical digests;
- canonicalization ambiguity;
- stale/cross-generation replay;
- public-key substitution;
- signature verification laxness;
- fixture-specific positive paths that production does not structurally enforce;
- manifest/freeze omissions for new load-bearing dependencies.

## Evidence to preserve

Do not reclassify earlier results:

- Successor-3 final manual review: `CHANGES_REQUIRED`.
- Successor-3 final adjudication commit: `3b16e06e8e2d6dc7d5d1f0864b8dea508edada8f`.
- Successor-4 preserved self-grant RED: run `35318618058`.
- Successor-4 strengthened construction all-up GREEN: run `35323905839`, 209/209 V24-V6 tests.
- Successor-4 exact final-head GREEN: run `35324254339`.
- Verification artifact: `10539040564`, artifact digest `sha256:50f9e004b13de66cdd19f6ae8aa6310dc45e2a7769dd0aaa259d355f2d42a2f7`.
- Verification JSON SHA-256: `e1492d7fd035085591ea5d29d21231180f9aac4f417d0d8da898c4e8e81afe54`, 7966 bytes.

A later GREEN does not erase the preserved RED or the Successor-3 review finding.

## Scope boundary

Construction-reviewable here: exact proof/reference closure, asymmetric attestation verification, canonical binding, completeness/set equality, decision/apply semantics, normative mapping semantics, effect/ledger validators, atomic proof gating, qualification-summary logic, external-trust byte binding, and exact freeze/package integrity.

Still not proven here: production key custody/HSM/KMS behavior, real process isolation, durable external writes, concurrency fencing/idempotency, provider behavior, external verifier semantic correctness, durable evidence retention across process failure, deployment controls, or scientific WDPC outcomes.

Scientific execution remains `CLOSED_PENDING_SUCCESSOR_REVIEW`. Runtime qualification remains `NOT_CLAIMED`.

## Required final output

Return one review artifact containing:

1. `PASS`, `CHANGES_REQUIRED`, or `INSUFFICIENT_EVIDENCE`.
2. Exact candidate family/commit/tree and package/binding identity.
3. Critical, High, Medium, and Low findings with reproducible failure path, why existing controls fail, narrow repair, and blocking status.
4. Explicit adjudication of PRC-1, DA-1, and NCP-1.
5. Any new systemic/transitive finding.
6. Positive attacks that failed.
7. Evidence/runtime limitations.
8. Final progression statement.

Any Critical or High finding keeps scientific execution closed and requires another repair/refreeze/re-review cycle. A PASS is construction-review evidence only and does not itself open scientific execution or grant runtime authority.
