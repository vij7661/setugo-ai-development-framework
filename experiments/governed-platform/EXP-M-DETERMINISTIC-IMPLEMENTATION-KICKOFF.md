# EXP-M Deterministic Implementation Kickoff

Status: `AUTHORIZED_TO_BEGIN_DETERMINISTIC_IMPLEMENTATION_ONLY`

Branch:

`experiment/exp-m-deterministic-implementation`

Frozen design source:

`experiment/exp-m-review-evidence-delivery-integrity@0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`

Independent R5 design disposition:

`BOUNDED_PASS`

## Authority boundary

EXP-M remains `NOT_QUALIFIED`.

Allowed:

- deterministic implementation;
- deterministic fake/adversarial provider adapters;
- unit/integration tests;
- deterministic phases A-T;
- data/state mutation testing;
- validator-logic mutation testing;
- self-falsification;
- generation of an implementation-review packet.

Not allowed:

- live provider/API qualification;
- live Claude/DeepSeek/Gemini/OpenRouter capability pilots;
- promotion/release authority;
- modification of the frozen R5 design without a separately reviewed design delta;
- importing Ruflo-derived semantics as new load-bearing EXP-M predicates.

## Source of truth

Implement exactly against:

- `standards/review-evidence-delivery-integrity.md`
- `experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md`
- `experiments/governed-platform/EXP-M-TEST-MATRIX.md`
- `governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md`
- `experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md`

all from the frozen R5 source commit above.

## Required work loop

```text
INVENTORY
-> IMPLEMENT
-> TEST
-> FALSIFY
-> MUTATE
-> FIX
-> RETEST
-> RE-FALSIFY
-> CHECK GIT/REPO FOR NEXT INCOMPLETE TASK
-> CONTINUE
-> REPEAT
```

## No-stop continuation rule

Do not stop merely because the current subtask, test file, phase, or commit is complete.

Before stopping for any reason, classify the reason as one of:

- `MANUAL_INTERVENTION_REQUIRED`
- `EXTERNAL_REVIEW_REQUIRED`
- `DETERMINISTIC_EXIT_REACHED`
- `AUTOMATABLE_WORK_REMAINS`

If the reason is `AUTOMATABLE_WORK_REMAINS`, stopping is prohibited.

In that case, immediately inspect the repository/Git state and continue with the next highest-priority incomplete task.

Use this repository continuation procedure:

1. `git status --short --branch`
2. `git fetch origin`
3. verify the current branch is still:
   `experiment/exp-m-deterministic-implementation`
4. inspect current HEAD and recent commits;
5. compare local branch with `origin/experiment/exp-m-deterministic-implementation`;
6. inspect this kickoff file and the frozen EXP-M R5 source-of-truth files;
7. inspect the EXP-M A-T test matrix and determine the first incomplete/failing deterministic phase;
8. inspect failing tests, mutation survivors, predicate-closure gaps, TODO/FIXME markers created by this implementation, and generated evidence status;
9. select the next task using the priority order below;
10. continue implementation automatically.

Next-task priority:

1. current failing production-path test;
2. surviving validator-logic mutation;
3. surviving data/state mutation;
4. incomplete admissibility-predicate closure;
5. incomplete deterministic A-T phase in order;
6. missing required production-path implementation used by the next phase;
7. missing generated evidence required by deterministic exit;
8. self-falsification finding;
9. repository hygiene needed to make the current EXP-M branch reproducible;
10. only after all above are complete, prepare the independent deterministic-review packet.

Do not switch to unrelated branches or begin unrelated project work merely because EXP-M has no immediate failing test.

Do not treat:
- a green single test file,
- a successful commit,
- one completed deterministic phase,
- zero failures in the current command,
- lack of TODOs in one file,
- or temporary absence of a next prompt

as permission to stop.

If GitHub/repository inspection shows more automatable EXP-M work, continue.

