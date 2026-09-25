# R8 v15-r1 — Implementation Slice 5: Local QualifiedTimeProof Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

Closed Slice 4 evidence head:
`d91b800d0003bc12b31a32bc14685147686c43ee`

Exact closed implementation candidates:
- Slice 4: `3b60d8f14851b755f09a35431c620d6ae594a894`
- Slice 3: `9b8b519c1f32b675d102b1267511a6a141f39c4a`
- Slice 2: `6a8d0b0e4baa3a9df75dc47f626953b4dde51255`
- Slice 1: `fdf825cb45fbd00441a4cd02bb1912bb3cda01b0`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Open runtime qualification finding `R8V15R1-RTQ-OPEN-001` remains OPEN.

Slice 5 does not alter or close prior implementation hardening findings unless separately
governed and evidenced.

## 2. Goal

Implement a repository-local, pure validator for:
- `TimeSourceAttestation`;
- `QualifiedTimeProof`;

using only exact frozen local structure, type/lexical rules, and the explicit binding between
`QualifiedTimeProof.decision_preseal_digest` and a supplied locally valid
`DecisionPresealContext.decision_preseal_digest`.

This slice does NOT validate live time authority, nonce consumption, source status,
attestation signatures, source independence, freshness windows, or `time_proof_digest`
cryptographic correctness.

## 3. Frozen TimeSourceAttestation contract

Exact required fields:
1. `time_source_id`
2. `source_status_digest`
3. `attestation_digest`

No extras are allowed.

`time_source_id` is a non-empty opaque CanonicalId string.

`source_status_digest` and `attestation_digest` are non-empty opaque Digest strings.

All strings must pass inherited GCP authority-string validation.

This local validator does not prove:
- that the source exists in the current qualified source registry;
- that it was ACTIVE at the attestation sequence;
- that the source is independent from any other source;
- that attestation_digest is cryptographically valid.

## 4. Frozen QualifiedTimeProof contract

Exact required fields:
1. `nonce_256bit_hex`
2. `decision_preseal_digest`
3. `effective_sequence`
4. `source_attestations`
5. `time_proof_digest`

No extras are allowed.

### nonce_256bit_hex
Must match exactly:
`^[0-9A-Fa-f]{64}$`

The frozen schema permits upper/lower hex. This slice does not canonicalize case or invent
a nonce digest rule.

### decision_preseal_digest
Opaque non-empty Digest, but when a supplied DecisionPresealContext is validated alongside
the proof it must equal `DecisionPresealContext.decision_preseal_digest`.

NORM-032 requires a time proof to be bound to the decision preseal context.

### effective_sequence
Frozen Sequence closure:
`0 <= value <= 9223372036854775807`, with booleans rejected.

Slice 5 does not infer that effective_sequence must equal semantic_state_sequence unless a
future governed source explicitly freezes that equality.

### source_attestations
Frozen JSON type is `array`, with:
- minItems = 2
- maxItems = 3

The Python validator therefore accepts only an actual `list`, not arbitrary Sequence types
such as tuple. Each element must be an exact-shape TimeSourceAttestation.

The frozen schema does not declare `uniqueItems`; this local slice therefore does not invent
a uniqueness/independence rule. Duplicate source IDs may be structurally valid but carry
authority effect NONE until a later runtime/authority validator proves the required source
qualification/independence rules.

### time_proof_digest
Opaque non-empty Digest. Slice 5 does not invent a digest preimage or algorithm.

## 5. Supplied DecisionPresealContext dependency

The validator accepts:
- a `QualifiedTimeProof`;
- a supplied `DecisionPresealContext`;
- a supplied `AuthorityReadSet`;
- verifier-owned `external_effect_involved`.

Before checking the time-proof binding, it invokes the closed Slice 4 local
DecisionPresealContext validator.

Only after Slice 4 local validation succeeds does it require:
`QualifiedTimeProof.decision_preseal_digest == DecisionPresealContext.decision_preseal_digest`.

No other currentness/qualification claim is imported from Slice 4.

## 6. Frozen invariants

**I5-I01** TimeSourceAttestation field constant exactly equals frozen schema required fields.
**I5-I02** QualifiedTimeProof field constant exactly equals frozen schema required fields.
**I5-I03** source_attestations uses exact JSON-array semantics: Python list only, length 2..3.
**I5-I04** each source attestation has exact field shape and non-empty GCP-valid opaque strings.
**I5-I05** nonce is exactly 64 ASCII hex characters, case-insensitive as frozen.
**I5-I06** effective_sequence uses non-boolean signed-int64 non-negative closure.
**I5-I07** decision_preseal_digest/time_proof_digest remain opaque non-empty GCP-valid Digests.
**I5-I08** supplied DecisionPresealContext must pass closed Slice 4 local validation first.
**I5-I09** time proof decision_preseal_digest must exactly equal supplied DPS decision_preseal_digest.
**I5-I10** duplicate source IDs are not locally rejected because uniqueness is not frozen in schema.
**I5-I11** no nonce-ledger state, source ACTIVE status, source independence, freshness or signature validity is self-granted.
**I5-I12** time_proof_digest is not recomputed or marked verified.
**I5-I13** successful result metadata is explicit authority NONE and all runtime/time-authority claims false.
**I5-I14** failures do not poison subsequent valid validation.
**I5-I15** frozen schema and closed Slice 1/2/3/4 implementation modules remain unchanged.
**I5-I16** inherited full test stack stays green and Slice 5 workflow directly covers governed Slice 5 files plus closed Slice 4/Slice 1 dependencies used at runtime.

## 7. Frozen acceptance cases

- I5-01 TimeSourceAttestation required fields exactly match frozen schema.
- I5-02 QualifiedTimeProof required fields exactly match frozen schema.
- I5-03 valid proof with exactly 2 source attestations passes.
- I5-04 valid proof with exactly 3 source attestations passes.
- I5-05 source_attestations empty/1/4 entries and tuple form reject.
- I5-06 source attestation missing/extra fields reject.
- I5-07 empty/non-NFC/noncharacter source strings reject; opaque non-SHA digests pass.
- I5-08 nonce lower/upper/mixed 64-hex pass; wrong length/nonhex/non-string reject.
- I5-09 effective_sequence min/max pass; negative/max+1/bool/string/float reject.
- I5-10 supplied valid DPS/read set/effect context is locally revalidated before binding.
- I5-11 exact DPS digest binding passes; mismatch rejects.
- I5-12 decision_preseal_digest and time_proof_digest remain opaque non-empty; no SHA-only rule.
- I5-13 duplicate time_source_id values remain locally structural-valid but result explicitly states source independence not proven.
- I5-14 result metadata remains authority NONE; nonce_consumed/source_status_valid/source_independence_proven/freshness_proven/signature_verified/time_proof_digest_verified all false.
- I5-15 failed proof validation does not poison later valid validation.
- I5-16 dependency immutability + inherited I4/I3/I2/I1 test stack + direct workflow trigger coverage all pass.

## 8. Deferred / nonclaims

This slice does not prove:
- NonceLedger ISSUED/CONSUMED/EXPIRED state;
- single-use nonce consumption;
- source ACTIVE status at effective sequence;
- time-source registry membership or independence;
- attestation cryptographic signatures/MACs;
- freshness/replay window;
- local clock correctness;
- qualified time source availability;
- time_proof_digest cryptographic correctness;
- VerifiedStateSeal correctness;
- COMMIT_WITH_SEAL/current-head recheck;
- runtime qualification, release, deployment, production, policy or terminal authority.

## 9. Workflow hardening

Slice 5 CI must directly trigger on changes to:
- Slice 5 preregistration;
- Slice 5 validator module;
- Slice 5 frozen acceptance harness;
- Slice 5 marker;
- Slice 5 workflow itself;
- closed Slice 4 preseal validator;
- closed Slice 1 canonicalizer;
- inherited Slice 4/3/2/1 acceptance sources executed by the workflow.

This explicitly avoids the Slice 4 reviewer-noted trigger-coverage gap.

## 10. Construction sequence

1. Commit this preregistration.
2. Add direct-trigger Slice 5 workflow and frozen acceptance harness with no Slice 5 mechanism.
3. Preserve expected RED mechanism-absence evidence.
4. Implement only the bounded local time-proof validator.
5. Require I5-01..I5-16 plus inherited Slice 4/3/2/1 suites on one exact candidate.
6. Freeze exact candidate.
7. Build fresh blind independent review packet.
8. Require fresh independent review before bounded Slice 5 adjudication.

## 11. Claim boundary

A positive Slice 5 result proves only deterministic local QualifiedTimeProof structure and
DecisionPresealContext digest binding under tested conditions.

It does not establish qualified time, freshness, anti-replay, source independence, source
status, cryptographic attestation validity, seal validity, runtime qualification, release,
deployment, production, policy or terminal authority.
