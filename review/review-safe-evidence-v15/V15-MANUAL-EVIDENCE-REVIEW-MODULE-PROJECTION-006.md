# V15 Manual Evidence Review — Projection Module 006

`MODULE_REVIEWED = review_safe_evidence_v15_projection.py`

`MODULE_COVERAGE = COMPLETE`

`V15_EXISTING_CRITICAL = CONFIRMED`

## New Critical findings

1. **Materiality is self-classified — a truly load-bearing field can be declared non-load-bearing and then legally redacted.** Functions: `validate_obligation_record`, `validate_projection_record`. `materiality_authority_id` / `materiality_control_domain_id` are unresolved plain strings, `materiality_recomputed=True` is a bare assertion, and the only partition check is non-overlap of load/non-load lists. False-green: classify a substantively load-bearing field as non-load-bearing, omit it under `STRUCTURED_REDACTION`, and pass. Repair: resolve materiality authority through the current role registry independent of candidate/compiler and require an independently executed recomputation record.

2. **Projection is never bound to the actual raw-evidence registry.** Functions: `validate_raw_projection_source`, `validate_projection_record`. `raw` is an arbitrary mapping checked only for internal digest self-consistency and membership of `evidence_id` in `required_evidence_ids`. False-green: invent a required evidence ID and arbitrary content/relations, recompute digests, and validate against invented raw data. Repair: bind projection source to the authoritative evidence-registry entry and independently verified captured bytes.

3. **`obligation_graph_digest` is never format-checked or cross-verified against the real obligation graph.** Function: `validate_projection_record`. It is only non-empty. False-green: use any string. Repair: require the actual authoritative obligation-graph digest and exact match.

4. **Disclosure catalog trusts opaque caller-supplied projection-result mappings.** Function: `validate_disclosure_catalog`. A projection is considered valid if `projections[pid]["valid"]` is true; the function does not itself verify the projection chain. False-green: pass `{"pid1":{"valid":true}}` without a real projection. Repair: consume actual projection records and required authoritative inputs, and validate internally.

5. **Disclosure completeness certificate is not bound to the real catalog.** Function: `validate_disclosure_completeness_certificate`. `catalog_digest` is compared only with `bound_catalog_digest` inside the same record; `catalog_result` is an opaque mapping. False-green: set both digest fields to the same fabricated SHA and use `catalog_result={"valid":true,"insufficient_obligations":[]}` to reach `review_ready=True`. Repair: pass the real catalog, recompute its validation result internally, and compare against the real catalog digest.

## New High findings

1. `expected_obligation_ids` in `validate_disclosure_completeness_certificate` is caller supplied and unbound to the authoritative obligation universe; an omitted obligation disappears from completeness.

2. Disclosure-certificate verifier independence is asserted via `verifier_independence_result="INDEPENDENT"` with no proof binding.

## New Medium / Low findings

1. **Medium:** `semantic_contract` fields are required but not behaviorally enforced by `validate_projection_record` as an explicit contract.
2. **Low:** projection compiler/verifier identity and control-domain fields are unresolved through the role registry.

## External review conclusion

The module does not mitigate the systemic root-of-trust defect. It adds a materiality false-green and two opaque-result-laundering boundaries: projection results into disclosure, and disclosure results into completeness certification.

`NEXT_MODULE_RECOMMENDED = review_safe_evidence_v15_universe.py`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
