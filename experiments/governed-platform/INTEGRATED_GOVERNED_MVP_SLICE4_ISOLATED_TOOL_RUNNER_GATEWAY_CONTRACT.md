# Integrated Governed MVP — Slice 4 Isolated Tool Runner Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

This slice begins only after the accepted Slice 3 integration into `feature/integrated-governed-mvp` at merge commit `a720fabd25ea21cf7a2c559dfa1ce3d68e8bb22d`. It consumes the exact bounded repository-mutation lineage established by Slice 3 and addresses the next execution-plane gap identified by `ARCHITECTURE_IMPLEMENTATION_MAP.md`: a product-facing tool execution boundary.

It deliberately does **not** claim a secure arbitrary-code sandbox. The frozen subject is narrower: a deterministic platform-owned subprocess/tool runner that executes only an exact pre-authorized argv-form command inside an isolated temporary workspace, with an explicitly minimized environment, bounded runtime/output, durable idempotency, and evidence lineage. Shell interpretation, ambient repository access, arbitrary network tools, production credentials, remote mutation, release, deploy, merge, and completion authority remain outside this slice.

## 1. Goal

Falsify the hypothesis that an exact Slice 3-authorized tool request can launch at most one bounded subprocess only when the platform-owned Tool Execution Contract and Tool Execution Manifest exactly match the current authoritative lineage; and that executable/argv/cwd/environment substitution, shell metacharacters, workspace escape, timeout, oversized output, replay, crash, concurrency, worker/model authority claims, or process failure cannot widen authority or become successful/terminal evidence.

## 2. Included

- exact Slice 3 result/lineage binding;
- platform-owned Tool Execution Contract;
- frozen Tool Execution Manifest binding executable identity, argv, workspace root, allowed environment keys, timeout, output limit, input digest, tool identity, and idempotency identity;
- argv-form subprocess execution with `shell=False` only;
- exact executable allowlist and command binding;
- isolated temporary workspace confinement and current-workspace revalidation immediately before launch;
- explicit environment allowlist with ambient secret-bearing variables absent by default;
- bounded timeout and process-group termination on timeout where supported by the reference runtime;
- bounded stdout/stderr capture with deterministic truncation metadata;
- durable local idempotency/non-rebinding across replay/restart;
- crash representation before process launch and after process completion/before response;
- concurrent identical-request convergence;
- exact evidence lineage from Slice 3 authorization through execution contract/manifest, command, workspace, process result, hashes, and replay/recovery disposition;
- explicit refusal to interpret tool/model output as release/deploy/merge/production/completion authority.

## 3. Deferred / nonclaims

- arbitrary untrusted-code containment against kernel/OS/container/VM escape;
- seccomp/AppArmor/SELinux production enforcement;
- production container/VM sandbox orchestration;
- authenticated network-egress enforcement at kernel/network-policy level;
- browser automation isolation;
- production GitHub/GitLab/Bitbucket credentials or remote writes;
- secret-manager credential leases;
- multi-host execution atomicity;
- distributed consensus;
- physical power-loss/storage-controller durability;
- third-party independent certification;
- release, deploy, merge, production, or completion authority.

Passing this slice proves only the frozen reference tool-runner boundary. It must not be described as proving arbitrary-code sandbox security.

## 4. Frozen authoritative records

### Tool Execution Contract

The platform-owned contract must bind at least:

- `tool_contract_id`
- `project_id`
- `task_id`
- `plan_step_id`
- `allowed_executable`
- `allowed_workspace_root`
- `allowed_env_keys`
- `timeout_seconds`
- `max_output_bytes`
- `required_slice3_result_hash`
- `contract_hash`

### Tool Execution Manifest

The frozen manifest must bind at least:

- `tool_execution_id`
- `tool_contract_id`
- `execution_id`
- `tool_id`
- `idempotency_key`
- `executable`
- `argv`
- `workspace_path`
- `input_digest`
- `environment`
- `slice3_result_hash`
- `manifest_hash`

Neither record may be created, widened, or rewritten by worker/model output.

## 5. Frozen authority invariants

**S4-I01 External authority only** — model/tool output cannot create, widen, refresh, replace, or revoke the execution contract, manifest, upstream capability, or terminal authority.

**S4-I02 Exact Slice 3 lineage** — tool launch is reachable only from an exact successful Slice 3 result bound to the same project/task/execution/plan-step lineage.

**S4-I03 Exact contract/manifest binding** — contract identity/hash and manifest identity/hash, tool/execution identity, input digest, executable, argv, workspace, environment, and idempotency identity must exactly match platform state.

**S4-I04 No shell interpretation** — process launch uses argv-form execution with `shell=False`; shell metacharacters, substitutions, redirections, pipes, or command separators cannot acquire shell semantics.

**S4-I05 Executable confinement** — only the exact platform-authorized executable may launch. Alternate executable paths, PATH substitution, interpreter substitution, or command widening fail before launch.

**S4-I06 Workspace confinement** — the execution cwd must resolve inside the exact isolated workspace root. Absolute/relative traversal, symlink escape, or replaced workspace identity fails before launch.

