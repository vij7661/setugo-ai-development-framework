# Review Finding Change-Control and Impact Gate — V1

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## RFCC-01 — Purpose

Independent-review findings are evidence, not executable change instructions. No reviewer suggestion may be applied directly to design/code merely because it was labeled Critical/High/Medium/Low.

Every accepted finding must pass deterministic adjudication, impact analysis, regression planning, implementation validation, and cleanliness checks before a successor candidate may be sent for another governed review.

## RFCC-02 — One review round, one complete finding set

For one exact candidate, collect and preserve the complete reviewer finding set before normal remediation begins. Do not create one successor per finding when findings can be adjudicated and repaired coherently together.

Critical emergency containment may occur earlier only to prevent an unsafe/invalid authority effect; it does not waive full finding adjudication or impact analysis.

## RFCC-03 — FindingDispositionRecord

Every reviewer finding receives one immutable `FindingDispositionRecord` binding:

- exact reviewed candidate commit;
- reviewer evidence identity;
- finding ID/severity/title;
- claimed failure path;
- affected invariant/contract;
- independent reproduction or reasoning result;
- root-cause class;
- disposition: `ACCEPT`, `PARTIAL_ACCEPT`, `REJECT`, `INSUFFICIENT_EVIDENCE`, or `PACKET_PROCESS_DEFECT`;
- rationale;
- whether design bytes, implementation bytes, tests/fixtures, packet/process, or documentation must change.

A reviewer-prescribed implementation is not automatically the selected fix.

## RFCC-04 — Root cause before patch

For accepted findings, remediation must address the violated invariant/root cause rather than only the example exploit.

If the same defect family appears in two consecutive successor reviews, another local symptom patch is prohibited. The next remediation must generalize the invariant/platform primitive and include adversarial coverage for sibling paths.

If review cycles continue without a new defect family, perform a process/meta-review before further version churn.

## RFCC-05 — Change-class separation

Classify the remediation before editing:

- `PACKET_PROCESS_DEFECT`: review packet/procedure only; same design candidate may remain valid if design bytes do not change.
- `DESIGN_DEFECT`: normative/design semantics change; creates a new exact design candidate.
- `IMPLEMENTATION_DEFECT`: runtime code changes while governing contract remains unchanged.
- `TEST_FIXTURE_DEFECT`: fixture/expectation/data repair only; production behavior must not be changed merely to make the test pass.
- `DOCUMENTATION_ONLY`: explanatory text only; must be proven non-authoritative/non-semantic under the active contract.
- `MIXED`: multiple classes; use the strictest applicable transition/review rule.

Historical findings/results are preserved and never rewritten into the successor result.

## RFCC-06 — Pre-change baseline snapshot

Before modifying an accepted design/code finding, record the exact baseline:

- base commit/tree;
- changed/affected subsystem boundaries;
- applicable normative controls/invariants;
- public/internal API contracts and schemas;
- persistence/event/ledger formats;
- configuration/policy identities;
- current unit/integration/regression/falsification status available for the affected area;
- known failures/deferred cases.

The successor cannot claim “no regression” without a comparable baseline.

## RFCC-07 — ChangeImpactManifest before implementation

Every accepted finding requiring design/code change must have a `ChangeImpactManifest` before the change is considered complete. It identifies at least:

1. directly changed files/components;
2. transitive callers/consumers/dependents;
3. authority/governance invariants affected;
4. APIs, schemas, events, ledgers, persistence and migrations;
5. provider/adapters/external effects;
6. configuration/secrets/policies;
7. caches/replicas/recovery/retry/idempotency paths;
8. tests, fixtures, mocks and generated artifacts;
9. dashboards/telemetry/audit/proof views;
10. backward/forward compatibility and rollout/rollback implications;
11. unchanged surfaces explicitly relied upon.

Unknown impact is blocking `CHANGE_IMPACT_INSUFFICIENT_EVIDENCE`, not assumed safe.

## RFCC-08 — No unaccounted diff

The actual base→successor diff must be reconciled against the approved impact/change manifest.

Every changed path is classified as:

- `INTENDED_REMEDIATION`;
- `REQUIRED_TRANSITIVE_CHANGE`;
- `TEST_OR_EVIDENCE_CHANGE`;
- `CLEANUP_WITH_PROVEN_NO_SEMANTIC_CHANGE`.

Any unclassified changed path fails the gate with `UNACCOUNTED_CHANGE`.

