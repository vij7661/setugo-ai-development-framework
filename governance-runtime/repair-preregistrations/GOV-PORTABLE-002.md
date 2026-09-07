# GOV-PORTABLE-002 — Single-File Manual Review Container

## Status
PREREGISTERED_BEFORE_MECHANISM_CHANGE

## Trigger
DeepSeek manual relay does not accept ZIP files, and requiring a human user to upload many raw files one-by-one is operationally impractical. REV-GOV-PR5-009 was activated but was not sent to the reviewer before this limitation was confirmed.

## Defect classification
`MANUAL_RELAY_ATTACHMENT_FORMAT_MISMATCH`

The current portable export proves raw bytes internally using a ZIP/ordinary-file artifact layout, but the external reviewer transport cannot consume that package conveniently. Sending only the Markdown convenience packet would recreate the REV-GOV-PR5-008 evidence gap and make `raw_byte_integrity` untestable.

## Frozen repair contract
1. REV-GOV-PR5-009 must be preserved and superseded before external review.
2. Manual relay must support a single ordinary text attachment containing the exact ReviewRequest, review instructions, evidence summaries, and every required UTF-8 artifact.
3. Every embedded artifact must include its repository path, raw Git blob SHA-256, exact UTF-8 byte length, and full content.
4. Re-encoding each embedded content string as UTF-8 must reproduce the recorded byte length and SHA-256.
5. The single-file container itself must have a deterministic canonical payload hash.
6. Reviewer instructions must explicitly state that the embedded artifact records, not reconstructed Markdown fences, are the byte-review basis.
7. No review/evidence/promotion semantics may be weakened by the packaging change.
8. CI must deterministically verify single-file reconstruction of every artifact before a candidate packet is accepted.
9. The human handoff for compatible reviewers must require exactly one ordinary attachment plus one prompt.
10. Failure to construct/verify the single-file container must fail closed and block request activation.

## Frozen adversarial cases
- P2-01: all embedded artifact UTF-8 bytes reconstruct to declared hash and length.
- P2-02: modified embedded content fails verification.
- P2-03: modified byte length fails verification.
- P2-04: omitted required artifact fails evidence coverage.
- P2-05: container payload tampering fails canonical container hash verification.
- P2-06: one-file packaging does not alter ReviewRequest hash, reviewer selection, required dimensions, or promotion eligibility.
- P2-07: single-file container explicitly embeds all byte-authoritative artifacts and declares one-file manual handoff.

## Scientific/authority constraint
Construction green under these cases is not independent review or promotion of PR #5. A new exact candidate must receive a fresh governed independent review request after the repair is frozen.
