# GOV-OPENROUTER-CAPACITY-PROBE-001

## Objective
Determine whether the existing GitHub `OPENROUTER_API_KEY` can carry a full-size governed review packet through a pinned free long-context OpenRouter model without truncation or provider-side request rejection.

## Pinned provider/model
- provider: `openrouter`
- model: `nvidia/nemotron-3-ultra-550b-a55b:free`
- advertised context: 1,000,000 tokens
- pricing: free

## Scientific question
Can one request in the ~60k-input-token class complete successfully using the exact pinned model, with no chunking, summarization, or evidence dropping?

## Frozen probe contract
1. Construct a deterministic synthetic payload of approximately 60,000 whitespace-delimited tokens.
2. Send it as a single OpenRouter chat-completions request.
3. Require a tiny machine-readable response containing the marker `OPENROUTER_CAPACITY_PROBE_OK`.
4. Capture HTTP status, returned model/provider metadata when available, prompt/completion token usage when available, latency, and failure body.
5. No governed promotion authority may derive from this probe; it is provider-capacity evidence only.
6. Any 4xx/5xx, rate-limit, context, TPM, quota, or truncation failure is a bounded FAIL for large-review suitability.
7. Success qualifies only the observed 60k-class request capacity at the time of test; it does not prove semantic reviewer quality.
8. The request must not be split, compressed, summarized, or retried with a smaller payload to manufacture a pass.

## Pass criterion
PASS only if the single full-size request succeeds and returns the required marker without evidence reduction.

## Fail-closed rule
If the provider cannot accept the full request, OpenRouter must not become the default for large governed reviews merely because its advertised context window is sufficient.
