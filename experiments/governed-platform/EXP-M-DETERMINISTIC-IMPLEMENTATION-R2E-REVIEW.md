# EXP-M Deterministic Implementation R2E — Independent Review Handoff

## Exact S -> E -> P identity

- S: 06fc3a9784105ec35c6eb231c261de361e28f5db
- S tree: 8a812eeb4305e7ed710b8456c79fc1f4308a392c
- E: bcc606619367ed0d2efdfb0846461147b64e9eb4
- E tree: 009f5ef28ce62f431c29917630c4c83c0b2ff5cf
- P: 26ab84b1a917710e237c52b20ea22045d83424b0
- P tree: 0d8b752579d859fc10842e14b19daa72f4bf3236

The current handoff commit is a docs-only post-P identity attestation. P is the immutable packet-content commit; this avoids the impossible requirement for a Git commit to contain its own SHA.

## Q identity publication

Q cannot contain its own final commit SHA/tree without Git self-reference. After Q exists, the governed portable-bundle step independently verifies S->E->P->Q and creates FINAL-REVIEW-HANDOFF.md carrying the exact Q commit/tree plus the verification-capture hash. Reviewers should treat that post-Q file inside the portable bundle as the exact Q identity carrier.

## E -> P changed paths

~~~text
experiments/governed-platform/EXP-M-R2E-PACKET-CONTENT.md
~~~

## Authority boundary

- EXP-M remains NOT_QUALIFIED.
- Authority effect remains NONE.
- No live provider/API execution occurred or is authorized.

## Packet content frozen at P

# EXP-M Deterministic Implementation R2E — Packet Content

## Bounded authority statement

- EXP-M: NOT_QUALIFIED
- Authority effect: NONE
- Live provider/API execution: false
- This packet covers deterministic/offline falsification only.

## Identity

- S source commit: 06fc3a9784105ec35c6eb231c261de361e28f5db
- S source tree: 8a812eeb4305e7ed710b8456c79fc1f4308a392c
- E evidence commit: bcc606619367ed0d2efdfb0846461147b64e9eb4
- E evidence tree: 009f5ef28ce62f431c29917630c4c83c0b2ff5cf
- Evidence manifest SHA-256 at E: 688c0ffc3d58331b48d17fb02cd497d3cfa94616da0e57920c414e3b835113aa
- Evidence manifest Git blob at E: 3bb5afd10b78938d440a219421dd2b9ebe90f76a
- P packet-content commit: established by the first commit containing this file; the exact P SHA is reported in the post-P handoff document to avoid Git commit-hash self-reference.

## S -> E changed paths

~~~text
experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json
experiments/governed-platform/EXP-M-MUTATION-RESULTS.json
experiments/governed-platform/EXP-M-R2D-SELF-ADJUDICATION.json
experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json
experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json
experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json
experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-SELF-ADJUDICATION-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-SOURCE-FREEZE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt
experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json
experiments/governed-platform/EXP-M-SOURCE-FREEZE.json
experiments/governed-platform/EXP-M-TEST-RESULTS.json
~~~

## Fresh evidence summary

- Core tests: 58/58 with all_passed=True
- Mutation closure: validator logic all killed=True, data/state all rejected=True, survivors=0
- Self-falsification total: 62, all rejected=True
- Reviewer compound attacks CA-1..CA-10: 10 executed, survivors=0

## Compound attack results

~~~json
{
  "all_rejected": true,
  "authority_effect": "NONE",
  "case_count": 10,
  "cases": [
    {
      "blocking_guard": "expectation_authority_invalid",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-1",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca1_self_consistent_context_plus_forged_complete_receipt"
    },
    {
      "blocking_guard": "evidence_token_mismatch",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-2",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca2_correctly_keyed_token_for_different_bundle"
    },
    {
      "blocking_guard": "authority_reviewed_commit_mismatch",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-3",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca3_fabricated_manifest_plus_matching_caller_commit"
    },
    {
      "blocking_guard": "retrieval_and_delivery_binding_rejected",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-4",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca4_fabricated_retrieval_bytes_plus_forged_receipt"
    },
    {
      "blocking_guard": "archive_and_schedule_attack_rejected",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-5",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca5_zip_named_bin_plus_fake_schedule_diversity"
    },
    {
      "blocking_guard": "qualification_authority_plan_missing",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-6",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca6_authority_plan_absent_but_caller_plan_self_consistent"
    },
    {
      "blocking_guard": "indexed_prior_artifact_missing",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-7",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca7_prior_artifact_deleted_but_index_unchanged"
    },
    {
      "blocking_guard": "reviewer_suite_hash_drift",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "id": "CA-8",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca8_reviewer_suite_modified_after_source_freeze"
    },
    {
      "blocking_guard": "disposition_promotable",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "guard_semantics": "FALSE means failed predicates derive CHANGES_REQUIRED; a caller-supplied PASS cannot override that derived disposition.",
      "id": "CA-9",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca9_caller_pass_with_failed_predicate"
    },
    {
      "blocking_guard": "r5_protocol_unavailable",
      "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
      "failure": null,
      "fault_injection": "AuthorityHandle.with_missing_r5_protocol_for_test() sets protocol_available=False for this negative test only; the frozen R5 protocol remains present in the authority root.",
      "id": "CA-10",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca10_missing_protocol_with_self_consistent_record"
    }
  ],
  "execution": {
    "command": "python governance-runtime/run_reviewer_compound_attacks.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
    "source_tree": "8a812eeb4305e7ed710b8456c79fc1f4308a392c",
    "utc": "2026-09-22T09:10:55.170311+00:00"
  },
  "exp_m_state": "NOT_QUALIFIED",
  "live_provider_api_execution": false,
  "schema": "EXP-M-R2E-COMPOUND/v2",
  "survivor_count": 0,
  "survivors": []
}
~~~

## Full mutation results

