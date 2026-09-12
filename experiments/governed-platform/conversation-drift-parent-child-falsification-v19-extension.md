# Workflow Drift & Parent-Child Impact Falsification Matrix — V19 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V19`

V19 inherits WDPC-01…282. It narrows the expected evidence contracts for WDPC-273, WDPC-276, and WDPC-277 and adds WDPC-283…308.

No V19 case is executed by this document. Expected outcomes are frozen before implementation testing begins.

## Narrowed inherited cases

### WDPC-273 — Crash inside atomic threshold commit / deterministic reconciliation

In addition to V18 expectations, `REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN` must enter the V19 deterministic reconciliation state machine. Recovery binds the original intent-level idempotency key, exact candidate/gate, authoritative durable threshold/consumption records, lineage/sequence, required witness currentness, and audit/publication commit identity.

Expected: exactly one of `COMMIT_CONFIRMED_EXISTING`, `NO_COMMIT_CONFIRMED`, `RECONCILIATION_CONFLICT`, or `INSUFFICIENT_EVIDENCE`; acknowledgement loss alone cannot imply rollback; no duplicate count.

### WDPC-276 — Corpus change dependency completeness / governed exemption

In addition to V18 expectations, revalidation requires a mechanical comparison of eligible, indexed, and revalidated-or-governedly-exempt decision sets. Independent-support exemptions require the exact governed registry/evidence/independence binding defined by V19.

Expected: any omitted eligible dependency or ungoverned/self-support exemption blocks with `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE`, `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`, `REVALIDATION_REQUIRED`, or `INSUFFICIENT_EVIDENCE` as applicable.

### WDPC-277 — Threshold-ledger rollback/fork / witness independence

In addition to V18 expectations, any required witness must satisfy the V19 control/admin/recovery-domain independence and currentness rules.

Expected: a non-independent, lagging, unavailable, or stale required witness cannot qualify lineage; no local/root assertion substitutes for required witness evidence.

## New negative falsification cases

### WDPC-283 — Audit/event publication excluded from atomic bound set

Fault: policy declares an authority-bearing audit/decision publication state outside the atomic threshold transaction; a crash occurs after threshold state commits but before publication or vice versa.

Expected: `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION`; no partial state may authorize or present a false authoritative decision.

### WDPC-284 — Root-policy rotation lowers mutation threshold

Fault: current root mutation threshold is T; a policy rotation authorized under T lowers the future ledger mutation threshold below T and the weaker set then mutates/reset/repairs/migrates a governed ledger.

Expected: `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`; governed ledgers and policy registries remain unchanged.

### WDPC-285 — Dependency index omits eligible dependent

Fault: a corpus/algorithm generation changes while one eligible `PARENT_UNAFFECTED`, canonical-equivalence, re-expression, review-projection, or qualification decision is omitted from the dependency index.

Expected: non-empty eligible-minus-indexed set; `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE`; omitted decision becomes `REVALIDATION_REQUIRED` or `INSUFFICIENT_EVIDENCE`.

### WDPC-286 — Independent-support exemption self-granted

Fault: an affected decision is declared independently supported using evidence from the candidate author, beneficiary, same evidence producer, same unverified provider relationship, or evidence lacking the governed registry/independence threshold binding.

Expected: `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`; revalidation remains required.

### WDPC-287 — Witness shares authority domain with ledger/root operator

Fault: witness control, administration, credential authority, or recovery authority overlaps the ledger/root operator below the required independence threshold.

Expected: `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID` or `INSUFFICIENT_EVIDENCE`; threshold count cannot rely on that witness.

### WDPC-288 — Witness unavailable or lagging treated as current

Fault: required witness has no current checkpoint or is behind the authoritative ledger lineage while qualification attempts to treat it as current.

Expected: `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID` or `INSUFFICIENT_EVIDENCE`; no qualification.

### WDPC-289 — Sequence remapping/backdating bypass

Fault: migration, compaction, rebasing, alternate sequence namespace, or policy backdating attempts to move an old consumption event after a later reuse policy's `effective_from_sequence`.

Expected: `REVIEW_THRESHOLD_SEQUENCE_REMAP_REJECTED`; original immutable consumption sequence governs reuse.

### WDPC-290 — Migration/compaction becomes authoritative while witness unavailable

Fault: physical migration/compaction completes while a required witness is unavailable/lagging and the new representation is marked qualification-authoritative anyway.

Expected: blocked as `INSUFFICIENT_EVIDENCE` or `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID` until current witness continuity is re-established.

### WDPC-291 — `OUTCOME_UNKNOWN` reconciliation duplicates count or infers false rollback

Fault: acknowledgement is lost after a possible commit; recovery either retries with a new idempotency key, creates another count, or assumes no commit from transport failure alone.

Expected: fail closed; duplicate count impossible; outcome remains unknown/conflict until authoritative durable evidence proves one terminal reconciliation outcome.

### WDPC-292 — Ledger reset/repair uses weaker threshold than normal mutation

Fault: a reset, emergency repair, migration, or recovery path applies a threshold weaker than the threshold required for ordinary mutation of the same governed ledger/policy class.

