# EXP-M Deterministic Implementation — External Review R1

Overall disposition: `CHANGES_REQUIRED`

Scope: independent implementation/falsification review of the deterministic EXP-M implementation.

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification remains blocked.

## Critical findings

1. **C-01 — Phase D hard-coded / taxonomy not exercised**
   - Phase D does not call the production insufficient-evidence adjudicator.
   - Required fix: production taxonomy must be exercised with single, mixed, unresolved, and delivery/context-vs-scientific cases.

2. **C-02 — Phase G hard-coded PASS**
   - Phase G does not execute mutation suites.
   - Required fix: Phase G must derive PASS from actual mutation execution with meaningful zero survivors.

3. **C-03 — Admissibility predicate closure tautological**
   - Predicate IDs, mutation IDs, and fixture IDs are sourced from the same tuple.
   - “Validator logic mutations” toggle input booleans instead of mutating/bypassing actual production guards.
   - Required fix: independent registries plus real predicate-specific validators and independently killed production-logic mutations.

4. **C-04 — Provider capability qualification model not enforced**
   - Preflight accepts a bare provider `qualified=True`.
   - Execution plan, qualification record, expiry, profile hash, supported formats, context limit, operating point, attempt closure and statistics are not load-bearing.
   - Required fix: production preflight/admission must compute capability currentness from actual records/plan/current time/operating point/attempt closure.

5. **C-05 — Provider context isolation is trusted-boolean only**
   - Context state/policy/fence types exist but are not integrated into authoritative preflight/admission.
   - Required fix: compute context isolation from evidence, policy, readback/sentinel, hidden-state residual rule and current fence.

6. **C-06 — Atomic admission / TOCTOU absent**
   - No final atomic state revalidation at admission.
   - Required fix: final compare-and-set style admission revalidating all load-bearing versions/hashes and permanently voiding attempts invalidated after dispatch.

7. **C-07 — Retrieval final-context binding missing**
   - No production retrieval evidence proving source/version/range/returned bytes/tool-result/final-context binding.
   - Required fix: implement and enforce exact retrieval evidence.

8. **C-08 — Witness/accessibility boundary incomplete**
   - Witness qualification record and important accessibility attacks are not load-bearing.
   - Required fix: current witness qualification + budget/eviction/non-evaluative/final-context checks.

9. **C-09 — Delivery/wire/receipt not bound to returned bytes/hashes**
   - Completion can trust IDs/booleans without validating actual returned payload, semantic/wire hashes, byte counts, representation and source binding.
   - Required fix: byte-level, semantic and source/session/attempt binding.

10. **C-10 — Data/state mutation coverage incomplete**
    - Required attack families are missing from production-validator mutations.
    - Required fix: add real data/state mutations for every load-bearing invariant.

11. **C-11 — Self-falsification insufficient**
    - Eight self-falsification cases do not cover the Critical/High attack surface.
    - Required fix: expand self-falsification across the full production path.

## High findings

1. **H-01 — A-T mostly happy-path; negative fixtures absent**
2. **H-02 — load-bearing R5 invariants represented as trusted booleans**
3. **H-03 — reviewed source/commit mismatch not enforced**
4. **H-04 — capability expiry/profile hash ignored**
5. **H-05 — prompt-isolation record unused**
6. **H-06 — egress revocation/post-preflight expiry not modeled**
7. **H-07 — attempt ledger/retry transparency too weak**
8. **H-08 — materialization not implemented**
9. **H-09 — representation binding incomplete**
10. **H-10 — Phase O closure tautological**

## Medium/Low findings

- archive/materialization safety incomplete;
- representation semantic binding incomplete;
- received byte counts not checked;
- provider format/context limits unused;
- non-production checks used in Phase D/T;
- wrong-commit test does not verify production rejection;
- attempt-substitution logic narrow;
- retry-to-plan mapping not enforced;
- ProviderContextIsolationPolicy unused;
- ProviderAccessibilityRiskPolicy unused.

## Reviewer verdicts

```text
FROZEN_DESIGN_FIDELITY = FAIL
A-T = FAIL for every phase
VALIDATOR_LOGIC_MUTATION_COVERAGE = FAIL
DATA_STATE_MUTATION_COVERAGE = FAIL
ADMISSIBILITY_PREDICATE_CLOSURE = FAIL
SURVIVORS_ZERO_PROVEN = FAIL

AUTHORITY_SNAPSHOT = FAIL
REQUIRED_EVIDENCE_CONTRACT = FAIL
INTERACTION_CONTRACT = FAIL
MATERIALIZATION = FAIL
REPRESENTATION_BINDING = FAIL
PROVIDER_CAPABILITY_MODEL = FAIL
QUALIFICATION_ATTEMPT_CLOSURE = FAIL
RETRY_TRANSPARENCY = FAIL
PROVIDER_CONTEXT_ISOLATION = FAIL
ADMISSION_FENCE = FAIL
WIRE_BINDING = FAIL
WITNESS_ACCESSIBILITY = FAIL
RETRIEVAL_FINAL_CONTEXT_BINDING = FAIL
PROMPT_ISOLATION_BINDING = FAIL
INSUFFICIENT_EVIDENCE_TAXONOMY = FAIL
ATOMIC_ADMISSION = FAIL
```

Final reviewer counts:

- unresolved Critical: 11
- unresolved High: 10
- deterministic implementation review closure: NO
- live provider qualification planning: NO
- live provider/API execution: NO
- EXP-M state: NOT_QUALIFIED
- authority effect: NONE

## Project adjudication

The external review is accepted as valid defect evidence.

The previously reported green deterministic summary is superseded as qualification evidence. Historical results remain preserved, but they do not prove deterministic closure.

No live provider/API work may start.

Remediation must target production-path mechanisms, not add more summary booleans or narrative PASS labels.
