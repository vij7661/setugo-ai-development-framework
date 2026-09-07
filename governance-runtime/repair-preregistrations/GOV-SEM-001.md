# GOV-SEM-001 — Review Disposition / Evidence Consistency Repair Preregistration

State: PREREGISTERED_BEFORE_MECHANISM_CHANGE
Date: 2026-09-07
Branch: governance/live-conversation-runtime

## Observed defect

`REV-GOV-PR5-008` returned `disposition=PASS` while its own `evidence_assessment` stated that the raw files were not directly accessible, even though raw-byte integrity was an explicit required review question. The current review validator checks that `PASS` is an allowed token but does not deterministically reject or downgrade a disposition that contradicts the reviewer's own stated evidence coverage.

Failure classification: `REVIEW_DISPOSITION_EVIDENCE_CONTRADICTION`.

## Repair objective

A review disposition must not be promotable when the review's own structured evidence coverage says a mandatory review dimension was not tested, unavailable, inaccessible, contradicted, or insufficient.

## Frozen requirements

1. ReviewRequest must carry explicit machine-readable required review dimensions, not rely only on natural-language questions.
2. ReviewEvidence must carry explicit machine-readable coverage for every required dimension.
3. Each required dimension must have a status from a closed governed vocabulary.
4. `PASS` is valid only when every required dimension is `TESTED_SUPPORTED`.
5. `BOUNDED_PASS` is valid only when any non-`TESTED_SUPPORTED` dimension is explicitly allowed by the ReviewRequest as bounded/non-mandatory; mandatory dimensions may not be missing or untested.
6. `NOT_TESTED` or `INSUFFICIENT_EVIDENCE` is required when one or more mandatory dimensions are `NOT_TESTED`, `UNAVAILABLE`, `INACCESSIBLE`, or `INSUFFICIENT`.
7. `FAIL` or `CHANGES_REQUIRED` remains valid when contradicted/defective evidence is found, provided required output fields are complete.
8. Free-text `evidence_assessment` may provide explanation but may not substitute for structured coverage.
9. Promotion must depend on semantic review validation, not merely an allowed disposition token.
10. Existing reviewer identity-provenance, current-request binding, shared-memory grounding, deterministic gate, and transport invariants must remain unchanged.
11. A malicious or mistaken reviewer cannot obtain promotable `PASS` by omitting coverage fields.
12. A reviewer cannot claim `TESTED_SUPPORTED` for a required dimension without a non-empty evidence reference/summary for that dimension.

## Required adversarial tests

- PASS + required raw-integrity dimension `NOT_TESTED` => rejected.
- PASS + required dimension omitted => rejected.
- PASS + all required dimensions `TESTED_SUPPORTED` with evidence => semantically valid.
- BOUNDED_PASS + mandatory dimension `NOT_TESTED` => rejected.
- INSUFFICIENT_EVIDENCE + mandatory dimension unavailable => valid review content but non-promotable.
- CHANGES_REQUIRED + contradicted dimension => valid review content but non-promotable.
- Free-text says 'not accessible' while structured coverage falsely says supported => structured/free-text conflict must fail closed when deterministic contradiction patterns are detected; at minimum the specific `REV-GOV-PR5-008` phrase family is a permanent regression fixture.
- Existing API/manual-mode equivalence, reviewer spoof, superseded replay, stale-memory, and API failure tests remain green.

## Scientific boundary

The existing `REV-GOV-PR5-008` review remains preserved unchanged as first exposure evidence. It must not be rewritten to satisfy this repair. Any new independent review must target a later exact candidate revision.
