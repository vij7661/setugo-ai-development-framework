# Workflow Drift and Parent-Child Impact Control — V19 Deterministic Reconciliation and Enforcement Attestation

Status: **PROPOSED V19 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V19-C01 — Exact base and additive precedence

V19 is additive over exact V18 candidate `290ac043959f30db12c9ae16826eda1dd5bcbdfb`.

All active V5–V18 controls remain in force except where V19 explicitly narrows a V18 ambiguity in the stricter fail-closed direction. V19 does not grant execution freeze, implementation qualification, merge, release, deployment, or terminal authority.

## V19-C02 — Authority-bearing audit/publication state is mandatory atomic state

For any qualification-to-threshold decision, every durable state element capable of presenting or authorizing an externally observable governance outcome is part of the mandatory atomic bound set. Policy may add bound state but may not remove authority-bearing audit/event publication, decision-publication, threshold-consumption, uniqueness, lineage, sequence, or authoritative status state from that set.

A commit is valid only when all mandatory bound elements share one committed transaction/consensus decision identity and exact candidate/idempotency binding. A partial commit or publication that can expose a false authoritative view is invalid and must not authorize progress.

Failure endpoint: `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION`.

## V19-C03 — Deterministic `OUTCOME_UNKNOWN` reconciliation state machine

`REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN` is a non-authorizing reconciliation state, not a rollback assumption.

Reconciliation must bind and evaluate at minimum:

- exact candidate/gate identity;
- one intent-level idempotency key;
- authoritative transaction/consensus decision identifier where present;
- `ReviewThresholdConsumptionLedger` lookup by the exact intent/candidate/gate tuple;
- `ReviewThresholdRecord` and uniqueness state;
- predecessor/commit digest and authoritative sequence;
- current witness/anchor state when witness evidence is required;
- audit/publication commit identity.

Permitted terminal reconciliation outcomes are:

1. `COMMIT_CONFIRMED_EXISTING` — exactly one complete authoritative commit exists; return that result and do not count again;
2. `NO_COMMIT_CONFIRMED` — authoritative durable state proves no commit exists; one retry using the same intent-level idempotency key may proceed;
3. `RECONCILIATION_CONFLICT` — contradictory/forked state is present; block;
4. `INSUFFICIENT_EVIDENCE` — current durable/witness evidence cannot distinguish commit from non-commit; block.

Lost acknowledgement alone can never produce `NO_COMMIT_CONFIRMED`. Reconciliation may not create a second count or infer rollback from transport failure.

## V19-C04 — Root-threshold anti-weakening invariant

For root-governed threshold/packet ledgers and their policy registries, any policy rotation, reset, repair, migration, compaction, emergency path, or authority change that can affect mutation requirements must be authorized under a threshold no weaker than the mutation threshold in force immediately before that change.

A policy rotation may strengthen the threshold prospectively. It may not lower the threshold and then use the lowered threshold to mutate, reset, repair, replace, rebase, fork, truncate, or migrate governed ledgers or their uniqueness/lineage rules.

The anti-weakening comparison binds the old policy version/digest, proposed policy version/digest, old threshold rule, proposed threshold rule, approving principal set, effective sequence, and exact governed object class.

Failure endpoint: `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`.

## V19-C05 — Authoritative sequence immutability / anti-remapping

An authoritative consumption sequence is immutable once committed. No policy backdating, sequence remapping, ledger rebasing, compaction numbering change, migration transform, or alternate sequence namespace may move an older consumption event to or beyond a later reuse policy's `effective_from_sequence`.

Reuse eligibility compares the original immutable authoritative consumption sequence and the reuse rule's original authoritative activation sequence in the same governed sequence domain.

Failure endpoint: `REVIEW_THRESHOLD_SEQUENCE_REMAP_REJECTED`.

## V19-C06 — Mechanical dependency-index completeness proof

