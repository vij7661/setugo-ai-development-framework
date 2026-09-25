# R8 v15-r1 — Implementation Slice 6: Local VerifiedStateSeal Binding Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

Closed Slice 5 evidence head:
`be1f195f437865a0c9caed19d4e4af48704c275b`

Exact closed implementation candidates:
- Slice 5: `403e40502e9d51740e89ef352b5611711439661e`
- Slice 4: `3b60d8f14851b755f09a35431c620d6ae594a894`
- Slice 3: `9b8b519c1f32b675d102b1267511a6a141f39c4a`
- Slice 2: `6a8d0b0e4baa3a9df75dc47f626953b4dde51255`
- Slice 1: `fdf825cb45fbd00441a4cd02bb1912bb3cda01b0`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Open runtime finding `R8V15R1-RTQ-OPEN-001` remains OPEN.

## 2. Goal

Implement a repository-local, pure validator for the frozen `VerifiedStateSeal` object and
its deterministic local bindings to already-closed Slice 4/5 inputs.

This slice validates only:
- exact seal field shape;
- opaque non-empty GCP-valid Digest fields;
- frozen Sequence closure;
- exact SemanticHeads shape;
- local cross-object equality between the seal, supplied DecisionPresealContext,
  supplied AuthorityReadSet and supplied QualifiedTimeProof.

It does NOT establish:
- current LAS head/state;
- seal_digest cryptographic correctness;
- current revocation/runtime/workload state;
- accepted/consumed qualified time;
- consequential commit authority;
- `COMMIT_WITH_SEAL` correctness.

## 3. Frozen VerifiedStateSeal contract

Exact required fields:
1. `decision_preseal_digest`
2. `time_proof_digest`
3. `authority_read_set_digest`
4. `semantic_state_sequence`
5. `semantic_heads`
6. `revocation_head`
7. `seal_digest`

No extras are allowed.

`semantic_state_sequence` uses frozen Sequence closure:
`0 <= value <= 9223372036854775807`, booleans rejected.

All Digest fields remain opaque non-empty GCP-valid strings. Slice 6 does not invent a
global SHA-256 lexical rule or a seal_digest preimage.

`semantic_heads` uses the exact closed Slice 4 SemanticHeads field set and string rules.

## 4. Frozen source basis for local composition

NORM-033:
- final seal binds the full authority read set and semantic/runtime/time/revocation state;
- consequential commit separately atomically rechecks current authority heads;
- state change -> STATE_CHANGED and no effect intent.

R8V12-I030:
- VerifiedStateSeal includes the same semantic fields as the preseal plus accepted time/nonce proof;
- consequential commit compares current LAS named semantic heads and semantic_state_sequence to the seal.

V12-025:
- current semantic sequence/heads are bound into preseal, time proof and final seal.

Therefore this bounded local validator checks only equality across supplied already-validated
objects. It does not perform the later current-state recheck.

## 5. Cross-object bindings

Before seal comparison:
1. revalidate supplied DecisionPresealContext + AuthorityReadSet via closed Slice 4;
2. revalidate supplied QualifiedTimeProof via closed Slice 5, using the same supplied
   DecisionPresealContext, AuthorityReadSet and verifier-owned effect context.

Then require:

- `seal.decision_preseal_digest == dps.decision_preseal_digest`;
- `seal.time_proof_digest == qualified_time_proof.time_proof_digest`;
- `seal.authority_read_set_digest == dps.authority_read_set_digest == authority_read_set.authority_read_set_digest`;
- `seal.semantic_state_sequence == dps.semantic_state_sequence`;
- `qualified_time_proof.effective_sequence == dps.semantic_state_sequence`;
- `seal.semantic_heads == dps.semantic_heads` by exact key/value equality;
- `seal.revocation_head == seal.semantic_heads.revocation_head == dps.semantic_heads.revocation_head`.

These are local binding checks only.

## 6. Explicit nonclaims

A successful local result MUST say false for:
- `seal_digest_verified`;
- `qualified_time_proven`;
- `nonce_consumed`;
- `current_heads_rechecked`;
- `state_unchanged_at_commit`;
- `current_revocation_proven`;
- `current_runtime_workload_proven`;
- `commit_with_seal_authorized`;
- `effect_intent_committed`;
- runtime qualification, release, deployment, production, policy, terminal authority.

