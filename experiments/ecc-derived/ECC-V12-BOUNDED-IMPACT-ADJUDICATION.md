# ECC-Derived V12 Bounded Impact Adjudication

Status: `BOUNDED_IMPACT_ADJUDICATION_COMPLETE`

Authority effect: `NONE_EVIDENCE_ONLY`

This adjudication does **not** promote a requirement into an active standard, modify V18, qualify a production mechanism, satisfy a manual-review threshold, or authorize merge/release/terminal action.

## Exact inputs

- Frozen V12 experiment candidate: `a87cccd803ce307c601b32e1ad47bfd45790d38c`
- Candidate tree: `1b159c664a64ed6d3180613bb8ab6a3433bc1c57`
- Exact V12 ledger-head test result: `198/198 PASS`
- Clean external packet SHA-256: `5fa323c1eab698d72c98bec89ce66a537f27597a565b0015d6575b87cea10c65`
- DeepSeek clean-review preservation commit: `42657d00fcbfa95834df67472c2da3af48563995`
- DeepSeek evidence class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- Manual-review threshold contribution: `0`
- Current V18 candidate remains: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

The reviewer disposition was `READY_FOR_BOUNDED_IMPACT_ADJUDICATION`, with EXP-ECC-1 through EXP-ECC-5 at `ADOPT_REQUIREMENT_CANDIDATE`, EXP-ECC-6 and EXP-ECC-7 deferred, and the experiment evidence safe to freeze for impact adjudication only.

## Adjudication rule

`ADOPT_REQUIREMENT_CANDIDATE` means the experiment has enough bounded evidence to require consideration in the next governed design candidate. It does **not** mean the requirement is already active, production-qualified, or allowed to bypass the normal candidate review/falsification/authority process.

A requirement candidate may enter the next governed design only with its tested scope and explicit nonclaims intact. Any broader implementation claim requires new evidence.

## EXP-ECC-1 — Enforcement Execution Attestation

Adjudication: `ADOPT_FOR_NEXT_GOVERNANCE_CANDIDATE`

Requirement candidate:

> When policy requires an enforcement control for a governed action, the platform must distinguish at least `CONTROL_CONFIGURED`, `CONTROL_EXECUTED`, `CONTROL_VERIFIED`, `CONTROL_FAILED`, and `CONTROL_UNKNOWN`. Configuration alone is not evidence of execution. Missing, stale, failed, or unknown required execution evidence must block the dependent governed transition.

Required binding includes the exact governed action/candidate, control identity/version/digest, execution identity, invocation/action sequence, and the evidence necessary to distinguish actual execution from configuration or telemetry.

Impact on current design:

- additive cross-cutting runtime/evidence requirement;
- proof views must expose execution state rather than merely declared/configured state;
- no V18 mutation in this adjudication;
- next post-V18 candidate must map this requirement to the authoritative runtime/governor enforcement point and falsification cases.

## EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence

Adjudication: `ADOPT_FOR_NEXT_GOVERNANCE_CANDIDATE`

Requirement candidate:

> A declared governance property may be relied upon only when the executable mechanism is proven equivalent for the material enforcement dimensions. Documentation, generated policy text, configured hooks, or labels must not assert stronger blocking/fail-closed behavior than the executable path actually provides.

Material mismatches such as blocking-vs-telemetry, fail-closed-vs-fail-open, hidden disable paths, stale executable profiles, or candidate-binding differences must fail closed for the dependent transition.

Impact on current design:

- cross-cuts standards, proof views, runtime gates, and documentation claims;
- a future candidate must define the canonical equivalence dimensions and their authoritative executable evidence;
- this does not convert documentation into authority.

## EXP-ECC-3 — Qualified Harness Capability Envelope

Adjudication: `ADOPT_FOR_NEXT_GOVERNANCE_CANDIDATE`

Requirement candidate:

> Every harness/runtime used for governed work must have an exact, versioned capability envelope. Required capabilities must be satisfied by governed capability classes such as native enforcement or explicitly qualified adapter enforcement; instruction-only/reference-only behavior cannot silently satisfy stronger requirements.

Role binding remains **provider/model neutral**. R1/R2/R3 or other governed roles are user-selectable and may be occupied by any qualified model/provider. A model, provider, harness, runtime version, capability class, or material configuration change is a governed binding change and must trigger the required revalidation/restart behavior; it may never be silently substituted.

Impact on current design:

- extends role/harness qualification rather than hard-coding Claude, GPT, Gemini, or any provider;
- the next candidate must bind harness ID, runtime version, configuration digest, runtime identity evidence, capability classes, and revalidation triggers;
- production/native enforcement equivalence remains unproven until integrated evidence exists.

## EXP-ECC-4 — Capability / Power-Surface Activation Consent

Adjudication: `ADOPT_FOR_NEXT_GOVERNANCE_CANDIDATE`

Requirement candidate:

> Capabilities that can materially widen platform power must not become active merely because the harness possesses them. Activation must be separately governed and exactly scoped to the approved project/context, role, manifest/configuration, powers, resources, sequence/effective point, revocation/expiry state, and other material activation constraints.

Relevant power surfaces include source mutation, subprocess/process control, transcript/model egress, MCP/tool execution, persistence, credentials, external side effects, and comparable capabilities.

Impact on current design:

- complements existing anti-self-grant and approval-scope rules;
- next candidate must define activation records independently from capability possession;
- activation records cannot manufacture terminal authority or broaden user approval.

## EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift

Adjudication: `ADOPT_FOR_NEXT_GOVERNANCE_CANDIDATE_WITH_BOUNDED_SCOPE`

