# EXP-M Deterministic Implementation R2E — Independent Review Handoff

## Exact S -> E -> P identity

- S: 13f7f17e7c1609de37dc3d1c4bc35a762607ecb5
- S tree: e07fa898c6abbabf667e1e62de45992d75966f18
- E: fbb11970afb74503ce2e572ea1adf9f6dd177a15
- E tree: c7507e41d035ef6168e6a2d067d54ebfc643752d
- P: 623187e5fcf5071fd0e4a97a1ee9aa92e1c688ac
- P tree: 23f1f4d848f7d51beff2c356207e10fc44343055

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

- S source commit: 13f7f17e7c1609de37dc3d1c4bc35a762607ecb5
- S source tree: e07fa898c6abbabf667e1e62de45992d75966f18
- E evidence commit: fbb11970afb74503ce2e572ea1adf9f6dd177a15
- E evidence tree: c7507e41d035ef6168e6a2d067d54ebfc643752d
- P packet-content commit: established by the first commit containing this file; the exact P SHA is reported in the post-P handoff document to avoid Git commit-hash self-reference.

## S -> E changed paths

~~~text
experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json
experiments/governed-platform/EXP-M-MUTATION-RESULTS.json
experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json
experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json
experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt
experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt
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
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca1_self_consistent_context_plus_forged_complete_receipt"
    },
    {
      "failure": null,
      "id": "CA-2",
      "rejected": true,
      "rejection_reason": "evidence_token_mismatch",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca2_correctly_keyed_token_for_different_bundle"
    },
    {
      "failure": null,
      "id": "CA-3",
      "rejected": true,
      "rejection_reason": "authority_reviewed_commit_mismatch",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca3_fabricated_manifest_plus_matching_caller_commit"
    },
    {
      "failure": null,
      "id": "CA-4",
      "rejected": true,
      "rejection_reason": "retrieval_and_delivery_binding_rejected",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca4_fabricated_retrieval_bytes_plus_forged_receipt"
    },
    {
      "failure": null,
      "id": "CA-5",
      "rejected": true,
      "rejection_reason": "archive_and_schedule_attack_rejected",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca5_zip_named_bin_plus_fake_schedule_diversity"
    },
    {
      "failure": null,
      "id": "CA-6",
      "rejected": true,
      "rejection_reason": "qualification_authority_plan_missing",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca6_authority_plan_absent_but_caller_plan_self_consistent"
    },
    {
      "failure": null,
      "id": "CA-7",
      "rejected": true,
      "rejection_reason": "indexed_prior_artifact_missing",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca7_prior_artifact_deleted_but_index_unchanged"
    },
    {
      "failure": null,
      "id": "CA-8",
      "rejected": true,
      "rejection_reason": "reviewer_suite_hash_drift",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca8_reviewer_suite_modified_after_source_freeze"
    },
    {
      "failure": null,
      "id": "CA-9",
      "rejected": true,
      "rejection_reason": "disposition_promotable",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca9_caller_pass_with_failed_predicate"
    },
    {
      "failure": null,
      "id": "CA-10",
      "rejected": true,
      "rejection_reason": "r5_protocol_unavailable",
      "source": "reviewer_exp_m_r2e_compound_suite.py",
      "test": "test_ca10_missing_protocol_with_self_consistent_record"
    }
  ],
  "execution": {
    "command": "python governance-runtime/run_reviewer_compound_attacks.py",
    "interpreter": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python",
    "source_commit": "13f7f17e7c1609de37dc3d1c4bc35a762607ecb5",
    "source_tree": "e07fa898c6abbabf667e1e62de45992d75966f18",
    "utc": "2026-09-20T14:34:37.392213+00:00"
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
        "manifest_hash": "7bf8f210febeadb52bd557e55a3900cdaf0cc4efdb05d81a9c6cbd3edbadd679",
        "reviewed_commit": "13f7f17e7c1609de37dc3d1c4bc35a762607ecb5"
      }
    }
  },
  "exp_m_state": "NOT_QUALIFIED",
  "live_provider_api_execution": false,
  "schema": "EXP-M-SOURCE-FREEZE/v1",
  "source_commit": "13f7f17e7c1609de37dc3d1c4bc35a762607ecb5",
  "source_files": {
    ".github/workflows/exp-m-r2e-offline.yml": "38010e9297c6b864f1594eee9ad707ce58a2289b6db56e52115b867e22c78bac",
    ".github/workflows/exp-m-r2e-sep.yml": "73c11286d19bed1d0d73697d668ddf0729edfbfb58eff1b8eb178240544a2edb",
    "governance-runtime/build_exp_m_r2e_packet.py": "1c8c637b38ecdacfea1f584b4e56fb4a9f1cd016d2febeed437740a8f1947e12",
    "governance-runtime/build_exp_m_review_packet.py": "c2861f61278d0c529a5719e588e9022f73d35ff31c7c6a20a9b381ed4aa8bc0a",
    "governance-runtime/build_prior_evidence_index.py": "bc777ea30960991e0247f8ed58aef749bce94b751bc329c042cc2a3a2fb812b0",
    "governance-runtime/exp_m_deterministic.py": "238d4c38271aec8fb9c67e7a5b9226dd8a213a1f58bc2eab4c59d7e701b52dff",
    "governance-runtime/exp_m_expectation_authority.py": "01b67779e7af945eb6f6d276952dd0e0099dc758beb1a964a72a7352166dacba",
    "governance-runtime/exp_m_mutation_catalog.py": "5c9da2dad5f36451075e1847c368eae031e4ff8f08baa3ca938f3eaa57bff08d",
    "governance-runtime/exp_m_predicate_registry.py": "357dcfc7241e5cb0ff1e3a051be3826f4c95a48af922bb2fdce60dc47321d255",
    "governance-runtime/exp_m_review_fixtures.py": "91f02d0cd05902cfa2c47e6a3d2bc12522438a46fcf3963cc774c21ae9b6f3a4",
    "governance-runtime/exp_m_test_fixtures.py": "4d3cabb858481dc7e39c523b7b353740011e87c2c4b81c42a7686d357b488832",
    "governance-runtime/freeze_source.py": "bb3ed4cb582f0c0a9aace2537407505adbef4b77c610cd9664dab0bbdabdfccf",
    "governance-runtime/generate_evidence.py": "c9b84bc663b2ae3f3c5b584d5a837a9761d585e8683e27c6682cd0f68b2a469f",
    "governance-runtime/reviewer_exp_m_r2e_authority_suite.py": "5a390122252a702a54aefa12794883f1ccadb15b07116d9a3759675f55bd86de",
    "governance-runtime/reviewer_exp_m_r2e_compound_suite.py": "4d4668db91efc73ce5327c49c22cdeb2d9e62e10ae5509eec14dfead454b4329",
    "governance-runtime/reviewer_exp_m_r2e_suite.py": "f5164eec5e795b9ef927f65b8a0261a8736dab2e10c86a3a6a868cde0055dd96",
    "governance-runtime/run_exp_m_deterministic.py": "8d8f028cc466c28a587cfbbb9a813b708c2a48a541bd8ca1fa7a6484a4880583",
    "governance-runtime/run_exp_m_mutations.py": "be705ba0749bc9df7fd4d1a3c26afbb81b060f0c4a8bb1933a3f036a95d257fb",
    "governance-runtime/run_exp_m_tests.py": "f6d5e35c401ce7393f23de5c5cd0f583c655ea8403575c968f2d664e3a9fb11c",
    "governance-runtime/run_reviewer_compound_attacks.py": "44489f445f888a89d9cfb8e7f3f6a80f45b8b384c10f6a18d40232c41227aed2",
    "governance-runtime/self_adjudicate_r2d.py": "e320addbc158cdf2d94959476ca2928d8d9ccdf9a8b1bc070b243f6d38336d20",
    "governance-runtime/self_falsify_exp_m.py": "4076873139f4da13ff6a0b15998081d487feff601fc77c3228f5754276c02436",
    "governance-runtime/test_exp_m_deterministic.py": "c484e6e29e304019330c28e761ac971c5b52f2fb427c6ac1495a7b3ab83ba089",
    "governance-runtime/test_exp_m_phases.py": "7db4f55d3aaac806f908338da7abbdade85c5ce354ce1204e3fceafefccc12fa",
    "governance-runtime/verify_exp_m_prior_evidence.py": "ef3a4d48e78cba27dcc323424ca04f0b2c02f2389fb58204a3d7f294fb719388",
    "governance-runtime/verify_exp_m_sep_sequence.py": "b9c1f849c43f377ac075887b1bfe949a0232771e2ac64f309eb6e8bc4e2a9618",
    "governance-runtime/verify_sep_sequence.py": "24928ca87f9dccac33ae7262e0a95cd8a1096e2f9a8d1512e0205dcf0f65289b"
  },
  "source_tree": "e07fa898c6abbabf667e1e62de45992d75966f18"
}
~~~

