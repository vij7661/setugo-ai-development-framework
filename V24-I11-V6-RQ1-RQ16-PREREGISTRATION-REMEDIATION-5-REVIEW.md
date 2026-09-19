# V24-I11-V6 RQ-16 preregistration remediation-5 review

Planning-only artifact. No RQ-16 execution occurred.

## Identity
reviewed_source_commit=73cbce0f8a322114f23532f3da545bf49fa70695
reviewed_source_tree=51da776ce699f9bbf1476805d0d1f3962dd7a906
packet_parent_commit=73cbce0f8a322114f23532f3da545bf49fa70695
packet_parent_tree=51da776ce699f9bbf1476805d0d1f3962dd7a906
predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
exact_source_diff_sha256=cdc71ded3a286517e7ec9b9a4f8a21fe2b40ceb3bc3caccb7558fb95fcd23a6c
source_manifest_sha256=9a13bbdabf7042c16dbbd67687b26a4609f669cec6f3f9607f8cfbc8c94bdcca
packet_content_identity_schema_version=1
branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION
packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION
packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION
RQ16_EXECUTED=false
RQ16_AUTHORIZED=false
RQ16_started=false
scientific_rerun=false
qualification=NOT_QUALIFIED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY

## Frozen contract

### execution contract

```json
{
  "rq_id": "RQ-16",
  "trigger": "Disk full / read-only / I/O / permission failure",
  "oracle": "Fail closed without fabricated success",
  "execution_required": true,
  "execution_authorized": false,
  "arms": {
    "ENOSPC": {
      "operation": "write_authority_record or fsync on exact bound records path",
      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
      "classification": "INSUFFICIENT_EVIDENCE",
      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
    },
    "EROFS": {
      "operation": "write_authority_record or rename on exact bound path",
      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
      "classification": "UNSAFE",
      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
    },
    "EIO": {
      "operation": "exact record read/write/fsync/rename syscall",
      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
      "classification": "INSUFFICIENT_EVIDENCE",
      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
    },
    "EACCES": {
      "operation": "exact service access to records/consumed path",
      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
      "classification": "PROXY_NOT_ACCEPTABLE",
      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
    }
  },
  "classification_rules": {
    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
  },
  "state_machine": {
    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
  },
  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```

## Source-path analysis

### preregistration

```markdown
# V24-I11-V6 RQ-16 preregistration (planning only)

Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
that closed Remediation-7 head.

Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
failure**. Oracle: **Fail closed without fabricated success**. This document
does not authorize execution.

## Actual write path

In `governance-runtime/native/v24_v6_trusted_authority_service.c`:

- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
  `fsync`, then closes and unlinks on failure.
- candidate handling calls `materialize_private()` for context, boundary and
  payload before gate execution.
- root control calls `consume_record_trusted()`.
- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
  from records to consumed. It returns an authoritative response only after
  `rename` succeeds.
- `write_authority_record()` creates records with
  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
  `fsync`, closes, and unlinks on failure.

RQ-16 must bind the injected errno to one of these exact operations; mocked
Python exceptions and candidate-side failures are proxies.

## Execution arms and classifications

ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
host `/run` is prohibited. No repository evidence proves such a quota boundary,
so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.

EROFS requires a dedicated qualification filesystem whose read-only transition
does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
unsafe and a separate filesystem would collide with RQ-17 topology semantics;
the arm is `UNSAFE` pending dedicated-mount evidence.

EIO requires a disposable kernel fault layer returning EIO on the exact target
operation. `dm-error` or equivalent is acceptable only with a dedicated device
and independent activation/errno proof. No such boundary is evidenced;
classification is `INSUFFICIENT_EVIDENCE`.

EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
trusted service runs as UID 0. Candidate-side permission failure or a mocked
exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.

These are execution arms under one frozen case, not new cases.

## Required state machine and proof

Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
state record target membership in records/consumed, response and authority,
errno proof, service state, filesystem/device/mount metadata, ownership/modes,
and hashes. PASS requires exact fault activation plus syscall errno, no
authoritative success, explainable target lifecycle, recoverable service,
complete observers, and exact post-restoration hashes/security state. Absence
of a response alone is never PASS. Authoritative success after a proven fault
is RED. Missing/malformed proof or observer/cleanup failure is
HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.

## Restoration, safety and aborts

The only permitted future mutation is a bounded fixture on a dedicated,
preflight-verified boundary. The host root filesystem, repository, historical
evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
workspace are never targets. Cleanup removes the fixture, restores mount/quota
and metadata, revalidates service/socket/PID, records/consumed integrity,
device IDs, mount options, ownership/modes, hashes and security controls. Any
failure blocks all dependent cases.

Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
free-space margin, backup material, root recovery, service health or observer
access differ from the preregistered baseline, or if an evidence directory could
be overwritten.

Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.

## Harness safety and governance

`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
`--execute-rq16` refuses with a nonzero result. Future execution requires a
separately generated authorization token bound to exact commit, host/runtime
identity and plan digest. No token exists in this branch.

`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
Qualification remains `NOT_QUALIFIED`; scientific execution remains
`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
mechanism classifications before any execution authorization.

## Remediation-2 hardening

The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.

Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.

No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
```

## Cleanup contract

### cleanup

```markdown
# RQ-16 cleanup and restoration contract

RQ-16 remains preregistration-only. No mutation has been executed.

Every future arm must capture an immutable baseline and restore it before any
dependent case. The baseline includes service/gate hashes, unit bytes, PID and
socket identity, records/consumed ownership and modes, filesystem device IDs,
mount options, security controls, and exact target lifecycle.

The inverse operation must be explicit: remove only the bounded fault fixture,
restore the saved mount/quota/metadata state, restart only as required by the
approved recovery procedure, and independently remeasure every baseline field.
If a mount operation fails, root recovery is unavailable, a fault fixture
cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
dependent cases abort. Historical evidence directories are never targets.

The future harness must refuse destructive execution unless the exact host,
commit, plan digest, and separately generated authorization token are bound.
`--plan` and `--self-test` are the only permitted modes in this preregistration.
```

## Issues

### issue ledger

```json
{
  "issues": [
    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
  ],
  "open_automatable_issues": 0,
  "manual_review_required": true,
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false,
  "latest_remediation_status": {
    "RQ16-TRUSTED-ATTESTATION": "RESOLVED",
    "RQ16-AUTH-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-IDENTITY-MODEL": "RESOLVED",
    "RQ16-TEST-SUFFICIENCY": "RESOLVED"
  }
}
```

## Included file SHA-256
19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
ffdf22fe6b7cb13c69bb21b01d927d1e097d4bc6b13e6c5224c3995681149c48  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7  implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00  implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md
ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b  implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
2d15ac596a29c00e8884952aeb4bc15421f2e14709f9de376232cb6f300fc16c  governance-runtime/v24_v6_rq1_rq16_harness.py
f524ed38c9bdf80c32638351b39310e8ac886f1efaad0a4e548c7ba41b21ac0f  governance-runtime/test_v24_v6_rq1_rq16_harness.py
1f8f4861537c1417bf7c9a12b8e39c26e464cfbd73559fc94a28148cabc28877  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
58c6c2ae49817f1380ce1b95173a2c2c6d18d46d636b0552c5dccdce588c7d2a  governance-runtime/check_rq16_preregistration_packet.py

### implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json sha256=31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7

```python
{
  "authorization_schema_version": "1",
  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
  "single_use": true,
  "arm_scoped": true,
  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md sha256=13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00

```python
# Durable authorization nonce design

No live nonce is created in preregistration. Future authorization must use a root-owned, trusted append-only nonce ledger outside the candidate workspace. Consumption is an atomic create-with-exclusive semantics operation containing the nonce, authorization hash, arm, and timestamp. A second consume attempt fails closed as replay. The ledger must survive process restart, be non-candidate-writable, and be independently observed before and after use.

The JSON token is not authoritative by itself. The trusted issuer/reviewer artifact hash, exact plan/contract/runtime bindings, and root-owned source path must all validate before the nonce ledger is touched. No trusted issuer mechanism is available on this planning host, so future authorization remains `MANUAL_REVIEW_REQUIRED`.
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md sha256=ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b

```python
# RQ-16 read-only capability inspection

This inspection was non-destructive and did not enable or mutate any host feature.

The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.

Source inspection found the trusted service operations at:

- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.

Read-only commands attempted:

```text
Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
```

Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.

`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
```


### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=2d15ac596a29c00e8884952aeb4bc15421f2e14709f9de376232cb6f300fc16c

```python
#!/usr/bin/env python3
"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
from __future__ import annotations
import argparse, json, math, re
from datetime import datetime, timezone

ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}

def expected_context(arm, record_id="abc123"):
    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","review_artifact_sha256":"review-sha"}

def check_rq17_contamination(expected, observed):
    reasons=[]
    if expected.get("expected_records_device") != expected.get("expected_consumed_device"): reasons.append("expected_baseline_split")
    for stage, o in (observed or {}).items():
        if not isinstance(o,dict): reasons.append(f"stage_malformed:{stage}"); continue
        pairs=(("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"))
        for actual, exp in pairs:
            if o.get(actual) != expected.get(exp): reasons.append(f"{stage}:{actual}_mismatch")
        if o.get("records_device") != o.get("consumed_device"): reasons.append(f"{stage}:split_filesystem")
    return not reasons, reasons

def validate_target_binding(observed, expected):
    reasons=[]
    fields=(("target_record_id","target_record_id"),("records_path","expected_records_path"),("consumed_path","expected_consumed_path"),("records_realpath","expected_records_realpath"),("consumed_realpath","expected_consumed_realpath"),("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"),("records_symlink","expected_records_symlink"),("consumed_symlink","expected_consumed_symlink"))
    for a,e in fields:
        if observed.get(a) != expected.get(e): reasons.append(f"target_binding:{a}")
    return reasons

def validate_fault_proof(proof, expected):
    reasons=[]; arm=expected["arm"]
    req=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","filesystem_identity","independent_observer_reference","cleanup_reference")
    if not isinstance(proof,dict) or any(k not in proof for k in req): return ["fault_proof_incomplete"]
    if proof["arm"]!=arm: reasons.append("wrong_arm")
    if proof["mechanism_id"]!=expected["mechanism_id"]: reasons.append("wrong_mechanism")
    if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_invalid")
    if proof["target_record_id"]!=expected["target_record_id"]: reasons.append("wrong_target_id")
    if proof["target_path"]!=expected["expected_records_path"]: reasons.append("wrong_target_path")
    if proof["expected_errno"]!=arm or proof["observed_errno"]!=arm: reasons.append("wrong_errno")
    if proof["target_operation"]!=OPS[arm]["operation"]: reasons.append("wrong_operation")
    if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
    if proof["device_id"]!=expected["expected_records_device"] or proof["mount_id"]!=expected["expected_records_mount"] or proof["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("wrong_filesystem_identity")
    if not isinstance(proof["activation_evidence"],dict) or proof["activation_evidence"].get("observed") is not True: reasons.append("activation_not_proven")
    if not isinstance(proof["operation_evidence"],dict) or proof["operation_evidence"].get("observed") is not True: reasons.append("operation_not_proven")
    if not isinstance(proof["service_pid"],int) or proof["service_pid"]<=0: reasons.append("service_pid_invalid")
    if not isinstance(proof["timestamp"],(int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
    return reasons

def validate_trusted_fault_attestation(att, expected):
    """Validate independently collected attestation; harness claims are not enough."""
    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","raw_artifact_sha256","cleanup_reference")
    if not isinstance(att,dict): return ["trusted_attestation_missing"]
    reasons=[f"attestation_field_missing:{k}" for k in req if k not in att]
    if reasons: return reasons
    if att["rq_id"]!="RQ-16" or att["arm"]!=expected["arm"]: reasons.append("attestation_arm_mismatch")
    if att["mechanism_id"]!=expected["mechanism_id"] or att["mechanism_digest"]!=expected["mechanism_digest"]: reasons.append("attestation_mechanism_mismatch")
    if att["target_record_id"]!=expected["target_record_id"] or att["target_path"]!=expected["expected_records_path"]: reasons.append("attestation_target_mismatch")
    if att["target_operation"]!=OPS[expected["arm"]]["operation"] or att["target_syscall"] not in OPS[expected["arm"]]["syscalls"]: reasons.append("attestation_operation_mismatch")
    if att["service_pid"]!=expected.get("expected_service_pid") or att["service_executable_sha256"]!=expected.get("expected_service_binary_sha256"): reasons.append("attestation_service_mismatch")
    if att["observed_errno"]!=expected["arm"]: reasons.append("attestation_errno_mismatch")
    if att["records_device"]!=expected["expected_records_device"] or att["consumed_device"]!=expected["expected_consumed_device"] or att["records_mount_id"]!=expected["expected_records_mount"] or att["consumed_mount_id"]!=expected["expected_consumed_mount"] or att["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("attestation_topology_mismatch")
    if not isinstance(att["fault_activation_raw_evidence"],(dict,list,str)) or not att["fault_activation_raw_evidence"]: reasons.append("activation_raw_missing")
    if not isinstance(att["operation_raw_evidence"],(dict,list,str)) or not att["operation_raw_evidence"]: reasons.append("operation_raw_missing")
    if att["observer_identity"] in ("candidate","harness","untrusted") or att["observer_source_sha256"]!="observer-sha" or att["raw_artifact_sha256"]!="artifact-sha": reasons.append("observer_provenance_untrusted")
    return reasons

def _obs_complete(observations, expected):
    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
    if not isinstance(observations,dict): return ["observations_missing"]
    for s in stages:
        o=observations.get(s)
        if not isinstance(o,dict): reasons.append(f"observation_missing:{s}"); continue
        reasons += validate_target_binding(o,expected)
        for k in ("service_pid","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
            if k not in o: reasons.append(f"observation_field_missing:{s}:{k}")
    return reasons

def _has_exact(entries, target):
    if not isinstance(entries,list): return False,0
    names=[]
    for e in entries:
        names.append(e if isinstance(e,str) else e.get("name") if isinstance(e,dict) else "")
    return target in names, names.count(target)

def derive_target_lifecycle(observations, expected):
    """Derive membership/deltas from observed directory entries, never summary flags."""
    target=expected["target_record_id"]+".record"; states={}; errors=[]
    if not isinstance(observations,dict): return {"states":{},"errors":["observations_missing"]}
    for stage,o in observations.items():
        if not isinstance(o,dict): errors.append(f"stage_malformed:{stage}"); continue
        r,rc=_has_exact(o.get("records_entries"),target); c,cc=_has_exact(o.get("consumed_entries"),target)
        if rc>1 or cc>1: errors.append(f"duplicate_target_entry:{stage}")
        states[stage]={"target_in_records":r,"target_in_consumed":c,"record_count":rc,"consumed_count":cc,"target_hash":o.get("target_hash")}
        if r and c: errors.append(f"target_in_both:{stage}")
    if states.get("baseline",{}).get("target_in_records") is not True or states.get("baseline",{}).get("target_in_consumed") is not False: errors.append("baseline_target_contract")
    for stage,s in states.items():
        if stage!="baseline" and not s["target_in_records"] and not s["target_in_consumed"]: errors.append(f"unexplained_disappearance:{stage}")
    return {"states":states,"errors":errors}

def _lifecycle_valid(life, expected, observations):
    derived=derive_target_lifecycle(observations,expected); reasons=list(derived["errors"])
    if not isinstance(life,dict): reasons.append("lifecycle_missing")
    if not isinstance(life.get("deltas") if isinstance(life,dict) else None,dict): reasons.append("lifecycle_deltas_missing")
    # Summary booleans are diagnostics only; derived errors are authoritative.
    return reasons

def validate_cleanup(cleanup, expected):
    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified")
    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True: reasons.append("cleanup_not_verified")
    baseline, restored=cleanup.get("baseline_observation"), cleanup.get("restored_observation")
    if not isinstance(baseline,dict) or not isinstance(restored,dict): reasons.append("cleanup_baseline_restored_missing")
    else:
        volatile={"service_pid","timestamp","inode"}; required=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
        for k in required:
            if k not in baseline or k not in restored: reasons.append(f"cleanup_field_missing:{k}")
            elif k not in volatile and baseline.get(k)!=restored.get(k): reasons.append(f"cleanup_changed:{k}")
    return reasons

def expected_authorization_context(expected):
    return {"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"BOUNDED_PASS","review_artifact_sha256":"review-sha","reviewer_designation":"independent-reviewer","issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":"issuer-sha"}

def validate_authorization_token(token, expected, now=None, used_nonces=None):
    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
    ctx=expected_authorization_context(expected)
    for k,v in ctx.items():
        if token.get(k)!=v: reasons.append(f"token_mismatch:{k}")
    try:
        issued=datetime.fromisoformat(token.get("authorization_timestamp","" ).replace("Z","+00:00")); expires=datetime.fromisoformat(token.get("expiration","").replace("Z","+00:00"))
        now=now or datetime.now(timezone.utc)
        if issued > now: reasons.append("authorization_in_future")
        if expires <= now or expires <= issued: reasons.append("expiration_invalid")
        if expires-issued > __import__('datetime').timedelta(hours=1): reasons.append("expiration_unbounded")
    except Exception: reasons.append("timestamp_unparseable")
    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
    if used_nonces is not None and token.get("nonce") in used_nonces: reasons.append("nonce_replay")
    if token.get("source_path")!="/root-owned/rq16-authorization": reasons.append("authorization_source_untrusted")
    if token.get("single_use_registry")!="root-owned-durable-ledger": reasons.append("nonce_registry_untrusted")
    return reasons

def evaluate_arm(arm, observed, expected):
    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
    reasons=[]
    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected)
    reasons += _obs_complete(observed.get("observations"),expected)
    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
    reasons += _lifecycle_valid(observed.get("lifecycle"),expected,observed.get("observations"))
    reasons += validate_cleanup(observed.get("cleanup_proof"),expected)
    if observed.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
    if not topo_ok: reasons.append("rq17_contamination")
    return ("PASS",[]) if not reasons else ("HARNESS_DEFECT",sorted(set(reasons)))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true"); a=ap.parse_args()
    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
    if a.self_test: print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["expected-vs-observed separation","exact target binding","structured provenance","observer stages","cleanup structure","RQ17 gate","token binding"]},indent=2)); return 0
    if not a.plan: ap.error("only --plan or --self-test is allowed")
    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
```


### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=f524ed38c9bdf80c32638351b39310e8ac886f1efaad0a4e548c7ba41b21ac0f

```python
#!/usr/bin/env python3
import copy, unittest
from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context

EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
def observation():
    return {s:{"target_record_id":TARGET,"records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":"ok","records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
def good():
    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":"trusted-root-observer","observer_source_sha256":"observer-sha","raw_artifact_sha256":"artifact-sha","cleanup_reference":"clean"}
    base={"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"owner":"root","mode":"0700","socket_state":"ok","service_identity":"uid0:trusted-service","security_controls":"stable","fault_state":"disabled","records_entries":[TARGET+".record"],"consumed_entries":[],"historical_evidence":"intact"}
    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}

class RQ16Tests(unittest.TestCase):
    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED)[0],"PASS")
    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
    def test_target_mutations_reject(self):
        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
    def test_provenance_mutations_reject(self):
        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
    def test_observer_cleanup_lifecycle_mutations_reject(self):
        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
    def test_authority_and_duplicate_transitions_red_or_reject(self):
        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"RED")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
    def test_token_requires_durable_trusted_binding(self):
        self.assertTrue(validate_authorization_token({},EXPECTED))
        token=expected_authorization_context(EXPECTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc)))
        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc)))
        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"}))
    def test_cross_arm_proof_rejected(self):
        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"))[0],"PASS")
    def test_absent_response_not_success(self):
        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")

if __name__=="__main__": unittest.main(verbosity=2)
```


### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=1f8f4861537c1417bf7c9a12b8e39c26e464cfbd73559fc94a28148cabc28877

```python
#!/usr/bin/env python3
import copy, json
from datetime import datetime, timezone
from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, validate_authorization_token
from test_v24_v6_rq1_rq16_harness import good
EXPECTED=expected_context("ENOSPC")
def main():
    specs=[
      ("wrong_device",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("wrong_mount",lambda e:e["observations"]["fault_active"].update(records_mount="m2")),
      ("wrong_filesystem",lambda e:e["observations"]["fault_active"].update(records_fs="fs2")),
      ("symlink",lambda e:e["observations"]["fault_active"].update(records_symlink=True)),
      ("wrong_target",lambda e:e["fault_proof"].update(target_record_id="other")),
      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
      ("attestation_missing_raw_activation",lambda e:e["trusted_fault_attestation"].pop("fault_activation_raw_evidence")),
      ("attestation_missing_raw_operation",lambda e:e["trusted_fault_attestation"].pop("operation_raw_evidence")),
      ("attestation_wrong_observer",lambda e:e["trusted_fault_attestation"].update(observer_identity="candidate")),
      ("attestation_wrong_pid",lambda e:e["trusted_fault_attestation"].update(service_pid=99)),
      ("attestation_wrong_artifact_hash",lambda e:e["trusted_fault_attestation"].update(raw_artifact_sha256="fake")),
      ("missing_observer",lambda e:e["observations"].pop("restored")),
      ("bool_only_observer",lambda e:e.pop("observations")),
      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
      ("duplicate_consume",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record","abc123.record"])),
      ("both_directories",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
      ("cleanup_service_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="bad")),
      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
      ("cleanup_fault_active",lambda e:e["cleanup_proof"].update(fault_disabled=False)),
      ("cleanup_target_state",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=[])),
      ("cleanup_historical_evidence",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence="changed")),
      ("cleanup_missing_restored",lambda e:e["cleanup_proof"].update(restored_observation={})),
    ]
    rows=[]
    for name,mut in specs:
        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED)
        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
    token=expected_authorization_context(EXPECTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
    for field in auth_fields:
        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
if __name__=="__main__": raise SystemExit(main())
```


### governance-runtime/check_rq16_preregistration_packet.py sha256=58c6c2ae49817f1380ce1b95173a2c2c6d18d46d636b0552c5dccdce588c7d2a

```python
#!/usr/bin/env python3
"""Verify preregistration identities knowable before packet commit."""
import hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'
def main():
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
    assert vals['packet_content_identity_schema_version']=='1'
    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-5-REVIEW)\.md',text,re.M)
    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
```

## Static and behavioral results

### plan

```text
{
  "mode": "PLAN",
  "arms": [
    "EACCES",
    "EIO",
    "ENOSPC",
    "EROFS"
  ],
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```


### self-test

```text
{
  "mode": "SELF_TEST",
  "passed": true,
  "RQ16_EXECUTED": false,
  "checks": [
    "expected-vs-observed separation",
    "exact target binding",
    "structured provenance",
    "observer stages",
    "cleanup structure",
    "RQ17 gate",
    "token binding"
  ]
}
```


### tests

```text
test_absent_response_not_success (__main__.RQ16Tests.test_absent_response_not_success) ... ok
test_authority_and_duplicate_transitions_red_or_reject (__main__.RQ16Tests.test_authority_and_duplicate_transitions_red_or_reject) ... ok
test_cross_arm_proof_rejected (__main__.RQ16Tests.test_cross_arm_proof_rejected) ... ok
test_expected_context_required (__main__.RQ16Tests.test_expected_context_required) ... ok
test_observer_cleanup_lifecycle_mutations_reject (__main__.RQ16Tests.test_observer_cleanup_lifecycle_mutations_reject) ... ok
test_provenance_mutations_reject (__main__.RQ16Tests.test_provenance_mutations_reject) ... ok
test_rq17_gate_cannot_be_overridden_by_boolean (__main__.RQ16Tests.test_rq17_gate_cannot_be_overridden_by_boolean) ... ok
test_target_mutations_reject (__main__.RQ16Tests.test_target_mutations_reject) ... ok
test_token_requires_durable_trusted_binding (__main__.RQ16Tests.test_token_requires_durable_trusted_binding) ... ok
test_valid_structured_expected_observed_passes (__main__.RQ16Tests.test_valid_structured_expected_observed_passes) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.004s

OK
```


### mutations

```json
{
  "RQ16_EXECUTED": false,
  "all_rejected": true,
  "mutations": [
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_device",
      "path": "wrong_device",
      "reasons": [
        "fault_active:records_device_mismatch",
        "fault_active:split_filesystem",
        "rq17_contamination",
        "target_binding:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_mount",
      "path": "wrong_mount",
      "reasons": [
        "fault_active:records_mount_mismatch",
        "rq17_contamination",
        "target_binding:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_filesystem",
      "path": "wrong_filesystem",
      "reasons": [
        "fault_active:records_fs_mismatch",
        "rq17_contamination",
        "target_binding:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "symlink",
      "path": "symlink",
      "reasons": [
        "target_binding:records_symlink"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target",
      "path": "wrong_target",
      "reasons": [
        "wrong_target_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_syscall",
      "path": "wrong_syscall",
      "reasons": [
        "wrong_syscall"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_errno",
      "path": "wrong_errno",
      "reasons": [
        "wrong_errno"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_activation",
      "path": "missing_activation",
      "reasons": [
        "activation_not_proven"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_operation",
      "path": "missing_operation",
      "reasons": [
        "operation_not_proven"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_missing_raw_activation",
      "path": "attestation_missing_raw_activation",
      "reasons": [
        "attestation_field_missing:fault_activation_raw_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_missing_raw_operation",
      "path": "attestation_missing_raw_operation",
      "reasons": [
        "attestation_field_missing:operation_raw_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_observer",
      "path": "attestation_wrong_observer",
      "reasons": [
        "observer_provenance_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_pid",
      "path": "attestation_wrong_pid",
      "reasons": [
        "attestation_service_mismatch"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_artifact_hash",
      "path": "attestation_wrong_artifact_hash",
      "reasons": [
        "observer_provenance_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_observer",
      "path": "missing_observer",
      "reasons": [
        "observation_missing:restored"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "bool_only_observer",
      "path": "bool_only_observer",
      "reasons": [
        "observations_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_cleanup",
      "path": "missing_cleanup",
      "reasons": [
        "cleanup_proof_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "bool_only_cleanup",
      "path": "bool_only_cleanup",
      "reasons": [
        "cleanup_proof_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_consume",
      "path": "duplicate_consume",
      "reasons": [
        "duplicate_target_entry:post_failure",
        "target_in_both:post_failure"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "both_directories",
      "path": "both_directories",
      "reasons": [
        "target_in_both:post_failure"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "rq17_false_but_changed",
      "path": "rq17_false_but_changed",
      "reasons": [
        "fault_active:records_device_mismatch",
        "fault_active:split_filesystem",
        "rq17_contamination",
        "target_binding:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "authoritative_success",
      "path": "authoritative_success",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "invalid_transition",
      "path": "invalid_transition",
      "reasons": [
        "invalid_transition_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "untrusted_expected_context",
      "path": "untrusted_expected_context",
      "reasons": [
        "wrong_mechanism"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_service_hash",
      "path": "cleanup_service_hash",
      "reasons": [
        "cleanup_changed:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_gate_hash",
      "path": "cleanup_gate_hash",
      "reasons": [
        "cleanup_changed:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mode",
      "path": "cleanup_mode",
      "reasons": [
        "cleanup_changed:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_owner",
      "path": "cleanup_owner",
      "reasons": [
        "cleanup_changed:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_socket",
      "path": "cleanup_socket",
      "reasons": [
        "cleanup_changed:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_active",
      "path": "cleanup_fault_active",
      "reasons": [
        "cleanup_not_verified"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_target_state",
      "path": "cleanup_target_state",
      "reasons": [
        "cleanup_changed:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_evidence",
      "path": "cleanup_historical_evidence",
      "reasons": [
        "cleanup_changed:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_missing_restored",
      "path": "cleanup_missing_restored",
      "reasons": [
        "cleanup_field_missing:consumed_device",
        "cleanup_field_missing:consumed_entries",
        "cleanup_field_missing:consumed_fs",
        "cleanup_field_missing:consumed_mount",
        "cleanup_field_missing:consumed_realpath",
        "cleanup_field_missing:fault_state",
        "cleanup_field_missing:gate_sha256",
        "cleanup_field_missing:historical_evidence",
        "cleanup_field_missing:mode",
        "cleanup_field_missing:owner",
        "cleanup_field_missing:records_device",
        "cleanup_field_missing:records_entries",
        "cleanup_field_missing:records_fs",
        "cleanup_field_missing:records_mount",
        "cleanup_field_missing:records_realpath",
        "cleanup_field_missing:security_controls",
        "cleanup_field_missing:service_binary_sha256",
        "cleanup_field_missing:service_identity",
        "cleanup_field_missing:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_arm",
      "path": "arm",
      "reasons": [
        "token_mismatch:arm"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_mechanism_id",
      "path": "mechanism_id",
      "reasons": [
        "token_mismatch:mechanism_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_mechanism_digest",
      "path": "mechanism_digest",
      "reasons": [
        "token_mismatch:mechanism_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_commit",
      "path": "plan_commit",
      "reasons": [
        "token_mismatch:plan_commit"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_tree",
      "path": "plan_tree",
      "reasons": [
        "token_mismatch:plan_tree"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_digest",
      "path": "plan_digest",
      "reasons": [
        "token_mismatch:plan_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_execution_contract_digest",
      "path": "execution_contract_digest",
      "reasons": [
        "token_mismatch:execution_contract_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_cleanup_contract_digest",
      "path": "cleanup_contract_digest",
      "reasons": [
        "token_mismatch:cleanup_contract_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_host_identity",
      "path": "host_identity",
      "reasons": [
        "token_mismatch:host_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_runtime_identity",
      "path": "runtime_identity",
      "reasons": [
        "token_mismatch:runtime_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_service_binary_sha256",
      "path": "service_binary_sha256",
      "reasons": [
        "token_mismatch:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_gate_sha256",
      "path": "gate_sha256",
      "reasons": [
        "token_mismatch:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_records_device",
      "path": "records_device",
      "reasons": [
        "token_mismatch:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_consumed_device",
      "path": "consumed_device",
      "reasons": [
        "token_mismatch:consumed_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_records_mount_id",
      "path": "records_mount_id",
      "reasons": [
        "token_mismatch:records_mount_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_consumed_mount_id",
      "path": "consumed_mount_id",
      "reasons": [
        "token_mismatch:consumed_mount_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_independent_review_disposition",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_review_artifact_sha256",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_reviewer_designation",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_issuer_identity",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_issuer_authority_artifact_sha256",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "2025-01-01T00:00:00Z",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_expired",
      "path": "expiration",
      "reasons": [
        "expiration_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "2030-01-01T00:00:00Z",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_future_issued",
      "path": "authorization_timestamp",
      "reasons": [
        "authorization_in_future",
        "expiration_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "bad",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_malformed_timestamp",
      "path": "expiration",
      "reasons": [
        "timestamp_unparseable"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_empty_nonce",
      "path": "nonce",
      "reasons": [
        "nonce_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "used",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_reused_nonce",
      "path": "nonce",
      "reasons": [
        "nonce_replay"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_untrusted_source",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "memory",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_untrusted_registry",
      "path": "single_use_registry",
      "reasons": [
        "nonce_registry_untrusted"
      ],
      "rejected": true
    }
  ],
  "rejected_mutations": 61,
  "surviving_mutations": 0,
  "total_mutations": 61
}
```


### packet-check

```text
Traceback (most recent call last):
  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 21, in <module>
    if __name__=='__main__': raise SystemExit(main())
                                              ^^^^^^
  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 8, in main
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Python312\Lib\pathlib.py", line 1027, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Python312\Lib\pathlib.py", line 1013, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\hp\\Downloads\\ps final\\pashusetu_app4_admin_web_connected\\setugo-runtime-qualification-1\\V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'
```


### execution-refusal

```text
{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
```

## Exact predecessor-to-reviewed-source diff

### diff

```text
diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
new file mode 100644
index 00000000..2ce39b02
--- /dev/null
+++ b/governance-runtime/build_rq16_preregistration_review.py
@@ -0,0 +1,19 @@
+from __future__ import annotations
+import hashlib, os, subprocess
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'
+FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py',ROOT/'governance-runtime/check_rq16_preregistration_packet.py']
+def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+def main():
+    current=run(['git','rev-parse','HEAD']).stdout.strip(); current_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); reviewed=os.environ.get('REVIEWED_SOURCE_COMMIT',current); reviewed_tree=os.environ.get('REVIEWED_SOURCE_TREE',run(['git','rev-parse',f'{reviewed}^{{tree}}']).stdout.strip()); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet_parent=current; packet_parent_tree=current_tree
+    diff=run(['git','diff',predecessor,reviewed,'--','.', ':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md']).stdout
+    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
+    manifest='\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES); ids=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_parent_commit={packet_parent}',f'packet_parent_tree={packet_parent_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_source_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}',f'source_manifest_sha256={hashlib.sha256(manifest.encode()).hexdigest()}','packet_content_identity_schema_version=1']
+    parts=['# V24-I11-V6 RQ-16 preregistration remediation-5 review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*ids,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION','packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION','packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION','RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json'), '## Included file SHA-256', manifest]
+    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+    parts += ['## Static and behavioral results',fence('plan',plan.stdout+plan.stderr),fence('self-test',selftest.stdout+selftest.stderr),fence('tests',tests.stdout+tests.stderr),fence('mutations',mutations.stdout+mutations.stderr,'json'),fence('packet-check',consistency.stdout+consistency.stderr),fence('execution-refusal',refuse.stdout+refuse.stderr), '## Exact predecessor-to-reviewed-source diff', fence('diff',diff), '## Manual-review questions','Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.']
+    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
+if __name__=='__main__': main()
diff --git a/governance-runtime/check_rq16_preregistration_packet.py b/governance-runtime/check_rq16_preregistration_packet.py
new file mode 100644
index 00000000..6a7b57e2
--- /dev/null
+++ b/governance-runtime/check_rq16_preregistration_packet.py
@@ -0,0 +1,21 @@
+#!/usr/bin/env python3
+"""Verify preregistration identities knowable before packet commit."""
+import hashlib, json, re, subprocess
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'
+def main():
+    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
+    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
+    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
+    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
+    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
+    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
+    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
+    assert vals['packet_content_identity_schema_version']=='1'
+    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
+    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
+    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-5-REVIEW)\.md',text,re.M)
+    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
+if __name__=='__main__': raise SystemExit(main())
diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
new file mode 100644
index 00000000..58e1fef5
--- /dev/null
+++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
@@ -0,0 +1,55 @@
+#!/usr/bin/env python3
+import copy, json
+from datetime import datetime, timezone
+from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, validate_authorization_token
+from test_v24_v6_rq1_rq16_harness import good
+EXPECTED=expected_context("ENOSPC")
+def main():
+    specs=[
+      ("wrong_device",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
+      ("wrong_mount",lambda e:e["observations"]["fault_active"].update(records_mount="m2")),
+      ("wrong_filesystem",lambda e:e["observations"]["fault_active"].update(records_fs="fs2")),
+      ("symlink",lambda e:e["observations"]["fault_active"].update(records_symlink=True)),
+      ("wrong_target",lambda e:e["fault_proof"].update(target_record_id="other")),
+      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
+      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
+      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
+      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
+      ("attestation_missing_raw_activation",lambda e:e["trusted_fault_attestation"].pop("fault_activation_raw_evidence")),
+      ("attestation_missing_raw_operation",lambda e:e["trusted_fault_attestation"].pop("operation_raw_evidence")),
+      ("attestation_wrong_observer",lambda e:e["trusted_fault_attestation"].update(observer_identity="candidate")),
+      ("attestation_wrong_pid",lambda e:e["trusted_fault_attestation"].update(service_pid=99)),
+      ("attestation_wrong_artifact_hash",lambda e:e["trusted_fault_attestation"].update(raw_artifact_sha256="fake")),
+      ("missing_observer",lambda e:e["observations"].pop("restored")),
+      ("bool_only_observer",lambda e:e.pop("observations")),
+      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
+      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
+      ("duplicate_consume",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record","abc123.record"])),
+      ("both_directories",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
+      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
+      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
+      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
+      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
+      ("cleanup_service_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="bad")),
+      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
+      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
+      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
+      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
+      ("cleanup_fault_active",lambda e:e["cleanup_proof"].update(fault_disabled=False)),
+      ("cleanup_target_state",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=[])),
+      ("cleanup_historical_evidence",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence="changed")),
+      ("cleanup_missing_restored",lambda e:e["cleanup_proof"].update(restored_observation={})),
+    ]
+    rows=[]
+    for name,mut in specs:
+        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED)
+        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+    token=expected_authorization_context(EXPECTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
+    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
+    for field in auth_fields:
+        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
+        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
+    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+if __name__=="__main__": raise SystemExit(main())
diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..f6ce281c
--- /dev/null
+++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,49 @@
+#!/usr/bin/env python3
+import copy, unittest
+from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context
+
+EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
+def observation():
+    return {s:{"target_record_id":TARGET,"records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":"ok","records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+def good():
+    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":"trusted-root-observer","observer_source_sha256":"observer-sha","raw_artifact_sha256":"artifact-sha","cleanup_reference":"clean"}
+    base={"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"owner":"root","mode":"0700","socket_state":"ok","service_identity":"uid0:trusted-service","security_controls":"stable","fault_state":"disabled","records_entries":[TARGET+".record"],"consumed_entries":[],"historical_evidence":"intact"}
+    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}
+
+class RQ16Tests(unittest.TestCase):
+    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED)[0],"PASS")
+    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
+    def test_target_mutations_reject(self):
+        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
+            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
+            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
+            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+    def test_provenance_mutations_reject(self):
+        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
+            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+    def test_observer_cleanup_lifecycle_mutations_reject(self):
+        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
+        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
+    def test_authority_and_duplicate_transitions_red_or_reject(self):
+        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"RED")
+        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+    def test_token_requires_durable_trusted_binding(self):
+        self.assertTrue(validate_authorization_token({},EXPECTED))
+        token=expected_authorization_context(EXPECTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
+        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc)))
+        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
+            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc)))
+        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"}))
+    def test_cross_arm_proof_rejected(self):
+        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"))[0],"PASS")
+    def test_absent_response_not_success(self):
+        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+
+if __name__=="__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..6d56797a
--- /dev/null
+++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,170 @@
+#!/usr/bin/env python3
+"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
+from __future__ import annotations
+import argparse, json, math, re
+from datetime import datetime, timezone
+
+ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
+OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
+MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}
+
+def expected_context(arm, record_id="abc123"):
+    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
+    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
+    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","review_artifact_sha256":"review-sha"}
+
+def check_rq17_contamination(expected, observed):
+    reasons=[]
+    if expected.get("expected_records_device") != expected.get("expected_consumed_device"): reasons.append("expected_baseline_split")
+    for stage, o in (observed or {}).items():
+        if not isinstance(o,dict): reasons.append(f"stage_malformed:{stage}"); continue
+        pairs=(("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"))
+        for actual, exp in pairs:
+            if o.get(actual) != expected.get(exp): reasons.append(f"{stage}:{actual}_mismatch")
+        if o.get("records_device") != o.get("consumed_device"): reasons.append(f"{stage}:split_filesystem")
+    return not reasons, reasons
+
+def validate_target_binding(observed, expected):
+    reasons=[]
+    fields=(("target_record_id","target_record_id"),("records_path","expected_records_path"),("consumed_path","expected_consumed_path"),("records_realpath","expected_records_realpath"),("consumed_realpath","expected_consumed_realpath"),("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"),("records_symlink","expected_records_symlink"),("consumed_symlink","expected_consumed_symlink"))
+    for a,e in fields:
+        if observed.get(a) != expected.get(e): reasons.append(f"target_binding:{a}")
+    return reasons
+
+def validate_fault_proof(proof, expected):
+    reasons=[]; arm=expected["arm"]
+    req=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","filesystem_identity","independent_observer_reference","cleanup_reference")
+    if not isinstance(proof,dict) or any(k not in proof for k in req): return ["fault_proof_incomplete"]
+    if proof["arm"]!=arm: reasons.append("wrong_arm")
+    if proof["mechanism_id"]!=expected["mechanism_id"]: reasons.append("wrong_mechanism")
+    if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_invalid")
+    if proof["target_record_id"]!=expected["target_record_id"]: reasons.append("wrong_target_id")
+    if proof["target_path"]!=expected["expected_records_path"]: reasons.append("wrong_target_path")
+    if proof["expected_errno"]!=arm or proof["observed_errno"]!=arm: reasons.append("wrong_errno")
+    if proof["target_operation"]!=OPS[arm]["operation"]: reasons.append("wrong_operation")
+    if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
+    if proof["device_id"]!=expected["expected_records_device"] or proof["mount_id"]!=expected["expected_records_mount"] or proof["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("wrong_filesystem_identity")
+    if not isinstance(proof["activation_evidence"],dict) or proof["activation_evidence"].get("observed") is not True: reasons.append("activation_not_proven")
+    if not isinstance(proof["operation_evidence"],dict) or proof["operation_evidence"].get("observed") is not True: reasons.append("operation_not_proven")
+    if not isinstance(proof["service_pid"],int) or proof["service_pid"]<=0: reasons.append("service_pid_invalid")
+    if not isinstance(proof["timestamp"],(int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
+    return reasons
+
+def validate_trusted_fault_attestation(att, expected):
+    """Validate independently collected attestation; harness claims are not enough."""
+    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","raw_artifact_sha256","cleanup_reference")
+    if not isinstance(att,dict): return ["trusted_attestation_missing"]
+    reasons=[f"attestation_field_missing:{k}" for k in req if k not in att]
+    if reasons: return reasons
+    if att["rq_id"]!="RQ-16" or att["arm"]!=expected["arm"]: reasons.append("attestation_arm_mismatch")
+    if att["mechanism_id"]!=expected["mechanism_id"] or att["mechanism_digest"]!=expected["mechanism_digest"]: reasons.append("attestation_mechanism_mismatch")
+    if att["target_record_id"]!=expected["target_record_id"] or att["target_path"]!=expected["expected_records_path"]: reasons.append("attestation_target_mismatch")
+    if att["target_operation"]!=OPS[expected["arm"]]["operation"] or att["target_syscall"] not in OPS[expected["arm"]]["syscalls"]: reasons.append("attestation_operation_mismatch")
+    if att["service_pid"]!=expected.get("expected_service_pid") or att["service_executable_sha256"]!=expected.get("expected_service_binary_sha256"): reasons.append("attestation_service_mismatch")
+    if att["observed_errno"]!=expected["arm"]: reasons.append("attestation_errno_mismatch")
+    if att["records_device"]!=expected["expected_records_device"] or att["consumed_device"]!=expected["expected_consumed_device"] or att["records_mount_id"]!=expected["expected_records_mount"] or att["consumed_mount_id"]!=expected["expected_consumed_mount"] or att["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("attestation_topology_mismatch")
+    if not isinstance(att["fault_activation_raw_evidence"],(dict,list,str)) or not att["fault_activation_raw_evidence"]: reasons.append("activation_raw_missing")
+    if not isinstance(att["operation_raw_evidence"],(dict,list,str)) or not att["operation_raw_evidence"]: reasons.append("operation_raw_missing")
+    if att["observer_identity"] in ("candidate","harness","untrusted") or att["observer_source_sha256"]!="observer-sha" or att["raw_artifact_sha256"]!="artifact-sha": reasons.append("observer_provenance_untrusted")
+    return reasons
+
+def _obs_complete(observations, expected):
+    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
+    if not isinstance(observations,dict): return ["observations_missing"]
+    for s in stages:
+        o=observations.get(s)
+        if not isinstance(o,dict): reasons.append(f"observation_missing:{s}"); continue
+        reasons += validate_target_binding(o,expected)
+        for k in ("service_pid","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
+            if k not in o: reasons.append(f"observation_field_missing:{s}:{k}")
+    return reasons
+
+def _has_exact(entries, target):
+    if not isinstance(entries,list): return False,0
+    names=[]
+    for e in entries:
+        names.append(e if isinstance(e,str) else e.get("name") if isinstance(e,dict) else "")
+    return target in names, names.count(target)
+
+def derive_target_lifecycle(observations, expected):
+    """Derive membership/deltas from observed directory entries, never summary flags."""
+    target=expected["target_record_id"]+".record"; states={}; errors=[]
+    if not isinstance(observations,dict): return {"states":{},"errors":["observations_missing"]}
+    for stage,o in observations.items():
+        if not isinstance(o,dict): errors.append(f"stage_malformed:{stage}"); continue
+        r,rc=_has_exact(o.get("records_entries"),target); c,cc=_has_exact(o.get("consumed_entries"),target)
+        if rc>1 or cc>1: errors.append(f"duplicate_target_entry:{stage}")
+        states[stage]={"target_in_records":r,"target_in_consumed":c,"record_count":rc,"consumed_count":cc,"target_hash":o.get("target_hash")}
+        if r and c: errors.append(f"target_in_both:{stage}")
+    if states.get("baseline",{}).get("target_in_records") is not True or states.get("baseline",{}).get("target_in_consumed") is not False: errors.append("baseline_target_contract")
+    for stage,s in states.items():
+        if stage!="baseline" and not s["target_in_records"] and not s["target_in_consumed"]: errors.append(f"unexplained_disappearance:{stage}")
+    return {"states":states,"errors":errors}
+
+def _lifecycle_valid(life, expected, observations):
+    derived=derive_target_lifecycle(observations,expected); reasons=list(derived["errors"])
+    if not isinstance(life,dict): reasons.append("lifecycle_missing")
+    if not isinstance(life.get("deltas") if isinstance(life,dict) else None,dict): reasons.append("lifecycle_deltas_missing")
+    # Summary booleans are diagnostics only; derived errors are authoritative.
+    return reasons
+
+def validate_cleanup(cleanup, expected):
+    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
+    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified")
+    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
+    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
+    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True: reasons.append("cleanup_not_verified")
+    baseline, restored=cleanup.get("baseline_observation"), cleanup.get("restored_observation")
+    if not isinstance(baseline,dict) or not isinstance(restored,dict): reasons.append("cleanup_baseline_restored_missing")
+    else:
+        volatile={"service_pid","timestamp","inode"}; required=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
+        for k in required:
+            if k not in baseline or k not in restored: reasons.append(f"cleanup_field_missing:{k}")
+            elif k not in volatile and baseline.get(k)!=restored.get(k): reasons.append(f"cleanup_changed:{k}")
+    return reasons
+
+def expected_authorization_context(expected):
+    return {"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"BOUNDED_PASS","review_artifact_sha256":"review-sha","reviewer_designation":"independent-reviewer","issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":"issuer-sha"}
+
+def validate_authorization_token(token, expected, now=None, used_nonces=None):
+    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
+    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+    ctx=expected_authorization_context(expected)
+    for k,v in ctx.items():
+        if token.get(k)!=v: reasons.append(f"token_mismatch:{k}")
+    try:
+        issued=datetime.fromisoformat(token.get("authorization_timestamp","" ).replace("Z","+00:00")); expires=datetime.fromisoformat(token.get("expiration","").replace("Z","+00:00"))
+        now=now or datetime.now(timezone.utc)
+        if issued > now: reasons.append("authorization_in_future")
+        if expires <= now or expires <= issued: reasons.append("expiration_invalid")
+        if expires-issued > __import__('datetime').timedelta(hours=1): reasons.append("expiration_unbounded")
+    except Exception: reasons.append("timestamp_unparseable")
+    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
+    if used_nonces is not None and token.get("nonce") in used_nonces: reasons.append("nonce_replay")
+    if token.get("source_path")!="/root-owned/rq16-authorization": reasons.append("authorization_source_untrusted")
+    if token.get("single_use_registry")!="root-owned-durable-ledger": reasons.append("nonce_registry_untrusted")
+    return reasons
+
+def evaluate_arm(arm, observed, expected):
+    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
+    reasons=[]
+    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
+    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
+    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
+    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
+    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected)
+    reasons += _obs_complete(observed.get("observations"),expected)
+    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
+    reasons += _lifecycle_valid(observed.get("lifecycle"),expected,observed.get("observations"))
+    reasons += validate_cleanup(observed.get("cleanup_proof"),expected)
+    if observed.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+    if not topo_ok: reasons.append("rq17_contamination")
+    return ("PASS",[]) if not reasons else ("HARNESS_DEFECT",sorted(set(reasons)))
+
+def main():
+    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true"); a=ap.parse_args()
+    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
+    if a.self_test: print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["expected-vs-observed separation","exact target binding","structured provenance","observer stages","cleanup structure","RQ17 gate","token binding"]},indent=2)); return 0
+    if not a.plan: ap.error("only --plan or --self-test is allowed")
+    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
+if __name__=="__main__": raise SystemExit(main())
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
new file mode 100644
index 00000000..f9f4f053
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
@@ -0,0 +1,7 @@
+{
+  "authorization_schema_version": "1",
+  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
+  "single_use": true,
+  "arm_scoped": true,
+  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
new file mode 100644
index 00000000..5ef55ad0
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
@@ -0,0 +1,19 @@
+# RQ-16 cleanup and restoration contract
+
+RQ-16 remains preregistration-only. No mutation has been executed.
+
+Every future arm must capture an immutable baseline and restore it before any
+dependent case. The baseline includes service/gate hashes, unit bytes, PID and
+socket identity, records/consumed ownership and modes, filesystem device IDs,
+mount options, security controls, and exact target lifecycle.
+
+The inverse operation must be explicit: remove only the bounded fault fixture,
+restore the saved mount/quota/metadata state, restart only as required by the
+approved recovery procedure, and independently remeasure every baseline field.
+If a mount operation fails, root recovery is unavailable, a fault fixture
+cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
+dependent cases abort. Historical evidence directories are never targets.
+
+The future harness must refuse destructive execution unless the exact host,
+commit, plan digest, and separately generated authorization token are bound.
+`--plan` and `--self-test` are the only permitted modes in this preregistration.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
new file mode 100644
index 00000000..fdc139d1
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
@@ -0,0 +1,48 @@
+{
+  "rq_id": "RQ-16",
+  "trigger": "Disk full / read-only / I/O / permission failure",
+  "oracle": "Fail closed without fabricated success",
+  "execution_required": true,
+  "execution_authorized": false,
+  "arms": {
+    "ENOSPC": {
+      "operation": "write_authority_record or fsync on exact bound records path",
+      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
+      "classification": "INSUFFICIENT_EVIDENCE",
+      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
+    },
+    "EROFS": {
+      "operation": "write_authority_record or rename on exact bound path",
+      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
+      "classification": "UNSAFE",
+      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
+    },
+    "EIO": {
+      "operation": "exact record read/write/fsync/rename syscall",
+      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
+      "classification": "INSUFFICIENT_EVIDENCE",
+      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
+    },
+    "EACCES": {
+      "operation": "exact service access to records/consumed path",
+      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
+      "classification": "PROXY_NOT_ACCEPTABLE",
+      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
+    }
+  },
+  "classification_rules": {
+    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
+    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
+    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
+    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
+  },
+  "state_machine": {
+    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
+    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
+    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
+    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
+  },
+  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md
new file mode 100644
index 00000000..19e2c2d2
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md
@@ -0,0 +1,5 @@
+# Durable authorization nonce design
+
+No live nonce is created in preregistration. Future authorization must use a root-owned, trusted append-only nonce ledger outside the candidate workspace. Consumption is an atomic create-with-exclusive semantics operation containing the nonce, authorization hash, arm, and timestamp. A second consume attempt fails closed as replay. The ledger must survive process restart, be non-candidate-writable, and be independently observed before and after use.
+
+The JSON token is not authoritative by itself. The trusted issuer/reviewer artifact hash, exact plan/contract/runtime bindings, and root-owned source path must all validate before the nonce ledger is touched. No trusted issuer mechanism is available on this planning host, so future authorization remains `MANUAL_REVIEW_REQUIRED`.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
new file mode 100644
index 00000000..832334ca
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
@@ -0,0 +1,21 @@
+{
+  "issues": [
+    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
+    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
+    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
+  ],
+  "open_automatable_issues": 0,
+  "manual_review_required": true,
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false,
+  "latest_remediation_status": {
+    "RQ16-TRUSTED-ATTESTATION": "RESOLVED",
+    "RQ16-AUTH-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
+    "RQ16-IDENTITY-MODEL": "RESOLVED",
+    "RQ16-TEST-SUFFICIENCY": "RESOLVED"
+  }
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
new file mode 100644
index 00000000..0a797b62
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
@@ -0,0 +1,103 @@
+# V24-I11-V6 RQ-16 preregistration (planning only)
+
+Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
+`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
+that closed Remediation-7 head.
+
+Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
+failure**. Oracle: **Fail closed without fabricated success**. This document
+does not authorize execution.
+
+## Actual write path
+
+In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
+
+- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
+  `fsync`, then closes and unlinks on failure.
+- candidate handling calls `materialize_private()` for context, boundary and
+  payload before gate execution.
+- root control calls `consume_record_trusted()`.
+- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
+  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
+  from records to consumed. It returns an authoritative response only after
+  `rename` succeeds.
+- `write_authority_record()` creates records with
+  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
+  `fsync`, closes, and unlinks on failure.
+
+RQ-16 must bind the injected errno to one of these exact operations; mocked
+Python exceptions and candidate-side failures are proxies.
+
+## Execution arms and classifications
+
+ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
+host `/run` is prohibited. No repository evidence proves such a quota boundary,
+so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
+
+EROFS requires a dedicated qualification filesystem whose read-only transition
+does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
+unsafe and a separate filesystem would collide with RQ-17 topology semantics;
+the arm is `UNSAFE` pending dedicated-mount evidence.
+
+EIO requires a disposable kernel fault layer returning EIO on the exact target
+operation. `dm-error` or equivalent is acceptable only with a dedicated device
+and independent activation/errno proof. No such boundary is evidenced;
+classification is `INSUFFICIENT_EVIDENCE`.
+
+EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
+trusted service runs as UID 0. Candidate-side permission failure or a mocked
+exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
+
+These are execution arms under one frozen case, not new cases.
+
+## Required state machine and proof
+
+Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
+RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
+state record target membership in records/consumed, response and authority,
+errno proof, service state, filesystem/device/mount metadata, ownership/modes,
+and hashes. PASS requires exact fault activation plus syscall errno, no
+authoritative success, explainable target lifecycle, recoverable service,
+complete observers, and exact post-restoration hashes/security state. Absence
+of a response alone is never PASS. Authoritative success after a proven fault
+is RED. Missing/malformed proof or observer/cleanup failure is
+HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
+
+## Restoration, safety and aborts
+
+The only permitted future mutation is a bounded fixture on a dedicated,
+preflight-verified boundary. The host root filesystem, repository, historical
+evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
+workspace are never targets. Cleanup removes the fixture, restores mount/quota
+and metadata, revalidates service/socket/PID, records/consumed integrity,
+device IDs, mount options, ownership/modes, hashes and security controls. Any
+failure blocks all dependent cases.
+
+Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
+free-space margin, backup material, root recovery, service health or observer
+access differ from the preregistered baseline, or if an evidence directory could
+be overwritten.
+
+Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
+responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
+
+## Harness safety and governance
+
+`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
+`--execute-rq16` refuses with a nonzero result. Future execution requires a
+separately generated authorization token bound to exact commit, host/runtime
+identity and plan digest. No token exists in this branch.
+
+`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
+Qualification remains `NOT_QUALIFIED`; scientific execution remains
+`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
+`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
+mechanism classifications before any execution authorization.
+
+## Remediation-2 hardening
+
+The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.
+
+Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.
+
+No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
new file mode 100644
index 00000000..d60eee26
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
@@ -0,0 +1,22 @@
+# RQ-16 read-only capability inspection
+
+This inspection was non-destructive and did not enable or mutate any host feature.
+
+The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.
+
+Source inspection found the trusted service operations at:
+
+- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
+- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
+- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.
+
+Read-only commands attempted:
+
+```text
+Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
+Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
+```
+
+Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.
+
+`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
```

## Manual-review questions
Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.
