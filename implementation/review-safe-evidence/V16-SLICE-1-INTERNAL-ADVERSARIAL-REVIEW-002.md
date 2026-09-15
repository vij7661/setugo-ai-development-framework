# V16 Slice 1 — Internal Adversarial Review 002

Status: **NEW LOAD-BEARING DEFECTS FOUND / REPAIR REQUIRED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound green construction candidate

- candidate commit: `3ec1d2b4ba8e5b404d46a68fde2cadff753cb547`
- candidate tree: `adb6b996fb5bb3a69f2f8e10ca0c1bee53aa9f11`
- construction run: `34978199943`
- mandatory tests: `38/38 PASS`
- manifest/source/execution set equality: `PASS`

The green construction evidence is preserved. This second internal review attacks trust/currentness assumptions not falsified by the 38-test set.

## Overall disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

## Critical finding V16-S1-IAR2-001 — A stale but correctly signed registry prefix can self-declare itself “current”

### Mechanism

`verify_signed_governance_record()` receives only a caller-supplied `registry_chain`. `_validate_registry_chain_internal()` authenticates every supplied snapshot under the bootstrap roots and then treats the **last supplied snapshot** as `current`.

There is no independently supplied current-head anchor binding the expected:

- registry ID;
- current sequence;
- current registry digest;
- current governance generation.

### Concrete false-green path

1. Registry sequence 1 contains key K as ACTIVE and is correctly threshold-signed by bootstrap roots.
2. Registry sequence 2 correctly revokes K and is also threshold-signed.
3. The authoritative world has advanced to sequence 2.
4. An attacker/replaying caller supplies only the valid historical prefix `[sequence 1]` plus a record signed by K under generation 1.
5. The validator sees sequence 1 as the last supplied snapshot, therefore calls it current and can return a valid current-authority result.

No signature is forged. The false green comes from **replay/currentness ambiguity**, not broken cryptography.

### Governing rule violated

Authenticated provenance is insufficient unless currentness is independently bound. A stale, correctly signed authority state must not regain current authority merely because a caller truncates later history.

### Narrow repair

Introduce a separately provisioned `PinnedRegistryHead`/currentness anchor containing at least:

- trust-set ID;
- registry ID;
- candidate ID;
- current sequence;
- current generation ID;
- current registry digest.

Current-authority verification must require this input and require the supplied chain's final snapshot to match it exactly. The anchor must not be derived from the chain inside the current-authority validator. The module must continue to state that host provisioning/freshness of this anchor is an external trust boundary not proven by construction code.

Add an adversarial regression in which sequence 2 revokes K, but the validator is given only the sequence-1 prefix against a sequence-2 pinned head; validation must fail closed.

## High finding V16-S1-IAR2-002 — Governance key registry permits one cryptographic key to masquerade as multiple authority identities/control domains

### Mechanism

`validate_bootstrap_trust_set()` now rejects duplicate bootstrap public-key material, but `_validate_registry_snapshot_structure()` does not apply the same uniqueness rule to governance issuer keys.

Two registry entries can therefore have:

- different `issuer_id`;
- different `key_id`;
- different `control_domain_id`;
- different roles;
- the same Ed25519 public-key bytes.

The same private key can then sign as both identities.

### False-green consequence

Any later quorum or independence layer that treats issuer/control-domain labels as distinct could count one cryptographic actor multiple times. This is a direct identity-alias path at the trust foundation and must be removed before Slice 2 can rely on registry identities.

### Narrow repair

Reject duplicate decoded Ed25519 public-key bytes across all key entries in each registry snapshot, including revoked entries. Because historical keys are append-preserved, this also prevents later key-ID relabeling/reuse. Add a regression that two issuer/domain labels sharing the same public key make the registry invalid.

## Medium finding V16-S1-IAR2-003 — Lone UTF-16 surrogate code points are not explicitly rejected by canonicalization

### Mechanism

The restricted canonicalizer NFC-normalizes strings and later UTF-8 encodes them. A string containing a lone surrogate can cause a `UnicodeEncodeError` rather than the governed `CanonicalizationError` fail-closed path.

### Narrow repair

Explicitly reject code points in `U+D800..U+DFFF` during string/key normalization and add a deterministic regression. Malformed Unicode must become an ordinary invalid-record result rather than an unhandled exception at a validation boundary.

## Residual already known and not closed by this review

The following remain explicitly outside Slice 1 mechanism proof and cannot be silently inferred from green tests:

- real independent provisioning/freshness of bootstrap roots;
- real independent provisioning/freshness of the proposed current-registry-head anchor;
- control-domain ancestry and shared-ancestor detection;
- dependency artifact/hash locking;
- downstream migration to authenticated V16 envelopes.

## Stopping rule

Do not start Slice 2 yet. Repair IAR2-001 and IAR2-002, add the Unicode fail-closed regression, expand the stable mandatory manifest without changing existing requirement-test IDs, preserve any intermediate RED, and rerun. Then perform another internal adversarial pass on the repaired Slice 1 foundation.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
