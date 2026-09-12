Below are the concrete fixes required to move V4 from `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION` toward a state where EXP-ECC-1…5 may enter bounded governed impact adjudication.

## P0 — Close the direct shared-core strict bypass

The main defect is that `ecc_governance.py` still exposes:

```python
requirement_candidate=False
```

on all seven public evaluation functions. A caller can call the shared core directly with `requirement_candidate=True`, receive `evaluation_class = REQUIREMENT_CANDIDATE`, and bypass `ecc_candidate_boundary.py`, `verify_runtime_policy()`, and the V4 cross-checks.

### Fix

Remove caller-selectable strict mode from the public shared core.

Preferred design:

1. Rename current strict-capable functions to private/internal implementations:
   - `_assess_control_execution_impl`
   - `_check_declared_executable_equivalence_impl`
   - `_qualify_role_binding_impl`
   - `_authorize_power_activation_impl`
   - `_check_tool_configuration_impl`
   - `_classify_review_binding_impl`
   - `_authorize_learning_promotion_impl`

2. Keep public `ecc_governance.py` functions historical-only:
   - no `requirement_candidate` parameter;
   - always return `HISTORICAL_REFERENCE`.

3. Move strict evaluation into a private module that only `ecc_candidate_boundary.py` may import, or require an unforgeable internal capability token.

Example boundary-only call:

```python
# ecc_candidate_boundary.py
from ecc_governance_strict import evaluate_execution_candidate

def assess_control_execution_candidate(control, event, *, candidate, action_id):
    if not verify_runtime_policy():
        return _policy_failure("execution")
    result = evaluate_execution_candidate(control, event, candidate=candidate, action_id=action_id)
    if result.get("verified") and not _execution_crosscheck(...):
        return _crosscheck_failure("execution")
    result["candidate_eligible"] = True
    return result
```

Public core must not accept `requirement_candidate=True` at all.

### Required test

Add a test proving this fails or returns non-candidate-eligible:

```python
gov.assess_control_execution(
    base_control(), strict_event(),
    candidate="shaA", action_id="act1",
    requirement_candidate=True,
)
```

Expected: `TypeError`, or `CANDIDATE_STRICT_ENTRYPOINT_REMOVED`, or `evaluation_class != REQUIREMENT_CANDIDATE`. It must not return favorable strict evidence.

Do the same for all seven functions.

---

## P0 — Fix `candidate_result_eligible()`

Current gate:

```python
return isinstance(result, dict) and result.get("evaluation_class") == STRICT
```

This accepts strict-classed failures such as:

- `CANDIDATE_BOUNDARY_POLICY_INVALID`
- `CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED`

### Fix

Require both:
1. `evaluation_class == REQUIREMENT_CANDIDATE`
2. a boundary-set `candidate_eligible is True`

Only `ecc_candidate_boundary.py` should set `candidate_eligible = True`, and only after:
- runtime policy verification passes;
- the strict core result is favorable;
- the independent cross-check passes.

Example:

```python
def candidate_result_eligible(result):
    if not isinstance(result, dict):
        return False
    if result.get("evaluation_class") != STRICT:
        return False
    if result.get("candidate_eligible") is not True:
        return False
    if result.get("status") in {
        "CANDIDATE_BOUNDARY_POLICY_INVALID",
        "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED",
    }:
        return False
    return True
```

Also add per-experiment favorable status allowlists, for example:

```python
FAVORABLE = {
    "execution": {"VERIFIED", "VERIFIED_DENY"},
    "equivalence": {"EQUIVALENT"},
    "role": {"ROLE_BINDING_ELIGIBLE"},
    "activation": {"ACTIVATION_ALLOWED"},
    "config": {"TOOL_CONFIG_CURRENT"},
    "review": {"REVIEW_BINDING_VALID"},
    "learning": {"LEARNING_PROPOSAL_REFERENCE_ELIGIBLE"},
}
```

Do not let `candidate_result_eligible()` accept a bare strict class.

---

## P0 — Make the candidate boundary mandatory, not optional

The V4 claim is that new candidate evaluation is no longer caller-selectable. That is not yet true.

### Fix

Use one of these structural options:

### Option A — Private strict module
- `ecc_governance.py` = historical only.
- `ecc_governance_strict.py` = strict internals, not part of public API.
- `ecc_candidate_boundary.py` = only public candidate path.
- No public function accepts `requirement_candidate`.

