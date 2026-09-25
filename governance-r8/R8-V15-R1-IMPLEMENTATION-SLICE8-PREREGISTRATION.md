# R8 v15-r1 — Implementation Slice 8: Local EffectStateRecord Validation

Status: PREREGISTERED BEFORE HARNESS OR MECHANISM IMPLEMENTATION

Base closure: 5477df994c2cc9db0033742e189b906eb20247c1
Closed Slice 7 candidate: 751162ee42c603cb6c84ee12021d16bab6fa626b
Frozen schema: f93ca26975ecb64f0da13779889c75b36140cdfc

## Goal
Validate only frozen local EffectStateRecord shape and deterministic binding to a supplied,
locally valid EffectIntent. No state transition, executor authority, reconciliation truth,
provider success, compensation correctness, runtime qualification, or downstream authority
is claimed.

## Frozen contract
Exact fields:
- effect_intent_id
- idempotency_key
- state
- executor_identity_digest
- reconciliation_evidence_digest
- state_record_digest

Allowed state values:
INTENT_COMMITTED, DISPATCHING, ACKNOWLEDGED_UNVERIFIED, SUCCEEDED_RECONCILED,
FAILED_FINAL, UNCERTAIN, COMPENSATION_REQUIRED, COMPENSATED.

executor_identity_digest and reconciliation_evidence_digest are nullable strings. If non-null
they must be non-empty GCP-valid opaque strings. state_record_digest is a non-empty opaque
GCP-valid Digest.

For SUCCEEDED_RECONCILED only, both executor_identity_digest and
reconciliation_evidence_digest must be non-null non-empty strings, matching the frozen schema.

## Local bindings
The supplied EffectIntent is revalidated through closed Slice 7 and:
- record.effect_intent_id == intent.effect_intent_id
- record.idempotency_key == intent.idempotency_key

No other state transition or lifecycle ordering rule is invented.

## Frozen acceptance I8-01..I8-16
I8-01 field parity with frozen schema.
I8-02 valid INTENT_COMMITTED record passes.
I8-03 every frozen enum state is locally accepted when shape-valid.
I8-04 missing/extra fields reject.
I8-05 invalid/unknown/non-string state rejects.
I8-06 opaque non-SHA IDs/digests pass; empty/non-NFC/noncharacter strings reject.
I8-07 nullable executor/reconciliation fields accept null on non-success states.
I8-08 non-null executor/reconciliation values must be non-empty GCP-valid strings.
I8-09 SUCCEEDED_RECONCILED requires executor_identity_digest.
I8-10 SUCCEEDED_RECONCILED requires reconciliation_evidence_digest.
I8-11 supplied EffectIntent is revalidated first.
I8-12 effect_intent_id mismatch rejects.
I8-13 idempotency_key mismatch rejects.
I8-14 result metadata never treats state label as external success, reconciliation truth,
executor qualification, dispatch authority, compensation correctness, or runtime authority.
I8-15 failure does not poison later valid validation.
I8-16 frozen schema / closed Slice 1..7 implementation bytes remain unchanged and inherited
full stack plus direct workflow coverage pass.

## Nonclaims
No actual effect-state stream append/commit; no legal state transition; no executor identity
qualification; no reconciliation evidence verification; no provider success; no compensation
authority; no runtime qualification, release, deployment, production, policy, terminal authority.

## Three-loop batch rule
This candidate may be frozen after construction but SHALL NOT be adjudicated closed before the
combined fresh independent review after Slice 8, Slice 9 and Slice 10 construction loops.
