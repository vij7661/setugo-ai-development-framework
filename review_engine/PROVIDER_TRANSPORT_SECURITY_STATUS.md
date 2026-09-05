# Provider Transport Security Status

Status recorded after exact-head validation of implementation commit:

- implementation SHA: `4c01d73c3c531995639439c21d2cc3277b940624`
- GitHub Actions run: `33989256194`
- workflow: `Governed Platform + Review Engine Harness`
- result: **SUCCESS**

## Enforced transport contract

Credential-bearing provider adapters now enforce the following platform-side transport rules:

1. Remote provider base URLs must use HTTPS.
2. Plain HTTP is allowed only for explicit loopback development endpoints (`localhost` or loopback IP addresses).
3. Provider base URLs may not embed URL credentials.
4. Provider base URLs may not contain query strings or fragments.
5. Provider base URLs with malformed authority or whitespace fail closed.
6. HTTP redirects are refused rather than followed for credential-bearing provider requests.
7. The OpenAI-compatible, Anthropic and Gemini adapters all use the same redirect-rejecting provider transport.

## Falsification evidence

`test_provider_redirect_security.py` runs two local HTTP servers: a configured provider endpoint that returns HTTP 302 and a second sink representing a redirected/attacker destination. Each supported credential-bearing adapter is invoked against the redirecting endpoint with a test credential. The regression requires:

- each original provider request reaches the configured endpoint,
- each adapter fails on HTTP 302,
- the redirect sink receives **zero** requests.

This guards against forwarding bearer/API-key headers to a redirected destination and against redirect-based transport downgrade.

Additional provider transport/configuration regressions cover remote plain-HTTP rejection and safe loopback allowance.

## Scope / non-claims

This baseline establishes application-level URL validation and redirect refusal for the current Python provider adapters. It does **not** claim:

- certificate pinning,
- protection against compromise of a trusted provider origin,
- protection against privileged host/DNS/network compromise,
- a universal cryptographic runtime provider-identity proof,
- production release approval.

External authority, reviewer qualification, exact artifact/evidence binding and action authorization remain separate governance controls.
