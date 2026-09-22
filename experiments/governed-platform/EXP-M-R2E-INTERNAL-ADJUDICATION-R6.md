# EXP-M R2E Internal Adjudication R6 — External Static Review R5

Status: **CHANGES_REQUIRED / REMEDIATION_AUTHORIZED**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This adjudication responds to the independent no-Git static review preserved in `EXP-M-R2E-EXTERNAL-REVIEW-R5.md`. The reviewer correctly limited Git/runtime provenance claims. This adjudication independently inspected the exact frozen source candidate `30faa9e8e410e27fce9ac8358825a62cd71cc3a0` through the repository connector.

## R6-01 — Ambient source-freeze state in production authority

Reviewer severity: Critical

Disposition: **CONFIRMED**

The frozen `AuthorityHandle._source_freeze()` reads `EXP-M-SOURCE-FREEZE.json` from the ambient working tree. `resolve_reviewed_commit()`, `resolve_reviewed_tree()`, `expected_delivery()`, `load_predicate_context()`, and `authority_context_valid()` depend on that ambient artifact.

Required remediation:
- remove ambient source-freeze reads from production authority resolution;
- bind the authority handle to an explicit content-addressed source commit/tree supplied by the execution boundary;
- derive delivery binding from the preregistered authority policy plus that explicit source identity;
- fail closed when explicit source identity is absent;
- add a regression attack proving a substituted working-tree freeze file cannot redirect production authority.

## R6-02 — Self-falsification context wrapper masks test intent

Reviewer severity: Critical

Disposition: **CONFIRMED AS EVIDENCE-INTEGRITY DEFECT**

The frozen self-falsification wrapper accepts a `context` argument but ignores it and always supplies `AUTHORITY_CONTEXT`. The compatibility `context_from_state()` likewise returns `AUTHORITY_CONTEXT` regardless of input. Several cases therefore do not exercise the context semantics suggested by their call site.

Required remediation:
- production `evaluate_admissibility` calls in self-falsification must consume an explicit context argument;
- evidence attacks that are intended to run under valid authority must pass `AUTHORITY_CONTEXT` explicitly;
- the self-derived/forged-context case must use an independently constructed unauthorized context and assert the authority rejection reason;
- the self-falsification integrity gate must reject wrappers that discard caller-supplied context.

## R6-03 — Assertion-less compound case can false-green

Reviewer severity: Critical

Disposition: **CONFIRMED**

`verify_exp_m_test_integrity.py` proves only the presence of required mechanism call names. `CaptureResult.addSuccess()` maps every successful unittest to `rejected=true`. Therefore an assertion-less test that merely calls the production mechanism can be misreported as a rejected attack.

Required remediation:
- every authoritative CA method must prove explicit rejection semantics, not merely call presence;
- the integrity gate must require assertion structure tied to the observed mechanism result/reason;
- the compound runner must consume an explicit rejection witness emitted by each test rather than treating generic unittest success as rejection;
- add a negative integrity probe containing a required call but no rejection assertion and prove the gate rejects it.

## R6-04 — Dynamic string shortcut bypass

Reviewer severity: Critical subfinding

Disposition: **CONFIRMED**

The executable-shortcut AST scan ignores string constants used by dynamic attribute access such as `getattr(..., "with_missing_r5_protocol_for_test")`.

Required remediation:
- reject forbidden shortcut tokens when used as executable dynamic-access strings;
- preserve documentation/docstring strings without false positives;
- add a regression probe for `getattr`-based bypass.

## R6-05 — Reviewer-suite source-files caller binding

Reviewer severity: High

Disposition: **PARTIALLY_CONFIRMED / DEFENSE-IN-DEPTH HARDENING REQUIRED**

The current verifier recomputes each reviewer-suite file from `source_commit` and separately checks preregistered hashes, so the reviewer-suite content itself is not accepted solely from `source_files`. However the function contract accepts a caller-provided map without independently proving that map is the canonical source-freeze map for the same source identity.

Required remediation:
- derive or independently verify the relevant source-file hashes from the explicit source commit;
- reject a caller map that does not exactly match the commit-derived reviewer-suite hashes;
- retain preregistration ancestry/hash checks.

## R6-06 — No-Git limitations

Disposition: **REVIEWER LIMITATION, NOT CANDIDATE CLOSURE**

The reviewer could not independently execute Git plumbing, CA-7/CA-8 synthetic commits, mutation subprocesses, RSA verification, or S->E->P->Q ancestry. Those claims remain unverified by that reviewer. Prior GitHub CI execution is project evidence but does not convert the no-Git review into an independent runtime verification.

## Preserved prior R3 status

- CA-7 simulated-outcome defect: statically closed, pending fresh post-R6 runtime evidence.
- CA-8 simulated-outcome defect: statically closed, pending fresh post-R6 runtime evidence.
- Positive controls: retained, but must be regenerated after R6 remediation.
- EXP-M remains NOT_QUALIFIED.
- Authority effect remains NONE.
- Live provider/API execution remains false / unauthorized.

## R6 closure rule

No finding in this adjudication may be closed by documentation alone. Closure requires:
1. remediation committed after this adjudication;
2. fresh offline falsification on the remediated head;
3. explicit regression attacks for R6-01 through R6-05;
4. zero surviving compound attacks and zero test-integrity findings;
5. a new source-freeze S created only after the remediated head is green;
6. fresh S->E->P->Q and portable-bundle verification;
7. independent review of the new bundle.

Until then:

- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized
