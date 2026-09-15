# V16 Slice 2 Internal Adversarial Review 003

Review class: **INTERNAL_ADVERSARIAL_RECORD**

Reviewed candidate: `685a56eab5c058f1120c22aca59d78f428874add`

Candidate tree: `67f1df46ca24da54290c4d7bb06621c54a106f49`

Construction run: `34990102308` — 53/53 mandatory tests PASS.

The 53-test PASS remains preserved as construction evidence. This review is internal, is not independent review, and creates no authority transition.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## IAR2-H-03 — outer validator-binding certificate quorum is not graph-qualified

Severity: **High**

Affected functions:

- `review_safe_evidence_v16_independence_v2._verify_binding_signatures`
- `review_safe_evidence_v16_independence_v2.validate_graph_validator_binding_certificate`

Concrete false-green path:

The repaired core now requires graph-authenticating bootstrap roots to be represented, non-candidate, and pairwise independent under the authenticated control graph. The outer Slice 2 validator-binding certificate does not apply that same rule. `_verify_binding_signatures` verifies bootstrap signatures and counts distinct root `control_domain_id` strings only.

A graph can therefore be structurally authenticated by an eligible quorum such as root-2 + root-3 while the signed graph classifies root-1 as candidate-controlled. The outer validator-binding certificate can then be signed by root-1 + root-2 and still be reported threshold-authenticated. Equivalent false-green routes exist when binding-signing roots share a load-bearing graph ancestor or when a binding-signing root domain is absent from the graph.

Global promotion remains blocked, so this does not recreate the earlier Critical promotion bypass. It does, however, invalidate the narrower structural claim that the exact validator/profile binding itself is authenticated by an independently controlled quorum.

Required narrow repair:

- after cryptographic verification of binding-certificate signatures, graph-qualify the signing-root domains against the exact graph bound by the certificate;
- require every counted root domain to be represented, non-candidate, and part of a threshold-sized pairwise-independent quorum;
- reject candidate-controlled/shared-ancestor/absent root domains before `construction_binding_valid=true`;
- add mandatory tests for each route.

## IAR2-H-04 — stable baseline requirement identities were reused after their test oracle changed

Severity: **High**

Affected evidence surfaces:

- `governance-runtime/test_review_safe_evidence_v16_independence.py`
- `governance-runtime/review-safe-evidence-v16-slice2-test-manifest.json`
- V16 Slice 2 workflow manifest-equality logic

Concrete false-green/evidence-laundering path:

The baseline test source was deliberately changed during the IAR2 repair. Several original tests that previously accepted generic `promotion_blocked=false` / `authority_admissible=true` semantics now assert the opposite fail-closed semantics. The manifest ID `REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001`, requirement IDs `V16-S2-001...030`, and Python test IDs were nevertheless reused unchanged.

The current workflow pins the exact source blob, so the current 53-test run is reproducible, and historical commits preserve the older oracle. However, a cross-run consumer comparing stable requirement IDs can incorrectly treat the old and new tests as the same semantic requirement. This weakens the project's stable-manifest evidence contract and can launder a changed oracle through an unchanged requirement identity.

Required narrow repair:

- preserve manifest `...MANDATORY-TESTS-001` as historical evidence;
- create a new current baseline manifest with a new manifest ID and semantic revision, for example `...MANDATORY-TESTS-002`;
- bind the exact current baseline test-source Git blob SHA in the current manifest;
- include an explicit `supersedes_manifest_id`/predecessor relation and semantic-change reason;
- issue new requirement IDs for the revised baseline semantics rather than silently reusing `V16-S2-001...030`;
- make the canonical workflow use only the new current baseline plus additive IAR manifests, while prior manifests remain preserved in history/evidence.

## Residual boundaries retained

The following are still explicit boundaries rather than new false-green findings because the repaired Slice 2 mechanism globally blocks promotion/authority around them:

- real-world control-graph completeness is unproven;
- exact validator source measurement is local/self-measured, not independently attested runtime code identity;
- pinned trust/currentness provisioning remains out-of-band and unproven;
- common registry/graph generation equality is a local construction contract, not the final authenticated governance-generation mechanism.

## Disposition

`V16_SLICE2_CONSTRUCTION_HISTORY = PRESERVED`

`V16_SLICE2_INTERNAL_REVIEW = CHANGES_REQUIRED`

`V16_SLICE2_NEW_CRITICAL_FINDINGS = 0`

`V16_SLICE2_NEW_HIGH_FINDINGS = 2`

`V16_SLICE2_FREEZE_ALLOWED = false`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
