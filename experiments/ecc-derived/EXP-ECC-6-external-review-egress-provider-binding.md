# EXP-ECC-6 — External Review Egress + Provider-Relationship Binding

Status: **PREREGISTERED — NOT EXECUTED**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Hypothesis

External review transport must bind the exact candidate packet, destination/model/provider relationship, permitted data egress, reviewer role, and evidence class. A cross-model or cross-provider label cannot be inferred merely from model names, gateways, or routing claims.

## Current testing constraint

During the current TESTING phase, external reviewer-model API calls are prohibited. This experiment may falsify packet construction, metadata, role/provider classification, consent, routing declarations, and fail-closed behavior using deterministic fixtures only. It must not send real external reviewer API requests.

## Provider-relationship classes

At minimum:
- `SAME_PROVIDER_CONFIRMED`
- `DIFFERENT_PROVIDER_CONFIRMED`
- `GATEWAY_RELATIONSHIP_UNVERIFIED`
- `PROVIDER_IDENTITY_UNKNOWN`

None of these classes grants authority. They describe evidence provenance/independence characteristics only.

## Required bindings

Exact candidate/packet digest, reviewer slot (`R1/R2/R3` as applicable), selected model/provider/gateway, provider-relationship class, permitted data classes, destination, consent/approval evidence where required, tool/network permissions, clean-room/isolation claims, and evidence class.

R1/R2/R3 remain configurable roles; no model/provider is hardcoded to any role.

## Falsification cases

- E6-01 packet digest changes after consent but transport metadata still says approved.
- E6-02 two model names behind the same provider are labeled independent cross-provider review.
- E6-03 gateway route hides returned provider identity and system claims `DIFFERENT_PROVIDER_CONFIRMED`.
- E6-04 R2 output is reused as R3 evidence without a new role binding.
- E6-05 user selects a different qualified model for R1/R2/R3 but stale provider/role metadata is retained.
- E6-06 review packet contains data outside the permitted egress class.
- E6-07 external-review transport failure is treated as a completed review.
- E6-08 model response is counted as manual human review.
- E6-09 reviewer context isolation cannot be evidenced but review is still labeled clean-room independent.
- E6-10 packet/candidate changes after review and review remains current.

## Positive controls

- E6-P1 manually transported AI review remains `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`, threshold contribution zero.
- E6-P2 user may assign any currently qualified model/provider to R1/R2/R3 and exact binding updates correctly.
- E6-P3 confirmed same-provider critique remains useful engineering evidence without being laundered into heterogeneous independence.
- E6-P4 future automated transport can remain disabled while deterministic packet/provenance checks still function.

## Pass condition

The system cannot upgrade provider diversity, reviewer independence, evidence class, or candidate binding based on names/consensus/routing assumptions, and current manual-only testing policy remains enforced.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
