# R8 v15-r1 — Implementation Slice 7: Local EffectIntent Binding Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

Closed Slice 6 evidence head:
`05081fad07c41fb1daf0900c3ff79287f4b5701b`

Exact closed implementation candidates:
- Slice 6: `a972ddcee333aff063858727739986fe2fd8088d`
- Slice 5: `403e40502e9d51740e89ef352b5611711439661e`
- Slice 4: `3b60d8f14851b755f09a35431c620d6ae594a894`
- Slice 3: `9b8b519c1f32b675d102b1267511a6a141f39c4a`
- Slice 2: `6a8d0b0e4baa3a9df75dc47f626953b4dde51255`
- Slice 1: `fdf825cb45fbd00441a4cd02bb1912bb3cda01b0`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Open runtime qualification finding `R8V15R1-RTQ-OPEN-001` remains OPEN.

## 2. Goal

Implement a repository-local, pure validator for the frozen `EffectIntent` object and
its deterministic local bindings to already-closed Slice 4/5/6 objects.

This slice validates only:
- exact EffectIntent field shape;
- non-empty opaque GCP-valid CanonicalId/Digest strings;
- frozen constant `state = "INTENT_COMMITTED"`;
- external-effect sentinel consistency with the supplied DecisionPresealContext;
- exact binding to the supplied VerifiedStateSeal digest and DecisionPresealContext digest;
- exact effect_class equality with the supplied DecisionPresealContext effect_class.

It does NOT implement `COMMIT_WITH_SEAL`, current-head CAS, executor dispatch,
provider calls, reconciliation, compensation, or external success.

## 3. Frozen EffectIntent contract

Exact required fields:
1. `effect_intent_id`
2. `idempotency_key`
3. `verified_state_seal_digest`
4. `decision_preseal_digest`
5. `effect_class`
6. `payload_digest`
7. `provider_id`
8. `action`
9. `candidate_scope_digest`
10. `action_scope_digest`
11. `tenant_scope_digest`
12. `state`

No extras are allowed.

`state` must be exactly `INTENT_COMMITTED`.

All CanonicalId/Digest-like values are non-empty GCP-valid strings.
No global SHA-256 lexical rule is invented.

## 4. Source basis

NORM-031:
- DecisionPresealContext binds the effect class where relevant.

NORM-033:
- consequential commit separately performs the atomic current-head recheck;
- any state change -> STATE_CHANGED and no effect intent.

NORM-034:
- COMMIT_WITH_SEAL may commit an EffectIntent only;
- intent is not completion;
- external success requires qualified execution and reconciliation.

R8V7-I032:
- COMMIT_WITH_SEAL may commit EffectIntent but this never means the external effect succeeded.

R8V7-I033:
- every EffectIntent binds effect identity, provider/action, exact payload digest,
  candidate/action/tenant scope, one idempotency key derived once from the effect identity,
  and the originating CommitCertificate/VerifiedStateSeal digest;
- retries reuse the same idempotency key.

The frozen runtime schema also includes `decision_preseal_digest` and `effect_class`.

## 5. Local composition rules

Before EffectIntent comparison:
1. revalidate supplied DecisionPresealContext + AuthorityReadSet via closed Slice 4;
2. revalidate supplied QualifiedTimeProof via closed Slice 5;
3. revalidate supplied VerifiedStateSeal via closed Slice 6.

Then require:

- verifier-owned `external_effect_involved` must be exactly `true`;
- DecisionPresealContext.effect_class must be a non-empty string;
- `intent.verified_state_seal_digest == seal.seal_digest`;
- `intent.decision_preseal_digest == dps.decision_preseal_digest`;
- `intent.effect_class == dps.effect_class`;
- `intent.state == "INTENT_COMMITTED"`.

The following remain locally opaque:
- derivation of idempotency_key from effect_intent_id/effect_id;
- payload_digest correctness;
- provider_id/action qualification;
- candidate/action/tenant scope digest derivation;
- any commit certificate;
- any actual intent stream append/commit.

## 6. Explicit nonclaims

A successful local result MUST state false for:
- `effect_intent_committed`;
- `commit_with_seal_authorized`;
- `current_heads_rechecked`;
- `state_unchanged_at_commit`;
- `idempotency_key_derivation_verified`;
- `payload_digest_verified`;
- `provider_action_authorized`;
- `scope_digests_verified`;
- `executor_qualified`;
- `dispatch_authorized`;
- `external_effect_succeeded`;
- `reconciliation_complete`;
- runtime qualification, release, deployment, production, policy, terminal authority.

