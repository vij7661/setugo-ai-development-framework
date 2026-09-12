# Platform Root & Meta-Governance Closure Standard

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: terminate governance-of-governance recursion at an explicit, reviewable trust boundary and make the resulting controls reusable across every governed platform subsystem, experiment family, review, testing workflow, implementation gate, release gate, and future authority-bearing feature.

This standard is platform-wide. It is not specific to WDPC, EXP-J, EXP-K, ECC, or any particular provider/model.

## PGR-01 — Scope and mandatory inheritance

Any component, policy, registry, reviewer/evaluator selector, evidence qualifier, attestor, witness, release gate, testing gate, research/evidence gate, implementation gate, or workflow that can create, mutate, interpret, qualify, suppress, publish, or consume authority-bearing state is in scope.

A future subsystem cannot opt out by renaming, reclassification, namespace change, wrapper creation, storage migration, new schema, or creation of a new authority-bearing object class.

If a subsystem can materially alter whether an action or evidence is treated as authoritative, that subsystem is inside the platform governance surface.

## PGR-02 — Explicit terminal trust boundary

Governance recursion terminates at an explicit `RootGovernanceKernel` for one `governance_generation_id`.

The kernel is the declared trusted computing/governance base for that generation. It is not self-proved by a lower layer and must never be described as eliminating all external trust assumptions.

Each generation has one immutable `GovernanceGenerationGenesisRecord` binding at minimum:

- `governance_generation_id`;
- root-kernel specification/version/digest;
- root-kernel executable/verifier identity and digest where applicable;
- genesis/bootstrap authority identities and threshold;
- bootstrap public-key/credential identities;
- bootstrap ceremony/evidence digest;
- independent witness/attestation identities required by the bootstrap policy;
- predecessor generation identity/digest, or explicit `GENESIS_NO_PREDECESSOR`;
- activation sequence/time;
- allowed migration policy identity/version;
- exact residual trust assumptions.

A missing or unreviewable genesis binding is `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE`.

## PGR-03 — Root kernel is immutable within a governance generation

Within one `governance_generation_id`, no governed actor, root-threshold set, local administrator, recovery actor, emergency actor, implementation under test, reviewer, evaluator, model, or policy transition may modify, replace, reinterpret, weaken, or bypass the active `RootGovernanceKernel`.

This includes indirect change through aliases, wrappers, changed parsers, changed comparison semantics, alternate registries, version remapping, storage migration, or executable substitution.

Any attempt to change the kernel in-place is rejected before activation with:

`ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`.

## PGR-04 — Constitutional invariant set

The root kernel contains a finite `ConstitutionalInvariantSet` whose semantics are fixed for the generation. At minimum it enforces:

1. governed identity/ancestry cannot be discarded to escape inherited obligations;
2. an effective mutation/approval threshold cannot become weaker inside the same governed lineage;
3. required independence cannot be reduced;
4. required quorum/domain diversity cannot be reduced;
5. forbidden relationships cannot silently become qualifying;
6. accepted issuer/evaluator/source classes cannot be broadened if doing so weakens prior restrictions;
7. currentness, expiry, revocation, compromise, replay, and continuity requirements cannot be weakened;
8. previously authorized scope cannot be retroactively broadened by later interpretation/schema changes;
9. secret-protection/non-reversibility guarantees cannot be weakened;
10. evidence required for authority cannot be replaced by assertion, model agreement, reviewer agreement, label, or transport success;
11. no authority-bearing object may authorize, qualify, validate, mutate, or weaken an ancestor from which its own authority derives;
12. the mechanism that decides whether a change is weaker cannot redefine weakening inside the same governance generation;
13. missing mandatory evidence fails closed and cannot be converted to PASS/authorized state by fallback policy;
14. a change to this invariant set is a governance-generation transition, not an ordinary policy amendment.

## PGR-05 — Strength contracts are constitutional, not ordinary mutable policy

Every authority-bearing policy class must have a `StrengthContract` that normalizes the dimensions used to determine equal/stronger/weaker transitions.

The contract binds:

- policy class identity;
- governed dimensions;
- ordering/partial-order rule for each dimension;
- forbidden transitions;
- equality semantics;
- treatment of unknown/missing dimensions;
- schema/version;
- kernel generation and digest.

A `StrengthContract` is kernel-bound and immutable inside the generation. An ordinary root-policy vote cannot redefine the comparison so that a previously weaker transition becomes equal or stronger.

Attempted in-generation strength-contract mutation or alternate comparison path returns:

`ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED`.

Unknown or incomparable material transitions fail closed as `INSUFFICIENT_EVIDENCE` unless the active constitutional contract explicitly defines the safe outcome.

## PGR-06 — Transitive authority-surface closure

Protection is determined by function, not by an enumerated name list.

Define `AuthoritySurfaceClosure` as the transitive closure of every object or policy that can materially affect:

- who may grant/mutate authority;
- how authority evidence is qualified;
- how identity/lineage is determined;
- how policy strength is compared;
- how conflicts are resolved;
- how reviewers/evaluators/attestors/witnesses/sources are selected or qualified;
- how publication classes are classified;
- how dependency universes are derived;
- how activation/scope is interpreted;
- how release/testing/implementation status is promoted;
- how evidence is made visible or hidden from a consuming decision.

Every member of `AuthoritySurfaceClosure` automatically becomes a governed object subject to immutable identity, ancestry, threshold floor, applicable `StrengthContract`, proof-view exposure, and root-kernel checks.

Failure to classify a material authority-affecting object into the closure is not permission to operate; it is `AUTHORITY_SURFACE_CLASSIFICATION_INCOMPLETE`.

This rule prevents future designs from escaping protection merely because a new meta-policy was omitted from a manually maintained list.

## PGR-07 — Authority dependency graph must be acyclic

The platform must maintain an exact `AuthorityDependencyGraph` for the active governance generation.

For every authority-bearing node, the graph binds:

- immutable governed object identity;
- authority parent(s);
- mutation authority;
- qualification authority;
- evidence authority;
- recovery/emergency authority;
- beneficiary/controller relationships;
- effective sequence/version.

Activation requires deterministic proof that the graph is acyclic after collapsing explicitly declared non-authoritative replica/transport edges.

No node may authorize, qualify, validate, mutate, or weaken an ancestor in its authority derivation path. No cycle may be resolved by majority vote, model agreement, implementation preference, or local override.

Detected cycle/self-parent/ancestor-control path returns:

`AUTHORITY_DEPENDENCY_CYCLE_REJECTED`.

Missing complete graph evidence returns `INSUFFICIENT_EVIDENCE`.

## PGR-08 — Anti-self-grant and beneficiary-control rule

No candidate, beneficiary, implementation under test, evidence producer, reviewer subject, dependent decision author, or sub-threshold related principal set may self-select or control the authority that qualifies its own evidence, review, exception, reconciliation, exemption, release, or promotion.

Control includes direct ownership plus administration, credential, recovery, mutation, deployment, configuration, and effective operational control.

Where a root-threshold-capable combination overlaps a supposedly independent authority, the overlap must be explicitly represented in proof views and either prohibited by the active independence contract or declared as a residual root trust assumption. It may not be silently treated as independent.

## PGR-09 — Governed identity and anti-reclassification

Every object in `AuthoritySurfaceClosure` has one immutable `governed_object_id`, lineage, aliases, physical/logical store identities, class/schema identity, threshold floor, and split/merge ancestry.

Rename, alias, split, merge, storage migration, wrapper creation, namespace change, parser change, or class relabeling cannot create a fresh governance identity to erase prior restrictions.

Descendants inherit no-weaker authority floors from authority-bearing ancestors. Merged objects inherit no weaker than the strongest applicable ancestor obligation.

## PGR-10 — Authority-bearing decisions require bound records

A material authority decision cannot exist only as an in-memory return value, model statement, reviewer prose, log label, UI state, or caller assertion.

The qualifying decision record must be immutable and exact-bound to, as applicable:

- decision identity and schema/version;
- exact candidate/workflow/gate/action/intent tuple;
- governing policy/kernel generation and digests;
- evaluator/reviewer/attestor identity and implementation/version;
- source evidence identities/classes/digests;
- authentication/signature/attestation proofs where required;
- branch/predicate outcomes;
- sequence/time/currentness;
- expiry/revocation state;
- predecessor/lineage;
- final endpoint/result.

Authority-bearing evidence from a valid cryptographic signer that is revoked, expired, non-qualifying, wrong-class, wrong-generation, wrong-tuple, or wrong-policy-bound is invalid even when the signature itself verifies.

## PGR-11 — Reviewer/evaluator independence and output integrity

Independent review/evaluation must prove both selector independence and decision-record integrity.

The requester/candidate/beneficiary cannot select or qualify its own independent reviewer/evaluator except through a pre-governed selector whose own policy is in `AuthoritySurfaceClosure`.