### Option B — Capability token
- Strict core functions require a private token object.
- Only `ecc_candidate_boundary.py` can construct that token.
- Direct callers cannot obtain or forge the token.

Option A is simpler and easier to review. Option B is acceptable only if the token is genuinely unforgeable and not importable by callers.

### Required test

Attempt every possible bypass:

- direct core call with `requirement_candidate=True`;
- alias function;
- `functools.partial`;
- wrapper that forwards the flag;
- monkeypatched `ecc_governance`;
- serialization layer that reconstructs the flag;
- import shadowing.

All must fail to produce `candidate_eligible=True`.

---

## P0 — Strengthen `verify_runtime_policy()`

Current manifest verification checks disk file hashes. That is not enough.

### Fix

At minimum:

1. Verify the imported module identity:
   ```python
   import ecc_governance as gov
   assert Path(gov.__file__).resolve() == expected_core_path
   ```
2. Verify `ecc_candidate_boundary.__file__` matches the manifest.
3. Verify the module object in `sys.modules` is the same object that was hash-checked.
4. Detect import shadowing: fail if `gov.__name__` or `__spec__` is unexpected.
5. Fail closed on symlinks, path replacement, or unreadable manifest.
6. Bind the manifest to an independent root/anchor. A signed manifest or V18 root-governed anchor is preferred.
7. Re-verify immediately before returning candidate-eligible evidence, not only at boundary entry.

### Required tests

- Replace `ecc_governance.py` after import; boundary must fail closed.
- Modify core, boundary, and manifest together; if no independent anchor exists, document that this is still a trust-root weakness and cannot support impact adjudication.
- Import shadowing with a malicious `ecc_governance.py` earlier on `sys.path`.
- Symlink replacement.
- TOCTOU between `verify_runtime_policy()` and evaluation.

---

## P1 — Make cross-checks actually independent

Current cross-checks are duplicate logic in the same process and accept the same caller-supplied fixture fields. A forged fixture can satisfy both the shared core and the cross-check.

### Fix at reference-mechanism level

Move cross-check logic into a separate module with:
- independently written validators;
- separate fixtures;
- no shared helper functions with the core;
- a separate trust-root simulation.

But note: for true impact adjudication, this is still not enough. The cross-check must be derived from a different source than the caller-supplied event/config/envelope.

### Fix at live-integration level

Require independent platform evidence:
- signed platform receipt;
- platform registry lookup;
- live execution log;
- authority service response;
- config attestation service response.

If the cross-check accepts the same caller-supplied booleans, it is not independent.

### Required tests

- Forge a fixture that satisfies both core and cross-check. It must still be rejected if independent evidence is missing.
- Monkeypatch the cross-check function itself. Boundary must fail closed.
- Replace the independent cross-check module. Boundary must fail closed.

---

## P1 — Per-experiment fixes

### EXP-ECC-1 — Enforcement Execution Attestation

**Required fixes:**
- Remove caller-supplied `attestation_valid` as sufficient proof.
- Require a signed platform enforcement-point receipt bound to `candidate`, `action_id`, control digest, invocation ID, process identity, and sequence.
- Cross-check against an independent platform log, not the same event dict.
- Add TOCTOU test between receipt verification and action execution.
- Add process replacement test after verification.

**Still required for impact adjudication:** live platform attestation and TOCTOU-resistant execution binding.

### EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence

**Required fixes:**
- Remove caller-supplied `machine_verified=True` as sufficient proof.
- Require executable profile from runtime extraction or an independent scanner.
- Cross-check discovered paths with a second independent extraction method.
- Reject declared-only profiles categorically.
- Add undocumented disable flag and multi-path enforcement tests at live level.

**Still required:** live executable extraction and complete production path discovery.

### EXP-ECC-3 — Qualified Harness Capability Envelope

**Required fixes:**
- Replace `identity_attested=True` and `identity_attestation_source="PLATFORM_HARNESS_REGISTRY"` with a signed registry attestation.
- Require `runtime_identity_digest` from the platform registry, not the caller.
- Bind qualification to registry sequence and version.
- Add gateway/harness identity spoofing tests.
- Keep R1/R2/R3 provider-neutral.

**Still required:** live harness-registry attestation.

### EXP-ECC-4 — Capability / Power-Surface Activation Consent

