# Reviewer Evidence Delivery and Defect-Remediation Contract

Status: GOVERNED PLATFORM INVARIANT — NO AUTHORITY EFFECT

## 1. What a reviewer is reviewing

When a review request declares a document, file, corpus, artifact, diff, log, or evidence object as review material, the reviewer is reviewing that exact material.

A filename, summary, digest, metadata row, or human description of a document is not a substitute for delivering the document itself.

The review request must distinguish:
- REVIEW_SUBJECT — the exact document/artifact/candidate being reviewed;
- SUPPORTING_EVIDENCE — logs, test outputs, diffs, manifests, historical evidence;
- REVIEW_INSTRUCTIONS — the questions/dimensions the reviewer must assess;
- EXPECTED_OUTPUT — the machine-readable review result contract.

The reviewer must not be asked to infer missing review material from summaries or model recollection.

## 2. Delivery completeness

Every mandatory REVIEW_SUBJECT or SUPPORTING_EVIDENCE item must be materially delivered to the reviewer execution by one supported mechanism:

1. native file/attachment delivery with exact file identity;
2. exact in-request materialization of the content;
3. deterministic chunked delivery with a complete manifest.

For every delivered item record:
- logical evidence id;
- exact source identity;
- raw SHA-256;
- byte count;
- delivery mode;
- if chunked: chunk_count, chunk indexes, per-chunk SHA-256, and exact coverage.

A review is non-promotable if mandatory material is:
- missing;
- truncated;
- summarized instead of delivered;
- partially chunked;
- digest-mismatched;
- delivered from a different candidate/version;
- referenced only by filename/URL without materialization when the reviewer cannot independently fetch it under the governed execution.

## 3. Chunk completeness

For chunked evidence:
- chunk indexes are contiguous and unique;
- all declared chunks are delivered;
- concatenated canonical bytes reproduce the declared whole-document SHA-256;
- no chunk may silently overlap, omit, or reorder source ranges unless the manifest explicitly defines the canonical reconstruction.

If expected chunks = N and delivered chunks != N, review cannot be treated as complete.

## 4. Reviewer task

The reviewer is expected to review the actual REVIEW_SUBJECT against the requested review dimensions.

For every defect, the reviewer should provide:
1. finding id;
2. severity;
3. exact location/contract;
4. concrete failure/false-green path;
5. evidence supporting the finding;
6. impact;
7. the narrowest safe proposed remediation;
8. exact regression/falsification test(s) that would prove the defect is closed;
9. whether the defect invalidates the candidate/review boundary;
10. whether it is merge/promotion blocking.

The reviewer SHOULD propose solutions for defects because this improves remediation quality and reduces repeated interpretation.

However:
- reviewer-proposed solutions are advisory engineering input, not authority;
- the proposing/implementing agent must independently validate the solution;
- the platform must not blindly implement a reviewer recommendation without checking cross-component effects and preserved valid behavior;
- a reviewer finding can be valid even if its proposed solution is rejected or narrowed;
- a reviewer solution can itself be incomplete or harmful and must be falsified before adoption.

## 5. Separation of roles

Reviewer:
- discovers and explains defects;
- proposes narrow remediation and tests;
- does not implement or self-approve the remediation;
- does not grant merge/release/deployment/production authority.

Implementer:
- adjudicates the proposal;
- checks whether the recommendation changes other contracts;
- implements the smallest safe repair;
- adds permanent regression/invariant coverage.

Governor:
- verifies exact evidence, candidate identity, and required review state;
- does not infer authority from reviewer confidence or a provider success response.

## 6. Defect-solution adjudication states

Each reviewer recommendation must be recorded as exactly one of:
- ACCEPTED_AS_PROPOSED
- ACCEPTED_NARROWED
- ACCEPTED_WITH_ALTERNATIVE_SOLUTION
- REJECTED_NOT_REPRODUCED
- REJECTED_UNSAFE_OR_OUT_OF_SCOPE
- DEFERRED_REQUIRES_EVIDENCE

The adjudication must preserve the original finding and proposed solution.

## 7. API request preservation

Evidence delivery metadata stays in the internal governance envelope unless the provider's review API explicitly requires file/chunk objects.

When the provider supports files, deliver the file through the provider's file/attachment mechanism and bind its exact content identity.

When the provider does not support files, materialize exact content/chunks into the reviewer request.

This evidence-delivery mechanism must not silently alter unrelated provider request semantics such as selected model, ordinary user content, timeout, retry, routing, or response interpretation.

## 8. Fail-closed rule

A review result cannot satisfy a governed review requirement unless:
- all mandatory review subjects/evidence were delivered completely;
- delivery identity is exact-bound;
- reviewer output validates against the required schema;
- every mandatory review dimension was actually assessed;
- any blocking finding prevents promotion.

AUTHORITY_EFFECT = NONE