Where the workflow requires a signed/attested output, the output must bind the exact packet/candidate/evidence digests and reviewer/evaluator identity. A pasted or paraphrased result is evidence only unless the governing workflow explicitly qualifies it.

## PGR-12 — Root-kernel change requires a new governance generation

A legitimate change to the root kernel, constitutional invariant set, or strength-contract semantics requires creation of a new `governance_generation_id` and a new `GovernanceGenerationGenesisRecord`.

The new generation must not inherit authority automatically. Migration requires an explicit governed `GenerationMigrationRecord` binding:

- predecessor generation/digest;
- successor generation/digest;
- exact objects/authority being migrated;
- migration policy/version;
- required approvals/witnesses;
- unresolved conflicts/exceptions;
- activation boundary;
- rollback/non-rollback semantics.

An old-generation object cannot be reinterpreted under a new kernel merely because the successor generation exists.

A generation transition that claims continuity without a qualifying genesis/migration record is `GOVERNANCE_GENERATION_TRANSITION_INVALID`.

## PGR-13 — Platform enforcement and review enforcement are both required

A review checklist alone does not satisfy this standard. The platform architecture must provide enforceable states/interfaces for the relevant controls before production qualification can be claimed.

Likewise, runtime enforcement alone does not eliminate the need for clean independent review. Every future design/review packet covering an authority-bearing surface must include a root/meta-governance closure review against this standard.

## PGR-14 — Mandatory root/meta-governance proof view

Reviewer-safe proof views must expose, where applicable:

- governance generation and genesis digest;
- root-kernel version/digest and executable/verifier identity;
- constitutional invariant set digest;
- applicable strength-contract identity/digest;
- governed object identity/ancestry/threshold floor;
- authority-surface classification result;
- authority graph parents and acyclicity result;
- selector/beneficiary/control-domain independence result;
- exact decision-record identity/digest;
- source qualification/authentication/currentness result;
- any root-threshold overlap/residual trust assumption;
- generation migration identity/status if applicable.

Missing mandatory root/meta-governance proof is `INSUFFICIENT_EVIDENCE`, never implicit PASS.

## PGR-15 — Platform-wide failure endpoints

At minimum:

- `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE`
- `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`
- `ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED`
- `AUTHORITY_SURFACE_CLASSIFICATION_INCOMPLETE`
- `AUTHORITY_DEPENDENCY_CYCLE_REJECTED`
- `GOVERNANCE_GENERATION_TRANSITION_INVALID`

Subsystem-specific stricter endpoints remain active and may take precedence where explicitly defined.

## PGR-16 — Mandatory future review attack

Every clean independent review of an authority-bearing design must explicitly attempt to falsify all of the following before recommending freeze/qualification:

1. root bootstrap/genesis ambiguity;
2. root-kernel in-place self-amendment;
3. strength-predicate/strength-contract mutation;
4. omission of a new authority-affecting policy from governance protection;
5. authority dependency cycles and ancestor mutation;
6. self-selection/self-qualification by candidate, beneficiary, requester, implementation, or reviewer subject;
7. rename/reclassification/split/merge identity escape;
8. evidence that is cryptographically valid but non-qualifying, revoked, expired, wrong-class, wrong-generation, or wrong-bound;
9. unsigned/unbound authority-bearing decision outputs;
10. conflict-resolution policy weakening;
11. scope/policy reinterpretation that retroactively broadens existing authority;
12. emergency/recovery/migration/reset path weakening;
13. proof-view omission that could conceal any of the above.

A reviewer must report `INSUFFICIENT_EVIDENCE` rather than assume a missing root/meta-governance property.

## PGR-17 — Future applicability

If this standard is later approved/adopted, it is intended to be inherited by all subsequent governed-platform designs and review packets unless an exact successor standard explicitly supersedes it with equal-or-stronger protections.

No subsystem-specific review result can waive these platform-level protections.

## PGR-18 — Nonclaims and freeze rule

This document is a design proposal. It does not prove that a production trust root, external bootstrap ceremony, independent witness infrastructure, signing infrastructure, or runtime enforcement exists.

It grants no implementation qualification, execution freeze, merge, release, deployment, adjudication, production authority, or terminal authority.

Before platform-wide adoption, this standard itself requires clean independent review with explicit instruction to attack its terminal trust boundary and determine whether any unacknowledged self-grant, self-amendment, mutable-strength, authority-cycle, or root-bootstrap path remains.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
