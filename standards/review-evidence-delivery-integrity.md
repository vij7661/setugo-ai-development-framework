# Review Evidence Delivery Integrity Standard

## Status

`PREREGISTERED_FOR_EXP_M_FALSIFICATION`

This standard defines the governance boundary between an authoritative evidence set and the reviewer context actually delivered to an external or platform reviewer.

It does not claim that provider context windows, file ingestion, attachment parsing, or model attention are intrinsically trustworthy. Those properties must be evidenced by the delivery protocol before a reviewer verdict may become admissible.

## Problem statement

A review can return `INSUFFICIENT_EVIDENCE`, `CHANGES_REQUIRED`, `PASS`, or another disposition even when the underlying scientific evidence is unchanged, simply because the reviewer received a different subset or representation of that evidence.

Examples include:

- provider context truncation;
- unsupported ZIP/TAR/PDF/file types;
- attachment accepted by transport but unavailable to the model;
- one chunk omitted, duplicated, reordered, or corrupted;
- prompt plus evidence exceeding provider input limits;
- generated Markdown omitting decisive raw files;
- a provider silently dropping trailing context;
- a review beginning before all required evidence is delivered;
- evidence referenced in a manifest but not materialized into reviewer context;
- reviewer citations referring only to summaries rather than required raw evidence.

Therefore evidence existence and evidence delivery are separate governed facts.

## Core authority rule

**A reviewer verdict is inadmissible for an authority transition unless delivery completeness for the required evidence set is proven first.**

A review result may still be stored as diagnostic/external evidence when completeness is unproven, but it cannot satisfy a mandatory review gate.

Missing scientific evidence and missing delivered evidence must never be conflated.

## Required failure taxonomy

At minimum the platform must distinguish:

- `SCIENTIFIC_EVIDENCE_MISSING` — required scientific evidence does not exist in the authoritative evidence set.
- `EVIDENCE_DELIVERY_INCOMPLETE` — authoritative evidence exists but required material was not delivered or acknowledged.
- `REVIEW_CONTEXT_INCOMPLETE` — provider/model context capability was insufficient for the required review corpus.
- `EVIDENCE_FORMAT_UNSUPPORTED` — required evidence representation could not be consumed by the selected reviewer.
- `EVIDENCE_CHUNK_MISSING`
- `EVIDENCE_CHUNK_DUPLICATE`
- `EVIDENCE_CHUNK_REORDERED`
- `EVIDENCE_CHUNK_HASH_MISMATCH`
- `EVIDENCE_MANIFEST_MISMATCH`
- `EVIDENCE_ATTACHMENT_UNAVAILABLE`
- `EVIDENCE_TRUNCATION_SUSPECTED`
- `EVIDENCE_RECEIPT_UNPROVEN`
- `REVIEW_STARTED_BEFORE_DELIVERY_COMPLETE`
- `REVIEW_VERDICT_INADMISSIBLE_DELIVERY_FAILURE`

A generic `INSUFFICIENT_EVIDENCE` reviewer response must be adjudicated into one of:

- scientific insufficiency;
- delivery/context insufficiency;
- mixed/undetermined insufficiency.

If the platform cannot determine which, the verdict remains non-promotable.

## Evidence Delivery Manifest

Before provider invocation, the platform must create an immutable content-addressed delivery manifest containing at least:

- review request ID;
- reviewed artifact commit/tree;
- reviewer provider/model constraint;
- delivery protocol version;
- provider capability profile ID/hash;
- required review dimensions;
- required evidence item count;
- per-item stable ID;
- evidence class;
- authoritative source reference;
- raw SHA-256;
- exact byte length;
- media/content type;
- required/optional flag;
- chunking plan if chunked;
- total chunk count;
- per-chunk SHA-256 and byte length;
- canonical ordering;
- whole-corpus SHA-256;
- prompt SHA-256;
- expected total delivered bytes/tokens where measurable.

The manifest itself must be integrity-bound before dispatch.

## Provider capability profile

Before material review, the platform must bind a capability profile for the selected provider/model/API mode. At minimum it records known or experimentally qualified support for:

- maximum accepted request/body size;
- maximum model context;
- attachment/file support;
- supported file types;
- maximum file count;
- per-file size limits;
- whether attachment content is exposed to the model;
- whether multi-message/chunk continuation is supported;
- whether server-side file references are stable across turns;
- structured-output constraints;
- truncation/error behavior;
- provider/API revision or adapter version.

Unknown capability is not evidence of capability.

If the required evidence corpus cannot fit the qualified delivery profile, dispatch must fail closed or switch to an explicitly qualified chunk protocol. It must not silently omit evidence.

## Delivery preflight

Before reviewer invocation:

1. Materialize every required evidence reference.
2. Verify raw bytes/hash against authoritative source.
3. Build the delivery manifest.
4. Resolve provider capability profile.
5. Determine whether one-shot delivery is qualified.
6. If not, select a qualified deterministic chunk protocol.
7. Verify all required items are representable in the selected format.
8. Verify no required evidence was dropped for size or format reasons.
9. Freeze the exact prompt and evidence ordering.
10. Emit `DELIVERY_PREFLIGHT_PASS` only if all mandatory evidence is deliverable.

Failure must occur before a reviewer disposition can be treated as authoritative.

## Chunk protocol

When evidence is too large for a single request, the platform must use deterministic chunking.

Each chunk must bind:

- review request ID;
- corpus hash;
- chunk index;
- total chunk count;
- evidence item IDs included;
- chunk SHA-256;
- prior/next chunk linkage where applicable.

Rules:

- stable deterministic ordering;
- no semantic summarization as a substitute for required raw evidence unless the review contract explicitly allows it;
- no missing chunk;
- no duplicate chunk;
- no reordering without explicit canonical reconstruction;
- no mutation after manifest freeze;
- chunks from one review request cannot be replayed into another request;
- retries must preserve exact chunk identity.

## Reviewer receipt and completeness acknowledgement

Where the provider/API supports a structured staged protocol, the reviewer must first return a non-dispositive receipt acknowledging:

- review request ID;
- corpus SHA-256;
- expected evidence item count;
- expected chunk count;
- received chunk IDs/count;
- received evidence item IDs/count;
- any inaccessible/unsupported evidence;
- completeness state.

A final review prompt may be issued only after deterministic platform validation establishes:

`REVIEW_CONTEXT_COMPLETE=true`.

Reviewer self-assertion alone is not sufficient where the platform can independently verify transport receipts or reconstructed delivery state.

If the provider cannot support a reliable receipt/completeness protocol for the required corpus, that provider/mode is not qualified for that material review.

## Verdict admissibility

A reviewer verdict is promotable only when all are true:

- platform-authenticated review transport;
- valid current ReviewRequest;
- complete required evidence materialization;
- delivery preflight passed;
- provider capability profile covers the delivery;
- every required chunk/item was delivered;
- corpus/hash identity preserved;
- review context completeness established;
- review started only after completeness;
- semantic review coverage is valid;
- reviewer disposition is otherwise promotable.

A valid semantic `PASS` with unproven delivery completeness is non-promotable.

## Insufficient-evidence adjudication

When a reviewer returns `INSUFFICIENT_EVIDENCE` or equivalent:

1. Compare missing items claimed by reviewer against the authoritative evidence manifest.
2. If the evidence did not exist: classify `SCIENTIFIC_EVIDENCE_MISSING`.
3. If it existed but was omitted/unavailable/truncated in delivery: classify `EVIDENCE_DELIVERY_INCOMPLETE` or `REVIEW_CONTEXT_INCOMPLETE`.
4. If provider format capability caused omission: classify `EVIDENCE_FORMAT_UNSUPPORTED`.
5. If cause cannot be proven: classify `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`.
6. Never downgrade a delivery defect into a scientific failure.
7. Never convert a scientific absence into a transport excuse.

## Multi-reviewer equivalence

For review consensus/comparison, all reviewers that are being compared must be bound to equivalent evidence manifests or an explicitly documented provider-qualified representation.

If Claude, DeepSeek, Gemini, or another reviewer receives materially different evidence, their dispositions are not directly comparable as evidence of model disagreement.

The platform must preserve:

- reviewer-specific delivery manifest;
- provider capability profile;
- corpus/chunk hashes;
- delivery completeness result;
- final verdict.

## Required audit evidence

Every material API review must retain:

- review request;
- delivery manifest;
- provider capability profile;
- exact prompt;
- exact evidence item list;
- chunk records where used;
- delivery/preflight result;
- receipt/completeness result;
- provider raw response;
- parsed review;
- semantic validation result;
- disposition admissibility result.

## Security and false-green rules

The following must never establish delivery completeness by themselves:

- reviewer says "I received everything";
- HTTP 200;
- provider accepted an attachment upload;
- token count estimate only;
- evidence count copied from the outgoing request;
- model cites one file from a multi-file corpus;
- green CI;
- proposer assertion;
- aggregate corpus hash without per-item materialization.

## Required platform behavior

If delivery completeness fails:

- do not ask the reviewer to adjudicate as though complete;
- or, if a reviewer response already exists, mark it diagnostic/non-authoritative;
- do not interpret `INSUFFICIENT_EVIDENCE` as a scientific result without cause adjudication;
- preserve the failed delivery attempt;
- retry only with the same frozen review/evidence identity or a newly governed review request if representation materially changes.

## Governance scope

This standard supplements existing:

- review transport/provenance controls;
- semantic review coverage rules;
- portable packet integrity;
- external-evidence classification;
- independent-review evidence/prompt governance.

It specifically governs **evidence delivery completeness and reviewer context integrity**.