## 7. Frozen invariants

**I6-I01** VerifiedStateSeal field constant exactly equals frozen schema required fields.
**I6-I02** top-level missing/extra seal fields reject.
**I6-I03** Digest fields are non-empty opaque GCP-valid strings.
**I6-I04** semantic_state_sequence uses non-boolean signed-int64 non-negative closure.
**I6-I05** SemanticHeads exact shape/value validation is reused without weakening.
**I6-I06** supplied DecisionPresealContext/AuthorityReadSet are locally revalidated first.
**I6-I07** supplied QualifiedTimeProof is locally revalidated first.
**I6-I08** decision_preseal_digest binding is exact.
**I6-I09** time_proof_digest binding is exact.
**I6-I10** authority_read_set_digest binding is exact across seal/DPS/read-set.
**I6-I11** semantic sequence is equal across seal/DPS/time proof effective_sequence.
**I6-I12** semantic heads exact-equal across seal/DPS and standalone revocation_head agrees.
**I6-I13** seal_digest remains opaque and is not marked verified.
**I6-I14** successful metadata remains authority NONE with all current-state/commit claims false.
**I6-I15** failures do not poison later validation.
**I6-I16** frozen schema and closed Slice 1..5 implementation modules remain unchanged; inherited full test stack stays green; Slice 6 CI directly covers every executed dependency/test path.

## 8. Frozen acceptance cases

- I6-01 VerifiedStateSeal required fields exactly match frozen schema.
- I6-02 valid locally bound seal passes.
- I6-03 missing/extra seal fields reject.
- I6-04 empty/non-NFC/noncharacter opaque seal digest fields reject; opaque non-SHA values pass.
- I6-05 semantic_state_sequence min/max pass; negative/max+1/bool/string/float reject.
- I6-06 malformed SemanticHeads missing/extra/empty/non-NFC reject.
- I6-07 invalid supplied DPS/read-set rejects before seal comparison.
- I6-08 invalid supplied QualifiedTimeProof rejects before seal comparison.
- I6-09 decision_preseal_digest mismatch rejects.
- I6-10 time_proof_digest mismatch rejects.
- I6-11 authority_read_set_digest mismatch rejects.
- I6-12 seal/DPS semantic_state_sequence mismatch rejects; QTP effective_sequence mismatch rejects.
- I6-13 seal/DPS semantic_heads mismatch rejects; standalone revocation_head disagreement rejects.
- I6-14 seal_digest remains opaque and non-authority metadata remains false for current-state/commit claims.
- I6-15 failed validation does not poison a later valid seal validation.
- I6-16 dependency immutability + inherited I5/I4/I3/I2/I1 stack + direct workflow trigger coverage all pass.

## 9. Workflow hardening

Slice 6 CI must directly trigger on:
- Slice 6 preregistration;
- Slice 6 validator;
- Slice 6 frozen harness;
- Slice 6 marker;
- Slice 6 workflow;
- closed Slice 5 time-proof validator;
- closed Slice 4 preseal validator;
- closed Slice 3/2/1 modules;
- every inherited acceptance/regression test executed by the workflow.

## 10. Construction sequence

1. Commit this preregistration.
2. Add Slice 6 frozen harness and direct-trigger workflow with no Slice 6 mechanism.
3. Preserve expected RED mechanism-absence evidence.
4. Implement only the bounded local seal-binding validator.
5. Require I6-01..I6-16 plus inherited Slice 5/4/3/2/1 suites on one exact candidate.
6. Freeze exact candidate.
7. Build a fresh blind independent-review packet.
8. Require fresh independent review before bounded Slice 6 adjudication.

## 11. Claim boundary

A positive Slice 6 result proves only deterministic local VerifiedStateSeal structure and
cross-object binding against supplied locally valid preseal/read-set/time-proof objects.

It does not establish a cryptographically verified seal, current authority state,
STATE_CHANGED protection at commit, COMMIT_WITH_SEAL authority, runtime qualification,
release, deployment, production, policy or terminal authority.
