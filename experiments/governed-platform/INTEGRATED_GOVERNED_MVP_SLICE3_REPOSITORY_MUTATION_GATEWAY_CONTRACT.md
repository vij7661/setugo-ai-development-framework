# Integrated Governed MVP — Slice 3 Repository Mutation Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

This slice begins only after the bounded Slice 2 adjudication in `adjudication/INTEGRATED-GOVERNED-MVP-SLICE2.json`. It consumes the exact bounded execution authorization/result lineage established by Slice 2 and moves one step closer to the target execution plane described in `ARCHITECTURE_IMPLEMENTATION_MAP.md` and `AUTHORITY_RUNTIME_OPERATIONAL_CONTRACT.md`.

It does **not** claim to implement an arbitrary-code sandbox. The frozen subject is narrower: a deterministic repository-mutation gateway applying a precomputed patch only inside an isolated local test workspace under a platform-owned Plan-Step Effect Contract and frozen Action Effect Manifest.

## 1. Goal

Falsify the hypothesis that an exact Slice 2-authorized development mutation can be applied to a local isolated Git workspace only when the frozen patch, base revision, target resources, path bounds, changed-file bounds, and effect-manifest lineage all match authoritative platform state; and that replay, crash, concurrency, path escape, Git-metadata mutation, remote/push attempts, or worker/model claims cannot widen the mutation or mint terminal authority.

## 2. Included

- exact Slice 2 decision/result lineage binding;
- platform-owned Plan-Step Effect Contract;
- frozen Action Effect Manifest containing base SHA, patch digest, target paths, changed files, action/tool identity, and idempotency identity;
- deterministic application of a precomputed patch to an isolated local Git workspace;
- exact current-base revalidation immediately before mutation;
- allowed-path and forbidden-path enforcement;
- maximum changed-file enforcement;
- path traversal, absolute-path, symlink-escape, and Git-metadata protection;
- atomic validation-before-commit behavior for malformed/conflicting patches;
- durable local idempotency/non-rebind across replay and restart;
- crash representation before commit and after local commit/before response;
- concurrent identical request convergence;
- exact evidence lineage from Slice 2 authorization through effect contract, manifest, patch, base revision, resulting local commit, and replay/recovery disposition;
- explicit refusal to push, merge, release, deploy, mutate a production remote, or interpret worker/model output as terminal authority.

## 3. Deferred / nonclaims

- arbitrary untrusted code or shell execution sandboxing;
- OS/container/VM escape resistance;
- production GitHub/GitLab/Bitbucket repository writes;
- authenticated remote push;
- browser or arbitrary network access;
- secret-manager or production credential leasing;
- multi-host repository atomicity;
- distributed consensus;
- production branch protection enforcement;
- cloud KMS/HSM production authority;
- physical power-loss/storage-controller durability;
- third-party independent certification;
- release, deploy, merge, production, or completion authority.

The reference implementation must use an isolated temporary local Git repository/workspace and must not require external network access or repository credentials. Passing this slice proves only the frozen local repository-mutation boundary.

## 4. Frozen authoritative records

### Plan-Step Effect Contract

The platform-owned contract must bind at least:

- `effect_contract_id`
- `project_id`
- `task_id`
- `plan_step_id`
- `allowed_action_classes`
- `allowed_paths`
- `forbidden_paths`
- `base_sha`
- `max_changed_files`
- `destructive_effect_allowed`
- `required_slice2_result_hash`
- `contract_hash`

### Action Effect Manifest

The frozen manifest must bind at least:

- `action_effect_id`
- `effect_contract_id`
- `execution_id`
- `tool_id`
- `idempotency_key`
- `base_sha`
- `patch_digest`
- `changed_files`
- `target_paths`
- `slice2_result_hash`
- `manifest_hash`

Neither record may be widened or rewritten by worker/model output.

## 5. Frozen authority invariants

**S3-I01 External authority only** — models/workers may propose content but cannot create, widen, refresh, or replace the effect contract, action-effect manifest, capability, or terminal authority.

**S3-I02 Exact Slice 2 lineage** — repository mutation is reachable only from an exact successful Slice 2 result bound to the same project/task/execution/effect identity and current authoritative lineage.

**S3-I03 Exact base binding** — the workspace HEAD must equal the frozen `base_sha` immediately before mutation. A stale, advanced, replaced, or unrelated base fails closed.

**S3-I04 Exact patch/manifest binding** — the actual patch digest, changed-file set, target-path set, tool identity, and idempotency identity must equal the frozen manifest.

**S3-I05 Resource subset enforcement** — every mutation must remain inside allowed paths, touch no forbidden path, remain within changed-file bounds, and never mutate `.git` control metadata through the patch surface.