~~~json
{
  "all_closed": true,
  "all_rejected": true,
  "closed_cases": 50,
  "data_state_all_rejected": true,
  "data_state_rejected_count": 27,
  "data_state_total": 27,
  "declared_fixture_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "declared_mutation_targets": [
    "review_request_current",
    "authority_snapshot_current",
    "evidence_contract_closed",
    "interaction_contract_closed",
    "materialization_complete",
    "representation_governed",
    "egress_authorized",
    "capability_current",
    "accessibility_policy_satisfied",
    "context_isolation_satisfied",
    "hidden_state_policy_satisfied",
    "context_state_clean",
    "admission_fence_current",
    "semantic_context_qualified",
    "wire_binding_valid",
    "delivery_complete",
    "accessibility_proven",
    "witness_record_current",
    "session_retrieval_coverage",
    "prompt_isolation_current",
    "semantic_coverage",
    "reviewer_provenance",
    "disposition_promotable"
  ],
  "executed_fixture_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "executed_mutation_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "execution": {
    "command": "python governance-runtime/run_exp_m_mutations.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
    "source_tree": "8a812eeb4305e7ed710b8456c79fc1f4308a392c",
    "utc": "2026-09-22T09:12:15.532381+00:00"
  },
  "experiment": "EXP-M",
  "killed_mutation_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "mutations": [
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "review_request_current",
      "family": "validator_logic",
      "fixture_constructor": "review_request_not_current",
      "fixture_hash": "4aad3ebcbcec185fb18c8884a856f6b33d86c7fe65aec5dfe0e35c70bab9b38c",
      "id": "TM-O-review_request_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:review_request_current",
      "negative_fixture_target_id": "review_request_current",
      "normal_reasons": [
        "review_request_current",
        "disposition_promotable"
      ],
      "target": "review_request_current",
      "target_predicate_id": "review_request_current"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "authority_snapshot_current",
      "family": "validator_logic",
      "fixture_constructor": "candidate_writable_snapshot",
      "fixture_hash": "403376782ba81bf4967fe6135696c8037be86d3a9cbc5126c4ec500513084608",
      "id": "TM-O-authority_snapshot_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:authority_snapshot_current",
      "negative_fixture_target_id": "authority_snapshot_current",
      "normal_reasons": [
        "authority_snapshot_current",
        "disposition_promotable"
      ],
      "target": "authority_snapshot_current",
      "target_predicate_id": "authority_snapshot_current"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "evidence_contract_closed",
      "family": "validator_logic",
      "fixture_constructor": "open_evidence_contract",
      "fixture_hash": "90bb4f3e646175d7e16f71a9db20d25d8ba0f2b4b8b75d8a1c7529fc285620de",
      "id": "TM-O-evidence_contract_closed",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:evidence_contract_closed",
      "negative_fixture_target_id": "evidence_contract_closed",
      "normal_reasons": [
        "evidence_contract_closed",
        "disposition_promotable"
      ],
      "target": "evidence_contract_closed",
      "target_predicate_id": "evidence_contract_closed"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "interaction_contract_closed",
      "family": "validator_logic",
      "fixture_constructor": "open_interaction_contract",
      "fixture_hash": "917a7017a2a891d1d77fe8aa431101a920bb533bb46bba8d5537da82e4caa28d",
      "id": "TM-O-interaction_contract_closed",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:interaction_contract_closed",
      "negative_fixture_target_id": "interaction_contract_closed",
      "normal_reasons": [
        "interaction_contract_closed",
        "disposition_promotable"
      ],
      "target": "interaction_contract_closed",
      "target_predicate_id": "interaction_contract_closed"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "materialization_complete",
      "family": "validator_logic",
      "fixture_constructor": "failed_materialization",
      "fixture_hash": "720a77311084dbc4d9ac3ce5cfd53cc68b7c2ab9a077532acce7e5a77378be91",
      "id": "TM-O-materialization_complete",
      "killed": true,
      "mutated_reasons": [
        "wire_binding_valid",
        "delivery_complete",
        "disposition_promotable"
      ],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:materialization_complete",
      "negative_fixture_target_id": "materialization_complete",
      "normal_reasons": [
        "materialization_complete",
        "wire_binding_valid",
        "delivery_complete",
        "disposition_promotable"
      ],
      "target": "materialization_complete",
      "target_predicate_id": "materialization_complete"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "representation_governed",
      "family": "validator_logic",
      "fixture_constructor": "unqualified_representation",
      "fixture_hash": "db52fbb7ac07dc888fdecdd9947c4f9c76628bda46851855f967ae8b5fe51c25",
      "id": "TM-O-representation_governed",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:representation_governed",
      "negative_fixture_target_id": "representation_governed",
      "normal_reasons": [
        "representation_governed",
        "disposition_promotable"
      ],
      "target": "representation_governed",
      "target_predicate_id": "representation_governed"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "egress_authorized",
      "family": "validator_logic",
      "fixture_constructor": "revoked_egress",
      "fixture_hash": "80159104c5e7b2e29e709b21655bf86229adea629f1ff1855559d8c8ebf82f30",
      "id": "TM-O-egress_authorized",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:egress_authorized",
      "negative_fixture_target_id": "egress_authorized",
      "normal_reasons": [
        "egress_authorized",
        "disposition_promotable"
      ],
      "target": "egress_authorized",
      "target_predicate_id": "egress_authorized"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "capability_current",
      "family": "validator_logic",
      "fixture_constructor": "invalid_capability_summary",
      "fixture_hash": "2404245b2fdf16e8b6567cc1049287ca8093c02f0d1085012f5a0c59124d1ce3",
      "id": "TM-O-capability_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:capability_current",
      "negative_fixture_target_id": "capability_current",
      "normal_reasons": [
        "capability_current",
        "disposition_promotable"
      ],
      "target": "capability_current",
      "target_predicate_id": "capability_current"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "accessibility_policy_satisfied",
      "family": "validator_logic",
      "fixture_constructor": "invalid_accessibility_policy",
      "fixture_hash": "181cd41989b25b03064c2a7bbc285fcc71585f5ae727c9bfdd695363f7848f6d",
      "id": "TM-O-accessibility_policy_satisfied",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:accessibility_policy_satisfied",
      "negative_fixture_target_id": "accessibility_policy_satisfied",
      "normal_reasons": [
        "accessibility_policy_satisfied",
        "disposition_promotable"
      ],
      "target": "accessibility_policy_satisfied",
      "target_predicate_id": "accessibility_policy_satisfied"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "context_isolation_satisfied",
      "family": "validator_logic",
      "fixture_constructor": "dirty_isolation",
      "fixture_hash": "9774b5d408f8cda0bda9d5413b10964f0a86080c8ab6b080dd49d74a8c13166e",
      "id": "TM-O-context_isolation_satisfied",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:context_isolation_satisfied",
      "negative_fixture_target_id": "context_isolation_satisfied",
      "normal_reasons": [
        "context_isolation_satisfied",
        "disposition_promotable"
      ],
      "target": "context_isolation_satisfied",
      "target_predicate_id": "context_isolation_satisfied"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "hidden_state_policy_satisfied",
      "family": "validator_logic",
      "fixture_constructor": "hidden_state",
      "fixture_hash": "20080274101d8eafed1a3af115899eddef583377d57e3844520b74a07ceacccc",
      "id": "TM-O-hidden_state_policy_satisfied",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:hidden_state_policy_satisfied",
      "negative_fixture_target_id": "hidden_state_policy_satisfied",
      "normal_reasons": [
        "hidden_state_policy_satisfied",
        "disposition_promotable"
      ],
      "target": "hidden_state_policy_satisfied",
      "target_predicate_id": "hidden_state_policy_satisfied"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "context_state_clean",
      "family": "validator_logic",
      "fixture_constructor": "dirty_context",
      "fixture_hash": "32689ee8cdc948d3aea2f1c0422043a0737a202540811a637facf93bb6dc2cc3",
      "id": "TM-O-context_state_clean",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:context_state_clean",
      "negative_fixture_target_id": "context_state_clean",
      "normal_reasons": [
        "context_state_clean",
        "disposition_promotable"
      ],
      "target": "context_state_clean",
      "target_predicate_id": "context_state_clean"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "admission_fence_current",
      "family": "validator_logic",
      "fixture_constructor": "stale_fence",
      "fixture_hash": "0e067e781a72ef18e57bf8b2c285ac5306c545f85d86b32d84e969e7df6abe6d",
      "id": "TM-O-admission_fence_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:admission_fence_current",
      "negative_fixture_target_id": "admission_fence_current",
      "normal_reasons": [
        "admission_fence_current",
        "disposition_promotable"
      ],
      "target": "admission_fence_current",
      "target_predicate_id": "admission_fence_current"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "semantic_context_qualified",
      "family": "validator_logic",
      "fixture_constructor": "wrong_semantic_context",
      "fixture_hash": "01c5525c6b8a6f53a47de18b4551e12fce3f115059ac7654df6a5ddb9737dbee",
      "id": "TM-O-semantic_context_qualified",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:semantic_context_qualified",
      "negative_fixture_target_id": "semantic_context_qualified",
      "normal_reasons": [
        "semantic_context_qualified",
        "disposition_promotable"
      ],
      "target": "semantic_context_qualified",
      "target_predicate_id": "semantic_context_qualified"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "wire_binding_valid",
      "family": "validator_logic",
      "fixture_constructor": "invalid_wire",
      "fixture_hash": "646ab90339b5341db65f09ed47cd43a229762ff6bdedfc8a74da40500d90f903",
      "id": "TM-O-wire_binding_valid",
      "killed": true,
      "mutated_reasons": [
        "delivery_complete",
        "disposition_promotable"
      ],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:wire_binding_valid",
      "negative_fixture_target_id": "wire_binding_valid",
      "normal_reasons": [
        "wire_binding_valid",
        "delivery_complete",
        "disposition_promotable"
      ],
      "target": "wire_binding_valid",
      "target_predicate_id": "wire_binding_valid"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "delivery_complete",
      "family": "validator_logic",
      "fixture_constructor": "incomplete_delivery",
      "fixture_hash": "041d122f1d7f8607678385e5783fcf4f5c75ee459947a4e0a18ac05d914b0996",
      "id": "TM-O-delivery_complete",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:delivery_complete",
      "negative_fixture_target_id": "delivery_complete",
      "normal_reasons": [
        "delivery_complete",
        "disposition_promotable"
      ],
      "target": "delivery_complete",
      "target_predicate_id": "delivery_complete"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "accessibility_proven",
      "family": "validator_logic",
      "fixture_constructor": "invalid_accessibility_proof",
      "fixture_hash": "cf7f4b6524f4ca841b8ef452d7e0ae578f71c038dd898a0a8d2164b35d625534",
      "id": "TM-O-accessibility_proven",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:accessibility_proven",
      "negative_fixture_target_id": "accessibility_proven",
      "normal_reasons": [
        "accessibility_proven",
        "disposition_promotable"
      ],
      "target": "accessibility_proven",
      "target_predicate_id": "accessibility_proven"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "witness_record_current",
      "family": "validator_logic",
      "fixture_constructor": "expired_witness",
      "fixture_hash": "4d96e06158ca9b305f0e6cde91797f053e4641de05a86c2c81566a204c52be44",
      "id": "TM-O-witness_record_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:witness_record_current",
      "negative_fixture_target_id": "witness_record_current",
      "normal_reasons": [
        "witness_record_current",
        "disposition_promotable"
      ],
      "target": "witness_record_current",
      "target_predicate_id": "witness_record_current"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "session_retrieval_coverage",
      "family": "validator_logic",
      "fixture_constructor": "invalid_retrieval",
      "fixture_hash": "56fb7a38c59a73e5993effbdda50f06a8cf41e93c78a8d1b040c5498f92cebc8",
      "id": "TM-O-session_retrieval_coverage",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:session_retrieval_coverage",
      "negative_fixture_target_id": "session_retrieval_coverage",
      "normal_reasons": [
        "session_retrieval_coverage",
        "disposition_promotable"
      ],
      "target": "session_retrieval_coverage",
      "target_predicate_id": "session_retrieval_coverage"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "prompt_isolation_current",
      "family": "validator_logic",
      "fixture_constructor": "expired_prompt",
      "fixture_hash": "53600f60dd85696504c6b5acdf3aad661d29f44b26ec256455fd820ab28541a8",
      "id": "TM-O-prompt_isolation_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:prompt_isolation_current",
      "negative_fixture_target_id": "prompt_isolation_current",
      "normal_reasons": [
        "prompt_isolation_current",
        "disposition_promotable"
      ],
      "target": "prompt_isolation_current",
      "target_predicate_id": "prompt_isolation_current"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "semantic_coverage",
      "family": "validator_logic",
      "fixture_constructor": "incomplete_coverage",
      "fixture_hash": "4dc33ee6f7d7c420962fb87075268a31de4b203a04325448606832d9a511d801",
      "id": "TM-O-semantic_coverage",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:semantic_coverage",
      "negative_fixture_target_id": "semantic_coverage",
      "normal_reasons": [
        "semantic_coverage",
        "disposition_promotable"
      ],
      "target": "semantic_coverage",
      "target_predicate_id": "semantic_coverage"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "reviewer_provenance",
      "family": "validator_logic",
      "fixture_constructor": "untrusted_reviewer",
      "fixture_hash": "82f0b89aba9871ef7e27da583eb086870b2e5a73f9860656b522d37925ccb022",
      "id": "TM-O-reviewer_provenance",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:reviewer_provenance",
      "negative_fixture_target_id": "reviewer_provenance",
      "normal_reasons": [
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "target": "reviewer_provenance",
      "target_predicate_id": "reviewer_provenance"
    },
    {
      "actual": "TARGET_GUARD_FLIPPED",
      "executed": true,
      "expected": "TARGET_GUARD_FLIPS",
      "expected_rejection_predicate": "disposition_promotable",
      "family": "validator_logic",
      "fixture_constructor": "non_promotable_disposition",
      "fixture_hash": "dd547efd0112c1c04fed85cac824980500c3aaa076d537a12be34d3e9dadf175",
      "id": "TM-O-disposition_promotable",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:disposition_promotable",
      "negative_fixture_target_id": "disposition_promotable",
      "normal_reasons": [
        "disposition_promotable"
      ],
      "target": "disposition_promotable",
      "target_predicate_id": "disposition_promotable"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-missing_chunk",
      "killed": true,
      "target": "missing_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-wrong_request",
      "killed": true,
      "target": "wrong_request"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-wrong_corpus",
      "killed": true,
      "target": "wrong_corpus"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-duplicate_index",
      "killed": true,
      "target": "duplicate_index"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-corrupt_chunk",
      "killed": true,
      "target": "corrupt_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-empty_chunk",
      "killed": true,
      "target": "empty_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-expired_profile",
      "killed": true,
      "reasons": [
        "profile_expired"
      ],
      "target": "expired_profile"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong_profile_hash",
      "killed": true,
      "reasons": [
        "profile_hash_mismatch"
      ],
      "target": "wrong_profile_hash"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong_operating_point",
      "killed": true,
      "reasons": [
        "operating_point_mismatch"
      ],
      "target": "wrong_operating_point"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-missing_attempt",
      "killed": true,
      "reasons": [
        "qualification_attempt_closure"
      ],
      "target": "missing_attempt"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-unsupported_format",
      "killed": true,
      "reasons": [
        "unsupported_format"
      ],
      "target": "unsupported_format"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-context-isolation",
      "killed": true,
      "reasons": [
        "context_transition_class_mismatch",
        "context_channel_unobserved",
        "context_state_unbound",
        "context_channel_observations_missing",
        "context_structured_channel_missing:memory",
        "context_structured_channel_missing:config",
        "admission_fence_not_current",
        "admission_fence_state_mismatch",
        "admission_fence_stale"
      ],
      "target": "dirty_hidden_stale_context"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-materialization-traversal",
      "killed": true,
      "target": "materialization"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong-reviewed-source",
      "killed": true,
      "reasons": [
        "delivery_authority_missing",
        "materialization_source_mismatch"
      ],
      "target": "reviewed_commit"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-retrieval-bytes",
      "killed": true,
      "reasons": [
        "retrieval_bytes_mismatch"
      ],
      "target": "retrieval_returned_bytes"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-witness-expired",
      "killed": true,
      "reasons": [
        "witness_record_expired"
      ],
      "target": "witness_qualification"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-admission-drift",
      "killed": true,
      "reasons": [
        "generation_drift",
        "generation_drift"
      ],
      "target": "atomic_admission_generation"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-egress-revoked",
      "killed": true,
      "reasons": [
        "egress_revoked_or_drifted"
      ],
      "target": "egress"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-prompt-isolation-expired",
      "killed": true,
      "reasons": [
        "prompt_isolation_expired"
      ],
      "target": "prompt_isolation"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-hidden-retry",
      "killed": true,
      "reasons": [
        "implicit_retry_unobserved"
      ],
      "target": "retry_transparency"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-retrieval-session",
      "killed": true,
      "reasons": [
        "retrieval_identity_mismatch"
      ],
      "target": "retrieval_session"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-registry-drift",
      "killed": true,
      "reasons": [
        "predicate_registry_drift"
      ],
      "target": "predicate_registry"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wire-semantic-binding",
      "killed": true,
      "reasons": [
        "delivery_authority_missing",
        "semantic_wire_hash_mismatch",
        "semantic_envelope_hash_mismatch"
      ],
      "target": "wire_semantic_hash"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-summary-only",
      "killed": true,
      "reasons": [
        "review_request_current",
        "authority_snapshot_current",
        "evidence_contract_closed",
        "interaction_contract_closed",
        "materialization_complete",
        "representation_governed",
        "egress_authorized",
        "capability_current",
        "accessibility_policy_satisfied",
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "semantic_context_qualified",
        "wire_binding_valid",
        "delivery_complete",
        "accessibility_proven",
        "witness_record_current",
        "session_retrieval_coverage",
        "prompt_isolation_current",
        "semantic_coverage",
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "target": "evidence_bundle"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-plan-record-mismatch",
      "killed": true,
      "reasons": [
        "qualification_plan_identity_mismatch"
      ],
      "target": "qualification_plan_id"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-forged-complete-receipt",
      "killed": true,
      "reasons": [
        "size_mismatch:a",
        "hash_mismatch:a",
        "delivery_authority_missing",
        "representation_hash_mismatch",
        "receipt_byte_count_mismatch",
        "wire_hash_mismatch",
        "semantic_envelope_hash_mismatch"
      ],
      "target": "receipt_returned_bytes"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-broken-retry-lineage",
      "killed": true,
      "reasons": [
        "planned_first_attempt_closure",
        "retry_lineage_invalid",
        "retry_parent_missing"
      ],
      "target": "retry_lineage"
    }
  ],
  "rejected_mutations": null,
  "rejected_mutations_aggregate_status": "NOT_APPLICABLE_MIXED_FAMILY_SEMANTICS",
  "surviving_mutations": 0,
  "total_mutations": 50,
  "validator_logic_all_killed": true,
  "validator_logic_killed_count": 23,
  "validator_logic_total": 23,
  "verdict_predicate_ids": [
    "review_request_current",
    "authority_snapshot_current",
    "evidence_contract_closed",
    "interaction_contract_closed",
    "materialization_complete",
    "representation_governed",
    "egress_authorized",
    "capability_current",
    "accessibility_policy_satisfied",
    "context_isolation_satisfied",
    "hidden_state_policy_satisfied",
    "context_state_clean",
    "admission_fence_current",
    "semantic_context_qualified",
    "wire_binding_valid",
    "delivery_complete",
    "accessibility_proven",
    "witness_record_current",
    "session_retrieval_coverage",
    "prompt_isolation_current",
    "semantic_coverage",
    "reviewer_provenance",
    "disposition_promotable"
  ]
}
~~~

## Full self-falsification results

