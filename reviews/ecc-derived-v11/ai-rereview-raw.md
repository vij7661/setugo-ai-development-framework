REVIEW_CONTEXT = CLEAN_PACKET_ONLY_CONTEXT
EVIDENCE_DECLARATION = AI_GENERATED_ENGINEERING_FEEDBACK_ONLY

Overall disposition: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`

Per-experiment disposition:
- EXP-ECC-1: `ADOPT_REQUIREMENT_CANDIDATE`
- EXP-ECC-2: `ADOPT_REQUIREMENT_CANDIDATE`
- EXP-ECC-3: `ADOPT_REQUIREMENT_CANDIDATE`
- EXP-ECC-4: `ADOPT_REQUIREMENT_CANDIDATE`
- EXP-ECC-5: `NARROW_REQUIREMENT_CANDIDATE`
- EXP-ECC-6: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- EXP-ECC-7: `DEFER_PENDING_INTEGRATION_EVIDENCE`

## Findings

### Critical — Concrete false-green path remains for EXP-ECC-5 via untracked primitive attributes in strict config equivalence

`ecc_governance_strict._sha256_json` uses module-global `hashlib.sha256` and `json.dumps`. The V11 dependency binder in `ecc_candidate_boundary._build_runtime_policy_verifier.capture_dependency` captures `hashlib` and `json` as module-object identities, but it does **not** capture `hashlib.sha256` or `json.dumps` as exact callables for the strict entrypoints. Therefore ordinary mutation of `boundary.strict_core.hashlib.sha256` or `boundary.strict_core.json.dumps` is not detected by `dependency_globals_ok()`.

This matters because `check_tool_configuration_candidate` relies on `check_tool_configuration`, which recomputes `argv_digest` and `canonical_digest` through `_sha256_json`. The candidate-boundary independent check `_config_evidence_ok` in `_build_candidate_api` compares `tool_id`, `harness_id`, `transport`, `endpoint`, `argv_digest`, `canonical_digest`, `credential_profile_fingerprint`, and `resolved_endpoint`, but does **not** compare `permission_profile` or the actual `argv` list. A forged config with a broader `permission_profile` and different `argv` can therefore be made to present the genuine reference record’s digest fields if `hashlib.sha256` is mutated to return the expected digest.

Relevant references:
- `experiments/ecc_derived/ecc_governance_strict.py` — `_sha256_json`, `check_tool_configuration`, `_v2_config_material`
- `experiments/ecc_derived/ecc_candidate_boundary.py` — `_build_runtime_policy_verifier.capture_dependency`, `dependency_globals_ok`
- `experiments/ecc_derived/ecc_candidate_boundary.py` — `_build_candidate_api.config_evidence_ok`
- `experiments/ecc_derived/test_ecc_governance_v11_module_global_integrity.py` — no test mutates `boundary.strict_core.hashlib.sha256` or `boundary.strict_core.json.dumps`

### High — Missing negative falsification cases for transitive module-attribute mutation

V11 closes direct global rebinding and same-code/new-function substitution for named globals, but it does not test mutation of attributes on referenced module objects (`hashlib.sha256`, `json.dumps`, etc.). This is a gap in the ordinary-module V11 threat model because these attributes are reachable through transitive module globals and directly affect EXP-ECC-5’s config-digest validation.

### Medium — `_config_evidence_ok` relies on digest recomputation without comparing all semantic fields

`_config_evidence_ok` does not compare `permission_profile` or actual `argv`. This is safe only when the digest primitives and `_sha256_json` dependencies are trusted. Given the Critical finding above, this becomes a false-green enabler for EXP-ECC-5.

### Low — Supersession reasons are explicit but only in runner output

The V11 runner prints superseded tests with reasons. Historical test files are preserved and not rewritten. This is acceptable, but the evidence JSON for V11 does not itself enumerate superseded tests; the transcript does. No history rewriting detected.

## False-green path as concrete attack sequence

1. Attacker mutates `boundary.strict_core.hashlib.sha256` to a function that returns the genuine `canonical_digest`/`argv_digest` values from reference record `ECC-V5-E5-POS` for arbitrary inputs.
2. Attacker constructs a forged config `current` with the same `tool_id`, `harness_id`, `transport`, `endpoint`, `argv_digest`, `canonical_digest`, `credential_profile_fingerprint`, and `resolved_endpoint` as `ECC-V5-E5-POS`, but with a broader `permission_profile` (e.g., `write`) and different `argv`.
3. Attacker calls `check_tool_configuration_candidate(expected, current)`.
4. `check_tool_configuration` recomputes digests using the mutated `hashlib.sha256`, accepts the forged config, and returns `TOOL_CONFIG_CURRENT`.
5. `_config_evidence_ok` compares only the fields above and finds they match the genuine reference record.
6. `finish_positive` calls `runtime_verify()`. `dependency_globals_ok()` checks `hashlib` module identity, not `hashlib.sha256`, so it passes.
7. The candidate API seals the result as eligible, falsely certifying a broader permission profile.

## Missing negative and positive falsification cases

Negative cases needed:
- Mutate `boundary.strict_core.hashlib.sha256` and attempt EXP-ECC-5 config drift with broader `permission_profile`; expect `CANDIDATE_BOUNDARY_POLICY_INVALID` or non-eligible.
- Mutate `boundary.strict_core.json.dumps` and attempt the same; expect non-eligible.
- Mutate `boundary.strict_core._sha256_json` dependencies via attribute mutation; expect fail-closed.
- Confirm that `permission_profile` and actual `argv` are semantically bound, not only digest-bound.

Positive cases needed:
- Legitimate EXP-ECC-5 config path remains positive with untampered primitives.
- V11 dependency capture verifies `hashlib.sha256` and `json.dumps` as exact callables for strict entrypoints, or explicitly excludes them as nonclaims.

## Assessment of historical supersessions and RED preservation

Supersessions are explicit in the V5/V6/V7/V8/V9/V10/V11 runners with reasons. Historical test modules are preserved. RED records are retained across V3–V11. No evidence of history rewriting. The V11 RED→repair→GREEN sequence is clean and preserves prior REDs. This aspect is acceptable.

## Assessment of remaining nonclaims

Most remaining nonclaims are acceptable bounded exclusions for impact adjudication: concurrent/TOCTOU, reflective closure extraction, interpreter/native-memory compromise, repository/code-replacement authority, live attestation, independent production trust-root separation, and durable cross-process provenance. However, the exclusion of “mutation of lower-level interpreter/runtime primitives” is too broad for EXP-ECC-5 as currently written, because `hashlib.sha256` and `json.dumps` are used directly by the strict config-equivalence mechanism and are not covered by V11’s dependency binding. Either EXP-ECC-5 must be narrowed with an explicit nonclaim that those primitives are assumed untampered, or V11 must be extended to capture them before impact adjudication.

## Freeze recommendation

`DO_NOT_FREEZE`

The V11 evidence is strong for direct module-global rebinding and entrypoint identity, but the concrete false-green path in EXP-ECC-5 and the missing negative falsification for transitive module-attribute mutation prevent freezing for bounded impact adjudication.

AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY
