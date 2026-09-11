# TESTING Qualification Independent Review Closure 011

Status: FROZEN_BEFORE_REPAIR
Authority effect: NONE_EVIDENCE_ONLY
Exposed candidate SHA: `bb6c8adc3ba98b2e9b06ba65d10ef36a061b2ceb`
Exposed checker SHA: `20f58c2b7eae3f3e2940bcd55d4af97bfe3ab18f`
Prior reviewer disposition: `INSUFFICIENT_EVIDENCE`

## Objective

Falsify and repair the independent-review gaps exposed after R10 without weakening the qualification boundary. A later green result must not erase the preserved R10 review failure.

## Frozen requirements

1. **R11-01 complete checker evidence** — the next independent review packet must include the full externally executed checker chain, including `falsify_candidate.py`, `falsify_candidate_entry.py`, `falsify_candidate_r9_entry.py`, `falsify_candidate_r10_entry.py`, the isolated runner, and workflow source, all bound to the exact checker commit by path and Git blob SHA.
2. **R11-02 test closure evidence** — include the complete externally enforced candidate test blob manifest, all bridge-imported qualification test modules and their contents or independently verifiable hashes, and enough source to verify no contributing test module is omitted.
3. **R11-03 async/generator fail closed** — top-level qualification tests that are coroutine functions, async-generator functions, generator functions, or return awaitable/generator objects must not be reported PASS without execution semantics that prove their bodies ran. Unsupported shapes must fail closed.
4. **R11-04 no command-shape bypass** — candidate qualification test execution must not fall through to a less-isolated runner merely because invocation spelling differs. Any candidate-runtime Python test invocation not explicitly recognized as the governed isolated path must fail closed rather than delegate to `_original_run`.
5. **R11-05 import-surface protection** — candidate runtime must not gain import precedence over checker-owned code or the Python standard library. Shadow protection must not depend on a short hand-maintained list of eight stdlib names. The checker must use a comprehensive stdlib namespace source available from the interpreter and reject collisions or otherwise prove precedence fail-closed.
6. **R11-06 no pytest/plugin discovery path** — pytest, conftest, plugin, implicit discovery, or other candidate-controlled collection mechanisms must not contribute to external qualification unless independently pinned and explicitly governed. Unknown test-runner paths fail closed.
7. **R11-07 raw evidence package** — next review packet must include raw or faithfully embedded external regression logs, exact App check payloads, candidate/checker/root SHAs, exact run IDs, expected polarity matrix, and prior RED chronology.
8. **R11-08 exact successor lineage** — include git/PR/merge evidence showing `af3b21fc...` -> R10 repair head `af162af...` -> merged successor `bb6c8adc...`, plus any later repaired successor exact SHA. Stale prior PASS/review evidence cannot qualify a different SHA.
9. **R11-09 exact checker use-time binding evidence** — include the emitted App check payload proving `head_sha` equals the exact candidate and `external_id` equals the exact checker revision that executed the qualification workflow. This remains evidence only.
10. **R11-10 independent re-review** — after repair, fresh exact-SHA local/external evidence and a fresh independent manual review are required. No prior reviewer result may be replayed.

## Acceptance

A repaired checker must preserve existing R10-A and R10-B fail-closed attacks, preserve the non-attack control PASS, add dedicated falsification coverage for R11-03/R11-04/R11-05/R11-06, and produce a self-contained review packet sufficient for an independent reviewer to verify the claims without network access. Unknown or missing material evidence is `REQUIREMENT_UNRESOLVED` and blocks TESTING.
