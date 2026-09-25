# R8 v15-r1 — Implementation Slice 2: Deterministic LAS/GGS State-Root Construction

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

Slice 1 bounded construction is closed at evidence head:
`194963c846fa62143aa03208d3617ca3f39dd173`.

Exact closed Slice 1 implementation candidate:
`fdf825cb45fbd00441a4cd02bb1912bb3cda01b0`.

Frozen executable-schema candidate remains:
`f93ca26975ecb64f0da13779889c75b36140cdfc`.

Open runtime-qualification finding
`R8V15R1-RTQ-OPEN-001` remains OPEN and is not resolved, weakened, or superseded by this slice.

This slice inherits the existing bounded implementation-construction authorization only.
It grants no runtime qualification, release, deployment, production, policy, or terminal authority.

## 2. Goal

Falsify whether repository-local code can construct and verify the exact frozen
`LASAuthorityStateRoot` and `GGSGenesisStateRoot` digest objects using the
already constructed Slice 1 GCP canonicalizer, without:

- adding, omitting, renaming, nesting, or reinterpreting frozen preimage members;
- treating generic input Digest fields as globally SHA-256 encoded;
- accepting caller-selected historical sequence/barrier values as current authority;
- allowing malformed sequence values or state-root digest encodings;
- including `state_root_digest` itself in its own preimage;
- treating successful digest recomputation as runtime/authority qualification.

This is a pure deterministic construction/verification slice. It performs no sequencing,
quorum verification, certificate validation, mutable authority lookup, filesystem write,
network access, or external effect.

## 3. Frozen source contracts

### LASAuthorityStateRoot

Frozen exact GCP-1 preimage member order/set from the executable schema:

1. `semantic_state_sequence`
2. `committed_log_prefix_digest`
3. `stream_head_map_root`
4. `idempotency_ledger_root`
5. `authority_state_machine_root`
6. `revocation_stream_head`
7. `nonce_ledger_head`
8. `effect_stream_head`
9. `csm5_registry_head`
10. `aim4_descriptor_head`
11. `any_scope_permission_head`
12. `aim_scope_policy_head`
13. `resolver_policy_head`
14. `resolver_implementation_registry_head`
15. `guard_registry_head`
16. `configuration_generation`
17. `prior_certificate_chain_digest`

Frozen formula:
`state_root_digest = SHA-256(GCP-1(exactly the 17-member object above))`.

No additional member is permitted in the preimage.

### GGSGenesisStateRoot

Frozen exact GCP-1 preimage member order/set:

1. `barrier_index`
2. `committed_log_prefix_digest`
3. `constitution_namespace_root`
4. `bootstrap_authorization_root`
5. `idempotency_ledger_root`
6. `configuration_generation`
7. `prior_certificate_chain_digest`

Frozen formula:
`state_root_digest = SHA-256(GCP-1(exactly the 7-member object above))`.

## 4. Included

- exact frozen-member-set constants for LAS and GGS roots;
- deterministic extraction of preimage fields from Python mappings;
- no missing/extra member tolerance;
- Sequence validation using the frozen signed-int64 non-negative range:
  `0 <= value <= 9223372036854775807`, with booleans rejected;
- generic Digest component validation as non-empty strings only, preserving the frozen
  "opaque Digest" rule rather than imposing global SHA-256 syntax;
- inherited GCP string/key validation through the Slice 1 canonicalizer;
- SHA-256 only for the root formula where the governing source explicitly fixes SHA-256;
- exact lowercase 64-hex `state_root_digest`;
- deterministic root verification;
- constant-time comparison for expected/observed root digests;
- non-authority result metadata.

## 5. Deferred / nonclaims

This slice does **not** implement or prove:

- that `semantic_state_sequence` is the current LAS committed index;
- that the named LAS heads were actually read from one coherent current LAS snapshot;
- that `barrier_index` is certified by a lawful ROTATION_PREPARE certificate;
- LAS/GGS quorum, log, voting, rollback, or durability behavior;
- STC construction or verification;
- CSM-5 `bundle_digest` construction;
- ResolverPolicy/RIR/RCS authority;
- runtime qualification;
- adversarial filesystem-race safety;
- release/deployment/production readiness.

A root whose digest recomputes correctly can still have authority effect NONE if its state
is historical, caller-selected, uncertified, stale, or otherwise not lawfully sourced.

## 6. Frozen invariants

**I2-I01 Exact LAS preimage set** — LAS construction requires exactly the 17 frozen
`x-gcp1-preimage-members`; missing or extra keys reject.

**I2-I02 Exact GGS preimage set** — GGS construction requires exactly the 7 frozen
`x-gcp1-preimage-members`; missing or extra keys reject.

