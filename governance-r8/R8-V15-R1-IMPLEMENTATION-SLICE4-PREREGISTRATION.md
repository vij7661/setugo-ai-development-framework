# R8 v15-r1 — Implementation Slice 4: Local AuthorityReadSet / DecisionPresealContext Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

Closed Slice 3 evidence head:
`adf6e2bfdcf96ec67f762615a3f5a1b0d031921a`

Exact closed Slice 3 implementation candidate:
`9b8b519c1f32b675d102b1267511a6a141f39c4a`

Exact closed Slice 2 implementation candidate:
`6a8d0b0e4baa3a9df75dc47f626953b4dde51255`

Exact closed Slice 1 implementation candidate:
`fdf825cb45fbd00441a4cd02bb1912bb3cda01b0`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Open runtime finding `R8V15R1-RTQ-OPEN-001` remains OPEN.

No prior open hardening item is silently closed by this slice. Slice 4 may add regression
coverage for earlier local validators, but changing a closed implementation module would require
its own successor/review lineage.

## 2. Goal

Implement a repository-local, pure validator for:
- `AuthorityReadSetEntry`;
- `AuthorityReadSet`;
- `DecisionPresealContext`;
- nested `SemanticHeads`;
- nested `ResolverIdentity`;

using only exact frozen field/shape rules and deterministic cross-field equality that the
frozen schema/source actually supports.

Slice 4 must NOT invent a digest formula for:
- `authority_read_set_digest`;
- `decision_preseal_digest`;
- any generic `Digest`.

Those fields remain opaque non-empty GCP-valid strings unless a later governing source binds
a concrete algorithm/preimage.

## 3. Frozen AuthorityReadSet contract

### AuthorityReadSetEntry exact fields
1. `input_id`
2. `source_id`
3. `head_digest`
4. `value_digest`
5. `schema_semantic_entry_digest`

All five are required. No extras are allowed.

`input_id` and `source_id` are opaque non-empty CanonicalId strings.
The three digest fields are opaque non-empty Digest strings.

### AuthorityReadSet exact fields
1. `entries`
2. `authority_read_set_digest`

`entries` is an ordered array with at least one AuthorityReadSetEntry.
No uniqueness or sorting rule is invented here because the frozen schema does not declare one.

`authority_read_set_digest` is an opaque non-empty Digest string.
This slice validates only shape and cross-field equality when the read set is supplied to a
DecisionPresealContext validator. It does not recompute the digest.

NORM-030 remains a runtime/authority rule: every mutable authority input consumed by a predicate
must be registered/captured; this local validator cannot prove completeness of an actual predicate's
read set.

## 4. Frozen DecisionPresealContext contract

Exact required fields:
1. `candidate_id`
2. `action_id`
3. `decision_scope_digest`
4. `governance_snapshot_digest`
5. `authority_read_set_digest`
6. `semantic_state_sequence`
7. `semantic_heads`
8. `rir_record_id`
9. `rir_head_digest`
10. `resolver_identity`
11. `revocation_state_digest`
12. `runtime_state_digest`
13. `workload_state_digest`
14. `effect_class`
15. `decision_preseal_digest`

No extra or omitted field is allowed.

`semantic_state_sequence` uses the frozen non-negative signed-int64 Sequence closure;
booleans are rejected.

Generic CanonicalId/Digest fields remain opaque non-empty GCP-valid strings.

`decision_preseal_digest` remains opaque: Slice 4 does not invent its preimage or algorithm.

## 5. Frozen SemanticHeads / ResolverIdentity contract

### SemanticHeads exact fields
- csm_head
- aim_head
- semantic_any_permission_head
- aim_scope_policy_head
- resolver_policy_head
- resolver_implementation_registry_head
- guard_registry_head
- revocation_head
- nonce_ledger_head
- effect_stream_head
- configuration_head

All values are non-empty opaque Digest strings and must pass inherited GCP string validation.

### ResolverIdentity exact fields
- resolver_policy_digest
- implementation_id
- runtime_identity_digest
- workload_identity_digest
- conformance_suite_digest
- conformance_evidence_digest

`implementation_id` is a non-empty opaque CanonicalId.
All other values are non-empty opaque Digest strings.
No local validation of active RIR membership, runtime/workload attestation, or current PASS
conformance status is claimed.

## 6. effect_class sentinel rule

Frozen schema invariant:
- `effect_class = null` exactly when the decision has no external effect;
- if an external effect is involved, `effect_class` is a non-empty governed class;
- omission is invalid.

A local validator therefore accepts a verifier-owned argument:
`external_effect_involved: bool`.

This argument is external validation context. It is not copied from DecisionPresealContext and
does not grant the candidate authority to choose its own effect semantics.

Rules:
- external_effect_involved=false -> effect_class must be exactly null;
- external_effect_involved=true -> effect_class must be a non-empty GCP-valid string;
- non-boolean verifier context rejects.

This slice does not prove the verifier context was lawfully derived; that remains a later
runtime/authority responsibility.

