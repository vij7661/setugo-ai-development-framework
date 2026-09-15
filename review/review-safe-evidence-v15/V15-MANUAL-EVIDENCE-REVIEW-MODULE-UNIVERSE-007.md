# V15 Manual Evidence Review — Universe Module 007

`MODULE_REVIEWED = review_safe_evidence_v15_universe.py`

`MODULE_COVERAGE = COMPLETE`

`V15_EXISTING_CRITICAL = CONFIRMED`

## New Critical findings

1. **Shared-source circularity detection can be defeated by re-labeling one real source across streams.** Function: `validate_universe_derivation_bundle`. The detector compares only caller-chosen `source_roots` labels. False-green: the same underlying document is labeled differently in NORMATIVE, AUTHORITY_SURFACE, and HISTORICAL streams, so no string intersection occurs. Repair: use canonical externally verifiable source identities/content digests.

2. **Absence of unknown/unclassified material surfaces is asserted, not demonstrated.** Function: `validate_universe_derivation_bundle`. `unclassified_material_surfaces=[]` is a caller-supplied passing assertion with no independent discovery mechanism. Repair: derive/verify unknown-surface state from a separately controlled discovery/observation mechanism.

3. **Universe challenge execution is unauthenticated; `NO_NEW_OBLIGATION_FOUND` requires no real algorithm execution.** Function: `validate_universe_challenge`. Algorithm identity, source/coverage digests and verifier independence are asserted rather than tied to an executed challenge and authoritative proof. Repair: authenticate challenge authority/verifier, prove independence, and bind source/coverage digests to real independently supplied execution evidence.

4. **Universe challenge and completeness certificate accept unbound authoritative obligations and opaque result mappings.** Functions: `validate_universe_challenge`, `validate_universe_completeness_certificate`. `authoritative_obligations` need not equal the actual derivation output; `derivation_result` and `challenge_result` can be fabricated mappings; `challenge_digest` is compared only to `bound_challenge_digest` inside the same certificate. False-green: fabricated valid result dicts plus two identical fabricated challenge digests can produce `UNIVERSE_COMPLETENESS_CERTIFICATE_VALID`. Repair: internally validate/bind the actual derivation bundle and challenge record and compare against their real digests.

5. **`unresolved_unknown_count=0` is an uncross-referenced assertion.** Function: `validate_universe_completeness_certificate`. The function does not receive the actual unknown-surface state. Repair: derive the count from the bound derivation/discovery state.

## New High findings

1. Derivation `authority_id` / `control_domain_id` are unresolved through the current `EVIDENCE_UNIVERSE_DERIVATION_AUTHORITY` registry.
2. `source_graph_digest`, `source_roots`, and per-stream `obligations` are not recomputed from the real normative/runtime/history sources.

## New Medium / Low findings

1. **Medium:** challenge `discovered_obligations` are unbound strings; `OBLIGATION_ADDED` is as fabricatable as `NO_NEW_OBLIGATION_FOUND`.
2. **Low / positive:** challenge logic correctly prevents obligation removal via `authority_may_remove_obligations` and `removed_obligations` checks.

## External review conclusion

The module does not mitigate the systemic root-of-trust defect. It leaves the negative-space completeness claim self-reportable, permits shared-source relabeling, allows a challenge to report no new obligation without real execution, and launders caller-supplied derivation/challenge result mappings into a completeness certificate.

`NEXT_MODULE_RECOMMENDED = review-safe-evidence-v15-schema-registry.json (and .github/workflows/)`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