## Evidence manifest

~~~json
{
  "artifacts": [
    {
      "path": "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json",
      "sha256": "7175dff8b451953859644d1d96ad7b640927c6a97acda942d3c0e4e9893110d7",
      "size": 3769
    },
    {
      "path": "experiments/governed-platform/EXP-M-TEST-RESULTS.json",
      "sha256": "f33982c6c745084ac0fceac0e89f1168cd5f87a4c1632e1cdb1cca337c981ea0",
      "size": 8310
    },
    {
      "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json",
      "sha256": "3909057c5df66509c554f368d513dec194d0ba864e02feedd6517ca2f409c555",
      "size": 30495
    },
    {
      "path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
      "sha256": "d4f503195b969e0b5e1fa529d33e7b324843ef8a4913341034619a6b65fe415f",
      "size": 32290
    },
    {
      "path": "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json",
      "sha256": "428cd3c6865b54f21631a5adb1686ea55743b4cd54abc850a2ef54804d260a5b",
      "size": 6450
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json",
      "sha256": "0f845fea90981c94cf40dbccfbe7c53e91de7d050108588604a4229fb43047c7",
      "size": 3256
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt",
      "sha256": "f33982c6c745084ac0fceac0e89f1168cd5f87a4c1632e1cdb1cca337c981ea0",
      "size": 8310
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt",
      "sha256": "483ab1025b4038013532aacb1fc4ab05aebfb594424c138d5c5c20624946717c",
      "size": 1347
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt",
      "sha256": "2a9b1d331c6679fd3bb317ec991aae904f681640b680a1e71a6b9604ad3afecb",
      "size": 1218
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt",
      "sha256": "e27c72d2b1e1f2833f7bc8f84705ff07d80f07c6189de8e9984aead1a7964aa5",
      "size": 5075
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt",
      "sha256": "3909057c5df66509c554f368d513dec194d0ba864e02feedd6517ca2f409c555",
      "size": 30495
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt",
      "sha256": "d4f503195b969e0b5e1fa529d33e7b324843ef8a4913341034619a6b65fe415f",
      "size": 32290
    },
    {
      "path": "experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt",
      "sha256": "c7cc0e01d499f83d005083886dac5068d994ac3300db7e96967b667c2747ae6f",
      "size": 4479
    }
  ],
  "authority_effect": "NONE",
  "commands": [
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_tests.py",
      "exit_code": 0,
      "name": "tests",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt",
      "stdout_sha256": "f33982c6c745084ac0fceac0e89f1168cd5f87a4c1632e1cdb1cca337c981ea0"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/reviewer_exp_m_r2e_suite.py",
      "exit_code": 0,
      "name": "reviewer-core",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt",
      "stdout_sha256": "483ab1025b4038013532aacb1fc4ab05aebfb594424c138d5c5c20624946717c"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
      "exit_code": 0,
      "name": "reviewer-authority",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt",
      "stdout_sha256": "2a9b1d331c6679fd3bb317ec991aae904f681640b680a1e71a6b9604ad3afecb"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_reviewer_compound_attacks.py",
      "exit_code": 0,
      "name": "reviewer-compound",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt",
      "stdout_sha256": "e27c72d2b1e1f2833f7bc8f84705ff07d80f07c6189de8e9984aead1a7964aa5"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_deterministic.py",
      "exit_code": 0,
      "name": "phases",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt",
      "stdout_sha256": "3909057c5df66509c554f368d513dec194d0ba864e02feedd6517ca2f409c555"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/run_exp_m_mutations.py",
      "exit_code": 0,
      "name": "mutations",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt",
      "stdout_sha256": "d4f503195b969e0b5e1fa529d33e7b324843ef8a4913341034619a6b65fe415f"
    },
    {
      "command": "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python governance-runtime/self_falsify_exp_m.py",
      "exit_code": 0,
      "name": "self-falsification",
      "stdout_path": "experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt",
      "stdout_sha256": "c7cc0e01d499f83d005083886dac5068d994ac3300db7e96967b667c2747ae6f"
    }
  ],
  "compound_attack_survivors": 0,
  "exp_m_state": "NOT_QUALIFIED",
  "generated_at_utc": "2026-09-20T14:36:23.673950+00:00",
  "live_provider_api_execution": false,
  "schema": "EXP-M-R2E-EVIDENCE-MANIFEST/v1",
  "source_commit": "13f7f17e7c1609de37dc3d1c4bc35a762607ecb5",
  "source_tree": "e07fa898c6abbabf667e1e62de45992d75966f18"
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