## 7. Cross-field local rule

When validating a DecisionPresealContext together with an AuthorityReadSet:
- the read set must first pass local structural validation;
- `DecisionPresealContext.authority_read_set_digest` must exactly equal
  `AuthorityReadSet.authority_read_set_digest`.

No other digest recomputation is permitted in this slice.

## 8. Frozen invariants

**I4-I01** AuthorityReadSetEntry field constant exactly equals frozen schema required fields.
**I4-I02** AuthorityReadSet field constant exactly equals frozen schema required fields.
**I4-I03** DecisionPresealContext field constant exactly equals frozen schema required fields.
**I4-I04** SemanticHeads and ResolverIdentity constants exactly equal frozen schema required fields.
**I4-I05** AuthorityReadSet requires at least one exact-shape entry.
**I4-I06** Generic IDs/digests are non-empty opaque GCP-valid strings; no global SHA format is invented.
**I4-I07** Sequence uses non-boolean signed-int64 non-negative closure.
**I4-I08** effect_class sentinel is validated against verifier-owned effect context.
**I4-I09** supplied AuthorityReadSet digest must exactly equal DPS authority_read_set_digest.
**I4-I10** authority_read_set_digest and decision_preseal_digest remain opaque; no recomputation/self-grant.
**I4-I11** nested SemanticHeads exact shape/value closure.
**I4-I12** nested ResolverIdentity exact shape/value closure.
**I4-I13** validation metadata grants no currentness, qualification, authority, release, or deployment.
**I4-I14** failures do not poison later validation; no mutable weakening state.
**I4-I15** frozen schema and closed Slice 1/2/3 implementation modules remain unchanged.
**I4-I16** inherited I1/S1R/S1R2/I2/I3 suites remain green, and Slice 4 CI directly covers governed paths.

## 9. Frozen acceptance cases

- I4-01 AuthorityReadSetEntry required fields exactly match frozen schema.
- I4-02 AuthorityReadSet required fields exactly match frozen schema.
- I4-03 DecisionPresealContext required fields exactly match frozen schema.
- I4-04 SemanticHeads + ResolverIdentity required fields exactly match frozen schema.
- I4-05 one-entry and multi-entry valid AuthorityReadSet pass; empty entries reject.
- I4-06 AuthorityReadSet entry/read-set missing or extra fields reject.
- I4-07 empty/non-NFC/noncharacter generic strings reject; opaque non-SHA digests pass.
- I4-08 semantic_state_sequence min/max pass; negative/max+1/bool/string/float reject.
- I4-09 no-effect + null effect_class passes; no-effect + string rejects.
- I4-10 effect + non-empty GCP-valid effect_class passes; effect + null/empty rejects; non-bool verifier context rejects.
- I4-11 DPS/read-set digest equality passes; mismatch rejects.
- I4-12 SemanticHeads missing/extra/empty/non-NFC value rejects.
- I4-13 ResolverIdentity missing/extra/empty/noncharacter value rejects.
- I4-14 decision_preseal_digest remains opaque non-empty; no SHA-only rule; result metadata remains authority NONE.
- I4-15 a failed validation does not poison subsequent valid read-set/DPS validation.
- I4-16 dependency immutability + inherited full test stack + direct Slice 4 workflow path coverage all pass.

## 10. Deferred / nonclaims

This slice does not prove:
- AuthorityReadSet completeness for an actual predicate;
- source/head/value freshness or currentness;
- authority_read_set_digest correctness beyond exact supplied equality;
- decision_preseal_digest correctness;
- active/current RIR membership;
- resolver implementation/runtime/workload/conformance qualification;
- revocation/runtime/workload state currentness;
- lawful derivation of external_effect_involved;
- time proof validity;
- VerifiedStateSeal correctness;
- consequential commit current-state recheck;
- runtime qualification, release, deployment, production, policy, or terminal authority.

## 11. Workflow hardening

Slice 4 CI must directly trigger on changes to:
- Slice 4 preregistration;
- Slice 4 validator module;
- Slice 4 frozen acceptance harness;
- Slice 4 marker;
- Slice 4 workflow itself;
- closed Slice 1 canonicalizer dependency.

## 12. Construction sequence

1. Commit this preregistration.
2. Add direct-trigger Slice 4 workflow and frozen acceptance harness with no Slice 4 mechanism.
3. Preserve expected RED mechanism-absence evidence.
4. Implement only the bounded local read-set/preseal validator.
5. Require I4-01..I4-16 plus inherited Slice 3/2/1 suites on one exact candidate.
6. Freeze exact candidate.
7. Build fresh blind independent review packet.
8. Require fresh independent review before bounded Slice 4 adjudication.

## 13. Claim boundary

A positive Slice 4 result proves only deterministic local structure/cross-field validation under
the frozen contracts and verifier-supplied effect context. It grants no runtime/currentness,
resolver qualification, time/seal/commit, release, deployment, production, policy, or terminal authority.
