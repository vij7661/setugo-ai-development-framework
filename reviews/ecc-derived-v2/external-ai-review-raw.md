## A. Review evidence declaration

`AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

## B. Program remediation disposition

`CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`

V2 materially improved the remediation evidence by freezing the new executable remediation harness before mechanism repair, preserving RED history, and producing a RED-to-GREEN transition. However, the repaired reference still contains omission-based false-green paths and legacy permissive branches. Several V2 checks only activate when specific attestation/authentication fields are present. If those fields are omitted, the mechanism can fall back to the older, weaker behavior. That is not sufficient for bounded impact adjudication of requirement candidates.

## C. Per-experiment disposition

### EXP-ECC-1 — Enforcement Execution Attestation

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** The V2 reference can reject worker-self-asserted execution receipts, TOCTOU sequence mismatches, and hook-process identity mismatches when those fields are supplied.
- **Strongest unsupported claim:** It does not require platform-attested execution receipts. A caller can omit attestation, sequence, and process-identity fields and still receive `VERIFIED`.
- **Remaining false-green path:** Supply an event dictionary with correct control/version/digest, candidate/action binding, `started=True`, `result_recorded=True`, `execution_ok=True`, valid digests, and no `attestation_source`, `attestation_valid`, `verified_action_sequence`, or `process_identity`. The reference can return `VERIFIED`.
- **Next evidence boundary:** Mandatory platform-attested enforcement-point receipt schema; live hook/process invocation; authenticated process identity; TOCTOU binding to the governed action sequence.

### EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** The V2 checker rejects declared-blocking vs runtime-fail-open, hidden disable flags, generated documentation stronger than runtime, and unverified executable profiles when those machine-derived fields are supplied.
- **Strongest unsupported claim:** It still does not inspect real executable code or runtime semantics. The strict path depends on caller-supplied executable-profile fields.
- **Remaining false-green path:** Pass the declared contract dictionary as the executable profile with no `machine_verified`, no `runtime_mode`, no `runtime_on_internal_error`, no `generated_doc_mode`, no `discovered_disable_flags`, and no `paths`. The checker can return `EQUIVALENT`.
- **Next evidence boundary:** Mandatory machine-derived executable/runtime extraction; real multi-path code inspection; runtime failure injection; no legacy declared-only equivalence for new requirements.

### EXP-ECC-3 — Qualified Harness Capability Envelope

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** The V2 reference supports per-capability allowed sets, rejects unattested harness identity when explicitly marked false, detects stale qualification digests, and requires revalidation after role/binding changes when those fields are supplied.
- **Strongest unsupported claim:** Harness identity attestation is not mandatory. If `identity_attested` is omitted, the reference does not fail closed. Legacy ordinal ranking also remains available when requirements are strings rather than per-capability dictionaries.
- **Remaining false-green path:** Omit `identity_attested` or use a legacy string requirement. A self-asserted envelope can claim `NATIVE_ENFORCEMENT` without external attestation or per-capability qualification.
- **Next evidence boundary:** Mandatory attested harness/runtime identity; mandatory per-capability allowed sets; live harness qualification; downgrade and gateway-substitution detection.

### EXP-ECC-4 — Capability / Power-Surface Activation Consent

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** The V2 reference rejects forged approvers, cross-project replay, and approval-to-activation revocation races when strict activation fields are present.
- **Strongest unsupported claim:** Authenticated principal/authority/project/sequence checking is not mandatory. Legacy approval dictionaries without `principal_authenticated`, `authority_grant_valid`, or `project_id` can still activate.
- **Remaining false-green path:** Supply an approval with `approved=True`, matching `manifest_digest`, matching `role`, matching approved powers/resources, and no authenticated principal or authority-grant fields. The reference can return `ACTIVATION_ALLOWED`.
- **Next evidence boundary:** Mandatory platform-issued authenticated activation record; exact principal and authority issuance; project/sequence binding; revocation propagation; TOCTOU between approval and activation.

### EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift

**Disposition:** `NARROWING_STILL_REQUIRED`

- **Strongest supported claim:** The V2 reference recomputes secret-safe canonical identity, rejects canonical-digest forgery, credential-profile fingerprint drift, and resolved-endpoint rebinding when V2 attestation fields are supplied.
- **Strongest unsupported claim:** It does not provide cryptographic live configuration attestation. The V2 path is activated only when `argv`, `credential_profile_fingerprint`, `credential_attestation`, or `resolved_endpoint` is present. Legacy comparison remains.
- **Remaining false-green path:** Use only legacy fields such as `credential_profile` and `canonical_digest`, omit V2 attestation material, and pass matching canonical digests. The reference can return `TOOL_CONFIG_CURRENT`.
- **Next evidence boundary:** Mandatory secret-safe cryptographic configuration attestation; explicit `UNKNOWN` on unreadable config; live endpoint resolution; DNS/rebinding resistance; executable/argv provenance.

### EXP-ECC-6 — External Review Egress + Provider-Relationship Binding

**Disposition:** `DEFER_PENDING_INTEGRATION_EVIDENCE`

- **Strongest supported claim:** The V2 reference keeps AI-generated feedback at zero manual threshold contribution when manual principal authentication is explicitly absent, rejects consent-sequence replay, and marks unauthenticated cross-provider claims as `PROVIDER_IDENTITY_UNKNOWN` when attestation fields are present.
- **Strongest unsupported claim:** It does not prove real provider identity, gateway routing, external reviewer transport, or authenticated manual review. Omission of attestation fields can still allow provider-relationship classification without cryptographic proof.
- **Remaining false-green path:** Omit `provider_identity_attested` and `gateway_route_attested`, set `selected_provider == returned_provider`, and the reference can return `SAME_PROVIDER_CONFIRMED`. Legacy manual-attestation handling can also return threshold contribution `1` when `manual_attestation_principal_authenticated` is omitted.
- **Next evidence boundary:** Real provider/gateway identity attestation; authenticated manual-review attestation; disabled real transport in testing; packet replay and consent-sequence enforcement against live transport.

### EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary

**Disposition:** `DEFER_PENDING_INTEGRATION_EVIDENCE`

- **Strongest supported claim:** The V2 reference rejects self-asserted independent support and incomplete retraction traversal when V2 governance fields are present, and it blocks stale learned-artifact session injection.
- **Strongest unsupported claim:** It is not integrated with the real claim/dependency/retraction pipeline. If V2 governance fields are omitted, legacy self-asserted promotion flags can still promote.
- **Remaining false-green path:** Supply a proposal with `source_verified=True`, `independent_support=True`, `governed_approval=True`, and no `claim_governance_evidence_valid`, `dependency_graph_current`, or `retraction_traversal_complete` fields. The reference can return `LEARNING_PROPOSAL_PROMOTABLE`.
- **Next evidence boundary:** Integration with governed claim/requirement/dependency machinery; real retraction traversal; stale artifact detection across sessions; no parallel self-asserted promotion flags.

## D. Preregistration / RED-history assessment

V2 genuinely improved the sequencing discipline for the new remediation assertions. The frozen V2 executable harness commit `387a32ae3dba3b92fff28b747cd294827fdba893` was run before mechanism repair, producing `17 failures + 2 errors` on 132 tests. The repair candidate `e176df47dd1faca4eca5437095c5bc55b09e4a4d` then produced `132/132 PASS`. This is a meaningful RED-to-GREEN record.

However, this does not fully repair the original V1 sequencing criticism. The original 86-case full-coverage harness was still added after the first mechanism existed. V2 freezes and preserves additional remediation assertions, but the broader executable coverage still has post-mechanism origin. RED history is preserved, including RED-001 and the classification correction. History was not rewritten, which is positive.

## E. Shared-module coupling assessment

The seven experiments remain coupled through a shared `ecc_governance.py` implementation, shared status strings, and shared helper factories. A single faulty abstraction, status convention, or fallback branch can make multiple children appear green. V2 does not demonstrate independent implementations or independent falsification paths. This is a remaining structural weakness. At minimum, the shared module should be treated as a trust boundary requiring its own verification, or the critical experiments should have independent reference implementations.

## F. Legacy-compatibility risk assessment

The legacy compatibility paths are too permissive for future production requirements. The mechanism repeatedly falls back to older behavior when V2 fields are absent. Comments say legacy fixtures remain valid evidence of the earlier bounded reference mechanism, but the code does not clearly restrict those paths to historical-fixture compatibility only.

For new requirement candidates, legacy paths should be explicitly scoped as historical-fixture compatibility, test-only, or disabled. A production requirement must not be satisfiable by omission of mandatory attestation, authentication, or governance fields.

## G. R1/R2/R3 provider-neutral role assessment

R1/R2/R3 remain configurable governed roles rather than hardcoded providers or models. The reference does not appear to contain provider-specific role branches. That is directionally correct.

The remaining gap is that role qualification still depends heavily on self-asserted envelope data. Live role binding requires attested harness capability envelopes, exact durable binding, and revalidation on substitution. Current evidence remains fixture-level.

## H. Manual-review / provider-identity boundary assessment

The AI-generated review evidence class remains `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` with zero manual-review threshold contribution. EXP-ECC-6 correctly avoids laundering AI feedback into manual review when the principal-authentication field is explicitly false.

However, real provider identity, gateway route attestation, and authenticated manual-review attestation are still absent. The legacy manual-attestation path can return threshold contribution `1` when the principal-authentication field is omitted. That must be closed before any manual-review threshold credit could be considered. The manual-only testing rule remains intact.

## I. Missing falsification cases

Additional cases should include:

- Omission-based false-green cases for every V2 strict branch: omit attestation fields, machine-derived profile fields, identity-attestation fields, activation authority fields, V2 configuration-attestation fields, provider/gateway attestation fields, manual principal fields, and V2 governance fields.
- EXP-ECC-1: live spoofed execution receipt, TOCTOU between verification and action, hook process replacement.
- EXP-ECC-2: real fail-open wrapper, undocumented disable flag, generated documentation stronger than code, multi-path enforcement.
- EXP-ECC-3: incomparable capabilities, gateway/harness identity spoofing, downgrade after qualification.
- EXP-ECC-4: forged approval principal, cross-project consent replay, revocation race, scope widening after approval.
- EXP-ECC-5: canonical/semantic digest collision, secret-redaction collision, DNS/endpoint rebinding, config read failure.
- EXP-ECC-6: provider identity spoofing, gateway route attestation failure, forged manual attestation, packet replay after consent.
- EXP-ECC-7: retraction dependency traversal, self-asserted independent support, stale learned artifact injected into a new session.
- Cross-experiment: correlated false-green through shared `ecc_governance.py` abstraction.

## J. Impact-adjudication recommendation

No requirement is ready for automatic adoption or promotion. EXP-ECC-1 through EXP-ECC-5 require further narrowing before they can enter a separate governed impact-adjudication step as narrowed requirement candidates. The required narrowing is primarily to make V2 attestation/authentication/governance fields mandatory and to scope or remove legacy permissive fallbacks.

EXP-ECC-6 and EXP-ECC-7 should remain outside impact adjudication until integration and live evidence exist. Their deferred fail-closed requirements may be reviewed later, but not as ready requirement candidates now.

No candidate should be promoted by this review.

## K. Freeze recommendation

`DO_NOT_FREEZE_V2_EXPERIMENT_EVIDENCE`

## L. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
