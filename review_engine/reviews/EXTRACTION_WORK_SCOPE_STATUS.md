# Extraction Work Scope Status

This record covers platform-issued extraction work scope and claim-coverage admission binding on `feature/review-engine-mvp`.

Green CI is verification evidence only. It grants no production, release, correctness, or external-action authority.

## Control implemented

`ExtractionWorkRegistry` issues a single-use `ExtractionWorkOrder` only after the selected claim extractor passes its dedicated retained qualification for the requested scope.

The retained work order binds:

- unique work-order ID;
- exact artifact SHA-256;
- risk;
- task type;
- platform-derived extractor ID;
- extractor qualification reference;
- extractor qualification epoch.

`WorkOrderBoundClaimCoverageRegistry` admits a `ClaimCoverageInventory` only when it matches an outstanding work order. Admission does not accept a new risk/task scope from the inventory caller; those fields are read from the previously retained platform order.

Before admission the platform checks:

- work order exists and is unconsumed;
- exact artifact hash matches;
- extractor ID matches;
- qualification reference and epoch match;
- extractor is still qualified for the retained risk/task scope at admission time.

The qualification re-check means a revocation, epoch advancement or other retained qualification change after issuance invalidates outstanding work rather than allowing stale capability use.

The work order is consumed only after the coverage registry has accepted the inventory. A consumed order cannot be replayed for another inventory.

## Governed application boundary

When reviewer qualification records place `ReviewEngineApp` in `GOVERNED` assurance mode and claim coverage is configured, the app now requires the injected coverage validator to assert both:

- `qualified_admission_enforced = True`; and
- `trusted_scope_binding_enforced = True`.

Therefore:

- the raw reference `RetainedClaimCoverageRegistry` cannot inherit governed claim-coverage assurance;
- the qualification-only `QualifiedRetainedClaimCoverageRegistry` cannot inherit governed claim-coverage assurance because it still accepts risk/task as admission arguments;
- `WorkOrderBoundClaimCoverageRegistry` is the current governed reference surface because it requires qualified admission plus platform-issued extraction scope.

## Falsification coverage

The product regression suite attacks:

1. work order binds exact artifact hash;
2. work order binds exact risk and task type;
3. work order binds exact extractor identity and qualification ref/epoch;
4. risk above extractor qualification ceiling cannot receive a work order;
5. task outside extractor qualification scope cannot receive a work order;
6. inventory cannot substitute a different artifact after issuance;
7. inventory cannot substitute a different extractor after issuance;
8. qualification revocation/epoch advancement after issuance invalidates the outstanding order;
9. a consumed work order cannot be replayed;
10. admitted risk/task scope is retained from the work order rather than accepted again from the inventory caller;
11. governed app rejects raw unqualified coverage admission;
12. governed app rejects qualification-only coverage with free admission scope;
13. governed app accepts work-order-bound qualified coverage.

## Verification evidence

Core work-order implementation/falsification head:

`01c0ad71acfbc45b8849f0696bacbb14ef56cada`

GitHub Actions run `33984809710` completed `success` at that exact head. Its `validate-harness` job shows successful committed JSON/canonical case validation, Python compilation, Review Engine system regressions, scorer regressions, runner regressions, protected-truth regressions, observability regressions, continuation-authority regressions and governor falsification regressions.

Implementation/documentation head immediately before this status record:

`9d3458d082d5b0521c4547cf1251674c32b7e98a`

GitHub Actions run `33984875050` completed `success` at that exact head.

This status-record commit itself must receive exact-head CI before becoming the new moving-branch baseline.

## What this closes

Within the current in-process platform trust model, extraction artifact/risk/task scope no longer needs to be re-supplied as free-form inventory-admission arguments. The scope is issued once by the platform, tied to a qualified extractor, revalidated at admission, and consumed after successful inventory retention.

This also closes the obvious single-process replay path in which one work-order ID is reused for multiple coverage inventories.

## Declared boundaries

This control does **not** establish:

1. **Cryptographic provider runtime identity** — the order binds configured platform identity, not universal proof that a remote provider actually executed the named model/SKU/path.
2. **Externally signed capability semantics** — work orders are UUID-based in-process records, not cryptographically signed bearer capabilities.
3. **Durability across process restart** — the current `ExtractionWorkRegistry` is in-memory. Issued and consumed state is lost if the process restarts.
4. **Cross-process atomic replay protection** — an in-memory set protects one process only; it is not a distributed or durable consume ledger.
5. **TTL/expiry** — work orders currently have no retained issuance/expiry clock policy.
6. **Platform compromise resistance** — the trusted platform can still issue an incorrect scope. The model/extractor cannot self-authorize scope, but this does not make the platform infallible.
7. **Semantic extraction completeness** — a correctly scoped qualified extractor may still omit a material claim.
8. **External immutability** — the work-order registry and current SQLite evidence stores are not external WORM systems.
9. **External-action authority** — extraction work is evidence-processing capability only; it grants no deploy/write/release authority.

## Next attack surface

The next concrete product control should make extraction work state durable and transactionally consumable across process restart. A single-node SQLite reference implementation should persist issued/consumed state, use atomic consume semantics, reject replay after restart, and be tested under concurrent consume attempts. This still must not be described as distributed consensus, WORM storage, or provider runtime attestation.
