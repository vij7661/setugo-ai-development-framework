# EXP-O Pilot 24 — Pre-Execution Safety Amendment

Status: **FROZEN BEFORE ANY PILOT 24 AWS/KMS EXECUTION**

Parent preregistration: `EXP-O-PILOT24-AWS-KMS-ASYMMETRIC-CHECKPOINT-PREREGISTRATION.md`

## Reason

The original preregistration described P24-13, P24-14 and P24-15 as runtime attempts to call `DisableKey`, `ScheduleKeyDeletion` and `CreateKey` and expect access denial.

That is not an acceptable falsification technique for a live cloud key: if the IAM role were unexpectedly over-permissioned, the test itself could disable, schedule deletion of, or create AWS KMS resources. A governance experiment must not rely on an unsafe action succeeding in order to discover that its permission assumption was wrong.

This issue was identified **before any Pilot 24 workflow, OIDC role assumption, KMS Sign call, or scientific execution**.

## Amendment

P24-13/14/15 are retained as least-privilege configuration endpoints but **must not issue those state-changing AWS API calls**.

Their evidence is limited to:

- Pilot 24 workflow/source contains no `DisableKey`, `ScheduleKeyDeletion`, `CreateKey`, or wildcard `kms:*` invocation;
- Pilot 24 workflow contains no static AWS access-key secret reference;
- the frozen expected role policy grants only `kms:Sign`, `kms:GetPublicKey`, and `kms:DescribeKey` on the exact configured KMS key ARN;
- no scientific conclusion may claim that AWS runtime denial of those three administrative APIs was directly observed unless a later safe, independent policy-inspection mechanism establishes it without invoking the actions.

Therefore final adjudication must report P24-13/14/15 as **CONFIGURATION-BOUND / NOT DESTRUCTIVE-RUNTIME-PROBED**, not as runtime access-denial observations.

## Unchanged cases

P24-01 through P24-12 and P24-16 through P24-20 remain unchanged and may be executed because they are read/sign/cryptographic-validation or non-destructive invalid-request paths.

P24-12 must use an unregistered/different key identifier only in a non-destructive read/sign request and must not modify any KMS resource.

## Scientific consequence

A full Pilot 24 result can support:

- observed GitHub OIDC -> AWS STS role acquisition;
- observed exact-key KMS signing/public-key retrieval;
- observed asymmetric local verification and substitution resistance;
- observed application semantic stale/scope/replay rejection;
- workflow/configuration evidence that no destructive KMS control-plane action is requested.

It cannot support a claim that `DisableKey`, `ScheduleKeyDeletion`, or `CreateKey` were individually denied by AWS at runtime.