~~~json
{
  "all_rejected": true,
  "cases": [
    {
      "id": "manifest_byte_mutation",
      "rejected": true
    },
    {
      "id": "candidate_writable_snapshot",
      "rejected": true
    },
    {
      "id": "admissibility_summary_only_rejected",
      "rejected": true
    },
    {
      "id": "missing_chunk",
      "rejected": true
    },
    {
      "id": "retry_hidden",
      "rejected": true
    },
    {
      "id": "attempt_set_open",
      "rejected": true
    },
    {
      "id": "witness_over_budget",
      "rejected": true
    },
    {
      "id": "empty_witness",
      "rejected": true
    },
    {
      "id": "production_bypass_absent",
      "rejected": true
    },
    {
      "id": "all_true_summary_only",
      "rejected": true
    },
    {
      "id": "empty_qualification_sets",
      "rejected": true
    },
    {
      "id": "stale_fence",
      "rejected": true
    },
    {
      "id": "void_revival_after_reload",
      "rejected": true
    },
    {
      "id": "retrieval_complete_only",
      "rejected": true
    },
    {
      "id": "forged_complete_receipt",
      "rejected": true
    },
    {
      "id": "witness_current_only",
      "rejected": true
    },
    {
      "id": "duplicate_normalized_member",
      "rejected": true
    },
    {
      "id": "unqualified_transform",
      "rejected": true
    },
    {
      "id": "broken_retry_lineage",
      "rejected": true
    },
    {
      "id": "closure_catalog_omission",
      "rejected": true
    },
    {
      "id": "missing_trial_root",
      "rejected": true
    },
    {
      "id": "self_derived_context",
      "rejected": true
    },
    {
      "id": "forged_delivery_result",
      "rejected": true
    },
    {
      "id": "witness_without_expected_answer",
      "rejected": true
    },
    {
      "id": "accessibility_valid_only",
      "rejected": true
    },
    {
      "id": "persistent_race_second_writer",
      "rejected": true
    },
    {
      "id": "phase_cases_are_executed",
      "rejected": true
    },
    {
      "id": "phase_negative_perturbation_fails",
      "rejected": true
    },
    {
      "id": "phase_case_removal_fails_closure",
      "rejected": true
    },
    {
      "id": "typed_summary_boolean",
      "rejected": true
    },
    {
      "id": "wrong_fixture_target_mapping",
      "rejected": true
    },
    {
      "id": "grouped_mutation_false_coverage",
      "rejected": true
    },
    {
      "id": "transition_class_self_downgrade",
      "rejected": true
    },
    {
      "id": "fence_version_self_binding",
      "rejected": true
    },
    {
      "id": "wrong_witness_answer",
      "rejected": true
    },
    {
      "id": "forged_prompt_authority",
      "rejected": true
    },
    {
      "id": "forged_reviewer_authority",
      "rejected": true
    },
    {
      "id": "r5_under_sampling",
      "rejected": true
    },
    {
      "id": "cas_missing_state_hash",
      "rejected": true
    },
    {
      "id": "caller_copied_observed_interactions",
      "rejected": true
    },
    {
      "id": "production_fixture_marker_bypass",
      "rejected": true
    },
    {
      "id": "missing_structured_context_channel",
      "rejected": true
    },
    {
      "id": "self_minted_fence_attestation",
      "rejected": true
    },
    {
      "id": "void_persists_after_restart",
      "rejected": true
    },
    {
      "id": "authoritative_admission_requires_ledger",
      "rejected": true
    },
    {
      "id": "caller_minted_verdict_token_rejected",
      "rejected": true
    },
    {
      "id": "empty_context_arbitrary_receipt",
      "rejected": true
    },
    {
      "id": "candidate_copied_context_interactions",
      "rejected": true
    },
    {
      "id": "complete_manifest_incomplete_context",
      "rejected": true
    },
    {
      "id": "accessibility_challenge_hash_only",
      "rejected": true
    },
    {
      "id": "zip_bomb_rejected_before_extraction",
      "rejected": true
    },
    {
      "id": "phase_cases_record_invocations",
      "rejected": true
    },
    {
      "blocking_guard": "expectation_authority_invalid",
      "id": "CA-1",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "evidence_token_mismatch",
      "id": "CA-2",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "authority_reviewed_commit_mismatch",
      "id": "CA-3",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "retrieval_and_delivery_binding_rejected",
      "id": "CA-4",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "archive_and_schedule_attack_rejected",
      "id": "CA-5",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "qualification_authority_plan_missing",
      "id": "CA-6",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "indexed_prior_artifact_missing",
      "id": "CA-7",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "reviewer_suite_hash_drift",
      "id": "CA-8",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "disposition_promotable",
      "id": "CA-9",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    },
    {
      "blocking_guard": "r5_protocol_unavailable",
      "id": "CA-10",
      "rejected": true,
      "source": "reviewer_exp_m_r2e_compound_suite.py"
    }
  ],
  "execution": {
    "command": "python governance-runtime/self_falsify_exp_m.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
    "source_tree": "8a812eeb4305e7ed710b8456c79fc1f4308a392c",
    "utc": "2026-09-22T09:13:41.411376+00:00"
  },
  "reviewer_compound_attacks": {
    "all_rejected": true,
    "case_ids": [
      "CA-1",
      "CA-10",
      "CA-2",
      "CA-3",
      "CA-4",
      "CA-5",
      "CA-6",
      "CA-7",
      "CA-8",
      "CA-9"
    ],
    "survivor_count": 0
  },
  "surviving_critical": 0,
  "surviving_high": 0,
  "total": 62
}
~~~

## Source freeze

~~~json
{
  "authority_effect": "NONE",
  "authority_reference": {
    "current_source_policy_id": "CURRENT-SOURCE-FREEZE-V1",
    "delivery_binding_policy_id": "SOURCE-FREEZE-DELIVERY-DERIVATION-V1",
    "policy_id": "CURRENT-SOURCE-FREEZE-V1",
    "root_commit": "f0792cc01915eb3accd893aba2ed107bed9ec560",
    "semantics": "The preregistered root authorizes the derivation rule; this artifact records current-S binding evidence only and grants no authority."
  },
  "delivery_binding": {
    "authoritative": false,
    "items": {
      "a": {
        "sha256": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
        "size": 1
      }
    },
    "manifest_hash": "f68682c3320c4f6a430be13c46a3c4fec21a26195e57c100aeff29c6892c7518",
    "policy_id": "SOURCE-FREEZE-DELIVERY-DERIVATION-V1",
    "request_id": "r",
    "reviewed_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
    "role": "DERIVED_BINDING_EVIDENCE"
  },
  "exp_m_state": "NOT_QUALIFIED",
  "live_provider_api_execution": false,
  "schema": "EXP-M-SOURCE-FREEZE/v2",
  "source_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
  "source_files": {
    ".github/workflows/exp-m-r2e-offline.yml": "a442529f1cec46ddeceb227363358d459d480c542f0212148a575c2520b6241f",
    ".github/workflows/exp-m-r2e-sep.yml": "1dcd6a7ea8fdd420d806dcc8ef385cf6a6b24f6fba49a6540af9d497dc7484f1",
    "experiments/governed-platform/EXP-M-R2E-EXTERNAL-REVIEW-R2.md": "4e29137de0c123b188eb43c79d09feb2a16ff0f5ce3b0ba8212c8a827a938ff9",
    "experiments/governed-platform/EXP-M-R2E-INTERNAL-ADJUDICATION-R3.md": "e4b2f3b732191c0f80bd7f94e62e5a22a5bae0d1f4d205b95eb57d3186b1fbb1",
    "experiments/governed-platform/EXP-M-R2E-REVIEW-R2-ADJUDICATION.md": "7a768d7008dbeacf77a6c75df70ace4427bd92abc6c55e983fc4a46c83cba33c",
    "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-ADJUDICATION.md": "408a3485e51521e223aacf30bd1185b67ec68f14b6b352d7f65a866ecbffe73c",
    "experiments/governed-platform/PRIOR-EVIDENCE-INDEX.md": "6de4040c8a928a036404a940e0403ec314989d7c041b2c40a08e7fa22a84a6fc",
    "governance-runtime/build_exp_m_portable_review_bundle.py": "8f0cbe14a3d7975c79458830fc99367e44b54ca7c770b6cd58c8a961d0b75fc0",
    "governance-runtime/build_exp_m_r2e_packet.py": "0453e33b3364d4c343741653a8e047b08fe631aa3b28c1273f3b905b91d721d8",
    "governance-runtime/build_exp_m_review_packet.py": "c2861f61278d0c529a5719e588e9022f73d35ff31c7c6a20a9b381ed4aa8bc0a",
    "governance-runtime/build_prior_evidence_index.py": "60ddacbac112f8cbaba62bc1f81d71724145df9e518eb80f9faf512d739886c2",
    "governance-runtime/exp_m_deterministic.py": "238d4c38271aec8fb9c67e7a5b9226dd8a213a1f58bc2eab4c59d7e701b52dff",
    "governance-runtime/exp_m_expectation_authority.py": "2b1e602f64067c7d1c78d2acf7864437ff6bdbc06631161de582c05c22926b20",
    "governance-runtime/exp_m_mutation_catalog.py": "5c9da2dad5f36451075e1847c368eae031e4ff8f08baa3ca938f3eaa57bff08d",
    "governance-runtime/exp_m_predicate_registry.py": "357dcfc7241e5cb0ff1e3a051be3826f4c95a48af922bb2fdce60dc47321d255",
    "governance-runtime/exp_m_review_fixtures.py": "91f02d0cd05902cfa2c47e6a3d2bc12522438a46fcf3963cc774c21ae9b6f3a4",
    "governance-runtime/exp_m_test_fixtures.py": "4d3cabb858481dc7e39c523b7b353740011e87c2c4b81c42a7686d357b488832",
    "governance-runtime/freeze_source.py": "7309eaa278179e308e0e13c2f00ac6208c520ab22ecce24ee13d221d8f5fc515",
    "governance-runtime/generate_evidence.py": "5996257b6f3144ba6fdf6187707be627faebc5def713c3d3cc96bf569f3ce7ae",
    "governance-runtime/reviewer_exp_m_r2e_authority_suite.py": "ed3dc5b0ab73ac866b9482ec3573f0d68c1970baf1f44f680912d0c2c95c5d45",
    "governance-runtime/reviewer_exp_m_r2e_compound_suite.py": "4d4668db91efc73ce5327c49c22cdeb2d9e62e10ae5509eec14dfead454b4329",
    "governance-runtime/reviewer_exp_m_r2e_suite.py": "f5164eec5e795b9ef927f65b8a0261a8736dab2e10c86a3a6a868cde0055dd96",
    "governance-runtime/run_exp_m_deterministic.py": "8d8f028cc466c28a587cfbbb9a813b708c2a48a541bd8ca1fa7a6484a4880583",
    "governance-runtime/run_exp_m_mutations.py": "be705ba0749bc9df7fd4d1a3c26afbb81b060f0c4a8bb1933a3f036a95d257fb",
    "governance-runtime/run_exp_m_static_review_probes.py": "c0bcff168444405d1f3fc26e82ae0075770ffbd58477306f5bfea117e4734f77",
    "governance-runtime/run_exp_m_tests.py": "f6d5e35c401ce7393f23de5c5cd0f583c655ea8403575c968f2d664e3a9fb11c",
    "governance-runtime/run_reviewer_compound_attacks.py": "23d512cd09ab98b90f8fbda62437e760a1c87f22945af632a47ab26cb4cbcadb",
    "governance-runtime/self_adjudicate_r2d.py": "e320addbc158cdf2d94959476ca2928d8d9ccdf9a8b1bc070b243f6d38336d20",
    "governance-runtime/self_falsify_exp_m.py": "5a4b98f878d0ec4872834e2c8f7a9501f180bfef07b34f10c50485f56d0844da",
    "governance-runtime/test_exp_m_deterministic.py": "cc9a89a63d321163fbe9adcb1ffcab0086aa2c8fa6d9e2cd1730c23fa31b5c5d",
    "governance-runtime/test_exp_m_phases.py": "7db4f55d3aaac806f908338da7abbdade85c5ce354ce1204e3fceafefccc12fa",
    "governance-runtime/verify_exp_m_prior_evidence.py": "b31ead9529327addb156dad10722f9955a485d126e2bf26e9fd7f02429267420",
    "governance-runtime/verify_exp_m_sep_sequence.py": "11763d584fce3ad074c42ff7410169b21b38cbcd2b07e5f839f8cc6eb0d98ed2",
    "governance-runtime/verify_sep_sequence.py": "24928ca87f9dccac33ae7262e0a95cd8a1096e2f9a8d1512e0205dcf0f65289b"
  },
  "source_tree": "8a812eeb4305e7ed710b8456c79fc1f4308a392c"
}
~~~

## Evidence manifest

The evidence manifest intentionally does not list itself as an artifact because that would create self-hash recursion. The immutable P packet independently attests the exact manifest bytes stored at E.

