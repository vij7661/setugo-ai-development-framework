# Extractor Qualification Admission Status

This record covers the dedicated claim-extractor qualification and coverage-inventory admission controls on `feature/review-engine-mvp`.

Green CI is verification evidence only. It grants no production, release, correctness, or external-action authority.

## Control implemented

Claim extraction is treated as a distinct qualified role rather than inheriting R1/R2/R3 reviewer qualification.

`ExtractorQualificationRecord` binds:

- qualification reference;
- provider;
- model;
- SKU;
- deployment path;
- foundation lineage;
- status;
- monotonically advancing qualification epoch;
- maximum risk;
- task-type scope.

`ExtractorQualificationRegistry` evaluates an extractor identity against those exact bindings. `QualifiedRetainedClaimCoverageRegistry` refuses to retain a coverage inventory until the extractor is eligible for the platform-supplied artifact risk/task scope.

A governed Review Engine application also fails initialization if claim coverage is configured with a validator that does not explicitly enforce qualified extractor admission. A raw experimental/reference coverage registry cannot silently inherit the `GOVERNED` assurance label.

## Falsification coverage

The regression suite attacks:

1. exact qualified extractor eligibility;
2. `REVOKED` qualification;
3. `PENDING` qualification;
4. `EXPIRED` qualification;
5. explicitly `UNQUALIFIED` status;
6. stale qualification epoch;
7. provider substitution;
8. model substitution;
9. SKU substitution;
10. deployment-path substitution;
11. foundation-lineage substitution;
12. risk above the extractor qualification ceiling;
13. task type outside qualification scope;
14. non-monotonic qualification epoch updates;
15. unqualified inventory admission before it can become coverage evidence;
16. qualified inventory admission with retained qualification reference/epoch/risk/task evidence;
17. governed application attempting to inject the raw unqualified reference coverage registry;
18. governed application using qualification-enforced coverage admission.

Claim-coverage stage findings also retain stable inventory, extractor, provenance and correlation-warning references so later evidence review can trace the retained coverage evidence that generated a `TVC-COVERAGE` finding.

## Verification evidence

Implementation/documentation head:

`56696e85906823f63401cf41d1e5df0d07d56515`

GitHub Actions run `33984640766` completed `success` at that exact head. Its `validate-harness` job shows successful:

- committed JSON/canonical case validation;
- Python compilation;
- Review Engine system regressions;
- scorer regressions;
- runner regressions;
- protected-truth regressions;
- observability regressions;
- continuation-authority regressions;
- governor falsification regressions.

This status-record commit itself must receive its own exact-head CI before becoming the new moving-branch baseline.

## What this closes

Within the current application trust model, an extractor's self-description or an arbitrary `qualification_ref` string is no longer sufficient to admit claim-coverage evidence in the qualification-enforced registry. Status, epoch, provider/model/SKU/deployment, lineage, risk and task scope are checked against retained platform qualification evidence.

When reviewer qualification records place the app in `GOVERNED` assurance mode, configured claim coverage cannot use the raw reference registry; qualified extractor admission is mandatory.

## Declared boundaries

This does **not** establish all of the following:

1. **Runtime cryptographic identity** — the platform qualification binding does not universally prove which remote provider/model/SKU actually executed extraction.
2. **Trusted admission scope provenance** — the risk/task values supplied when an inventory is admitted must come from the trusted extraction pipeline. The qualification registry cannot detect a compromised platform caller lying about those admission facts.
3. **Semantic extraction completeness** — a qualified extractor can still miss a material claim. Qualification means the extractor passed retained eligibility evidence; it is not a correctness oracle.
4. **Unknown correlation** — distinct models/runtime paths/foundation-lineage labels reduce some obvious correlation but do not prove training or reasoning independence.
5. **Source/evidence truth** — claim coverage inventories identify truth-bearers; they do not themselves prove those truth-bearers are factually correct. Evidence correspondence remains a separate control.
6. **External immutability** — in-memory reference qualification/coverage registries and SQLite session evidence are not external WORM systems.
7. **Low-level library enforcement** — direct construction of lower-level components can omit optional controls. The `ReviewEngineApp` governed product boundary is the assurance surface described here.

## Next attack surface

The next meaningful trust boundary is **runtime/admission provenance**: connect extractor execution to authenticated platform-issued work identity so the retained inventory can be bound to the exact artifact, task/risk envelope and qualified deployment that actually performed extraction. Until a provider/runtime attestation mechanism exists, this should be represented as an integration boundary rather than simulated with self-reported model labels.