**S3-I06 Workspace containment** — absolute paths, `..` traversal, symlink escape, alternate worktree escape, or equivalent path confusion cannot cause mutation outside the isolated workspace.

**S3-I07 Validation-before-authoritative-commit** — malformed, conflicting, overbroad, or semantically rebound input cannot leave a partially accepted authoritative local commit.

**S3-I08 Durable idempotency/non-rebind** — one idempotency identity maps to at most one exact manifest/patch/base/result binding across replay and restart.

**S3-I09 Crash/retry non-amplification** — crash before authoritative local commit leaves no accepted mutation; crash after authoritative local commit but before response recovers the exact existing result without a duplicate commit.

**S3-I10 Concurrent convergence** — concurrent identical requests converge to one exact local commit/result identity.

**S3-I11 Exact evidence lineage** — retained evidence binds Slice 2 result, effect contract, action manifest, base SHA, patch digest, changed files, resulting commit SHA, and replay/recovery disposition.

**S3-I12 Terminal/remote separation** — local mutation success cannot push, merge, release, deploy, change a remote, or mint production/completion authority.

## 6. Frozen acceptance cases

- **S3-01** clean exact Slice 2 lineage + exact effect contract + exact manifest applies one allowed patch to an isolated local Git workspace and creates one exact local result commit.
- **S3-02** missing, forged, denied, mismatched, or non-success Slice 2 lineage fails before workspace mutation.
- **S3-03** effect-contract identity/hash/project/task/plan-step substitution or manifest-to-contract substitution fails before mutation.
- **S3-04** stale, advanced, replaced, or unrelated workspace base SHA fails before mutation.
- **S3-05** patch digest, tool identity, execution identity, changed-file set, target-path set, or manifest hash substitution fails before mutation.
- **S3-06** attempted write outside `allowed_paths`, inside `forbidden_paths`, or beyond `max_changed_files` fails with no accepted local commit.
- **S3-07** absolute path, `..` traversal, path normalization trick, or symlink escape cannot mutate outside the isolated workspace.
- **S3-08** attempted mutation of `.git` metadata, hooks, refs, remote configuration, or equivalent repository-control metadata fails before accepted commit.
- **S3-09** malformed/conflicting patch or patch application failure leaves the authoritative local repository at the original accepted base with no partial accepted commit.
- **S3-10** exact replay with the same idempotency identity returns the exact prior local result commit/evidence and creates no duplicate commit.
- **S3-11** same idempotency identity with changed base, patch, manifest, contract, or Slice 2 lineage fails closed and preserves the original binding.
- **S3-12** crash before local commit leaves no accepted mutation; exact retry may apply and commit once.
- **S3-13** crash after local commit but before response preserves one accepted commit; exact retry returns the existing commit without duplicate mutation.
- **S3-14** concurrent identical requests converge to one exact local result commit and one durable idempotency binding.
- **S3-15** evidence contains exact Slice 2 result hash, effect-contract hash, manifest hash, base SHA, patch digest, changed-file set, result commit SHA, and replay/recovery disposition; worker/model terminal claims add no authority.
- **S3-16** no remote push/merge/release/deploy occurs, and after prior denial/replay/crash cases a fresh independently authorized second local mutation remains live and commits exactly once.

## 7. Construction and freeze rules

1. Commit this contract before acceptance-harness or mechanism implementation.
2. Freeze S3-01..S3-16 in a dedicated acceptance harness before implementing the repository-mutation gateway.
3. Preserve the first construction failure/result before repair.
4. Repairs may not weaken an invariant, acceptance case, or nonclaim.
5. The implementation may use local Git and durable local storage, but tests must not require external network or repository credentials.
6. Freeze one exact candidate SHA only after the dedicated Slice 3 harness and complete governed-platform regression are green in construction.
7. The first complete dedicated Slice 3 workflow and complete governed-platform workflow on that exact frozen SHA are the authoritative scientific acceptance evidence.
8. `BOUNDED_PASS` requires S3-01..S3-16 explicitly pass plus the complete governed-platform regression suite on the same exact frozen SHA.
9. Workflow status alone is insufficient; direct job-log correspondence and exact checkout SHA must be verified.
10. Any post-freeze repair requires a new candidate; the first frozen result remains retained, even if the failure is metadata/provenance rather than mechanism behavior.

## 8. Claim boundary

A positive Slice 3 result would support only that, in the tested local reference repository-mutation gateway, a precomputed patch can be constrained to an exact frozen local Git workspace/effect manifest and committed at most once under the tested replay/crash/concurrency conditions. It would **not** establish arbitrary-code sandbox security, production remote-repository mutation safety, credential isolation, distributed atomicity, or release/deploy/merge/production/completion authority.