~~~json
{
  "artifacts": [
    {
      "path": "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json",
      "sha256": "fecd65b30aa0a7e214ec4330b4f1c566e9cb73d963455dcc827aaf7744c9ffb5",
      "size": 5391
    },
    {
      "path": "experiments/governed-platform/EXP-M-TEST-RESULTS.json",
      "sha256": "07b9f469ce5c81ac3ca746976c5c894849ee67285ceccc14b2a0469ed0c6006c",
      "size": 8662
    },
    {
      "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json",
      "sha256": "6ff0e0d9dd711b3e3babbe772386aab2f77d2e8b6fe01a3b994055ae177b6c1c",
      "size": 30495
    },
    {
      "path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
      "sha256": "207e9d48de04d581ea32ff1d9ef74d18193973c0b7cd44a826568ba886e059e1",
      "size": 32290
    },
    {
      "path": "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json",
      "sha256": "67cfee563d21f4cfb46be8df23a2f03d8b59bb2c77e779d745c7b0c6adf60b3b",
      "size": 6430
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json",
      "sha256": "1084c5435a36d588767b44048c52d1cf6c6f7b81240d7e6810085272ffc3e798",
      "size": 5145
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json",
      "sha256": "003dbdce34e96972995486f9aa8d170c00f80cd62f9a7c17f959d157c0bfc0f9",
      "size": 3015
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2D-SELF-ADJUDICATION.json",
      "sha256": "e4399b5edcc04ef0c1d37412d7d8c0bcb0f266adea383618509520004d1f6b8e",
      "size": 760
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-SOURCE-FREEZE-STDOUT.txt",
      "sha256": "5491f366e314fc836519bed69d71bd3f6dd84c6c45e30024c86bde508f2cb744",
      "size": 6819
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt",
      "sha256": "02ba6886f321cc645260ad6418c6fa7d8045b24bc9ba04a8d8a7eca9a35991bc",
      "size": 1101
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt",
      "sha256": "bdef7910650cd4c7497376808382b84fe3ed523c1f016bc4dcbb40d347fa9bf5",
      "size": 10030
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt",
      "sha256": "eaa0a91c7bab153468c028eeaa81d8c6b58a0656bde726034fa78b660e6913fa",
      "size": 2427
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt",
      "sha256": "6475190f19e8dc3efb804ce21546ebd8776dc8cbdd44a9f2b127557ecc4afba5",
      "size": 2482
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt",
      "sha256": "291abaa112399fc42182536f87b61e48406c652cf624b70a73b6d09a911e5704",
      "size": 8593
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt",
      "sha256": "52945e923b7e57b5590659a67bf7bc4af8c0a9f6251cf9f3c76459736adf8376",
      "size": 4489
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt",
      "sha256": "4b7fd9aaae8abc37c2b3b0b02f89fd6a70710877e1c2ab3f8fb11ce1f29558d2",
      "size": 35072
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt",
      "sha256": "f5207ce3355ecb24b90e1c643bdbdfb9a04f10622f7a0ebf9cf1448582b8091a",
      "size": 36937
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt",
      "sha256": "141ab088dffea96f729bdb4c070aaa79eba575257aa13299eb07efe167dd5960",
      "size": 8421
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-SELF-ADJUDICATION-STDOUT.txt",
      "sha256": "366bb56b31f26d18d347ec61550e3a0b7ef06404406fc06a946381d7f8e62228",
      "size": 2015
    }
  ],
  "authority_effect": "NONE",
  "commands": [
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/freeze_source.py",
      "command_source_path": "governance-runtime/freeze_source.py",
      "command_source_sha256": "7309eaa278179e308e0e13c2f00ac6208c520ab22ecce24ee13d221d8f5fc515",
      "exit_code": 0,
      "name": "source-freeze",
      "portable_command": "python governance-runtime/freeze_source.py",
      "result_path": "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json",
      "result_sha256_at_command_exit": "fecd65b30aa0a7e214ec4330b4f1c566e9cb73d963455dcc827aaf7744c9ffb5",
      "result_size_at_command_exit": 5391,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-SOURCE-FREEZE-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "fecd65b30aa0a7e214ec4330b4f1c566e9cb73d963455dcc827aaf7744c9ffb5",
      "stdout_payload_size": 5391,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "5491f366e314fc836519bed69d71bd3f6dd84c6c45e30024c86bde508f2cb744"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/verify_exp_m_prior_evidence.py",
      "command_source_path": "governance-runtime/verify_exp_m_prior_evidence.py",
      "command_source_sha256": "b31ead9529327addb156dad10722f9955a485d126e2bf26e9fd7f02429267420",
      "exit_code": 0,
      "name": "prior-evidence",
      "portable_command": "python governance-runtime/verify_exp_m_prior_evidence.py",
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt",
      "stdout_payload_sha256": "4655fb93a5b5b0105ff370eb8b00f0b90913fc448c7f8e7dc630d037883c12c7",
      "stdout_payload_size": 26,
      "stdout_role": "source-bound command-console capture",
      "stdout_sha256": "02ba6886f321cc645260ad6418c6fa7d8045b24bc9ba04a8d8a7eca9a35991bc"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_tests.py",
      "command_source_path": "governance-runtime/run_exp_m_tests.py",
      "command_source_sha256": "f6d5e35c401ce7393f23de5c5cd0f583c655ea8403575c968f2d664e3a9fb11c",
      "exit_code": 0,
      "name": "tests",
      "portable_command": "python governance-runtime/run_exp_m_tests.py",
      "result_path": "experiments/governed-platform/EXP-M-TEST-RESULTS.json",
      "result_sha256_at_command_exit": "07b9f469ce5c81ac3ca746976c5c894849ee67285ceccc14b2a0469ed0c6006c",
      "result_size_at_command_exit": 8662,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "07b9f469ce5c81ac3ca746976c5c894849ee67285ceccc14b2a0469ed0c6006c",
      "stdout_payload_size": 8662,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "bdef7910650cd4c7497376808382b84fe3ed523c1f016bc4dcbb40d347fa9bf5"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/reviewer_exp_m_r2e_suite.py",
      "command_source_path": "governance-runtime/reviewer_exp_m_r2e_suite.py",
      "command_source_sha256": "f5164eec5e795b9ef927f65b8a0261a8736dab2e10c86a3a6a868cde0055dd96",
      "exit_code": 0,
      "name": "reviewer-core",
      "portable_command": "python governance-runtime/reviewer_exp_m_r2e_suite.py",
      "stderr_payload_sha256": "df3364cac4c04084d7927b7a1f13976243557ac312a5cf96a03f9b800f6d2d65",
      "stderr_payload_size": 1347,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt",
      "stdout_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stdout_payload_size": 0,
      "stdout_role": "source-bound command-console capture",
      "stdout_sha256": "eaa0a91c7bab153468c028eeaa81d8c6b58a0656bde726034fa78b660e6913fa"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
      "command_source_path": "governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
      "command_source_sha256": "ed3dc5b0ab73ac866b9482ec3573f0d68c1970baf1f44f680912d0c2c95c5d45",
      "exit_code": 0,
      "name": "reviewer-authority",
      "portable_command": "python governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
      "stderr_payload_sha256": "fc30f2c69b66e508a2582cf7cc8a81e60a4fa44f687d02105c1219948b9908a3",
      "stderr_payload_size": 1368,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt",
      "stdout_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stdout_payload_size": 0,
      "stdout_role": "source-bound command-console capture",
      "stdout_sha256": "6475190f19e8dc3efb804ce21546ebd8776dc8cbdd44a9f2b127557ecc4afba5"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_reviewer_compound_attacks.py",
      "command_source_path": "governance-runtime/run_reviewer_compound_attacks.py",
      "command_source_sha256": "23d512cd09ab98b90f8fbda62437e760a1c87f22945af632a47ab26cb4cbcadb",
      "exit_code": 0,
      "name": "reviewer-compound",
      "portable_command": "python governance-runtime/run_reviewer_compound_attacks.py",
      "result_path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json",
      "result_sha256_at_command_exit": "1084c5435a36d588767b44048c52d1cf6c6f7b81240d7e6810085272ffc3e798",
      "result_size_at_command_exit": 5145,
      "stderr_payload_sha256": "ab3c63494bf8129a9427180bf3f8cc4724c42d60190ece7beff8ec04d1413916",
      "stderr_payload_size": 1819,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "1084c5435a36d588767b44048c52d1cf6c6f7b81240d7e6810085272ffc3e798",
      "stdout_payload_size": 5145,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "291abaa112399fc42182536f87b61e48406c652cf624b70a73b6d09a911e5704"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_static_review_probes.py",
      "command_source_path": "governance-runtime/run_exp_m_static_review_probes.py",
      "command_source_sha256": "c0bcff168444405d1f3fc26e82ae0075770ffbd58477306f5bfea117e4734f77",
      "exit_code": 0,
      "name": "static-review-probes",
      "portable_command": "python governance-runtime/run_exp_m_static_review_probes.py",
      "result_path": "experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json",
      "result_sha256_at_command_exit": "003dbdce34e96972995486f9aa8d170c00f80cd62f9a7c17f959d157c0bfc0f9",
      "result_size_at_command_exit": 3015,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "003dbdce34e96972995486f9aa8d170c00f80cd62f9a7c17f959d157c0bfc0f9",
      "stdout_payload_size": 3015,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "52945e923b7e57b5590659a67bf7bc4af8c0a9f6251cf9f3c76459736adf8376"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_deterministic.py",
      "command_source_path": "governance-runtime/run_exp_m_deterministic.py",
      "command_source_sha256": "8d8f028cc466c28a587cfbbb9a813b708c2a48a541bd8ca1fa7a6484a4880583",
      "exit_code": 0,
      "name": "phases",
      "portable_command": "python governance-runtime/run_exp_m_deterministic.py",
      "result_path": "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json",
      "result_sha256_at_command_exit": "6ff0e0d9dd711b3e3babbe772386aab2f77d2e8b6fe01a3b994055ae177b6c1c",
      "result_size_at_command_exit": 30495,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "6ff0e0d9dd711b3e3babbe772386aab2f77d2e8b6fe01a3b994055ae177b6c1c",
      "stdout_payload_size": 30495,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "4b7fd9aaae8abc37c2b3b0b02f89fd6a70710877e1c2ab3f8fb11ce1f29558d2"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_mutations.py",
      "command_source_path": "governance-runtime/run_exp_m_mutations.py",
      "command_source_sha256": "be705ba0749bc9df7fd4d1a3c26afbb81b060f0c4a8bb1933a3f036a95d257fb",
      "exit_code": 0,
      "name": "mutations",
      "portable_command": "python governance-runtime/run_exp_m_mutations.py",
      "result_path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
      "result_sha256_at_command_exit": "207e9d48de04d581ea32ff1d9ef74d18193973c0b7cd44a826568ba886e059e1",
      "result_size_at_command_exit": 32290,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "207e9d48de04d581ea32ff1d9ef74d18193973c0b7cd44a826568ba886e059e1",
      "stdout_payload_size": 32290,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "f5207ce3355ecb24b90e1c643bdbdfb9a04f10622f7a0ebf9cf1448582b8091a"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/self_falsify_exp_m.py",
      "command_source_path": "governance-runtime/self_falsify_exp_m.py",
      "command_source_sha256": "5a4b98f878d0ec4872834e2c8f7a9501f180bfef07b34f10c50485f56d0844da",
      "exit_code": 0,
      "name": "self-falsification",
      "portable_command": "python governance-runtime/self_falsify_exp_m.py",
      "result_path": "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json",
      "result_sha256_at_command_exit": "67cfee563d21f4cfb46be8df23a2f03d8b59bb2c77e779d745c7b0c6adf60b3b",
      "result_size_at_command_exit": 6430,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "67cfee563d21f4cfb46be8df23a2f03d8b59bb2c77e779d745c7b0c6adf60b3b",
      "stdout_payload_size": 6430,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "141ab088dffea96f729bdb4c070aaa79eba575257aa13299eb07efe167dd5960"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/self_adjudicate_r2d.py",
      "command_source_path": "governance-runtime/self_adjudicate_r2d.py",
      "command_source_sha256": "e320addbc158cdf2d94959476ca2928d8d9ccdf9a8b1bc070b243f6d38336d20",
      "exit_code": 0,
      "name": "self-adjudication",
      "portable_command": "python governance-runtime/self_adjudicate_r2d.py",
      "result_path": "experiments/governed-platform/EXP-M-R2D-SELF-ADJUDICATION.json",
      "result_sha256_at_command_exit": "e4399b5edcc04ef0c1d37412d7d8c0bcb0f266adea383618509520004d1f6b8e",
      "result_size_at_command_exit": 760,
      "stderr_payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_payload_size": 0,
      "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-SELF-ADJUDICATION-STDOUT.txt",
      "stdout_payload_identical_to_result": true,
      "stdout_payload_sha256": "e4399b5edcc04ef0c1d37412d7d8c0bcb0f266adea383618509520004d1f6b8e",
      "stdout_payload_size": 760,
      "stdout_role": "source-bound exact result serialization",
      "stdout_sha256": "366bb56b31f26d18d347ec61550e3a0b7ef06404406fc06a946381d7f8e62228"
    }
  ],
  "compound_attack_survivors": 0,
  "exp_m_state": "NOT_QUALIFIED",
  "generated_at_utc": "2026-09-22T09:13:41.703294+00:00",
  "live_provider_api_execution": false,
  "manifest_self_attestation": {
    "included_in_artifacts": false,
    "reason": "self-hash recursion is intentionally avoided; P independently attests the complete manifest bytes as stored at E"
  },
  "reproducibility": {
    "checkout_sequence": [
      "git fetch --all --tags --prune",
      "git checkout --detach <S>",
      "git rev-parse HEAD",
      "git rev-parse HEAD^{tree}",
      "verify clean worktree before evidence generation"
    ],
    "dependency_basis": "governed Python source import audit found only Python standard-library and repository-local modules",
    "dynamic_code_sites": [],
    "dynamic_import_sites": [],
    "git_version": "git version 2.55.0",
    "github_actions_all_pinned_by_commit_sha": true,
    "github_actions_dependencies": {
      ".github/workflows/exp-m-r2e-offline.yml": [
        "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
      ],
      ".github/workflows/exp-m-r2e-sep.yml": [
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
      ]
    },
    "github_actions_image_os": "ubuntu24",
    "github_actions_image_version": "20260907.300.1",
    "network_capable_imports": [],
    "network_required_for_test_commands": false,
    "platform": "Linux-6.17.0-1022-azure-x86_64-with-glibc2.39",
    "python_executable": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "python_version": "3.12.14 (main, Aug 13 2026, 02:47:42) [GCC 13.3.0]",
    "runner_arch": "X64",
    "runner_os": "Linux",
    "third_party_python_dependencies": [],
    "unfrozen_local_imports": []
  },
  "schema": "EXP-M-R2E-EVIDENCE-MANIFEST/v4",
  "source_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
  "source_tree": "8a812eeb4305e7ed710b8456c79fc1f4308a392c"
}
~~~

