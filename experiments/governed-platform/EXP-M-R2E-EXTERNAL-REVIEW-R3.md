# Independent Adversarial Review — EXP-M Deterministic Implementation R2E — R3

Disposition: **CHANGES_REQUIRED**

Authority effect: **NONE**

EXP-M: **NOT_QUALIFIED**

Live provider/API execution: **not authorized and not performed**

## Independently reproduced controls

The reviewer reported that the portable bundle verifier passed, reconstructed the nested Git history, independently reran the S->E->P->Q verifier successfully, confirmed authority-root-v3 ancestry, inspected dynamic-import/eval/exec and local-import closure, inspected the RSA signature implementation, and found mutation/self-falsification/test counts internally consistent.

## Critical finding — Reviewer-suite-freeze check was ambient and CA-8 was tautological

The reviewer demonstrated that `verify_reviewer_suite_frozen()` read `EXP-M-SOURCE-FREEZE.json` from the local filesystem rather than consuming the already-verified E-side Git object / explicit source identity. Editing only the on-disk freeze file could redirect which source commit the helper validated, without binding that commit to the enclosing `verify_sep_sequence()` source argument.

The reviewer also demonstrated that legacy CA-8 called `verify_reviewer_suite_frozen(simulate_suite_mutation=True)`, whose simulated path returned `reviewer_suite_hash_drift` before the real Git/hash comparison logic ran. Therefore that CA-8 result did not prove the real reviewer-suite-freeze mechanism.

Required remediation:
1. Make reviewer-suite verification accept the explicit source commit/source-files map already verified from E; no ambient governance-state read.
2. Replace simulated CA-8 with a real synthetic Git commit containing a reviewer-suite mutation and invoke the unchanged production verifier.
3. Preserve positive/normal-path evidence so constant rejection cannot masquerade as detection.

## Medium finding — CA-7 used forced failure injection

Legacy CA-7 called `verify_prior_evidence_index(simulate_deleted_indexed_artifact=True)`, which appended the expected failure reason rather than creating a real deletion and observing normal detection.

Required remediation:
- Construct a synthetic commit that actually deletes an indexed historical artifact while leaving the index unchanged and invoke the normal prior-evidence verifier without a simulation flag.

## Cross-cutting review-method implication

The reviewer identified a broader false-green class: an adversarial test can report the expected rejection while bypassing the mechanism it claims to validate. Critical/High falsification evidence must therefore mutate real input/state and traverse the unchanged production mechanism; simulated outcome shortcuts are not authoritative evidence.

## Final disposition

**CHANGES_REQUIRED**

The delivered S->E->P->Q data was not shown to be forged. The blocker is falsification/verifier integrity. EXP-M remains **NOT_QUALIFIED** and authority effect remains **NONE**.
