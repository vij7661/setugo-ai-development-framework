# GOV-OPENROUTER-REVIEW-RUNNER-001

## Objective
Extend the already-qualified provider-neutral review runner with OpenRouter while preserving exact ReviewRequest provider/model binding, evidence materialization, role attestation, semantic validation, and fail-closed authority semantics.

## Prerequisite capacity evidence
`GOV-OPENROUTER-CAPACITY-PROBE-001` run 34239601859 completed a single request whose observed OpenRouter prompt usage was 173,870 tokens, HTTP 200, exact returned model `nvidia/nemotron-3-ultra-550b-a55b:free`, upstream provider `Nvidia`, cost 0, latency about 13.1s.

## Frozen implementation contract
1. Preserve v3 unchanged as historical qualified runner.
2. Add v4 supporting providers: gemini, groq, openrouter.
3. OpenRouter secret name is `OPENROUTER_API_KEY`.
4. OpenRouter uses `https://openrouter.ai/api/v1/chat/completions`.
5. ReviewRequest provider must be exactly `openrouter` and exact model must match trigger/runtime model when an exact model is frozen.
6. OpenRouter response `model` must equal the requested exact model; mismatch fails before semantic authority.
7. Capture OpenRouter upstream `provider` metadata in the execution envelope when returned.
8. Do not rely on OpenRouter/provider `response_format` support; strict JSON is prompt-required and deterministically parsed/validated locally.
9. R2 blind / R3 review-of-review attestation semantics remain unchanged and provider-independent.
10. Evidence materialization remains v2 and must complete before provider invocation.
11. All provider responses retain authority NONE until deterministic ingestion.
12. Existing frozen Gemini/Groq requests are not rewritten or silently substituted.

## Frozen deterministic tests
- ORR-01 supported provider set includes openrouter.
- ORR-02 secret mapping returns OPENROUTER_API_KEY.
- ORR-03 exact OpenRouter provider/model binding accepted.
- ORR-04 OpenRouter cannot satisfy Gemini-bound request.
- ORR-05 wrong OpenRouter exact model rejected.
- ORR-06 OpenRouter response model mismatch rejected.
- ORR-07 OpenRouter upstream provider metadata captured.
- ORR-08 R2 attestation remains blind.
- ORR-09 R3 attestation remains review-of-review exposed.
- ORR-10 no deterministic test invokes a real provider/network.

## Promotion effect
None. This qualifies runner capability only. Slice5 remains blocked until a separately frozen current R3 request is validly reviewed and deterministically adjudicated.
