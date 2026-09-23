# R8 v7 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed effective candidate:
- R8 v5 base: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6 overlay: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7 successor: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v7 blob: `4bffae9907735862946e97ff9c608abf960078a8`

Independent review evidence:
- preserved at `review-evidence/R8-V7-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `c32a6eaef610dfbcfe64f3bf3227c424ee6138d3c67b3ad2984c2e3b8d35a41c`
- disposition: `CHANGES_REQUIRED`
- type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v7 closed most prior rollback, concurrency, provenance, and effect-state gaps. Executable-schema freeze remains blocked by two critical findings and eight additional high/medium closure requirements.

## 2. Critical findings

### V7-C1 — Unauthorized T0 successor reservation
**ACCEPTED — BLOCKER**

`RESERVE_T0_SUCCESSOR` must not accept a caller-supplied successor digest based only on generation state. A valid reservation request must include:
- predecessor T0 manifest digest;
- lawful predecessor constitutional/EBA threshold authorization over the exact successor digest;
- exact successor manifest digest;
- exact expected next generation;
- MTR freshness challenge;
- BTW/EBA trust bindings required by the predecessor policy.

Unauthorized reservation attempts must not consume or poison the generation slot.

### V7-C2 — Inherited v4 case semantics absent from review packet
**ACCEPTED — BLOCKER**

The next blind packet must include canonical R8 v4 design text containing G001-G025 and V4-001…V4-084 case semantics, not merely a consolidated lookup table.

This is a review-completeness defect. No claim about G001-G025 qualification can be made from a packet that omits their canonical semantics.

## 3. Accepted high findings

R8 v8 must additionally close:
- persisted highest-accepted MTR response sequence and rollback-resistant challenge-consumption state;
- workload-attested AuthorityInputGateway and broker channel identity;
- GGS configuration/replica rotation continuity;
- QualifiedEffectExecutor revocation/compromise handling for in-flight effects;
- complete `decision_preseal_digest` authority context;
- CSM-bound, workload-attested SPM generator identity;
- migration destination-policy freshness at commit;
- exact CSM applicable-scope resolution.

## 4. Accepted medium findings

R8 v8 must additionally:
- bind MTR challenge state to rollback-resistant storage;
- define compensation uncertainty/failure terminal states;
- assert inherited canonical-output vectors remain unchanged and freeze a v8 vector manifest;
- define omission failure for migration maps;
- preserve ReviewPresentationSchema before schema freeze;
- require governed evidence for trust-loss declaration;
- keep time nonce context bound to the full preseal/read-set context.

## 5. Bounded interpretation

The review is design evidence only. It grants no authority and proves no runtime exploit.

The explicit T0/EBA/MTR/BTW trust assumptions remain bounded roots. The required fixes concern software authorization, freshness, rotation, attestation, provenance, and packet completeness.

## 6. Successor rule

Create R8 v8 as a new successor overlay.

Do not mutate v5, v6, or v7.

R8 v8 must receive a fresh blind design review before executable-schema freeze.

Until then:
- R8 v1-v7 = `CHANGES_REQUIRED`
- R8 v8 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39/#40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
