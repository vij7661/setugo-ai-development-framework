# ECC-Derived Parallel Program — V3 Omission-Hardening Ledger

## Status

- Program: `ECC_DERIVED_PARALLEL_V3_OMISSION_HARDENING`
- Parent reviewed V2 candidate: `2bea9dab240ac9b57b0e3e12fa96c8193ab2bbf8`
- Governing V2 review evidence class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- V2 review disposition: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- Manual-review threshold contribution: `0`
- Authority effect: `NONE_EVIDENCE_ONLY`
- V3 production integration: `NOT_CLAIMED`
- V3 requirement adoption/promotion: `NOT_AUTHORIZED`

## Review finding being falsified

The V2 review found omission-based false-green paths: V2 strict checks activated only when stronger attestation/authentication/governance fields happened to be supplied. Omission could fall back to historical permissive behavior. The review also identified `ecc_governance.py` as a shared trust boundary.

V3 therefore separates two evaluation classes:

1. Historical calls without `requirement_candidate=True` remain available only to replay V1/V2 bounded-reference evidence.
2. New requirement-candidate evaluation explicitly uses `requirement_candidate=True` and must fail closed when mandatory evidence is absent.

The historical path MUST NOT qualify or promote a new requirement candidate.

## Frozen executable assertions before repair

- Test file: `experiments/ecc_derived/test_ecc_governance_v3_omission_hardening.py`
- Frozen test commit: `4012eb6082aaeb3cd79bda77b77a892cbc05a375`
- Workflow-enabled pre-repair candidate: `8472480d4e6be10f2d01c902617ad0bb10f765b8`

### RED-001

- Workflow run: `34690281109`
- Job: `103544199688`
- Exact checkout: `8472480d4e6be10f2d01c902617ad0bb10f765b8`
- Result: `153 tests; 18 failures + 3 errors`
- Prior 132 tests: `PASS`
- Mechanism had not been repaired before this RED.

The new failures established that the strict requirement-candidate entrypoint and shared-module trust manifest did not yet exist.

## Mechanism repair

- Mechanism repair commit: `1bf710e6f9825d264ef7f355f72f9c98d2f96376`
- Module blob: `c03d1a45ef9a312c27ab975cbb7fce626edbf0fa`
- Tests unchanged.

The repair introduced `requirement_candidate=True` on the reference functions. In this evaluation class:

- EXP-ECC-1 requires platform enforcement-point attestation, action-sequence binding, and process identity.
- EXP-ECC-2 requires a machine-verified executable/runtime profile and nonempty verified execution paths.
- EXP-ECC-3 requires attested harness/runtime identity and per-capability allowed-set requirements; provider/model remains user-selectable and role-neutral.
- EXP-ECC-4 requires authenticated principal authority, project binding, and approval/current-sequence binding.
- EXP-ECC-5 requires secret-safe configuration identity plus platform configuration attestation, executable/argv evidence, credential attestation, and resolved endpoint evidence.
- EXP-ECC-6 requires provider identity evidence for relationship classification and authenticated manual-review principal evidence before any manual-threshold credit. AI feedback remains zero-credit.
- EXP-ECC-7 requires governed claim/dependency/retraction evidence. Even a fully supported strict reference proposal is only `LEARNING_PROPOSAL_REFERENCE_ELIGIBLE` and remains `promotable = false` because live pipeline integration is absent.

### RED-002

- Workflow run: `34690496958`
- Job: `103544765124`
- Exact checkout: `1bf710e6f9825d264ef7f355f72f9c98d2f96376`
- Result: `153 tests; 152 PASS; 1 failure`
- Remaining failure: `SHARED_MODULE_TRUST_BOUNDARY_MANIFEST_MISSING`
- All omission-hardening behavior: `PASS`
- Prior 132 tests: `PASS`

## Shared-module trust boundary

Added `experiments/ecc_derived/ecc_governance_trust_manifest.json` binding the shared reference module by SHA-256 and Git blob and declaring:

- `legacy_path_policy = HISTORICAL_REFERENCE_ONLY`
- `candidate_path_policy = MANDATORY_STRICT_EVALUATION`
- coverage of EXP-ECC-1 through EXP-ECC-7.

This does not make the shared implementation independently trustworthy; it makes the coupling explicit and exactly bound for review/falsification.

## GREEN-003

- Candidate: `0c2a48af3fd9af0d0e03df5bc42a109f360c011d`
- Workflow run: `34690527701`
- Job: `103544844775`
- Exact checkout: `0c2a48af3fd9af0d0e03df5bc42a109f360c011d`
- Result: `153/153 PASS`
- Prior 132 tests: `PASS`
- New V3 omission/trust-boundary tests: `PASS`

## Per-experiment V3 status pending external re-review

| Experiment | V3 internal bounded status | Remaining nonclaim |
|---|---|---|
| EXP-ECC-1 | `STRICT_REFERENCE_MECHANISM_PASS_PENDING_REVIEW` | No live hook/process attestation demonstrated |
| EXP-ECC-2 | `STRICT_REFERENCE_MECHANISM_PASS_PENDING_REVIEW` | No real executable code extraction/runtime failure injection demonstrated |
| EXP-ECC-3 | `STRICT_REFERENCE_MECHANISM_PASS_PENDING_REVIEW` | No live harness qualification/identity attestation demonstrated |
| EXP-ECC-4 | `STRICT_REFERENCE_MECHANISM_PASS_PENDING_REVIEW` | No live platform-issued activation authority demonstrated |
| EXP-ECC-5 | `STRICT_REFERENCE_MECHANISM_PASS_PENDING_REVIEW` | No live cryptographic configuration attestation/DNS enforcement demonstrated |
| EXP-ECC-6 | `DEFER_PENDING_INTEGRATION_EVIDENCE` | Real provider/gateway identity and authenticated human/manual review absent |
| EXP-ECC-7 | `DEFER_PENDING_INTEGRATION_EVIDENCE` | Real governed claim/dependency/retraction pipeline integration absent |

## Explicit nonclaims

V3 does not establish:

- V18 or production-runtime integration;
- live third-party hook, harness, MCP, or adapter enforcement;
- cryptographic provider identity or real external reviewer-model transport;
- independent human/manual review;
- live learned-artifact promotion;
- requirement adoption into the governed platform;
- merge/release/deploy/completion authority.

## Next permitted action

Run the full suite on the exact ledger head. If it remains green, freeze that exact head as the V3 remediation candidate and submit a self-contained external engineering re-review packet. The external review may recommend bounded impact adjudication but cannot itself promote any requirement.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