**I2-I03 Schema/member parity** — implementation member constants must exactly equal the frozen
runtime schema's `x-gcp1-preimage-members` lists for both root types.

**I2-I04 Sequence closure** — LAS `semantic_state_sequence`, LAS/GGS
`configuration_generation`, and GGS `barrier_index` must be integers in
[0, 9223372036854775807]; booleans, negatives, max+1, decimals, and strings reject.

**I2-I05 Opaque Digest preservation** — component digest/head fields require non-empty strings and
GCP-valid authority-string encoding; they are not globally required to be SHA-256-looking strings.

**I2-I06 Exact root encoding** — computed `state_root_digest` is lowercase 64-hex SHA-256 of the
exact GCP-1 preimage bytes.

**I2-I07 No self-inclusion** — `state_root_digest` is not part of the preimage and supplying it to
a construction function as a preimage member rejects.

**I2-I08 Order independence of input mapping** — input mapping insertion order cannot change the
canonical preimage bytes or root digest.

**I2-I09 Member sensitivity** — changing any one preimage member changes the root digest.

**I2-I10 Verification fails closed** — verification rejects missing/extra members, malformed
`state_root_digest`, or any recomputation mismatch.

**I2-I11 No currentness self-grant** — construction/verification APIs never return
`current=true`, `certified=true`, `authority=true`, or an equivalent authority claim from caller input.

**I2-I12 Non-authority metadata** — successful results explicitly carry
`authority_effect="NONE"`, `runtime_qualified=false`, and no downstream authority.

**I2-I13 Determinism and statelessness** — repeated calls with identical values return identical
canonical preimage bytes/digest and retain no mutable weakening state after failures.

**I2-I14 Slice 1 dependency integrity** — Slice 2 uses the closed Slice 1 canonicalizer behavior;
it must not modify the Slice 1 module or any frozen executable-schema byte.

**I2-I15 Currentness remains external** — historical/caller-selected LAS sequence or GGS barrier
may be digested for forensic/reference purposes but are explicitly authority NONE until a later
governed runtime slice proves current/certified sourcing.

**I2-I16 Honest claim boundary** — a passing Slice 2 proves only deterministic root
construction/verification under tested conditions.

## 7. Frozen acceptance cases

- **I2-01** frozen runtime schema LAS member list equals the implementation LAS member constant.
- **I2-02** frozen runtime schema GGS member list equals the implementation GGS member constant.
- **I2-03** LAS known vector produces exact canonical preimage bytes and hardcoded SHA-256.
- **I2-04** LAS input-key permutation produces identical canonical bytes/root.
- **I2-05** LAS missing/extra/self-included member rejects.
- **I2-06** LAS sequence/config generation min/max pass; negative/max+1/bool/string reject.
- **I2-07** LAS one-member mutation changes root and old full-root verification fails.
- **I2-08** LAS full-root verification accepts exact result and rejects malformed/mismatched digest.
- **I2-09** GGS known vector produces exact canonical preimage bytes and hardcoded SHA-256.
- **I2-10** GGS missing/extra/self-included member rejects.
- **I2-11** GGS barrier/config generation boundaries behave exactly as I2-I04.
- **I2-12** opaque non-SHA-looking component digests are accepted when non-empty/GCP-valid.
- **I2-13** empty/non-NFC/noncharacter component digest strings reject.
- **I2-14** result metadata remains non-authoritative regardless of caller-supplied sequence/barrier.
- **I2-15** failure does not poison subsequent deterministic valid construction.
- **I2-16** original Slice 1 I1/S1R/S1R2 + post-freeze regressions remain green and
  frozen schema/Slice 1 module bytes are unchanged.

## 8. Construction sequence

1. Commit this preregistration before the Slice 2 harness or mechanism.
2. Add the frozen I2-01..I2-16 acceptance harness with no Slice 2 implementation module.
3. Preserve the expected RED mechanism-absence run.
4. Add only the narrow deterministic state-root implementation.
5. Require I2-01..I2-16 plus all inherited Slice 1 acceptance/regression suites on one exact candidate.
6. Preserve all construction/control failures without reclassification.
7. Freeze one exact Slice 2 candidate SHA.
8. Require a fresh blind independent implementation review before bounded Slice 2 adjudication.
9. A Slice 2 construction pass grants no runtime qualification or downstream authority.

## 9. Claim boundary

A positive Slice 2 result establishes only that the repository-local reference implementation
can construct and verify the exact frozen LAS/GGS root-digest objects under tested conditions.

It does not establish that a root came from current lawful authority state, a lawful barrier,
a valid quorum/certificate, or a production-qualified runtime.
