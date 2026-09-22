# R8 v6 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed effective candidate:
- R8 v5 base commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6 successor commit: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v6 blob: `4604fc38859087f08f941f5bde023214876528cb`

Independent review evidence:
- preserved at `review-evidence/R8-V6-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `3085a4fbcf1390461a3f214d6e779e011d41d130fe8f9960188c8ef55f024403`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v6 closes many v5 blockers, especially atomic authority-stream CAS, semantic default-deny, read-set sealing, revocation/time rollback controls, migration requalification, Channel H authenticity, and explicit trust-domain failure. However executable-schema freeze remains blocked by five critical design/evidence gaps:

1. MTR freshness/anti-replay is not closed;
2. GGS rollback resistance is not defined;
3. T0 successor generation reservation is not atomic;
4. LAS-2 configuration rotation continuity is not frozen;
5. the complete inherited guard/fault-proof catalog was absent from the review packet.

R8 v6 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blockers

### V6-C1 — MTR freshness and replay
**ACCEPTED — BLOCKER**

The successor must remove ambiguous cached-token authority and define an exact online attestation protocol:
- verifier challenge nonce;
- exact trust-domain/context binding;
- single-use challenge;
- MTR response sequence/high-water tuple;
- freshness bound;
- response signature/attestation policy;
- fail closed when live freshness cannot be established for authority-bearing use.

### V6-C2 — GGS rollback resistance
**ACCEPTED — BLOCKER**

GGS must gain rollback-resistant hard state equivalent in strength to LAS:
- highest term/epoch;
- highest committed genesis index;
- committed constitution namespace digest;
- committed authorization-state digest;
- configuration generation;
- durable vote state;
- attested/monotonic persistence.

A rolled-back GGS replica becomes non-voting.

### V6-C3 — Atomic T0 generation reservation
**ACCEPTED — BLOCKER**

MTR must expose one atomic reservation primitive:

`RESERVE_T0_SUCCESSOR(expected_generation, successor_digest)`

At most one digest may reserve a given next generation.

Conflicting reservation at the same generation produces `T0_EQUIVOCATION`.

### V6-C4 — LAS configuration rotation
**ACCEPTED — BLOCKER**

LAS rotation must be constitutionally/CSM bound and preserve:
- term;
- vote hard state;
- committed/applied index;
- last committed entry digest;
- StreamHeadMap;
- idempotency state;
- configuration generation.

Use joint consensus or an equivalent frozen two-quorum transition; old configuration certificates become invalid after the exact activation index.

### V6-C5 — Complete guard/fault-proof catalog
**ACCEPTED — BLOCKER**

The next review packet must include one complete guard catalog from G001 through the successor's final guard, with:
- mechanism;
- positive case;
- every negative/adversarial case;
- per-negative `fault_proof` = REQUIRED/NOT_APPLICABLE;
- exact proof artifact class where REQUIRED.

No inherited catalog may be omitted from the packet.

## 3. Accepted high findings

The successor must additionally close:

- ACTIVE-only admin-domain quorum eligibility;
- canonical controller/principal/admin-domain alias resolution that cannot manufacture independence;
- mandatory schema-freeze semantic provenance manifest for RG-1;
- external side-effect execution/idempotency/reconciliation after effect intent;
- an exact AuthorityInputGateway enforcement profile rather than prose-only read discipline;
- CSM lifecycle state machine and deterministic AIM->CSM resolution.

## 4. Accepted medium findings

The successor must also:

- apply revocation rollback protection to every authority-bearing use, not only terminal/root-sensitive classes;
- make workload-attestation downgrade an explicit constitutional claim mode that cannot satisfy root/terminal runtime identity;
- freeze v6 Unicode/key-collision rejection vectors;
- fail migration with `MIGRATION_OBJECT_UNBOUND` when a referenced object was omitted from the migration map;
- freeze ReviewPresentationSchema semantics before schema freeze;
- define evidence/proof and sequence for entering a terminal trust-loss status;
- bind time decision context to the full AuthorityReadSet/seal context and single-use nonce.

## 5. Bounded interpretation

The review remains design/static evidence only and grants no implementation/runtime authority.

The explicit T0/MTR trust assumptions remain acceptable bounded axioms. The required corrections concern software-consumed freshness, rollback resistance, atomicity, provenance, and complete falsification coverage.

## 6. Successor rule

Create R8 v7 as a new successor overlay.

Do not mutate v5 or v6.

R8 v7 must receive a fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v6 = `CHANGES_REQUIRED`
- R8 v7 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
