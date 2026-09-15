# V16 Slice 1 — Internal Adversarial Review 003

Status: **NEW LOAD-BEARING DEFECTS FOUND / REPAIR REQUIRED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound green construction candidate

- candidate commit: `71a40cbef92a807d2b13714e8eda4655eba91873`
- candidate tree: `ee66422856f56618424077cd0a1f9212ea78210f`
- construction run: `34979376969`
- mandatory tests: `42/42 PASS`
- manifest/source/execution equality: `PASS`

The 42-test green is preserved as construction evidence only. This third internal pass attacks policy-selection, fork binding, and schema-type boundaries that were not falsified by the 42-test set.

## Overall disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

## Critical finding V16-S1-IAR3-001 — Record type → authority role policy is caller-selected

### Mechanism

`verify_signed_governance_record()` currently accepts both:

- `expected_record_type`;
- `required_role`.

It checks that the signed envelope repeats those caller-supplied values and that the resolved issuer key possesses the caller-supplied role. There is no canonical machine-enforced mapping from governance record type to the role authorized to issue that record type.

### Concrete false-green path

A key legitimately authorized only for `RAW_EVIDENCE_CAPTURE_AUTHORITY` can sign an envelope whose `record_type` is `BLOCKER_RESOLUTION` while setting `required_role` to `RAW_EVIDENCE_CAPTURE_AUTHORITY`. A caller that asks the generic verifier to validate that same pairing can receive a valid cryptographic/registry result even though raw-evidence capture authority must not imply blocker-resolution authority.

No key or signature is forged. The authority-policy relation itself is delegated to the caller.

### Governing rule violated

Load-bearing authority policy must be machine-enforced and cannot be selected by the party presenting the object for validation. Authenticated identity is insufficient if the validator lets the caller choose which role is required for the action.

### Narrow repair

1. Define a canonical `RECORD_TYPE_REQUIRED_ROLE` registry in the trust foundation for every V16 signed governance record type exposed by the implementation contract.
2. Remove `required_role` as a caller-selected validation input for current-authority verification, or treat any supplied value as non-authoritative metadata and derive the actual required role solely from the canonical mapping.
3. Reject unknown record types fail closed.
4. Add a regression proving that `BLOCKER_RESOLUTION` signed by a raw-evidence-only key is rejected even when the envelope claims the raw-evidence role.

## High finding V16-S1-IAR3-002 — Signed record does not bind the exact authenticated registry head/trust-set context

### Mechanism

The signed envelope currently binds `issued_registry_sequence` and `generation_id`, but it does not contain the exact issuance `registry_digest` or bootstrap `trust_set_id`.

The verifier separately compares the supplied chain to a pinned current head, but the issuer signature itself does not prove which exact registry snapshot/trust-set context the issuer intended.

### Concrete false-green path

Two bootstrap-authenticated registry forks can exist with the same registry ID, candidate ID, sequence and generation ID but different registry contents/digests. If issuer key K is valid in both, a record signed while operating under fork A can be replayed under fork B because the record signature contains no fork digest. A similar ambiguity exists if identical registry content/key material is admitted under two distinct trust sets.

The pinned head chooses the verifier's current fork; it does not prove that the signed record was issued for that exact fork.

### Governing rule violated

A signed authority-bearing object must bind the exact authoritative state against which its issuer was qualified, not only labels that can be shared by divergent histories.

### Narrow repair

Add at least:

- `trust_set_id`;
- `issued_registry_digest`

to the signed envelope and signature. Current-authority verification must require exact equality with the pinned current head/trust set. Add a two-fork regression proving a record signed for fork A cannot validate under pinned fork B even when issuer key, registry ID, sequence and generation labels are otherwise identical.

## High finding V16-S1-IAR3-003 — Python booleans satisfy several integer-only governance fields

### Mechanism

Python `bool` is a subclass of `int`. Checks such as:

`isinstance(sequence, int)`

therefore accept `True` as integer `1`. Load-bearing fields affected include registry/head sequence, signed-record issuance sequence, and key validity/revocation sequence checks.

Canonical JSON preserves `true` and `1` as different byte representations, but Python equality can subsequently make them compare equal (`True == 1`). This creates cross-implementation/schema ambiguity at precisely the currentness and key-validity boundary.

### Narrow repair

Introduce an exact-integer helper such as `type(value) is int` plus range rules, and use it for every integer governance field. Add regressions that boolean values are rejected for registry sequence, pinned-head sequence, issuance sequence, validity sequence, and revocation sequence.

## Explicit residual boundary

This review does not reclassify the already-declared external boundaries as repaired:

- bootstrap root provisioning/ownership remains out-of-band and unproven;
- pinned current-head freshness/provisioning remains out-of-band and unproven;
- control-domain ancestry/shared-ancestor proof remains a later V16 slice;
- package/dependency artifact authenticity remains open;
- downstream V15 surface migration has not begun.

## Stopping rule

Do not start Slice 2. Repair IAR3-001 through IAR3-003, preserve all intermediate REDs, extend the stable mandatory manifest without renumbering prior tests, obtain a clean governed construction run, and perform another adversarial pass.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