Likewise, every manifest-required direct/transitive change must be present or explicitly dispositioned `NO_CHANGE_REQUIRED` with rationale.

## RFCC-09 — Regression obligations

A successor affected by code/design change cannot be review-ready until:

- targeted tests for each accepted finding pass;
- regression tests for every impacted invariant/interface pass;
- previously passing load-bearing tests are rerun where the impact manifest says they are reachable;
- negative/adversarial tests prove the old failure path is closed;
- positive controls prove valid behavior was not overblocked;
- migrations/backward compatibility are tested when contracts/state changed;
- failures remain preserved rather than deleted/disabled to obtain green status.

A test may be removed/changed only with an explicit test-obligation disposition explaining why the prior expectation is obsolete or invalid.

## RFCC-10 — Clean-code and architecture preservation

Remediation must leave the implementation cleaner or no worse by requiring:

- one authoritative implementation path per invariant where feasible;
- no duplicate policy/business logic introduced merely to patch a review finding;
- stable domain/API contracts unless the accepted finding requires a governed contract change;
- presentation/UI separated from domain/governance/data logic;
- provider-specific behavior behind stable adapters/interfaces;
- configuration/data-driven values rather than scattered hard-coded exceptions;
- no test-only production branches to force PASS;
- no dead compatibility code without an explicit migration/removal plan;
- no swallowed errors, silent fallback or permissive default added by the repair;
- names/types/constants centralized and semantically consistent;
- comments/documentation updated only to match implemented behavior, never to paper over missing enforcement.

## RFCC-11 — Cleanliness checks are evidence, not style opinion

Where the repository/toolchain supports them, a changed implementation must run applicable formatter, linter/static analysis, type/compile checks, unit tests, integration/regression tests, and security/secret checks. A clean-code assertion without available tool evidence must be marked `NOT_VERIFIED` rather than PASS.

Existing unrelated failures may be preserved as bounded known failures, but a successor must not introduce new failures in previously green reachable surfaces.

## RFCC-12 — Compatibility and migration rule

When a remediation changes a schema/API/event/policy/ledger/state representation, it must choose and document exactly one strategy:

- backward-compatible additive evolution;
- versioned dual-read/write transition;
- explicit migration with rollback/reconciliation;
- intentional breaking change requiring governed generation/release transition.

Implicit breaking changes are prohibited.

## RFCC-13 — Re-review convergence rule

A new independent review is requested only after all accepted findings in the current round are adjudicated, the coherent successor change set is complete, impact/regression/cleanliness gates pass, and the exact successor candidate is frozen.

Do not repeatedly ask reviewers to inspect intermediate partial repairs.

Medium/Low findings should normally be batched with the current coherent repair unless they are explicitly deferred with non-authoritative/no-safety-impact rationale. Critical/High findings remain blocking.

A packet/process defect alone does not trigger a design version increment.

## RFCC-14 — Reviewer independence from remediation choice

The reviewer may identify a defect and suggest a narrow fix, but the implementation team/governor independently determines whether the suggestion is sufficient, overbroad, weakening, incompatible, or merely one possible repair.

The chosen remediation must prove the invariant, not prove obedience to reviewer wording.

## RFCC-15 — Successor readiness states

The change-control gate returns exactly one high-level state:

- `CHANGE_READY_FOR_REVIEW` — finding adjudication complete, change impact reconciled, required regression/cleanliness evidence satisfied;
- `CHANGE_NOT_READY` — missing/failed obligation;
- `NO_DESIGN_CHANGE_PACKET_REPAIR` — only packet/process defect corrected and exact design candidate unchanged.

These states are evidence only and cannot grant design/release authority.

## RFCC-16 — Mandatory future attacks

Tests/reviews must attack at least:

- blindly applying reviewer-prescribed code;
- fixing the example while leaving sibling/root-cause paths open;
- hidden changed file outside impact manifest;
- changed API/schema without migration/compatibility plan;
- deleting/fixing tests instead of fixing production behavior;
- adding provider/test-specific hard-coded branches;
- cleanup that silently changes authority semantics;
- re-reviewing a partial repair while other accepted findings remain unresolved;
- repeated same-family review failures without generalizing the invariant;
- claiming clean/no-regression without comparable baseline evidence.

## RFCC-17 — Nonclaims

This standard does not prove that every language/framework dependency graph can be derived automatically. Where static tooling cannot establish transitive reachability, the impact remains explicitly human/reviewer-assisted and must be marked with evidence/uncertainty rather than assumed complete.

No implementation/release authority follows from this document.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
