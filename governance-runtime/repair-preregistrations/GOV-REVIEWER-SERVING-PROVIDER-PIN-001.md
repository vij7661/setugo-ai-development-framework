# GOV-REVIEWER-SERVING-PROVIDER-PIN-001

Status: FROZEN BEFORE MECHANISM CHANGE
Date: 2026-09-09

## Trigger

Slice 7 review request `REV-MVP-SLICE7-TERMINAL-EXECUTOR-006` reached OpenRouter using the intended R3 credential, but the selected DeepSeek model was served by an unpinned upstream and consumed its full completion budget as reasoning, returning no assistant content. The run failed closed and has authority effect NONE.

## Approved requirement

For every governed reviewer slot (R1, R2, R3), provider routing must be data-driven and explicitly bound by the frozen review request. A reviewer request that uses a routing gateway such as OpenRouter must specify:

- exact gateway/provider identity;
- exact model identity;
- exact serving-provider allowlist/pin;
- `allow_fallbacks=false` for a single-provider governed review;
- bounded reasoning budget;
- bounded output budget;
- structured JSON output requirement.

The runtime must send those controls to the gateway and verify the returned serving provider. A mismatch, silent fallback, missing returned provider identity, missing assistant content, invalid JSON, or unsupported route must fail closed with no semantic or promotion authority.

Credential identity is separate from reviewer/model/serving-provider identity. Secret values must never be persisted in review evidence.

The rule is slot-generic. R1/R2/R3 are metadata; no semantic or dashboard behavior may depend on hard-coded provider names. Future reviewer APIs use the same frozen route fields and telemetry schema.

## Current Slice 7 rerun selection

- reviewer slot: R3
- gateway: `openrouter`
- model: `nvidia/nemotron-3-ultra-550b-a55b`
- serving provider: `deepinfra`
- provider fallback: disabled
- reasoning maximum: 4096 tokens
- total completion maximum: 16384 tokens
- output: strict JSON object
- candidate remains: `a4ad8bdd5b995e97529b08f12a7b3a7c6c924299`

This change modifies review orchestration only. It does not modify the Slice 7 candidate and cannot itself grant merge/release/deploy authority.
