# EXP-M Deterministic Implementation R2E — Independent Review Handoff

## Exact S -> E -> P identity

- S: 63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a
- S tree: 596c9bec58cd40f8ac27999f26ea62b6a2cc109d
- E: ae0fd712b1a8a1a703898bf361ff071d9b7edabb
- E tree: c53218da9954d795ae0799a6fceac3a395ebaed4
- P: 2e166e75a56c53d3947b5487e5ac274e8c190c06
- P tree: 8d1e7397713b1215d7301f3cb2da5424132e570e

The current handoff commit is a docs-only post-P identity attestation. P is the immutable packet-content commit; this avoids the impossible requirement for a Git commit to contain its own SHA.

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

- S source commit: 63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a
- S source tree: 596c9bec58cd40f8ac27999f26ea62b6a2cc109d
- E evidence commit: ae0fd712b1a8a1a703898bf361ff071d9b7edabb
- E evidence tree: c53218da9954d795ae0799a6fceac3a395ebaed4
- Evidence manifest SHA-256 at E: 9ba72fde64baf3c5d85abb6f25399e1b0004d42017c37fbdcdbec0a7e8ba3a28
- Evidence manifest Git blob at E: f440462fd69e47b22fd1655da4d0247cf3080a3c
- P packet-content commit: established by the first commit containing this file; the exact P SHA is reported in the post-P handoff document to avoid Git commit-hash self-reference.

## S -> E changed paths

~~~text
experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json
experiments/governed-platform/EXP-M-MUTATION-RESULTS.json
experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json
experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json
experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json
experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt
experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json
experiments/governed-platform/EXP-M-SOURCE-FREEZE.json
experiments/governed-platform/EXP-M-TEST-RESULTS.json
~~~

## Fresh evidence summary

- Core tests: 56/56 with all_passed=True
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
      "failure": null,
      "id": "CA-1",
      "rejected": true,
      "rejection_reason": "expectation_authority_invalid",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca1_self_consistent_context_plus_forged_complete_receipt"
    },
    {
      "failure": null,
      "id": "CA-2",
      "rejected": true,
      "rejection_reason": "evidence_token_mismatch",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca2_correctly_keyed_token_for_different_bundle"
    },
    {
      "failure": null,
      "id": "CA-3",
      "rejected": true,
      "rejection_reason": "authority_reviewed_commit_mismatch",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca3_fabricated_manifest_plus_matching_caller_commit"
    },
    {
      "failure": null,
      "id": "CA-4",
      "rejected": true,
      "rejection_reason": "retrieval_and_delivery_binding_rejected",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca4_fabricated_retrieval_bytes_plus_forged_receipt"
    },
    {
      "failure": null,
      "id": "CA-5",
      "rejected": true,
      "rejection_reason": "archive_and_schedule_attack_rejected",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca5_zip_named_bin_plus_fake_schedule_diversity"
    },
    {
      "failure": null,
      "id": "CA-6",
      "rejected": true,
      "rejection_reason": "qualification_authority_plan_missing",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca6_authority_plan_absent_but_caller_plan_self_consistent"
    },
    {
      "failure": null,
      "id": "CA-7",
      "rejected": true,
      "rejection_reason": "indexed_prior_artifact_missing",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca7_prior_artifact_deleted_but_index_unchanged"
    },
    {
      "failure": null,
      "id": "CA-8",
      "rejected": true,
      "rejection_reason": "reviewer_suite_hash_drift",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca8_reviewer_suite_modified_after_source_freeze"
    },
    {
      "failure": null,
      "guard_semantics": "FALSE means failed predicates derive CHANGES_REQUIRED; a caller-supplied PASS cannot override that derived disposition.",
      "id": "CA-9",
      "rejected": true,
      "rejection_reason": "disposition_promotable",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca9_caller_pass_with_failed_predicate"
    },
    {
      "failure": null,
      "fault_injection": "AuthorityHandle.with_missing_r5_protocol_for_test() sets protocol_available=False for this negative test only; the frozen R5 protocol remains present in the authority root.",
      "id": "CA-10",
      "rejected": true,
      "rejection_reason": "r5_protocol_unavailable",
      "rejection_reason_semantics": "blocking guard/control label; not a positive-status assertion",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca10_missing_protocol_with_self_consistent_record"
    }
  ],
  "execution": {
    "command": "python governance-runtime/run_reviewer_compound_attacks.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a",
    "source_tree": "596c9bec58cd40f8ac27999f26ea62b6a2cc109d",
    "utc": "2026-09-22T06:33:39.938058+00:00"
  },
  "exp_m_state": "NOT_QUALIFIED",
  "live_provider_api_execution": false,
  "schema": "EXP-M-R2E-COMPOUND/v1",
  "survivor_count": 0,
  "survivors": []
}
~~~