Expected: `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED` or `ROOT_GOVERNED_LEDGER_MUTATION_REJECTED`.

## Positive controls for V18-remediation rules

### WDPC-293 — Atomic audit/publication positive control

Positive control: threshold state, uniqueness/consumption state, authoritative sequence/lineage, and authority-bearing audit/publication state commit under one decision identity and recovery observes the complete commit.

Expected: original committed decision is returned exactly once; no false atomic-bound violation.

### WDPC-294 — Same-or-stronger root rotation positive control

Positive control: root policy rotation is authorized under the current threshold and retains or strengthens the mutation threshold before a legitimate governed ledger migration.

Expected: rotation/migration may proceed when every exact policy/object/lineage predicate passes.

### WDPC-295 — Complete dependency-index audit positive control

Positive control: eligible dependency set equals indexed dependency set and every indexed decision is either revalidated or covered by a valid governed exemption.

Expected: both V19 set differences are empty and downstream decisions may regain current status.

### WDPC-296 — Valid independent-support exemption positive control

Positive control: exact decision/evidence/generation identities are registered under the active independent-support policy, required independent domains satisfy threshold, no forbidden/self-support relation exists, and evidence is current.

Expected: the specific dependent may be proven unaffected without false `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`.

### WDPC-297 — Witness lag recovery positive control

Positive control: qualification blocks while witness is lagging; witness later publishes a current checkpoint proving continuity from the last accepted state through the present lineage.

Expected: earlier blocked attempt stays blocked in history; subsequent governed attempt may proceed after currentness/continuity verifies.

### WDPC-298 — Immutable sequence / prospective reuse positive control

Positive control: original consumption sequence remains unchanged through migration/compaction; a reuse rule activated before the destination consumption event satisfies all scope/evidence predicates.

Expected: legitimate prospective reuse count without sequence-remap rejection or duplicate count.

## ECC-derived bounded requirement-candidate cases

### WDPC-299 — Configured control falsely treated as executed

Fault: a required hook/gate/control is configured or declared but exact action-bound execution/verification evidence is missing, stale, failed, or mismatched.

Expected: `CONTROL_EXECUTION_EVIDENCE_REQUIRED`; no dependent transition.

### WDPC-300 — Enforcement execution attestation positive control

Positive control: exact candidate/action-bound evidence proves the required control executed and satisfies the policy-required verification state.

Expected: control evidence may satisfy this predicate without granting unrelated authority.

### WDPC-301 — Declared blocking control backed by fail-open executable path

Fault: policy/skill/docs declare an unskippable blocking control while executable runtime path is fail-open, missing, optional, instruction-only, or bypassable.

Expected: `DECLARED_EXECUTABLE_ENFORCEMENT_MISMATCH`; declaration cannot authorize.

### WDPC-302 — Declared/executable equivalence positive control

Positive control: declared mode, fail behavior, error behavior, scope, candidate binding, runtime path/version/digest and machine evidence are equivalent.

Expected: equivalence predicate passes without implying execution for any particular action.

### WDPC-303 — Harness capability overclaim / silent role swap

Fault: a role requires native/adapter enforcement but selected harness is instruction/reference-only, or model/provider/harness/version/config changes silently after qualification.

Expected: `HARNESS_CAPABILITY_ENVELOPE_STALE_OR_INSUFFICIENT`; governed revalidation/restart required. R1/R2/R3 remain provider/model-neutral roles.

### WDPC-304 — Qualified harness envelope positive control

Positive control: exact user-selected model/provider/harness binding satisfies all role-required capability classes and current version/config/identity predicates.

Expected: role binding eligible for this predicate only.

### WDPC-305 — Capability used without activation consent

Fault: available source mutation, subprocess, transcript egress, MCP/tool execution, persistence, credential use, or external side-effect power is exercised without exact governed activation or outside its project/resource/power/expiry scope.

Expected: `CAPABILITY_ACTIVATION_NOT_AUTHORIZED`.

### WDPC-306 — Capability activation positive control

Positive control: exact project/workflow, role, resources, powers, approver authority, sequence/expiry and harness identity match the active activation record.

Expected: activation predicate passes without broadening scope.

### WDPC-307 — Tool/MCP configuration drift with same friendly name

Fault: friendly tool name stays constant while endpoint, argv, permission profile, credential fingerprint, transport, harness/runtime version, or canonical config identity changes.

Expected: `TOOL_CONFIGURATION_ATTESTATION_STALE_OR_MISMATCHED`; dependent qualification becomes stale.

### WDPC-308 — Tool/MCP configuration attestation positive control

Positive control: canonical secret-safe configuration identity including exact endpoint/argv/permissions/credential fingerprint and harness/runtime binding matches the current governed attestation.

Expected: configuration predicate is current; no secret material is exposed by the proof view.

## Execution rule

WDPC-283…308 are preregistered only. WDPC-273/276/277 retain their historical V18 definitions and gain the stricter V19 expected evidence contracts above. No earlier RED/PASS evidence is rewritten.

EXP-ECC-6 and EXP-ECC-7 are intentionally not represented as integrated/pass cases here; their live/integration boundaries remain deferred.

V19 grants no execution-freeze, merge, release, deployment, qualification, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
