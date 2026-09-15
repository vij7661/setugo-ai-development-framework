# V16 Slice 2 Internal Adversarial Review 001

Review class: **INTERNAL_ADVERSARIAL_RECORD**

This is not independent review and carries no authority transition.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Reviewed candidate

- candidate commit: `c484a52970725e117bb8b2246e18ba47744c9b76`
- candidate tree: `09da36f1680e9beb3597ab9266a090fabe184f34`
- construction run: `34986943870`
- construction job: `104441358252`
- construction result: 30/30 mandatory tests PASS

The construction PASS remains preserved. The following findings are against the mechanism and stopping rule, not a rewrite of the historical test result.

## IAR2-C-01 — unproven real-world independence is emitted as non-blocking promotion state

Severity: **Critical**

Affected functions:

- `validate_control_domain_graph_chain`
- `assess_domain_independence`
- `assess_candidate_control`
- `resolve_registry_key_authority`
- `assess_registry_key_independence`

Concrete false-green path:

The code explicitly returns `graph_completeness_real_world_proven=false`, `independence_real_world_proven=false`, or `control_real_world_completeness_proven=false`, while successful within-graph results set `promotion_blocked=false`. Registry authority resolution can additionally set `authority_admissible=true` under the same unproven real-world completeness boundary. Existing mandatory tests affirm this behavior for disconnected domains and registry keys.

This creates a load-bearing semantic contradiction: the mechanism correctly says that real-world independence/control completeness is unproven, but simultaneously emits a generic promotion/nonblocking or admissible signal. A downstream consumer could therefore treat a construction-only graph conclusion as sufficient promotion authority, recreating the false-green class the V16 successor is intended to remove.

Required narrow repair:

- keep generic `promotion_blocked=true` for every Slice 2 result while real-world graph completeness/independence qualification is unproven;
- replace generic `authority_admissible=true` with a clearly bounded construction field such as `authority_structurally_admissible_within_authenticated_graph=true`, while global `authority_admissible=false` remains fail-closed;
- expose within-graph result separately from promotion authority;
- add mandatory adversarial tests proving no successful structural path clears global promotion/authority while real-world completeness remains false.

## IAR2-H-01 — Slice 2 signed graph state is not bound to exact validator semantics/artifact identity

Severity: **High**

Affected surfaces:

- `CONTROL_DOMAIN_GRAPH` schema
- `control_domain_graph_digest`
- `control_domain_graph_signature_message`
- `PinnedControlDomainGraphHead`
- Slice 2 validation entry points

Concrete false-green path:

The same threshold-signed graph bytes can be replayed under changed Slice 2 validator semantics because the graph/signature/head bind graph content but not the exact validation profile or Slice 2 validator artifact bundle. A later code change could reinterpret parent-edge semantics, candidate-control derivation, canonicalization, or blocking rules while old signatures still verify.

Slice 1 already closed the equivalent class by binding load-bearing validation semantics/artifacts. Slice 2 currently regresses that protection for the new graph mechanism.

Required narrow repair:

- define a Slice 2 validation-profile digest that binds graph schema, signature domain, edge semantics, candidate-control rule, independence rule, currentness rule and exact validator artifact bundle identity;
- bind that digest into graph content/signatures and pinned graph head;
- reject profile/artifact drift before evaluating independence or candidate control;
- add replay-under-different-validator tests.

## IAR2-H-02 — registry authority and graph independence can be combined without a common currentness/generation vector

Severity: **High**

Affected functions:

- `resolve_registry_key_authority`
- `assess_registry_key_independence`

Concrete false-green path:

The resolver validates the registry against one pinned current head and the control graph against another, but never requires them to represent the same expected governance generation/currentness vector. A registry state from one generation can therefore be combined with an independently valid graph state from another generation. Because authority and candidate-control/independence are jointly derived from those two states, cross-generation mixing can evaluate a key against ancestry that did not govern that authority state.

Required narrow repair:

- require an explicit expected governance generation ID/currentness vector at the combined resolver boundary;
- require registry head and graph head to match that generation before authority/independence can be structurally satisfied;
- later replace this temporary equality contract with the dedicated authenticated governance-generation/currentness mechanism from the frozen successor scope;
- add mixed-generation rejection tests.

## IAR2-M-01 — generic role resolver still allows caller selection of the semantic role being checked

Severity: **Medium**

Affected functions:

- `resolve_registry_key_authority`
- `assess_registry_key_independence`

The supplied `required_role` must exist in authenticated registry state, which prevents fabricated grants, but the caller still selects which role is semantically required. A confused or malicious integration could ask whether a key has some role it actually holds and then reinterpret the positive result for a different operation.

Required narrow repair:

Prefer an operation/record-type input whose canonical required role is derived from the frozen policy, or introduce operation-specific wrappers. At minimum, preserve the checked role in the result and prohibit consumers from treating a generic successful lookup as operation authorization.

## Disposition

`V16_SLICE2_CONSTRUCTION_HISTORY = PRESERVED`

`V16_SLICE2_INTERNAL_REVIEW = CHANGES_REQUIRED`

`V16_SLICE2_CRITICAL_FINDINGS = 1`

`V16_SLICE2_HIGH_FINDINGS = 2`

`V16_SLICE2_MEDIUM_FINDINGS = 1`

`V16_SLICE2_FREEZE_ALLOWED = false`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
