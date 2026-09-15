# V16 Slice 1 — Internal Adversarial Review 005

Status: **NEW LOAD-BEARING DEFECTS FOUND / REPAIR REQUIRED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound green construction candidate

- candidate commit: `9087d79c95d9a09ae4aa46a6b487cb312aeeb8b7`
- candidate tree: `f8f5aaf448771ef35e01e35dd874555a2641e6b9`
- construction run: `34982513762`
- construction job: `104426147460`
- mandatory tests: `64/64 PASS`
- manifest/source/execution equality: `PASS`

The 64-test green is preserved in `V16-SLICE-1-CONSTRUCTION-EVIDENCE-005.md` as non-authoritative construction evidence. This fifth internal pass attacks whether the repaired content bindings remain trustworthy under mutable in-process inputs, strict serialized ingress, cross-tier key aliasing, and later verifier-policy drift.

## Overall disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

## Critical finding V16-S1-IAR5-001 — validation authenticates mutable objects and later re-reads the same mutable references

### Mechanism

The public validation functions accept generic `Mapping` / `Sequence` objects. `_validate_chain()` validates the supplied registry objects and then retains references to the original mappings in `current` and `snapshots_by_sequence`. `verify_signed_governance_record()` subsequently re-reads those mappings for currentness, generation, roles, key state, control domain and public-key verification.

The bootstrap trust dataclass is frozen only at the top level; Python does not enforce that callers actually pass the annotated `tuple` / `frozenset` containers. A caller can supply mutable roots or candidate-domain collections. The authority-policy mapping is also a mutable global dictionary.

Therefore the bytes/state checked at one point in the function are not guaranteed to be the bytes/state later used to grant the generic `valid` result.

### Concrete false-green paths

1. A registry snapshot is bootstrap-signature-verified with governance key K1 and safe role/domain values.
2. After chain validation but before the later key lookup/signature step, a concurrent caller or adversarial mapping mutates the referenced key entry to attacker key K2 and/or different role/domain/state values.
3. The later verification path reads K2 from the already-accepted mapping without recomputing the registry digest or bootstrap signature over the changed object.
4. An attacker-signed governance record can therefore be checked against state different from the state that the roots authenticated.

A similar TOCTOU exists for signed-record fields themselves: semantic checks and the final signature-message construction re-read the caller-owned mapping at different times. A custom `Mapping` can even return different values on successive reads without a thread.

For bootstrap trust, a mutable root list could be changed after `trust_set_digest` validation but before `_verify_bootstrap_signatures()` constructs its root index. That permits signer membership used for threshold verification to diverge from membership represented by the validated trust-set digest.

### Governing rule violated

Authenticated bytes must be the exact immutable bytes whose semantics are later consumed. Validation must not authenticate one state and authorize based on a later caller-mutated state.

### Narrow repair

1. At every public ingress, materialize an owned exact JSON snapshot once and use only that snapshot for the entire validation decision.
2. Reject adversarial/custom mappings or recursively copy to exact built-in JSON types before any load-bearing read; do not return/use references to caller-owned registry records.
3. Enforce exact immutable container types for `PinnedBootstrapTrustSet` (`tuple` roots and `frozenset` candidate-domain IDs) or canonical-snapshot them before validation and use only the snapshot.
4. Freeze the record-type→role policy rather than exposing a mutable global dictionary.
5. Add adversarial tests using mutation-capable mappings/containers and demonstrate that post-snapshot mutation cannot alter the validated decision.

## Critical finding V16-S1-IAR5-002 — authority-policy digest covers the role map but not the rest of the load-bearing verifier semantics

### Mechanism

`authority_policy_digest()` binds `AUTHORITY_POLICY_VERSION` plus the record-type→required-role mapping. Other load-bearing interpretation rules remain code-local and can change without changing the digest currently bound into registry/head/envelope state. Examples include exact field schemas, exact-integer rules, NFC-identifier policy, accepted algorithms, signature domain-separation labels, role vocabulary, and canonicalization profile.

### Concrete false-green path

1. A fully signed governance envelope with `schema_version = true` is invalid today because `_schema_one()` requires exact integer type.
2. Registry, pinned head and envelope can all carry the same unchanged `authority_policy_digest` because the record-type→role mapping has not changed.
3. A later verifier update changes schema interpretation back to equality-style `schema_version == 1` or otherwise relaxes a load-bearing validation rule without modifying the role map.
4. The previously invalid signed object becomes valid although no governance generation or authenticated policy digest changed.

The same class of retroactive reinterpretation exists for changes to accepted signature algorithms, identifier policy or exact field sets.

### Governing rule violated