**S4-I07 Environment minimization** — only explicitly allowed environment keys/values from the frozen manifest reach the subprocess. Ambient CI/provider credentials and undeclared environment variables are not inherited.

**S4-I08 Runtime bound** — exceeding the frozen timeout produces a timeout result and terminates the launched process/process group; timeout is never classified as successful execution.

**S4-I09 Output bound** — retained stdout/stderr are bounded by the frozen byte limit and evidence records whether truncation occurred; oversized output cannot corrupt authority state or silently bypass evidence limits.

**S4-I10 Durable idempotency/non-rebind** — one idempotency identity maps to at most one exact contract/manifest/command/workspace/result binding across replay and restart; semantic rebinding fails closed.

**S4-I11 Crash/retry non-amplification** — crash before launch leaves no completed execution; crash after durable process result but before response recovers the exact retained result without a duplicate launch.

**S4-I12 Concurrent convergence** — concurrent identical requests converge to one exact launch/result binding.

**S4-I13 Process outcome honesty** — nonzero exit, signal termination, timeout, malformed result, or ambiguous durable state cannot be converted to success by worker/model claims or response text.

**S4-I14 Exact evidence lineage** — evidence binds upstream Slice 3 result, contract hash, manifest hash, executable/argv, workspace identity, input digest, environment digest, start/result state, exit classification, stdout/stderr hashes, and replay/recovery disposition.

**S4-I15 Terminal/remote separation** — tool success cannot mint remote push, merge, release, deploy, production, or completion authority.

**S4-I16 Liveness after adversity** — after denial, timeout, replay, crash, or concurrency cases, a fresh independently authorized execution remains live and can run exactly once.

## 6. Frozen acceptance cases

- **S4-01** clean exact Slice 3 lineage + exact tool contract + exact manifest launches one allowed argv-form command in the isolated workspace and retains one exact result.
- **S4-02** missing, forged, denied, mismatched, or non-success Slice 3 lineage fails before process launch.
- **S4-03** tool-contract identity/hash/project/task/plan-step substitution or manifest-to-contract substitution fails before launch.
- **S4-04** executable, argv, tool identity, execution identity, input digest, environment, workspace, or manifest-hash substitution fails before launch.
- **S4-05** alternate executable, PATH-based substitution, or unapproved interpreter fails before launch.
- **S4-06** shell metacharacters/separators/redirection tokens are passed only as literal argv data; no second command or shell side effect occurs.
- **S4-07** absolute/relative cwd escape, `..` traversal, symlink escape, or replaced workspace identity fails before launch.
- **S4-08** undeclared ambient environment variables, including a synthetic secret, are absent in the subprocess; declared frozen environment values are present exactly.
- **S4-09** execution exceeding the frozen timeout is terminated and classified `TIMED_OUT`, never success.
- **S4-10** stdout/stderr exceeding the frozen output bound are deterministically truncated with hashes/byte counts/truncation flags retained.
- **S4-11** nonzero exit is retained as `FAILED_PROCESS`; worker/model text claiming success or terminal authority changes no effective state.
- **S4-12** exact replay returns the exact prior durable result/evidence and launches no duplicate process.
- **S4-13** same idempotency identity with changed command/manifest/contract/workspace/upstream lineage fails closed and preserves the original binding.
- **S4-14** crash before launch permits one exact retry; crash after durable process completion but before response returns the retained result without duplicate launch.
- **S4-15** concurrent identical requests converge to one exact process/result identity and one durable idempotency binding.
- **S4-16** evidence retains all required hashes/bindings, no remote/release/deploy/merge occurs, and a fresh independently authorized second execution remains live after prior adverse cases.

## 7. Construction and freeze rules

1. Commit this contract before acceptance-harness or mechanism implementation.
2. Freeze S4-01..S4-16 in a dedicated acceptance harness before implementing the tool runner.
3. The first harness run is expected to fail at the intentionally absent Slice 4 mechanism; preserve that construction failure.
4. Repairs may not weaken an invariant, acceptance case, timeout/output bound, authority boundary, or nonclaim.
5. Tests must not require production credentials, external network access, or remote repository mutation.
6. Freeze one exact candidate SHA only after the dedicated Slice 4 harness and complete governed-platform regression are green in construction.
7. The first complete dedicated Slice 4 workflow and complete governed-platform workflow on that exact frozen SHA are the authoritative scientific acceptance evidence.
8. `BOUNDED_PASS` requires S4-01..S4-16 explicitly pass plus the complete governed-platform regression suite on the same exact frozen SHA.
9. Workflow status alone is insufficient; direct job-log correspondence and exact checkout SHA must be verified.
10. Any post-freeze repair requires a new candidate; the prior exposed result remains preserved without rewriting.
11. Independent semantic/platform review is required before bounded scientific adjudication because this slice adds a consequential execution boundary.

## 8. Claim boundary

A positive Slice 4 result would support only that, in the tested reference runner, one exact platform-authorized argv-form subprocess can be constrained to an isolated workspace, minimized environment, fixed executable/arguments, bounded runtime/output, and durable replay identity under the tested conditions. It would **not** establish arbitrary-code sandbox security, kernel/container escape resistance, production network isolation, production credential safety, remote repository authority, or release/deploy/merge/production/completion authority.
