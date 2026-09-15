# V16 Slice 1 — Internal Adversarial Review 006

Status: **NEW LOAD-BEARING DEFECTS FOUND / REPAIR REQUIRED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound green construction candidate

- candidate commit: `2a305c8b4604e70c00fe818fd0f6c34a6bb556e8`
- candidate tree: `bf2faa1168fb6a25faa9cc1dd36c6d5addf5d61f`
- V2 construction run: `34984651272`
- mandatory tests: `77/77 PASS`
- composite manifest/source/execution equality: `PASS`

The green is preserved as construction evidence only. This review attacks the claim that authenticated policy identity now covers the verifier semantics that actually decide acceptance, and it attacks CI stopping-rule ambiguity.

## Overall disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

## Critical V16-S1-IAR6-001 — Validation-profile digest still does not bind the exact verifier implementation that enforces it

### Mechanism

`validation_profile_digest()` hashes a declarative material structure containing selected constants: field sets, canonicalization descriptors, role policy, algorithm names and signature domains. The actual acceptance semantics live in Python functions such as `_validate_snapshot`, `_verify_bootstrap_signatures`, `_validate_chain_owned`, `_validate_pinned_registry_head_with_profile`, and `verify_signed_governance_record`.

A code change can alter those functions without changing any field included in `validation_profile_material()`. Concrete examples include removing the cross-tier bootstrap/governance public-key check, weakening key-removal/revocation rules, changing currentness checks, or changing threshold decision logic while leaving all declared profile constants unchanged. The profile digest would remain identical and an already bootstrap-signed registry/head/record could be reinterpreted by different executable verifier logic.

The repair also claims that key/signature byte sizes are profile-bound, but `validation_profile_material()` does not include `ED25519_PUBLIC_KEY_BYTES` or `ED25519_SIGNATURE_BYTES`.

### False-green path

1. Registry/head/record are validly signed with profile digest `P`.
2. Verifier implementation is changed so one load-bearing validation rule is weakened while the declared profile material is left unchanged.
3. `validation_profile_digest()` still returns `P`.
4. Existing signed state passes the profile-equality checks but is evaluated under weaker executable semantics.

### Narrow repair

Bind an exact validator-artifact identity in addition to the declarative profile. For this Python construction slice, compute SHA-256 over the exact validator source artifact actually imported/executed and bind that digest into the bootstrap-signed registry, pinned current head and signed governance envelope. Current verification must recompute the local artifact digest and require exact equality across all three. Preserve the declarative profile as a human/machine policy descriptor, but do not treat it alone as executable-semantic identity. Runtime packaging/attestation remains a later qualification boundary.

## Critical V16-S1-IAR6-002 — Mixed-profile registry history is revalidated under only the current verifier semantics

### Mechanism

`_validate_chain_owned()` requires only the **current** registry snapshot's `authority_policy_digest` to equal the current verifier profile. Earlier registry snapshots may carry different profile digests, yet every earlier snapshot is structurally and semantically revalidated using the current Python verifier implementation and current role vocabulary/rules.

There is no versioned verifier dispatch keyed by each historical snapshot's bound profile and no rule requiring one profile/artifact identity across the whole registry chain.

### False-green path

A historical snapshot that was invalid under the policy/verifier identity it claims to bind can later become accepted when a newer verifier generation interprets the old bytes under different rules. Because historical snapshots determine key first appearance, immutability and revocation lineage, retroactive reinterpretation can affect present authority.

### Narrow repair

For Slice 1, fail closed on mixed verifier/profile identity: every registry snapshot in one chain must carry the exact same validation-profile digest and exact same validator-artifact digest. Any verifier/profile change must start a separately anchored registry epoch/genesis until a future version implements explicit cross-version transition certificates and historical verifier dispatch.

## High V16-S1-IAR6-003 — Two active construction workflows can produce contradictory green/red signals

### Mechanism

The repository still contains the original 64-test workflow and the newer V2 77-test composite workflow. A source change triggers both. The original workflow can report green while an IAR5 supplemental test in V2 fails.

No branch protection/required-status rule currently makes the 77-test V2 result the single canonical stopping signal.

### False-green path

A future candidate passes the original 64 tests but fails one of the 13 IAR5 regressions. GitHub then exposes a green `Review Safe Evidence V16 Slice 1 Trust Foundation` run next to a red V2 run. A consumer or automation selecting the old status can treat a known-red candidate as construction-green.

### Narrow repair

Retire the old workflow from active execution and preserve its historical runs. Keep one canonical Slice 1 construction workflow whose stopping rule verifies the complete mandatory set. Later repository rules should require the exact canonical check before any protected transition.

## Medium V16-S1-IAR6-004 — Construction environment remains reproducible only partially

`cryptography==46.0.4` is version-pinned, but transitive artifacts (`cffi`, `pycparser`) are resolved without hash locking, and `ubuntu-24.04` identifies a mutable hosted-runner image family. The run records the observed image/version, but construction does not cryptographically bind the entire environment.

This is not a new authority escalation because qualification remains unclaimed, but it must remain explicit evidence debt before runtime/implementation qualification.

## Stopping rule

Do not start Slice 2. Repair IAR6-001 through IAR6-003, preserve any new RED, obtain a governed green on the single canonical workflow, then perform another internal adversarial pass.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
