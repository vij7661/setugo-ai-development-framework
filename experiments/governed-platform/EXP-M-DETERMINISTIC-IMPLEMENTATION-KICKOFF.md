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
-> REPEAT
```

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
