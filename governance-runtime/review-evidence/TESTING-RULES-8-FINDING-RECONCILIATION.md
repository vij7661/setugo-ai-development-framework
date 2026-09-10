# TESTING Rules Eight-Finding Reconciliation

Status: **RECONSTRUCTED GOVERNANCE EVIDENCE — NOT REVIEWER-VERBATIM**

Source review pack: `Governed_Platform_Rules_Review_Pack.docx`, originally bound to testing head `0286a8f8e6ba8c1b10efe6ab721f28d91591dab5`.
Current reconciliation candidate before this record: `8cf779f99cd8f5215fb1811dcddf57b7f7a48b3a`.

Important evidence boundary: the full returned eight-finding reviewer response is not persisted in the project Library. The user did provide a summary of that response. Four load-bearing findings are directly supported by that summary; four additional findings below are reconstructed from the exact unowned decision points in the reviewed pack. These reconstructed entries MUST NOT be represented as verbatim reviewer findings.

## Governing principle

No evaluated actor may define, weaken, waive, reinterpret, or appoint the authority controlling a material part of its own qualification criteria.

## Directly supported findings from the supplied reviewer summary

### F1 — Adversarial-matrix ownership undefined
- Original reviewed rule: TESTING pass requires `Standard adversarial matrix exercised`.
- Failure shape: the evaluated implementation could choose or weaken the matrix that qualifies it.
- Current mechanism status: **REPAIRED_IN_CONSTRUCTION_AWAITING_INDEPENDENT_REFALSIFICATION**.
- Repair: platform-owned, versioned/hash-bound TESTING adversarial matrix in `governance-runtime/qualification_boundary_policy.py`; required cases cannot be omitted/rebound.

### F2 — Mandatory review-dimension ownership undefined
- Original reviewed rule: required review dimensions must be explicit/unique; BOUNDED_PASS depends on mandatory status.
- Failure shape: candidate/caller could decide which dimensions are mandatory and thereby lower its own qualification bar.
- Current mechanism status: **REPAIRED_IN_CONSTRUCTION_AWAITING_INDEPENDENT_REFALSIFICATION**.
- Repair: platform-owned review profile and policy hash; caller dimensions may add scrutiny but cannot remove/downgrade/rebind the platform floor.

### F3 — `review is needed` decision owner undefined
- Original reviewed rule: manual review by default; assistant tells user when review is needed; pass requires review where policy requires it.
- Failure shape: evaluated/candidate-controlled facts or an unowned judgment can avoid a required review.
- Current mechanism status: **REPAIRED_IN_CONSTRUCTION_AWAITING_INDEPENDENT_REFALSIFICATION**.
- Repair: platform-owned deterministic review-required triggers and protected-path/materiality floor; uncertain consequential materiality escalates rather than waives review.

### F4 — Terminal-authority holder undefined
- Original reviewed rule: terminal authority remains external to model/agent/reviewer execution.
- Failure shape: saying authority is merely `external` does not name who may actually authorize; legacy Slice6 also accepted `PLATFORM_POLICY`, allowing a platform self-grant path.
- Current mechanism status: **REPAIRED_IN_CONSTRUCTION_AWAITING_INDEPENDENT_REFALSIFICATION**.
- Repair: explicit human authority roles by phase/action; generic `HUMAN`, `PLATFORM_POLICY`, models, reviewers, workers and judges cannot mint terminal authority.

## Reconstructed findings from unowned load-bearing decisions in the exact review pack

### F5-R — Contract / acceptance-boundary freeze owner undefined
- Reviewed text says to `Freeze or preregister the contract/acceptance boundary where required`.
- Failure shape: evaluated actor could decide both what is frozen and whether freezing is required, selecting an easier qualification target.
- Current mechanism status: **OPEN_RECONSTRUCTED**.
- Required narrow repair: define a platform-owned rule for which artifact/contract types require preregistration, identify the authority that approves the frozen boundary, SHA-bind it before exposure, and forbid candidate-side waiver/redefinition after first RED.

### F6-R — Root-cause classification authority undefined
- Reviewed text requires `Classify the root cause before repair` and TESTING pass requires all observed failures classified.
- Failure shape: evaluated actor could classify its own implementation failure as TEST/fixture/environment/reviewer error and thereby avoid code repair.
- Current mechanism status: **OPEN_RECONSTRUCTED**.
- Required narrow repair: deterministic evidence rules where possible; contested/material classifications require an independent adjudication record bound to exact failure evidence; the candidate implementation cannot be terminal classifier of its own defect.

### F7-R — Reviewer-finding adjudicator undefined
- Reviewed text says findings are evidence until adjudicated and only adjudicated findings flow into repairs/governance.
- Failure shape: the same actor under evaluation could reject inconvenient reviewer findings as unsupported or accept favorable findings, controlling the evidence gate.
- Current mechanism status: **OPEN_RECONSTRUCTED**.
- Required narrow repair: name an adjudication authority/protocol distinct from candidate/reviewer; require exact-SHA/evidence binding and preserve both raw finding and adjudication result; disagreement cannot silently become PASS.

### F8-R — TESTING-blocking vs deferred phase-classification owner undefined
- Reviewed text says production-only findings are `DEFERRED_TO_RELEASE` / `DEFERRED_TO_PRODUCTION` rather than blocking TESTING.
- Failure shape: evaluated actor could defer a genuine TESTING-contract defect by labeling it production-only.
- Current mechanism status: **OPEN_RECONSTRUCTED**.
- Required narrow repair: phase classification must be derived from the frozen phase contract and governed decision rules; material uncertainty or conflict becomes `REQUIREMENT_UNRESOLVED` / non-promotable rather than candidate-selected deferral.

## Evidence / run history preserved

- Initial qualification-boundary construction run on SHA `c4a480a1e8aa9ac61bbb511b0038cc86a14b6d3d` failed: 60 tests executed, 9 failures and 1 error. This RED is preserved and was not weakened away.
- After fixture/consumer adaptation to the stronger mandatory review floor, run `34437250626` on SHA `716c18838033fc4e4c4cc36f05775d9df4767059` passed the 60-test review/governance suite.
- Terminal-authority integration exposed an additional self-grant path (`PLATFORM_POLICY` accepted as authority source). The path was repaired.
- Run `34437594290` on SHA `8cf779f99cd8f5215fb1811dcddf57b7f7a48b3a` passed both the qualification-boundary/review suite and the terminal-authority ownership regressions.

## Current adjudication state

- F1–F4: construction repair is green but **not independently re-falsified**.
- F5-R–F8-R: **OPEN_RECONSTRUCTED** and must not be called original reviewer-verbatim findings.
- Overall TESTING state: **NOT COMPLETE**.
- Promotion effect: **BLOCKED** pending closure/re-falsification of material ownership gaps and independent review of the exact repaired SHA.

## Recovery rule

If the original full eight-finding reviewer response is later recovered, replace the reconstructed mapping only through a new superseding evidence record. Do not rewrite or delete this reconstruction; preserve lineage and note which reconstructed entries correspond to, differ from, or are absent from the original reviewer findings.
