# R8 v15-r1 — Implementation Slice 19: Local AIEPRuntimeProfile Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 14–16 closure anchor:
`fa69cd70113c043a285646d0b1bfaef94caa0c69`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slices 17 and 18 are independently frozen for the next combined review but grant no dependency authority to Slice 19.

## 2. Goal
Implement a repository-local pure structural validator for `AIEPRuntimeProfile`.

It validates exact frozen field shape, attestation-state enum closure, exact boolean constants,
approved-channel list shape/uniqueness, and non-empty GCP-valid opaque IDs/digests.

A declared `ATTESTED` field is not itself proof of attestation. This slice performs no runtime
attestation verification and grants no runtime/evidence/root/terminal authority.

## 3. Frozen fields
Exact required fields:
- runtime_manifest_digest
- attestation_state
- read_only_root_filesystem
- arbitrary_mutable_environment_allowed
- direct_db_cloud_provider_credentials_allowed
- general_external_network_dns_allowed
- approved_channel_ids
- dynamic_code_loading_outside_runtime_manifest_allowed
- profile_digest

No extras allowed.

`attestation_state` is exactly ATTESTED | UNATTESTED_RUNTIME.
`read_only_root_filesystem` is exactly boolean true.
`arbitrary_mutable_environment_allowed` is exactly boolean false.
`direct_db_cloud_provider_credentials_allowed` is exactly boolean false.
`general_external_network_dns_allowed` is exactly boolean false.
`dynamic_code_loading_outside_runtime_manifest_allowed` is exactly boolean false.

`approved_channel_ids` is a Python/JSON list with minItems=1, uniqueItems=true, each element a
non-empty GCP-valid opaque CanonicalId.

`runtime_manifest_digest` and `profile_digest` are non-empty GCP-valid opaque Digest strings.

## 4. Frozen x-validator invariant that remains bounded
`UNATTESTED_RUNTIME` has authority effect NONE and cannot act as root/terminal authority evaluator
or strong evidence producer.

This local validator enforces no positive authority for either attestation_state. For both states,
actual attestation verification/currentness/qualification remains false.

## 5. Frozen invariants
I19-01 exact required-field parity.
I19-02 valid declared ATTESTED profile passes structurally.
I19-03 valid UNATTESTED_RUNTIME profile passes structurally with explicit no-authority metadata.
I19-04 top-level non-Mapping, missing, and extra fields reject.
I19-05 runtime_manifest_digest/profile_digest reject non-string/empty/non-NFC/noncharacter values.
I19-06 attestation_state enum closure.
I19-07 read_only_root_filesystem is exact boolean true; false/non-bool reject.
I19-08 arbitrary_mutable_environment_allowed is exact boolean false; true/non-bool reject.
I19-09 direct_db_cloud_provider_credentials_allowed is exact boolean false; true/non-bool reject.
I19-10 general_external_network_dns_allowed is exact boolean false; true/non-bool reject.
I19-11 dynamic_code_loading_outside_runtime_manifest_allowed is exact boolean false; true/non-bool reject.
I19-12 approved_channel_ids must be a non-empty list.
I19-13 approved_channel_ids require unique non-empty GCP-valid string elements.
I19-14 opaque non-SHA digests pass; actual attestation/runtime/profile/channel authorization remains unverified and authority flags remain false.
I19-15 failure does not poison later validation.
I19-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 6. Nonclaims
No attestation authenticity, runtime-manifest correctness, profile-digest correctness, approved-channel
authorization/currentness, runtime-profile currentness, strong evidence producer qualification,
root/terminal authority evaluation, runtime qualification, evidence promotion, release, deployment,
production, policy authority, or terminal authority.

## 7. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow validator -> require I19 16/16 + inherited baseline 140/140 -> freeze exact candidate -> build one fresh blind combined review packet for Slices 17–19 including raw RED/GREEN logs.
