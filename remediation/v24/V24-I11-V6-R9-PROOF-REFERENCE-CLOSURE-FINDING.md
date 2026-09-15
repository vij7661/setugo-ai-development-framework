# V24 I11 V6 R9 — Proof-Reference Closure Finding

Status: **GENUINE IMPLEMENTATION DEFECT / CHANGES REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Frozen subject

- predecessor candidate: `88cba7e1224ecbd5a8264ba4c31c4c264fc24fef`
- predecessor tree: `97146905411b258b5c7a8cab1beb725ff3b19bc0`
- approved V6 raw SHA-256: `96ec464fbf602ac6b8c89fca5af16aa71a8d53f9f042605e46a07b4cd628ca62`
- approved V6 plan-body SHA-256: `286217399947144630c29e991c3529dfee64d382be08a6ccd3f87e9fc5173ad5`
- predecessor successor-verification run: `34758715430`

The frozen predecessor remains immutable. Repair work occurs only on `remediation/v24-i11-v6-proof-resolution`.

## Finding V6-PRC-001 — Opaque qualification references can be treated as proved authority

**Severity:** Critical

### 1. Authority-bearing path

The concrete demonstrated path is the R4 `evaluate_decision_apply_latch` path. The same reference-consumption pattern is also present across R2-R8 mechanisms that consume qualification, independence, currentness, verifier, witness, parser, registry, compiler, or gate references.

### 2. Governing V6 contract

Approved V6 Sections 4-5 require every authority-bearing governance object/mechanism to inherit exact generic qualification, currentness, independence, anti-self-qualification, and reviewer-safe exact binding. Sections 8-16 make those qualified/current dependencies load-bearing for endpoint projection, material/effect closure, decision/apply, normative disposition, atomic binding, and result accounting.

A SHA-shaped `*_qualification_digest` or state label is a reference to evidence; it is not itself evidence that the referenced record exists, recomputes, belongs to the exact subject, is current, is independent, or is rooted in permitted genesis trust.

### 3. Concrete false-green

On the frozen predecessor, the inherited R4 positive fixture supplies opaque 64-hex strings for qualification/currentness/independence references and caller-provided `QUALIFIED` / `CURRENT` labels, but supplies no exact resolvable governance evidence store. `evaluate_decision_apply_latch` nevertheless returns `allowed=True` when the labels and local digest fields are mutually consistent.

A falsification test was added without changing predecessor production semantics:

- branch: `remediation/v24-i11-v6-proof-resolution`
- RED test commit: `4fd5fa309d4a1be5c61c14af993479465eb68e08`
- workflow commit: `3160c540af4a21e1b94d8403be7ecaf4cf0da22e`
- workflow run: `35000549932`
- compile step: PASS
- `Falsify opaque qualification reference path`: **FAIL**

This is an expected RED proving the candidate permits the forbidden path.

### 4. Narrow required repair

Introduce one generic proof-reference closure boundary rather than bespoke per-case patches.

For every load-bearing qualification/currentness/independence reference used by R2-R8:

1. resolve the exact referenced record from a candidate/environment-bound governance evidence surface;
2. recompute the referenced record digest and reject unknown/mismatched references;
3. validate it through the applicable R1 generic validator;
4. bind it to the exact expected subject ID/content digest and required result;
5. recursively resolve verifier/independence/currentness dependencies;
6. reject cycles, missing records, stale records, wrong-subject records, and self-grant paths;
7. permit recursion termination only through exact paired membership in the governed genesis trusted scope or another explicitly admitted V6 root rule;
8. keep the trusted genesis/root input separated from caller-provided decision data;
9. make downstream R2-R8 authority-bearing functions fail closed when proof closure is absent;
10. add adversarial regressions for unknown digest, wrong-subject digest, stale evidence, cyclic qualification graph, cross-pair genesis substitution, and fabricated witness/reference labels.

### 5. Affected surfaces

At minimum re-audit and repair:

- `v24_v6_endpoint_projection.py`
- `v24_v6_material_surface.py`
- `v24_v6_decision_apply.py`
- `v24_v6_normative_clause_projection.py`
- `v24_v6_effect_ledger_closure.py`
- `v24_v6_atomic_binding_modes.py`
- `v24_v6_qualification_integrity.py`
- R9 integrated successor verification and its complete regression surface

The R3 material-observation witness path is a concrete additional instance: caller-provided `CURRENT` / `QUALIFIED` witness labels and a different control-domain string can satisfy the current implementation without resolving exact witness independence/currentness evidence.

## Gate consequence

The predecessor candidate `88cba7e...` must remain `CLOSED_PENDING_SUCCESSOR_REVIEW` and must not be advanced to scientific WDPC execution. Its earlier GREEN construction run remains historical evidence and is not rewritten, but it is superseded as a review candidate by this later genuine defect discovery.

Any repaired successor requires a new commit/tree, full affected and inherited regression, a regenerated exact successor-verification package, fresh clean independent review, repository binding adjudication, and only then scientific falsification.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