A load-bearing policy/interpretation change must create governed state/generation change. Binding only one subsection of verifier semantics is insufficient to prove that an old signature is still interpreted under the policy under which it was admitted.

### Narrow repair

Introduce a canonical `validation_profile_digest` covering at least: canonicalization-profile identifier/version; registry and signed-envelope schema field sets/version rules; supported signature algorithms and domain-separation labels; identifier-canonicality policy; role vocabulary; and record-type→role mapping. Bind that digest into every registry snapshot, pinned current head and signed governance envelope, and require exact equality to the verifier's current profile before accepting current authority. Keep implementation correctness itself subject to testing and independent review; a digest is policy identity, not proof that code implements the declared profile.

## High finding V16-S1-IAR5-003 — the strict JSON ingress silently normalizes non-NFC identifier values before semantic canonicality checks

### Mechanism

The direct mapping path now rejects load-bearing identifiers whose spelling is not already NFC. However `load_strict_json()` ends by calling `_normalize(parsed)`, which NFC-normalizes every string value. `verify_signed_governance_record_json()` and `validate_governance_key_registry_chain_json()` therefore pass already-normalized identifiers to `_require_identifier()`.

### Concrete false-green path

A serialized envelope or registry can carry decomposed `e + combining acute` in a load-bearing ID. Direct mapping validation rejects that spelling, but strict JSON ingress silently converts it to composed `é` before semantic validation and can accept it. Thus two ingress paths enforce different identity contracts and the exact wire spelling is not rejected as required by IAR4-003.

### Governing rule violated

Load-bearing identifiers must already be canonical NFC; noncanonical spellings are to be rejected, not silently repaired before uniqueness/lookup.

### Narrow repair

Preserve string values exactly during strict JSON parsing while still rejecting malformed UTF-8, duplicate/normalized-duplicate object keys, floats, out-of-range integers and lone surrogates. Let the load-bearing identifier validators reject non-NFC values. Canonical hashing may still normalize content according to the declared canonicalization profile. Add strict-JSON regressions for decomposed root IDs, key IDs, candidate/generation IDs and signed-envelope IDs.

## High finding V16-S1-IAR5-004 — bootstrap-root and governance-key public-key uniqueness are checked in separate namespaces

### Mechanism

`validate_bootstrap_trust_set()` prevents public-key reuse among bootstrap roots. `_validate_snapshot()` prevents reuse among governance keys within a registry snapshot. It does not reject a governance key whose decoded Ed25519 public key is identical to one of the bootstrap-root public keys.

This contradicts the Slice 1 contract statement that bootstrap and governance public-key material are unique so one private key cannot masquerade as multiple nominal identities.

### Concrete failure path

A bootstrap root key can simultaneously appear as an operational governance issuer under another key/issuer/control-domain label. Compromise or control of that one private key therefore crosses the root/operational role boundary even though nominal identities differ. Declared domain/role separation can look stronger than the actual cryptographic-key separation.

### Narrow repair

During every registry-snapshot validation, decode the pinned bootstrap-root public keys and reject any governance key whose public bytes equal any bootstrap-root public bytes. Add regressions proving cross-tier key reuse is rejected at genesis and on later key introduction.

## Medium finding V16-S1-IAR5-005 — cross-implementation canonicalization profile is still implicit in Python behavior

The current implementation uses NFC plus Python `json.dumps(... sort_keys=True, separators=(",", ":"), ensure_ascii=False)` with floats forbidden and integers bounded to `2^53-1`. That is deterministic inside this Python implementation, but the exact property-name ordering/escaping profile is not given a normative cross-language identifier/specification. An independent implementation could reasonably implement RFC 8785/JCS ordering and disagree on edge Unicode property names while both believe they are canonical.

Narrow repair: make the canonicalization profile an explicit versioned part of the new validation profile, document its byte-level ordering/escaping rules or adopt a named normative standard/profile, and add edge-vector fixtures for non-BMP/BMP key ordering and escaping.

## Previously declared residuals remain open

- real-world bootstrap-root ownership/provisioning and current-head freshness/provisioning remain external and unproven;
- control-domain ancestry/shared-root resolution remains a later V16 slice;
- dependency artifacts/transitives remain not fully hash-locked;
- downstream V15 governance surfaces remain unmigrated;
- no implementation, runtime, scientific, release, terminal or effect authority is claimed.

## Stopping rule

Do not start Slice 2. Repair IAR5-001 through IAR5-004 and the validation-profile/canonicalization identity part of IAR5-005, preserve any construction RED, obtain a new governed green with exact manifest/source/execution equality, then perform another internal adversarial pass. A same-model pass remains internal evidence only.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
