# V16 Slice 1 — Internal Adversarial Review 001

Status: **DEFECTS FOUND / REPAIR REQUIRED / CONSTRUCTION GREEN PRESERVED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound construction candidate

- candidate commit: `c94db68bdff477ad749109de28085f5a6a4bed4a`
- candidate tree: `d9be4130fc52c165ddf2db1e56bafe3002e979b5`
- construction run: `34975785276`
- construction result: `30/30 PASS`

The green run is preserved as construction evidence. This review does not rewrite it as failure; it identifies adversarial mechanisms not represented in the original 30-test manifest.

## Overall disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

## Critical finding V16-S1-IAR-001 — Bootstrap threshold signatures are relabelable if pinned roots reuse key material

### Mechanism

`registry_signature_message()` signs only:

`RSE-V16:KEY-REGISTRY:<registry_digest>`

The signed message does not bind:

- bootstrap trust-set identity;
- `root_id`;
- root `key_id`;
- root control-domain identity.

`validate_bootstrap_trust_set()` also does not reject duplicate Ed25519 public-key material across nominally distinct roots.

### False-green path

A pinned trust set can contain:

- root A / domain A / public key K;
- root B / domain B / the same public key K.

One valid signature made by private key K over the registry digest can be copied twice. The second copy can change only `root_id`/`key_id` to root B. Both entries verify because the signed bytes are identical and both pinned roots expose the same public key. The validator then counts two distinct control-domain labels and can satisfy threshold 2 with one cryptographic signer.

### Narrow repair

1. Reject duplicate bootstrap public-key bytes across pinned roots.
2. Domain-separate each root signature with the exact `trust_set_id`, `root_id`, `key_id`, `control_domain_id`, and registry digest.
3. Add mandatory adversarial tests for duplicate-key trust sets and signature relabel/copy attacks.

## Critical finding V16-S1-IAR-002 — Registry/key issuance can be backdated across governance generations

### Mechanism

A new key introduced in registry sequence 2 can declare `valid_from_registry_sequence = 1`, because structure validation only requires `valid_from <= current sequence`.

`verify_signed_governance_record()` resolves the key only from the current registry and checks only:

- `issued_registry_sequence <= current_registry_sequence`;
- `issued_registry_sequence >= key.valid_from_registry_sequence`.

It does not prove that the key actually existed in the registry snapshot identified by `issued_registry_sequence`, nor that the record generation equals the generation at that registry sequence.

### False-green path

1. Registry sequence 1 does not contain key K.
2. Sequence 2 introduces K but sets `valid_from_registry_sequence=1`.
3. K signs a record with `issued_registry_sequence=1` and generation 2.
4. Current registry sequence 2 resolves K as active; all current checks can pass.

The record therefore obtains authenticated-looking provenance for a time/generation in which the key did not exist.

### Narrow repair

1. A newly introduced key must have `valid_from_registry_sequence == first appearance sequence`.
2. Current-authority verification must resolve the issuance registry snapshot, prove the key existed and was valid in that snapshot, and bind the record generation to that snapshot.
3. Because every registry mutation creates a new governance generation in this slice, current-authority verification must additionally require the record's issuance sequence and generation to equal the current registry sequence/generation. Historical signature verification, if later required, must be a separate evidence-only API that cannot grant current authority.

## High finding V16-S1-IAR-003 — Caller-selected expected generation is not independently tied to current registry generation

`verify_signed_governance_record()` accepts `expected_generation_id` from its caller but does not require it to equal the authenticated current registry generation.

A caller can therefore select an older generation context while presenting a newer registry chain, subject to the existing key-validity checks.

This is repaired by the same current-sequence/current-generation binding required for V16-S1-IAR-002.

## Medium residual V16-S1-IAR-004 — Serialized-record strict parsing is optional at the public API boundary

`load_strict_json()` correctly rejects duplicate keys, normalized key collisions and floats. However, the registry and signed-record validators accept already-parsed `Mapping` objects. If an external serialized object was first parsed by an unsafe parser that collapsed duplicate keys, the validator cannot reconstruct the discarded ambiguity.

Narrow repair for downstream integration: expose byte/string ingress helpers that call `load_strict_json()` internally and designate mapping validators as trusted/internal construction APIs. Do not claim raw-wire ambiguity protection when callers bypass strict ingress.

## Medium residual V16-S1-IAR-005 — Python dependency version is pinned but artifact/transitive dependency identity is not

The workflow pins `cryptography==46.0.4`, but pip resolves transitive dependencies (`cffi`, `pycparser`) and package artifacts from the configured index without hash locking. The construction run observed `cffi 2.1.1` and `pycparser 3.0`, but the requirements file does not bind those artifacts.

This does not invalidate the Slice 1 mechanism result, but it remains a V16 evidence/environment reproducibility requirement. Use a hash-locked dependency set or equivalent independently bound environment before qualification evidence is claimed.

## Preserved posture

The original construction run remains:

`V16_SLICE1_AUTHENTICATED_TRUST_FOUNDATION=CONSTRUCTION_TESTS_PASS_NONAUTHORITATIVE`

It does not satisfy internal adversarial review after these new findings.

No downstream V16 slice may treat Slice 1 as stabilized until IAR-001, IAR-002 and IAR-003 are repaired and rerun with stable mandatory test IDs.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
