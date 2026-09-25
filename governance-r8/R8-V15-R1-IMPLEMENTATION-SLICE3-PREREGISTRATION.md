# R8 v15-r1 — Implementation Slice 3: Local StateTransferCertificate Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

Closed Slice 2 evidence head:
`5e274ebffad1ffe84ffd569027e07a0a77915f1b`

Exact closed Slice 2 implementation candidate:
`6a8d0b0e4baa3a9df75dc47f626953b4dde51255`

Closed Slice 1 implementation candidate:
`fdf825cb45fbd00441a4cd02bb1912bb3cda01b0`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Open runtime finding `R8V15R1-RTQ-OPEN-001` remains open.

Slice 2 nonblocking hardening items remain historical findings. This Slice 3 will directly cover:
- GGS verify positive/mismatch/malformed paths before relying on them;
- verify-result non-authority metadata;
- direct workflow path coverage for Slice 3 governed files.

## 2. Goal

Implement a repository-local, pure validator for the frozen `StateTransferCertificate`
structure and deterministic cross-field consistency rules only.

It may verify:
- exact field set and local type/shape closure;
- LAS/GGS system-specific null/non-null rules;
- semantic-head object shape and required/null relation;
- LAS requirement that `semantic_state_binding_required=true`;
- GGS nested `GGSGenesisStateRoot` local digest validity using closed Slice 2;
- equality between GGS nested root members and their corresponding STC barrier snapshot fields;
- equality between GGS nested root `state_root_digest` and STC `state_root_digest`;
- lowercase 64-hex encoding for LAS/GGS state-root digest because the governing root formulas explicitly fix SHA-256;
- non-authority result metadata.

It must NOT verify or claim:
- that `rotation_prepare_certificate_digest` is a lawful committed ROTATION_PREPARE certificate;
- that `barrier_snapshot_index` is current/correct for the rotation;
- old/new quorum signatures;
- STC_COMMIT uniqueness or configuration-stream linearization;
- barrier reservation/abort semantics;
- whether a GGS operation lawfully requires semantic-state binding;
- whether LAS semantic heads correspond to one lawful barrier snapshot;
- sequencing/currentness, runtime qualification, release, deployment, production, policy, or terminal authority.

## 3. Frozen local schema contract

Exact required STC fields:
1. system_id
2. rotation_id
3. transition_id
4. rotation_prepare_certificate_digest
5. old_configuration_generation
6. old_configuration_digest
7. proposed_new_configuration_digest
8. barrier_snapshot_index
9. committed_log_prefix_digest
10. highest_seen_term
11. highest_committed_index
12. highest_applied_index
13. last_committed_entry_digest
14. state_root_digest
15. stream_head_map_root_digest
16. idempotency_dedup_ledger_root_digest
17. prior_certificate_chain_digest
18. ggs_namespace_root_digest
19. ggs_authorization_root_digest
20. semantic_state_binding_required
21. semantic_heads
22. ggs_genesis_state_root
23. stc_digest

`system_id` = `LAS-3 | GGS-3`.

Generic CanonicalId/Digest values are non-empty opaque strings unless a governing source
explicitly fixes a stronger encoding.

Sequence values use frozen signed-int64 non-negative closure:
`0 <= value <= 9223372036854775807`, booleans rejected.

`highest_applied_index` may additionally be null.

SemanticHeads exact required fields:
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

All SemanticHeads values are generic non-empty opaque Digest strings.

## 4. Frozen LAS local rules

For `system_id=LAS-3`:
- `semantic_state_binding_required` must be true;
- `semantic_heads` must be a valid non-null SemanticHeads object;
- `stream_head_map_root_digest` must be a non-empty Digest string;
- `ggs_namespace_root_digest` must be null;
- `ggs_authorization_root_digest` must be null;
- `ggs_genesis_state_root` must be null;
- `state_root_digest` must be lowercase 64-hex SHA-256 lexical form.

This slice does not prove that the LAS root or heads are the lawful barrier-B snapshot.

## 5. Frozen GGS local rules

For `system_id=GGS-3`:
- `stream_head_map_root_digest` must be null;
- `ggs_namespace_root_digest` must be a non-empty Digest string;
- `ggs_authorization_root_digest` must be a non-empty Digest string;
- `ggs_genesis_state_root` must be non-null and locally valid;
- if `semantic_state_binding_required=true`, `semantic_heads` must be valid/non-null;
- if false, `semantic_heads` must be null;
- `state_root_digest` must be lowercase 64-hex SHA-256 lexical form.

