# R8 v15-r1 — Implementation Slice 9: Local EvidenceRecord Validation

Status: PREREGISTERED BEFORE HARNESS OR MECHANISM IMPLEMENTATION

Base closure: 5477df994c2cc9db0033742e189b906eb20247c1
Closed Slice 7 candidate: 751162ee42c603cb6c84ee12021d16bab6fa626b
Frozen schema: f93ca26975ecb64f0da13779889c75b36140cdfc

## Goal
Validate only frozen local EvidenceRecord JSON shape, list cardinality/type, opaque GCP-valid
strings and Sequence closure.

No evidence promotion, evidence-class upgrade, temporal revocation judgment, execution proof,
output derivation proof, or authority decision is made.

## Exact required fields
evidence_id, evidence_class, producer_identity_digest, runtime_identity_digest, input_digest,
input_object_ids, input_object_digests, execution_proof_digest, output_derivation_digest,
event_id, output_digest, effective_sequence, evidence_digest.

input_object_ids and input_object_digests use exact JSON-array semantics represented by Python
list only, minItems=1. The frozen schema does not require equal lengths, uniqueness, sorting,
or one-to-one positional correspondence; Slice 9 does not invent those rules.

All CanonicalId/Digest fields are opaque non-empty GCP-valid strings.
effective_sequence is frozen Sequence: non-boolean integer 0..INT64_MAX.

## Frozen x-validator invariants that remain NONCLAIMS
- rewrapping/copying cannot upgrade evidence class;
- producer revocation evaluated temporally;
- mandatory missing/contradictory evidence blocks promotion.

The local result must state all three as unproven and promotion_authorized=false.

## Frozen acceptance I9-01..I9-16
I9-01 exact required-field parity.
I9-02 valid one-input EvidenceRecord passes.
I9-03 valid multi-input EvidenceRecord passes.
I9-04 missing/extra top-level fields reject.
I9-05 input_object_ids must be list and non-empty.
I9-06 input_object_digests must be list and non-empty.
I9-07 input arrays are not forced to equal length because schema does not freeze that invariant.
I9-08 opaque non-SHA strings pass.
I9-09 empty/non-NFC/noncharacter strings reject.
I9-10 effective_sequence min/max pass.
I9-11 negative/max+1/bool/string/float sequence reject.
I9-12 duplicate input IDs/digests remain locally structurally valid because uniqueness is not frozen.
I9-13 evidence_digest remains opaque/unverified.
I9-14 metadata leaves class-upgrade, temporal revocation, mandatory-evidence and promotion claims false.
I9-15 failure does not poison later valid validation.
I9-16 frozen schema/closed Slice 1..7 implementation bytes remain unchanged; inherited full stack and direct workflow coverage pass.

## Three-loop batch rule
This candidate may be frozen after construction but SHALL NOT be adjudicated closed before the
combined fresh independent review after Slice 8, Slice 9 and Slice 10.
