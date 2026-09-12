# Reviewer Change-Requirement and Existing-Impact Contract — V1

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## RCIC-01 — Purpose

Every governed review request must deliberately ask the reviewer whether changes are required for the exact candidate and must provide the evidence needed to verify that conclusion. A reviewer must not be forced to infer missing code, contracts, tests, dependencies, state, or runtime behavior from summaries.

Reviewer change suggestions are evidence and impact hypotheses, not executable instructions. The implementation/governance side must independently adjudicate the finding and reconcile the suggested change against the existing system before remediation is considered complete.

## RCIC-02 — Deliberate change-required question

Every review request must explicitly ask:

`Are changes required for this exact candidate?`

The reviewer must answer exactly one:

- `YES`
- `NO`
- `INSUFFICIENT_EVIDENCE`

A disposition such as `CHANGES_REQUIRED` does not replace this field. The field exists so the review contract always distinguishes defect detection, recommended remediation, and evidence insufficiency.

## RCIC-03 — Required reviewer change assessment

For every finding for which the reviewer answers that change is required, the reviewer must provide at least:

- finding ID;
- violated invariant/contract or exact requirement;
- concrete failure/false-green path;
- minimum required change at the semantic level;
- why that change is required;
- affected existing code/components/interfaces/state/tests known from the supplied evidence;
- likely regression/compatibility risks;
- evidence/tests that would verify the repair;
- any acceptable alternative repair criteria when the implementation need not match one exact patch.

The reviewer should not prescribe implementation details beyond the evidence available. When impact cannot be established from the supplied material, the reviewer must state the missing evidence rather than speculate.

## RCIC-04 — Required existing-system impact assessment

The reviewer must separately assess whether each recommended change could affect existing behavior. At minimum the review considers, where applicable:

1. direct implementation paths;
2. callers/consumers/dependents;
3. APIs and schemas;
4. events, persistence, ledgers and state migration;
5. provider/adapters and external effects;
6. configuration, policy, credentials and secrets;
7. retries, idempotency, recovery, caches and replicas;
8. tests, fixtures and mocks;
9. telemetry, audit, proof views and dashboards;
10. backward/forward compatibility and rollback.

The reviewer may return `INSUFFICIENT_EVIDENCE` for a surface when the review packet/request does not contain enough material. Silence is not treated as proof of no impact.

## RCIC-05 — VerificationEvidenceManifest before review dispatch

Before a review is sent, the review surface must carry a machine-readable `VerificationEvidenceManifest` bound to the exact candidate commit.

It must explicitly classify these evidence classes:

- `EXACT_CANDIDATE_ARTIFACTS`
- `BASE_TO_CANDIDATE_DIFF`
- `APPLICABLE_CONTRACTS`
- `EXISTING_CODE_IMPACT_SURFACE`
- `INTERFACES_SCHEMAS_STATE`
- `CURRENT_TESTS_AND_RESULTS`
- `KNOWN_FAILURES_AND_DEFERRED`
- `RUNTIME_EXECUTION_EVIDENCE`

Each class is one of:

- `PRESENT`
- `NOT_APPLICABLE`
- `UNAVAILABLE`

Each entry also states whether it is required for the current review, the exact artifact/evidence references when present, and a reason for `NOT_APPLICABLE` or `UNAVAILABLE`.

A review must not be dispatched when an evidence class marked `required_for_review=true` is not `PRESENT`.

## RCIC-06 — Exact evidence, not summaries alone

When the review requires code/design/test verification, the packet/request must provide exact reviewable evidence rather than only a projection or summary. Exact evidence may include full artifacts, exact diffs, dependency/call-impact reports, interface/schema definitions, test outputs, runtime receipts, or equivalent integrity-bound material.

Summaries may orient the reviewer but cannot substitute for required exact evidence.

## RCIC-07 — Missing evidence must be explicit

The review output must contain a `missing_evidence` section. If the reviewer cannot verify a proposed change, affected existing surface, or repair criterion, it must name the missing artifact/data precisely.

