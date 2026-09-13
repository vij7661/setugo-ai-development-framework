# V24 I11 Manual / External Evidence Collection Packet V1

Packet class: **EVIDENCE COLLECTION / MANUAL REVIEW PREPARATION ONLY**  
Scientific execution effect: **NONE**  
Authority effect: **NONE_EVIDENCE_ONLY**

## Exact binding

- Pre-scientific frontier: `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`
- Frontier tree: `f9de48189b7d304f50f169277dc1b4dceb642546`
- Frozen V24 design: `db9e4b349fd26e128f4486878a4af64929000a7c`
- Frozen I10 implementation: `9836dc3ff233cca582f485434fc1c6494cf7eb05`
- Frozen I10 tree: `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`
- Reviewed V8 packet SHA-256: `e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e`
- Reviewed V8 body SHA-256: `3b442e55bec52aec24042d714d4064985eb85acf914afa5903d00d1a61b373ab`
- V8 review-binding blob: `716a2a2917130c898cc4244d44cf0141e49dd83e`
- Harness V7 blob: `6573767ae85d7ca0cfaa8b7bbafa826a7ba0c5cb`

The reviewed V8 packet bytes are not materialized in the frozen repository tree. Therefore this packet records only evidence requirements explicitly present in the repository case projection, harness contract, and review binding. Missing packet-only requirements must **not** be reconstructed from memory.

## Review rules

1. Review is user-initiated and manual. Automated reviewer API dispatch is prohibited.
2. Reviewer may be human or AI, but a clean independent review context is required where independence is part of the case.
3. Evidence is not authority. A reviewer opinion cannot manufacture a missing source, witness, ledger lineage, IAM boundary, bootstrap ceremony, control-plane observation, or semantic mapping.
4. If mandatory evidence is absent, stale, contradictory, circular, candidate-self-derived where independence is required, or cannot be bound to the exact subject, return `MISSING_EVIDENCE` / `INSUFFICIENT_EVIDENCE`; never infer PASS.
5. A scientific case remains `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED` until its evidence profile is materially satisfied and bound to the exact run.
6. WDPC-469 and WDPC-495 remain blocked by I1 semantic qualification and are not opened by this packet.

## Required evidence bundle envelope

For every evidence snapshot provide, where applicable:

- `evidence_snapshot_id`
- evidence profile ID
- exact case IDs using the snapshot
- source identity and source class
- source artifact/record identifiers
- source content digest(s)
- observation / capture timestamp or bounded logical time
- governance generation
- subject / sink / capability / ledger / authority identifiers
- independence/control-domain statement and supporting evidence
- current/stale/revoked state
- contradiction statement
- collector identity
- collector control domain
- whether any evidence is candidate-self-derived
- chain/lineage predecessor and current-head identifiers when lineage is load-bearing

If a field is not available, record `NOT_PRESENT`; do not silently omit it.

## Evidence profiles and cases

### E-CONTROL-INDEPENDENCE

- **WDPC-443** — `HYBRID_EXTERNAL_REQUIRED`; expected governed endpoint `INSUFFICIENT_EVIDENCE` when the target condition is actually established: *IUDA shares prohibited effective control with candidate*.

Collect independent control-domain evidence for the candidate, the IUDA/derivation authority, relevant root-threshold-capable control sets, and any shared effective-control path. Candidate labels alone are insufficient.

### E-WITNESS

- **WDPC-449** — expected `WITNESS_INDEPENDENCE_INSUFFICIENT`.
- **WDPC-467** — positive `WITNESSED_LEDGER_INTEGRITY_QUALIFIES`; hybrid external required.
- **WDPC-477** — expected `WITNESS_INDEPENDENCE_INSUFFICIENT`.

Collect witness identity, control domain, witness state, exact witnessed ledger digest, generation, quorum policy, ledger operator control domain, root-threshold-capable operational domains, and evidence that at least the required witness independence relation is real rather than declared.

### E-WITNESS-LINEAGE

- **WDPC-460** — expected `RECONCILIATION_CONFLICT`.
- **WDPC-484** — expected `RECONCILIATION_CONFLICT`.

Collect competing witness/ledger lineage records, predecessor links, current-head evidence, exact ledger digests, generation, and independent evidence sufficient to determine whether one lineage is current or whether the state is genuinely conflicting.

### E-IUDA

- **WDPC-458** — `EXTERNAL_MANUAL_REQUIRED`; expected `INSUFFICIENT_EVIDENCE` only when the narrowed fixture is *authority present, independence unproven*.
- **WDPC-468** — positive `COMPLETENESS_RECORD_CURRENT`.

Collect derivation-authority identity, control domain, root/bootstrap lineage, source-contract authority, current completeness record, exact subject, universe digest, independent derivation digest, source evidence digest, and evidence of non-self-qualification.

### E-CAPABILITY-ATTESTATION

- **WDPC-466** — positive `CAPABILITY_REATTESTATION_QUALIFIES`.

Collect capability identity, owner control domain, independent attestor identity/control domain, measured deployment digest, measured configuration digest, current deployment/configuration observation, generation, and evidence that the attestor is independently controlled.

### E-LEDGER-LINEAGE

- **WDPC-472** — expected `INSUFFICIENT_EVIDENCE` when *exact current admission-ledger lineage cannot be established*.

