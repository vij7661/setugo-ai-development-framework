## A. Review evidence declaration

`AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

## B. Program remediation disposition

`CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`

V3 materially improves the strict reference path: when `requirement_candidate=True` is passed, EXP-ECC-1 through EXP-ECC-5 fail closed on omitted attestation/authentication/governance fields, and EXP-ECC-6/EXP-ECC-7 prevent several legacy credit/promotion paths. The RED-001 → RED-002 → GREEN-003 history is also preserved and externally checkable.

However, V3 does not close the core V2 omission-based false-green at the reference-mechanism boundary. `requirement_candidate` is an optional keyword defaulting to `False`. A new requirement candidate can still be evaluated through the historical permissive path if the caller omits the flag. The trust manifest declares `candidate_path_policy = MANDATORY_STRICT_EVALUATION`, but the shared functions do not consult or enforce the manifest. The manifest is checked by the V3 test, not by the runtime mechanism. Therefore V3 remains a strict-mode hardening, not a mandatory-strict boundary.

## C. Per-experiment disposition

### EXP-ECC-1 — Enforcement Execution Attestation

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** In `requirement_candidate=True` mode, platform enforcement-point attestation, action-sequence binding, and process identity are mandatory; omission fails closed.
- **Strongest unsupported claim:** New requirement candidates are forced into strict mode. They are not; the default path remains permissive.
- **Remaining false-green path:** Call `assess_control_execution(..., requirement_candidate=False)` or omit the flag with a legacy-shaped event. The legacy path can return `VERIFIED` without platform attestation, sequence binding, or process identity.
- **Next evidence boundary:** A mandatory higher-level API or separate strict-only entrypoint that cannot fall back to legacy behavior for new candidates.

### EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** In strict mode, `machine_verified`, runtime fields, and nonempty verified execution paths are required.
- **Strongest unsupported claim:** The strict mode is enforced for all new requirement candidates. It is only enforced when the flag is supplied.
- **Remaining false-green path:** Omit `requirement_candidate=True`; pass a declared contract dictionary as the executable profile with no machine-derived runtime evidence. The legacy path can return `EQUIVALENT`.
- **Next evidence boundary:** Mandatory strict API; real executable/runtime extraction or independent verification rather than caller-supplied `machine_verified=True`.

### EXP-ECC-3 — Qualified Harness Capability Envelope

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** Strict mode requires identity attestation fields, platform registry source, runtime identity digest, and per-capability dictionaries.
- **Strongest unsupported claim:** Harness identity is actually attested. Strict mode accepts self-asserted booleans/strings such as `identity_attested=True` and `identity_attestation_source="PLATFORM_HARNESS_REGISTRY"`.
- **Remaining false-green path:** Omit the strict flag and use a legacy string requirement or legacy envelope; the permissive path can qualify a role without mandatory per-capability allowed sets.
- **Next evidence boundary:** Mandatory strict API plus live platform harness identity attestation or independent qualification evidence.

### EXP-ECC-4 — Capability / Power-Surface Activation Consent

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** Strict mode requires `principal_authenticated`, `authority_grant_valid`, `project_id`, and approval/current-sequence binding.
- **Strongest unsupported claim:** Authority is platform-authenticated. The strict path still trusts caller-supplied booleans and sequence fields.
- **Remaining false-green path:** Omit the strict flag; supply a legacy approval with `approved=True`, matching manifest digest/role/powers/resources, and no authenticated principal or authority-grant fields. Legacy activation can return `ACTIVATION_ALLOWED`.
- **Next evidence boundary:** Mandatory strict API; platform-issued authenticated activation record; real revocation/TOCTOU semantics.

### EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** Strict mode requires secret-safe configuration material, credential attestation, resolved endpoint evidence, and platform configuration attestation fields.
- **Strongest unsupported claim:** The attestation is cryptographic or live. Strict mode still accepts caller-declared `config_attestation_valid=True` and `config_attestation_source="PLATFORM_CONFIG_REGISTRY"`.
- **Remaining false-green path:** Omit the strict flag and use legacy fields such as `credential_profile` and `canonical_digest`. The legacy comparison can return `TOOL_CONFIG_CURRENT`.
- **Next evidence boundary:** Mandatory strict API; live cryptographic configuration attestation; explicit `UNKNOWN` on unreadable config; DNS/rebinding resistance.

### EXP-ECC-6 — External Review Egress + Provider-Relationship Binding

**Disposition:** `DEFER_PENDING_INTEGRATION_EVIDENCE`

- **Strongest supported claim:** In strict mode, omitted provider attestation prevents `SAME_PROVIDER_CONFIRMED`, and omitted manual-principal authentication prevents manual threshold credit.
- **Strongest unsupported claim:** Real provider/gateway identity or authenticated manual review exists.
- **Remaining false-green path:** Omit the strict flag; the legacy manual path can still return threshold contribution `1` when `manual_attestation_principal_authenticated` is omitted.
- **Next evidence boundary:** Real provider/gateway identity attestation and authenticated manual-review attestation; keep outside impact adjudication until integration evidence exists.

### EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary

**Disposition:** `DEFER_PENDING_INTEGRATION_EVIDENCE`

- **Strongest supported claim:** In strict mode, self-asserted promotion flags fail closed, and even fully supported reference evidence is capped at `LEARNING_PROPOSAL_REFERENCE_ELIGIBLE` with `promotable=false`.
- **Strongest unsupported claim:** Integration with the governed claim/dependency/retraction pipeline exists.
- **Remaining false-green path:** Omit the strict flag; legacy self-asserted promotion flags can still produce `LEARNING_PROPOSAL_PROMOTABLE`.
- **Next evidence boundary:** Actual claim/dependency/retraction pipeline integration and live promotion-boundary evidence.

## D. Strict-vs-historical mode assessment

A caller can accidentally or maliciously route a new requirement candidate through historical compatibility mode by omitting `requirement_candidate=True`.

The V3 mechanism does not enforce strict mode. The flag is optional and defaults to `False`. The trust manifest declares historical paths as `HISTORICAL_REFERENCE_ONLY`, but the functions do not read the manifest and do not reject legacy calls based on caller intent or candidate status. There is no separate strict-only module, no mandatory wrapper, and no API boundary that prevents a new candidate from being evaluated through the legacy path.

Therefore the omission-based false-green is only closed for callers that voluntarily pass the strict flag. It is not closed at the reference-mechanism level.

## E. Shared-module coupling / trust-manifest assessment

The shared `ecc_governance.py` coupling remains a trust-boundary weakness.

The V3 trust manifest binds the module SHA-256 and Git blob, declares coverage of EXP-ECC-1 through EXP-ECC-7, and states the intended legacy/candidate policies. That is useful for review traceability, but it does not create independent implementations or independent falsification paths. A single faulty shared abstraction, status convention, or fallback branch can still make multiple experiments appear green.

The manifest is also not runtime-enforced. It is checked by the V3 test, but the production/reference functions do not consult it. For bounded impact adjudication, the shared module should either be independently cross-checked or the critical experiments should have independent reference implementations.

## F. Preregistration and RED-history assessment

V3 preserves a good RED→GREEN sequence:

- Frozen V3 tests before repair: `4012eb6082aaeb3cd79bda77b77a892cbc05a375`
- RED-001: `153 tests; 18 failures + 3 errors`
- Mechanism repair: `1bf710e6f9825d264ef7f355f72f9c98d2f96376`
- RED-002: `153 tests; 152 PASS; 1 failure` — missing trust-boundary manifest
- Trust manifest added
- GREEN-003: `153/153 PASS`
- Frozen V3 ledger closure: `351f08c7f5236f73bec37f62ec53085af48d15c7`, `153/153 PASS`

This is materially better than V2. The V3 omission-hardening assertions are frozen pre-repair.

However, the original V1 86-case full-coverage harness was still added after the first mechanism existed. That does not erase the V3-specific preregistration, but it continues to limit broad claims about the original experiment family. V3 can support narrow strict-mode hardening claims; it cannot by itself retroactively cure the original post-mechanism coverage origin.

## G. Positive-control / block-all assessment

Positive controls are present for the strict branches:

- EXP-ECC-1: strict valid receipt is `VERIFIED`
- EXP-ECC-2: strict machine profile can be `EQUIVALENT`
- EXP-ECC-3: strict provider-neutral binding is `ROLE_BINDING_ELIGIBLE`
- EXP-ECC-4: strict activation is `ACTIVATION_ALLOWED`
- EXP-ECC-5: strict attested config can be `TOOL_CONFIG_CURRENT`
- EXP-ECC-6: strict provider binding still has zero AI credit
- EXP-ECC-7: strict governance evidence remains reference-only with `promotable=false`

These are sufficient to reject a trivial block-all implementation inside strict mode. They are not sufficient to prove that strict mode is mandatory for new candidates.

## H. R1/R2/R3 provider-neutral role assessment

V3 preserves provider-neutral governed roles. The strict test for EXP-ECC-3 accepts `user-selected-qualified-model` and does not hardcode a provider or model into R1/R2/R3. That is directionally correct.

The remaining gap is that role qualification still depends on self-asserted envelope data. `identity_attested=True` and `identity_attestation_source="PLATFORM_HARNESS_REGISTRY"` are strings/booleans supplied by the caller. There is no live harness registry attestation or independent qualification evidence. Current evidence remains fixture-level.

## I. Manual-review/provider-identity boundary assessment

The AI-generated review evidence class remains `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` with zero manual-review threshold contribution.

In strict mode, EXP-ECC-6 prevents provider-relationship confirmation without provider attestation and prevents manual threshold credit without authenticated manual-principal evidence. That is an improvement.

The boundary is still incomplete because:

- legacy mode can return manual threshold contribution `1` when the strict flag is omitted;
- real provider identity and gateway route attestation are absent;
- authenticated manual-review attestation is absent;
- the testing policy remains manual-only, and no live external reviewer transport is proven.

Therefore EXP-ECC-6 should remain deferred.

## J. Missing falsification cases

Additional cases should include:

- Omitting `requirement_candidate=True` for every EXP-ECC-1 through EXP-ECC-7 strict branch.
- Calling the shared functions directly through a legacy wrapper that defaults to `requirement_candidate=False`.
- Cross-mode confusion where a candidate object is marked strict in metadata but evaluated through legacy code.
- A higher-level API that fails to forward the strict flag.
- Monkeypatching, serialization, or adapter layers that drop `requirement_candidate=True`.
- Trust-manifest mismatch where the manifest says mandatory strict but the runtime path still permits legacy calls.
- Alias functions or alternate entrypoints that bypass the strict branch.
- Shared-module correlated false-green across multiple experiments.
- EXP-ECC-1: spoofed platform attestation string, process replacement after verification, TOCTOU between verification and action.
- EXP-ECC-2: real fail-open wrapper, undocumented disable flag, multi-path enforcement.
- EXP-ECC-3: gateway/harness identity spoofing, downgrade after qualification.
- EXP-ECC-4: forged principal flags, cross-project replay, revocation race, scope widening after approval.
- EXP-ECC-5: canonical/semantic digest collision, secret-redaction collision, DNS/endpoint rebinding, config read failure.
- EXP-ECC-6: provider identity spoofing, gateway route attestation failure, forged manual attestation, packet replay after consent.
- EXP-ECC-7: retraction dependency traversal, stale learned artifact injected into a new session.

## K. Impact-adjudication recommendation

No candidate should be promoted by this review.

In the current V3 state, EXP-ECC-1 through EXP-ECC-5 should not yet enter bounded governed impact adjudication because the mandatory-strict boundary is not enforced. They remain narrowed reference-mechanism candidates, but they require a strict-only API or equivalent runtime enforcement before impact adjudication.

EXP-ECC-6 and EXP-ECC-7 should remain outside impact adjudication pending live integration evidence.

No requirement is adopted, promoted, or authorized.

## L. Freeze recommendation

`DO_NOT_FREEZE_V3_EXPERIMENT_EVIDENCE`

## M. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
