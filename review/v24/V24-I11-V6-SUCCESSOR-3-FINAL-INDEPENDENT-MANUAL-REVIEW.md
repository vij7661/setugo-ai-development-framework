I missed a couple in the earlier `view` (it was probably truncated). Let me read the dedicated PRC-1 test files closely, especially the RED reproduction and manual-review-RED tests.

Let me actually attempt the PRC-1 self-grant attack directly against the production code.

PRC-1 self-grant confirmed working against production code. Now let's examine DA-1.

Let's confirm the shipped test suite passes (to understand what "green" actually covers) and check if any existing test attempts the cross-module compound attack we just found.

# Independent Manual Engineering Review — V24-I11-V6-INTEGRATED-SUCCESSOR-3

## Disposition: **CHANGES_REQUIRED**

## 1. Candidate identity

| Field | Value |
|---|---|
| Family | `V24-I11-V6-INTEGRATED-SUCCESSOR-3` |
| Commit | `b4b91dcf5855ae2bb7162c0b94d1a79a8a64e171` |
| Tree | `a81204c73016243556c6eefd711bc91c37adda49` |
| Package manifest | 48/48 files hash-verified against `PACKAGE-MANIFEST.json` — no integrity discrepancies |
| Exact final-head run | `35072181274` |

## 2. Adjudication of the three blocking findings

### PRC-1 — **NOT CLOSED (Critical, blocking)**

The repair adds an "external" `V24_V6_TRUSTED_BOUNDARY_ANCHOR_SHA256` env var check in `validate_proof_context`. I built a full end-to-end forged proof chain (root genesis record, qualification, independence record, currentness bindings, proof context, trusted boundary) using **only exported production functions** (`digest`, `trusted_boundary_anchor_digest`, `seal_proof_context` — no test-only helper imported), then set the "external" anchor env var myself to match my own self-built boundary, exactly the way `v24_v6_test_proof_context.py`'s `_trusted_boundary_for_test` does it. Result:

```
SELF-GRANT ATTACK RESULT: True PROOF_REFERENCE_CLOSED
problems: []
```

This is not "external trust exists" (which the instructions say not to flag) — it's that nothing in the code distinguishes an anchor set by a genuinely independent process from an anchor set by the same caller constructing the context it's meant to police. `os.environ` is read fresh on every call (no import-time freeze, no separate process boundary, no signature/HMAC/keyed check), and the digest function that must match it is public and importable by anyone. The only thing preventing this in "production" today is a documentation convention ("production modules may not import that helper") — confirmed true by grep (only test files import/write the anchor) — but nothing *structural* enforces it. The regression test added for this (`test_prc1_self_constructed_trusted_boundary_is_rejected`) only checks the case where the attacker *reuses the old, unmodified* anchor value against a new context; it never tests updating the anchor to match the forged boundary, which is the actual attack and is exactly what every other positive fixture in the suite already does as routine construction.

**Failure path:** any caller that can construct `proof_context`/`trusted_boundary` and has `os.environ` write access (true of any code in the same process) can self-grant unlimited trust.
**Narrow repair:** the anchor must come from something the checking code cannot itself produce — e.g., an HMAC/signature keyed with a secret unavailable to the validating process, or verification performed out-of-process/out-of-band, with a test asserting that *setting the env var to match a self-built boundary* still fails.

### DA-1 — **Join logic sound in isolation, but not independently closed (High, blocking as a system)**

`canonical_decision_content_digest` correctly folds in `authorized_effect_path_id`, `authorized_effect_path_content_digest`, and `authorized_effect_class_id`, and the qualification proof required for `decision_qualification_digest` must resolve against that exact recomputed digest (`_close_decision_proofs`, `subject_content_digest=canonical_decision_content_digest(decision)`), plus apply-time exact-match checks against the *active* (possibly reevaluated) decision. Attempted substitutions of `path_id`, `path_content_digest`, decision context, and stale-decision replay all correctly failed with `DECISION_EFFECT_PATH_*_BINDING_MISMATCH` / `DECISION_CONTENT_DIGEST_MISMATCH` in isolated testing — this part of the repair is real.

