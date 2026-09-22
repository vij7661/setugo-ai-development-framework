# EXP-M R2E Internal Adjudication R7 — R5/R6 Remediation Closure

Status: **REMEDIATED_PENDING_FRESH_AUTHORITATIVE_CHAIN_AND_EXTERNAL_REVIEW**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This adjudication closes the implementation work authorized by `EXP-M-R2E-INTERNAL-ADJUDICATION-R6.md` only at the local/offline remediation layer. It does not grant qualification, authority, or runtime authorization.

## Candidate and fresh offline evidence

- Remediated candidate commit: `ca219eb3a88075c89c9b4fc1c75b9d2d5a1e1505`
- GitHub Actions run: `35720768749`
- Workflow: `EXP-M R2E Offline Falsification`
- Result: **SUCCESS**
- Exact-candidate checkout: PASS
- Offline unit/phase and local S->E->P->Q preflight: PASS
- No-live-provider/API marker assertion: PASS

Intermediate remediation commits that failed while the patch set was incomplete are preserved in Git history but are not closure evidence.

## R7-01 — Ambient source-freeze authority redirection

R6 finding: R6-01

Disposition: **REMEDIATED_PENDING_EXTERNAL_FALSIFICATION**

Implemented:
- production `AuthorityHandle` no longer reads `EXP-M-SOURCE-FREEZE.json`;
- current S identity is supplied as explicit content-addressed `source_commit` / `source_tree` execution input;
- evidence subprocesses receive S through `EXP_M_SOURCE_COMMIT` / `EXP_M_SOURCE_TREE`;
- missing or invalid explicit identity fails closed;
- `AuthorityHandle._verified_root()` rebinds the in-memory root to the preregistered Git root object so removing the ambient freeze does not permit caller-substituted root policy;
- regression test `test_r5_ambient_source_freeze_cannot_redirect_authority` corrupts the working-tree freeze file and proves production authority identity/delivery resolution is unchanged;
- regression test `test_r5_invalid_explicit_source_binding_fails_closed` proves invalid source identity cannot be accepted.

## R7-02 — Self-falsification context masking

R6 finding: R6-02

Disposition: **REMEDIATED_PENDING_EXTERNAL_FALSIFICATION**

Implemented:
- the self-falsification wrapper now passes the caller-supplied context to production instead of silently replacing it with `AUTHORITY_CONTEXT`;
- evidence-only attacks that intentionally use valid authority pass `AUTHORITY_CONTEXT` explicitly;
- candidate-derived contexts are produced through the unauthorized fixture adapter;
- `self_derived_context` now requires the production reason `expectation_authority_invalid`;
- the integrity checker statically rejects a self-falsification wrapper that discards its explicit context.

## R7-03 — Assertion-less compound false-green

R6 finding: R6-03

Disposition: **REMEDIATED_PENDING_EXTERNAL_FALSIFICATION**

Implemented:
- each CA-1..CA-10 method now has an independently checked rejection contract covering its required production mechanism and expected assertion structure;
- generic `unittest` success is recorded only as `test_passed`, not as attack rejection;
- `run_reviewer_compound_attacks.py` derives `rejected=true` only when the test passes, the frozen suite source matches the exact S Git object, and the method's rejection contract is valid;
- a synthetic assertion-less CA probe must be rejected by the integrity gate.

## R7-04 — Dynamic shortcut access

R6 finding: R6-04

Disposition: **REMEDIATED_PENDING_EXTERNAL_FALSIFICATION**

Implemented:
- executable dynamic attribute names passed to `getattr`, `setattr`, `hasattr`, or `delattr` are inspected for forbidden shortcut tokens;
- ordinary documentation strings remain non-executable and do not create false positives;
- an explicit `getattr(..., "with_missing_r5_protocol_for_test")` regression probe must be rejected.

## R7-05 — Reviewer source-map self-binding

R6 finding: R6-05

Disposition: **REMEDIATED_PENDING_EXTERNAL_FALSIFICATION**

Implemented:
- `verify_reviewer_suite_frozen()` derives reviewer-suite hashes directly from the explicit `source_commit`;
- the caller-supplied reviewer subset of `source_files` must equal the commit-derived map;
- preregistration ancestry and preregistered-content hash checks remain independently enforced;
- a tampered source-map regression control must fail with `reviewer_suite_source_map_not_commit_derived`.

## Prior R3 protections retained

- CA-7 uses real synthetic Git deletion and the unmodified prior-evidence verifier.
- CA-8 uses real synthetic Git reviewer-suite mutation and the unmodified reviewer-freeze verifier.
- Positive controls remain mandatory.
- The independent R5 review is preserved in `PRIOR-EVIDENCE-INDEX.md`.

## Remaining closure requirements

This adjudication is not authoritative final closure. The next steps are mandatory:

1. freeze a new source identity S after this adjudication is part of the governed source;
2. generate a fresh remote S->E->P->Q chain;
3. require final S-E-P-Q and portable-bundle verification to pass;
4. preserve EXP-M = NOT_QUALIFIED and Authority effect = NONE;
5. obtain a new independent review of the resulting bundle, including adversarial review of R7-01 through R7-05.

Until that independent review completes:

- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized
