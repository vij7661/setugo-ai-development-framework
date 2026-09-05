# Claim Coverage Current Review Scope Binding — Status

## Verified implementation baseline

- Implementation SHA: `24a90f69afbd7e7813f163464b9b1859aaefefb3`
- Exact-head GitHub Actions run: `33988375196`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The successful exact-head run covered the Review Engine system regressions plus the existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control implemented

Durable claim-coverage evidence is no longer reusable solely because it matches the current artifact.

`SQLiteExtractionWorkRegistry.retained_inventories_for_scope` now filters retained inventories against the current trusted review scope. An inventory is eligible only when:

1. its original extraction work-order risk is at least the current review risk;
2. its original work-order task type matches the current review task type;
3. the extractor's currently retained qualification still covers the current review risk/task;
4. the retained extractor identity still matches the current qualification epoch/bindings.

`SQLiteWorkOrderBoundClaimCoverageRegistry` advertises this as `review_scope_binding_enforced` and `current_extractor_qualification_recheck_enforced`.

`ReviewEngineApp` refuses GOVERNED claim-coverage assurance without both controls. The application opens a per-request trusted coverage scope using the platform-derived request risk and task type. `ClaimCoverageGuardedInvoker` keeps that scope in a `ContextVar`, so concurrent requests do not share mutable governance scope.

R1 may raise its own proposed risk. The guard raises the retained scope before evaluating R1's claim coverage and preserves that stricter value for later reviewer calls in the same request. R1 cannot lower the platform floor.

## Falsification coverage

The regressions verify:

1. a LOW-risk retained inventory can satisfy a LOW-risk review but is `UNVERIFIED` for HIGH risk;
2. a RESEARCH-scoped inventory cannot satisfy a GENERAL review;
3. extractor revocation after inventory admission makes the retained inventory ineligible for current assessment;
4. a HIGH-risk application request cannot reuse a LOW-risk inventory without a material `TVC-COVERAGE` finding;
5. an R1 request that begins LOW but is self-escalated by R1 to HIGH raises claim-coverage scope before the R1 completion event;
6. a HIGH-risk inventory remains eligible for a matching HIGH-risk review, avoiding a false block;
7. health/review output exposes current-review scope binding and qualification-recheck state.

## What this does not prove

This control does not claim:

- semantic truth or completeness of the extracted inventory;
- authenticity of external evidence sources;
- cryptographic runtime identity of the extractor provider/model;
- distributed or externally immutable retention;
- that historical qualification revocation policy is universally correct for every domain.

The implemented policy is deliberately fail-closed for current governed use: if a retained extractor qualification is no longer current/eligible, previously admitted coverage does not satisfy a new governed review.
