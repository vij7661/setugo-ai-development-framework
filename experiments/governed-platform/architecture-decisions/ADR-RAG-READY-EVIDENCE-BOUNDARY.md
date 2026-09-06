# ADR: RAG-Ready Evidence Boundary

Status: **Accepted as target-architecture constraint**

## Context

The platform is currently proving governance, authority separation, reviewer independence, crash consistency, trust rotation, and latency without retrieval-augmented generation. RAG may be added later, but introducing retrieval must not require redesigning R1/R2/R3, authority issuance, routing, adjudication, or release gates.

## Decision

Adopt a stable, provider-independent `EvidenceBundle` boundary between evidence production and reviewer input assembly.

Reviewers and models MUST NOT depend directly on vector databases, embedding models, rerankers, web search engines, or document stores. Future RAG components are optional upstream adapters that populate the same EvidenceBundle contract used by current non-RAG evidence sources.

Retrieved content has `instructional_authority = false` and remains untrusted evidence. Retrieval never grants capabilities or authoritative state transitions.

The governor selects retrieval mode (`NONE`, `FROZEN_SHARED`, or `INDEPENDENT`) rather than the model.

## Consequences

Positive:
- RAG can be added later without changing reviewer contracts.
- Non-RAG operation remains first-class and independently testable.
- Retrieval latency can be measured separately from model latency.
- Retrieval defects remain distinguishable from reasoning/governance defects.
- Prompt-injection and provenance controls have a clear enforcement boundary.
- Multiple retrieval technologies can be swapped without changing R1/R2/R3.

Costs:
- EvidenceBundle schema/versioning must be maintained.
- Retrieval provenance and source authorization add metadata and validation work when RAG is introduced.
- Independent retrieval experiments will require separate frozen evidence bundles and additional storage.

## Deferred implementation

No vector DB, embedding service, reranker, or retrieval API is introduced by this ADR. Implementation is deferred to a separate EXP-R governed falsification campaign after the current governance/trust experiments are sufficiently stable.

## Governing reference

See `experiments/governed-platform/RAG_EXTENSION_CONTRACT.md` for the full interface, provenance, security, latency, failure-taxonomy, and migration requirements.
