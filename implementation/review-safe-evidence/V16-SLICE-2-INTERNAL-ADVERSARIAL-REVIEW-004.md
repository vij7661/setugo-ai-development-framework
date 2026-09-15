# V16 Slice 2 Internal Adversarial Review 004

Status: **CHANGES_REQUIRED / INTERNAL NON-INDEPENDENT REVIEW**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Reviewed construction candidate

- Exact V4 candidate commit: `e46c60423648218e9de1716f0b3cf111c399b138`
- Exact V4 candidate tree: `fb7a0ce73202e7d3feb4fc976c745458dc6221ba`
- V4 run: `34991977657`
- Mandatory construction tests: `61/61 PASS`
- Source/manifest/execution set equality: `PASS`

The green construction run is preserved as evidence only. This review intentionally searches for false-green paths not exercised by that run.

## Critical findings

**None identified in this pass.**

## High findings

### IAR4-H-01 — Graph validation and binding-signer qualification can observe different caller-owned graph states

Affected code: `review_safe_evidence_v16_independence_v2.py::validate_graph_validator_binding_certificate`, `_qualify_binding_signers`, and downstream bound authority/independence calls.

The wrapper first calls `core.validate_control_domain_graph_chain(graph_chain, ...)`, which validates an owned snapshot internally. It later calls `_qualify_binding_signers(..., graph_chain, ...)`, which re-reads the original caller-owned list/dicts. The binding and downstream resolver paths also invoke graph validation more than once from the original caller object.

Concrete false-green path: a concurrent mutator can present graph A while the core validates the exact bound head/digest, then mutate the same plain list/dict before `_qualify_binding_signers` re-reads it. Signer candidate-control/shared-ancestor qualification can therefore be computed from graph B even though the certificate and pinned graph head bind graph A. The later result can report `construction_binding_valid=true` using a qualification relation that was not derived from the exact graph snapshot that authenticated the certificate.

The current tests use immutable-by-convention fixtures and do not exercise mutation between validation phases.

Narrow repair: take one fail-closed owned plain snapshot of the complete graph chain at the public wrapper boundary, validate that exact owned snapshot, and pass only that same snapshot to every signer-qualification, candidate-control, independence, and registry-resolution operation in the call. Add a deterministic adversarial mutable-input test proving post-snapshot mutation cannot change the result.

### IAR4-H-02 — Baseline-manifest succession binds predecessor ID but not predecessor content

Affected artifacts: `review-safe-evidence-v16-slice2-test-manifest-v2.json`, historical `review-safe-evidence-v16-slice2-test-manifest.json`, current-manifest index, and V4 manifest verification.

The semantic-revision-2 baseline says it supersedes manifest ID `REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001`, but neither the v2 manifest nor the current index binds the historical predecessor's exact Git blob or canonical content digest. V4 only verifies that the historical file still reports the expected manifest ID.

Concrete false-green path: rewrite the historical v1 manifest's test mappings/requirements while retaining the same manifest ID. The current v2 lineage and V4 verification still succeed, so preserved semantic history can be rewritten without invalidating the claimed successor relationship.

Current historical predecessor blob at this review is `27983a245408589ec39681aa69da3a003294ddd8`.

Narrow repair: add exact predecessor Git-blob binding to the v2 manifest and current index, require V4 to recompute and match it, and add an adversarial lineage test showing same-ID/different-content predecessor substitution fails.

### IAR4-H-03 — Load-bearing JSON manifests accept duplicate keys and do not enforce exact schemas

Affected code: V4 manifest/index verification uses ordinary `json.loads`; manifest and index objects are checked for selected values but not duplicate keys or exact allowed field sets.

Python's standard `json.loads` accepts duplicate object keys and keeps one value. Other consumers may use first-value or duplicate-reject semantics. Unknown extra fields are also currently tolerated.

Concrete false-green path: a modified manifest can contain duplicate load-bearing fields such as `manifest_id`, `semantic_revision`, or qualification/authority fields. V4 may interpret the last occurrence and pass while another verifier or reviewer interprets a different occurrence. Likewise, ungoverned extra load-bearing-looking fields can survive the current verifier. This violates the frozen machine-enforceable canonical-schema requirement and creates parser-differential evidence ambiguity.

Narrow repair: introduce a strict JSON loader that rejects duplicate keys, require exact top-level and per-test field sets for each current manifest/index schema, and run those checks in the canonical workflow before test-set equality. Add mandatory duplicate-key and unknown-field rejection tests.

## Medium / Low observations

The generic historical filename remains easy for a naive consumer to discover before the explicit current-manifest index. The index now disambiguates current versus historical state, but after H-02/H-03 repair the current index should be treated as the only canonical discovery point and its exact schema/content bindings should be enforced.

## Disposition

`V16_SLICE2_INTERNAL_REVIEW = CHANGES_REQUIRED`

`V16_SLICE2_NEW_CRITICAL = 0`

`V16_SLICE2_NEW_HIGH = 3`

`V16_SLICE2_FREEZE_ALLOWED = false`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