## Evidence manifest post-generation attestation

~~~json
{
  "attestation_stage": "P",
  "git_blob": "3bb5afd10b78938d440a219421dd2b9ebe90f76a",
  "path": "experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json",
  "reason_not_self_listed": "The manifest cannot safely contain its own final cryptographic hash without self-reference. P independently attests the exact manifest bytes stored at E.",
  "sha256": "688c0ffc3d58331b48d17fb02cd497d3cfa94616da0e57920c414e3b835113aa",
  "size": 19223
}
~~~

## Static-review clarification probes

~~~json
{
  "authority_effect": "NONE",
  "execution": {
    "command": "python governance-runtime/run_exp_m_static_review_probes.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "06fc3a9784105ec35c6eb231c261de361e28f5db",
    "source_tree": "8a812eeb4305e7ed710b8456c79fc1f4308a392c",
    "utc": "2026-09-22T09:10:55.575443+00:00"
  },
  "exp_m_state": "NOT_QUALIFIED",
  "live_provider_api_execution": false,
  "schema": "EXP-M-R2E-STATIC-REVIEW-PROBES/v1",
  "sr_1_ca9": {
    "admissible": false,
    "caller_disposition": "PASS",
    "derived_disposition": "CHANGES_REQUIRED",
    "disposition_promotable_value": false,
    "failed_predicates": [
      "review_request_current",
      "authority_snapshot_current",
      "evidence_contract_closed",
      "interaction_contract_closed",
      "materialization_complete",
      "representation_governed",
      "egress_authorized",
      "capability_current",
      "accessibility_policy_satisfied",
      "context_isolation_satisfied",
      "hidden_state_policy_satisfied",
      "context_state_clean",
      "admission_fence_current",
      "semantic_context_qualified",
      "wire_binding_valid",
      "delivery_complete",
      "accessibility_proven",
      "witness_record_current",
      "session_retrieval_coverage",
      "prompt_isolation_current",
      "semantic_coverage",
      "reviewer_provenance",
      "disposition_promotable"
    ],
    "interpretation": "disposition_promotable is a predicate name. False means the derived disposition is not promotable or conflicts with the caller-supplied disposition; it is not a positive rejection status.",
    "verdict_reasons": [
      "review_request_current",
      "authority_snapshot_current",
      "evidence_contract_closed",
      "interaction_contract_closed",
      "materialization_complete",
      "representation_governed",
      "egress_authorized",
      "capability_current",
      "accessibility_policy_satisfied",
      "context_isolation_satisfied",
      "hidden_state_policy_satisfied",
      "context_state_clean",
      "admission_fence_current",
      "semantic_context_qualified",
      "wire_binding_valid",
      "delivery_complete",
      "accessibility_proven",
      "witness_record_current",
      "session_retrieval_coverage",
      "prompt_isolation_current",
      "semantic_coverage",
      "reviewer_provenance",
      "disposition_promotable"
    ]
  },
  "sr_2_ca10": {
    "fault_injected_error": "r5_protocol_unavailable",
    "fault_injected_protocol_available": false,
    "fault_injection_method": "AuthorityHandle.with_missing_r5_protocol_for_test()",
    "interpretation": "CA-10 deliberately removes protocol availability only from the test AuthorityHandle; it does not assert that the real authority root lacks the frozen R5 protocol.",
    "real_protocol_available": true,
    "real_protocol_id": "R5-CP-1",
    "real_protocol_live_provider_execution_authorized": false,
    "real_protocol_version": "2"
  }
}
~~~

## Independent external review R2 (CHANGES_REQUIRED)

# Independent External Review — EXP-M Deterministic Implementation R2E — R2

Disposition: **CHANGES_REQUIRED**

Authority effect: **NONE**

EXP-M: **NOT_QUALIFIED**

Live provider/API execution: **not authorized and not performed**

## Finding 1 — Unrecorded post-processing breaks chain-of-custody for critical results

The evidence manifest records `stdout_payload_identical_to_result=false` for `reviewer-compound` and `self-falsification`, with `stdout_role` stating the final result artifact differs because governed post-processing occurred after command execution.

Impact: `EXP-M-R2E-COMPOUND-RESULTS.json` and `EXP-M-SELF-FALSIFICATION-RESULTS.json` are not directly bound to the captured command output. No post-processing command, script hash, input/output hash binding, or capture envelope is present. This is a remaining false-green/replay path.

Required remediation: Either eliminate post-processing so the result artifact is byte-identical to the command stdout raw payload, or record post-processing as a governed command with its own source-bound capture envelope, script hash, input raw-payload hash, output artifact hash, and S identity.

## Finding 2 — Authority delivery-ledger mismatch

The source freeze contains a current-S delivery record for request `r`, while the pinned authority delivery ledger and signed test expectations remain anchored to the legacy reviewed commit `2814499a37912ea252b759c530fc07bdcef4950c`.

Impact: Two conflicting delivery-authority records exist. If runtime uses the source-freeze copy it is an authority substitution; if runtime uses the pinned ledger the source freeze is inconsistent or stale.

Required remediation: Reconcile the two records and state which is authoritative for the current S-E-P-Q sequence. Any current-S derivation must be explicitly rooted in the external authority rather than silently substituting candidate-generated authority.

## Finding 3 — Missing generation provenance for EXP-M-SOURCE-FREEZE.json

`EXP-M-SOURCE-FREEZE.json` is an E artifact but the evidence manifest contains no source-bound command record for its generation.

Impact: Its final hash is attested, but its generation provenance is outside the command-capture chain.

Required remediation: Add a source-bound generation capture with S commit/tree, command identity, exit code, raw output hash/size, and result artifact binding.

## Finding 4 — Q / S-E-P-Q separation is incomplete

The textual handoff identifies S, E and P but not Q commit/tree and contains no explicit S-E-P-Q verification output.

Impact: The complete S -> E -> P -> Q sequence cannot be independently verified from the handoff.

Required remediation: Publish Q commit/tree and an explicit S-E-P-Q verification capture.

## Finding 5 — Full mutation and self-falsification results are not embedded

Only summaries are visible in the textual handoff.

Impact: The reviewer cannot adversarially inspect every mutation/self-falsification case and rejection reason from the handoff text alone.

Required remediation: Embed the complete mutation and self-falsification JSON or make their complete bytes available and hash-bound in the portable review bundle.

## Finding 6 — CA-9 / CA-10 clarified, but field name remains misleading

CA-9 and CA-10 semantics are sufficiently clarified, but `rejection_reason` still carries a guard/predicate identifier for CA-9.

Required remediation: Rename the field to `blocking_guard` or `predicate_failed` in the next schema revision. This is secondary to the primary blockers.

## Finding 7 — Handoff alone cannot complete hash / Git-object verification

The handoff does not itself contain the referenced Git objects.

Impact: Commit/blob and manifest identities cannot be independently recomputed from text alone.

Required remediation: Ensure the portable bundle contains the required Git objects or exact offline fetch instructions plus a verifier; bind every required artifact, excluding only a self-referential manifest with explicit justification.

## Final disposition

**CHANGES_REQUIRED**

Authority effect remains **NONE**. EXP-M remains **NOT_QUALIFIED**. No live provider/API execution is authorized or performed.

## Internal adversarial adjudication R3

# EXP-M R2E Internal Adjudication R3

Status: **REMEDIATED_PENDING_FRESH_GREEN_CHAIN**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This is an additional adversarial internal adjudication loop requested after the R2 remediation reached a green preflight. It does not replace independent external review and cannot grant qualification.

## IA-R3-01 — Candidate-selectable authority root / missing temporal preregistration proof

Severity: **Critical**

### Failure path

The candidate source contained `DEFAULT_AUTHORITY_COMMIT`, while the S-E-P verifier also contained a matching authority-root constant. The preregistered reviewer-authority suite exercised `load_default_authority()` but did not itself freeze the exact permitted authority-root commit. A coordinated candidate change could therefore redirect both loader and verifier to a candidate-selected historical Git object while preserving self-consistency.

The verifier also compared reviewer-suite bytes to named preregistration commits but did not require those commits to be strict ancestors of source S. A candidate could therefore point a "preregister" anchor at S itself or at a non-prior object.

### Remediation

1. Created authority root v3 at immutable commit:
   `f0792cc01915eb3accd893aba2ed107bed9ec560`.
2. Root v3 removes reviewer-suite back-pointers, avoiding circular trust. It states that reviewer suites are preregistered separately after the root and before candidate S.
3. Created reviewer-authority preregistration commit:
   `aae96510eb1ac05b45b961b62a5ea2b010ad6b32`.
4. That preregistered suite contains the literal:
   `EXPECTED_AUTHORITY_ROOT_COMMIT = "f0792cc01915eb3accd893aba2ed107bed9ec560"`
   and tests that both `DEFAULT_AUTHORITY_COMMIT` and the loaded authority handle equal it.
5. The S-E-P-Q verifier requires:
   - current reviewer-authority suite bytes equal the preregistered suite bytes;
   - the suite literal equals the verifier's preregistered root;
   - every reviewer-suite preregistration commit is a strict ancestor of S;
   - authority root v3 is a strict ancestor of the reviewer-authority preregistration commit;
   - authority root v3 is a strict ancestor of S.
6. Current candidate loader, source-freeze generation, packet builder, portable-bundle builder and S-E-P-Q verifier all consume authority root v3.

Adjudication: **REMEDIATED_IN_DESIGN; requires fresh green evidence and independent review.**

## IA-R3-02 — Unfrozen local dependency / dynamic-load provenance bypass

Severity: **High**

### Failure path

The source freeze selected EXP-M-named Python files plus explicit files. The reproducibility import audit classified repository-local imports as "local" but did not require every imported local module to be present in the source-freeze map. A candidate could move load-bearing logic into a differently named local Python module, import it, and influence evidence while the helper remained outside the frozen source set.

Likewise, a non-literal `__import__` / `importlib.import_module` or dynamic `eval` / `exec` path could evade the static import closure. Top-level evidence commands also recorded their script hash but the verifier did not require that command source path itself be in the source-freeze map.

### Remediation

1. Reproducibility audit now maps local module names to repository paths and records `unfrozen_local_imports`.
2. Evidence generation fails closed if any imported local Python module is not in the source-freeze set.
3. Literal `__import__("module")` calls are included in the dependency set.
4. Non-literal `__import__` and `importlib.import_module` calls fail closed as `dynamic_import_not_statically_bound`.
5. `eval` and `exec` calls in the governed source surface fail closed as `dynamic_code_execution_not_allowed`.
6. S-E-P-Q verification requires every captured evidence-command `command_source_path` to be present in `EXP-M-SOURCE-FREEZE.json` and requires the source-freeze hash, capture hash and Git S hash to agree.
7. Offline CI now creates adversarial temporary local modules and proves:
   - an unfrozen local import is detected;
   - a non-literal dynamic import is detected;
   - same-commit "preregistration" is not considered a strict ancestor;
   - the authority root is a strict ancestor of the candidate.

Adjudication: **REMEDIATED_IN_DESIGN; requires fresh green evidence and independent review.**

## IA-R3-03 — Remediation implementation defect found by the loop

Severity: **Implementation defect, fail-closed**

During the first post-remediation offline run, the new command-source provenance check referenced `source_files` before binding it from the evidence source-freeze artifact. The verifier crashed with `NameError` rather than yielding a false PASS.

Remediation:
- `verify_exp_m_sep_sequence.py` now binds and validates `source_files = freeze["source_files"]` immediately after loading the E source-freeze artifact.
- Missing/empty source-file maps are explicit verification failures.

Adjudication: **FIXED; no false green occurred.**

## R3 closure rule

This internal adjudication is not a PASS authority. Closure of R3 requires:
1. latest offline falsification run succeeds on the exact post-R3 source;
2. local S -> E -> P -> Q construction and explicit verification succeed;
3. portable review bundle and nested Git-object verifier succeed outside the repository worktree;
4. no live provider/API execution occurs;
5. after final source freeze, a fresh governed remote S -> E -> P -> Q sequence is produced;
6. the resulting bundle is sent to an independent external reviewer.

Until independent review:
- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized

## External review R2 remediation adjudication

# EXP-M R2E External Review R2 — Remediation Adjudication

Status: **REMEDIATED_PENDING_FRESH_S_E_P_Q_AND_INDEPENDENT_REVIEW**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This record maps every finding from `EXP-M-R2E-EXTERNAL-REVIEW-R2.md` to the narrow remediation implemented after that review. It is internal remediation evidence only. It does not convert the external CHANGES_REQUIRED disposition into PASS. Closure requires a fresh immutable S -> E -> P -> Q sequence, successful offline falsification and bundle verification, followed by independent review of that fresh bundle.

## R2-F1 — Unrecorded result post-processing

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_EVIDENCE**

Remediation:
- Removed the evidence-generator post-processing step that mutated self-falsification after command execution.
- `self_falsify_exp_m.py` now consumes the already source-bound CA-1..CA-10 result inside the governed command, verifies its S commit/tree and zero-survivor closure, and emits the final CA-inclusive self-falsification JSON itself.
- Result-producing commands are now required to have raw stdout bytes exactly equal to the final result artifact bytes.
- Command capture schema v2 records command-source path/SHA-256, S commit/tree, stdout/stderr hashes and sizes, result SHA-256/size at command exit, and the exact stdout/result equality flag.
- Evidence generation fails closed on any result/stdout mismatch; S-E-P verification independently rechecks those bindings.

