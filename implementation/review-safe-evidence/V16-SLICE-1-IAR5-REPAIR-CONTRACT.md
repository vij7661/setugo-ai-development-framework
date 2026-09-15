# V16 Slice 1 — IAR5 Repair Contract

Status: **CONSTRUCTION REPAIR / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This contract binds the repair of `V16-SLICE-1-INTERNAL-ADVERSARIAL-REVIEW-005` before any Slice 2 work may begin.

## Required repaired mechanisms

The Slice 1 validator must not validate caller-owned live object graphs and then later re-read mutable values as if they were the authenticated values. Authority-bearing registry chains and signed records are copied into owned plain-JSON containers at the validation boundary. Non-plain mappings or unsupported containers fail closed. The out-of-band bootstrap trust set must use immutable tuple/frozenset containers, and its members must be copied before a decision.

Serialized strict ingress must preserve string spellings so a load-bearing identifier that is not already NFC canonical is rejected by semantic validation rather than silently normalized into acceptance. Duplicate object keys and normalized key collisions remain rejected.

Bootstrap-root public keys and operational governance public keys occupy separate cryptographic tiers. A governance registry snapshot that reuses any current pinned bootstrap Ed25519 public key fails closed, including both genesis and later key introduction.

The authenticated authority-policy digest is expanded into a complete load-bearing validation-profile digest. It covers the record-type/role mapping, exact registry/signed-record field sets, canonicalization profile, integer range, key/signature sizes, supported algorithms, and signature domain-separation constants. A verifier-profile change therefore changes the digest and cannot silently reinterpret previously authenticated current state.

The canonicalization profile is explicit and test-vectored: UTF-8 JSON, NFC string normalization for signed representation, Unicode scalar/code-point object-key order, deterministic escaping, lowercase `\u00xx` control escapes, no floats, interoperable integer range, and no lone surrogates. Semantic identifiers must independently be supplied in canonical NFC form.

## Mandatory adversarial set

The established 64-test manifest remains preserved as:

`governance-runtime/review-safe-evidence-v16-slice1-test-manifest.json`

IAR5 adds the stable 13-test supplement:

`governance-runtime/review-safe-evidence-v16-slice1-test-manifest-iar5.json`

The governed construction set is the exact union: **77 mandatory test IDs**. CI must prove exact equality among the union of both manifests, the static test functions in both test modules, and the raw unittest `... ok` execution IDs. Missing, skipped, renamed, undeclared, or duplicate IDs fail closed.

## Preserved limitations

This repair does not prove the real-world provisioning, ownership, independence, or freshness of the bootstrap trust set or current-head pin. It does not yet implement control-domain ancestry/shared-root recomputation, downstream V15 relational repairs, full schema execution, effect authority, implementation qualification, runtime qualification, or scientific authority. Python dependency artifacts/transitives are still not hash-locked and remain an explicit evidence/environment residual.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