Every governed corpus/algorithm generation must bind a mechanically enumerable universe of decision classes and concrete decision identities that are dependency-eligible for that generation.

Before a corpus/algorithm change can complete revalidation, the platform must compute and retain:

- `eligible_dependency_set`;
- `indexed_dependency_set`;
- `revalidated_or_exempt_set`;
- set difference `eligible_dependency_set - indexed_dependency_set`;
- set difference `indexed_dependency_set - revalidated_or_exempt_set`.

Any non-empty difference is fail-closed. Omitted dependents become `REVALIDATION_REQUIRED` or `INSUFFICIENT_EVIDENCE`; they may not silently retain `PARENT_UNAFFECTED`, canonical-equivalence, re-expression, review-projection, or qualification status.

Failure endpoint: `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE`.

## V19-C07 — Governed independent-support exemption

An exemption from corpus-dependent revalidation is permitted only through a root-governed `IndependentSupportRegistry` record bound to:

- exact dependent decision identity/digest;
- exact corpus/algorithm generation being superseded and the new generation;
- exact support evidence identities and evidence classes;
- the independence policy/version and required independence threshold;
- supporting principal/provider/source domains;
- forbidden relationships and conflict/self-support predicates;
- expiry/staleness state;
- approving governed authority and effective sequence.

The candidate author, beneficiary, same evidence producer, same unverified provider relationship, or any party forbidden by the active independence policy cannot self-prove the exemption. Missing, stale, conflicting, or self-supporting evidence is not an exemption.

Failure endpoint: `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`.

## V19-C08 — Witness authority independence and currentness

Where a witness/anchor is required to prove non-replacement, its authority must be independent from the governed ledger/root operator across the policy-defined control, administration, credential, recovery, and mutation domains.

The witness binding records exact witness identity, governance domain, control/admin/recovery domains, credential authority, current checkpoint/sequence/digest, observed ledger lineage, currentness window, and independence-policy version.

A witness controlled by, recoverable by, or jointly administered below the required independence threshold with the ledger/root operator is non-qualifying.

A lagging or unavailable witness is `INSUFFICIENT_EVIDENCE`, not current. When the witness later becomes current, governed recovery may resume only after the current checkpoint proves continuity from the last accepted witnessed state through the present lineage.

Failure endpoint: `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`.

## V19-C09 — Migration/compaction under witness unavailability

Physical compaction/migration may prepare data while required witness evidence is unavailable, but the migrated representation cannot become qualification-authoritative until witness continuity/currentness is re-established against the complete logical lineage and the governed migration identity.

No local success, root-operator assertion, or store-local hash chain substitutes for a required current witness.

## V19-C10 — Proof-view requirements

Reviewer-safe proof/evidence views expose, as applicable:

- mandatory atomic-bound-set membership, including authority-bearing audit/publication state;
- `OUTCOME_UNKNOWN` reconciliation state, exact idempotency binding, ledger lookup result, and terminal reconciliation outcome;
- root-policy old/new threshold comparison and anti-weakening result;
- immutable authoritative sequence-domain identity and anti-remapping result;
- dependency eligible/indexed/revalidated-or-exempt sets and both set differences;
- independent-support registry record, evidence-class binding, independence threshold, conflict/self-support result;
- witness authority/control/admin/recovery-domain independence result;
- witness lag/currentness and recovery-continuity result;
- migration/compaction authority status while witness evidence is unavailable.

Missing mandatory proof values are `NOT_PRESENT` or `INSUFFICIENT_EVIDENCE`, never implicit PASS.

## V19-C11 — Enforcement execution attestation

A control being configured or declared does not prove that it executed for a governed action. Material transitions must distinguish at minimum:

- `CONTROL_CONFIGURED`;
- `CONTROL_EXECUTED`;
- `CONTROL_VERIFIED`;
- `CONTROL_FAILED`;
- `CONTROL_UNKNOWN`.