Residual authority: NONE.

## R2-F2 — Conflicting delivery-authority records

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_EVIDENCE**

Remediation:
- A preregistered authority-root-v2 commit was created before the dependent implementation changes: `251647e5f44d394b761f1c6cdbb02a779901bc43`.
- Root v2 removes the legacy delivery ledger from current authority and freezes a deterministic current-S delivery-binding policy.
- The legacy signed `reviewed_commit=2814499a...` remains only a signed expectation sentinel and is explicitly labeled `LEGACY_SIGNED_EXPECTATION_SENTINEL_ONLY`.
- `EXP-M-SOURCE-FREEZE.json` no longer contains a field named delivery authority. It records `delivery_binding` with `role=DERIVED_BINDING_EVIDENCE` and `authoritative=false`.
- The production authority loader derives the current-S delivery expectation from the preregistered root policy plus the independently verified S identity. It rejects source-freeze policy/root substitution.
- The S-E-P verifier independently resolves authority root v2 and recomputes the same delivery binding.

Residual authority: authority remains solely the preregistered root policy; source freeze grants none.

## R2-F3 — Missing source-freeze generation provenance

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_EVIDENCE**

Remediation:
- `freeze_source.py` is now the first governed evidence command.
- It prints the exact final `EXP-M-SOURCE-FREEZE.json` bytes to stdout.
- Evidence capture records its S commit/tree, exact command, command-source SHA-256, stdout/stderr hashes/sizes, result SHA-256/size, exit code, and exact stdout/result equality.
- Source freeze remains an E artifact and the verifier independently validates its result/capture/source bindings.

## R2-F4 — Incomplete Q / S-E-P-Q verification

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_SEQUENCE**

Remediation:
- `verify_exp_m_sep_sequence.py` now accepts `--handoff Q`.
- It resolves and reports Q commit/tree/parent, requires Q parent=P, and requires P->Q to change only the review-handoff document.
- The verifier records its own S path/SHA-256.
- Final workflows produce an explicit S-E-P-Q verification JSON.
- The portable bundle generates a post-Q `FINAL-REVIEW-HANDOFF.md` containing exact S/E/P/Q commit/tree identities, avoiding commit self-reference.

## R2-F5 — Full mutation/self-falsification results unavailable

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_PACKET**

Remediation:
- P now embeds the full mutation-results JSON and the full self-falsification-results JSON, not only summaries.
- E still hash/size binds those complete artifacts.
- The portable review bundle includes the complete E artifacts and manifest.

## R2-F6 — Misleading CA-9 field name

Adjudication: **REMEDIATED**

Remediation:
- Compound schema bumped to v2.
- `rejection_reason` renamed to `blocking_guard`.
- `rejection_reason_semantics` renamed to `blocking_guard_semantics`.
- CA-9/CA-10 explanatory semantics remain preserved.

## R2-F7 — Handoff alone cannot verify Git objects/hashes

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_BUNDLE**

Remediation:
- The portable bundle now includes a nested Git bundle containing S/E/P/Q, preregistered authority, and indexed historical commits.
- It includes `VERIFY-BUNDLE.py`, which verifies every outer bundle manifest entry, verifies the nested Git bundle, fetches the custom review refs into a temporary repository, recomputes commit/tree identities, recomputes each recorded Git blob identity, and checks included bytes against Git objects.
- It includes `OFFLINE-VERIFY.md` with no-network verification steps.
- It includes explicit S-E-P-Q verification output and `FINAL-REVIEW-HANDOFF.md`.
- `BUNDLE-MANIFEST.json` attests every other outer archive entry; its own exclusion is explicit to avoid recursive self-hashing.

## Closure rule

No finding above is externally closed by this adjudication. The next allowed sequence is:
1. run the full offline falsification/preflight against the exact latest source;
2. if green, freeze a new S;
3. generate fresh E, P, Q and portable review bundle;
4. independently verify the bundle and S-E-P-Q capture;
5. send that fresh bundle to an independent reviewer.

Until step 5 returns an independent acceptable disposition:

- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized

## Static-review clarification adjudication

# EXP-M R2E Static Review Clarification Adjudication

Status: REMEDIATED_PENDING_FRESH_S_E_P

Authority effect: NONE

EXP-M state: NOT_QUALIFIED

Live provider/API execution authorized: false

This record adjudicates the seven clarification findings returned by the static-only independent review of the prior R2E handoff. The reviewer explicitly stated that it could not fetch Git objects, recompute hashes, or execute suites. These findings are therefore separated into implementation defects, evidence/reporting defects, and inherent static-review limitations.

## SR-1 — CA-9 rejection label

Classification: REPORTING_AMBIGUITY

The production governor evaluates all non-disposition predicates first. It then derives PASS only when every underlying predicate is true; otherwise it derives CHANGES_REQUIRED. A caller-supplied disposition that disagrees with that derived disposition is rejected. Therefore the predicate named disposition_promotable is false in CA-9. The earlier compound result used the predicate identifier as a field named rejection_reason, which could be misread as a positive assertion.

Remediation:
- Preserve the preregistered CA-9 attack unchanged.
- Record rejection_reason_semantics as a blocking guard/control label.
- Record guard_semantics explaining that disposition_promotable=false when failed predicates derive CHANGES_REQUIRED and caller PASS cannot override it.
- Explain the same semantics in the review packet.

Adjudication: CLARIFIED; no production-validator weakness identified by this finding.

## SR-2 — CA-10 protocol unavailable while protocol is present

Classification: FAULT-INJECTION-REPORTING_AMBIGUITY

CA-10 intentionally creates an AuthorityHandle with protocol_available=False by calling with_missing_r5_protocol_for_test(). The test asks whether a self-consistent R5 record is rejected when the authoritative protocol is deliberately made unavailable. The real preregistered authority root still contains and hash-binds the R5 protocol.

Remediation:
- Preserve the preregistered CA-10 attack unchanged.
- Add explicit fault_injection metadata to the compound result.
- Explain in the packet that r5_protocol_unavailable is the expected result of this injected negative condition and does not state that the real authority root lacks the protocol.

Adjudication: CLARIFIED; no contradiction between CA-10 and the frozen real protocol.

## SR-3 — Evidence manifest does not list itself

Classification: SELF-REFERENCE / ATTESTATION GAP

A final manifest cannot contain its own final SHA-256 without recursive self-reference. The earlier packet did not explain this.

Remediation:
- Manifest schema explicitly records that it is intentionally not self-listed.
- P independently attests the exact manifest bytes stored at E using SHA-256, size, and Git blob identity.
- S-E-P verification recomputes the E manifest hash and requires the P content to contain the same attestation.

Adjudication: REMEDIATED.

## SR-4 — JSON results and STDOUT have identical hashes

Classification: EVIDENCE-INDEPENDENCE CLARIFICATION

Some runners serialize the result JSON to a file and print the same serialization to stdout. Those two files are duplicate representations and must not be counted as independent corroboration.

Remediation:
- Every command-console capture is now wrapped in a source-bound envelope carrying the exact S commit/tree, command identity, exit code, capture time, and SHA-256/size of the raw console payload.
- The evidence manifest records the envelope hash separately from the raw payload hash.
- When the raw console payload is byte-identical to a corresponding result JSON, the manifest records stdout_payload_identical_to_result=true and labels the capture as non-independent evidence rather than presenting it as corroboration.
- S-E-P verification independently parses every capture envelope, recomputes both envelope and raw-payload hashes/sizes, verifies the S identity and command identity, and checks the declared relationship to any result artifact.
- This also prevents a constant/stale console artifact from silently surviving into a fresh E unchanged.

Adjudication: REMEDIATED.

## SR-5 — Authority-root referenced inputs were not visible in the packet

Classification: STATIC-REVIEW VISIBILITY GAP

The referenced authority inputs are not generated E artifacts. Runtime resolution pins them by the preregistered authority commit and validates the declared hashes. The prior static packet did not include their contents.

Remediation:
- P resolves the authority commit from source S.
- P embeds the authority root, test expectations, signature, R5 protocol, retrieval ledger, delivery ledger, qualification ledger, and retrieval backing-source identity.
- P recomputes declared hashes and fails packet construction on mismatch.
- Git blob identities and SHA-256 values are included for static inspection.

Adjudication: REMEDIATED for static visibility.

## SR-6 — Reproducibility information was partial

Classification: REPRODUCIBILITY EVIDENCE GAP

Remediation:
- E records Python version/executable, platform, Git version, GitHub runner image metadata when available, and portable commands.
- E records an AST import audit across the frozen governed Python source.
- Evidence generation fails if an unexpected third-party Python import is found.
- The governed test surface declares zero third-party Python dependencies and no network requirement for test commands.
- P includes exact source checkout guidance and portable re-execution commands.

Adjudication: REMEDIATED for the governed Python/offline scope.

## SR-7 — Prior failure preservation cannot be independently verified from text alone

Classification: INHERENT STATIC-ONLY REVIEW LIMITATION plus EVIDENCE-VISIBILITY GAP

Independent recomputation of historical Git-object hashes inherently requires the Git objects. A static text handoff cannot itself provide independent proof of repository history.

Remediation:
- E now executes verify_exp_m_prior_evidence.py as a dedicated evidence command and preserves its stdout/hash.
- The full prior-evidence index remains embedded in P.
- The packet explicitly states that independent historical recomputation still requires the pinned Git objects and does not convert a static assertion into authority.

Adjudication: EVIDENCE VISIBILITY REMEDIATED; external independent historical recomputation remains intentionally outside the candidate's authority.

## Closure rule

These clarifications do not grant a PASS. After these changes, a fresh source S, evidence E, packet P, and handoff Q must be generated and the full offline falsification + S-E-P verification gates must pass. The next independent reviewer must review that fresh handoff.

Authority effect remains NONE. EXP-M remains NOT_QUALIFIED.

## Static-review clarifications

- CA-9: disposition_promotable is a blocking predicate identifier, not a positive status. In this attack the underlying predicates fail, the governor derives CHANGES_REQUIRED, and a caller-supplied PASS cannot override it; therefore disposition_promotable evaluates false.
- CA-10: r5_protocol_unavailable is deliberately fault-injected by AuthorityHandle.with_missing_r5_protocol_for_test() for that negative case only. The frozen R5 protocol remains present and hash-bound in the real authority root.
- Every result-producing governed command now emits the exact final result JSON on stdout. The v2 command capture separately records stdout/stderr, command-source SHA-256, result SHA-256/size at command exit, and S commit/tree; any stdout/result byte mismatch fails evidence generation. No later result post-processing is permitted.
- Delivery authority is no longer substituted by the source freeze. Preregistered authority-root v2 freezes the current-S identity rule and delivery derivation policy; EXP-M-SOURCE-FREEZE.json records only non-authoritative derived binding evidence, which the authority loader and S-E-P verifier independently recompute.
- Reproducibility evidence records Python, Git, runner image metadata, exact checkout guidance, and an import audit. The governed Python surface has no third-party Python dependencies; test commands are offline.
- Prior-failure preservation is checked by a dedicated evidence command in E and the full index remains embedded below. Independent historical recomputation still requires the pinned Git objects; that is an inherent limit of static-only review, not an authority grant.

## Reproducibility environment and checkout