## Source freeze

~~~json
{
  "authority_effect": "NONE",
  "delivery_authority": {
    "requests": {
      "r": {
        "manifest_hash": "d78b4d92914062aa249e4e99684cd265e7cd2db9f09d496bd3ce27b02d86fe53",
        "reviewed_commit": "63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a"
      }
    }
  },
  "exp_m_state": "NOT_QUALIFIED",
  "live_provider_api_execution": false,
  "schema": "EXP-M-SOURCE-FREEZE/v1",
  "source_commit": "63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a",
  "source_files": {
    ".github/workflows/exp-m-r2e-offline.yml": "61c95474063332e9d49a08686748a4218cff5a3b1885090671960496c48422c9",
    ".github/workflows/exp-m-r2e-sep.yml": "dd27d845df12b789e933bce66a19707ab29dc707d55aadd4634038e0b7dd3845",
    "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-ADJUDICATION.md": "de65f8aff326e3b1e660c1707086c6b0695e08749a16a8e0de6023b3863d8f1b",
    "experiments/governed-platform/PRIOR-EVIDENCE-INDEX.md": "f6d661614626c9107185fdc12e0cf0af175dee991fe7eda12ed86490742fbee5",
    "governance-runtime/build_exp_m_portable_review_bundle.py": "5adec7a84edb4db7b902887e2909c1d93e64dedd9f46453c17ed9a617de680f5",
    "governance-runtime/build_exp_m_r2e_packet.py": "f647cdba79b78e3e4ec8d0cb08a2e6a0f598c449743999e067ef300d3e2743d5",
    "governance-runtime/build_exp_m_review_packet.py": "c2861f61278d0c529a5719e588e9022f73d35ff31c7c6a20a9b381ed4aa8bc0a",
    "governance-runtime/build_prior_evidence_index.py": "bc777ea30960991e0247f8ed58aef749bce94b751bc329c042cc2a3a2fb812b0",
    "governance-runtime/exp_m_deterministic.py": "238d4c38271aec8fb9c67e7a5b9226dd8a213a1f58bc2eab4c59d7e701b52dff",
    "governance-runtime/exp_m_expectation_authority.py": "01b67779e7af945eb6f6d276952dd0e0099dc758beb1a964a72a7352166dacba",
    "governance-runtime/exp_m_mutation_catalog.py": "5c9da2dad5f36451075e1847c368eae031e4ff8f08baa3ca938f3eaa57bff08d",
    "governance-runtime/exp_m_predicate_registry.py": "357dcfc7241e5cb0ff1e3a051be3826f4c95a48af922bb2fdce60dc47321d255",
    "governance-runtime/exp_m_review_fixtures.py": "91f02d0cd05902cfa2c47e6a3d2bc12522438a46fcf3963cc774c21ae9b6f3a4",
    "governance-runtime/exp_m_test_fixtures.py": "4d3cabb858481dc7e39c523b7b353740011e87c2c4b81c42a7686d357b488832",
    "governance-runtime/freeze_source.py": "89eb46914ac2e267117b95c98b1e03dce4f18fa796118ab8d5c6cda1f4dfc344",
    "governance-runtime/generate_evidence.py": "ce3671befbc2cafaaf7b05d1bfdef0ca7427ba1f6eda342b5a33be8f3aabba5c",
    "governance-runtime/reviewer_exp_m_r2e_authority_suite.py": "5a390122252a702a54aefa12794883f1ccadb15b07116d9a3759675f55bd86de",
    "governance-runtime/reviewer_exp_m_r2e_compound_suite.py": "4d4668db91efc73ce5327c49c22cdeb2d9e62e10ae5509eec14dfead454b4329",
    "governance-runtime/reviewer_exp_m_r2e_suite.py": "f5164eec5e795b9ef927f65b8a0261a8736dab2e10c86a3a6a868cde0055dd96",
    "governance-runtime/run_exp_m_deterministic.py": "8d8f028cc466c28a587cfbbb9a813b708c2a48a541bd8ca1fa7a6484a4880583",
    "governance-runtime/run_exp_m_mutations.py": "be705ba0749bc9df7fd4d1a3c26afbb81b060f0c4a8bb1933a3f036a95d257fb",
    "governance-runtime/run_exp_m_static_review_probes.py": "c0bcff168444405d1f3fc26e82ae0075770ffbd58477306f5bfea117e4734f77",
    "governance-runtime/run_exp_m_tests.py": "f6d5e35c401ce7393f23de5c5cd0f583c655ea8403575c968f2d664e3a9fb11c",
    "governance-runtime/run_reviewer_compound_attacks.py": "5aab77b66393b7278a3b4ec662eee5eaafb021f14ca1ed4bef3dff88e12ecbf3",
    "governance-runtime/self_adjudicate_r2d.py": "e320addbc158cdf2d94959476ca2928d8d9ccdf9a8b1bc070b243f6d38336d20",
    "governance-runtime/self_falsify_exp_m.py": "4076873139f4da13ff6a0b15998081d487feff601fc77c3228f5754276c02436",
    "governance-runtime/test_exp_m_deterministic.py": "c484e6e29e304019330c28e761ac971c5b52f2fb427c6ac1495a7b3ab83ba089",
    "governance-runtime/test_exp_m_phases.py": "7db4f55d3aaac806f908338da7abbdade85c5ce354ce1204e3fceafefccc12fa",
    "governance-runtime/verify_exp_m_prior_evidence.py": "ef3a4d48e78cba27dcc323424ca04f0b2c02f2389fb58204a3d7f294fb719388",
    "governance-runtime/verify_exp_m_sep_sequence.py": "9c86bb2113eb82b51aa1da6e5fd83b21260827b553ead76191f2c9cb1aeb3485",
    "governance-runtime/verify_sep_sequence.py": "24928ca87f9dccac33ae7262e0a95cd8a1096e2f9a8d1512e0205dcf0f65289b"
  },
  "source_tree": "596c9bec58cd40f8ac27999f26ea62b6a2cc109d"
}
~~~

