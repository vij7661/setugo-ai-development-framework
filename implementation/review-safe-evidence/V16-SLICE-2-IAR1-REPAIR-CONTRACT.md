# V16 Slice 2 IAR1 Repair Contract

Status: **CONSTRUCTION REPAIR CONTRACT / NON-AUTHORITATIVE**

Predecessor Slice 2 candidate: `c484a52970725e117bb8b2246e18ba47744c9b76`

Predecessor internal review: `V16-SLICE-2-INTERNAL-ADVERSARIAL-REVIEW-001.md`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Mandatory repairs

### R1 — global promotion remains fail-closed while real-world independence is unproven

No Slice 2 structural success may emit a generic nonblocking promotion result while `graph_completeness_real_world_proven=false`, `independence_real_world_proven=false`, or equivalent control-completeness proof remains false.

Required behavior:

- generic `promotion_blocked` remains `true` throughout Slice 2 construction;
- registry authority may expose a bounded structural result, but generic `authority_admissible` remains `false` until a later independently qualified real-world/currentness layer exists;
- within-graph success must be explicitly named as construction/structural evidence only.

### R2 — bind exact Slice 2 validator semantics and source artifacts

Introduce a bootstrap-threshold-authenticated binding certificate over the exact current control-domain graph plus:

- Slice 2 validation-profile digest;
- exact validator-bundle digest;
- graph candidate/ID/sequence/generation/digest;
- trust-set ID/digest.

The local validation profile must bind the graph schema, signature domain, edge meaning, candidate-control rule, independence rule, additive-history rule, global fail-closed rule, and Slice 1 base validation profile.

The validator bundle must measure exact source bytes for the frozen Slice 1 base validator, the Slice 2 structural core, and the Slice 2 binding wrapper. Self-measurement remains construction evidence only; independent runtime measurement is not claimed.

A pinned binding head must require the exact binding/profile/bundle identity. Replay of an old signed graph/binding under changed validator semantics or source bytes must fail closed.

### R3 — common governance-generation/currentness at combined authority boundary

Any function that combines registry authority with graph-derived candidate-control/independence must require an explicit expected governance generation and verify that both the pinned registry head and pinned graph head use that same generation.

This is a Slice 2 construction stopgap. The dedicated authenticated governance-generation/currentness surface remains required later by the frozen V16 successor scope.

### R4 — derive semantic role from canonical record/operation type

Combined registry-authority functions must not accept a free-form `required_role` as the load-bearing semantic requirement. They must accept an expected record/operation type and derive the required role from the Slice 1 canonical policy mapping. Unknown record types fail closed.

## Mandatory adversarial additions

The repaired candidate must add stable tests proving at least:

- structural graph success still leaves global promotion blocked;
- disconnected within-graph independence still leaves global promotion blocked;
- structurally clear candidate-control result still leaves global promotion blocked;
- structurally admissible registry authority leaves generic authority non-admissible and promotion blocked;
- profile drift invalidates an old binding;
- validator-bundle drift/tamper invalidates a binding even with newly recomputed certificate digest/signatures;
- graph-head/digest substitution invalidates the binding;
- threshold binding signatures remain required;
- mixed registry/graph governance generations fail closed;
- role semantics are derived from canonical record type;
- unknown record type fails closed;
- two structurally independent registry keys remain globally blocked while real-world independence is unproven;
- no repaired PASS path claims implementation/runtime/scientific/effect authority.

## Preserved boundaries

Repairing these findings does not prove real-world graph completeness, corporate/account ownership, bootstrap provisioning, pinned-head freshness, independent source measurement, implementation qualification, runtime qualification, scientific authority, or effect authority.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
