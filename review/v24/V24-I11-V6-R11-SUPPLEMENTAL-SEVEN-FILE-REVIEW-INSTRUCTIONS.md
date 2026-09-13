# V24 I11 V6 R11 — Supplemental Seven-File Independent Review Instructions

Status: **R11 ALREADY REJECTED / R12 REQUIRED / R12 SCOPE PENDING SUPPLEMENTAL REVIEW**

Authority effect: `NONE_EVIDENCE_ONLY`

## Purpose

Complete the clean R11 systemic review by reading the seven supplied files that the prior reviewer explicitly did not fully inspect. Do not repeat package identity verification unless a new mismatch is discovered. Preserve the already accepted R11-C1, R11-C2, and R11-C3 findings unchanged.

## Files that must be read in full

1. `candidate/governance-runtime/v24_admission_application_witness.py`
2. `candidate/governance-runtime/v24_completeness_bootstrap.py`
3. `candidate/governance-runtime/v24_aggregate_budget.py`
4. `candidate/governance-runtime/v24_generation_migration.py`
5. `candidate/governance-runtime/v24_review_proof_audit.py`
6. `candidate/governance-runtime/v24_authority_surface_inventory.py`
7. `candidate/governance-runtime/validate_runtime.py`

Read any directly-called candidate dependency needed to understand a material authority path, but do not broaden into an unrelated new review.

## Questions to answer

For each file:
- Does it create, inherit, infer, validate, or consume any authority-bearing state?
- Can caller-provided labels, booleans, names, counts, digests, or status strings substitute for independently-bound evidence?
- Can any omission, stale record, duplicate, replay, rollback, alternate path, or self-derived source produce a false-green result?
- Can any code path weaken the accepted R11-C1 interpreter-isolation requirement, R11-C2 trusted/candidate process-boundary requirement, or R11-C3 executed-adversarial-evidence requirement?
- Does it change the prior H, I, P, or Q conclusions?
- Does it expose a new R12-required repair?

## Required focused output

Return:

1. `SUPPLEMENTAL_CONTENT_SCOPE = COMPLETE | INCOMPLETE`
2. `NEW_CRITICAL_FINDINGS = <integer>`
3. `NEW_HIGH_FINDINGS = <integer>`
4. Findings, each with exact file/function, concrete false-green/bypass path, governing V6/R11 rule, and narrow repair requirement.
5. `H_AMENDMENT = NONE | <text>`
6. `I_AMENDMENT = NONE | <text>`
7. `P_AMENDMENT = NONE | <text>`
8. `Q_AMENDMENT = NONE | <text>`
9. `R12_SCOPE_ADDITIONS = NONE | <explicit additions>`
10. `R12_SCOPE_CAN_NOW_FREEZE = YES | NO`

Do not downgrade or remove the three already accepted R11 blockers:
- runtime interpreter isolation must be verified from actual process state;
- candidate code must not share mutable trusted result-accounting state;
- mandatory adversarial checks require bound executed evidence, not names alone.

If any of the seven files cannot be read in full, set `SUPPLEMENTAL_CONTENT_SCOPE = INCOMPLETE` and `R12_SCOPE_CAN_NOW_FREEZE = NO`.

End exactly:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