- experiments/governed-platform/EXP-M-SOURCE-FREEZE.json — 7175dff8b451953859644d1d96ad7b640927c6a97acda942d3c0e4e9893110d7
- experiments/governed-platform/EXP-M-TEST-RESULTS.json — f33982c6c745084ac0fceac0e89f1168cd5f87a4c1632e1cdb1cca337c981ea0
- experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json — 3909057c5df66509c554f368d513dec194d0ba864e02feedd6517ca2f409c555
- experiments/governed-platform/EXP-M-MUTATION-RESULTS.json — d4f503195b969e0b5e1fa529d33e7b324843ef8a4913341034619a6b65fe415f
- experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json — 428cd3c6865b54f21631a5adb1686ea55743b4cd54abc850a2ef54804d260a5b
- experiments/governed-platform/EXP-M-R2E-COMPOUND-RESULTS.json — 0f845fea90981c94cf40dbccfbe7c53e91de7d050108588604a4229fb43047c7
- experiments/governed-platform/EXP-M-R2E-TEST-RUN-STDOUT.txt — f33982c6c745084ac0fceac0e89f1168cd5f87a4c1632e1cdb1cca337c981ea0
- experiments/governed-platform/EXP-M-R2E-REVIEWER-CORE-STDOUT.txt — 483ab1025b4038013532aacb1fc4ab05aebfb594424c138d5c5c20624946717c
- experiments/governed-platform/EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt — 2a9b1d331c6679fd3bb317ec991aae904f681640b680a1e71a6b9604ad3afecb
- experiments/governed-platform/EXP-M-R2E-COMPOUND-STDOUT.txt — e27c72d2b1e1f2833f7bc8f84705ff07d80f07c6189de8e9984aead1a7964aa5
- experiments/governed-platform/EXP-M-R2E-PHASE-STDOUT.txt — 3909057c5df66509c554f368d513dec194d0ba864e02feedd6517ca2f409c555
- experiments/governed-platform/EXP-M-R2E-MUTATION-STDOUT.txt — d4f503195b969e0b5e1fa529d33e7b324843ef8a4913341034619a6b65fe415f
- experiments/governed-platform/EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt — c7cc0e01d499f83d005083886dac5068d994ac3300db7e96967b667c2747ae6f

## External-review scope

Treat all self-reported PASS values as claims. Attack the authority/source/evidence boundaries, verify S->E->P changed-path restrictions, verify prior-failure preservation, and independently confirm CA-1..CA-10.

A PASS here cannot qualify EXP-M and cannot authorize live provider/API execution.
