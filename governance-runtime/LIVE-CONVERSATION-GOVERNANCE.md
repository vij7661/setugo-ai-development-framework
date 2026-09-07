# Live Conversation Governance Runtime

## Purpose

Apply governed-platform rules to the human–LLM development conversation so chat-window changes, model confidence, shared-memory drift, reviewer substitution, reviewer self-identification, review-delivery mode, pasted content, packet representation, or reviewer-disposition overclaim cannot silently change authoritative project state.

This is an operational control for our collaboration. It does not claim that the ChatGPT product itself enforces these rules internally.

## Authority precedence

1. Governed Git/evidence bound to exact revisions.
2. Governed registries/checkpoints referenced by Git.
3. Governed shared project memory as active continuity/coordination whose material pointers must resolve to authority.
4. Current project chats/files as working context.
5. Ungoverned summaries/caches as advisory navigation.
6. Model recollection/confidence has no authority.

Shared memory is actively read and written, but never independently authoritative. Conflict is surfaced; authoritative state wins; memory is repaired rather than silently merged.

## Session bootstrap

Before authoritative continuation in a fresh chat/session:

1. Read `governance-runtime/shared-memory.json`.
2. Read `governance-runtime/session-state.json`.
3. Verify referenced branches, commits, review requests/evidence, and frozen artifacts.
4. Read applicable governed standards.
5. Reconcile memory/chat context with authority.
6. If authority cannot be verified, enter `GROUNDING_REQUIRED`.

A chat boundary may not change claim status, experiment state, review state, revision identity, evidence validity, promotion eligibility, or terminal authority.

## Review levels and platform modes

Review requirement and interaction mode are independent dimensions.

### Review levels

- `NONE` — no review requested for non-authoritative/routine work.
- `RECOMMENDED` — R1 may recommend review for non-mandatory work.
- `REQUIRED` — protected authority transition cannot promote without valid independent review.

R1 may raise `NONE` to `RECOMMENDED`; R1 may not lower a protected transition to optional merely by changing a trigger label.

### `AUTO_MODE`

When review is recommended/required, the platform dispatches the configured provider API automatically via `AUTOMATIC_API`. A successful authenticated execution is classified `PLATFORM_AUTO_API_REVIEW`.

### `MANUAL_MODE`

R1 shows its answer first. When review is recommended/required, the UI shows controls such as `Ask Claude` / `Ask DeepSeek`. A user click dispatches the configured provider API through `USER_INITIATED_API`. A successful authenticated execution is classified `PLATFORM_USER_INITIATED_API_REVIEW`.

For `RECOMMENDED`, the user may skip review. For `REQUIRED`, the user may decline the call, but the protected authoritative transition remains pending/non-authoritative.

Changing AUTO ↔ MANUAL changes **who initiates the provider API call only**. It never changes evidence, identity, independence, semantic review, or promotion rules.

## Review execution classes

There are exactly two platform review execution classes:

1. `PLATFORM_AUTO_API_REVIEW` — `AUTO_MODE` + `AUTOMATIC_API`.
2. `PLATFORM_USER_INITIATED_API_REVIEW` — `MANUAL_MODE` user action + `USER_INITIATED_API`.

Both use trusted provider adapters and the same ReviewRequest, semantic coverage, identity, independence, fail-closed, and promotion semantics. Neither class derives reviewer provenance from reviewer-authored content.

Copy/paste is **not** a platform review transport.

## External evidence ingestion

User-pasted/copied material enters a separate evidence family.

### `USER_PROVIDED_EXTERNAL_CONTENT`

This is the default class for pasted review-shaped content when the user has not explicitly identified its source.

- no provider/model origin is inferred from the payload;
- fields such as `reviewer.provider` / `reviewer.model` are self-declared content claims only;
- the content may expose defects or provide useful technical evidence;
- it is not a platform review execution and cannot satisfy a mandatory platform review gate.

### `USER_ATTESTED_EXTERNAL_LLM_REVIEW`

Only after the user explicitly identifies pasted material as a review from an external LLM may it be reclassified to this class.

- user attestation records the reported provider/model source;
- user attestation is **not** provider-API authentication;
- self-declared payload identity must never create or upgrade provenance;
- the content remains external evidence and is non-promotable by itself.

Core rule: **content cannot establish its own provenance**.

Historical `MANUAL_RELAY` artifacts remain readable and preserved, but `MANUAL_RELAY` is no longer a platform review transport. Legacy manual-relay results are external evidence/history only.

## Material authority review floor

`can_promote_material_transition` is the authority boundary. Material promotion is **review-required by definition**, regardless of the caller-supplied `trigger` string.

The UI/orchestration classifier additionally fails closed for:

- known mandatory-review triggers;
- explicit material transitions;
- governing-standard review requirements;
- governance-relevant paths including `governance-runtime/`, `standards/`, `experiments/governed-platform/`, and `.github/workflows/`.