However, because the qualification that "closes" the new canonical digest is obtained through the same broken PRC-1 resolver, I compounded the attack: forged a complete proof chain (as above) qualifying a decision whose `authorized_effect_path_id`/content/effect-class point at PATH-2 while the original legitimate decision only ever authorized PATH-1, and self-granted the anchor.

```
ATTACK RESULT allowed: True state: DECISION_APPLY_LATCH_READY
problems: []
```

DA-1's binding rule is only as strong as PRC-1. It is not independently closed.

### NCP-1 — **Binding tuple sound in isolation, same transitive exposure (Critical as system, blocking)**

`canonical_catalog_control_binding_digest` correctly covers exactly `(candidate_clause_id, control_id, artifact_sha256, normative_artifact_blob_sha, candidate_span_digest)`, and `validate_catalog_candidate_coverage` requires a fresh `GOVERNED_QUALIFICATION` over that exact digest, so a bare `control_id` swap with stale proof correctly fails (confirmed by the shipped `test_ncp1_control_reassignment_requires_new_authorized_binding`, and by inspection). There is no independent catalog-integrity anchor beyond `close_governance_dependencies`, so this too routes through the compromised PRC-1 resolver and is defeatable by the identical self-grant technique (construct a qualification whose `subject_content_digest` equals the new binding digest, wrap it in a self-forged context, self-grant the anchor).

## 3. Cross-cutting systemic finding (Critical)

R2–R8 (endpoint projection, material surface, decision/apply, normative projection, effect ledger, mode registry, case-universe/qualification-integrity) all bottom out in the same `resolve_governed_qualification` / `close_governance_dependencies` in `v24_v6_proof_reference_closure.py`. Because that single module's root-of-trust check collapses to a self-computable-and-self-settable environment variable, **every authority-bearing check in the system inherits the same single point of failure** — this is exactly the "Object A qualified + Object B qualified implies A→B" collapse the review was asked to hunt for, except it's worse: it's "anything can be self-qualified," which subsumes the individual A→B binding questions.

## 4. Positive attacks that failed (repair is doing real work where it's reached)

- Reusing an old/unmatched trusted anchor against a newly-built context — correctly rejected (`EXTERNAL_ANCHOR_MISMATCH`).
- Path A→B substitution, decision-context substitution, stale/cross-generation replay, cross-pair genesis composition, shared-control independence, non-`QUALIFIED`/non-`CURRENT` embedded records, proof cycles, wrong-subject qualifications — all correctly rejected under a *genuinely* fixed external anchor.
- `control_id`-only reassignment with stale proof — correctly rejected.
- Missing/`None` trusted boundary, candidate-embedded `governance_proof_context`/`trusted_boundary` fields — correctly rejected.
- Full existing suite (225 tests) passes; the package-manifest hashes are all correct — no tampering in transit.

## 5. Evidence/runtime limitations

This is construction-level review only. I did not (and per scope should not) assess real process/secret isolation for the anchor in an actual deployment, concurrency fencing, durable external writes, or external verifier semantics — but the finding above is precisely a *construction-level* gap (a self-computable digest check with no cryptographic asymmetry), not a runtime-environment question, so it is in scope and blocking.

## 6. Historical evidence — preserved as instructed

`35070903107` (genuine pre-fix RED), `35071250976`/`35071608899` (tooling-preflight only, no production mutation), `35071757663`, `35071849800`, `35072081665`, `35072181274` (GREEN runs) are left as classified; none of the later GREENs rewrite the earlier RED, and none of the GREENs actually exercised the self-grant compound attack documented here, so they do not conflict with this finding — they simply never tested for it.

## 7. Final progression statement

PRC-1, DA-1, and NCP-1 are **not** independently closed. DA-1 and NCP-1's own binding logic is well-constructed, but the whole chain roots in a PRC-1 "external anchor" that is trivially self-grantable by any caller with the same access as the code it's meant to constrain. This keeps scientific/runtime execution closed per the package binding; another repair (an anchor mechanism with real asymmetric/out-of-process verification, plus a regression test that self-updates the anchor to match a forged boundary and expects rejection) and re-freeze/re-review cycle is required before a future successor can be considered. This assessment is review evidence only and grants no runtime, deployment, or scientific authority.
