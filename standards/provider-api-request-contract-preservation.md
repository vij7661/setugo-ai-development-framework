# Provider API Request Contract Preservation Standard

Status: GOVERNED PLATFORM INVARIANT — NO AUTHORITY EFFECT

## Goal

Keep governance/control/evidence changes from accidentally changing the actual provider API request.

The platform separates:

1. **internal governance envelope**
   - request/candidate identity
   - policy/admission decision
   - evidence identities
   - reviewer/authority state
   - audit metadata

2. **provider-facing request**
   - provider/endpoint
   - HTTP method
   - model
   - messages/input
   - provider parameters
   - timeout semantics
   - retry semantics

Internal governance metadata MUST NOT be inserted into the provider request unless the provider contract explicitly requires it and the change is separately governed as an API request change.

## Change classes

- CONTROL_PLANE_ONLY — governance state/decision changes only.
- EVIDENCE_ONLY — evidence/audit representation changes only.
- API_ADMISSION_EFFECT — may allow/block an invocation but does not change a valid provider request.
- API_REQUEST_SCHEMA_CHANGE — changes provider-facing request fields/schema.
- API_EXECUTION_BEHAVIOR_CHANGE — changes endpoint/routing/retry/timeout/streaming/response handling.

Governance remediation defaults to CONTROL_PLANE_ONLY and/or EVIDENCE_ONLY.

## Preservation invariant

For the same admitted logical request:

provider_request_fingerprint(before) == provider_request_fingerprint(after)

when the declared remediation class excludes API_REQUEST_SCHEMA_CHANGE and API_EXECUTION_BEHAVIOR_CHANGE.

A changed fingerprint under those classes is fail-closed.

## Secret handling

The fingerprint MUST NOT contain:
- Authorization values
- API keys
- bearer tokens
- repository secret values

Credential identity may be represented by a non-secret profile/slot identifier outside the provider semantic body.

## Provider-neutrality

The preservation mechanism is provider-neutral.
Provider-specific adapters may translate the canonical request into provider wire format, but governance fields cannot silently leak into that translation.

## Separate approval boundary

If a defect genuinely requires changing model, messages, endpoint, timeout, retry, streaming, routing, or response interpretation, classify it explicitly as API_REQUEST_SCHEMA_CHANGE and/or API_EXECUTION_BEHAVIOR_CHANGE and require separate review/tests.
