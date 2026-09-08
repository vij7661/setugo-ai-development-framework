# GOV-MULTI-PROVIDER-REVIEW-RUNNER-001

## Status
PREREGISTERED_BEFORE_IMPLEMENTATION

## Objective
Extend the authenticated governance review runner so future ReviewRequests may select an explicitly frozen provider without changing candidate/evidence semantics. Preserve the existing Gemini path and add Groq as the default provider for single-provider testing when the ReviewRequest explicitly requires Groq.

## Non-goals
- Do not change any already-frozen ReviewRequest provider binding.
- Do not use provider failover unless the ReviewRequest/policy explicitly permits it.
- Do not let workflow configuration substitute a provider that disagrees with the ReviewRequest.
- Do not weaken request integrity, evidence materialization, semantic coverage, role attestation, or fail-closed behavior.

## Required mechanism
1. Trigger `provider` must exactly match `required_reviewer.provider` in the frozen ReviewRequest.
2. Supported authenticated providers for this repair: `gemini`, `groq`.
3. Both providers reuse `platform_candidate_review_v2.py` evidence materialization semantics: every declared `file`, `ci_run`, and `history` ref is materialized or the run fails before provider invocation.
4. Provider-specific invocation is isolated behind an adapter. Semantic review JSON uses the same schema, mandatory dimension vocabulary, findings rules, and R2/R3 attestation validation.
5. Execution envelope must record actual provider/model and `provider_api_authenticated=true`; reviewer-supplied identity is not authority by itself.
6. Unknown providers fail closed before any external provider call.
7. Missing provider secret fails closed before invocation.
8. Existing Gemini behavior must remain regression-equivalent.
9. Groq must use only the exact provider/model frozen in the trigger/request; no hidden fallback model substitution.
10. Provider outage/retry history remains preserved with authority effect NONE.

## Default policy after qualification
- New single-provider TEST ReviewRequests: prefer Groq when no experiment-specific provider is required.
- Multi-provider/cross-provider experiments: use only the preregistered provider set/topology.
- Existing frozen Gemini requests remain Gemini-bound and are never rewritten to Groq.

## Frozen deterministic cases
- MPR-01 Gemini trigger + Gemini request routes Gemini adapter.
- MPR-02 Groq trigger + Groq request routes Groq adapter.
- MPR-03 trigger/request provider mismatch fails before provider invocation.
- MPR-04 unsupported provider fails before provider invocation.
- MPR-05 missing Groq secret fails before provider invocation.
- MPR-06 Groq review output must satisfy the same 10/12/etc mandatory dimension schema as Gemini.
- MPR-07 R2 blind attestation and R3 review-of-review attestation remain validator-enforced for Groq.
- MPR-08 provider/model recorded in execution envelope must match actual adapter runtime.
- MPR-09 evidence materialization counts are identical before either provider call.
- MPR-10 existing Gemini deterministic tests remain green.

## Authority
No implementation, workflow success, or provider response from this repair grants Slice5 authority. Slice5 remains blocked pending its already-frozen mandatory Gemini R3 or a separately governed superseding ReviewRequest/policy decision.