Collect all competing admission-ledger heads relevant to the case, predecessor links, record digests, generation, durable-current evidence, and any reconciliation evidence. Missing run evidence is not itself the target condition.

### E-COMPLETENESS-LEDGER-LINEAGE

- **WDPC-474** — expected `INSUFFICIENT_EVIDENCE` when *exact current completeness-ledger lineage cannot be established*.

Collect competing completeness-ledger heads, predecessor links, exact record digests, subject IDs, generation, current-state evidence, and reconciliation evidence.

### E-ADMISSION-COMPLETENESS

- **WDPC-485** — positive `ADMISSION_COMPLETENESS_APPLY_QUALIFIES`.

Collect exact current admission ledger, current completeness ledger, decision bindings to both, sink/writer admission perimeter state, generation, application boundary observation, and evidence that no material discovery is pending.

### E-COMPOSITE-486

- **WDPC-486** — positive `NORMATIVE_CAPABILITY_COMPLETENESS_WITNESS_QUALIFIES`.

This is a composite positive claim. Supply independently sufficient evidence for each named component—normative, capability, completeness, and witness—and exact binding showing they apply to the same candidate/generation/decision. Partial evidence cannot qualify the conjunction.

### E-CONTROL-PLANE

- **WDPC-489** — hybrid external; expected `EFFECTIVE_CONTROL_SOURCE_COMPLETENESS_INVALID`.
- **WDPC-494** — external/manual positive `CONTROL_PLANE_SOURCE_COMPLETENESS_QUALIFIES`.

Collect independently derived control-plane source inventory, source classes, control domains, generation, source evidence digests, relationship queries/answers, negative relationship evidence where claimed, and observed deployment/control-plane evidence. Candidate-only registry contents are insufficient to prove completeness.

### E-SEMANTIC

- **WDPC-491** — `MANUAL_SEMANTIC_REQUIRED`; expected `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` when the semantic defect is established.
- **WDPC-469** — blocked by I1 semantic qualification.
- **WDPC-495** — blocked by I1 semantic qualification.

For WDPC-491, review exact authoritative clauses/descriptors and semantic mappings. The evidence must establish what the clause means, not merely that a descriptor exists or that hashes match. Missing V8 packet-only semantic rubric details remain `MISSING_EVIDENCE` unless the reviewed packet is supplied exactly.

### E-IAM-PERIMETER

- **WDPC-497** — external/manual; expected `INSUFFICIENT_EVIDENCE` when an *unadmitted direct sink writer prevents closed-world qualification*; narrowed branch `DIRECT_UNADMITTED_WRITER_NO_STRICTER_FENCE`.
- **WDPC-498** — hybrid external; expected `ROOT_KERNEL_DECISION_STALE`; narrowed branch `IAM_PERIMETER_ONLY_DRIFT_AFTER_DECISION`.
- **WDPC-504** — external/manual; expected `INSUFFICIENT_EVIDENCE` when a *material sink lacks unavoidable deny-by-default admission boundary*.
- **WDPC-505** — external/manual positive `ADMISSION_PERIMETER_QUALIFIES`.

Collect IAM/policy configuration identity and digest, all effective writer principals/paths for the material sink, enforcement location, deny-by-default state, bypass paths, independent observation of enforcement, before/after perimeter state for drift cases, and exact decision/apply-time bindings.

### E-BOOTSTRAP-CONTROL

- **WDPC-500** — hybrid external; expected `INSUFFICIENT_EVIDENCE` when an *operational root is relabeled independent without control-domain separation*.

Collect root/bootstrap authority identities, actual control domains, threshold/membership, source-contract authority, operational-root relationships, and evidence that purportedly independent authorities are—or are not—under distinct effective control.

### E-STATIC-GOVERNANCE

- **WDPC-503** — `STATIC_OR_MANUAL_REQUIRED`; expected `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`; narrowed branch `IN_PLACE_BOOTSTRAP_MUTATION_UNCHANGED_GENERATION`.

Collect the exact governing rule/configuration that determines whether bootstrap/root-kernel state may mutate in place, the before/after static artifacts or governed records, generation identifiers, exact mutation diff, and the enforcement/rejection evidence. Source inspection alone may describe the mechanism but cannot be promoted to an operational PASS unless the reviewed evidence contract permits it.

### E-BOOTSTRAP

- **WDPC-506** — external/manual positive `BOOTSTRAP_RESIDUAL_TRUST_BOUNDARY_QUALIFIES`.

Collect bootstrap ceremony evidence, authority membership/threshold, source contracts, root-of-trust provenance, control domains, residual-trust declaration, generation genesis record, and evidence that descendant machinery did not self-qualify the bootstrap boundary.

## Manual reviewer output schema

For each reviewed case return:

- `case_id`
- `evidence_profile`
- `evidence_snapshot_id`
- `evidence_state = PRESENT | MISSING | CONTRADICTED | STALE | CIRCULAR | INSUFFICIENT`
- `independence_state = PROVEN | NOT_PROVEN | NOT_APPLICABLE`
- `exact_subject_binding_state = PROVEN | NOT_PROVEN`
- source IDs and digests actually relied upon
- contradictions found
- `review_finding`
- `scientific_case_execution_authorized = YES | NO`
- reason

The reviewer must not output a WDPC scientific `PASS` merely from reviewing this collection packet. The scientific harness remains authoritative for case adjudication after evidence admission.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