If local state is behind the remote branch and the remote changes belong to this EXP-M implementation work, reconcile safely before continuing. Never overwrite uncommitted work. Never reset away evidence or first-failure history.

Do not create new manual-review requirements merely to stop. Manual intervention is genuine only when the next required action cannot be completed safely or authoritatively by Codex, such as:

- independent external review;
- user approval explicitly required by governance;
- unavailable secret/credential that the user must supply;
- unavailable exact host/device/environment required by the frozen experiment;
- a destructive or external side effect that is not already authorized;
- an unresolved policy choice that the frozen design does not decide.

Ordinary coding decisions, test repair, fixture generation, deterministic fake-provider work, refactoring needed to satisfy the frozen design, Git inspection, committing/pushing current branch work, and proceeding to the next A-T phase are **not** manual intervention.

Do not stop for ordinary coding/test failures.

Stop only when:

1. genuine manual intervention/external review is required; or
2. every deterministic exit criterion below is satisfied.

## Minimum implementation surfaces

Implement production-path equivalents for:

- GovernanceAuthoritySnapshot
- RequiredEvidenceContract
- RequiredInteractionContract
- EvidenceDeliveryManifest
- ProviderCapabilityProfile
- ProviderQualificationExecutionPlan
- ProviderCapabilityQualificationRecord
- ProviderAccessibilityRiskPolicy
- ProviderContextIsolationPolicy
- ProviderContextStateEvidence
- AdmissionFenceRecord
- PromptIsolationQualificationRecord
- WitnessProtocolQualificationRecord
- DeliveryPreflightResult
- WireDeliveryRecord
- EvidenceChunk
- ReviewerReceipt
- DeliveryCompletenessResult
- InsufficientEvidenceAdjudication
- AdmissibilityPredicateRegistry
- VerdictAdmissibilityResult

Reuse existing governed project primitives where semantics match. Do not create a parallel framework merely for EXP-M.

## Deterministic provider model

No live external provider APIs.

Use deterministic fake/adversarial adapters for:

- clean context
- dirty context
- lying readback
- hidden semantic state
- context/config drift
- post-SDK semantic mutation
- hidden/replayed retry
- content truncation
- canary-preserving content loss
- witness-induced context eviction
- wrong/missing retrieval range
- retrieval from wrong session
- stale qualification
- attempt cherry-picking
- admission-time races.

## Test gate

All deterministic phases A-T from the frozen test matrix are mandatory.

Tests must exercise real production validators/governors, not summary booleans.

## Mutation gate

Maintain two separate families:

1. data/state mutations;
2. validator-logic mutations.

Every material authority predicate must have a targeted validator-logic mutation.

Require exact closure:

```text
required predicate IDs
==
VerdictAdmissibilityResult predicate IDs
==
logic mutation target IDs
==
independently killed mutation IDs
```

All material false-green mutations must be killed.

## Deterministic exit criteria

Do not declare completion until all are true:

- deterministic A-T phases pass;
- unit/integration suite passes;
- zero surviving data/state mutations;
- zero surviving validator-logic mutations;
- exact admissibility predicate closure passes;
- authority-snapshot poisoning tests pass;
- qualification-attempt closure passes;
- retry transparency passes;
- provider-context isolation/fence tests pass;
- witness context-budget/structural-isolation tests pass;
- retrieval final-context tests pass;
- atomic admission race tests pass;
- taxonomy/cause tests pass;
- self-falsification finds zero unresolved Critical implementation defects;
- self-falsification finds zero unresolved High implementation defects.

## Final output

When deterministic exit is reached:

1. freeze exact source commit/tree;
2. freeze exact machine evidence;
3. generate a self-contained independent implementation/falsification review packet;
4. preserve first-failure history;
5. preserve test/mutation generated counts;
6. return `DETERMINISTIC_REVIEW_REQUIRED`;
7. keep live provider pilots blocked.

Do not start any live provider experiment automatically.
