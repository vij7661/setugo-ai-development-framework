# V24-I11-V6-R11 — Final Review-Protocol Dependency Review

1. `DEPENDENCY_CONTENT_SCOPE = COMPLETE`

2. `NEW_CRITICAL_FINDINGS = 3`

3. `NEW_HIGH_FINDINGS = 3`

4. Findings

**CRITICAL — `BOUNDED_PASS` can be promotable with no mandatory semantic coverage.**
- Exact path: `_normalize_required_review_dimensions` allows every dimension to be `mandatory: false`; `validate_review_semantics` computes `mandatory = {... if x.get("mandatory") is True}` and for `BOUNDED_PASS` checks `any(statuses.get(d) != "TESTED_SUPPORTED" for d in mandatory)`. If `mandatory` is empty, `any(...)` is `False`, so validation returns `True`. `PROMOTABLE_REVIEW_DISPOSITIONS` includes `BOUNDED_PASS`, and `can_promote_material_transition` accepts that disposition.
- Concrete false-green/bypass: A schema-4 request can declare all dimensions `mandatory: false`; a `BOUNDED_PASS` evidence record can mark every dimension `NOT_TESTED` or `CONTRADICTED` and still pass `validate_review_semantics`, then promote if the deterministic gate, shared memory, and execution checks also pass.
- Governing rule: material transitions require deterministic gate plus authenticated, semantically complete mandatory review evidence.
- Narrow repair requirement: Require at least one mandatory dimension for material reviews; for `BOUNDED_PASS`, require a non-empty mandatory set, all mandatory dimensions `TESTED_SUPPORTED`, and reject defect/contradiction statuses or contradictory `evidence_assessment` text.

**CRITICAL — Transport identity assurance is caller-declared and forgeable.**
- Exact path: `DispatchResult` is a public dataclass; `_APITransportBase.dispatch` sets `identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED"` without independently authenticating `provider_call`; `ReviewOrchestrator.dispatch` checks only `transport.name` against `PLATFORM_REVIEW_TRANSPORTS`; `validate_review_evidence` trusts `execution.identity_assurance`, `execution.reviewer_provider`, `execution.reviewer_model`, and `execution.review_class`; `can_promote_material_transition` trusts `validate_review_evidence`.
- Concrete false-green/bypass: A caller can supply a custom transport object with `.name = "AUTOMATIC_API"` or directly construct a `DispatchResult` with `state="REVIEW_RECEIVED"`, `payload_hash=canonical_hash(request)`, `review_class="PLATFORM_AUTO_API_REVIEW"`, `identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED"`, and matching reviewer provider/model. Validation then succeeds without an authenticated provider transport.
- Governing rule: reviewer/provider/model identity must come from an independently authenticated transport, not wrapper-declared metadata.
- Narrow repair requirement: Require a non-forgeable trusted-adapter receipt or registry check; do not let caller-declared `DispatchResult` fields establish identity assurance; verify the concrete platform transport type and provider authentication.

**CRITICAL — Material Git commit identity is only a SHA-shaped string and is optionally bound.**
- Exact path: `build_review_request` and `verify_review_request` validate `artifact_commit` only via `SHA40.fullmatch`; `can_promote_material_transition` checks `active.get("current_reviewed_artifact_commit")` only when it is non-`None`, and never verifies the commit is an actual governed Git object or matches the active workstream head.
- Concrete false-green/bypass: A review request targeting commit A can be used to promote a transition for commit B if `authoritative_state.independent_review.current_reviewed_artifact_commit` is absent/`None`. Even when present, the commit remains only a 40-hex string, not independently resolved governed Git provenance.
- Governing rule: material Git commit identities must be verified as actual governed Git objects and bound to the material transition artifact.
- Narrow repair requirement: Require `current_reviewed_artifact_commit` to be non-`None` and equal to `review_request.artifact.commit`; verify the commit exists as a governed Git object and matches the authoritative transition/workstream head.

**HIGH — Legacy schemas return true from semantic validation.**
- Exact path: `validate_review_semantics` returns `True` immediately when `request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION`; `validate_review_evidence` calls it and can return `True` for legacy schema 1–3 if transport, identity, and field checks pass. `can_promote_material_transition` blocks schema `<4`, but the public validator does not.
- Concrete false-green/bypass: Any caller using `validate_review_evidence` as sufficient authority can accept a legacy schema 1–3 review without semantic coverage, despite the `SEMANTIC_REVIEW_SCHEMA_VERSION = 4` contract.
- Governing rule: material review validation requires semantic completeness; legacy content is historical only.
- Narrow repair requirement: Require schema `>=4` in `validate_review_evidence` for any promotable/material validation; keep legacy validation separate and explicitly non-authoritative.

**HIGH — Stale/mismatched request state and unused trigger/material binding.**
- Exact path: `can_promote_material_transition` never checks `review_request.get("state")`, never uses the `trigger` parameter, and never checks `review_request.get("material_authority_transition")`; `verify_review_request` permits states including `REVIEW_REJECTED` and `SUPERSEDED_BEFORE_REVIEW`.
- Concrete false-green/bypass: If `authoritative_state.independent_review.current_review_status` is promotable and the request ID matches, a review request whose own state is rejected/superseded, or whose trigger is for a different mandatory condition, can still be promoted.
- Governing rule: stale request state and trigger/material-authority binding.
- Narrow repair requirement: Require `review_request.state` to be in a promotable set, require `material_authority_transition` for material promotion, and require supplied `trigger` to match both the request trigger and the authoritative transition trigger.

**HIGH — Shared-memory grounding only inspects the first pending review.**
- Exact path: `validate_shared_memory_grounding` checks `pending[0]` only and does not validate later entries in `pending_reviews`.
- Concrete false-green/bypass: Shared memory can contain a valid first pending review plus stale/conflicting later pending review entries; grounding still passes.
- Governing rule: shared-memory state must not be stale or conflicted with authoritative review state.
- Narrow repair requirement: Validate the entire `pending_reviews` list against authoritative state, or require exactly one active pending review and reject extra/mismatched entries.

5. `CHANGES_TO_EXISTING_R12_SCOPE = ADD review_protocol.py findings for BOUNDED_PASS mandatory-coverage bypass, forgeable transport/identity assurance, governed Git commit binding, legacy semantic-validation false-green, request-state/trigger/material binding, and shared-memory pending-list validation. No existing R11/R12 findings are removed or downgraded.`

6. `R12_SCOPE_CAN_NOW_FREEZE = NO`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