A proposer mislabel such as `ROUTINE_FORMATTING` cannot waive review at the material promotion gate.

## ReviewRequest and current-state binding

A mandatory platform review is represented by an integrity-bound `ReviewRequest` containing at least:

- request identity;
- exact reviewed artifact commit;
- proposer provider/model;
- required reviewer provider plus model/model-class constraint;
- blind-review requirement;
- review questions;
- evidence references;
- material/standard/path classification context.

For material promotion, the runtime additionally requires a semantic review contract (ReviewRequest schema 4+) containing machine-readable `required_review_dimensions`. A legacy review request without this semantic contract may be preserved as historical content but cannot authorize material promotion.

Promotion must bind review evidence to the currently authoritative review request and current reviewed artifact. A review for a superseded request or older revision cannot be replayed into a later candidate.

## Semantic review coverage and disposition consistency

A reviewer conclusion is not valid merely because its `disposition` token is syntactically allowed.

Every schema-4 material ReviewRequest defines explicit review dimensions with:

- stable dimension ID;
- `mandatory` boolean;
- description;
- governed closed coverage-status vocabulary.

ReviewEvidence must provide one `review_coverage` entry for every dimension, containing:

- `dimension_id`;
- status;
- concrete evidence references/observations where the dimension was tested;
- a non-empty assessment of what was actually examined.

Allowed dimension statuses are:

- `TESTED_SUPPORTED`
- `TESTED_DEFECT_FOUND`
- `CONTRADICTED`
- `NOT_TESTED`
- `UNAVAILABLE`
- `INACCESSIBLE`
- `INSUFFICIENT`

Semantic disposition rules are deterministic:

- `PASS` requires every listed review dimension to be `TESTED_SUPPORTED`, with non-empty evidence for each.
- `BOUNDED_PASS` requires every `mandatory: true` dimension to be `TESTED_SUPPORTED`; only explicitly non-mandatory dimensions may remain bounded.
- `NOT_TESTED` / `INSUFFICIENT_EVIDENCE` are correct when one or more mandatory dimensions are unavailable, inaccessible, not tested, or insufficient.
- `FAIL` / `CHANGES_REQUIRED` require at least one concrete finding and a contradicted, defective, or insufficient coverage state.
- negative review outcomes can be valid review evidence but are not promotable.
- only semantically valid `PASS` or `BOUNDED_PASS` may satisfy the review side of material promotion.

Free-text `evidence_assessment` explains structured coverage but cannot substitute for it. If free text contradicts an asserted `PASS`, the review fails closed. `REV-GOV-PR5-008` is a permanent regression fixture for this failure family.

## Reviewer identity provenance

Reviewer-authored JSON fields such as:

```json
{"reviewer":{"provider":"anthropic","model":"claude-..."}}
```

are content claims, **not authentication**.

`AUTOMATIC_API` and `USER_INITIATED_API` derive provider/model identity from the trusted configured provider adapter/execution envelope. Review content must agree with that trusted identity; disagreement fails closed.

Pasted external evidence has no platform-authenticated provider identity. If the user explicitly identifies the external source, that creates user-attested provenance only.

## Review execution to promotion wiring

Material promotion consumes all of these directly:

1. deterministic gate result;
2. authoritative checkpoint;
3. grounded shared memory;
4. current schema-4 ReviewRequest with required dimensions;
5. ReviewEvidence with complete semantic coverage;
6. a trusted platform API execution/provenance envelope whose review class matches its API transport.

No caller-provided boolean such as `valid_independent_review_present=True`, no pasted JSON, and no user-attested external review can mint review validity.

Review fails closed when execution is missing, pending, errored, non-platform transport, wrong request, wrong revision, unauthenticated, wrong provider/model, self-review, malformed, non-blind when blind review is required, semantically inconsistent, negative/non-promotable, or conflicts with its trusted execution identity.

Consensus is metadata, not evidence, and cannot bypass deterministic evidence gates.

## Shared-memory grounding

Before material promotion, shared memory must reconcile with authoritative checkpoint state for at least:

- active workstream branch;
- exact workstream head;
- workstream status;
- current review request;
- current review status;
- pending review coordination.

Stale/conflicted memory blocks material promotion until reconciled.

Authoritative persistence occurs before memory synchronization. If memory synchronization later fails, authority remains valid and memory is marked stale. If authoritative persistence fails, authoritative completion is blocked.

## Portable external review/evidence export

A portable packet may still be generated for advisory external review/evidence work when the external model has zero repository/browser/tool access. That export is an **external evidence transport artifact**, not a platform review execution and not a substitute for `AUTOMATIC_API` or `USER_INITIATED_API`.

A portable export should contain:

- exact ReviewRequest or review context;
- exact reviewed candidate identity;
- explicit review dimensions;
- detached manifest;
- human-readable packet;
- raw canonical repository artifacts where required;
- per-artifact SHA-256 and exact byte length over raw Git blob UTF-8 bytes;
- evidence-reference coverage;
- CI/builder evidence;
- whole-packet/logical hashes;
- `repository_access_required: false`.

Raw files are byte-authoritative. Markdown fences are convenience only. If an external reviewer cannot inspect a mandatory dimension, its external result must not claim that dimension was tested.

Portable-packet integrity makes external evidence more useful; it does **not** upgrade external evidence into a platform-authenticated review.

## Frozen evidence and repair discipline

For falsification/acceptance work:

1. preregister/freeze where required before exposure;
2. preserve first exposure;
3. classify before repair;
4. never change frozen tests/fixtures/expectations merely to get green;
5. changes to frozen artifacts after exposure require a new governed boundary and independent review;
6. preserve superseded/invalid attempts and correction history;
7. construction green is not scientific acceptance when a later frozen acceptance run is required.

## Failure taxonomy

At minimum preserve/surface:

- `MEMORY_OVERRIDES_AUTHORITY`
- `SHARED_MEMORY_STALE_UNDETECTED`
- `SHARED_MEMORY_CONFLICT_SILENTLY_MERGED`
- `MODEL_CONFIDENCE_BYPASSED_REVIEW`
- `PROPOSER_CONTROLLED_REVIEW_CLASSIFICATION`
- `MANDATORY_REVIEW_SKIPPED`
- `REVIEWER_IDENTITY_SELF_ATTESTATION_ACCEPTED`
- `EXTERNAL_CONTENT_SELF_PROVENANCE_ACCEPTED`
- `USER_ATTESTATION_TREATED_AS_PROVIDER_AUTHENTICATION`
- `EXTERNAL_EVIDENCE_TREATED_AS_PLATFORM_REVIEW`
- `REVIEW_INDEPENDENCE_UNPROVEN`
- `REVIEW_WRONG_REVISION_ACCEPTED`
- `SUPERSEDED_REVIEW_REPLAY_ACCEPTED`
- `REVIEW_TRANSPORT_CHANGED_POLICY`
- `PLATFORM_MODE_CHANGED_AUTHORITY`
- `API_FAILURE_TREATED_AS_APPROVAL`
- `REVIEW_ID_SEMANTIC_REBIND`
- `CONSENSUS_AS_EVIDENCE`
- `REVIEW_DISPOSITION_EVIDENCE_CONTRADICTION`
- `REVIEW_REQUIRED_DIMENSION_OMITTED`
- `REVIEW_PASS_WITH_UNTESTED_MANDATORY_DIMENSION`
- `NEGATIVE_REVIEW_TREATED_AS_PROMOTABLE`
- `LEGACY_REVIEW_SCHEMA_PROMOTED`
- `PORTABLE_REVIEW_BUNDLE_TAMPERED`
- `PORTABLE_REVIEW_MANIFEST_MISMATCH`
- `PORTABLE_REVIEW_RAW_HASH_UNREPRODUCIBLE`
- `FAILURE_HISTORY_REWRITTEN`
- `TERMINAL_AUTHORITY_SELF_GRANTED`

## Live operating procedure

1. Recover shared memory.
2. Verify against authoritative Git/evidence.
3. Reconcile stale/conflicting memory.
4. Classify work/review level.
5. Preregister/freeze when applicable.
6. Execute narrow construction.
7. Preserve first failures/revisions.
8. Apply platform review policy.
9. In AUTO_MODE, dispatch `AUTOMATIC_API`; in MANUAL_MODE, show reviewer controls and dispatch `USER_INITIATED_API` only after user selection.
10. Treat copy/paste as external evidence ingestion, initially `USER_PROVIDED_EXTERNAL_CONTENT`.
11. Reclassify pasted content to `USER_ATTESTED_EXTERNAL_LLM_REVIEW` only when the user explicitly identifies the source; never equate that attestation with API authentication.
12. Bind platform reviewer identity from trusted execution provenance.
13. Validate ReviewRequest + ReviewEvidence + structured semantic coverage + platform API execution envelope.
14. Require a positive promotable disposition before platform review can satisfy material promotion.
15. Apply deterministic governor/evidence gate.
16. Persist authoritative checkpoint.
17. Synchronize shared memory.
18. New chat resumes from shared memory then verifies Git.

## Current collaboration limitation

This chat can ingest pasted external evidence, but pasted content is not a platform review execution. Therefore it cannot satisfy a mandatory provider-authenticated PR #5 review gate. In the production platform, both AUTO_MODE and MANUAL_MODE avoid this limitation by using trusted provider API adapters (`AUTOMATIC_API` / `USER_INITIATED_API`).