**Required fixes:**
- Replace caller-supplied `principal_authenticated` and `authority_grant_valid` with platform-issued authority evidence.
- Require signed approval object bound to manifest digest, project ID, role, powers, resources, sequence, and expiry.
- Require current revocation check against an authoritative revocation source.
- Add cross-project replay, revocation race, and scope-widening-after-approval tests.

**Still required:** platform-issued authority, revocation, and sequence evidence.

### EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift

**Required fixes:**
- Replace caller-supplied `config_attestation_valid=True` with cryptographic config attestation from a platform registry.
- On unreadable config: return `TOOL_CONFIG_UNKNOWN` or `TOOL_CONFIG_ATTESTATION_REQUIRED`; never treat as unchanged.
- Pin resolved endpoint identity and check DNS/rebinding.
- Fix secret-redaction collision: compare secret fingerprints from attestation, not redacted strings.
- Add canonical/semantic digest collision tests.

**Still required:** live cryptographic config attestation, unreadable-config handling, DNS/rebinding resistance.

### EXP-ECC-6 — External Review Egress + Provider-Relationship Binding

**Required fixes:**
- Keep deferred.
- Remove self-asserted provider/manual attestation as sufficient.
- Require real provider/gateway identity attestation.
- Require authenticated manual-review principal evidence.
- Keep AI review at zero manual-threshold credit.
- Do not allow direct core strict calls to produce manual threshold contribution.

**Still required:** live provider identity, gateway route attestation, authenticated manual review transport.

### EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary

**Required fixes:**
- Keep deferred.
- Integrate with the governed claim/dependency/retraction pipeline.
- Ensure strict candidate promotion remains `promotable=false`.
- Ensure downstream consumers cannot treat `LEARNING_PROPOSAL_REFERENCE_ELIGIBLE` as authority.
- Add retraction traversal and stale learned artifact injection tests.

**Still required:** live claim/dependency/retraction pipeline integration and promotion-boundary evidence.

---

## P1 — Tests to add immediately

Reference-mechanism tests:

1. Direct strict core call for all seven functions must not produce candidate-eligible evidence.
2. `candidate_result_eligible()` rejects `CANDIDATE_BOUNDARY_POLICY_INVALID`.
3. `candidate_result_eligible()` rejects `CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED`.
4. `candidate_result_eligible()` rejects strict-classed non-favorable statuses.
5. Downstream consumer ignores `evaluation_class`; it must not get authority.
6. Alias, wrapper, adapter, `functools.partial`, serialization layer cannot forward `requirement_candidate=True`.
7. Monkeypatch `gov`, `ecc_candidate_boundary`, `verify_runtime_policy`, or cross-check functions; boundary must fail closed.
8. Import shadowing with malicious `ecc_governance.py`.
9. Manifest mismatch, symlink, path replacement, TOCTOU.
10. Forged fixture satisfies core and cross-check; still rejected without independent source.

Live-integration tests remain required for all EXP-ECC-1…7 as listed in the review.

---

## P2 — Documentation and authority fixes

Update the V4 ledger to state clearly:

- the mandatory candidate boundary is **not yet mandatory**;
- direct shared-core strict calls remain possible;
- `candidate_result_eligible()` currently accepts strict-classed failures;
- EXP-ECC-1…5 remain `NARROWING_STILL_REQUIRED`;
- EXP-ECC-6…7 remain `DEFER_PENDING_INTEGRATION_EVIDENCE`;
- V4 is not frozen for impact adjudication.

Do not claim:
- production readiness;
- live attestation;
- qualifying manual review;
- requirement adoption;
- authority effect beyond evidence-only.

---

## Minimum acceptable fix set

To move EXP-ECC-1…5 to `READY_FOR_BOUNDED_IMPACT_ADJUDICATION`, the minimum is:

1. Public shared core no longer accepts `requirement_candidate=True`.
2. `ecc_candidate_boundary.py` is the only path to strict candidate evidence.
3. `candidate_result_eligible()` checks `candidate_eligible is True` and favorable status.
4. `verify_runtime_policy()` verifies imported module identity, not just disk hashes.
5. Cross-checks use a separate trust source, not the same caller-supplied fixture.
6. New bypass tests fail closed.
7. Live-integration gaps remain explicitly deferred.

Until then, the correct disposition remains:

`CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`