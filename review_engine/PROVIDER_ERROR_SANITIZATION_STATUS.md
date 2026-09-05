# Provider Error Sanitization Status

Validated implementation SHA: `ec5678f48d131786f02b0992ec83d7d50e9a81ee`

Exact-head GitHub Actions run: `33989618030` — **SUCCESS**.

## Enforced application boundary

When a provider/runtime `RuntimeError` occurs after a review request has been admitted:

1. the owning execution attempt terminally records `EXECUTION_ABORTED`;
2. provider-private exception text is not copied into retained session evidence;
3. direct application/CLI callers receive only `review execution failed; inspect retained session evidence`;
4. the original provider exception is suppressed from user-facing exception chaining;
5. request-admission/policy `ValueError` behavior, including duplicate request-ID rejection, remains distinct and is not collapsed into the generic provider failure.

## Regression evidence

The application and execution-abort suites inject provider failures containing deliberate secret markers and require that those markers appear in neither:

- the caller-visible RuntimeError, nor
- the hash-linked session evidence.

They also retain the existing checks for owned terminal abort, valid evidence-chain state, single-use aborted request IDs across restart, and no duplicate provider invocation.

## Non-claims

This is an application-boundary disclosure control. It does not claim privileged-process memory secrecy, provider-side log secrecy, operating-system isolation, or protection from a compromised runtime/debugger.
