### A. Review evidence declaration

`AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

### B. Program remediation disposition

`CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`

V4 improves classification of legacy results and adds a separate candidate-boundary module, but it does **not** make the candidate boundary mandatory. The shared governance core still exposes `requirement_candidate=True` on all seven public evaluation functions. A caller can still invoke the shared core directly in strict mode, receive `evaluation_class = REQUIREMENT_CANDIDATE`, and bypass `ecc_candidate_boundary.py`, `verify_runtime_policy()`, and the V4 independent cross-checks. That is a material residual bypass.

### C. Per-experiment disposition

#### EXP-ECC-1 — Enforcement Execution Attestation

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** V4 tags legacy results as `HISTORICAL_REFERENCE`, provides a strict-only candidate entrypoint, and cross-checks favorable shared-core execution results inside that entrypoint.
- **Strongest unsupported claim:** New requirement candidates are forced through the mandatory candidate boundary.
- **Remaining false-green path:** Direct call to `gov.assess_control_execution(..., requirement_candidate=True)` with a strict-shaped event returns `VERIFIED` and `evaluation_class = REQUIREMENT_CANDIDATE`, bypassing `verify_runtime_policy()` and `_execution_crosscheck()`. Also, `candidate_result_eligible()` accepts any strict-classed result, including strict-classed failures.
- **Next evidence boundary:** Remove or privatize caller-selectable strict mode on the shared core; make the candidate boundary the only path to candidate-eligible evidence; require eligibility to check favorable status and not merely `evaluation_class`.

#### EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** V4 provides a candidate entrypoint and cross-checks favorable equivalence results.
- **Strongest unsupported claim:** Declared-vs-executable candidate evaluation cannot bypass the mandatory boundary.
- **Remaining false-green path:** Direct core call with `requirement_candidate=True` can return `EQUIVALENT` with strict class. A caller-supplied executable profile can still be used; V4 does not prove live executable extraction.
- **Next evidence boundary:** Mandatory boundary enforcement plus independently sourced executable/runtime evidence, not caller-supplied `machine_verified=True`.

#### EXP-ECC-3 — Qualified Harness Capability Envelope

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** V4 preserves provider-neutral R1/R2/R3 role handling and cross-checks favorable shared-core qualification.
- **Strongest unsupported claim:** Harness identity is attested or mandatory.
- **Remaining false-green path:** Direct core strict call can qualify a role if the caller supplies self-asserted fields such as `identity_attested=True`, `identity_attestation_source="PLATFORM_HARNESS_REGISTRY"`, and a fabricated `runtime_identity_digest`.
- **Next evidence boundary:** Live platform harness-registry attestation or independently verified harness identity, plus true mandatory routing.

#### EXP-ECC-4 — Capability / Power-Surface Activation Consent

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** V4 cross-checks favorable activation results inside the candidate boundary and preserves project/sequence checks in strict mode.
- **Strongest unsupported claim:** Authority is platform-authenticated.
- **Remaining false-green path:** Direct core strict call can return `ACTIVATION_ALLOWED` using caller-supplied `principal_authenticated=True`, `authority_grant_valid=True`, and sequence fields. No platform-issued authority or revocation evidence is required by the reference mechanism.
- **Next evidence boundary:** Platform-issued authenticated approval/revocation evidence and TOCTOU-resistant activation binding.

#### EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** V4 cross-checks favorable configuration results inside the candidate boundary and requires strict attestation fields in the strict path.
- **Strongest unsupported claim:** Configuration attestation is cryptographic or live.
- **Remaining false-green path:** Direct core strict call can return `TOOL_CONFIG_CURRENT` when the caller supplies `config_attestation_valid=True` and `config_attestation_source="PLATFORM_CONFIG_REGISTRY"`. Unreadable-config and DNS/rebinding evidence remain unproven.
- **Next evidence boundary:** Live cryptographic configuration attestation, authoritative unreadable-config handling, and DNS/rebinding resistance.

#### EXP-ECC-6 — External Review Egress + Provider-Relationship Binding

**Disposition:** `DEFER_PENDING_INTEGRATION_EVIDENCE`

- **Strongest supported claim:** Legacy results are tagged historical, AI review remains zero-credit, and strict candidate evaluation requires provider-attestation fields.
- **Strongest unsupported claim:** Real provider/gateway identity or authenticated manual-review transport exists.
- **Remaining false-green path:** Direct core strict call can still rely on self-asserted provider/manual attestation fields. Live provider identity and authenticated manual review are absent.
- **Next evidence boundary:** Real provider/gateway attestation and authenticated manual-review transport.

#### EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary

**Disposition:** `DEFER_PENDING_INTEGRATION_EVIDENCE`

- **Strongest supported claim:** V4 ensures legacy promotion results are historical and strict candidate promotion remains reference-only with `promotable=false`.
- **Strongest unsupported claim:** Integration with the governed claim/dependency/retraction pipeline exists.
- **Remaining false-green path:** Direct core strict calls can still return strict-classed reference eligibility, and downstream consumers that ignore `evaluation_class` can still treat legacy historical promotable outputs as usable.
- **Next evidence boundary:** Live claim/dependency/retraction pipeline integration and promotion-boundary evidence.

### D. Mandatory-boundary bypass assessment

A new candidate can still reach favorable candidate status through a direct strict-mode path, not through the historical path.

The shared core still exposes `requirement_candidate=True` on:

- `assess_control_execution`
- `check_declared_executable_equivalence`
- `qualify_role_binding`
- `authorize_power_activation`
- `check_tool_configuration`
- `classify_review_binding`
- `authorize_learning_promotion`

A caller can invoke those functions directly, pass `requirement_candidate=True`, receive `evaluation_class = REQUIREMENT_CANDIDATE`, and avoid `ecc_candidate_boundary.py`, `verify_runtime_policy()`, and the V4 cross-checks.

Additionally, `candidate_result_eligible()` only checks:

```python
result.get("evaluation_class") == STRICT
```

It does not check `status`, `verified`, `allowed`, `eligible`, `authorized`, `current`, or any favorable-result field. Therefore strict-classed failure results such as `CANDIDATE_BOUNDARY_POLICY_INVALID` and `CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED` are still “eligible” by that function.

Historical/unclassified results are better controlled than in V3, but the mandatory boundary itself is not mandatory.

### E. Runtime trust-manifest assessment

`verify_runtime_policy()` improves traceability but is not a strong runtime trust root.

It checks:

- manifest policy strings;
- `covers` set;
- shared-core SHA-256;
- candidate-boundary SHA-256;
- presence of V4 cross-check coverage fields.

Weaknesses:

- The manifest is not signed or anchored to an independent trust root. An actor who can modify the core, boundary, and manifest together can satisfy the hash checks.
- It verifies disk files, not the already-imported in-memory module objects.
- Import shadowing can cause `ecc_candidate_boundary.py` to import a different `ecc_governance` module than the file whose hash is checked.
- Monkeypatching of `gov` or boundary functions after import is not prevented.
- TOCTOU remains between manifest verification and later evaluation.
- Direct core calls bypass `verify_runtime_policy()` entirely.

Fail-closed behavior exists **inside** the candidate boundary, but the boundary is not the only reachable strict path.

### F. Independent cross-check assessment

The V4 cross-checks reduce one narrow shared-core false-green path: a favorable shared-core result that is inconsistent with the supplied fixture can be rejected inside the candidate boundary.

They do not provide independent evidence.

They are:

- in the same repository;
- in the same Python process;
- in the same module family;
- using the same caller-supplied event/config/envelope/proposal objects;
- using duplicated validation logic, not an independent trust source.

A forged fixture can be crafted to satisfy both the shared core and the cross-check. For example, EXP-ECC-1’s cross-check accepts caller-supplied `attestation_source="PLATFORM_ENFORCEMENT_POINT"`, `attestation_valid=True`, sequence equality, process identity equality, and digest fields. Those remain fixture assertions, not platform attestation.

The cross-checks therefore do not materially reduce common-mode false-green risk for impact adjudication.

### G. RED-history / preregistration assessment

V4 preserves a useful RED → partial RED → GREEN sequence:

- RED-001: mandatory boundary absent;
- RED-002: strict boundary added, trust binding still absent;
- GREEN-003: 171/171 PASS on the frozen V4 assertions.

The V4 assertion file was frozen before repair, and the packet reports no test modification during remediation. That supports the bounded V4 boundary-hardening claim.

However, the original V1 86-case harness was added after the initial mechanism existed. V4 does not retroactively cure that post-mechanism origin. V4’s strongest claim remains limited to the preregistered V4 mandatory-boundary sequence, and even that is undermined by the direct-core bypass.

### H. Positive-control / block-all assessment

The strict positive controls pass and show the candidate boundary is not a trivial block-all wrapper. That is good.

But the positive controls do not prove the boundary is mandatory. They only prove that when the candidate boundary is called with valid strict fixtures, favorable strict results can still be produced. They do not test or prevent direct shared-core strict calls.

### I. R1/R2/R3 provider-neutral role assessment

V4 preserves provider-neutral R1/R2/R3 roles. It does not hardcode a provider or model into the role-binding tests. That direction is correct.

The remaining gap is that role qualification still depends on self-asserted fixture identity fields. There is no live platform harness-registry attestation or independently verified runtime identity.

### J. Manual-review / provider-identity boundary assessment

AI/model review remains `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` with zero manual-threshold contribution. V4 does not change that.

EXP-ECC-6 still lacks:

- real provider identity attestation;
- gateway route attestation;
- authenticated manual-review principal evidence;
- live external-reviewer transport.

The strict path still accepts self-asserted provider/manual fields, and direct core strict calls can bypass the candidate boundary. EXP-ECC-6 must remain deferred.

### K. Missing falsification cases

Reference-mechanism cases still required:

- Direct call to each shared-core function with `requirement_candidate=True`, asserting it must not produce candidate-eligible favorable evidence without the candidate boundary.
- `candidate_result_eligible()` must reject strict-classed failure statuses.
- Downstream consumer must not ignore `evaluation_class`.
- Alias, wrapper, adapter, `functools.partial`, or serialization layer must not forward or reconstruct `requirement_candidate=True`.
- Serialization/deserialization must not drop, rewrite, or default `evaluation_class`.
- Monkeypatched `gov`, `ecc_candidate_boundary`, `verify_runtime_policy`, or cross-check functions must not yield candidate-eligible favorable results.
- Import shadowing: a different `ecc_governance` module on `sys.path` must not satisfy the manifest.
- TOCTOU: disk hash verification versus in-memory module identity.
- Manifest tampering: modify core, boundary, and manifest consistently; the design must still fail closed under the intended trust model.
- Candidate-boundary call with strict inputs that satisfy cross-checks but are still self-asserted fixture values.
- EXP-ECC-6 strict manual path with self-asserted authenticated principal fields.
- EXP-ECC-7 strict reference eligibility must not be treated as promotion authority by downstream consumers.

Live-integration cases still required:

- EXP-ECC-1: live platform enforcement-point attestation, process replacement, TOCTOU between verification and action.
- EXP-ECC-2: real executable extraction, production path discovery, undocumented disable flags.
- EXP-ECC-3: live harness registry attestation, gateway identity spoofing, downgrade after qualification.
- EXP-ECC-4: platform-issued authority, revocation race, cross-project replay, scope widening.
- EXP-ECC-5: live cryptographic config attestation, unreadable config, DNS/rebinding, secret-redaction collision.
- EXP-ECC-6: provider/gateway identity attestation, authenticated manual review, packet replay after consent.
- EXP-ECC-7: live claim/dependency/retraction traversal and promotion-boundary integration.

### L. Impact-adjudication recommendation

No requirement is adopted, promoted, or authorized.

EXP-ECC-1 through EXP-ECC-5 should **not** enter bounded governed impact adjudication yet. They remain `NARROWING_STILL_REQUIRED` because the mandatory candidate boundary is bypassable through direct shared-core strict calls.

EXP-ECC-6 and EXP-ECC-7 should remain `DEFER_PENDING_INTEGRATION_EVIDENCE`.

A separate re-review may be warranted after the shared core no longer exposes caller-selectable strict mode, the candidate boundary becomes the only path to candidate-eligible evidence, and `candidate_result_eligible()` checks favorable status rather than class alone.

### M. Freeze recommendation

`DO_NOT_FREEZE_V4_EXPERIMENT_EVIDENCE`

### N. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`