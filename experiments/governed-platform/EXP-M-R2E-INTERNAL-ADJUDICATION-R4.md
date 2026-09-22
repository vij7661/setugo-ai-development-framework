# EXP-M R2E Internal Adjudication R4 — Falsification-Mechanism Integrity

Status: **REMEDIATED_PENDING_FRESH_GREEN_CHAIN_AND_EXTERNAL_REVIEW**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This adjudication responds to independent adversarial review R3, which demonstrated that legacy CA-8 used ambient working-tree state plus a simulated failure shortcut, and that legacy CA-7 similarly injected its expected failure reason instead of mutating real evidence.

## R4-01 — Reviewer-suite-freeze ambient-state dependency

Severity: **Critical**

Remediation:
- `verify_reviewer_suite_frozen()` now requires explicit `source_commit` and `source_files` inputs.
- It no longer reads `EXP-M-SOURCE-FREEZE.json` from the ambient filesystem.
- The enclosing S-E-P-Q verifier passes the source commit and source-file map already loaded from the verified E-side freeze artifact.
- A dedicated integrity gate rejects any reintroduction of `FREEZE_PATH` or ambient read calls inside this function.
- A positive control requires the unmodified real S to pass before CA-8 negative evidence can count.

## R4-02 — CA-8 tautological simulated mutation

Severity: **Critical**

Remediation:
- Legacy `simulate_suite_mutation` is removed from the production verifier API.
- A new reviewer-authored mechanism-integrity suite was preregistered at commit `24415847085e4032a9892aaa8730806bd246225e` before the verifier remediation.
- CA-8 now creates a real synthetic Git child commit that mutates `reviewer_exp_m_r2e_authority_suite.py`.
- It supplies the original frozen source-file hash map to the unchanged verifier and requires organic detection through `reviewer_suite_hash_drift` or preregistered-hash drift.
- The authoritative compound runner executes only the ten CA-1..CA-10 methods from this real-path suite; the legacy simulated suite remains preserved as historical evidence only.

## R4-03 — CA-7 forced prior-artifact deletion result

Severity: **Medium**

Remediation:
- `simulate_deleted_indexed_artifact` is removed from the prior-evidence verifier API.
- Prior-index parsing is content-addressed through an explicit `index_commit`; the ambient working-tree index is no longer authoritative.
- CA-7 now creates a real synthetic Git child commit deleting an indexed prior review while leaving the source index unchanged.
- The unchanged verifier must organically return `indexed_prior_artifact_deleted_after_source_freeze`.
- A positive control requires the genuine source/index pair to pass before this negative case counts.

## R4-04 — Cross-cutting test-oracle/mechanism-bypass false-green class

Severity: **High governance gap**

Remediation:
- Added `verify_exp_m_test_integrity.py` as a governed evidence command.
- It statically requires every authoritative CA-1..CA-10 method to invoke the production/verifier mechanism associated with that attack.
- It rejects executable `simulate_*`, `force_*`, `mock_*`, and `with_missing_r5_protocol_for_test` references in the authoritative suite.
- It proves the compound runner imports the mechanism-integrity suite and does not treat the legacy simulated suite as authoritative.
- It audits self-falsification for hardcoded boolean outcomes and the mutation harness for hardcoded `killed`/PASS/REJECT outcomes.
- It audits self-falsification source/tree binding to the compound results and the mutation harness for real isolated production-guard mutation markers.
- It runs positive controls for reviewer-suite freeze and prior-evidence preservation so a constant-reject implementation cannot satisfy CA-7/CA-8.

## R4 closure rule

This internal adjudication cannot grant PASS. Closure requires:
1. exact latest-source offline falsification succeeds;
2. test-integrity evidence reports zero findings and both positive controls pass;
3. real-path CA-1..CA-10 execute with zero survivors;
4. fresh local S->E->P->Q and portable-bundle verification succeed;
5. a new authoritative remote S->E->P->Q chain is frozen after all R4 changes;
6. the resulting portable bundle is independently reviewed.

Until independent review:
- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized
