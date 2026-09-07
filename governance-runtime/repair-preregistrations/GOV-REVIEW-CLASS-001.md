# GOV-REVIEW-CLASS-001 — Platform Review vs External Evidence Classification

## Trigger

Live adversarial testing showed that pasted JSON can self-declare any reviewer/provider and that the user may intentionally paste review-shaped content without asserting that it is a review from that provider. Treating copy/paste as a normal review transport conflates initiation, provenance, and evidence ingestion.

## Frozen design

There are exactly two platform review execution classes and one external-evidence ingestion family:

1. `PLATFORM_AUTO_API_REVIEW`
   - initiated automatically by `AUTO_MODE`;
   - dispatched through `AUTOMATIC_API`;
   - reviewer provider/model provenance comes from the trusted provider adapter execution envelope;
   - may satisfy mandatory review when all other deterministic review/evidence gates pass.

2. `PLATFORM_USER_INITIATED_API_REVIEW`
   - initiated by a user control in `MANUAL_MODE` such as Ask Claude / Ask DeepSeek;
   - dispatched through `USER_INITIATED_API`;
   - uses the same trusted provider adapter, identity, semantic review, and promotion semantics as AUTO_MODE;
   - may satisfy mandatory review when all other deterministic review/evidence gates pass.

3. User-pasted/copied external material is **not a platform review transport**.
   - initial class: `USER_PROVIDED_EXTERNAL_CONTENT`;
   - no provider/model origin is inferred from the pasted payload itself;
   - payload fields such as `reviewer.provider` or `reviewer.model` are content claims only;
   - only after the user explicitly identifies the source as an external LLM review may the content be reclassified as `USER_ATTESTED_EXTERNAL_LLM_REVIEW`;
   - user attestation records reported provenance but does not create provider-API authentication;
   - neither external-content class may satisfy a mandatory provider-authenticated platform review gate by itself.

Core rule: **content cannot establish its own provenance**.

## Required mechanism changes

- `ReviewOrchestrator` must accept only `AUTOMATIC_API` and `USER_INITIATED_API` as review transports.
- `MANUAL_RELAY` must no longer be a production/platform review transport.
- Add explicit external-content classification/attestation functions that return evidence records, not `DispatchResult` review executions.
- Platform API execution must expose deterministic review class (`PLATFORM_AUTO_API_REVIEW` or `PLATFORM_USER_INITIATED_API_REVIEW`).
- Promotion must remain impossible from pasted/user-attested external content because no trusted platform review execution envelope exists.
- Normative contract, runtime validator, session checkpoint, and shared memory must use the new taxonomy.
- Historical manual-relay artifacts remain preserved as history; do not rewrite them into authenticated platform reviews.

## Frozen adversarial cases

- RC-01 AUTO_MODE + `AUTOMATIC_API` => `PLATFORM_AUTO_API_REVIEW`.
- RC-02 MANUAL_MODE user button + `USER_INITIATED_API` => `PLATFORM_USER_INITIATED_API_REVIEW` with the same authority semantics as RC-01.
- RC-03 pasted JSON self-declaring DeepSeek/Claude/Kimi without user source attestation => `USER_PROVIDED_EXTERNAL_CONTENT`; provider/model provenance remains unknown.
- RC-04 explicitly user-attested pasted DeepSeek review => `USER_ATTESTED_EXTERNAL_LLM_REVIEW`, reported provider DeepSeek, provider API authenticated = false.
- RC-05 self-declared reviewer fields may not upgrade RC-03 to RC-04.
- RC-06 external content/user-attested external review cannot be passed off as a trusted `DispatchResult` and cannot satisfy `validate_review_evidence` / material promotion.
- RC-07 API execution identity overrides/rejects contradictory reviewer self-claims exactly as before.
- RC-08 API failure remains fail-closed in both platform review classes.
- RC-09 platform MANUAL_MODE means user-initiated API, never copy/paste.
- RC-10 historical `MANUAL_RELAY` evidence remains readable/preserved but is non-promotable legacy external evidence.

## Current pasted-evidence classification

- The first REV-GOV-PR5-011-shaped payload pasted without a source assertion remains `USER_PROVIDED_EXTERNAL_CONTENT`; its internal `moonshot/kimi` fields are self-declared content only.
- The later payload explicitly introduced by the user as a DeepSeek review is `USER_ATTESTED_EXTERNAL_LLM_REVIEW`; reported provider/model = DeepSeek/DeepSeek; provider API authenticated by the platform = false.
- Both may inform defects/hardening, but neither counts as the platform-authenticated review required for PR #5 promotion.

## Non-blocking hardening observations retained from external content

- LOW: free-text PASS contradiction detection is regex-bounded.
- LOW: shared-memory grounding currently inspects only the first pending review entry.
- LOW: model-class matching is token-containment/coarse.

These are retained as hardening backlog and are not silently promoted to blocking defects in this repair.