~~~json
{
  "checkout_sequence": [
    "git fetch --all --tags --prune",
    "git checkout --detach <S>",
    "git rev-parse HEAD",
    "git rev-parse HEAD^{tree}",
    "verify clean worktree before evidence generation"
  ],
  "dependency_basis": "governed Python source import audit found only Python standard-library and repository-local modules",
  "dynamic_code_sites": [],
  "dynamic_import_sites": [],
  "git_version": "git version 2.55.0",
  "github_actions_all_pinned_by_commit_sha": true,
  "github_actions_dependencies": {
    ".github/workflows/exp-m-r2e-offline.yml": [
      "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
      "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
    ],
    ".github/workflows/exp-m-r2e-sep.yml": [
      "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    ]
  },
  "github_actions_image_os": "ubuntu24",
  "github_actions_image_version": "20260907.300.1",
  "network_capable_imports": [],
  "network_required_for_test_commands": false,
  "platform": "Linux-6.17.0-1022-azure-x86_64-with-glibc2.39",
  "python_executable": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
  "python_version": "3.12.14 (main, Aug 13 2026, 02:47:42) [GCC 13.3.0]",
  "runner_arch": "X64",
  "runner_os": "Linux",
  "third_party_python_dependencies": [],
  "unfrozen_local_imports": []
}
~~~

Exact re-execution sequence from a repository clone:

~~~text
git fetch --all --tags --prune
git checkout --detach 06fc3a9784105ec35c6eb231c261de361e28f5db
git status --porcelain
python governance-runtime/freeze_source.py
python governance-runtime/verify_exp_m_prior_evidence.py
python governance-runtime/run_exp_m_tests.py
python governance-runtime/reviewer_exp_m_r2e_suite.py
python governance-runtime/reviewer_exp_m_r2e_authority_suite.py
python governance-runtime/run_reviewer_compound_attacks.py
python governance-runtime/run_exp_m_static_review_probes.py
python governance-runtime/run_exp_m_deterministic.py
python governance-runtime/run_exp_m_mutations.py
python governance-runtime/self_falsify_exp_m.py
python governance-runtime/self_adjudicate_r2d.py
~~~

## Portable static-review bundle

After Q is created and explicit S-E-P-Q verification succeeds, the governed workflow builds and uploads EXP-M-R2E-PORTABLE-REVIEW-BUNDLE.zip. The ZIP contains frozen source, all E artifacts, full mutation/self-falsification results, P, Q, the S-E-P-Q verification capture, pinned authority inputs, prior-history artifacts, an offline verifier, exact fetch/replay instructions, and a nested Git bundle carrying the referenced commit objects. BUNDLE-MANIFEST.json attests every other archive entry; only the manifest itself is excluded to avoid recursive self-hashing. The ZIP grants no authority.

## Pinned authority input bundle

~~~json
{
  "authority_commit": "f0792cc01915eb3accd893aba2ed107bed9ec560",
  "authority_tree": "2aabd23b15455a063313a75f13ec7220e1502340",
  "files": [
    {
      "content": "{\n  \"root_id\": \"EXP-M-R2E-AUTHORITY-ROOT-3\",\n  \"algorithm\": \"RSA-PKCS1v15-SHA256\",\n  \"public_exponent\": 65537,\n  \"public_modulus_decimal\": \"19406969437044342697006292572534246890649549718354567902768001038286874304304682288020677530606005820054444675079471098425907485198331095391772392801025164916645300473325780772218648947160031840197498040865742698933283040385481975892632796869861298660466727128777265850590008210570317565352170761177301191402556845217267656166718395054603786870476147220744764007503464619233599989818010247587677328630583301117929218359939034728678769665015656442490751063943627454538116262981266197813114553648863497431294732647080288693673751776261338545078532466863274953590622425413421850328414913402167268030046439645802938513031\",\n  \"test_expectation_manifest_path\": \"experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.json\",\n  \"test_expectation_manifest_sha256\": \"f0b7e5dc95a749242ddc0bdf2426789c97c47f7526d426f8cd0973e4580ae543\",\n  \"test_expectation_signature_path\": \"experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.sig\",\n  \"r5_protocol_path\": \"experiments/governed-platform/EXP-M-R5-QUALIFICATION-PROTOCOL.json\",\n  \"r5_protocol_sha256\": \"bf57312019d11529553ab4abdf7586e44ca29cf9c4da02c744f4a65b4fb84876\",\n  \"authority_private_key_committed\": false,\n  \"live_provider_execution_authorized\": false,\n  \"reviewed_commit_anchor\": \"2814499a37912ea252b759c530fc07bdcef4950c\",\n  \"retrieval_source_ledger_path\": \"experiments/governed-platform/EXP-M-R2E-RETRIEVAL-SOURCE-LEDGER.json\",\n  \"retrieval_source_ledger_sha256\": \"61599e9c5fb9975a58799f7e67a50646f9da8b1d7da0f67d87f85ac5b4c5238c\",\n  \"qualification_ledger_path\": \"experiments/governed-platform/EXP-M-R2E-QUALIFICATION-LEDGER.json\",\n  \"qualification_ledger_sha256\": \"73995967363087854175c049ba351fdd2b9ebaaa612789702a1c97241a568c6e\",\n  \"version\": \"3\",\n  \"reviewed_commit_anchor_semantics\": \"LEGACY_SIGNED_EXPECTATION_SENTINEL_ONLY\",\n  \"current_source_identity_policy\": {\n    \"policy_id\": \"CURRENT-SOURCE-FREEZE-V1\",\n    \"source_freeze_path\": \"experiments/governed-platform/EXP-M-SOURCE-FREEZE.json\",\n    \"semantics\": \"The preregistered root authorizes the deterministic derivation rule. The source-freeze artifact supplies immutable S identity and derived binding evidence only; it is not an authority source.\"\n  },\n  \"delivery_binding_policy\": {\n    \"policy_id\": \"SOURCE-FREEZE-DELIVERY-DERIVATION-V1\",\n    \"request_id\": \"r\",\n    \"items\": {\n      \"a\": {\n        \"sha256\": \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\",\n        \"size\": 1\n      }\n    },\n    \"derivation\": \"manifest_hash = SHA256(canonical_json({request_id, reviewed_commit: S, items}))\",\n    \"source_identity\": \"current_source_identity_policy\",\n    \"authority_semantics\": \"Authoritative rule is frozen in this root. EXP-M-SOURCE-FREEZE.json may record only the derived current-S binding and cannot alter request_id, item set, item hashes/sizes, or derivation.\"\n  },\n  \"reviewer_anchor_semantics\": \"Reviewer suites are preregistered in separate immutable Git commits after this authority root is frozen and before candidate S; the root does not point back to those suites, avoiding circular trust.\",\n  \"authority_bootstrap_semantics\": \"Candidate S must use an independently preregistered reviewer-authority suite whose literal EXPECTED_AUTHORITY_ROOT_COMMIT equals this root commit. Candidate-local redirection of the authority commit is non-authoritative.\"\n}\n",
      "declared_sha256": null,
      "git_blob": "6c397f7840f3d4ff077c0b3a30da884729efee84",
      "label": "authority_root",
      "path": "experiments/governed-platform/EXP-M-R2E-AUTHORITY-ROOT.json",
      "sha256": "a999ea876b86d1de4172106c062b0bf37e897bc52f539f0774ddb0c9f6aed173"
    },
    {
      "content": "{\"context\":{\"attempt_id\":\"a\",\"authority_snapshot_hash\":\"snapshot-hash\",\"authority_snapshot_id\":\"snap\",\"authority_version\":\"1\",\"expected_adapter\":\"adapter\",\"expected_authority_generation\":1,\"expected_challenge_id\":\"challenge\",\"expected_context_state_hash\":\"\",\"expected_egress_version\":\"1\",\"expected_fence_attestation\":\"fence-attestation-v1\",\"expected_fence_authority_hash\":\"protected-resource-v1\",\"expected_fence_authority_id\":\"platform-protected-resource\",\"expected_fence_issuer_id\":\"platform-fence-observer\",\"expected_fence_state_hash\":\"\",\"expected_fence_version\":\"1\",\"expected_model\":\"deterministic\",\"expected_operating_point\":\"default\",\"expected_profile_hash\":\"profile-hash\",\"expected_prompt_authority_digest\":\"prompt-authority-v1\",\"expected_prompt_authority_id\":\"platform-prompt-authority\",\"expected_provider\":\"fake\",\"expected_qualification_profile\":\"TEST_PROFILE\",\"expected_reviewer_authority_digest\":\"review-authority-v1\",\"expected_reviewer_issuer_id\":\"platform-review-authority\",\"expected_reviewer_policy_hash\":\"policy\",\"expected_reviewer_role_scope\":\"EXP-M-REVIEW\",\"expected_semantic_algorithm\":\"coverage-v1\",\"expected_semantic_hash\":\"\",\"expected_transition_class\":\"LOWER\",\"expected_witness_answer_hash\":\"ecc15040bffeb51b056b6c2f0a86a77df2dd429b83b866ce94f1f4fe64712f2c\",\"expected_witness_authority_digest\":\"witness-authority-v1\",\"expected_witness_authority_id\":\"platform-witness-authority\",\"fence_version\":\"1\",\"final_context_hash\":\"ctx-h\",\"final_context_id\":\"ctx\",\"max_context_bytes\":1000000,\"predicate_registry_version\":\"2\",\"promotable_dispositions\":[\"PASS\"],\"prompt_mode\":\"inline\",\"prompt_provider\":\"fake\",\"request_id\":\"r\",\"retrieval_source\":\"file\",\"retrieval_version\":\"v\",\"reviewed_commit\":\"2814499a37912ea252b759c530fc07bdcef4950c\",\"session_id\":\"s\",\"transition_class\":\"LOWER\",\"witness_mode\":\"inline\",\"witness_prompt_mode\":\"prompt\",\"witness_provider\":\"fake\"},\"manifest_id\":\"EXP-M-R2E-TEST-EXPECTATIONS-1\",\"scope\":\"OFFLINE_TEST_ONLY\",\"version\":\"1\"}\n",
      "declared_sha256": "f0b7e5dc95a749242ddc0bdf2426789c97c47f7526d426f8cd0973e4580ae543",
      "git_blob": "dc2b53c10eac5e88ecd54ef6c46f4e56ccdd4e9c",
      "label": "test_expectations",
      "path": "experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.json",
      "sha256": "f0b7e5dc95a749242ddc0bdf2426789c97c47f7526d426f8cd0973e4580ae543"
    },
    {
      "content": "gdFVREFD8hBVMd/oCtKFOjiPXoPWrdj54x/J5AkbpzgUl/QrLJCIclUsj3mHxvwFB5Ip5D/Fa806srGYfSwxYaC2l/P+mBKaPTfscQd+x7IH8qCa1ZT3hUzTOMbwFpwvNrV/coh0qw3bc+k9zITRax1WAqCc/zyXa8f5XQm4KdmRrlAaFo3ltaowlzp7DueXwII0S3JjYsuqDpxDgFpGc43elutbhaBcaWKjqZXiCdaKwi/GKZJs9PzenEyjt7LH9g+zz/RXTrRgb+D+3+c0Kq1cm1c3RdVfW/G0udR7YtNqeLDM5UtzpQWovrWK7UvmKbQwERaXrqTS/x7pH7vtFQ==\n",
      "declared_sha256": null,
      "git_blob": "01b6ccad49015480926b7be4d5e702b86db1f844",
      "label": "test_expectations_signature",
      "path": "experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.sig",
      "sha256": "7e15dd863aa88b98f9ce1dea43120090c35f453f2b675e555d285e81866a7724"
    },
    {
      "content": "{\n  \"protocol_id\": \"R5-CP-1\",\n  \"protocol_version\": \"2\",\n  \"confidence_level\": 0.95,\n  \"lower_bound_threshold\": 0.99,\n  \"n_min\": 299,\n  \"success_requirement\": \"ZERO_FIRST_ATTEMPT_FAILURES\",\n  \"retry_policy\": \"NO_RETRY_OR_REPLACEMENT\",\n  \"schedule_requirements\": {\n    \"min_distinct_days\": 3,\n    \"min_distinct_time_blocks\": 4,\n    \"require_exact_plan_coverage\": true,\n    \"assignment_rule\": \"ROUND_ROBIN_DECLARED_ORDER\"\n  },\n  \"distribution_requirements\": {\n    \"day_assignment\": \"attempt_index_mod_scheduled_days\",\n    \"time_block_assignment\": \"attempt_index_mod_scheduled_time_blocks\",\n    \"exact_match_required\": true\n  },\n  \"authority_status\": \"PREREGISTERED_OFFLINE_ONLY\",\n  \"live_provider_execution_authorized\": false\n}\n",
      "declared_sha256": "bf57312019d11529553ab4abdf7586e44ca29cf9c4da02c744f4a65b4fb84876",
      "git_blob": "d1067483fa59d1c0428998d97b90a32784b5cc72",
      "label": "r5_protocol",
      "path": "experiments/governed-platform/EXP-M-R5-QUALIFICATION-PROTOCOL.json",
      "sha256": "bf57312019d11529553ab4abdf7586e44ca29cf9c4da02c744f4a65b4fb84876"
    },
    {
      "content": "{\n  \"sources\": {\n    \"file|v\": {\n      \"length\": 1,\n      \"path\": \"experiments/governed-platform/r2e-authority/retrieval/file-v.bin\",\n      \"sha256\": \"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb\"\n    }\n  },\n  \"version\": \"1\"\n}\n",
      "declared_sha256": "61599e9c5fb9975a58799f7e67a50646f9da8b1d7da0f67d87f85ac5b4c5238c",
      "git_blob": "4ffe2e73d0932a90db37309a60581f98c12c7d98",
      "label": "retrieval_ledger",
      "path": "experiments/governed-platform/EXP-M-R2E-RETRIEVAL-SOURCE-LEDGER.json",
      "sha256": "61599e9c5fb9975a58799f7e67a50646f9da8b1d7da0f67d87f85ac5b4c5238c"
    },
    {
      "content": "{\n  \"plans\": {\n    \"plan\": {\n      \"plan\": {\n        \"confirmation_ids\": [\n          \"a1\"\n        ],\n        \"operating_point\": \"default\",\n        \"plan_id\": \"plan\",\n        \"production_envelope_hash\": \"\",\n        \"provider_id\": \"fake\",\n        \"qualification_profile\": \"TEST_PROFILE\",\n        \"schedule_seed\": \"\",\n        \"scheduled_days\": [],\n        \"scheduled_time_blocks\": [],\n        \"trial_ids\": [\n          \"a1\"\n        ]\n      },\n      \"record\": {\n        \"all_trials_closed\": true,\n        \"attempt_records\": [\n          {\n            \"attempt_id\": \"a1\",\n            \"kind\": \"FIRST\",\n            \"outcome\": \"OK\",\n            \"parent_attempt_id\": null,\n            \"planned_root_id\": \"a1\",\n            \"provider_request_id\": \"\",\n            \"request_hash\": \"\",\n            \"request_id\": \"r\",\n            \"session_id\": \"s\",\n            \"time_block\": \"\",\n            \"utc_day\": \"\",\n            \"wire_hash\": \"wire-a1\"\n          }\n        ],\n        \"closed_attempt_ids\": [\n          \"a1\"\n        ],\n        \"hard_failures\": 0,\n        \"independence_status\": \"STATISTICAL_INDEPENDENCE_UNPROVEN\",\n        \"model_id\": \"deterministic\",\n        \"operating_point\": \"default\",\n        \"plan_id\": \"plan\",\n        \"planned_attempt_ids\": [\n          \"a1\"\n        ],\n        \"profile_hash\": \"profile-hash\",\n        \"protocol_version\": \"R5-CP-1\",\n        \"provider_id\": \"fake\",\n        \"statistical_qualified\": true\n      }\n    }\n  },\n  \"version\": \"1\"\n}\n",
      "declared_sha256": "73995967363087854175c049ba351fdd2b9ebaaa612789702a1c97241a568c6e",
      "git_blob": "2d48d7d3cf00c2b406d219e900e1d02ccc51593f",
      "label": "qualification_ledger",
      "path": "experiments/governed-platform/EXP-M-R2E-QUALIFICATION-LEDGER.json",
      "sha256": "73995967363087854175c049ba351fdd2b9ebaaa612789702a1c97241a568c6e"
    }
  ],
  "note": "Authority inputs are pinned by the preregistered authority commit and consumed by source S. They are not generated E evidence.",
  "retrieval_backing_sources": [
    {
      "content_hex": "61",
      "path": "experiments/governed-platform/r2e-authority/retrieval/file-v.bin",
      "sha256": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
      "size": 1,
      "source_id": "file|v"
    }
  ],
  "root_sha256": "a999ea876b86d1de4172106c062b0bf37e897bc52f539f0774ddb0c9f6aed173"
}
~~~

## Prior failure preservation index

# EXP-M Prior Evidence Index

This index preserves superseded and failed EXP-M deterministic evidence. It is historical evidence only; it grants no qualification or runtime authority.

| ID | Artifact | Pinned commit | SHA-256 at pinned commit | Historical claim | Disposition |
|---|---|---|---|---|---|
| HIST-22-TEST | governance-runtime/test_exp_m_deterministic.py | 1e954c7c584c01086456af6434cde05e3336df63 | 09c7e1499e9434236207a50c72ee096143eaff5d22de6faf45e78311daec41bd | 22 test methods in original deterministic suite | SUPERSEDED_FALSE_GREEN |
| HIST-29-MUTATION | experiments/governed-platform/EXP-M-MUTATION-RESULTS.json | 1e954c7c584c01086456af6434cde05e3336df63 | 5542cb5a389a47d229b1898681a24e6f85dacfb8394d3f13b9ccfc9f7d7ee9c4 | 29/29 mutations reported rejected | SUPERSEDED_FALSE_GREEN |
| R1-34-TEST | governance-runtime/test_exp_m_deterministic.py | 66129025f9b5211a551f191c4367713e78ef14c4 | c65d39b2768513191bb48d8441c157707fcc5d5777473b6d5149644fee0d82ca | 34 test methods in R1 remediation suite | SUPERSEDED_BY_R1_CHANGES_REQUIRED |
| R1-46-MUTATION | experiments/governed-platform/EXP-M-MUTATION-RESULTS.json | 66129025f9b5211a551f191c4367713e78ef14c4 | 51777eace12acd5034b6764c8ab513da536de306ed30f342fd8c382a5ae5967d | 46/46 mutations reported rejected | SUPERSEDED_BY_R1_CHANGES_REQUIRED |
| R1-REVIEW | experiments/governed-platform/EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R1.md | 8e23ba2b9359c1f3040b6260e23c91b46309cf2e | 9e03fe8b83c120db9627310c8b3ecbb80fb5bfad54e89be7a0a5a011acce23db | Independent R1 implementation review | CHANGES_REQUIRED |
| R2-REVIEW | experiments/governed-platform/EXP-M-R2-EXTERNAL-REVIEW.md | f0df30118d37b5bcbbdd5cb61380b7e3c7c429f1 | f128f76d37226c84dc321475b7fe2db65c64b5f35d68143163fafb9e1aee4b58 | Independent R2 review | CHANGES_REQUIRED |
| R2E-EXTERNAL-REVIEW-R2 | experiments/governed-platform/EXP-M-R2E-EXTERNAL-REVIEW-R2.md | acbcfded67bd34530ede467a8d7432fbc04d3825 | 4e29137de0c123b188eb43c79d09feb2a16ff0f5ce3b0ba8212c8a827a938ff9 | Independent R2E external review identifying seven remaining findings | CHANGES_REQUIRED |
| R2E-STATIC-REVIEW-R1 | experiments/governed-platform/EXP-M-R2E-EXTERNAL-STATIC-REVIEW-R1.md | 2d01e38a5e7b2bb3e181cc3fdd7b46d7bf261bd6 | bc817b2004ffbb232f46642562011f2a6a4ece930b0a4e8e8f17b571686722fa | Independent R2E static review after first clarified handoff | CLARIFICATIONS_REQUIRED |
| R2A-REMEDIATION | experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2A-REMEDIATION.md | e40fa99043cfba081b71e430e4e981c410314bf8 | 875f2d25aa20ec65fc36b2d561b11e882b7773c9c2d73ab1896ae33b720da340 | R2A internal remediation/adjudication record | SUPERSEDED_INTERNAL_EVIDENCE |
| R2B-REMEDIATION | experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2B-REMEDIATION.md | 0bb7bc6bcde7d36c89fd017b6d05d0c99529108b | e8e5e041499186bcb7a03b76b40b9ea56a29240556974b65e3175c1135041b33 | R2B internal remediation/adjudication record | SUPERSEDED_INTERNAL_EVIDENCE |
| R2C-REMEDIATION | experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2C-REMEDIATION.md | b873291ee6ecb982c2fac213ab819c89f34e7890 | 88f9e95070852e7f87da6cf2ed359a950418d0c541a98bc62220d32b1f9a6af7 | R2C internal remediation/adjudication record | SUPERSEDED_INTERNAL_EVIDENCE |

All hashes are recomputed from the pinned Git object by governance-runtime/build_prior_evidence_index.py.

Authority effect: NONE.

## Frozen R5 protocol

~~~json
{
  "protocol_id": "R5-CP-1",
  "protocol_version": "2",
  "confidence_level": 0.95,
  "lower_bound_threshold": 0.99,
  "n_min": 299,
  "success_requirement": "ZERO_FIRST_ATTEMPT_FAILURES",
  "retry_policy": "NO_RETRY_OR_REPLACEMENT",
  "schedule_requirements": {
    "min_distinct_days": 3,
    "min_distinct_time_blocks": 4,
    "require_exact_plan_coverage": true,
    "assignment_rule": "ROUND_ROBIN_DECLARED_ORDER"
  },
  "distribution_requirements": {
    "day_assignment": "attempt_index_mod_scheduled_days",
    "time_block_assignment": "attempt_index_mod_scheduled_time_blocks",
    "exact_match_required": true
  },
  "authority_status": "PREREGISTERED_OFFLINE_ONLY",
  "live_provider_execution_authorized": false
}
~~~

## Authority root

~~~json
{
  "root_id": "EXP-M-R2E-AUTHORITY-ROOT-3",
  "algorithm": "RSA-PKCS1v15-SHA256",
  "public_exponent": 65537,
  "public_modulus_decimal": "19406969437044342697006292572534246890649549718354567902768001038286874304304682288020677530606005820054444675079471098425907485198331095391772392801025164916645300473325780772218648947160031840197498040865742698933283040385481975892632796869861298660466727128777265850590008210570317565352170761177301191402556845217267656166718395054603786870476147220744764007503464619233599989818010247587677328630583301117929218359939034728678769665015656442490751063943627454538116262981266197813114553648863497431294732647080288693673751776261338545078532466863274953590622425413421850328414913402167268030046439645802938513031",
  "test_expectation_manifest_path": "experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.json",
  "test_expectation_manifest_sha256": "f0b7e5dc95a749242ddc0bdf2426789c97c47f7526d426f8cd0973e4580ae543",
  "test_expectation_signature_path": "experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.sig",
  "r5_protocol_path": "experiments/governed-platform/EXP-M-R5-QUALIFICATION-PROTOCOL.json",
  "r5_protocol_sha256": "bf57312019d11529553ab4abdf7586e44ca29cf9c4da02c744f4a65b4fb84876",
  "authority_private_key_committed": false,
  "live_provider_execution_authorized": false,
  "reviewed_commit_anchor": "2814499a37912ea252b759c530fc07bdcef4950c",
  "retrieval_source_ledger_path": "experiments/governed-platform/EXP-M-R2E-RETRIEVAL-SOURCE-LEDGER.json",
  "retrieval_source_ledger_sha256": "61599e9c5fb9975a58799f7e67a50646f9da8b1d7da0f67d87f85ac5b4c5238c",
  "qualification_ledger_path": "experiments/governed-platform/EXP-M-R2E-QUALIFICATION-LEDGER.json",
  "qualification_ledger_sha256": "73995967363087854175c049ba351fdd2b9ebaaa612789702a1c97241a568c6e",
  "version": "3",
  "reviewed_commit_anchor_semantics": "LEGACY_SIGNED_EXPECTATION_SENTINEL_ONLY",
  "current_source_identity_policy": {
    "policy_id": "CURRENT-SOURCE-FREEZE-V1",
    "source_freeze_path": "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json",
    "semantics": "The preregistered root authorizes the deterministic derivation rule. The source-freeze artifact supplies immutable S identity and derived binding evidence only; it is not an authority source."
  },
  "delivery_binding_policy": {
    "policy_id": "SOURCE-FREEZE-DELIVERY-DERIVATION-V1",
    "request_id": "r",
    "items": {
      "a": {
        "sha256": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
        "size": 1
      }
    },
    "derivation": "manifest_hash = SHA256(canonical_json({request_id, reviewed_commit: S, items}))",
    "source_identity": "current_source_identity_policy",
    "authority_semantics": "Authoritative rule is frozen in this root. EXP-M-SOURCE-FREEZE.json may record only the derived current-S binding and cannot alter request_id, item set, item hashes/sizes, or derivation."
  },
  "reviewer_anchor_semantics": "Reviewer suites are preregistered in separate immutable Git commits after this authority root is frozen and before candidate S; the root does not point back to those suites, avoiding circular trust.",
  "authority_bootstrap_semantics": "Candidate S must use an independently preregistered reviewer-authority suite whose literal EXPECTED_AUTHORITY_ROOT_COMMIT equals this root commit. Candidate-local redirection of the authority commit is non-authoritative."
}
~~~

## Evidence artifact hashes

- experiments/governed-platform/EXP-M-SOURCE-FREEZE.json — fecd65b30aa0a7e214ec4330b4f1c566e9cb73d963455dcc827aaf7744c9ffb5
- experiments/governed-platform/EXP-M-TEST-RESULTS.json — 07b9f469ce5c81ac3ca746976c5c894849ee67285ceccc14b2a0469ed0c6006c
- experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json — 6ff0e0d9dd711b3e3babbe772386aab2f77d2e8b6fe01a3b994055ae177b6c1c
- experiments/governed-platform/EXP-M-MUTATION-RESULTS.json — 207e9d48de04d581ea32ff1d9ef74d18193973c0b7cd44a826568ba886e059e1
- experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json — 67cfee563d21f4cfb46be8df23a2f03d8b59bb2c77e779d745c7b0c6adf60b3b
- experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json — 1084c5435a36d588767b44048c52d1cf6c6f7b81240d7e6810085272ffc3e798
- experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json — 003dbdce34e96972995486f9aa8d170c00f80cd62f9a7c17f959d157c0bfc0f9
- experiments/governed-platform/EXP-M-R2D-SELF-ADJUDICATION.json — e4399b5edcc04ef0c1d37412d7d8c0bcb0f266adea383618509520004d1f6b8e
- experiments/governed-platform/EXP-M-R2E-SOURCE-FREEZE-STDOUT.txt — 5491f366e314fc836519bed69d71bd3f6dd84c6c45e30024c86bde508f2cb744
- experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt — 02ba6886f321cc645260ad6418c6fa7d8045b24bc9ba04a8d8a7eca9a35991bc
- experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt — bdef7910650cd4c7497376808382b84fe3ed523c1f016bc4dcbb40d347fa9bf5
- experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt — eaa0a91c7bab153468c028eeaa81d8c6b58a0656bde726034fa78b660e6913fa
- experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt — 6475190f19e8dc3efb804ce21546ebd8776dc8cbdd44a9f2b127557ecc4afba5
- experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt — 291abaa112399fc42182536f87b61e48406c652cf624b70a73b6d09a911e5704
- experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt — 52945e923b7e57b5590659a67bf7bc4af8c0a9f6251cf9f3c76459736adf8376
- experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt — 4b7fd9aaae8abc37c2b3b0b02f89fd6a70710877e1c2ab3f8fb11ce1f29558d2
- experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt — f5207ce3355ecb24b90e1c643bdbdfb9a04f10622f7a0ebf9cf1448582b8091a
- experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt — 141ab088dffea96f729bdb4c070aaa79eba575257aa13299eb07efe167dd5960
- experiments/governed-platform/EXP-M-R2E-SELF-ADJUDICATION-STDOUT.txt — 366bb56b31f26d18d347ec61550e3a0b7ef06404406fc06a946381d7f8e62228

## External-review scope

Treat all self-reported PASS values as claims. Attack the authority/source/evidence boundaries, verify S->E->P changed-path restrictions, verify prior-failure preservation, and independently confirm CA-1..CA-10.

A PASS here cannot qualify EXP-M and cannot authorize live provider/API execution.