## Evidence manifest

The evidence manifest intentionally does not list itself as an artifact because that would create self-hash recursion. The immutable P packet independently attests the exact manifest bytes stored at E.

~~~json
{
  "artifacts": [
    {
      "path": "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json",
      "sha256": "373c94bcb76da5a696d48db4ac5407f38a92ea2a9f8fa7bdc853cc310bfdd17a",
      "size": 4303
    },
    {
      "path": "experiments/governed-platform/EXP-M-TEST-RESULTS.json",
      "sha256": "70f0da81e90edd490e83b42f39c71bee9e886de262b2961a3c563d27d2cf6423",
      "size": 8310
    },
    {
      "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json",
      "sha256": "a6642be71a7be52feab6e2f6e0979cb486cef9fb2d6498b923d5b55fa080d278",
      "size": 30495
    },
    {
      "path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
      "sha256": "971153a6059b2051957270ad60ac6027e1218c03ccba21c92aa0efde724115eb",
      "size": 32290
    },
    {
      "path": "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json",
      "sha256": "7ab2c53cccb080b6cd8d1d2bd8b3391d295986d773b688c2af8a6ad6b7c98e8f",
      "size": 6450
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json",
      "sha256": "4decf4dabe11f2ea69d849c1d82a6451c8cb21ea0c5ce90f84997c546d10032f",
      "size": 4615
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json",
      "sha256": "b25ddd5c4da4f0f09556ffbcca645fce8664640cd692286a825a916773be7a5f",
      "size": 3015
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt",
      "sha256": "4655fb93a5b5b0105ff370eb8b00f0b90913fc448c7f8e7dc630d037883c12c7",
      "size": 26
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt",
      "sha256": "70f0da81e90edd490e83b42f39c71bee9e886de262b2961a3c563d27d2cf6423",
      "size": 8310
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt",
      "sha256": "6ec2d9fc5c4105ec484f0358d72e64a04635a03395757bb37014a816383eb11b",
      "size": 1347
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt",
      "sha256": "373634e95ed7ae361ffa5f1c20c0b725de483daea7f10dcd0fc2f9cafa5712f7",
      "size": 1218
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt",
      "sha256": "7d33ff8085d210485d046cf0e11a852e0620870ba689813fec1c64afd1972963",
      "size": 6434
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt",
      "sha256": "b25ddd5c4da4f0f09556ffbcca645fce8664640cd692286a825a916773be7a5f",
      "size": 3015
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt",
      "sha256": "a6642be71a7be52feab6e2f6e0979cb486cef9fb2d6498b923d5b55fa080d278",
      "size": 30495
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt",
      "sha256": "971153a6059b2051957270ad60ac6027e1218c03ccba21c92aa0efde724115eb",
      "size": 32290
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt",
      "sha256": "728319ba900a411bcf8932860c4f820e01c98c601881f4715c0dd4279ba0691f",
      "size": 4479
    }
  ],
  "authority_effect": "NONE",
  "commands": [
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/verify_exp_m_prior_evidence.py",
      "exit_code": 0,
      "name": "prior-evidence",
      "portable_command": "python governance-runtime/verify_exp_m_prior_evidence.py",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt",
      "stdout_role": "command_console_capture",
      "stdout_sha256": "4655fb93a5b5b0105ff370eb8b00f0b90913fc448c7f8e7dc630d037883c12c7"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_tests.py",
      "exit_code": 0,
      "name": "tests",
      "portable_command": "python governance-runtime/run_exp_m_tests.py",
      "result_path": "experiments/governed-platform/EXP-M-TEST-RESULTS.json",
      "stdout_identical_to_result": true,
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt",
      "stdout_role": "duplicate_serialization_of_result_json; retained as command-console capture, not independent evidence",
      "stdout_sha256": "70f0da81e90edd490e83b42f39c71bee9e886de262b2961a3c563d27d2cf6423"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/reviewer_exp_m_r2e_suite.py",
      "exit_code": 0,
      "name": "reviewer-core",
      "portable_command": "python governance-runtime/reviewer_exp_m_r2e_suite.py",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt",
      "stdout_role": "command_console_capture",
      "stdout_sha256": "6ec2d9fc5c4105ec484f0358d72e64a04635a03395757bb37014a816383eb11b"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
      "exit_code": 0,
      "name": "reviewer-authority",
      "portable_command": "python governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt",
      "stdout_role": "command_console_capture",
      "stdout_sha256": "373634e95ed7ae361ffa5f1c20c0b725de483daea7f10dcd0fc2f9cafa5712f7"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_reviewer_compound_attacks.py",
      "exit_code": 0,
      "name": "reviewer-compound",
      "portable_command": "python governance-runtime/run_reviewer_compound_attacks.py",
      "result_path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json",
      "stdout_identical_to_result": false,
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt",
      "stdout_role": "command_console_capture",
      "stdout_sha256": "7d33ff8085d210485d046cf0e11a852e0620870ba689813fec1c64afd1972963"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_static_review_probes.py",
      "exit_code": 0,
      "name": "static-review-probes",
      "portable_command": "python governance-runtime/run_exp_m_static_review_probes.py",
      "result_path": "experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json",
      "stdout_identical_to_result": true,
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt",
      "stdout_role": "duplicate_serialization_of_result_json; retained as command-console capture, not independent evidence",
      "stdout_sha256": "b25ddd5c4da4f0f09556ffbcca645fce8664640cd692286a825a916773be7a5f"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_deterministic.py",
      "exit_code": 0,
      "name": "phases",
      "portable_command": "python governance-runtime/run_exp_m_deterministic.py",
      "result_path": "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json",
      "stdout_identical_to_result": true,
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt",
      "stdout_role": "duplicate_serialization_of_result_json; retained as command-console capture, not independent evidence",
      "stdout_sha256": "a6642be71a7be52feab6e2f6e0979cb486cef9fb2d6498b923d5b55fa080d278"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_mutations.py",
      "exit_code": 0,
      "name": "mutations",
      "portable_command": "python governance-runtime/run_exp_m_mutations.py",
      "result_path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
      "stdout_identical_to_result": true,
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt",
      "stdout_role": "duplicate_serialization_of_result_json; retained as command-console capture, not independent evidence",
      "stdout_sha256": "971153a6059b2051957270ad60ac6027e1218c03ccba21c92aa0efde724115eb"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/self_falsify_exp_m.py",
      "exit_code": 0,
      "name": "self-falsification",
      "portable_command": "python governance-runtime/self_falsify_exp_m.py",
      "result_path": "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json",
      "stdout_identical_to_result": true,
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt",
      "stdout_role": "duplicate_serialization_of_result_json; retained as command-console capture, not independent evidence",
      "stdout_sha256": "728319ba900a411bcf8932860c4f820e01c98c601881f4715c0dd4279ba0691f"
    }
  ],
  "compound_attack_survivors": 0,
  "exp_m_state": "NOT_QUALIFIED",
  "generated_at_utc": "2026-09-22T06:35:41.234919+00:00",
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
    "third_party_python_dependencies": []
  },
  "schema": "EXP-M-R2E-EVIDENCE-MANIFEST/v2",
  "source_commit": "63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a",
  "source_tree": "596c9bec58cd40f8ac27999f26ea62b6a2cc109d"
}
~~~