Requirement candidate:

> Governed tool/MCP/harness configuration must be attested using a canonical, secret-safe exact configuration identity. Material configuration drift must stale dependent qualification and must not be hidden by friendly names, stale digest fields, redaction collisions, endpoint rebinding, credential-profile aliasing, or equivalent substitutions.

The bounded V12 reference mechanism demonstrates, within its stated ordinary-module threat model, binding of fields including harness/tool identity, transport/resolved endpoint, actual `argv`, `permission_profile`, credential-profile fingerprint, and canonical/digest material, together with transitive digest-primitive integrity checks.

Impact on current design:

- next candidate must define the canonical production configuration schema, secret-safe representation, exact drift/staleness propagation, and authoritative attestation source;
- `REFERENCE_REPO_BOUND_SIMULATION_ONLY` remains non-live and non-independent;
- V12 does not prove live MCP/platform attestation, production trust-root separation, durable cross-process authority, TOCTOU safety, reflective/interpreter compromise resistance, or repository replacement resistance.

Reviewer follow-up obligations retained:

- `M1`: restore/reconstruct V9 verifier-primitive RED/GREEN records in the neutral lineage projection before production qualification/final archival closure;
- `M2`: `marshal.dumps(function.__code__)` is metadata-sensitive and must not become self-authorizing semantic proof. A future production candidate must use governed review discipline and preferably a more stable semantic/source/bytecode integrity approach;
- optional additional negatives for `_sha256_json`, `_v2_config_material`, reference-record mutation, and targeted wrappers may be added during implementation falsification without reopening the bounded experiment disposition unless they expose a concrete false green.

## EXP-ECC-6 — External Review Egress and Provider-Relationship Binding

Adjudication: `DEFER_PENDING_INTEGRATION_EVIDENCE`

No active requirement is promoted from this experiment yet.

Current testing policy remains unchanged: **testing uses manual external review transport; no automated external reviewer API calls are introduced by this adjudication.** AI reviewer outputs remain engineering feedback and contribute zero manual-review threshold credit.

A future integration experiment must prove exact packet/destination/consent/provider-relationship binding and prevent same-provider/gateway/manual-attestation laundering before this experiment can advance.

## EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary

Adjudication: `DEFER_PENDING_INTEGRATION_EVIDENCE`

No active requirement is promoted from this experiment yet.

The platform already follows the safety posture that memory/learned artifacts are not authority, but EXP-ECC-7 itself remains deferred until a real learned-artifact promotion/retraction/descendant-reassessment path exists and is falsified end-to-end.

Confidence, repetition, lack of correction, model agreement, or generated skill/rule/hook/agent output must not be treated as independent evidence of governed promotion merely because the reference tests express that principle.

## V18 impact decision

`V18_MUTATION = NONE`

V18 remains exact SHA `290ac043959f30db12c9ae16826eda1dd5bcbdfb`.

The existing V18 R3 design-review packet remains valid for that exact candidate and must not be silently regenerated or broadened by this adjudication.

ECC-1 through ECC-5 are queued as additive requirement candidates for the **next governed successor after the V18 review outcome is resolved**. If V18 R3 produces `CHANGES_REQUIRED`, the next successor may combine concrete V18 review repairs with these accepted ECC requirement candidates, but each change must remain attributable. If V18 R3 passes its design stage, the ECC requirements still enter a new successor candidate rather than rewriting the reviewed V18 SHA.

## Production and authority boundary

This adjudication does not support claims of:

- production readiness;
- live platform enforcement;
- independent production trust-root separation;
- durable cross-process provenance;
- arbitrary interpreter/native-process compromise resistance;
- complete concurrent/TOCTOU safety;
- automated-review integration readiness;
- learned-artifact integration readiness;
- manual-review qualification; or
- terminal/merge/release authority.

## Terminal disposition

- EXP-ECC-1: `ADOPTED_AS_BOUNDED_REQUIREMENT_CANDIDATE_FOR_NEXT_GOVERNANCE_DESIGN`
- EXP-ECC-2: `ADOPTED_AS_BOUNDED_REQUIREMENT_CANDIDATE_FOR_NEXT_GOVERNANCE_DESIGN`
- EXP-ECC-3: `ADOPTED_AS_BOUNDED_REQUIREMENT_CANDIDATE_FOR_NEXT_GOVERNANCE_DESIGN`
- EXP-ECC-4: `ADOPTED_AS_BOUNDED_REQUIREMENT_CANDIDATE_FOR_NEXT_GOVERNANCE_DESIGN`
- EXP-ECC-5: `ADOPTED_AS_BOUNDED_REQUIREMENT_CANDIDATE_FOR_NEXT_GOVERNANCE_DESIGN_WITH_RETAINED_NONCLAIMS`
- EXP-ECC-6: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- EXP-ECC-7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- V12 experiment evidence: `FROZEN_FOR_BOUNDED_IMPACT_ADJUDICATION`
- V18: `UNCHANGED`
- production qualification: `NOT_GRANTED`
- manual-review threshold effect: `0`
- authority effect: `NONE_EVIDENCE_ONLY`

## Next governed action

Resume the already-generated **V18 R3 design review** against exact V18 SHA `290ac043959f30db12c9ae16826eda1dd5bcbdfb`. Do not modify V18 first. After that review is preserved and adjudicated, create the next governed successor candidate incorporating only (a) concrete accepted V18 review repairs and (b) EXP-ECC-1 through EXP-ECC-5 from this bounded impact decision, with fresh falsification and review against the exact successor SHA.
