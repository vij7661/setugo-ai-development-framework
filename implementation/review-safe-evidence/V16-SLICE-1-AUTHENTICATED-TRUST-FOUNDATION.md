# V16 Slice 1 — Authenticated Provenance and Root-of-Trust Foundation

Status: **CONSTRUCTION IMPLEMENTATION / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 1. Scope

This is the first implementation slice under the frozen V16 successor-remediation scope.

It addresses the foundation required before repairing downstream V15 validators:

- `AUTHENTICATED_PROVENANCE_AND_ROOT_OF_TRUST`;
- the issuer-authentication portion of `REGISTRY_BACKED_AUTHORITY_AND_INDEPENDENCE_RESOLUTION`;
- canonical signed-object serialization needed by later relational binding work.

It does **not** yet claim completion of control-domain ancestry, downstream evidence/universe/projection/monitor/snapshot/effect repairs, implementation qualification, runtime qualification, release authority, scientific authority, or terminal authority.

## 2. V15 failure repaired by this slice

V15 treated SHA-256 self-hashes and caller-declared authority fields as if they could support provenance. An attacker able to manufacture a record could change its load-bearing fields and recompute its digest.

V16 Slice 1 makes these concepts separate:

1. **Content integrity** — SHA-256 over a restricted canonical JSON representation.
2. **Issuer authenticity** — Ed25519 signature over the exact signed envelope.
3. **Authority admissibility** — signer key and role must exist in the current bootstrap-authenticated governance key registry.
4. **Root of trust** — registry snapshots require a threshold of signatures from distinct control domains in an out-of-band pinned bootstrap trust set.

A content digest alone never authenticates an issuer.

## 3. Out-of-band root boundary

`PinnedBootstrapTrustSet` is a host-provisioned trust input. It is deliberately not read from the candidate record being validated.

The implementation verifies:

- root IDs and key IDs;
- Ed25519 public keys;
- at least two distinct root control domains;
- threshold satisfaction by distinct authenticated root domains;
- candidate-controlled root-domain exclusion when supplied by trusted configuration.

The implementation **cannot prove how the embedding host obtained the trust set**. Therefore every result includes:

- `trust_anchor_origin = OUT_OF_BAND_PINNED_CONFIG_REQUIRED`;
- `trust_anchor_provisioning_proven = false`;
- `qualified = false`;
- `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`.

A later deployment/qualification stage must establish the actual bootstrap ceremony, control ownership and provisioning channel independently.

## 4. Canonical serialization

The signing profile accepts only:

- JSON null;
- booleans;
- integers;
- strings;
- arrays;
- objects with string keys.

It rejects floating-point numbers and unsupported Python types. Strings and keys are normalized to Unicode NFC. Normalized key collisions are rejected.

Serialized inputs can be parsed through `load_strict_json`, which rejects duplicate keys, normalized duplicate keys, floats and invalid UTF-8/JSON.

Canonical byte encoding is UTF-8 JSON with deterministic sorted keys and no insignificant whitespace.

This is a deliberately restricted profile rather than a claim of full RFC 8785/JCS compatibility.

## 5. Governance key registry

Each `GOVERNANCE_KEY_REGISTRY` snapshot binds:

- candidate ID;
- governance generation ID;
- registry sequence;
- predecessor registry digest;
- issuer/key/control-domain identity;
- Ed25519 public key;
- immutable role set;
- key state and effective registry sequence.

Registry content receives a SHA-256 content digest. That digest is then signed by a threshold of pinned bootstrap roots.

Registry-chain rules are fail closed:

- first snapshot is sequence 1 with predecessor `GENESIS`;
- every later snapshot increments sequence by exactly one;
- predecessor digest must equal the prior snapshot's digest;
- every registry update requires a new governance generation ID;
- prior key IDs cannot disappear;
- issuer ID, control domain, algorithm, public key, roles and `valid_from_registry_sequence` are immutable for an existing key ID;
- a revoked key cannot be reactivated;
- revocation must bind to the current registry sequence;
- a single issuer ID cannot span multiple control domains within a registry snapshot.

Key privilege expansion therefore requires a new key ID and a new bootstrap-authenticated registry generation.

## 6. Signed governance records

A signed governance envelope binds:

- record type and record ID;
- candidate ID;
- governance generation ID;
- optional snapshot ID;
- registry sequence under which it was issued;
- issuer ID and key ID;
- required authority role;
- exact payload digest and payload;
- signature algorithm.

The Ed25519 signature covers the complete canonical envelope except the signature bytes themselves.

Verification does not trust a caller-supplied "valid result" mapping. It directly:

1. revalidates the supplied registry chain under the pinned bootstrap roots;
2. resolves the key from the current registry;
3. verifies issuer/key binding;
4. verifies required role;
5. rejects forbidden or candidate-controlled issuer domains;
6. verifies key validity and current active state;
7. recomputes the payload digest;
8. verifies the exact Ed25519 signature.

Revoked keys cannot grant current authority even for records signed before revocation. Historical-evidence semantics, if later required, must be implemented as a separate non-authority verification path.

## 7. Cryptographic provider

Construction dependency:

`cryptography == 46.0.4`

The implementation accepts Ed25519 only. Unsupported or unavailable cryptographic providers fail closed.

Private keys are never accepted by the validation API and are not stored in governance records. Test private keys exist only as deterministic test fixtures.

## 8. Mandatory adversarial tests

The slice has a stable machine-readable mandatory-test manifest:

`governance-runtime/review-safe-evidence-v16-slice1-test-manifest.json`

CI must prove exact equality between:

- test IDs declared mandatory in the manifest;
- test IDs statically present in the frozen test source;
- test IDs actually reported `ok` by the construction run.

Missing, skipped, renamed or undeclared tests fail the workflow.

The adversarial matrix includes:

- recompute-SHA-after-tamper attacks;
- attacker-generated signatures;
- unknown keys;
- role mismatch;
- candidate-controlled issuer domain;
- bootstrap threshold collapse;
- unknown bootstrap root;
- registry predecessor substitution;
- public-key substitution under an existing key ID;
- role expansion under an existing key ID;
- silent key removal;
- revoked-key reuse;
- generation rebinding;
- extra-field injection;
- duplicate/ambiguous canonical JSON keys.

## 9. Construction stopping rule for this slice

A green Slice 1 workflow means only:

`V16_SLICE1_AUTHENTICATED_TRUST_FOUNDATION = CONSTRUCTION_TESTS_PASS_NONAUTHORITATIVE`

It must not emit implementation qualification, runtime qualification, release readiness, scientific authority, effect authority or successor-completion claims.

The next implementation slice may consume this foundation only after preserving its exact source/test/dependency identity.

## 10. Known residuals after Slice 1

The following remain open by design:

- out-of-band bootstrap trust provisioning is not proven by this code;
- control-domain ancestry and independent-root recomputation are not yet integrated;
- downstream V15 records are not yet migrated to signed V16 envelopes;
- real upstream-object relational binding remains unimplemented;
- executable full schema system remains incomplete;
- effect authority remains closed;
- no external reviewer/provider API is invoked by this construction slice.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