## 7. Frozen invariants

**I7-I01** EffectIntent field constant exactly equals frozen schema required fields.
**I7-I02** missing/extra EffectIntent fields reject.
**I7-I03** all generic string fields are non-empty opaque GCP-valid strings.
**I7-I04** state must equal exactly INTENT_COMMITTED.
**I7-I05** supplied DPS/read-set are revalidated through Slice 4.
**I7-I06** supplied QualifiedTimeProof is revalidated through Slice 5.
**I7-I07** supplied VerifiedStateSeal is revalidated through Slice 6.
**I7-I08** EffectIntent is invalid when verifier-owned external_effect_involved is false.
**I7-I09** non-bool external_effect_involved rejects.
**I7-I10** intent verified_state_seal_digest must equal supplied seal seal_digest.
**I7-I11** intent decision_preseal_digest must equal supplied DPS decision_preseal_digest.
**I7-I12** intent effect_class must equal non-null DPS effect_class.
**I7-I13** idempotency/payload/provider/action/scope fields remain opaque and unverified beyond local string shape.
**I7-I14** result metadata remains authority NONE and external success/commit/dispatch claims false.
**I7-I15** failures do not poison later valid validation.
**I7-I16** frozen schema and closed Slice 1..6 modules remain unchanged; inherited full stack stays green; Slice 7 workflow directly covers every executed dependency/test path.

## 8. Frozen acceptance cases

- I7-01 EffectIntent required fields exactly match frozen schema.
- I7-02 valid locally bound EffectIntent passes.
- I7-03 missing/extra EffectIntent fields reject.
- I7-04 empty/non-NFC/noncharacter generic string values reject; opaque non-SHA digests pass.
- I7-05 state other than INTENT_COMMITTED rejects.
- I7-06 invalid supplied DPS/read-set rejects before intent comparison.
- I7-07 invalid supplied QualifiedTimeProof rejects before intent comparison.
- I7-08 invalid supplied VerifiedStateSeal rejects before intent comparison.
- I7-09 external_effect_involved=false rejects intent; non-bool context rejects.
- I7-10 verified_state_seal_digest mismatch rejects.
- I7-11 decision_preseal_digest mismatch rejects.
- I7-12 effect_class mismatch or null DPS effect_class rejects.
- I7-13 idempotency_key/payload/provider/action/scope fields accept opaque non-SHA strings and remain explicitly unverified.
- I7-14 successful result explicitly states intent is not committed/completed and no dispatch/external success/reconciliation authority exists.
- I7-15 failed validation does not poison later valid validation.
- I7-16 dependency immutability + inherited I6/I5/I4/I3/I2/I1 stack + direct workflow trigger coverage all pass.

## 9. Deferred / nonclaims

This slice does not prove:
- atomic COMMIT_WITH_SEAL;
- current-head/state recheck;
- STATE_CHANGED protection;
- intent stream append/commit;
- idempotency key derivation or ledger consumption;
- payload digest correctness;
- provider/action/effect authorization at dispatch time;
- scope digest derivation;
- executor qualification/current credential/revocation state;
- provider attempt, receipt, observation or reconciliation;
- external success;
- compensation;
- runtime qualification, release, deployment, production, policy or terminal authority.

## 10. Workflow hardening

Slice 7 CI must directly trigger on:
- Slice 7 preregistration;
- Slice 7 validator;
- Slice 7 frozen harness;
- Slice 7 marker;
- Slice 7 workflow;
- closed Slice 6/5/4/3/2/1 modules;
- every inherited acceptance/regression source executed by the workflow.

## 11. Construction sequence

1. Commit this preregistration.
2. Add frozen Slice 7 harness and direct-trigger workflow with no Slice 7 mechanism.
3. Preserve expected RED mechanism-absence evidence.
4. Implement only the bounded local EffectIntent validator.
5. Require I7-01..I7-16 plus inherited Slice 6/5/4/3/2/1 suites on one exact candidate.
6. Freeze exact candidate.
7. Build a fresh blind independent-review packet.
8. Require fresh independent review before bounded Slice 7 adjudication.

## 12. Claim boundary

A positive Slice 7 result proves only deterministic local EffectIntent structure and binding to
supplied locally valid preseal/time/seal objects.

It does not establish that an intent was committed, that COMMIT_WITH_SEAL succeeded, that a
dispatch is authorized, or that any external effect occurred or succeeded.
