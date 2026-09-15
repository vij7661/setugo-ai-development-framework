# V24 I11 V6 R2 — Endpoint Projection Construction Evidence

Status: **CONSTRUCTION COMPLETE / QUALIFICATION NOT GRANTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Lineage

Branch: `implementation/v24-i11-v6-r2-endpoint-projection`

Parent lineage includes validated R1 construction evidence and ultimately frozen I10 `9836dc3ff233cca582f485434fc1c6494cf7eb05`.

Validated R2 head: `a0fd7a49496877bebc562d757d41fe81791b39fa`

Validated tree: `ff1fa925107ceb31902f62d1b753171f7c26ccfb`

## Implemented mechanisms

- exact I5 compiled endpoint-table digest binding;
- qualified/current endpoint-table gate;
- complete applicability rule coverage over endpoint predicates;
- explicit omission-sensitive `ApplicablePredicateUniverse` completeness gate;
- one evaluator contract per applicable predicate;
- registered TRUE-condition schemas and FALSE negative-evidence classes;
- complete one-record-per-applicable-predicate evaluation coverage;
- producer-selected `NOT_APPLICABLE` rejection;
- TRUE without registered typed condition rejection;
- FALSE without governed negative evidence rejection;
- qualified canonical endpoint projector;
- deterministic earliest-phase / exact within-phase endpoint selection;
- stale endpoint-table digest rejection;
- unknown TRUE predicate rejection;
- no diagnostic-string-to-endpoint authority mapping.

## CI history

### Preserved failure

Run `34753547457`: **FAILURE**.

R2's 15 new construction tests all passed. Failure occurred while loading inherited `test_v24_endpoint_proof_compiler.py`, which contained a pre-existing unmatched `}` syntax error. This is classified as an inherited test-artifact defect, not R2 mechanism failure.

The test artifact was repaired narrowly by removing the unmatched brace. No production endpoint semantics were changed or weakened.

### Validated run

Run `34753597247`: **SUCCESS**.

Environment: Python `3.12.7`.

Passed:
- R2 construction tests: 15/15;
- R1 governance-foundation construction tests;
- inherited I5 endpoint/proof compiler tests;
- anti-case-specific production coupling gate;
- construction-only authority assertion.

## Scientific status

No WDPC case was rerun.

Historical 44-case scientific evidence and 36 REDs remain unchanged. WDPC-469/495 stay I1-blocked; WDPC-503 remains static/manual unresolved.

`R2_CONSTRUCTION = PASS`

`R2_RUNTIME_QUALIFICATION = NOT_CLAIMED`

Next implementation workstream: **R3 — independently derived material authority surface, append-only material observation state, materiality/effect-path closure**.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Post-review proof-resolution remediation — 2026-09-15

This section is append-only follow-up evidence. It does not alter the earlier construction history above.

Independent V6 review exposed a systemic false-green boundary that was not closed by the original R2 construction: SHA-shaped qualification references and caller-supplied `QUALIFIED` state labels could reach R2 authority-bearing stages without resolving the referenced R1 qualification/currentness/independence records under a separately trusted proof boundary.

Remediation was performed on branch `remediation/v24-i11-v6-proof-resolution`. The shared construction-only resolver `governance-runtime/v24_v6_proof_reference_closure.py` now makes the R1 proof validators load-bearing for R2. `proof_context` and `trusted_boundary` are supplied separately from the candidate bundle; candidate-embedded context cannot substitute for them.

R2 was migrated so exact proof closure and recomputable binding material are required for:
- normative catalog qualification and endpoint-table qualification;
- endpoint-table bytes consumed by applicability;
- applicability compiler and applicable-predicate universe;
- evaluator mechanisms and evaluator/condition universe;
- predicate coverage verifier and upstream applicability/evaluator artifacts;
- endpoint projection, including the true-predicate set and exact compiled table.

The repair also rejects artifact substitution between R2 stages instead of trusting downstream state labels.

### Preserved proof-resolution failure

Run `35002507190`: **FAILURE / genuine false-green**.

The preserved R2 falsification demonstrated that opaque endpoint-table/catalog qualification state could still be treated as authority. The test was retained and the production mechanism was repaired rather than weakening the falsification.

### Proof-resolution validation

Run `35003864194`: **SUCCESS** for the repaired R2 chain together with the shared proof resolver and then-current R3/R4 regressions.

All-up proof-resolution run `35007121039`: **SUCCESS**. It passed the shared resolver, R2-R8 migrated suites, and every preserved opaque-proof regression.

Subsequent R9 dependency-closure run `35007800567`: **SUCCESS**, again preserving the R2-R8 proof-resolution gate while also validating the successor shared-dependency freeze repair.

Remediated R2 production blob at this evidence update: `600abaa446e6711d24f2834b7b6ff14ea8b30aa5`.

No WDPC scientific case was executed by this remediation. Runtime qualification remains `NOT_CLAIMED`; scientific execution remains closed pending successor review.

`R2_POST_REVIEW_PROOF_RESOLUTION = PASS`

`R2_RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
