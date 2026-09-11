# TESTING Qualification Boundary — Independent Re-falsification 008

Status: `CHANGES_REQUIRED`
Authority effect: `NONE_EVIDENCE_ONLY`
Reviewed candidate: `61e98ba0ca8fc461b407e91e4f60ffc687fc784e`
Reviewer transport: user-relayed independent DeepSeek review.

This artifact preserves the reviewer disposition and findings as evidence. It does not itself adjudicate the findings, grant authority, or rewrite prior RED/green history.

## Reviewer findings

- `R8-01` CRITICAL — `manual_authority_verifier.py` is not externally blob-pinned; a candidate could replace `verify_manual_authority_attestation()` and forge verification results while the currently pinned policy/root modules remain unchanged.
- `R8-02` CRITICAL as reported — reviewer packet did not prove the required external check is source-bound to the dedicated GitHub App. This requires reconciliation against live ruleset evidence because the ruleset was changed immediately before merge and may not have been represented in the review packet.
- `R8-03` CRITICAL/HIGH — external checker workflow checks out mutable default-branch content and the checker repository is not protected/archived; historical checker SHA evidence is not a use-time checker-revision binding.
- `R8-04` HIGH — compatibility facade and other runtime modules are not externally pinned; externally validated module coverage may differ from runtime import paths.
- `R8-05` HIGH evidence gap — signed-attestation JSON/signature fixtures referenced by tests were absent from the review packet, preventing independent reproduction.
- `R8-06` HIGH evidence gap — preregistration 007 names `2fee17ad...` as its scientific subject while the reviewed post-merge candidate is `61e98ba0...`; exact-SHA requalification lineage was not explicit in the packet.
- `R8-07` MEDIUM/HIGH — runner-visible ruleset validation allows missing `bypass_actors` when administrative visibility is unavailable; external checker does not independently establish admin bypass state.

## Reviewer R7 closure disposition

- `R7-01`: PARTIALLY_CLOSED; R8-01 remains.
- `R7-02`: PARTIALLY_CLOSED; R8-01 remains.
- `R7-03`: STILL_OPEN according to packet evidence; reconcile against live source-bound ruleset evidence.
- `R7-04`: PARTIALLY_CLOSED; R8-01/R8-03 remain.
- `R7-05`: PARTIALLY_CLOSED; R8-01/R8-04 remain.
- `R7-06`: PARTIALLY_CLOSED; R8-04 remains.

## Evidence gaps explicitly reported

1. No external pin for `governance-runtime/manual_authority_verifier.py`.
2. Packet did not evidence live source binding of `external-governance-qualification` to the dedicated GitHub App.
3. No use-time immutable/pinned checker revision; checker repository not shown protected/archived.
4. Packet did not expose the actual Git blob SHA values in a directly recomputable evidence section.
5. Manual signed-attestation fixtures omitted from packet.
6. No administrative separation between repositories; all remain under the same human account.
7. Preregistration 007 subject SHA differs from reviewed merge SHA.
8. External checker did not independently establish ruleset bypass-actor state.

## Preservation rule

The earlier external PASS on `61e98ba0ca8fc461b407e91e4f60ffc687fc784e` remains valid historical evidence of what checker revision `b42fb00a03a41b6eea9a233bc8281de081649cc0` concluded at that time. This review does not erase that PASS; it falsifies the sufficiency of the mechanism/evidence boundary and therefore keeps TESTING blocked pending adjudication and repair.