## Evidence manifest post-generation attestation

~~~json
{
  "attestation_stage": "P",
  "git_blob": "f440462fd69e47b22fd1655da4d0247cf3080a3c",
  "path": "experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json",
  "reason_not_self_listed": "The manifest cannot safely contain its own final cryptographic hash without self-reference. P independently attests the exact manifest bytes stored at E.",
  "sha256": "9ba72fde64baf3c5d85abb6f25399e1b0004d42017c37fbdcdbec0a7e8ba3a28",
  "size": 10719
}
~~~

## Static-review clarification probes

~~~json
{
  "authority_effect": "NONE",
  "execution": {
    "command": "python governance-runtime/run_exp_m_static_review_probes.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a",
    "source_tree": "596c9bec58cd40f8ac27999f26ea62b6a2cc109d",
    "utc": "2026-09-22T06:33:40.241334+00:00"
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
- Each command record now carries stdout_role.
- Where hashes and sizes match the corresponding JSON result, the manifest sets stdout_identical_to_result=true and labels STDOUT as duplicate_serialization_of_result_json.
- The packet explicitly states that such STDOUT is command-console capture, not independent evidence.

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
- Duplicate JSON/STDOUT hashes are expected when a runner prints the same serialized JSON it writes to its result file. Such STDOUT is retained as command-console capture and is explicitly not independent evidence; the manifest records this relationship.
- Authority inputs are not generated E artifacts. They are pinned by the preregistered authority commit used by source S and are embedded below with recomputed hashes and Git blob identities for static inspection.
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
  "third_party_python_dependencies": []
}
~~~

Exact re-execution sequence from a repository clone:

~~~text
git fetch --all --tags --prune
git checkout --detach 63b9f08998db0dce0a3ee2fbd46bf80fa4f6852a
git status --porcelain
python governance-runtime/verify_exp_m_prior_evidence.py
python governance-runtime/run_exp_m_tests.py
python governance-runtime/reviewer_exp_m_r2e_suite.py
python governance-runtime/reviewer_exp_m_r2e_authority_suite.py
python governance-runtime/run_reviewer_compound_attacks.py
python governance-runtime/run_exp_m_static_review_probes.py
python governance-runtime/run_exp_m_deterministic.py
python governance-runtime/run_exp_m_mutations.py
python governance-runtime/self_falsify_exp_m.py
~~~

## Portable static-review bundle

After Q is created and final S-E-P verification succeeds, the governed workflow builds and uploads EXP-M-R2E-PORTABLE-REVIEW-BUNDLE.zip. The ZIP contains the frozen source files from S, all E evidence artifacts plus the manifest, P packet content, Q handoff, pinned authority inputs/backing source, and each prior-history artifact named by the prior-evidence index. Its internal BUNDLE-MANIFEST.json records SHA-256, size, Git blob, origin commit, and origin path for each included repository object. The ZIP is review convenience only and grants no authority.

## Pinned authority input bundle

~~~json
{
  "authority_commit": "e24e18a0f05e9be38e4f549a77914e014c738812",
  "authority_tree": "daff689e55a4bab3f5782dce850de0e497d0d926",
  "files": [
    {
      "content": "{\n  \"root_id\": \"EXP-M-R2E-AUTHORITY-ROOT-1\",\n  \"algorithm\": \"RSA-PKCS1v15-SHA256\",\n  \"public_exponent\": 65537,\n  \"public_modulus_decimal\": \"19406969437044342697006292572534246890649549718354567902768001038286874304304682288020677530606005820054444675079471098425907485198331095391772392801025164916645300473325780772218648947160031840197498040865742698933283040385481975892632796869861298660466727128777265850590008210570317565352170761177301191402556845217267656166718395054603786870476147220744764007503464619233599989818010247587677328630583301117929218359939034728678769665015656442490751063943627454538116262981266197813114553648863497431294732647080288693673751776261338545078532466863274953590622425413421850328414913402167268030046439645802938513031\",\n  \"test_expectation_manifest_path\": \"experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.json\",\n  \"test_expectation_manifest_sha256\": \"f0b7e5dc95a749242ddc0bdf2426789c97c47f7526d426f8cd0973e4580ae543\",\n  \"test_expectation_signature_path\": \"experiments/governed-platform/EXP-M-R2E-TEST-EXPECTATIONS.sig\",\n  \"r5_protocol_path\": \"experiments/governed-platform/EXP-M-R5-QUALIFICATION-PROTOCOL.json\",\n  \"r5_protocol_sha256\": \"bf57312019d11529553ab4abdf7586e44ca29cf9c4da02c744f4a65b4fb84876\",\n  \"authority_private_key_committed\": false,\n  \"live_provider_execution_authorized\": false,\n  \"reviewer_suite_path\": \"governance-runtime/reviewer_exp_m_r2e_suite.py\",\n  \"reviewer_suite_preregister_commit\": \"04913502b7ea1dcb11d551b2bec27c5a8d9c4a8a\",\n  \"reviewed_commit_anchor\": \"2814499a37912ea252b759c530fc07bdcef4950c\",\n  \"retrieval_source_ledger_path\": \"experiments/governed-platform/EXP-M-R2E-RETRIEVAL-SOURCE-LEDGER.json\",\n  \"retrieval_source_ledger_sha256\": \"61599e9c5fb9975a58799f7e67a50646f9da8b1d7da0f67d87f85ac5b4c5238c\",\n  \"delivery_ledger_path\": \"experiments/governed-platform/EXP-M-R2E-DELIVERY-LEDGER.json\",\n  \"delivery_ledger_sha256\": \"1cccb652bf6a77d33ae97e81846031b2cff2a40a383f9530c4a425a93d9dc45a\",\n  \"qualification_ledger_path\": \"experiments/governed-platform/EXP-M-R2E-QUALIFICATION-LEDGER.json\",\n  \"qualification_ledger_sha256\": \"73995967363087854175c049ba351fdd2b9ebaaa612789702a1c97241a568c6e\",\n  \"reviewer_authority_suite_path\": \"governance-runtime/reviewer_exp_m_r2e_authority_suite.py\",\n  \"reviewer_authority_suite_preregister_commit\": \"a7b5e5ac59a3da745a6ac06d828763be59ab9668\"\n}\n",
      "declared_sha256": null,
      "git_blob": "0b2c7397a1732c45b4c704ae864effe224bd1632",
      "label": "authority_root",
      "path": "experiments/governed-platform/EXP-M-R2E-AUTHORITY-ROOT.json",
      "sha256": "f6fa3e11e580d580f7d7d3069e0e7bfc66116f1a3c89579e33cea1577953a2e4"
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
      "content": "{\n  \"requests\": {\n    \"r\": {\n      \"manifest_hash\": \"d2050c596c0d4d33058c0003cf11ab2fff297b9d12e49ed5f80becd657b9d873\",\n      \"reviewed_commit\": \"2814499a37912ea252b759c530fc07bdcef4950c\"\n    }\n  },\n  \"version\": \"1\"\n}\n",
      "declared_sha256": "1cccb652bf6a77d33ae97e81846031b2cff2a40a383f9530c4a425a93d9dc45a",
      "git_blob": "ba65aa159e972140a86be783c130a07c173938e2",
      "label": "delivery_ledger",
      "path": "experiments/governed-platform/EXP-M-R2E-DELIVERY-LEDGER.json",
      "sha256": "1cccb652bf6a77d33ae97e81846031b2cff2a40a383f9530c4a425a93d9dc45a"
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
  "root_sha256": "f6fa3e11e580d580f7d7d3069e0e7bfc66116f1a3c89579e33cea1577953a2e4"
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
  "root_id": "EXP-M-R2E-AUTHORITY-ROOT-1",
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
  "reviewer_suite_path": "governance-runtime/reviewer_exp_m_r2e_suite.py",
  "reviewer_suite_preregister_commit": "04913502b7ea1dcb11d551b2bec27c5a8d9c4a8a",
  "reviewed_commit_anchor": "2814499a37912ea252b759c530fc07bdcef4950c",
  "retrieval_source_ledger_path": "experiments/governed-platform/EXP-M-R2E-RETRIEVAL-SOURCE-LEDGER.json",
  "retrieval_source_ledger_sha256": "61599e9c5fb9975a58799f7e67a50646f9da8b1d7da0f67d87f85ac5b4c5238c",
  "delivery_ledger_path": "experiments/governed-platform/EXP-M-R2E-DELIVERY-LEDGER.json",
  "delivery_ledger_sha256": "1cccb652bf6a77d33ae97e81846031b2cff2a40a383f9530c4a425a93d9dc45a",
  "qualification_ledger_path": "experiments/governed-platform/EXP-M-R2E-QUALIFICATION-LEDGER.json",
  "qualification_ledger_sha256": "73995967363087854175c049ba351fdd2b9ebaaa612789702a1c97241a568c6e",
  "reviewer_authority_suite_path": "governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
  "reviewer_authority_suite_preregister_commit": "a7b5e5ac59a3da745a6ac06d828763be59ab9668"
}
~~~

## Evidence artifact hashes

- experiments/governed-platform/EXP-M-SOURCE-FREEZE.json — 373c94bcb76da5a696d48db4ac5407f38a92ea2a9f8fa7bdc853cc310bfdd17a
- experiments/governed-platform/EXP-M-TEST-RESULTS.json — 70f0da81e90edd490e83b42f39c71bee9e886de262b2961a3c563d27d2cf6423
- experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json — a6642be71a7be52feab6e2f6e0979cb486cef9fb2d6498b923d5b55fa080d278
- experiments/governed-platform/EXP-M-MUTATION-RESULTS.json — 971153a6059b2051957270ad60ac6027e1218c03ccba21c92aa0efde724115eb
- experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json — 7ab2c53cccb080b6cd8d1d2bd8b3391d295986d773b688c2af8a6ad6b7c98e8f
- experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json — 4decf4dabe11f2ea69d849c1d82a6451c8cb21ea0c5ce90f84997c546d10032f
- experiments/governed-platform/EXP-M-R2E-CLARIFICATION-PROBES.json — b25ddd5c4da4f0f09556ffbcca645fce8664640cd692286a825a916773be7a5f
- experiments/governed-platform/EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt — 4655fb93a5b5b0105ff370eb8b00f0b90913fc448c7f8e7dc630d037883c12c7
- experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt — 70f0da81e90edd490e83b42f39c71bee9e886de262b2961a3c563d27d2cf6423
- experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt — 6ec2d9fc5c4105ec484f0358d72e64a04635a03395757bb37014a816383eb11b
- experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt — 373634e95ed7ae361ffa5f1c20c0b725de483daea7f10dcd0fc2f9cafa5712f7
- experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt — 7d33ff8085d210485d046cf0e11a852e0620870ba689813fec1c64afd1972963
- experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt — b25ddd5c4da4f0f09556ffbcca645fce8664640cd692286a825a916773be7a5f
- experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt — a6642be71a7be52feab6e2f6e0979cb486cef9fb2d6498b923d5b55fa080d278
- experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt — 971153a6059b2051957270ad60ac6027e1218c03ccba21c92aa0efde724115eb
- experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt — 728319ba900a411bcf8932860c4f820e01c98c601881f4715c0dd4279ba0691f

## External-review scope

Treat all self-reported PASS values as claims. Attack the authority/source/evidence boundaries, verify S->E->P changed-path restrictions, verify prior-failure preservation, and independently confirm CA-1..CA-10.

A PASS here cannot qualify EXP-M and cannot authorize live provider/API execution.
