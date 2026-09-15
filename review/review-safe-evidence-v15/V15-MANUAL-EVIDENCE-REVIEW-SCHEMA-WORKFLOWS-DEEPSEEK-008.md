# V15 Manual Evidence Review — Schema Registry + Workflows — DeepSeek Handoff 008

`REVIEWER_TRANSITION = CLAUDE_TO_DEEPSEEK_QUOTA_EXHAUSTION`

`SURFACE_REVIEWED = V15_SCHEMA_REGISTRY_AND_WORKFLOWS`

`SURFACE_COVERAGE = COMPLETE`

`V15_EXISTING_CRITICAL = CONFIRMED`

This record preserves the manually relayed DeepSeek review of the final planned V15 schema-registry/workflow surface. It is engineering evidence only and does not by itself establish authenticated reviewer provenance or authority.

## New Critical findings

1. **Canonical schema registry is metadata-only, not machine-enforceable.** The registry contains required-field arrays and prose rules, while the construction workflow merely parses JSON and checks schema version, authority posture, schema count, and fenced-token `single_use`. It does not validate emitted records against types, enums, additional-property rules, canonical serialization, authentication/provenance, foreign-key bindings, generation/snapshot/currentness bindings, role resolution, or cross-field invariants. False-green: registry CI prints `V15_CANONICAL_SCHEMA_REGISTRY=PASS` while runtime validators accept records not actually constrained by a canonical schema system. Narrow repair: replace metadata arrays with executable schemas/validators and negative CI coverage for every required/conditional invariant.

2. **`workflow_dispatch` is unbound to the frozen candidate.** All V15 workflows permit manual dispatch, checkout the selected ref, echo commit/tree, but do not compare them to frozen candidate `380e1d9db083a6477691bf187d5cba7c61eee280` / tree `6bdd7bf8ec214e406383e084bd7c28b8c9738ee9` before readiness output. False-green: run effects workflow on another ref and still obtain `NEXT_ACTION=FREEZE_EXACT_CANDIDATE_BUILD_EVIDENCE_PACKAGE_MANUAL_INDEPENDENT_EVIDENCE_REVIEW`. Narrow repair: require and verify expected commit/tree and emit readiness only after exact binding.

3. **Path filters permit stale-green dependent workflows.** Slice workflows generally watch only their own slice/test/workflow paths and omit shared core `review_safe_evidence_v15.py`, schema registry, standards, helpers, package builders, and earlier load-bearing slices. False-green: a shared dependency changes while dependent slice workflows retain previous green results. Narrow repair: central dependency graph/path set so every affected suite reruns.

4. **PASS / `33/33_IMPLEMENTED` / stopping-rule / readiness statements are hardcoded outputs rather than derived evidence.** Workflows echo these states after unit tests without a stable mandatory-test manifest proving all required adversarial test IDs executed and passed. Narrow repair: machine-readable test manifest/result parsing, stable IDs, fail on missing/skipped tests, derive all counts/readiness from evidence.

5. **Historical RED records are not required, discovered, or bound before stopping/readiness output.** No V15 construction workflow gates its boundary on RED-history completeness/digests. False-green: stopping boundary can be emitted with absent/stale failure history. Narrow repair: RED registry/evidence completeness and digest binding as a prerequisite.

## New High findings

1. **GitHub Actions/toolchain identities are mutable.** `actions/checkout@v4`, `actions/setup-python@v5`, `ubuntu-latest`, and generic `3.12` are not immutable identities. Repair: pin action SHAs and runtime/container/toolchain identities.
2. **Shallow checkout (`fetch-depth: 1`) prevents lineage/history validation.** Repair: fetch sufficient/full history and explicitly verify ancestry/history.
3. **Schema registry/record conformance is not validated across all workflows.** Repair: bind schema digest/version into every slice and validate representative/actual records.
4. **Conditional schema rules remain prose, not machine-enforced.** Examples include blocker resolution, reviewer positive-disposition coverage, and independence-result requirements. Repair: executable conditional/cross-field validation.
5. **No stable-ID proof that mandatory cross-object adversarial tests executed.** Repair: mandatory test manifest + machine-readable results + fail on missing/skipped IDs.
6. **Evidence-package completeness is not verified before readiness.** Effects workflow emits the next-action handoff without first building/verifying package manifest, file set, RED history, and digests. Repair: deterministic package builder/completeness verifier gated before readiness.

## Medium / Low findings

- Registry validation is brittle (`len(schemas)==10`) rather than exact schema-ID/version/digest validation.
- Construction logs are unsigned and not machine-bound attestations; they must not be treated as authority evidence.
- Workflows lack concurrency/current-run binding, enabling stale successful runs to be mistaken for current evidence.

`SCHEMA_REGISTRY_MACHINE_ENFORCEABLE = NO`

`WORKFLOW_EVIDENCE_BOUNDARY_SOUND = NO`

`SUCCESSOR_SCOPE_FREEZE_RECOMMENDATION = DO_NOT_FREEZE`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