The nested GGS root must map exactly:
- ggs_genesis_state_root.barrier_index == barrier_snapshot_index
- .committed_log_prefix_digest == committed_log_prefix_digest
- .constitution_namespace_root == ggs_namespace_root_digest
- .bootstrap_authorization_root == ggs_authorization_root_digest
- .idempotency_ledger_root == idempotency_dedup_ledger_root_digest
- .configuration_generation == old_configuration_generation
- .prior_certificate_chain_digest == prior_certificate_chain_digest
- .state_root_digest == state_root_digest

The nested GGS root must also pass the closed Slice 2 deterministic GGS root verifier.

This slice does not decide whether `semantic_state_binding_required` was lawfully derived
from the governed GGS operation; that remains external/runtime authority.

## 6. Frozen invariants

**I3-I01 Exact STC field parity** — implementation STC field constant equals frozen schema required set.
**I3-I02 Exact SemanticHeads parity** — implementation head-field constant equals frozen schema required set.
**I3-I03 LAS conditional closure** — LAS accepts only the frozen LAS conditional shape.
**I3-I04 GGS conditional closure** — GGS accepts only the frozen GGS conditional shape.
**I3-I05 GGS nested root equality** — every mapped nested root field equals its STC counterpart.
**I3-I06 GGS nested root digest verification** — nested root must pass closed Slice 2 verification.
**I3-I07 Sequence closure** — all non-null Sequence fields enforce non-boolean signed-int64 range.
**I3-I08 Opaque ID/Digest preservation** — generic IDs/digests remain non-empty opaque GCP-valid strings.
**I3-I09 Root digest encoding** — STC state_root_digest is lowercase 64-hex.
**I3-I10 highest_applied nullability** — null or valid Sequence only.
**I3-I11 No caller currentness/certification self-grant** — successful validation emits no authority/current/certified claim.
**I3-I12 stc_digest opacity** — local validator checks only non-empty/GCP-valid Digest shape; it does not invent a hash formula.
**I3-I13 Stateless failure recovery** — invalid validation cannot weaken subsequent calls.
**I3-I14 Closed dependency preservation** — frozen schema, Slice 1 module, and Slice 2 module bytes remain unchanged.
**I3-I15 Direct Slice 2 verify regression** — direct GGS verify positive/mismatch/malformed paths and verify-result non-authority metadata are exercised before Slice 3 closure.
**I3-I16 Honest claim boundary** — local STC validation is not barrier/quorum/runtime qualification.

## 7. Frozen acceptance cases

- I3-01 frozen STC required fields exactly equal implementation constant.
- I3-02 frozen SemanticHeads required fields exactly equal implementation constant.
- I3-03 valid LAS local STC passes.
- I3-04 LAS false semantic binding, null heads, GGS fields present, or missing stream head each reject.
- I3-05 valid GGS with semantic binding false and null semantic_heads passes.
- I3-06 valid GGS with semantic binding true and exact SemanticHeads passes.
- I3-07 GGS nested field mismatch rejects for every mapped member.
- I3-08 GGS nested state-root digest mismatch/malformed digest rejects.
- I3-09 Sequence min/max pass; negative/max+1/bool/string/float reject.
- I3-10 highest_applied_index null or valid Sequence passes; malformed values reject.
- I3-11 empty/non-NFC/noncharacter IDs/digests reject; opaque non-SHA generic digests remain allowed.
- I3-12 malformed STC state_root_digest rejects while opaque stc_digest remains allowed.
- I3-13 semantic_heads missing/extra/empty-value rejects.
- I3-14 validation result metadata remains authority NONE and no current/certified self-grant.
- I3-15 failure does not poison subsequent valid LAS/GGS validation.
- I3-16 direct Slice 2 GGS verify and verify-metadata regressions pass; inherited I1/S1R/S1R2/I2 and regressions remain green; frozen dependency bytes unchanged.

## 8. Workflow hardening

Slice 3 CI must trigger on direct changes to:
- Slice 3 preregistration;
- Slice 3 validator module;
- Slice 3 frozen acceptance harness;
- Slice 3 marker;
- Slice 3 workflow itself;
- the Slice 2 state-root dependency module.

The exact candidate is still SHA-bound by the final run; workflow triggering is defense-in-depth.

## 9. Construction sequence

1. Commit this preregistration.
2. Add Slice 3 workflow and frozen acceptance harness with no Slice 3 mechanism.
3. Preserve expected RED mechanism-absence evidence.
4. Implement only the narrow local STC validator.
5. Require I3-01..I3-16 + inherited Slice 1/Slice 2 suites on one exact candidate.
6. Freeze exact candidate.
7. Build fresh blind independent review packet.
8. Require fresh independent review before bounded Slice 3 adjudication.

## 10. Claim boundary

A positive Slice 3 result proves only local deterministic STC shape/cross-field validation under
tested conditions. It grants no sequencing, certificate, quorum, barrier, runtime, release,
deployment, production, policy, or terminal authority.