The platform must not interpret omitted reviewer discussion as `NO_CHANGE_REQUIRED` or `NO_IMPACT`.

## RCIC-08 — Clean independent review versus remediation verification

Two review modes are distinct:

- `CLEAN_INDEPENDENT_REVIEW`: prior concrete reviewer findings/dispositions are excluded. The reviewer receives the exact candidate, neutral baseline/change data, current code/contracts/tests and impact evidence necessary to review from first principles.
- `REMEDIATION_VERIFICATION_REVIEW`: the protocol may include the specific prior finding and remediation claim so the reviewer can verify closure.

A remediation-verification review does not substitute for a clean independent review when the active governance requires clean-room independence.

## RCIC-09 — Reviewer proposal consideration record

Every reviewer finding that contains a change recommendation must be preserved in the `FindingDispositionRecord` with:

- reviewer-recommended semantic change;
- reviewer-claimed affected existing surfaces;
- reviewer-claimed regression/compatibility risks;
- reviewer-requested verification evidence;
- independent adjudication of the finding;
- independent impact assessment;
- decision on the proposed repair: `ADOPT`, `ADOPT_WITH_MODIFICATION`, `REJECT_FIX_ACCEPT_FINDING`, `REJECT_FINDING`, or `DEFER_INSUFFICIENT_EVIDENCE`;
- rationale and evidence.

A reviewer suggestion cannot disappear between review and implementation.

## RCIC-10 — Reviewer impact claims must be reconciled

Before a successor candidate is review-ready, every existing-system surface claimed by the reviewer must be reconciled by the `ChangeImpactManifest` as one of:

- directly changed;
- transitive change required;
- test/evidence-only change;
- explicitly no change required with evidence;
- reviewer impact claim rejected with rationale/evidence;
- unresolved/insufficient evidence.

Any unresolved material reviewer impact claim blocks re-review with `REVIEWER_IMPACT_CLAIM_UNRESOLVED`.

## RCIC-11 — Chosen remediation may differ from reviewer wording

The reviewer identifies defects, required properties, likely impacts and verification criteria. The implementation team/governor chooses the actual repair only after root-cause and impact analysis.

A different repair is acceptable only when it closes the same invariant/failure path, addresses all accepted material impacts, and satisfies or supersedes the reviewer's verification criteria without weakening existing guarantees.

## RCIC-12 — Successor evidence for re-review

Before the successor is sent for review, provide neutral evidence sufficient to inspect the actual result, including as applicable:

- exact successor candidate;
- exact baseline-to-successor diff;
- changed and transitively impacted code/contracts;
- updated schemas/state/migration material;
- targeted negative and positive tests;
- affected regression results;
- compatibility/rollback evidence;
- cleanliness/static-analysis evidence;
- preserved known failures/deferred cases.

For a clean independent review, this evidence is provided without seeding the reviewer with previous reviewer conclusions.

## RCIC-13 — Mandatory runtime enforcement

A governed review dispatcher/packet assembler must fail closed when the deliberate change-impact contract is absent or when required verification evidence is unavailable.

The reference runtime validator is `governance-runtime/review_change_impact_gate.py`.

## RCIC-14 — Mandatory future attacks

Tests/reviews must attack at least:

- review sent without explicitly asking whether changes are required;
- reviewer asked for changes without receiving current code/contract/test evidence;
- required evidence class silently omitted;
- reviewer recommendation accepted without independent impact analysis;
- reviewer-claimed affected surface omitted from the change-impact manifest;
- reviewer suggestion implemented literally despite breaking an existing interface;
- reviewer impact speculation treated as fact despite missing evidence;
- remediation-verification review mislabeled as clean independent review;
- clean review contaminated with prior reviewer conclusions;
- successor re-reviewed without exact diff and regression evidence.

## RCIC-15 — Nonclaims

This contract improves review sufficiency and remediation discipline. It does not make reviewer recommendations authoritative and does not prove that dependency/impact discovery is complete when the available repository/toolchain cannot establish it. Unknown material impact remains blocking rather than assumed safe.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