When policy requires a control, only exact action/candidate-bound evidence satisfying the required execution/verification state may authorize the dependent transition. Missing, stale, mismatched, failed, or unknown execution evidence blocks.

## V19-C12 — Declared-vs-executable enforcement equivalence

A governance document, skill, policy, hook declaration, or control description may not claim stronger enforcement semantics than the executable mechanism actually provides.

For each authority-bearing control, the governed equivalence record binds the declared mode, fail-open/fail-closed behavior, error behavior, scope, candidate binding, runtime path(s), version/digest, and machine-verification evidence. A declared blocking/unskippable control backed by a fail-open, missing, optional, instruction-only, or bypassable execution path is non-equivalent and non-authorizing.

## V19-C13 — Qualified harness capability envelope

Every governed harness/runtime binding uses an exact, versioned capability envelope. Capability classes include at minimum `NATIVE_ENFORCEMENT`, `ADAPTER_ENFORCEMENT`, `INSTRUCTION_ONLY`, `REFERENCE_ONLY`, and `UNSUPPORTED`.

Role assignment remains provider/model-neutral: R1/R2/R3 are governed roles, not hardcoded providers or model names. A selected model/provider/harness may occupy a role only if the exact binding satisfies the role's required capability envelope. Model/provider/harness/version/config changes make the affected binding stale and require governed revalidation/restart as policy requires.

Installation, naming similarity, or successful invocation does not prove equivalent enforcement.

## V19-C14 — Capability / power-surface activation consent

Possession of a capability does not authorize activation. Authority-bearing power surfaces—including repository/source mutation, subprocess/process control, external transcript/model egress, MCP/tool execution, durable persistence, credential use, external side effects, and equivalent future capabilities—require a separate governed activation record bound to exact project/workflow, role, resource scope, powers, approver authority, sequence/expiry, and capability/harness identity.

Activation outside the approved powers/resources/scope or after expiry is rejected. Capability widening requires a new governed activation decision.

## V19-C15 — Cross-harness tool/MCP configuration attestation and drift

Tool/MCP configuration qualification binds a canonical secret-safe configuration identity including exact harness/tool identity, transport, resolved endpoint where applicable, command/argv, permission profile, credential-profile fingerprint/attestation, configuration digest, and runtime/harness version.

Friendly names are not identity. Configuration drift, endpoint rebinding, permission widening, credential-profile change, argv change, harness/runtime change, or canonical-digest mismatch makes dependent qualification stale until governed revalidation.

Secrets must not be exposed merely to compute or display the canonical inventory.

## V19-C16 — Deferred ECC boundaries remain deferred

External-review egress/provider-relationship qualification and learned-artifact promotion/retraction governance are not promoted by V19. They remain separate deferred boundaries pending their required live/integration evidence.

No deterministic reference mechanism may be represented as live provider/manual-review integration, production trust-root evidence, or a live learned-artifact promotion pipeline.

## V19-C17 — New endpoints

- `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION`
- `RECONCILIATION_CONFLICT`
- `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`
- `REVIEW_THRESHOLD_SEQUENCE_REMAP_REJECTED`
- `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE`
- `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`
- `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`
- `CONTROL_EXECUTION_EVIDENCE_REQUIRED`
- `DECLARED_EXECUTABLE_ENFORCEMENT_MISMATCH`
- `HARNESS_CAPABILITY_ENVELOPE_STALE_OR_INSUFFICIENT`
- `CAPABILITY_ACTIVATION_NOT_AUTHORIZED`
- `TOOL_CONFIGURATION_ATTESTATION_STALE_OR_MISMATCHED`

## V19-C18 — Freeze rule

V19 is a design successor only. It requires its own clean design review and subsequent implementation/falsification evidence under the active policy. Earlier V18 or ECC review results do not qualify V19 and must not be counted as V19 review evidence.

Manual-review and live-attestation requirements remain unchanged. `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`.
