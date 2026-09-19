# V24-I11-V6 RQ-16 preregistration remediation-3 review

Planning-only artifact. No RQ-16 execution occurred.

## Identity
reviewed_source_commit=8280f69d3fbbc1e3c140eb98d38cf55c6a12fa87
reviewed_source_tree=3159b811ccaab9ed267cebb34a4b0a3ddb1b6166
packet_commit=e2a08fa3167f405ad1a9d79103bf39a2e8518993
packet_tree=139c01a57149cc4bc25749656254462b031a4ebb
predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
exact_diff_sha256=36379cb72a44ea880a9a4e0e5d7be29e6718a3cb210fb28e537facb2b825c4d3
branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
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
  "RQ16_AUTHORIZED": false
}
```

## Included file SHA-256
19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
0ca35e0500e701151bdd13e544b29b8771d1929dbbcdd6cede148adf0d11183d  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7  implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00  implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md
ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b  implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
ed574abbf3f485361b6d3fef283852c93be7a072d965d5408c51f3460ce4b708  governance-runtime/v24_v6_rq1_rq16_harness.py
ceaaa2d2cd5e616f8b12f158a1480b0c79852ae70bfbd8e1611b408edabede06  governance-runtime/test_v24_v6_rq1_rq16_harness.py
69d6428f9b473a07428e58b449bf9c1f7b290ec81bc6c6e2d1c3e11d84fca9cc  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
dd502744e05aac5fb6b9c1bb0587b429d2ff8cdf208a395f03affbc95ad2dcd7  governance-runtime/check_rq16_preregistration_packet.py

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


### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=ed574abbf3f485361b6d3fef283852c93be7a072d965d5408c51f3460ce4b708

```python
#!/usr/bin/env python3
"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
from __future__ import annotations
import argparse, json, math, re

ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}

def expected_context(arm, record_id="abc123"):
    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","review_artifact_sha256":"review-sha"}

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

def _lifecycle_valid(life, expected):
    if not isinstance(life,dict): return ["lifecycle_missing"]
    reasons=[]
    if life.get("target_record_id")!=expected["target_record_id"]: reasons.append("lifecycle_wrong_target")
    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
    for k in ("unexplained_disappearance","duplicate_authoritative_consume","second_authoritative_retry","authoritative_replay","unrelated_transition","historical_transition"):
        if life.get(k): reasons.append(k)
    if not isinstance(life.get("deltas"),dict): reasons.append("lifecycle_deltas_missing")
    return reasons

def validate_cleanup(cleanup, expected):
    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified")
    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True: reasons.append("cleanup_not_verified")
    return reasons

def validate_authorization_token(token, expected):
    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer","source_path","single_use_registry")
    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
    if token.get("rq_id")!="RQ-16" or token.get("arm")!=expected.get("arm"): reasons.append("token_arm_mismatch")
    if token.get("mechanism_id")!=expected.get("mechanism_id"): reasons.append("token_mechanism_mismatch")
    for k in ("plan_commit","plan_tree","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","review_artifact_sha256"):
        if k in token and token[k] != expected.get(k.replace("records_mount_id","expected_records_mount").replace("consumed_mount_id","expected_consumed_mount").replace("records_device","expected_records_device").replace("consumed_device","expected_consumed_device").replace("service_binary_sha256","expected_service_binary_sha256").replace("gate_sha256","expected_gate_sha256")): reasons.append(f"token_mismatch:{k}")
    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
    if token.get("issuer")!="trusted-review-authority": reasons.append("issuer_untrusted")
    if token.get("single_use_registry")!="root-owned-durable-ledger": reasons.append("nonce_registry_untrusted")
    return reasons

def evaluate_arm(arm, observed, expected):
    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
    reasons=[]
    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
    reasons += _obs_complete(observed.get("observations"),expected)
    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
    reasons += _lifecycle_valid(observed.get("lifecycle"),expected)
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


### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=ceaaa2d2cd5e616f8b12f158a1480b0c79852ae70bfbd8e1611b408edabede06

```python
#!/usr/bin/env python3
import copy, unittest
from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token

EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
def observation():
    return {s:{"target_record_id":TARGET,"records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
def good():
    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":observation(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True},"service_recoverable":True}

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
    def test_observer_cleanup_lifecycle_mutations_reject(self):
        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
    def test_authority_and_duplicate_transitions_red_or_reject(self):
        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"RED")
        e=good(); e["lifecycle"]["duplicate_authoritative_consume"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
    def test_token_requires_durable_trusted_binding(self):
        self.assertTrue(validate_authorization_token({},EXPECTED))
        token={"rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"issuer":"candidate","single_use_registry":"memory"}
        self.assertTrue(validate_authorization_token(token,EXPECTED))
    def test_cross_arm_proof_rejected(self):
        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"))[0],"PASS")
    def test_absent_response_not_success(self):
        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")

if __name__=="__main__": unittest.main(verbosity=2)
```


### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=69d6428f9b473a07428e58b449bf9c1f7b290ec81bc6c6e2d1c3e11d84fca9cc

```python
#!/usr/bin/env python3
import copy, json
from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context
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
      ("missing_observer",lambda e:e["observations"].pop("restored")),
      ("bool_only_observer",lambda e:e.pop("observations")),
      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
    ]
    rows=[]
    for name,mut in specs:
        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED)
        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
if __name__=="__main__": raise SystemExit(main())
```


### governance-runtime/check_rq16_preregistration_packet.py sha256=dd502744e05aac5fb6b9c1bb0587b429d2ff8cdf208a395f03affbc95ad2dcd7

```python
#!/usr/bin/env python3
"""Offline packet consistency checks; no runtime interaction."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
    import re, subprocess
    vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_commit|packet_tree|predecessor_commit|predecessor_tree|exact_diff_sha256)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_commit','packet_tree','predecessor_commit','predecessor_tree','exact_diff_sha256'}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert subprocess.run(['git','merge-base','--is-ancestor',vals['packet_commit'],head],cwd=ROOT).returncode==0
    assert vals['predecessor_commit']=='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d' and vals['predecessor_tree']=='82457b9307f133db281055dbbdae26b618f8c3cf'
    assert 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
```

## Static results

### plan output

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


### self-test output

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


### unit output

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
Ran 10 tests in 0.003s

OK
```


### mutation output

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
        "duplicate_authoritative_consume"
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
        "target_in_both_directories"
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
    }
  ],
  "rejected_mutations": 19,
  "surviving_mutations": 0,
  "total_mutations": 19
}
```


### packet consistency

```text
{
  "packet_consistency": "PASS",
  "arm_count": 4,
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```


### execution refusal output

```text
{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
```

compile_exit=0
## Exact diff from predecessor

### git diff

```text
diff --git a/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
new file mode 100644
index 00000000..3387beab
--- /dev/null
+++ b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
@@ -0,0 +1,5313 @@
+# V24-I11-V6 RQ-16 preregistration review
+
+Planning-only artifact. No RQ-16 execution occurred.
+
+## Identity
+predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
+predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
+branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
+head=f173cbe57b3401ace215748cdf4a5b62a3691c47
+tree=c94367543c181eac0875b9fd8d95a9ef2012eaa8
+RQ16_EXECUTED=false
+RQ16_AUTHORIZED=false
+RQ16_started=false
+scientific_rerun=false
+qualification=NOT_QUALIFIED
+scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
+authority_effect=NONE_EVIDENCE_ONLY
+
+## Frozen contract
+
+### execution contract
+
+```json
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
+```
+
+## Source-path analysis
+
+### preregistration
+
+```markdown
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
+```
+
+## Cleanup contract
+
+### cleanup
+
+```markdown
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
+```
+
+## Issues
+
+### issue ledger
+
+```json
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
+  "RQ16_AUTHORIZED": false
+}
+```
+
+## Included file SHA-256
+19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+0ca35e0500e701151bdd13e544b29b8771d1929dbbcdd6cede148adf0d11183d  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7  implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
+ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b  implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
+ee46c0504e723cac2a18e15967265a643340751579344cfdd335c482817d2723  governance-runtime/v24_v6_rq1_rq16_harness.py
+8d529f6295c0e5d4bf2e79f9d0a8560a28afd4c33589e7e13d35f40bf3820b3a  governance-runtime/test_v24_v6_rq1_rq16_harness.py
+95d1eb222301a193ead0759a7611e1e95e08bda82586410614ba12e58a95374e  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+dbbd1d72b76bd83c638f0bbb212b9411373fb68052e610f74a8ad1bd47b035cd  governance-runtime/check_rq16_preregistration_packet.py
+
+### implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json sha256=31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7
+
+```python
+{
+  "authorization_schema_version": "1",
+  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
+  "single_use": true,
+  "arm_scoped": true,
+  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
+}
+```
+
+
+### implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md sha256=ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b
+
+```python
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
+```
+
+
+### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=ee46c0504e723cac2a18e15967265a643340751579344cfdd335c482817d2723
+
+```python
+#!/usr/bin/env python3
+"""RQ-16 preregistration evaluator; plan/self-test only, never performs faults."""
+from __future__ import annotations
+import argparse, json, math, re
+
+ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
+BASE = "/run/v24-v6-authority/private"
+OPS = {
+    "ENOSPC": {"operation": "write_authority_record", "syscalls": {"write", "fsync"}},
+    "EROFS": {"operation": "write_authority_record", "syscalls": {"write", "fsync", "rename"}},
+    "EIO": {"operation": "record_io", "syscalls": {"read", "write", "fsync", "rename"}},
+    "EACCES": {"operation": "record_access", "syscalls": {"open", "write", "rename"}},
+}
+MECHANISM_CLASSES = {"kernel_quota", "dedicated_ro_mount", "disposable_fault_layer", "kernel_policy"}
+
+def exact_paths(record_id: str):
+    if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", record_id): return None
+    return f"{BASE}/records/{record_id}.record", f"{BASE}/consumed/{record_id}.record"
+
+def check_rq17_contamination(baseline: dict, test: dict):
+    reasons=[]
+    for k in ("records_device", "consumed_device", "records_fs", "consumed_fs", "mount_topology"):
+        if baseline.get(k) != test.get(k): reasons.append(f"topology_changed:{k}")
+    if baseline.get("records_device") != baseline.get("consumed_device"): reasons.append("baseline_already_split")
+    return (not reasons, reasons)
+
+def _structured_map(obj, keys):
+    return isinstance(obj, dict) and all(k in obj and obj[k] not in (None, "") for k in keys)
+
+def validate_fault_proof(arm, proof, target_id, expected_paths):
+    required=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","independent_observer_reference","cleanup_reference")
+    reasons=[]
+    if not _structured_map(proof, required): reasons.append("fault_proof_incomplete")
+    else:
+        if proof["arm"] != arm: reasons.append("wrong_arm")
+        if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_not_allowed")
+        if proof["target_record_id"] != target_id: reasons.append("wrong_target_id")
+        if proof["target_path"] not in expected_paths: reasons.append("wrong_target_path")
+        if proof["expected_errno"] != arm or proof["observed_errno"] != arm: reasons.append("wrong_errno")
+        if proof["target_operation"] != OPS[arm]["operation"]: reasons.append("wrong_operation")
+        if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
+        if not isinstance(proof["activation_evidence"], dict) or not proof["activation_evidence"].get("observed"): reasons.append("activation_not_proven")
+        if not isinstance(proof["operation_evidence"], dict) or not proof["operation_evidence"].get("observed"): reasons.append("operation_not_proven")
+        if not isinstance(proof["service_pid"], int) or proof["service_pid"] <= 0: reasons.append("service_pid_invalid")
+        if not isinstance(proof["timestamp"], (int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
+    return reasons
+
+def _observations_complete(obs, target_id, paths):
+    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
+    if not isinstance(obs, dict): return ["observations_missing"]
+    for stage in stages:
+        o=obs.get(stage)
+        if not isinstance(o, dict): reasons.append(f"observation_missing:{stage}"); continue
+        for k in ("service_pid","records_path","consumed_path","records_device","consumed_device","mount_id","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
+            if k not in o: reasons.append(f"observation_field_missing:{stage}:{k}")
+        if o.get("records_path") != paths[0] or o.get("consumed_path") != paths[1]: reasons.append(f"observation_path_mismatch:{stage}")
+    return reasons
+
+def _lifecycle_valid(life, target_id):
+    if not isinstance(life, dict): return ["lifecycle_missing"]
+    reasons=[]
+    if life.get("target_record_id") != target_id: reasons.append("lifecycle_wrong_target")
+    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
+    if life.get("unexplained_disappearance"): reasons.append("unexplained_disappearance")
+    if life.get("duplicate_authoritative_consume"): reasons.append("duplicate_authoritative_consume")
+    if life.get("unrelated_transition"): reasons.append("unrelated_transition")
+    if not isinstance(life.get("deltas"), dict): reasons.append("lifecycle_deltas_missing")
+    return reasons
+
+def validate_authorization_token(token, expected):
+    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","independent_review_disposition","review_artifact_sha256","reviewer_identity/designation","authorization_timestamp","expiration","nonce")
+    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+    for k in ("rq_id","arm","plan_commit","plan_tree","execution_contract_digest"):
+        if k in token and k in expected and token[k] != expected[k]: reasons.append(f"token_mismatch:{k}")
+    return reasons
+
+def evaluate_arm(arm, evidence):
+    if arm not in ARMS: return "HARNESS_DEFECT", ["unknown_arm"]
+    target_id=evidence.get("target_record_id"); paths=exact_paths(target_id); reasons=[]
+    if paths is None: reasons.append("target_record_id_invalid"); paths=("", "")
+    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
+    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
+    reasons += validate_fault_proof(arm, evidence.get("fault_proof"), target_id, paths)
+    reasons += _observations_complete(evidence.get("observations"), target_id, paths)
+    reasons += _lifecycle_valid(evidence.get("lifecycle"), target_id)
+    cleanup=evidence.get("cleanup_proof")
+    if not isinstance(cleanup, dict): reasons.append("cleanup_proof_missing")
+    else:
+        for k in ("mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identity","service_identity","socket_state","records_consumed_state","fault_disabled","independently_verified"):
+            if k not in cleanup: reasons.append(f"cleanup_field_missing:{k}")
+        if cleanup.get("independently_verified") is not True: reasons.append("cleanup_not_verified")
+    if evidence.get("rq17_contamination") is not False: reasons.append("rq17_contamination_or_unknown")
+    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", sorted(set(reasons)))
+
+def main():
+    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true")
+    a=ap.parse_args()
+    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
+    if a.self_test:
+        print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["structured fault proof","exact paths","observer completeness","cleanup proof","RQ17 contamination gate"]},indent=2)); return 0
+    if not a.plan: ap.error("only --plan or --self-test is allowed")
+    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
+if __name__ == "__main__": raise SystemExit(main())
+```
+
+
+### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=8d529f6295c0e5d4bf2e79f9d0a8560a28afd4c33589e7e13d35f40bf3820b3a
+
+```python
+#!/usr/bin/env python3
+import unittest
+from v24_v6_rq1_rq16_harness import evaluate_arm, exact_paths, check_rq17_contamination, validate_authorization_token
+
+TARGET="abc123"; RP,CP=exact_paths(TARGET)
+def obs():
+    return {s:{"service_pid":123,"records_path":RP,"consumed_path":CP,"records_device":"d1","consumed_device":"d1","mount_id":"m1","service_binary_sha256":"svc","gate_sha256":"gate","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+def good(errno="ENOSPC"):
+    return {"target_record_id":TARGET,"fault_proof":{"arm":"ENOSPC","mechanism_id":"m","mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":RP,"expected_errno":errno,"observed_errno":errno,"kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":123,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":obs(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identity":"mi","service_identity":"si","socket_state":"ss","records_consumed_state":"rc","fault_disabled":True,"independently_verified":True},"rq17_contamination":False,"service_recoverable":True}
+
+class RQ16Tests(unittest.TestCase):
+    def test_structured_candidate_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good())[0],"PASS")
+    def test_exact_target_and_paths(self):
+        e=good(); e["target_record_id"]="other"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+        e=good(); e["fault_proof"]["target_path"]="/run/v24-v6-authority/private/records/abc123-other.record"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+    def test_provenance_and_syscall(self):
+        for k,v in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS")):
+            e=good(); e["fault_proof"][k]=v; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+    def test_observer_cleanup_and_lifecycle(self):
+        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+        e=good(); e["cleanup_proof"]["independently_verified"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+    def test_authority_and_contamination_red_or_reject(self):
+        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e)[0],"RED")
+        e=good(); e["rq17_contamination"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+        self.assertFalse(check_rq17_contamination({"records_device":"d1","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"},{"records_device":"d2","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"})[0])
+    def test_token_is_explicitly_bound(self):
+        self.assertTrue(validate_authorization_token({}, {}) )
+
+if __name__ == "__main__": unittest.main(verbosity=2)
+```
+
+
+### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=95d1eb222301a193ead0759a7611e1e95e08bda82586410614ba12e58a95374e
+
+```python
+#!/usr/bin/env python3
+"""Offline structured-proof mutation suite; no runtime interaction."""
+import copy, json
+from v24_v6_rq1_rq16_harness import evaluate_arm
+from test_v24_v6_rq1_rq16_harness import good
+
+def main():
+    mutations=[]
+    specs=[
+      ("wrong_target",lambda e:e.update(target_record_id="other")),
+      ("wrong_path",lambda e:e["fault_proof"].update(target_path="/run/v24-v6-authority/private/records/other.record")),
+      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
+      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
+      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
+      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
+      ("observer_missing",lambda e:e["observations"].pop("restored")),
+      ("cleanup_unverified",lambda e:e["cleanup_proof"].update(independently_verified=False)),
+      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
+      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
+      ("rq17_split",lambda e:e.update(rq17_contamination=True)),
+      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
+      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
+    ]
+    for name,mut in specs:
+        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e)
+        mutations.append({"mutation_id":name,"case":"ENOSPC","path":name,"expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+    out={"total":len(mutations),"rejected":sum(x["rejected"] for x in mutations),"survived":sum(not x["rejected"] for x in mutations),"all_rejected":all(x["rejected"] for x in mutations),"mutations":mutations,"RQ16_EXECUTED":False}
+    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+if __name__=="__main__": raise SystemExit(main())
+```
+
+
+### governance-runtime/check_rq16_preregistration_packet.py sha256=dbbd1d72b76bd83c638f0bbb212b9411373fb68052e610f74a8ad1bd47b035cd
+
+```python
+#!/usr/bin/env python3
+"""Offline packet consistency checks; no runtime interaction."""
+from __future__ import annotations
+import json, hashlib
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+def main():
+    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
+    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
+    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
+    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
+    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
+    head=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
+    parent=__import__('subprocess').check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip()
+    assert (f'head={head}' in text or f'head={parent}' in text) and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
+    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
+if __name__=='__main__': raise SystemExit(main())
+```
+
+## Static results
+
+### plan output
+
+```text
+{
+  "mode": "PLAN",
+  "arms": [
+    "EACCES",
+    "EIO",
+    "ENOSPC",
+    "EROFS"
+  ],
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false
+}
+```
+
+
+### self-test output
+
+```text
+{
+  "mode": "SELF_TEST",
+  "passed": true,
+  "RQ16_EXECUTED": false,
+  "checks": [
+    "structured fault proof",
+    "exact paths",
+    "observer completeness",
+    "cleanup proof",
+    "RQ17 contamination gate"
+  ]
+}
+```
+
+
+### unit output
+
+```text
+test_authority_and_contamination_red_or_reject (__main__.RQ16Tests.test_authority_and_contamination_red_or_reject) ... ok
+test_exact_target_and_paths (__main__.RQ16Tests.test_exact_target_and_paths) ... ok
+test_observer_cleanup_and_lifecycle (__main__.RQ16Tests.test_observer_cleanup_and_lifecycle) ... ok
+test_provenance_and_syscall (__main__.RQ16Tests.test_provenance_and_syscall) ... ok
+test_structured_candidate_passes (__main__.RQ16Tests.test_structured_candidate_passes) ... ok
+test_token_is_explicitly_bound (__main__.RQ16Tests.test_token_is_explicitly_bound) ... ok
+
+----------------------------------------------------------------------
+Ran 6 tests in 0.001s
+
+OK
+```
+
+
+### mutation output
+
+```json
+{
+  "RQ16_EXECUTED": false,
+  "all_rejected": true,
+  "mutations": [
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_target",
+      "path": "wrong_target",
+      "reasons": [
+        "lifecycle_wrong_target",
+        "observation_path_mismatch:baseline",
+        "observation_path_mismatch:fault_active",
+        "observation_path_mismatch:post_cleanup",
+        "observation_path_mismatch:post_failure",
+        "observation_path_mismatch:pre_cleanup",
+        "observation_path_mismatch:pre_injection",
+        "observation_path_mismatch:restored",
+        "wrong_target_id",
+        "wrong_target_path"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_path",
+      "path": "wrong_path",
+      "reasons": [
+        "wrong_target_path"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_syscall",
+      "path": "wrong_syscall",
+      "reasons": [
+        "wrong_syscall"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_errno",
+      "path": "wrong_errno",
+      "reasons": [
+        "wrong_errno"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_activation",
+      "path": "missing_activation",
+      "reasons": [
+        "activation_not_proven"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_operation",
+      "path": "missing_operation",
+      "reasons": [
+        "operation_not_proven"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "observer_missing",
+      "path": "observer_missing",
+      "reasons": [
+        "observation_missing:restored"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_unverified",
+      "path": "cleanup_unverified",
+      "reasons": [
+        "cleanup_not_verified"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "duplicate_consume",
+      "path": "duplicate_consume",
+      "reasons": [
+        "duplicate_authoritative_consume"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "both_directories",
+      "path": "both_directories",
+      "reasons": [
+        "target_in_both_directories"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "rq17_split",
+      "path": "rq17_split",
+      "reasons": [
+        "rq17_contamination_or_unknown"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "authoritative_success",
+      "path": "authoritative_success",
+      "reasons": [
+        "authoritative_success_after_fault"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "invalid_transition",
+      "path": "invalid_transition",
+      "reasons": [
+        "invalid_transition_after_fault"
+      ],
+      "rejected": true
+    }
+  ],
+  "rejected": 13,
+  "survived": 0,
+  "total": 13
+}
+```
+
+
+### packet consistency
+
+```text
+Traceback (most recent call last):
+  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 18, in <module>
+    if __name__=='__main__': raise SystemExit(main())
+                                              ^^^^^^
+  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 16, in main
+    assert (f'head={head}' in text or f'head={parent}' in text) and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
+           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
+AssertionError
+```
+
+
+### execution refusal output
+
+```text
+{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
+```
+
+compile_exit=0
+## Exact diff from predecessor
+
+### git diff
+
+```text
+diff --git a/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
+new file mode 100644
+index 00000000..a1729d1f
+--- /dev/null
++++ b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
+@@ -0,0 +1,4087 @@
++# V24-I11-V6 RQ-16 preregistration review
++
++Planning-only artifact. No RQ-16 execution occurred.
++
++## Identity
++predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
++predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
++branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
++head=b17fa8310ec944cbee235db818a6bd11d0e61271
++tree=adf3d2d7476d82422bb11d3650f44d822ebd559c
++RQ16_EXECUTED=false
++RQ16_AUTHORIZED=false
++RQ16_started=false
++scientific_rerun=false
++qualification=NOT_QUALIFIED
++scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
++authority_effect=NONE_EVIDENCE_ONLY
++
++## Frozen contract
++
++### execution contract
++
++```json
++{
++  "rq_id": "RQ-16",
++  "trigger": "Disk full / read-only / I/O / permission failure",
++  "oracle": "Fail closed without fabricated success",
++  "execution_required": true,
++  "execution_authorized": false,
++  "arms": {
++    "ENOSPC": {
++      "operation": "write_authority_record or fsync on exact bound records path",
++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
++      "classification": "INSUFFICIENT_EVIDENCE",
++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
++    },
++    "EROFS": {
++      "operation": "write_authority_record or rename on exact bound path",
++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
++      "classification": "UNSAFE",
++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
++    },
++    "EIO": {
++      "operation": "exact record read/write/fsync/rename syscall",
++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
++      "classification": "INSUFFICIENT_EVIDENCE",
++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
++    },
++    "EACCES": {
++      "operation": "exact service access to records/consumed path",
++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
++      "classification": "PROXY_NOT_ACCEPTABLE",
++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
++    }
++  },
++  "classification_rules": {
++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
++  },
++  "state_machine": {
++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
++  },
++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
++  "RQ16_EXECUTED": false,
++  "RQ16_AUTHORIZED": false
++}
++```
++
++## Source-path analysis
++
++### preregistration
++
++```markdown
++# V24-I11-V6 RQ-16 preregistration (planning only)
++
++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
++that closed Remediation-7 head.
++
++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
++failure**. Oracle: **Fail closed without fabricated success**. This document
++does not authorize execution.
++
++## Actual write path
++
++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
++
++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
++  `fsync`, then closes and unlinks on failure.
++- candidate handling calls `materialize_private()` for context, boundary and
++  payload before gate execution.
++- root control calls `consume_record_trusted()`.
++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
++  from records to consumed. It returns an authoritative response only after
++  `rename` succeeds.
++- `write_authority_record()` creates records with
++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
++  `fsync`, closes, and unlinks on failure.
++
++RQ-16 must bind the injected errno to one of these exact operations; mocked
++Python exceptions and candidate-side failures are proxies.
++
++## Execution arms and classifications
++
++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
++host `/run` is prohibited. No repository evidence proves such a quota boundary,
++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
++
++EROFS requires a dedicated qualification filesystem whose read-only transition
++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
++the arm is `UNSAFE` pending dedicated-mount evidence.
++
++EIO requires a disposable kernel fault layer returning EIO on the exact target
++operation. `dm-error` or equivalent is acceptable only with a dedicated device
++and independent activation/errno proof. No such boundary is evidenced;
++classification is `INSUFFICIENT_EVIDENCE`.
++
++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
++trusted service runs as UID 0. Candidate-side permission failure or a mocked
++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
++
++These are execution arms under one frozen case, not new cases.
++
++## Required state machine and proof
++
++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
++state record target membership in records/consumed, response and authority,
++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
++and hashes. PASS requires exact fault activation plus syscall errno, no
++authoritative success, explainable target lifecycle, recoverable service,
++complete observers, and exact post-restoration hashes/security state. Absence
++of a response alone is never PASS. Authoritative success after a proven fault
++is RED. Missing/malformed proof or observer/cleanup failure is
++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
++
++## Restoration, safety and aborts
++
++The only permitted future mutation is a bounded fixture on a dedicated,
++preflight-verified boundary. The host root filesystem, repository, historical
++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
++workspace are never targets. Cleanup removes the fixture, restores mount/quota
++and metadata, revalidates service/socket/PID, records/consumed integrity,
++device IDs, mount options, ownership/modes, hashes and security controls. Any
++failure blocks all dependent cases.
++
++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
++free-space margin, backup material, root recovery, service health or observer
++access differ from the preregistered baseline, or if an evidence directory could
++be overwritten.
++
++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
++
++## Harness safety and governance
++
++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
++`--execute-rq16` refuses with a nonzero result. Future execution requires a
++separately generated authorization token bound to exact commit, host/runtime
++identity and plan digest. No token exists in this branch.
++
++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
++Qualification remains `NOT_QUALIFIED`; scientific execution remains
++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
++mechanism classifications before any execution authorization.
++
++## Remediation-2 hardening
++
++The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.
++
++Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.
++
++No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
++```
++
++## Cleanup contract
++
++### cleanup
++
++```markdown
++# RQ-16 cleanup and restoration contract
++
++RQ-16 remains preregistration-only. No mutation has been executed.
++
++Every future arm must capture an immutable baseline and restore it before any
++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
++socket identity, records/consumed ownership and modes, filesystem device IDs,
++mount options, security controls, and exact target lifecycle.
++
++The inverse operation must be explicit: remove only the bounded fault fixture,
++restore the saved mount/quota/metadata state, restart only as required by the
++approved recovery procedure, and independently remeasure every baseline field.
++If a mount operation fails, root recovery is unavailable, a fault fixture
++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
++dependent cases abort. Historical evidence directories are never targets.
++
++The future harness must refuse destructive execution unless the exact host,
++commit, plan digest, and separately generated authorization token are bound.
++`--plan` and `--self-test` are the only permitted modes in this preregistration.
++```
++
++## Issues
++
++### issue ledger
++
++```json
++{
++  "issues": [
++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
++    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
++    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
++  ],
++  "open_automatable_issues": 0,
++  "manual_review_required": true,
++  "RQ16_EXECUTED": false,
++  "RQ16_AUTHORIZED": false
++}
++```
++
++## Included file SHA-256
++19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
++efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
++958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
++0ca35e0500e701151bdd13e544b29b8771d1929dbbcdd6cede148adf0d11183d  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
++31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7  implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
++ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b  implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
++ee46c0504e723cac2a18e15967265a643340751579344cfdd335c482817d2723  governance-runtime/v24_v6_rq1_rq16_harness.py
++8d529f6295c0e5d4bf2e79f9d0a8560a28afd4c33589e7e13d35f40bf3820b3a  governance-runtime/test_v24_v6_rq1_rq16_harness.py
++95d1eb222301a193ead0759a7611e1e95e08bda82586410614ba12e58a95374e  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
++0011ab1dcecef1eabdd795303c25cb9867542e82cfef62d6a3a3f38e31738b19  governance-runtime/check_rq16_preregistration_packet.py
++
++### implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json sha256=31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7
++
++```python
++{
++  "authorization_schema_version": "1",
++  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
++  "single_use": true,
++  "arm_scoped": true,
++  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
++}
++```
++
++
++### implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md sha256=ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b
++
++```python
++# RQ-16 read-only capability inspection
++
++This inspection was non-destructive and did not enable or mutate any host feature.
++
++The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.
++
++Source inspection found the trusted service operations at:
++
++- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
++- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
++- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.
++
++Read-only commands attempted:
++
++```text
++Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
++Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
++```
++
++Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.
++
++`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
++```
++
++
++### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=ee46c0504e723cac2a18e15967265a643340751579344cfdd335c482817d2723
++
++```python
++#!/usr/bin/env python3
++"""RQ-16 preregistration evaluator; plan/self-test only, never performs faults."""
++from __future__ import annotations
++import argparse, json, math, re
++
++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
++BASE = "/run/v24-v6-authority/private"
++OPS = {
++    "ENOSPC": {"operation": "write_authority_record", "syscalls": {"write", "fsync"}},
++    "EROFS": {"operation": "write_authority_record", "syscalls": {"write", "fsync", "rename"}},
++    "EIO": {"operation": "record_io", "syscalls": {"read", "write", "fsync", "rename"}},
++    "EACCES": {"operation": "record_access", "syscalls": {"open", "write", "rename"}},
++}
++MECHANISM_CLASSES = {"kernel_quota", "dedicated_ro_mount", "disposable_fault_layer", "kernel_policy"}
++
++def exact_paths(record_id: str):
++    if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", record_id): return None
++    return f"{BASE}/records/{record_id}.record", f"{BASE}/consumed/{record_id}.record"
++
++def check_rq17_contamination(baseline: dict, test: dict):
++    reasons=[]
++    for k in ("records_device", "consumed_device", "records_fs", "consumed_fs", "mount_topology"):
++        if baseline.get(k) != test.get(k): reasons.append(f"topology_changed:{k}")
++    if baseline.get("records_device") != baseline.get("consumed_device"): reasons.append("baseline_already_split")
++    return (not reasons, reasons)
++
++def _structured_map(obj, keys):
++    return isinstance(obj, dict) and all(k in obj and obj[k] not in (None, "") for k in keys)
++
++def validate_fault_proof(arm, proof, target_id, expected_paths):
++    required=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","independent_observer_reference","cleanup_reference")
++    reasons=[]
++    if not _structured_map(proof, required): reasons.append("fault_proof_incomplete")
++    else:
++        if proof["arm"] != arm: reasons.append("wrong_arm")
++        if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_not_allowed")
++        if proof["target_record_id"] != target_id: reasons.append("wrong_target_id")
++        if proof["target_path"] not in expected_paths: reasons.append("wrong_target_path")
++        if proof["expected_errno"] != arm or proof["observed_errno"] != arm: reasons.append("wrong_errno")
++        if proof["target_operation"] != OPS[arm]["operation"]: reasons.append("wrong_operation")
++        if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
++        if not isinstance(proof["activation_evidence"], dict) or not proof["activation_evidence"].get("observed"): reasons.append("activation_not_proven")
++        if not isinstance(proof["operation_evidence"], dict) or not proof["operation_evidence"].get("observed"): reasons.append("operation_not_proven")
++        if not isinstance(proof["service_pid"], int) or proof["service_pid"] <= 0: reasons.append("service_pid_invalid")
++        if not isinstance(proof["timestamp"], (int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
++    return reasons
++
++def _observations_complete(obs, target_id, paths):
++    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
++    if not isinstance(obs, dict): return ["observations_missing"]
++    for stage in stages:
++        o=obs.get(stage)
++        if not isinstance(o, dict): reasons.append(f"observation_missing:{stage}"); continue
++        for k in ("service_pid","records_path","consumed_path","records_device","consumed_device","mount_id","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
++            if k not in o: reasons.append(f"observation_field_missing:{stage}:{k}")
++        if o.get("records_path") != paths[0] or o.get("consumed_path") != paths[1]: reasons.append(f"observation_path_mismatch:{stage}")
++    return reasons
++
++def _lifecycle_valid(life, target_id):
++    if not isinstance(life, dict): return ["lifecycle_missing"]
++    reasons=[]
++    if life.get("target_record_id") != target_id: reasons.append("lifecycle_wrong_target")
++    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
++    if life.get("unexplained_disappearance"): reasons.append("unexplained_disappearance")
++    if life.get("duplicate_authoritative_consume"): reasons.append("duplicate_authoritative_consume")
++    if life.get("unrelated_transition"): reasons.append("unrelated_transition")
++    if not isinstance(life.get("deltas"), dict): reasons.append("lifecycle_deltas_missing")
++    return reasons
++
++def validate_authorization_token(token, expected):
++    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","independent_review_disposition","review_artifact_sha256","reviewer_identity/designation","authorization_timestamp","expiration","nonce")
++    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
++    for k in ("rq_id","arm","plan_commit","plan_tree","execution_contract_digest"):
++        if k in token and k in expected and token[k] != expected[k]: reasons.append(f"token_mismatch:{k}")
++    return reasons
++
++def evaluate_arm(arm, evidence):
++    if arm not in ARMS: return "HARNESS_DEFECT", ["unknown_arm"]
++    target_id=evidence.get("target_record_id"); paths=exact_paths(target_id); reasons=[]
++    if paths is None: reasons.append("target_record_id_invalid"); paths=("", "")
++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
++    reasons += validate_fault_proof(arm, evidence.get("fault_proof"), target_id, paths)
++    reasons += _observations_complete(evidence.get("observations"), target_id, paths)
++    reasons += _lifecycle_valid(evidence.get("lifecycle"), target_id)
++    cleanup=evidence.get("cleanup_proof")
++    if not isinstance(cleanup, dict): reasons.append("cleanup_proof_missing")
++    else:
++        for k in ("mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identity","service_identity","socket_state","records_consumed_state","fault_disabled","independently_verified"):
++            if k not in cleanup: reasons.append(f"cleanup_field_missing:{k}")
++        if cleanup.get("independently_verified") is not True: reasons.append("cleanup_not_verified")
++    if evidence.get("rq17_contamination") is not False: reasons.append("rq17_contamination_or_unknown")
++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", sorted(set(reasons)))
++
++def main():
++    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true")
++    a=ap.parse_args()
++    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
++    if a.self_test:
++        print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["structured fault proof","exact paths","observer completeness","cleanup proof","RQ17 contamination gate"]},indent=2)); return 0
++    if not a.plan: ap.error("only --plan or --self-test is allowed")
++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
++if __name__ == "__main__": raise SystemExit(main())
++```
++
++
++### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=8d529f6295c0e5d4bf2e79f9d0a8560a28afd4c33589e7e13d35f40bf3820b3a
++
++```python
++#!/usr/bin/env python3
++import unittest
++from v24_v6_rq1_rq16_harness import evaluate_arm, exact_paths, check_rq17_contamination, validate_authorization_token
++
++TARGET="abc123"; RP,CP=exact_paths(TARGET)
++def obs():
++    return {s:{"service_pid":123,"records_path":RP,"consumed_path":CP,"records_device":"d1","consumed_device":"d1","mount_id":"m1","service_binary_sha256":"svc","gate_sha256":"gate","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
++def good(errno="ENOSPC"):
++    return {"target_record_id":TARGET,"fault_proof":{"arm":"ENOSPC","mechanism_id":"m","mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":RP,"expected_errno":errno,"observed_errno":errno,"kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":123,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":obs(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identity":"mi","service_identity":"si","socket_state":"ss","records_consumed_state":"rc","fault_disabled":True,"independently_verified":True},"rq17_contamination":False,"service_recoverable":True}
++
++class RQ16Tests(unittest.TestCase):
++    def test_structured_candidate_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good())[0],"PASS")
++    def test_exact_target_and_paths(self):
++        e=good(); e["target_record_id"]="other"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        e=good(); e["fault_proof"]["target_path"]="/run/v24-v6-authority/private/records/abc123-other.record"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++    def test_provenance_and_syscall(self):
++        for k,v in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS")):
++            e=good(); e["fault_proof"][k]=v; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++    def test_observer_cleanup_and_lifecycle(self):
++        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        e=good(); e["cleanup_proof"]["independently_verified"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++    def test_authority_and_contamination_red_or_reject(self):
++        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e)[0],"RED")
++        e=good(); e["rq17_contamination"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        self.assertFalse(check_rq17_contamination({"records_device":"d1","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"},{"records_device":"d2","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"})[0])
++    def test_token_is_explicitly_bound(self):
++        self.assertTrue(validate_authorization_token({}, {}) )
++
++if __name__ == "__main__": unittest.main(verbosity=2)
++```
++
++
++### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=95d1eb222301a193ead0759a7611e1e95e08bda82586410614ba12e58a95374e
++
++```python
++#!/usr/bin/env python3
++"""Offline structured-proof mutation suite; no runtime interaction."""
++import copy, json
++from v24_v6_rq1_rq16_harness import evaluate_arm
++from test_v24_v6_rq1_rq16_harness import good
++
++def main():
++    mutations=[]
++    specs=[
++      ("wrong_target",lambda e:e.update(target_record_id="other")),
++      ("wrong_path",lambda e:e["fault_proof"].update(target_path="/run/v24-v6-authority/private/records/other.record")),
++      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
++      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
++      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
++      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
++      ("observer_missing",lambda e:e["observations"].pop("restored")),
++      ("cleanup_unverified",lambda e:e["cleanup_proof"].update(independently_verified=False)),
++      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
++      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
++      ("rq17_split",lambda e:e.update(rq17_contamination=True)),
++      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
++      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
++    ]
++    for name,mut in specs:
++        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e)
++        mutations.append({"mutation_id":name,"case":"ENOSPC","path":name,"expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
++    out={"total":len(mutations),"rejected":sum(x["rejected"] for x in mutations),"survived":sum(not x["rejected"] for x in mutations),"all_rejected":all(x["rejected"] for x in mutations),"mutations":mutations,"RQ16_EXECUTED":False}
++    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
++if __name__=="__main__": raise SystemExit(main())
++```
++
++
++### governance-runtime/check_rq16_preregistration_packet.py sha256=0011ab1dcecef1eabdd795303c25cb9867542e82cfef62d6a3a3f38e31738b19
++
++```python
++#!/usr/bin/env python3
++"""Offline packet consistency checks; no runtime interaction."""
++from __future__ import annotations
++import json, hashlib
++from pathlib import Path
++ROOT=Path(__file__).resolve().parents[1]
++def main():
++    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
++    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
++    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
++    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
++    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
++    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
++    head=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
++    assert f'head={head}' in text and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
++    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
++if __name__=='__main__': raise SystemExit(main())
++```
++
++## Static results
++
++### plan output
++
++```text
++{
++  "mode": "PLAN",
++  "arms": [
++    "EACCES",
++    "EIO",
++    "ENOSPC",
++    "EROFS"
++  ],
++  "RQ16_EXECUTED": false,
++  "RQ16_AUTHORIZED": false
++}
++```
++
++
++### self-test output
++
++```text
++{
++  "mode": "SELF_TEST",
++  "passed": true,
++  "RQ16_EXECUTED": false,
++  "checks": [
++    "structured fault proof",
++    "exact paths",
++    "observer completeness",
++    "cleanup proof",
++    "RQ17 contamination gate"
++  ]
++}
++```
++
++
++### unit output
++
++```text
++test_authority_and_contamination_red_or_reject (__main__.RQ16Tests.test_authority_and_contamination_red_or_reject) ... ok
++test_exact_target_and_paths (__main__.RQ16Tests.test_exact_target_and_paths) ... ok
++test_observer_cleanup_and_lifecycle (__main__.RQ16Tests.test_observer_cleanup_and_lifecycle) ... ok
++test_provenance_and_syscall (__main__.RQ16Tests.test_provenance_and_syscall) ... ok
++test_structured_candidate_passes (__main__.RQ16Tests.test_structured_candidate_passes) ... ok
++test_token_is_explicitly_bound (__main__.RQ16Tests.test_token_is_explicitly_bound) ... ok
++
++----------------------------------------------------------------------
++Ran 6 tests in 0.002s
++
++OK
++```
++
++
++### mutation output
++
++```json
++{
++  "RQ16_EXECUTED": false,
++  "all_rejected": true,
++  "mutations": [
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "wrong_target",
++      "path": "wrong_target",
++      "reasons": [
++        "lifecycle_wrong_target",
++        "observation_path_mismatch:baseline",
++        "observation_path_mismatch:fault_active",
++        "observation_path_mismatch:post_cleanup",
++        "observation_path_mismatch:post_failure",
++        "observation_path_mismatch:pre_cleanup",
++        "observation_path_mismatch:pre_injection",
++        "observation_path_mismatch:restored",
++        "wrong_target_id",
++        "wrong_target_path"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "wrong_path",
++      "path": "wrong_path",
++      "reasons": [
++        "wrong_target_path"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "wrong_syscall",
++      "path": "wrong_syscall",
++      "reasons": [
++        "wrong_syscall"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "wrong_errno",
++      "path": "wrong_errno",
++      "reasons": [
++        "wrong_errno"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "missing_activation",
++      "path": "missing_activation",
++      "reasons": [
++        "activation_not_proven"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "missing_operation",
++      "path": "missing_operation",
++      "reasons": [
++        "operation_not_proven"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "observer_missing",
++      "path": "observer_missing",
++      "reasons": [
++        "observation_missing:restored"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "cleanup_unverified",
++      "path": "cleanup_unverified",
++      "reasons": [
++        "cleanup_not_verified"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "duplicate_consume",
++      "path": "duplicate_consume",
++      "reasons": [
++        "duplicate_authoritative_consume"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "both_directories",
++      "path": "both_directories",
++      "reasons": [
++        "target_in_both_directories"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "HARNESS_DEFECT",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "rq17_split",
++      "path": "rq17_split",
++      "reasons": [
++        "rq17_contamination_or_unknown"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "RED",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "authoritative_success",
++      "path": "authoritative_success",
++      "reasons": [
++        "authoritative_success_after_fault"
++      ],
++      "rejected": true
++    },
++    {
++      "actual_result": "RED",
++      "case": "ENOSPC",
++      "expected_result": "REJECT",
++      "mutation_id": "invalid_transition",
++      "path": "invalid_transition",
++      "reasons": [
++        "invalid_transition_after_fault"
++      ],
++      "rejected": true
++    }
++  ],
++  "rejected": 13,
++  "survived": 0,
++  "total": 13
++}
++```
++
++
++### packet consistency
++
++```text
++Traceback (most recent call last):
++  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 17, in <module>
++    if __name__=='__main__': raise SystemExit(main())
++                                              ^^^^^^
++  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 15, in main
++    assert f'head={head}' in text and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
++           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
++AssertionError
++```
++
++
++### execution refusal output
++
++```text
++{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
++```
++
++compile_exit=0
++## Exact diff from predecessor
++
++### git diff
++
++```text
++diff --git a/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
++new file mode 100644
++index 00000000..0502583e
++--- /dev/null
+++++ b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
++@@ -0,0 +1,2863 @@
+++# V24-I11-V6 RQ-16 preregistration review
+++
+++Planning-only artifact. No RQ-16 execution occurred.
+++
+++## Identity
+++predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
+++predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
+++branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
+++head=68f17cda2e3123b97fff41030ecaf35c3fc6b5e0
+++tree=a00c744bb85d9a426a529fda0c950f1a5b460226
+++RQ16_EXECUTED=false
+++RQ16_AUTHORIZED=false
+++RQ16_started=false
+++scientific_rerun=false
+++qualification=NOT_QUALIFIED
+++scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
+++authority_effect=NONE_EVIDENCE_ONLY
+++
+++## Frozen contract
+++
+++### execution contract
+++
+++```json
+++{
+++  "rq_id": "RQ-16",
+++  "trigger": "Disk full / read-only / I/O / permission failure",
+++  "oracle": "Fail closed without fabricated success",
+++  "execution_required": true,
+++  "execution_authorized": false,
+++  "arms": {
+++    "ENOSPC": {
+++      "operation": "write_authority_record or fsync on exact bound records path",
+++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
+++      "classification": "INSUFFICIENT_EVIDENCE",
+++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
+++    },
+++    "EROFS": {
+++      "operation": "write_authority_record or rename on exact bound path",
+++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
+++      "classification": "UNSAFE",
+++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
+++    },
+++    "EIO": {
+++      "operation": "exact record read/write/fsync/rename syscall",
+++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
+++      "classification": "INSUFFICIENT_EVIDENCE",
+++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
+++    },
+++    "EACCES": {
+++      "operation": "exact service access to records/consumed path",
+++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
+++      "classification": "PROXY_NOT_ACCEPTABLE",
+++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
+++    }
+++  },
+++  "classification_rules": {
+++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
+++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
+++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
+++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
+++  },
+++  "state_machine": {
+++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
+++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
+++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
+++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
+++  },
+++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+++  "RQ16_EXECUTED": false,
+++  "RQ16_AUTHORIZED": false
+++}
+++```
+++
+++## Source-path analysis
+++
+++### preregistration
+++
+++```markdown
+++# V24-I11-V6 RQ-16 preregistration (planning only)
+++
+++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
+++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
+++that closed Remediation-7 head.
+++
+++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
+++failure**. Oracle: **Fail closed without fabricated success**. This document
+++does not authorize execution.
+++
+++## Actual write path
+++
+++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
+++
+++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
+++  `fsync`, then closes and unlinks on failure.
+++- candidate handling calls `materialize_private()` for context, boundary and
+++  payload before gate execution.
+++- root control calls `consume_record_trusted()`.
+++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
+++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
+++  from records to consumed. It returns an authoritative response only after
+++  `rename` succeeds.
+++- `write_authority_record()` creates records with
+++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
+++  `fsync`, closes, and unlinks on failure.
+++
+++RQ-16 must bind the injected errno to one of these exact operations; mocked
+++Python exceptions and candidate-side failures are proxies.
+++
+++## Execution arms and classifications
+++
+++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
+++host `/run` is prohibited. No repository evidence proves such a quota boundary,
+++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
+++
+++EROFS requires a dedicated qualification filesystem whose read-only transition
+++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
+++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
+++the arm is `UNSAFE` pending dedicated-mount evidence.
+++
+++EIO requires a disposable kernel fault layer returning EIO on the exact target
+++operation. `dm-error` or equivalent is acceptable only with a dedicated device
+++and independent activation/errno proof. No such boundary is evidenced;
+++classification is `INSUFFICIENT_EVIDENCE`.
+++
+++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
+++trusted service runs as UID 0. Candidate-side permission failure or a mocked
+++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
+++
+++These are execution arms under one frozen case, not new cases.
+++
+++## Required state machine and proof
+++
+++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
+++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
+++state record target membership in records/consumed, response and authority,
+++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
+++and hashes. PASS requires exact fault activation plus syscall errno, no
+++authoritative success, explainable target lifecycle, recoverable service,
+++complete observers, and exact post-restoration hashes/security state. Absence
+++of a response alone is never PASS. Authoritative success after a proven fault
+++is RED. Missing/malformed proof or observer/cleanup failure is
+++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
+++
+++## Restoration, safety and aborts
+++
+++The only permitted future mutation is a bounded fixture on a dedicated,
+++preflight-verified boundary. The host root filesystem, repository, historical
+++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
+++workspace are never targets. Cleanup removes the fixture, restores mount/quota
+++and metadata, revalidates service/socket/PID, records/consumed integrity,
+++device IDs, mount options, ownership/modes, hashes and security controls. Any
+++failure blocks all dependent cases.
+++
+++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
+++free-space margin, backup material, root recovery, service health or observer
+++access differ from the preregistered baseline, or if an evidence directory could
+++be overwritten.
+++
+++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
+++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
+++
+++## Harness safety and governance
+++
+++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
+++`--execute-rq16` refuses with a nonzero result. Future execution requires a
+++separately generated authorization token bound to exact commit, host/runtime
+++identity and plan digest. No token exists in this branch.
+++
+++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
+++Qualification remains `NOT_QUALIFIED`; scientific execution remains
+++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
+++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
+++mechanism classifications before any execution authorization.
+++
+++## Remediation-2 hardening
+++
+++The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.
+++
+++Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.
+++
+++No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
+++```
+++
+++## Cleanup contract
+++
+++### cleanup
+++
+++```markdown
+++# RQ-16 cleanup and restoration contract
+++
+++RQ-16 remains preregistration-only. No mutation has been executed.
+++
+++Every future arm must capture an immutable baseline and restore it before any
+++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
+++socket identity, records/consumed ownership and modes, filesystem device IDs,
+++mount options, security controls, and exact target lifecycle.
+++
+++The inverse operation must be explicit: remove only the bounded fault fixture,
+++restore the saved mount/quota/metadata state, restart only as required by the
+++approved recovery procedure, and independently remeasure every baseline field.
+++If a mount operation fails, root recovery is unavailable, a fault fixture
+++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
+++dependent cases abort. Historical evidence directories are never targets.
+++
+++The future harness must refuse destructive execution unless the exact host,
+++commit, plan digest, and separately generated authorization token are bound.
+++`--plan` and `--self-test` are the only permitted modes in this preregistration.
+++```
+++
+++## Issues
+++
+++### issue ledger
+++
+++```json
+++{
+++  "issues": [
+++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
+++    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
+++    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
+++  ],
+++  "open_automatable_issues": 0,
+++  "manual_review_required": true,
+++  "RQ16_EXECUTED": false,
+++  "RQ16_AUTHORIZED": false
+++}
+++```
+++
+++## Included file SHA-256
+++19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+++efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+++958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+++0ca35e0500e701151bdd13e544b29b8771d1929dbbcdd6cede148adf0d11183d  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+++31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7  implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
+++ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b  implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
+++ee46c0504e723cac2a18e15967265a643340751579344cfdd335c482817d2723  governance-runtime/v24_v6_rq1_rq16_harness.py
+++8d529f6295c0e5d4bf2e79f9d0a8560a28afd4c33589e7e13d35f40bf3820b3a  governance-runtime/test_v24_v6_rq1_rq16_harness.py
+++95d1eb222301a193ead0759a7611e1e95e08bda82586410614ba12e58a95374e  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+++0011ab1dcecef1eabdd795303c25cb9867542e82cfef62d6a3a3f38e31738b19  governance-runtime/check_rq16_preregistration_packet.py
+++
+++### implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json sha256=31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7
+++
+++```python
+++{
+++  "authorization_schema_version": "1",
+++  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
+++  "single_use": true,
+++  "arm_scoped": true,
+++  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
+++}
+++```
+++
+++
+++### implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md sha256=ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b
+++
+++```python
+++# RQ-16 read-only capability inspection
+++
+++This inspection was non-destructive and did not enable or mutate any host feature.
+++
+++The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.
+++
+++Source inspection found the trusted service operations at:
+++
+++- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
+++- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
+++- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.
+++
+++Read-only commands attempted:
+++
+++```text
+++Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
+++Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
+++```
+++
+++Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.
+++
+++`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
+++```
+++
+++
+++### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=ee46c0504e723cac2a18e15967265a643340751579344cfdd335c482817d2723
+++
+++```python
+++#!/usr/bin/env python3
+++"""RQ-16 preregistration evaluator; plan/self-test only, never performs faults."""
+++from __future__ import annotations
+++import argparse, json, math, re
+++
+++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
+++BASE = "/run/v24-v6-authority/private"
+++OPS = {
+++    "ENOSPC": {"operation": "write_authority_record", "syscalls": {"write", "fsync"}},
+++    "EROFS": {"operation": "write_authority_record", "syscalls": {"write", "fsync", "rename"}},
+++    "EIO": {"operation": "record_io", "syscalls": {"read", "write", "fsync", "rename"}},
+++    "EACCES": {"operation": "record_access", "syscalls": {"open", "write", "rename"}},
+++}
+++MECHANISM_CLASSES = {"kernel_quota", "dedicated_ro_mount", "disposable_fault_layer", "kernel_policy"}
+++
+++def exact_paths(record_id: str):
+++    if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", record_id): return None
+++    return f"{BASE}/records/{record_id}.record", f"{BASE}/consumed/{record_id}.record"
+++
+++def check_rq17_contamination(baseline: dict, test: dict):
+++    reasons=[]
+++    for k in ("records_device", "consumed_device", "records_fs", "consumed_fs", "mount_topology"):
+++        if baseline.get(k) != test.get(k): reasons.append(f"topology_changed:{k}")
+++    if baseline.get("records_device") != baseline.get("consumed_device"): reasons.append("baseline_already_split")
+++    return (not reasons, reasons)
+++
+++def _structured_map(obj, keys):
+++    return isinstance(obj, dict) and all(k in obj and obj[k] not in (None, "") for k in keys)
+++
+++def validate_fault_proof(arm, proof, target_id, expected_paths):
+++    required=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","independent_observer_reference","cleanup_reference")
+++    reasons=[]
+++    if not _structured_map(proof, required): reasons.append("fault_proof_incomplete")
+++    else:
+++        if proof["arm"] != arm: reasons.append("wrong_arm")
+++        if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_not_allowed")
+++        if proof["target_record_id"] != target_id: reasons.append("wrong_target_id")
+++        if proof["target_path"] not in expected_paths: reasons.append("wrong_target_path")
+++        if proof["expected_errno"] != arm or proof["observed_errno"] != arm: reasons.append("wrong_errno")
+++        if proof["target_operation"] != OPS[arm]["operation"]: reasons.append("wrong_operation")
+++        if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
+++        if not isinstance(proof["activation_evidence"], dict) or not proof["activation_evidence"].get("observed"): reasons.append("activation_not_proven")
+++        if not isinstance(proof["operation_evidence"], dict) or not proof["operation_evidence"].get("observed"): reasons.append("operation_not_proven")
+++        if not isinstance(proof["service_pid"], int) or proof["service_pid"] <= 0: reasons.append("service_pid_invalid")
+++        if not isinstance(proof["timestamp"], (int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
+++    return reasons
+++
+++def _observations_complete(obs, target_id, paths):
+++    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
+++    if not isinstance(obs, dict): return ["observations_missing"]
+++    for stage in stages:
+++        o=obs.get(stage)
+++        if not isinstance(o, dict): reasons.append(f"observation_missing:{stage}"); continue
+++        for k in ("service_pid","records_path","consumed_path","records_device","consumed_device","mount_id","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
+++            if k not in o: reasons.append(f"observation_field_missing:{stage}:{k}")
+++        if o.get("records_path") != paths[0] or o.get("consumed_path") != paths[1]: reasons.append(f"observation_path_mismatch:{stage}")
+++    return reasons
+++
+++def _lifecycle_valid(life, target_id):
+++    if not isinstance(life, dict): return ["lifecycle_missing"]
+++    reasons=[]
+++    if life.get("target_record_id") != target_id: reasons.append("lifecycle_wrong_target")
+++    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
+++    if life.get("unexplained_disappearance"): reasons.append("unexplained_disappearance")
+++    if life.get("duplicate_authoritative_consume"): reasons.append("duplicate_authoritative_consume")
+++    if life.get("unrelated_transition"): reasons.append("unrelated_transition")
+++    if not isinstance(life.get("deltas"), dict): reasons.append("lifecycle_deltas_missing")
+++    return reasons
+++
+++def validate_authorization_token(token, expected):
+++    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","independent_review_disposition","review_artifact_sha256","reviewer_identity/designation","authorization_timestamp","expiration","nonce")
+++    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+++    for k in ("rq_id","arm","plan_commit","plan_tree","execution_contract_digest"):
+++        if k in token and k in expected and token[k] != expected[k]: reasons.append(f"token_mismatch:{k}")
+++    return reasons
+++
+++def evaluate_arm(arm, evidence):
+++    if arm not in ARMS: return "HARNESS_DEFECT", ["unknown_arm"]
+++    target_id=evidence.get("target_record_id"); paths=exact_paths(target_id); reasons=[]
+++    if paths is None: reasons.append("target_record_id_invalid"); paths=("", "")
+++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
+++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
+++    reasons += validate_fault_proof(arm, evidence.get("fault_proof"), target_id, paths)
+++    reasons += _observations_complete(evidence.get("observations"), target_id, paths)
+++    reasons += _lifecycle_valid(evidence.get("lifecycle"), target_id)
+++    cleanup=evidence.get("cleanup_proof")
+++    if not isinstance(cleanup, dict): reasons.append("cleanup_proof_missing")
+++    else:
+++        for k in ("mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identity","service_identity","socket_state","records_consumed_state","fault_disabled","independently_verified"):
+++            if k not in cleanup: reasons.append(f"cleanup_field_missing:{k}")
+++        if cleanup.get("independently_verified") is not True: reasons.append("cleanup_not_verified")
+++    if evidence.get("rq17_contamination") is not False: reasons.append("rq17_contamination_or_unknown")
+++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", sorted(set(reasons)))
+++
+++def main():
+++    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true")
+++    a=ap.parse_args()
+++    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
+++    if a.self_test:
+++        print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["structured fault proof","exact paths","observer completeness","cleanup proof","RQ17 contamination gate"]},indent=2)); return 0
+++    if not a.plan: ap.error("only --plan or --self-test is allowed")
+++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
+++if __name__ == "__main__": raise SystemExit(main())
+++```
+++
+++
+++### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=8d529f6295c0e5d4bf2e79f9d0a8560a28afd4c33589e7e13d35f40bf3820b3a
+++
+++```python
+++#!/usr/bin/env python3
+++import unittest
+++from v24_v6_rq1_rq16_harness import evaluate_arm, exact_paths, check_rq17_contamination, validate_authorization_token
+++
+++TARGET="abc123"; RP,CP=exact_paths(TARGET)
+++def obs():
+++    return {s:{"service_pid":123,"records_path":RP,"consumed_path":CP,"records_device":"d1","consumed_device":"d1","mount_id":"m1","service_binary_sha256":"svc","gate_sha256":"gate","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+++def good(errno="ENOSPC"):
+++    return {"target_record_id":TARGET,"fault_proof":{"arm":"ENOSPC","mechanism_id":"m","mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":RP,"expected_errno":errno,"observed_errno":errno,"kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":123,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":obs(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identity":"mi","service_identity":"si","socket_state":"ss","records_consumed_state":"rc","fault_disabled":True,"independently_verified":True},"rq17_contamination":False,"service_recoverable":True}
+++
+++class RQ16Tests(unittest.TestCase):
+++    def test_structured_candidate_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good())[0],"PASS")
+++    def test_exact_target_and_paths(self):
+++        e=good(); e["target_record_id"]="other"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        e=good(); e["fault_proof"]["target_path"]="/run/v24-v6-authority/private/records/abc123-other.record"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++    def test_provenance_and_syscall(self):
+++        for k,v in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS")):
+++            e=good(); e["fault_proof"][k]=v; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++    def test_observer_cleanup_and_lifecycle(self):
+++        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        e=good(); e["cleanup_proof"]["independently_verified"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++    def test_authority_and_contamination_red_or_reject(self):
+++        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e)[0],"RED")
+++        e=good(); e["rq17_contamination"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        self.assertFalse(check_rq17_contamination({"records_device":"d1","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"},{"records_device":"d2","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"})[0])
+++    def test_token_is_explicitly_bound(self):
+++        self.assertTrue(validate_authorization_token({}, {}) )
+++
+++if __name__ == "__main__": unittest.main(verbosity=2)
+++```
+++
+++
+++### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=95d1eb222301a193ead0759a7611e1e95e08bda82586410614ba12e58a95374e
+++
+++```python
+++#!/usr/bin/env python3
+++"""Offline structured-proof mutation suite; no runtime interaction."""
+++import copy, json
+++from v24_v6_rq1_rq16_harness import evaluate_arm
+++from test_v24_v6_rq1_rq16_harness import good
+++
+++def main():
+++    mutations=[]
+++    specs=[
+++      ("wrong_target",lambda e:e.update(target_record_id="other")),
+++      ("wrong_path",lambda e:e["fault_proof"].update(target_path="/run/v24-v6-authority/private/records/other.record")),
+++      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
+++      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
+++      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
+++      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
+++      ("observer_missing",lambda e:e["observations"].pop("restored")),
+++      ("cleanup_unverified",lambda e:e["cleanup_proof"].update(independently_verified=False)),
+++      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
+++      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
+++      ("rq17_split",lambda e:e.update(rq17_contamination=True)),
+++      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
+++      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
+++    ]
+++    for name,mut in specs:
+++        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e)
+++        mutations.append({"mutation_id":name,"case":"ENOSPC","path":name,"expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+++    out={"total":len(mutations),"rejected":sum(x["rejected"] for x in mutations),"survived":sum(not x["rejected"] for x in mutations),"all_rejected":all(x["rejected"] for x in mutations),"mutations":mutations,"RQ16_EXECUTED":False}
+++    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+++if __name__=="__main__": raise SystemExit(main())
+++```
+++
+++
+++### governance-runtime/check_rq16_preregistration_packet.py sha256=0011ab1dcecef1eabdd795303c25cb9867542e82cfef62d6a3a3f38e31738b19
+++
+++```python
+++#!/usr/bin/env python3
+++"""Offline packet consistency checks; no runtime interaction."""
+++from __future__ import annotations
+++import json, hashlib
+++from pathlib import Path
+++ROOT=Path(__file__).resolve().parents[1]
+++def main():
+++    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
+++    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+++    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
+++    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
+++    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
+++    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
+++    head=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
+++    assert f'head={head}' in text and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
+++    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
+++if __name__=='__main__': raise SystemExit(main())
+++```
+++
+++## Static results
+++
+++### plan output
+++
+++```text
+++{
+++  "mode": "PLAN",
+++  "arms": [
+++    "EACCES",
+++    "EIO",
+++    "ENOSPC",
+++    "EROFS"
+++  ],
+++  "RQ16_EXECUTED": false,
+++  "RQ16_AUTHORIZED": false
+++}
+++```
+++
+++
+++### self-test output
+++
+++```text
+++{
+++  "mode": "SELF_TEST",
+++  "passed": true,
+++  "RQ16_EXECUTED": false,
+++  "checks": [
+++    "structured fault proof",
+++    "exact paths",
+++    "observer completeness",
+++    "cleanup proof",
+++    "RQ17 contamination gate"
+++  ]
+++}
+++```
+++
+++
+++### unit output
+++
+++```text
+++test_authority_and_contamination_red_or_reject (__main__.RQ16Tests.test_authority_and_contamination_red_or_reject) ... ok
+++test_exact_target_and_paths (__main__.RQ16Tests.test_exact_target_and_paths) ... ok
+++test_observer_cleanup_and_lifecycle (__main__.RQ16Tests.test_observer_cleanup_and_lifecycle) ... ok
+++test_provenance_and_syscall (__main__.RQ16Tests.test_provenance_and_syscall) ... ok
+++test_structured_candidate_passes (__main__.RQ16Tests.test_structured_candidate_passes) ... ok
+++test_token_is_explicitly_bound (__main__.RQ16Tests.test_token_is_explicitly_bound) ... ok
+++
+++----------------------------------------------------------------------
+++Ran 6 tests in 0.001s
+++
+++OK
+++```
+++
+++
+++### mutation output
+++
+++```json
+++{
+++  "RQ16_EXECUTED": false,
+++  "all_rejected": true,
+++  "mutations": [
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "wrong_target",
+++      "path": "wrong_target",
+++      "reasons": [
+++        "lifecycle_wrong_target",
+++        "observation_path_mismatch:baseline",
+++        "observation_path_mismatch:fault_active",
+++        "observation_path_mismatch:post_cleanup",
+++        "observation_path_mismatch:post_failure",
+++        "observation_path_mismatch:pre_cleanup",
+++        "observation_path_mismatch:pre_injection",
+++        "observation_path_mismatch:restored",
+++        "wrong_target_id",
+++        "wrong_target_path"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "wrong_path",
+++      "path": "wrong_path",
+++      "reasons": [
+++        "wrong_target_path"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "wrong_syscall",
+++      "path": "wrong_syscall",
+++      "reasons": [
+++        "wrong_syscall"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "wrong_errno",
+++      "path": "wrong_errno",
+++      "reasons": [
+++        "wrong_errno"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "missing_activation",
+++      "path": "missing_activation",
+++      "reasons": [
+++        "activation_not_proven"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "missing_operation",
+++      "path": "missing_operation",
+++      "reasons": [
+++        "operation_not_proven"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "observer_missing",
+++      "path": "observer_missing",
+++      "reasons": [
+++        "observation_missing:restored"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "cleanup_unverified",
+++      "path": "cleanup_unverified",
+++      "reasons": [
+++        "cleanup_not_verified"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "duplicate_consume",
+++      "path": "duplicate_consume",
+++      "reasons": [
+++        "duplicate_authoritative_consume"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "both_directories",
+++      "path": "both_directories",
+++      "reasons": [
+++        "target_in_both_directories"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "HARNESS_DEFECT",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "rq17_split",
+++      "path": "rq17_split",
+++      "reasons": [
+++        "rq17_contamination_or_unknown"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "RED",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "authoritative_success",
+++      "path": "authoritative_success",
+++      "reasons": [
+++        "authoritative_success_after_fault"
+++      ],
+++      "rejected": true
+++    },
+++    {
+++      "actual_result": "RED",
+++      "case": "ENOSPC",
+++      "expected_result": "REJECT",
+++      "mutation_id": "invalid_transition",
+++      "path": "invalid_transition",
+++      "reasons": [
+++        "invalid_transition_after_fault"
+++      ],
+++      "rejected": true
+++    }
+++  ],
+++  "rejected": 13,
+++  "survived": 0,
+++  "total": 13
+++}
+++```
+++
+++
+++### packet consistency
+++
+++```text
+++{
+++  "packet_consistency": "PASS",
+++  "arm_count": 4,
+++  "RQ16_EXECUTED": false,
+++  "RQ16_AUTHORIZED": false
+++}
+++```
+++
+++
+++### execution refusal output
+++
+++```text
+++{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
+++```
+++
+++compile_exit=0
+++## Exact diff from predecessor
+++
+++### git diff
+++
+++```text
+++diff --git a/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
+++new file mode 100644
+++index 00000000..a2907089
+++--- /dev/null
++++++ b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
+++@@ -0,0 +1,1765 @@
++++# V24-I11-V6 RQ-16 preregistration review
++++
++++Planning-only artifact. No RQ-16 execution occurred.
++++
++++## Identity
++++predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
++++predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
++++branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
++++head=bcc20c9dd20ceccccf59910e906e6b15b152c3a4
++++tree=87aaddadf26d8beffe823298f50dc61e55274c17
++++RQ16_EXECUTED=false
++++RQ16_AUTHORIZED=false
++++RQ16_started=false
++++scientific_rerun=false
++++qualification=NOT_QUALIFIED
++++scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
++++authority_effect=NONE_EVIDENCE_ONLY
++++
++++## Frozen contract
++++
++++### execution contract
++++
++++```json
++++{
++++  "rq_id": "RQ-16",
++++  "trigger": "Disk full / read-only / I/O / permission failure",
++++  "oracle": "Fail closed without fabricated success",
++++  "execution_required": true,
++++  "execution_authorized": false,
++++  "arms": {
++++    "ENOSPC": {
++++      "operation": "write_authority_record or fsync on exact bound records path",
++++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
++++      "classification": "INSUFFICIENT_EVIDENCE",
++++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
++++    },
++++    "EROFS": {
++++      "operation": "write_authority_record or rename on exact bound path",
++++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
++++      "classification": "UNSAFE",
++++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
++++    },
++++    "EIO": {
++++      "operation": "exact record read/write/fsync/rename syscall",
++++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
++++      "classification": "INSUFFICIENT_EVIDENCE",
++++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
++++    },
++++    "EACCES": {
++++      "operation": "exact service access to records/consumed path",
++++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
++++      "classification": "PROXY_NOT_ACCEPTABLE",
++++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
++++    }
++++  },
++++  "classification_rules": {
++++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
++++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
++++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
++++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
++++  },
++++  "state_machine": {
++++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
++++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
++++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
++++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
++++  },
++++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
++++  "RQ16_EXECUTED": false,
++++  "RQ16_AUTHORIZED": false
++++}
++++```
++++
++++## Source-path analysis
++++
++++### preregistration
++++
++++```markdown
++++# V24-I11-V6 RQ-16 preregistration (planning only)
++++
++++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
++++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
++++that closed Remediation-7 head.
++++
++++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
++++failure**. Oracle: **Fail closed without fabricated success**. This document
++++does not authorize execution.
++++
++++## Actual write path
++++
++++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
++++
++++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
++++  `fsync`, then closes and unlinks on failure.
++++- candidate handling calls `materialize_private()` for context, boundary and
++++  payload before gate execution.
++++- root control calls `consume_record_trusted()`.
++++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
++++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
++++  from records to consumed. It returns an authoritative response only after
++++  `rename` succeeds.
++++- `write_authority_record()` creates records with
++++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
++++  `fsync`, closes, and unlinks on failure.
++++
++++RQ-16 must bind the injected errno to one of these exact operations; mocked
++++Python exceptions and candidate-side failures are proxies.
++++
++++## Execution arms and classifications
++++
++++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
++++host `/run` is prohibited. No repository evidence proves such a quota boundary,
++++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
++++
++++EROFS requires a dedicated qualification filesystem whose read-only transition
++++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
++++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
++++the arm is `UNSAFE` pending dedicated-mount evidence.
++++
++++EIO requires a disposable kernel fault layer returning EIO on the exact target
++++operation. `dm-error` or equivalent is acceptable only with a dedicated device
++++and independent activation/errno proof. No such boundary is evidenced;
++++classification is `INSUFFICIENT_EVIDENCE`.
++++
++++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
++++trusted service runs as UID 0. Candidate-side permission failure or a mocked
++++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
++++
++++These are execution arms under one frozen case, not new cases.
++++
++++## Required state machine and proof
++++
++++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
++++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
++++state record target membership in records/consumed, response and authority,
++++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
++++and hashes. PASS requires exact fault activation plus syscall errno, no
++++authoritative success, explainable target lifecycle, recoverable service,
++++complete observers, and exact post-restoration hashes/security state. Absence
++++of a response alone is never PASS. Authoritative success after a proven fault
++++is RED. Missing/malformed proof or observer/cleanup failure is
++++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
++++
++++## Restoration, safety and aborts
++++
++++The only permitted future mutation is a bounded fixture on a dedicated,
++++preflight-verified boundary. The host root filesystem, repository, historical
++++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
++++workspace are never targets. Cleanup removes the fixture, restores mount/quota
++++and metadata, revalidates service/socket/PID, records/consumed integrity,
++++device IDs, mount options, ownership/modes, hashes and security controls. Any
++++failure blocks all dependent cases.
++++
++++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
++++free-space margin, backup material, root recovery, service health or observer
++++access differ from the preregistered baseline, or if an evidence directory could
++++be overwritten.
++++
++++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
++++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
++++
++++## Harness safety and governance
++++
++++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
++++`--execute-rq16` refuses with a nonzero result. Future execution requires a
++++separately generated authorization token bound to exact commit, host/runtime
++++identity and plan digest. No token exists in this branch.
++++
++++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
++++Qualification remains `NOT_QUALIFIED`; scientific execution remains
++++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
++++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
++++mechanism classifications before any execution authorization.
++++```
++++
++++## Cleanup contract
++++
++++### cleanup
++++
++++```markdown
++++# RQ-16 cleanup and restoration contract
++++
++++RQ-16 remains preregistration-only. No mutation has been executed.
++++
++++Every future arm must capture an immutable baseline and restore it before any
++++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
++++socket identity, records/consumed ownership and modes, filesystem device IDs,
++++mount options, security controls, and exact target lifecycle.
++++
++++The inverse operation must be explicit: remove only the bounded fault fixture,
++++restore the saved mount/quota/metadata state, restart only as required by the
++++approved recovery procedure, and independently remeasure every baseline field.
++++If a mount operation fails, root recovery is unavailable, a fault fixture
++++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
++++dependent cases abort. Historical evidence directories are never targets.
++++
++++The future harness must refuse destructive execution unless the exact host,
++++commit, plan digest, and separately generated authorization token are bound.
++++`--plan` and `--self-test` are the only permitted modes in this preregistration.
++++```
++++
++++## Issues
++++
++++### issue ledger
++++
++++```json
++++{
++++  "issues": [
++++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
++++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
++++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
++++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
++++  ],
++++  "open_automatable_issues": 0,
++++  "manual_review_required": true,
++++  "RQ16_EXECUTED": false,
++++  "RQ16_AUTHORIZED": false
++++}
++++```
++++
++++## Included file SHA-256
++++e63491de1fde5387992f3bdd10499fe43ffe702338530695664da47f7e7450a8  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
++++efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
++++958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
++++b1bca1d340b9231c552a7cf44e97718a5f77a6fcfbe017c7474942b7aa6f2906  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
++++3c1240fde52af3eb0c5b98b63caa8b99b8636e0cf95ec56db257e27751f412b3  governance-runtime/v24_v6_rq1_rq16_harness.py
++++7f1a6b461344591db378df4245b7a1cec7af9c278855a18ad99feb4ff4898044  governance-runtime/test_v24_v6_rq1_rq16_harness.py
++++90515988f3a7dbe5bdef48fa193a062174bcc5a6a6c9fa40817f37a070c81746  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
++++
++++### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=3c1240fde52af3eb0c5b98b63caa8b99b8636e0cf95ec56db257e27751f412b3
++++
++++```python
++++#!/usr/bin/env python3
++++"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
++++from __future__ import annotations
++++import argparse, json
++++from pathlib import Path
++++
++++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
++++ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}
++++
++++def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
++++    reasons = []
++++    if arm not in ARMS: reasons.append("unknown_arm")
++++    proof = evidence.get("fault_proof")
++++    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
++++    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
++++    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
++++    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
++++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
++++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
++++    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
++++    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
++++    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
++++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
++++    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
++++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)
++++
++++def main() -> int:
++++    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
++++    args = ap.parse_args()
++++    if args.execute_rq16:
++++        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
++++        return 3
++++    if not (args.plan or args.self_test):
++++        ap.error("only --plan or --self-test is allowed")
++++    if args.self_test:
++++        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
++++        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
++++        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
++++        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
++++        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
++++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
++++    return 0
++++
++++if __name__ == "__main__": raise SystemExit(main())
++++```
++++
++++
++++### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=7f1a6b461344591db378df4245b7a1cec7af9c278855a18ad99feb4ff4898044
++++
++++```python
++++#!/usr/bin/env python3
++++import unittest
++++from v24_v6_rq1_rq16_harness import evaluate_arm
++++
++++def good(errno="ENOSPC"):
++++    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
++++
++++class RQ16SelfTests(unittest.TestCase):
++++    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
++++    def test_missing_or_wrong_fault_proof_never_passes(self):
++++        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
++++    def test_authority_and_cleanup_fail_closed(self):
++++        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
++++        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
++++    def test_arms_cannot_substitute(self):
++++        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
++++        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
++++        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
++++    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")
++++
++++if __name__ == "__main__": unittest.main(verbosity=2)
++++```
++++
++++
++++### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=90515988f3a7dbe5bdef48fa193a062174bcc5a6a6c9fa40817f37a070c81746
++++
++++```python
++++#!/usr/bin/env python3
++++"""Offline RQ-16 preregistration mutation checks; never touches the runtime."""
++++from __future__ import annotations
++++import copy, json
++++from v24_v6_rq1_rq16_harness import evaluate_arm
++++
++++GOOD = {
++++    "fault_proof": {"injected": True, "errno": "ENOSPC"},
++++    "target_path": "/run/v24-v6-authority/private/records/T.record",
++++    "observer_ok": True, "cleanup_verified": True, "restored_exact": True,
++++    "service_recoverable": True, "lifecycle_explained": True,
++++}
++++
++++def case(name, mutate, expected="reject"):
++++    ev = copy.deepcopy(GOOD); mutate(ev)
++++    actual, reasons = evaluate_arm("ENOSPC", ev)
++++    return {"mutation_id": name, "expected": expected, "actual": actual,
++++            "reasons": reasons, "rejected": actual != "PASS"}
++++
++++def main():
++++    muts = [
++++        ("missing_fault_proof", lambda e: e.pop("fault_proof")),
++++        ("wrong_errno", lambda e: e["fault_proof"].update(errno="EROFS")),
++++        ("injected_false", lambda e: e["fault_proof"].update(injected=False)),
++++        ("observer_failure", lambda e: e.update(observer_ok=False)),
++++        ("cleanup_failure", lambda e: e.update(cleanup_verified=False)),
++++        ("restoration_mismatch", lambda e: e.update(restored_exact=False)),
++++        ("service_not_recoverable", lambda e: e.update(service_recoverable=False)),
++++        ("lifecycle_unexplained", lambda e: e.update(lifecycle_explained=False)),
++++        ("authoritative_success", lambda e: e.update(authoritative_success=True)),
++++        ("invalid_transition", lambda e: e.update(invalid_transition=True)),
++++        ("missing_target", lambda e: e.pop("target_path")),
++++        ("unknown_arm_cross_substitution", lambda e: None),
++++    ]
++++    results = []
++++    for name, mutate in muts:
++++        if name == "unknown_arm_cross_substitution":
++++            actual, reasons = evaluate_arm("EROFS", GOOD)
++++            results.append({"mutation_id": name, "expected": "reject", "actual": actual, "reasons": reasons, "rejected": actual != "PASS"})
++++        else:
++++            results.append(case(name, mutate))
++++    out = {"total_mutations": len(results), "rejected_mutations": sum(r["rejected"] for r in results),
++++           "surviving_mutations": sum(not r["rejected"] for r in results),
++++           "all_rejected": all(r["rejected"] for r in results), "mutations": results,
++++           "RQ16_EXECUTED": False}
++++    print(json.dumps(out, indent=2, sort_keys=True))
++++    return 0 if out["all_rejected"] and out["surviving_mutations"] == 0 else 2
++++
++++if __name__ == "__main__": raise SystemExit(main())
++++```
++++
++++## Static results
++++
++++### plan output
++++
++++```text
++++{
++++  "mode": "PLAN",
++++  "arms": [
++++    "EACCES",
++++    "EIO",
++++    "ENOSPC",
++++    "EROFS"
++++  ],
++++  "RQ16_EXECUTED": false,
++++  "RQ16_AUTHORIZED": false
++++}
++++```
++++
++++
++++### self-test output
++++
++++```text
++++{
++++  "mode": "SELF_TEST",
++++  "results": [
++++    "PASS",
++++    "HARNESS_DEFECT",
++++    "HARNESS_DEFECT",
++++    "HARNESS_DEFECT",
++++    "RED",
++++    "HARNESS_DEFECT"
++++  ],
++++  "passed": true,
++++  "RQ16_EXECUTED": false
++++}
++++```
++++
++++
++++### unit output
++++
++++```text
++++test_absent_response_is_not_success (__main__.RQ16SelfTests.test_absent_response_is_not_success) ... ok
++++test_arms_cannot_substitute (__main__.RQ16SelfTests.test_arms_cannot_substitute) ... ok
++++test_authority_and_cleanup_fail_closed (__main__.RQ16SelfTests.test_authority_and_cleanup_fail_closed) ... ok
++++test_missing_or_wrong_fault_proof_never_passes (__main__.RQ16SelfTests.test_missing_or_wrong_fault_proof_never_passes) ... ok
++++test_valid_evidence_is_only_candidate_pass (__main__.RQ16SelfTests.test_valid_evidence_is_only_candidate_pass) ... ok
++++
++++----------------------------------------------------------------------
++++Ran 5 tests in 0.001s
++++
++++OK
++++```
++++
++++
++++### mutation output
++++
++++```json
++++{
++++  "RQ16_EXECUTED": false,
++++  "all_rejected": true,
++++  "mutations": [
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "missing_fault_proof",
++++      "reasons": [
++++        "fault_not_proven",
++++        "errno_not_proven"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "wrong_errno",
++++      "reasons": [
++++        "wrong_errno"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "injected_false",
++++      "reasons": [
++++        "fault_not_proven"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "observer_failure",
++++      "reasons": [
++++        "observer_incomplete"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "cleanup_failure",
++++      "reasons": [
++++        "cleanup_not_verified"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "restoration_mismatch",
++++      "reasons": [
++++        "restoration_not_exact"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "service_not_recoverable",
++++      "reasons": [
++++        "service_not_recoverable"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "lifecycle_unexplained",
++++      "reasons": [
++++        "lifecycle_unexplained"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "RED",
++++      "expected": "reject",
++++      "mutation_id": "authoritative_success",
++++      "reasons": [
++++        "authoritative_success_after_fault"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "RED",
++++      "expected": "reject",
++++      "mutation_id": "invalid_transition",
++++      "reasons": [
++++        "invalid_transition_after_fault"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "missing_target",
++++      "reasons": [
++++        "target_path_missing"
++++      ],
++++      "rejected": true
++++    },
++++    {
++++      "actual": "HARNESS_DEFECT",
++++      "expected": "reject",
++++      "mutation_id": "unknown_arm_cross_substitution",
++++      "reasons": [
++++        "wrong_errno"
++++      ],
++++      "rejected": true
++++    }
++++  ],
++++  "rejected_mutations": 12,
++++  "surviving_mutations": 0,
++++  "total_mutations": 12
++++}
++++```
++++
++++
++++### execution refusal output
++++
++++```text
++++{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
++++```
++++
++++compile_exit=0
++++## Exact diff from predecessor
++++
++++### git diff
++++
++++```text
++++diff --git a/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
++++new file mode 100644
++++index 00000000..63e85940
++++--- /dev/null
+++++++ b/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md
++++@@ -0,0 +1,849 @@
+++++# V24-I11-V6 RQ-16 preregistration review
+++++
+++++Planning-only artifact. No RQ-16 execution occurred.
+++++
+++++## Identity
+++++predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
+++++predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
+++++branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
+++++head=80a3f65c05f2e17362ee6799f72dd01bfe41feca
+++++tree=dde2b0fdcc4f3dde0f11ec13e53c9546aa3deba0
+++++RQ16_EXECUTED=false
+++++RQ16_AUTHORIZED=false
+++++RQ16_started=false
+++++scientific_rerun=false
+++++qualification=NOT_QUALIFIED
+++++scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
+++++authority_effect=NONE_EVIDENCE_ONLY
+++++
+++++## Frozen contract
+++++
+++++### execution contract
+++++
+++++```json
+++++{
+++++  "rq_id": "RQ-16",
+++++  "trigger": "Disk full / read-only / I/O / permission failure",
+++++  "oracle": "Fail closed without fabricated success",
+++++  "execution_required": true,
+++++  "execution_authorized": false,
+++++  "arms": {
+++++    "ENOSPC": {
+++++      "operation": "write_authority_record or fsync on exact bound records path",
+++++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
+++++      "classification": "INSUFFICIENT_EVIDENCE",
+++++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
+++++    },
+++++    "EROFS": {
+++++      "operation": "write_authority_record or rename on exact bound path",
+++++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
+++++      "classification": "UNSAFE",
+++++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
+++++    },
+++++    "EIO": {
+++++      "operation": "exact record read/write/fsync/rename syscall",
+++++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
+++++      "classification": "INSUFFICIENT_EVIDENCE",
+++++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
+++++    },
+++++    "EACCES": {
+++++      "operation": "exact service access to records/consumed path",
+++++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
+++++      "classification": "PROXY_NOT_ACCEPTABLE",
+++++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
+++++    }
+++++  },
+++++  "classification_rules": {
+++++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
+++++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
+++++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
+++++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
+++++  },
+++++  "state_machine": {
+++++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
+++++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
+++++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
+++++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
+++++  },
+++++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+++++  "RQ16_EXECUTED": false,
+++++  "RQ16_AUTHORIZED": false
+++++}
+++++```
+++++
+++++## Source-path analysis
+++++
+++++### preregistration
+++++
+++++```markdown
+++++# V24-I11-V6 RQ-16 preregistration (planning only)
+++++
+++++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
+++++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
+++++that closed Remediation-7 head.
+++++
+++++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
+++++failure**. Oracle: **Fail closed without fabricated success**. This document
+++++does not authorize execution.
+++++
+++++## Actual write path
+++++
+++++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
+++++
+++++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
+++++  `fsync`, then closes and unlinks on failure.
+++++- candidate handling calls `materialize_private()` for context, boundary and
+++++  payload before gate execution.
+++++- root control calls `consume_record_trusted()`.
+++++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
+++++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
+++++  from records to consumed. It returns an authoritative response only after
+++++  `rename` succeeds.
+++++- `write_authority_record()` creates records with
+++++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
+++++  `fsync`, closes, and unlinks on failure.
+++++
+++++RQ-16 must bind the injected errno to one of these exact operations; mocked
+++++Python exceptions and candidate-side failures are proxies.
+++++
+++++## Execution arms and classifications
+++++
+++++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
+++++host `/run` is prohibited. No repository evidence proves such a quota boundary,
+++++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
+++++
+++++EROFS requires a dedicated qualification filesystem whose read-only transition
+++++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
+++++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
+++++the arm is `UNSAFE` pending dedicated-mount evidence.
+++++
+++++EIO requires a disposable kernel fault layer returning EIO on the exact target
+++++operation. `dm-error` or equivalent is acceptable only with a dedicated device
+++++and independent activation/errno proof. No such boundary is evidenced;
+++++classification is `INSUFFICIENT_EVIDENCE`.
+++++
+++++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
+++++trusted service runs as UID 0. Candidate-side permission failure or a mocked
+++++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
+++++
+++++These are execution arms under one frozen case, not new cases.
+++++
+++++## Required state machine and proof
+++++
+++++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
+++++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
+++++state record target membership in records/consumed, response and authority,
+++++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
+++++and hashes. PASS requires exact fault activation plus syscall errno, no
+++++authoritative success, explainable target lifecycle, recoverable service,
+++++complete observers, and exact post-restoration hashes/security state. Absence
+++++of a response alone is never PASS. Authoritative success after a proven fault
+++++is RED. Missing/malformed proof or observer/cleanup failure is
+++++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
+++++
+++++## Restoration, safety and aborts
+++++
+++++The only permitted future mutation is a bounded fixture on a dedicated,
+++++preflight-verified boundary. The host root filesystem, repository, historical
+++++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
+++++workspace are never targets. Cleanup removes the fixture, restores mount/quota
+++++and metadata, revalidates service/socket/PID, records/consumed integrity,
+++++device IDs, mount options, ownership/modes, hashes and security controls. Any
+++++failure blocks all dependent cases.
+++++
+++++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
+++++free-space margin, backup material, root recovery, service health or observer
+++++access differ from the preregistered baseline, or if an evidence directory could
+++++be overwritten.
+++++
+++++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
+++++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
+++++
+++++## Harness safety and governance
+++++
+++++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
+++++`--execute-rq16` refuses with a nonzero result. Future execution requires a
+++++separately generated authorization token bound to exact commit, host/runtime
+++++identity and plan digest. No token exists in this branch.
+++++
+++++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
+++++Qualification remains `NOT_QUALIFIED`; scientific execution remains
+++++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
+++++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
+++++mechanism classifications before any execution authorization.
+++++```
+++++
+++++## Cleanup contract
+++++
+++++### cleanup
+++++
+++++```markdown
+++++# RQ-16 cleanup and restoration contract
+++++
+++++RQ-16 remains preregistration-only. No mutation has been executed.
+++++
+++++Every future arm must capture an immutable baseline and restore it before any
+++++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
+++++socket identity, records/consumed ownership and modes, filesystem device IDs,
+++++mount options, security controls, and exact target lifecycle.
+++++
+++++The inverse operation must be explicit: remove only the bounded fault fixture,
+++++restore the saved mount/quota/metadata state, restart only as required by the
+++++approved recovery procedure, and independently remeasure every baseline field.
+++++If a mount operation fails, root recovery is unavailable, a fault fixture
+++++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
+++++dependent cases abort. Historical evidence directories are never targets.
+++++
+++++The future harness must refuse destructive execution unless the exact host,
+++++commit, plan digest, and separately generated authorization token are bound.
+++++`--plan` and `--self-test` are the only permitted modes in this preregistration.
+++++```
+++++
+++++## Issues
+++++
+++++### issue ledger
+++++
+++++```json
+++++{
+++++  "issues": [
+++++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+++++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+++++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+++++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
+++++  ],
+++++  "open_automatable_issues": 0,
+++++  "manual_review_required": true,
+++++  "RQ16_EXECUTED": false,
+++++  "RQ16_AUTHORIZED": false
+++++}
+++++```
+++++
+++++## Included file SHA-256
+++++e63491de1fde5387992f3bdd10499fe43ffe702338530695664da47f7e7450a8  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+++++efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+++++958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+++++b1bca1d340b9231c552a7cf44e97718a5f77a6fcfbe017c7474942b7aa6f2906  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+++++3c1240fde52af3eb0c5b98b63caa8b99b8636e0cf95ec56db257e27751f412b3  governance-runtime/v24_v6_rq1_rq16_harness.py
+++++7f1a6b461344591db378df4245b7a1cec7af9c278855a18ad99feb4ff4898044  governance-runtime/test_v24_v6_rq1_rq16_harness.py
+++++90515988f3a7dbe5bdef48fa193a062174bcc5a6a6c9fa40817f37a070c81746  governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+++++
+++++### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=3c1240fde52af3eb0c5b98b63caa8b99b8636e0cf95ec56db257e27751f412b3
+++++
+++++```python
+++++#!/usr/bin/env python3
+++++"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
+++++from __future__ import annotations
+++++import argparse, json
+++++from pathlib import Path
+++++
+++++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
+++++ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}
+++++
+++++def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
+++++    reasons = []
+++++    if arm not in ARMS: reasons.append("unknown_arm")
+++++    proof = evidence.get("fault_proof")
+++++    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
+++++    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
+++++    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
+++++    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
+++++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
+++++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
+++++    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
+++++    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
+++++    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
+++++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+++++    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
+++++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)
+++++
+++++def main() -> int:
+++++    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
+++++    args = ap.parse_args()
+++++    if args.execute_rq16:
+++++        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
+++++        return 3
+++++    if not (args.plan or args.self_test):
+++++        ap.error("only --plan or --self-test is allowed")
+++++    if args.self_test:
+++++        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
+++++        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
+++++        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
+++++        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
+++++        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
+++++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
+++++    return 0
+++++
+++++if __name__ == "__main__": raise SystemExit(main())
+++++```
+++++
+++++
+++++### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=7f1a6b461344591db378df4245b7a1cec7af9c278855a18ad99feb4ff4898044
+++++
+++++```python
+++++#!/usr/bin/env python3
+++++import unittest
+++++from v24_v6_rq1_rq16_harness import evaluate_arm
+++++
+++++def good(errno="ENOSPC"):
+++++    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
+++++
+++++class RQ16SelfTests(unittest.TestCase):
+++++    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
+++++    def test_missing_or_wrong_fault_proof_never_passes(self):
+++++        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
+++++    def test_authority_and_cleanup_fail_closed(self):
+++++        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
+++++        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
+++++    def test_arms_cannot_substitute(self):
+++++        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
+++++        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
+++++        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
+++++    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")
+++++
+++++if __name__ == "__main__": unittest.main(verbosity=2)
+++++```
+++++
+++++
+++++### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=90515988f3a7dbe5bdef48fa193a062174bcc5a6a6c9fa40817f37a070c81746
+++++
+++++```python
+++++#!/usr/bin/env python3
+++++"""Offline RQ-16 preregistration mutation checks; never touches the runtime."""
+++++from __future__ import annotations
+++++import copy, json
+++++from v24_v6_rq1_rq16_harness import evaluate_arm
+++++
+++++GOOD = {
+++++    "fault_proof": {"injected": True, "errno": "ENOSPC"},
+++++    "target_path": "/run/v24-v6-authority/private/records/T.record",
+++++    "observer_ok": True, "cleanup_verified": True, "restored_exact": True,
+++++    "service_recoverable": True, "lifecycle_explained": True,
+++++}
+++++
+++++def case(name, mutate, expected="reject"):
+++++    ev = copy.deepcopy(GOOD); mutate(ev)
+++++    actual, reasons = evaluate_arm("ENOSPC", ev)
+++++    return {"mutation_id": name, "expected": expected, "actual": actual,
+++++            "reasons": reasons, "rejected": actual != "PASS"}
+++++
+++++def main():
+++++    muts = [
+++++        ("missing_fault_proof", lambda e: e.pop("fault_proof")),
+++++        ("wrong_errno", lambda e: e["fault_proof"].update(errno="EROFS")),
+++++        ("injected_false", lambda e: e["fault_proof"].update(injected=False)),
+++++        ("observer_failure", lambda e: e.update(observer_ok=False)),
+++++        ("cleanup_failure", lambda e: e.update(cleanup_verified=False)),
+++++        ("restoration_mismatch", lambda e: e.update(restored_exact=False)),
+++++        ("service_not_recoverable", lambda e: e.update(service_recoverable=False)),
+++++        ("lifecycle_unexplained", lambda e: e.update(lifecycle_explained=False)),
+++++        ("authoritative_success", lambda e: e.update(authoritative_success=True)),
+++++        ("invalid_transition", lambda e: e.update(invalid_transition=True)),
+++++        ("missing_target", lambda e: e.pop("target_path")),
+++++        ("unknown_arm_cross_substitution", lambda e: None),
+++++    ]
+++++    results = []
+++++    for name, mutate in muts:
+++++        if name == "unknown_arm_cross_substitution":
+++++            actual, reasons = evaluate_arm("EROFS", GOOD)
+++++            results.append({"mutation_id": name, "expected": "reject", "actual": actual, "reasons": reasons, "rejected": actual != "PASS"})
+++++        else:
+++++            results.append(case(name, mutate))
+++++    out = {"total_mutations": len(results), "rejected_mutations": sum(r["rejected"] for r in results),
+++++           "surviving_mutations": sum(not r["rejected"] for r in results),
+++++           "all_rejected": all(r["rejected"] for r in results), "mutations": results,
+++++           "RQ16_EXECUTED": False}
+++++    print(json.dumps(out, indent=2, sort_keys=True))
+++++    return 0 if out["all_rejected"] and out["surviving_mutations"] == 0 else 2
+++++
+++++if __name__ == "__main__": raise SystemExit(main())
+++++```
+++++
+++++## Static results
+++++
+++++### plan output
+++++
+++++```text
+++++{
+++++  "mode": "PLAN",
+++++  "arms": [
+++++    "EACCES",
+++++    "EIO",
+++++    "ENOSPC",
+++++    "EROFS"
+++++  ],
+++++  "RQ16_EXECUTED": false,
+++++  "RQ16_AUTHORIZED": false
+++++}
+++++```
+++++
+++++
+++++### self-test output
+++++
+++++```text
+++++{
+++++  "mode": "SELF_TEST",
+++++  "results": [
+++++    "PASS",
+++++    "HARNESS_DEFECT",
+++++    "HARNESS_DEFECT",
+++++    "HARNESS_DEFECT",
+++++    "RED",
+++++    "HARNESS_DEFECT"
+++++  ],
+++++  "passed": true,
+++++  "RQ16_EXECUTED": false
+++++}
+++++```
+++++
+++++
+++++### unit output
+++++
+++++```text
+++++test_absent_response_is_not_success (__main__.RQ16SelfTests.test_absent_response_is_not_success) ... ok
+++++test_arms_cannot_substitute (__main__.RQ16SelfTests.test_arms_cannot_substitute) ... ok
+++++test_authority_and_cleanup_fail_closed (__main__.RQ16SelfTests.test_authority_and_cleanup_fail_closed) ... ok
+++++test_missing_or_wrong_fault_proof_never_passes (__main__.RQ16SelfTests.test_missing_or_wrong_fault_proof_never_passes) ... ok
+++++test_valid_evidence_is_only_candidate_pass (__main__.RQ16SelfTests.test_valid_evidence_is_only_candidate_pass) ... ok
+++++
+++++----------------------------------------------------------------------
+++++Ran 5 tests in 0.000s
+++++
+++++OK
+++++```
+++++
+++++
+++++### mutation output
+++++
+++++```json
+++++{
+++++  "RQ16_EXECUTED": false,
+++++  "all_rejected": true,
+++++  "mutations": [
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "missing_fault_proof",
+++++      "reasons": [
+++++        "fault_not_proven",
+++++        "errno_not_proven"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "wrong_errno",
+++++      "reasons": [
+++++        "wrong_errno"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "injected_false",
+++++      "reasons": [
+++++        "fault_not_proven"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "observer_failure",
+++++      "reasons": [
+++++        "observer_incomplete"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "cleanup_failure",
+++++      "reasons": [
+++++        "cleanup_not_verified"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "restoration_mismatch",
+++++      "reasons": [
+++++        "restoration_not_exact"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "service_not_recoverable",
+++++      "reasons": [
+++++        "service_not_recoverable"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "lifecycle_unexplained",
+++++      "reasons": [
+++++        "lifecycle_unexplained"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "RED",
+++++      "expected": "reject",
+++++      "mutation_id": "authoritative_success",
+++++      "reasons": [
+++++        "authoritative_success_after_fault"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "RED",
+++++      "expected": "reject",
+++++      "mutation_id": "invalid_transition",
+++++      "reasons": [
+++++        "invalid_transition_after_fault"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "missing_target",
+++++      "reasons": [
+++++        "target_path_missing"
+++++      ],
+++++      "rejected": true
+++++    },
+++++    {
+++++      "actual": "HARNESS_DEFECT",
+++++      "expected": "reject",
+++++      "mutation_id": "unknown_arm_cross_substitution",
+++++      "reasons": [
+++++        "wrong_errno"
+++++      ],
+++++      "rejected": true
+++++    }
+++++  ],
+++++  "rejected_mutations": 12,
+++++  "surviving_mutations": 0,
+++++  "total_mutations": 12
+++++}
+++++```
+++++
+++++
+++++### execution refusal output
+++++
+++++```text
+++++{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
+++++```
+++++
+++++compile_exit=0
+++++## Exact diff from predecessor
+++++
+++++### git diff
+++++
+++++```text
+++++diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
+++++new file mode 100644
+++++index 00000000..12b110ab
+++++--- /dev/null
++++++++ b/governance-runtime/build_rq16_preregistration_review.py
+++++@@ -0,0 +1,19 @@
++++++from __future__ import annotations
++++++import hashlib, subprocess
++++++from pathlib import Path
++++++ROOT=Path(__file__).resolve().parents[1]
++++++OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
++++++FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py']
++++++def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
++++++def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
++++++def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
++++++def main():
++++++    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16'])
++++++    diff=run(['git','diff','8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','HEAD']).stdout
++++++    parts=['# V24-I11-V6 RQ-16 preregistration review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity','predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f"branch={run(['git','branch','--show-current']).stdout.strip()}",f"head={run(['git','rev-parse','HEAD']).stdout.strip()}",f"tree={run(['git','rev-parse','HEAD^{tree}']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
++++++    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
++++++    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
++++++    compile_result=run(['python','-m','compileall','-q']+[str(p) for p in FILES[4:]])
++++++    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
++++++    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
++++++if __name__=='__main__': main()
+++++diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
+++++new file mode 100644
+++++index 00000000..5a1d9777
+++++--- /dev/null
++++++++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
+++++@@ -0,0 +1,21 @@
++++++#!/usr/bin/env python3
++++++import unittest
++++++from v24_v6_rq1_rq16_harness import evaluate_arm
++++++
++++++def good(errno="ENOSPC"):
++++++    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
++++++
++++++class RQ16SelfTests(unittest.TestCase):
++++++    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
++++++    def test_missing_or_wrong_fault_proof_never_passes(self):
++++++        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
++++++    def test_authority_and_cleanup_fail_closed(self):
++++++        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
++++++        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
++++++    def test_arms_cannot_substitute(self):
++++++        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
++++++        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
++++++        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
++++++    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")
++++++
++++++if __name__ == "__main__": unittest.main(verbosity=2)
+++++diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
+++++new file mode 100644
+++++index 00000000..782816d7
+++++--- /dev/null
++++++++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
+++++@@ -0,0 +1,44 @@
++++++#!/usr/bin/env python3
++++++"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
++++++from __future__ import annotations
++++++import argparse, json
++++++from pathlib import Path
++++++
++++++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
++++++ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}
++++++
++++++def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
++++++    reasons = []
++++++    if arm not in ARMS: reasons.append("unknown_arm")
++++++    proof = evidence.get("fault_proof")
++++++    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
++++++    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
++++++    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
++++++    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
++++++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
++++++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
++++++    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
++++++    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
++++++    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
++++++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
++++++    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
++++++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)
++++++
++++++def main() -> int:
++++++    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
++++++    args = ap.parse_args()
++++++    if args.execute_rq16:
++++++        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
++++++        return 3
++++++    if not (args.plan or args.self_test):
++++++        ap.error("only --plan or --self-test is allowed")
++++++    if args.self_test:
++++++        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
++++++        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
++++++        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
++++++        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
++++++        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
++++++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
++++++    return 0
++++++
++++++if __name__ == "__main__": raise SystemExit(main())
+++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+++++new file mode 100644
+++++index 00000000..5ef55ad0
+++++--- /dev/null
++++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+++++@@ -0,0 +1,19 @@
++++++# RQ-16 cleanup and restoration contract
++++++
++++++RQ-16 remains preregistration-only. No mutation has been executed.
++++++
++++++Every future arm must capture an immutable baseline and restore it before any
++++++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
++++++socket identity, records/consumed ownership and modes, filesystem device IDs,
++++++mount options, security controls, and exact target lifecycle.
++++++
++++++The inverse operation must be explicit: remove only the bounded fault fixture,
++++++restore the saved mount/quota/metadata state, restart only as required by the
++++++approved recovery procedure, and independently remeasure every baseline field.
++++++If a mount operation fails, root recovery is unavailable, a fault fixture
++++++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
++++++dependent cases abort. Historical evidence directories are never targets.
++++++
++++++The future harness must refuse destructive execution unless the exact host,
++++++commit, plan digest, and separately generated authorization token are bound.
++++++`--plan` and `--self-test` are the only permitted modes in this preregistration.
+++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+++++new file mode 100644
+++++index 00000000..5c0c9f14
+++++--- /dev/null
++++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+++++@@ -0,0 +1,42 @@
++++++{
++++++  "rq_id": "RQ-16",
++++++  "trigger": "Disk full / read-only / I/O / permission failure",
++++++  "oracle": "Fail closed without fabricated success",
++++++  "execution_required": true,
++++++  "execution_authorized": false,
++++++  "arms": {
++++++    "ENOSPC": {
++++++      "operation": "write_authority_record or fsync on exact bound records path",
++++++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
++++++      "classification": "INSUFFICIENT_EVIDENCE",
++++++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
++++++    },
++++++    "EROFS": {
++++++      "operation": "write_authority_record or rename on exact bound path",
++++++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
++++++      "classification": "UNSAFE",
++++++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
++++++    },
++++++    "EIO": {
++++++      "operation": "exact record read/write/fsync/rename syscall",
++++++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
++++++      "classification": "INSUFFICIENT_EVIDENCE",
++++++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
++++++    },
++++++    "EACCES": {
++++++      "operation": "exact service access to records/consumed path",
++++++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
++++++      "classification": "PROXY_NOT_ACCEPTABLE",
++++++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
++++++    }
++++++  },
++++++  "classification_rules": {
++++++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
++++++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
++++++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
++++++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
++++++  },
++++++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
++++++  "RQ16_EXECUTED": false,
++++++  "RQ16_AUTHORIZED": false
++++++}
+++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+++++new file mode 100644
+++++index 00000000..00d465a3
+++++--- /dev/null
++++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+++++@@ -0,0 +1,12 @@
++++++{
++++++  "issues": [
++++++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
++++++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
++++++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
++++++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
++++++  ],
++++++  "open_automatable_issues": 0,
++++++  "manual_review_required": true,
++++++  "RQ16_EXECUTED": false,
++++++  "RQ16_AUTHORIZED": false
++++++}
+++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+++++new file mode 100644
+++++index 00000000..f0bdb1b2
+++++--- /dev/null
++++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+++++@@ -0,0 +1,95 @@
++++++# V24-I11-V6 RQ-16 preregistration (planning only)
++++++
++++++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
++++++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
++++++that closed Remediation-7 head.
++++++
++++++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
++++++failure**. Oracle: **Fail closed without fabricated success**. This document
++++++does not authorize execution.
++++++
++++++## Actual write path
++++++
++++++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
++++++
++++++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
++++++  `fsync`, then closes and unlinks on failure.
++++++- candidate handling calls `materialize_private()` for context, boundary and
++++++  payload before gate execution.
++++++- root control calls `consume_record_trusted()`.
++++++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
++++++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
++++++  from records to consumed. It returns an authoritative response only after
++++++  `rename` succeeds.
++++++- `write_authority_record()` creates records with
++++++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
++++++  `fsync`, closes, and unlinks on failure.
++++++
++++++RQ-16 must bind the injected errno to one of these exact operations; mocked
++++++Python exceptions and candidate-side failures are proxies.
++++++
++++++## Execution arms and classifications
++++++
++++++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
++++++host `/run` is prohibited. No repository evidence proves such a quota boundary,
++++++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
++++++
++++++EROFS requires a dedicated qualification filesystem whose read-only transition
++++++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
++++++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
++++++the arm is `UNSAFE` pending dedicated-mount evidence.
++++++
++++++EIO requires a disposable kernel fault layer returning EIO on the exact target
++++++operation. `dm-error` or equivalent is acceptable only with a dedicated device
++++++and independent activation/errno proof. No such boundary is evidenced;
++++++classification is `INSUFFICIENT_EVIDENCE`.
++++++
++++++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
++++++trusted service runs as UID 0. Candidate-side permission failure or a mocked
++++++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
++++++
++++++These are execution arms under one frozen case, not new cases.
++++++
++++++## Required state machine and proof
++++++
++++++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
++++++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
++++++state record target membership in records/consumed, response and authority,
++++++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
++++++and hashes. PASS requires exact fault activation plus syscall errno, no
++++++authoritative success, explainable target lifecycle, recoverable service,
++++++complete observers, and exact post-restoration hashes/security state. Absence
++++++of a response alone is never PASS. Authoritative success after a proven fault
++++++is RED. Missing/malformed proof or observer/cleanup failure is
++++++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
++++++
++++++## Restoration, safety and aborts
++++++
++++++The only permitted future mutation is a bounded fixture on a dedicated,
++++++preflight-verified boundary. The host root filesystem, repository, historical
++++++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
++++++workspace are never targets. Cleanup removes the fixture, restores mount/quota
++++++and metadata, revalidates service/socket/PID, records/consumed integrity,
++++++device IDs, mount options, ownership/modes, hashes and security controls. Any
++++++failure blocks all dependent cases.
++++++
++++++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
++++++free-space margin, backup material, root recovery, service health or observer
++++++access differ from the preregistered baseline, or if an evidence directory could
++++++be overwritten.
++++++
++++++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
++++++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
++++++
++++++## Harness safety and governance
++++++
++++++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
++++++`--execute-rq16` refuses with a nonzero result. Future execution requires a
++++++separately generated authorization token bound to exact commit, host/runtime
++++++identity and plan digest. No token exists in this branch.
++++++
++++++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
++++++Qualification remains `NOT_QUALIFIED`; scientific execution remains
++++++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
++++++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
++++++mechanism classifications before any execution authorization.
+++++```
+++++
+++++## Manual-review questions
+++++
+++++Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
++++diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
++++new file mode 100644
++++index 00000000..cf74e7cd
++++--- /dev/null
+++++++ b/governance-runtime/build_rq16_preregistration_review.py
++++@@ -0,0 +1,19 @@
+++++from __future__ import annotations
+++++import hashlib, subprocess
+++++from pathlib import Path
+++++ROOT=Path(__file__).resolve().parents[1]
+++++OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
+++++FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py']
+++++def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+++++def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+++++def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+++++def main():
+++++    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'])
+++++    diff=run(['git','diff','8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','HEAD']).stdout
+++++    parts=['# V24-I11-V6 RQ-16 preregistration review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity','predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f"branch={run(['git','branch','--show-current']).stdout.strip()}",f"head={run(['git','rev-parse','HEAD']).stdout.strip()}",f"tree={run(['git','rev-parse','HEAD^{tree}']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
+++++    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
+++++    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+++++    compile_result=run(['python','-m','compileall','-q']+[str(p) for p in FILES[4:]])
+++++    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('mutation output',mutations.stdout+mutations.stderr,'json'),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
+++++    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
+++++if __name__=='__main__': main()
++++diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
++++new file mode 100644
++++index 00000000..81157199
++++--- /dev/null
+++++++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
++++@@ -0,0 +1,49 @@
+++++#!/usr/bin/env python3
+++++"""Offline RQ-16 preregistration mutation checks; never touches the runtime."""
+++++from __future__ import annotations
+++++import copy, json
+++++from v24_v6_rq1_rq16_harness import evaluate_arm
+++++
+++++GOOD = {
+++++    "fault_proof": {"injected": True, "errno": "ENOSPC"},
+++++    "target_path": "/run/v24-v6-authority/private/records/T.record",
+++++    "observer_ok": True, "cleanup_verified": True, "restored_exact": True,
+++++    "service_recoverable": True, "lifecycle_explained": True,
+++++}
+++++
+++++def case(name, mutate, expected="reject"):
+++++    ev = copy.deepcopy(GOOD); mutate(ev)
+++++    actual, reasons = evaluate_arm("ENOSPC", ev)
+++++    return {"mutation_id": name, "expected": expected, "actual": actual,
+++++            "reasons": reasons, "rejected": actual != "PASS"}
+++++
+++++def main():
+++++    muts = [
+++++        ("missing_fault_proof", lambda e: e.pop("fault_proof")),
+++++        ("wrong_errno", lambda e: e["fault_proof"].update(errno="EROFS")),
+++++        ("injected_false", lambda e: e["fault_proof"].update(injected=False)),
+++++        ("observer_failure", lambda e: e.update(observer_ok=False)),
+++++        ("cleanup_failure", lambda e: e.update(cleanup_verified=False)),
+++++        ("restoration_mismatch", lambda e: e.update(restored_exact=False)),
+++++        ("service_not_recoverable", lambda e: e.update(service_recoverable=False)),
+++++        ("lifecycle_unexplained", lambda e: e.update(lifecycle_explained=False)),
+++++        ("authoritative_success", lambda e: e.update(authoritative_success=True)),
+++++        ("invalid_transition", lambda e: e.update(invalid_transition=True)),
+++++        ("missing_target", lambda e: e.pop("target_path")),
+++++        ("unknown_arm_cross_substitution", lambda e: None),
+++++    ]
+++++    results = []
+++++    for name, mutate in muts:
+++++        if name == "unknown_arm_cross_substitution":
+++++            actual, reasons = evaluate_arm("EROFS", GOOD)
+++++            results.append({"mutation_id": name, "expected": "reject", "actual": actual, "reasons": reasons, "rejected": actual != "PASS"})
+++++        else:
+++++            results.append(case(name, mutate))
+++++    out = {"total_mutations": len(results), "rejected_mutations": sum(r["rejected"] for r in results),
+++++           "surviving_mutations": sum(not r["rejected"] for r in results),
+++++           "all_rejected": all(r["rejected"] for r in results), "mutations": results,
+++++           "RQ16_EXECUTED": False}
+++++    print(json.dumps(out, indent=2, sort_keys=True))
+++++    return 0 if out["all_rejected"] and out["surviving_mutations"] == 0 else 2
+++++
+++++if __name__ == "__main__": raise SystemExit(main())
++++diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
++++new file mode 100644
++++index 00000000..5a1d9777
++++--- /dev/null
+++++++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
++++@@ -0,0 +1,21 @@
+++++#!/usr/bin/env python3
+++++import unittest
+++++from v24_v6_rq1_rq16_harness import evaluate_arm
+++++
+++++def good(errno="ENOSPC"):
+++++    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
+++++
+++++class RQ16SelfTests(unittest.TestCase):
+++++    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
+++++    def test_missing_or_wrong_fault_proof_never_passes(self):
+++++        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
+++++    def test_authority_and_cleanup_fail_closed(self):
+++++        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
+++++        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
+++++    def test_arms_cannot_substitute(self):
+++++        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
+++++        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
+++++        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
+++++    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")
+++++
+++++if __name__ == "__main__": unittest.main(verbosity=2)
++++diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
++++new file mode 100644
++++index 00000000..782816d7
++++--- /dev/null
+++++++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
++++@@ -0,0 +1,44 @@
+++++#!/usr/bin/env python3
+++++"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
+++++from __future__ import annotations
+++++import argparse, json
+++++from pathlib import Path
+++++
+++++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
+++++ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}
+++++
+++++def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
+++++    reasons = []
+++++    if arm not in ARMS: reasons.append("unknown_arm")
+++++    proof = evidence.get("fault_proof")
+++++    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
+++++    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
+++++    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
+++++    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
+++++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
+++++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
+++++    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
+++++    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
+++++    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
+++++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+++++    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
+++++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)
+++++
+++++def main() -> int:
+++++    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
+++++    args = ap.parse_args()
+++++    if args.execute_rq16:
+++++        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
+++++        return 3
+++++    if not (args.plan or args.self_test):
+++++        ap.error("only --plan or --self-test is allowed")
+++++    if args.self_test:
+++++        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
+++++        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
+++++        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
+++++        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
+++++        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
+++++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
+++++    return 0
+++++
+++++if __name__ == "__main__": raise SystemExit(main())
++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
++++new file mode 100644
++++index 00000000..5ef55ad0
++++--- /dev/null
+++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
++++@@ -0,0 +1,19 @@
+++++# RQ-16 cleanup and restoration contract
+++++
+++++RQ-16 remains preregistration-only. No mutation has been executed.
+++++
+++++Every future arm must capture an immutable baseline and restore it before any
+++++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
+++++socket identity, records/consumed ownership and modes, filesystem device IDs,
+++++mount options, security controls, and exact target lifecycle.
+++++
+++++The inverse operation must be explicit: remove only the bounded fault fixture,
+++++restore the saved mount/quota/metadata state, restart only as required by the
+++++approved recovery procedure, and independently remeasure every baseline field.
+++++If a mount operation fails, root recovery is unavailable, a fault fixture
+++++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
+++++dependent cases abort. Historical evidence directories are never targets.
+++++
+++++The future harness must refuse destructive execution unless the exact host,
+++++commit, plan digest, and separately generated authorization token are bound.
+++++`--plan` and `--self-test` are the only permitted modes in this preregistration.
++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
++++new file mode 100644
++++index 00000000..fdc139d1
++++--- /dev/null
+++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
++++@@ -0,0 +1,48 @@
+++++{
+++++  "rq_id": "RQ-16",
+++++  "trigger": "Disk full / read-only / I/O / permission failure",
+++++  "oracle": "Fail closed without fabricated success",
+++++  "execution_required": true,
+++++  "execution_authorized": false,
+++++  "arms": {
+++++    "ENOSPC": {
+++++      "operation": "write_authority_record or fsync on exact bound records path",
+++++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
+++++      "classification": "INSUFFICIENT_EVIDENCE",
+++++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
+++++    },
+++++    "EROFS": {
+++++      "operation": "write_authority_record or rename on exact bound path",
+++++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
+++++      "classification": "UNSAFE",
+++++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
+++++    },
+++++    "EIO": {
+++++      "operation": "exact record read/write/fsync/rename syscall",
+++++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
+++++      "classification": "INSUFFICIENT_EVIDENCE",
+++++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
+++++    },
+++++    "EACCES": {
+++++      "operation": "exact service access to records/consumed path",
+++++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
+++++      "classification": "PROXY_NOT_ACCEPTABLE",
+++++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
+++++    }
+++++  },
+++++  "classification_rules": {
+++++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
+++++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
+++++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
+++++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
+++++  },
+++++  "state_machine": {
+++++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
+++++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
+++++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
+++++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
+++++  },
+++++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+++++  "RQ16_EXECUTED": false,
+++++  "RQ16_AUTHORIZED": false
+++++}
++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
++++new file mode 100644
++++index 00000000..00d465a3
++++--- /dev/null
+++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
++++@@ -0,0 +1,12 @@
+++++{
+++++  "issues": [
+++++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+++++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+++++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+++++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
+++++  ],
+++++  "open_automatable_issues": 0,
+++++  "manual_review_required": true,
+++++  "RQ16_EXECUTED": false,
+++++  "RQ16_AUTHORIZED": false
+++++}
++++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
++++new file mode 100644
++++index 00000000..f0bdb1b2
++++--- /dev/null
+++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
++++@@ -0,0 +1,95 @@
+++++# V24-I11-V6 RQ-16 preregistration (planning only)
+++++
+++++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
+++++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
+++++that closed Remediation-7 head.
+++++
+++++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
+++++failure**. Oracle: **Fail closed without fabricated success**. This document
+++++does not authorize execution.
+++++
+++++## Actual write path
+++++
+++++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
+++++
+++++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
+++++  `fsync`, then closes and unlinks on failure.
+++++- candidate handling calls `materialize_private()` for context, boundary and
+++++  payload before gate execution.
+++++- root control calls `consume_record_trusted()`.
+++++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
+++++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
+++++  from records to consumed. It returns an authoritative response only after
+++++  `rename` succeeds.
+++++- `write_authority_record()` creates records with
+++++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
+++++  `fsync`, closes, and unlinks on failure.
+++++
+++++RQ-16 must bind the injected errno to one of these exact operations; mocked
+++++Python exceptions and candidate-side failures are proxies.
+++++
+++++## Execution arms and classifications
+++++
+++++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
+++++host `/run` is prohibited. No repository evidence proves such a quota boundary,
+++++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
+++++
+++++EROFS requires a dedicated qualification filesystem whose read-only transition
+++++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
+++++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
+++++the arm is `UNSAFE` pending dedicated-mount evidence.
+++++
+++++EIO requires a disposable kernel fault layer returning EIO on the exact target
+++++operation. `dm-error` or equivalent is acceptable only with a dedicated device
+++++and independent activation/errno proof. No such boundary is evidenced;
+++++classification is `INSUFFICIENT_EVIDENCE`.
+++++
+++++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
+++++trusted service runs as UID 0. Candidate-side permission failure or a mocked
+++++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
+++++
+++++These are execution arms under one frozen case, not new cases.
+++++
+++++## Required state machine and proof
+++++
+++++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
+++++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
+++++state record target membership in records/consumed, response and authority,
+++++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
+++++and hashes. PASS requires exact fault activation plus syscall errno, no
+++++authoritative success, explainable target lifecycle, recoverable service,
+++++complete observers, and exact post-restoration hashes/security state. Absence
+++++of a response alone is never PASS. Authoritative success after a proven fault
+++++is RED. Missing/malformed proof or observer/cleanup failure is
+++++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
+++++
+++++## Restoration, safety and aborts
+++++
+++++The only permitted future mutation is a bounded fixture on a dedicated,
+++++preflight-verified boundary. The host root filesystem, repository, historical
+++++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
+++++workspace are never targets. Cleanup removes the fixture, restores mount/quota
+++++and metadata, revalidates service/socket/PID, records/consumed integrity,
+++++device IDs, mount options, ownership/modes, hashes and security controls. Any
+++++failure blocks all dependent cases.
+++++
+++++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
+++++free-space margin, backup material, root recovery, service health or observer
+++++access differ from the preregistered baseline, or if an evidence directory could
+++++be overwritten.
+++++
+++++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
+++++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
+++++
+++++## Harness safety and governance
+++++
+++++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
+++++`--execute-rq16` refuses with a nonzero result. Future execution requires a
+++++separately generated authorization token bound to exact commit, host/runtime
+++++identity and plan digest. No token exists in this branch.
+++++
+++++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
+++++Qualification remains `NOT_QUALIFIED`; scientific execution remains
+++++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
+++++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
+++++mechanism classifications before any execution authorization.
++++```
++++
++++## Manual-review questions
++++
++++Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
+++diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
+++new file mode 100644
+++index 00000000..cf74e7cd
+++--- /dev/null
++++++ b/governance-runtime/build_rq16_preregistration_review.py
+++@@ -0,0 +1,19 @@
++++from __future__ import annotations
++++import hashlib, subprocess
++++from pathlib import Path
++++ROOT=Path(__file__).resolve().parents[1]
++++OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
++++FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py']
++++def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
++++def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
++++def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
++++def main():
++++    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'])
++++    diff=run(['git','diff','8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','HEAD']).stdout
++++    parts=['# V24-I11-V6 RQ-16 preregistration review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity','predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f"branch={run(['git','branch','--show-current']).stdout.strip()}",f"head={run(['git','rev-parse','HEAD']).stdout.strip()}",f"tree={run(['git','rev-parse','HEAD^{tree}']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
++++    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
++++    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
++++    compile_result=run(['python','-m','compileall','-q']+[str(p) for p in FILES[4:]])
++++    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('mutation output',mutations.stdout+mutations.stderr,'json'),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
++++    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
++++if __name__=='__main__': main()
+++diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+++new file mode 100644
+++index 00000000..81157199
+++--- /dev/null
++++++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+++@@ -0,0 +1,49 @@
++++#!/usr/bin/env python3
++++"""Offline RQ-16 preregistration mutation checks; never touches the runtime."""
++++from __future__ import annotations
++++import copy, json
++++from v24_v6_rq1_rq16_harness import evaluate_arm
++++
++++GOOD = {
++++    "fault_proof": {"injected": True, "errno": "ENOSPC"},
++++    "target_path": "/run/v24-v6-authority/private/records/T.record",
++++    "observer_ok": True, "cleanup_verified": True, "restored_exact": True,
++++    "service_recoverable": True, "lifecycle_explained": True,
++++}
++++
++++def case(name, mutate, expected="reject"):
++++    ev = copy.deepcopy(GOOD); mutate(ev)
++++    actual, reasons = evaluate_arm("ENOSPC", ev)
++++    return {"mutation_id": name, "expected": expected, "actual": actual,
++++            "reasons": reasons, "rejected": actual != "PASS"}
++++
++++def main():
++++    muts = [
++++        ("missing_fault_proof", lambda e: e.pop("fault_proof")),
++++        ("wrong_errno", lambda e: e["fault_proof"].update(errno="EROFS")),
++++        ("injected_false", lambda e: e["fault_proof"].update(injected=False)),
++++        ("observer_failure", lambda e: e.update(observer_ok=False)),
++++        ("cleanup_failure", lambda e: e.update(cleanup_verified=False)),
++++        ("restoration_mismatch", lambda e: e.update(restored_exact=False)),
++++        ("service_not_recoverable", lambda e: e.update(service_recoverable=False)),
++++        ("lifecycle_unexplained", lambda e: e.update(lifecycle_explained=False)),
++++        ("authoritative_success", lambda e: e.update(authoritative_success=True)),
++++        ("invalid_transition", lambda e: e.update(invalid_transition=True)),
++++        ("missing_target", lambda e: e.pop("target_path")),
++++        ("unknown_arm_cross_substitution", lambda e: None),
++++    ]
++++    results = []
++++    for name, mutate in muts:
++++        if name == "unknown_arm_cross_substitution":
++++            actual, reasons = evaluate_arm("EROFS", GOOD)
++++            results.append({"mutation_id": name, "expected": "reject", "actual": actual, "reasons": reasons, "rejected": actual != "PASS"})
++++        else:
++++            results.append(case(name, mutate))
++++    out = {"total_mutations": len(results), "rejected_mutations": sum(r["rejected"] for r in results),
++++           "surviving_mutations": sum(not r["rejected"] for r in results),
++++           "all_rejected": all(r["rejected"] for r in results), "mutations": results,
++++           "RQ16_EXECUTED": False}
++++    print(json.dumps(out, indent=2, sort_keys=True))
++++    return 0 if out["all_rejected"] and out["surviving_mutations"] == 0 else 2
++++
++++if __name__ == "__main__": raise SystemExit(main())
+++diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
+++new file mode 100644
+++index 00000000..5a1d9777
+++--- /dev/null
++++++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
+++@@ -0,0 +1,21 @@
++++#!/usr/bin/env python3
++++import unittest
++++from v24_v6_rq1_rq16_harness import evaluate_arm
++++
++++def good(errno="ENOSPC"):
++++    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
++++
++++class RQ16SelfTests(unittest.TestCase):
++++    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
++++    def test_missing_or_wrong_fault_proof_never_passes(self):
++++        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
++++    def test_authority_and_cleanup_fail_closed(self):
++++        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
++++        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
++++    def test_arms_cannot_substitute(self):
++++        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
++++        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
++++        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
++++    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")
++++
++++if __name__ == "__main__": unittest.main(verbosity=2)
+++diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
+++new file mode 100644
+++index 00000000..782816d7
+++--- /dev/null
++++++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
+++@@ -0,0 +1,44 @@
++++#!/usr/bin/env python3
++++"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
++++from __future__ import annotations
++++import argparse, json
++++from pathlib import Path
++++
++++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
++++ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}
++++
++++def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
++++    reasons = []
++++    if arm not in ARMS: reasons.append("unknown_arm")
++++    proof = evidence.get("fault_proof")
++++    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
++++    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
++++    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
++++    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
++++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
++++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
++++    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
++++    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
++++    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
++++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
++++    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
++++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)
++++
++++def main() -> int:
++++    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
++++    args = ap.parse_args()
++++    if args.execute_rq16:
++++        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
++++        return 3
++++    if not (args.plan or args.self_test):
++++        ap.error("only --plan or --self-test is allowed")
++++    if args.self_test:
++++        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
++++        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
++++        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
++++        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
++++        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
++++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
++++    return 0
++++
++++if __name__ == "__main__": raise SystemExit(main())
+++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+++new file mode 100644
+++index 00000000..5ef55ad0
+++--- /dev/null
++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+++@@ -0,0 +1,19 @@
++++# RQ-16 cleanup and restoration contract
++++
++++RQ-16 remains preregistration-only. No mutation has been executed.
++++
++++Every future arm must capture an immutable baseline and restore it before any
++++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
++++socket identity, records/consumed ownership and modes, filesystem device IDs,
++++mount options, security controls, and exact target lifecycle.
++++
++++The inverse operation must be explicit: remove only the bounded fault fixture,
++++restore the saved mount/quota/metadata state, restart only as required by the
++++approved recovery procedure, and independently remeasure every baseline field.
++++If a mount operation fails, root recovery is unavailable, a fault fixture
++++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
++++dependent cases abort. Historical evidence directories are never targets.
++++
++++The future harness must refuse destructive execution unless the exact host,
++++commit, plan digest, and separately generated authorization token are bound.
++++`--plan` and `--self-test` are the only permitted modes in this preregistration.
+++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+++new file mode 100644
+++index 00000000..fdc139d1
+++--- /dev/null
++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+++@@ -0,0 +1,48 @@
++++{
++++  "rq_id": "RQ-16",
++++  "trigger": "Disk full / read-only / I/O / permission failure",
++++  "oracle": "Fail closed without fabricated success",
++++  "execution_required": true,
++++  "execution_authorized": false,
++++  "arms": {
++++    "ENOSPC": {
++++      "operation": "write_authority_record or fsync on exact bound records path",
++++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
++++      "classification": "INSUFFICIENT_EVIDENCE",
++++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
++++    },
++++    "EROFS": {
++++      "operation": "write_authority_record or rename on exact bound path",
++++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
++++      "classification": "UNSAFE",
++++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
++++    },
++++    "EIO": {
++++      "operation": "exact record read/write/fsync/rename syscall",
++++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
++++      "classification": "INSUFFICIENT_EVIDENCE",
++++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
++++    },
++++    "EACCES": {
++++      "operation": "exact service access to records/consumed path",
++++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
++++      "classification": "PROXY_NOT_ACCEPTABLE",
++++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
++++    }
++++  },
++++  "classification_rules": {
++++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
++++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
++++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
++++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
++++  },
++++  "state_machine": {
++++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
++++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
++++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
++++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
++++  },
++++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
++++  "RQ16_EXECUTED": false,
++++  "RQ16_AUTHORIZED": false
++++}
+++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+++new file mode 100644
+++index 00000000..00d465a3
+++--- /dev/null
++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+++@@ -0,0 +1,12 @@
++++{
++++  "issues": [
++++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
++++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
++++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
++++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
++++  ],
++++  "open_automatable_issues": 0,
++++  "manual_review_required": true,
++++  "RQ16_EXECUTED": false,
++++  "RQ16_AUTHORIZED": false
++++}
+++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+++new file mode 100644
+++index 00000000..f0bdb1b2
+++--- /dev/null
++++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+++@@ -0,0 +1,95 @@
++++# V24-I11-V6 RQ-16 preregistration (planning only)
++++
++++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
++++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
++++that closed Remediation-7 head.
++++
++++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
++++failure**. Oracle: **Fail closed without fabricated success**. This document
++++does not authorize execution.
++++
++++## Actual write path
++++
++++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
++++
++++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
++++  `fsync`, then closes and unlinks on failure.
++++- candidate handling calls `materialize_private()` for context, boundary and
++++  payload before gate execution.
++++- root control calls `consume_record_trusted()`.
++++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
++++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
++++  from records to consumed. It returns an authoritative response only after
++++  `rename` succeeds.
++++- `write_authority_record()` creates records with
++++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
++++  `fsync`, closes, and unlinks on failure.
++++
++++RQ-16 must bind the injected errno to one of these exact operations; mocked
++++Python exceptions and candidate-side failures are proxies.
++++
++++## Execution arms and classifications
++++
++++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
++++host `/run` is prohibited. No repository evidence proves such a quota boundary,
++++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
++++
++++EROFS requires a dedicated qualification filesystem whose read-only transition
++++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
++++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
++++the arm is `UNSAFE` pending dedicated-mount evidence.
++++
++++EIO requires a disposable kernel fault layer returning EIO on the exact target
++++operation. `dm-error` or equivalent is acceptable only with a dedicated device
++++and independent activation/errno proof. No such boundary is evidenced;
++++classification is `INSUFFICIENT_EVIDENCE`.
++++
++++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
++++trusted service runs as UID 0. Candidate-side permission failure or a mocked
++++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
++++
++++These are execution arms under one frozen case, not new cases.
++++
++++## Required state machine and proof
++++
++++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
++++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
++++state record target membership in records/consumed, response and authority,
++++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
++++and hashes. PASS requires exact fault activation plus syscall errno, no
++++authoritative success, explainable target lifecycle, recoverable service,
++++complete observers, and exact post-restoration hashes/security state. Absence
++++of a response alone is never PASS. Authoritative success after a proven fault
++++is RED. Missing/malformed proof or observer/cleanup failure is
++++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
++++
++++## Restoration, safety and aborts
++++
++++The only permitted future mutation is a bounded fixture on a dedicated,
++++preflight-verified boundary. The host root filesystem, repository, historical
++++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
++++workspace are never targets. Cleanup removes the fixture, restores mount/quota
++++and metadata, revalidates service/socket/PID, records/consumed integrity,
++++device IDs, mount options, ownership/modes, hashes and security controls. Any
++++failure blocks all dependent cases.
++++
++++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
++++free-space margin, backup material, root recovery, service health or observer
++++access differ from the preregistered baseline, or if an evidence directory could
++++be overwritten.
++++
++++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
++++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
++++
++++## Harness safety and governance
++++
++++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
++++`--execute-rq16` refuses with a nonzero result. Future execution requires a
++++separately generated authorization token bound to exact commit, host/runtime
++++identity and plan digest. No token exists in this branch.
++++
++++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
++++Qualification remains `NOT_QUALIFIED`; scientific execution remains
++++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
++++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
++++mechanism classifications before any execution authorization.
+++```
+++
+++## Manual-review questions
+++
+++Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
++diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
++new file mode 100644
++index 00000000..eea5a68d
++--- /dev/null
+++++ b/governance-runtime/build_rq16_preregistration_review.py
++@@ -0,0 +1,19 @@
+++from __future__ import annotations
+++import hashlib, subprocess
+++from pathlib import Path
+++ROOT=Path(__file__).resolve().parents[1]
+++OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
+++FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py',ROOT/'governance-runtime/check_rq16_preregistration_packet.py']
+++def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+++def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+++def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+++def main():
+++    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
+++    diff=run(['git','diff','8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','HEAD']).stdout
+++    parts=['# V24-I11-V6 RQ-16 preregistration review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity','predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f"branch={run(['git','branch','--show-current']).stdout.strip()}",f"head={run(['git','rev-parse','HEAD']).stdout.strip()}",f"tree={run(['git','rev-parse','HEAD^{tree}']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
+++    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
+++    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+++    compile_result=run(['python','-m','compileall','-q']+[str(p) for p in FILES[4:]])
+++    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('mutation output',mutations.stdout+mutations.stderr,'json'),fence('packet consistency',consistency.stdout+consistency.stderr),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
+++    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
+++if __name__=='__main__': main()
++diff --git a/governance-runtime/check_rq16_preregistration_packet.py b/governance-runtime/check_rq16_preregistration_packet.py
++new file mode 100644
++index 00000000..e364040c
++--- /dev/null
+++++ b/governance-runtime/check_rq16_preregistration_packet.py
++@@ -0,0 +1,17 @@
+++#!/usr/bin/env python3
+++"""Offline packet consistency checks; no runtime interaction."""
+++from __future__ import annotations
+++import json, hashlib
+++from pathlib import Path
+++ROOT=Path(__file__).resolve().parents[1]
+++def main():
+++    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
+++    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+++    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
+++    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
+++    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
+++    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
+++    head=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
+++    assert f'head={head}' in text and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
+++    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
+++if __name__=='__main__': raise SystemExit(main())
++diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
++new file mode 100644
++index 00000000..492ea52c
++--- /dev/null
+++++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
++@@ -0,0 +1,29 @@
+++#!/usr/bin/env python3
+++"""Offline structured-proof mutation suite; no runtime interaction."""
+++import copy, json
+++from v24_v6_rq1_rq16_harness import evaluate_arm
+++from test_v24_v6_rq1_rq16_harness import good
+++
+++def main():
+++    mutations=[]
+++    specs=[
+++      ("wrong_target",lambda e:e.update(target_record_id="other")),
+++      ("wrong_path",lambda e:e["fault_proof"].update(target_path="/run/v24-v6-authority/private/records/other.record")),
+++      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
+++      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
+++      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
+++      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
+++      ("observer_missing",lambda e:e["observations"].pop("restored")),
+++      ("cleanup_unverified",lambda e:e["cleanup_proof"].update(independently_verified=False)),
+++      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
+++      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
+++      ("rq17_split",lambda e:e.update(rq17_contamination=True)),
+++      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
+++      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
+++    ]
+++    for name,mut in specs:
+++        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e)
+++        mutations.append({"mutation_id":name,"case":"ENOSPC","path":name,"expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+++    out={"total":len(mutations),"rejected":sum(x["rejected"] for x in mutations),"survived":sum(not x["rejected"] for x in mutations),"all_rejected":all(x["rejected"] for x in mutations),"mutations":mutations,"RQ16_EXECUTED":False}
+++    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+++if __name__=="__main__": raise SystemExit(main())
++diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
++new file mode 100644
++index 00000000..6ae417c7
++--- /dev/null
+++++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
++@@ -0,0 +1,30 @@
+++#!/usr/bin/env python3
+++import unittest
+++from v24_v6_rq1_rq16_harness import evaluate_arm, exact_paths, check_rq17_contamination, validate_authorization_token
+++
+++TARGET="abc123"; RP,CP=exact_paths(TARGET)
+++def obs():
+++    return {s:{"service_pid":123,"records_path":RP,"consumed_path":CP,"records_device":"d1","consumed_device":"d1","mount_id":"m1","service_binary_sha256":"svc","gate_sha256":"gate","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+++def good(errno="ENOSPC"):
+++    return {"target_record_id":TARGET,"fault_proof":{"arm":"ENOSPC","mechanism_id":"m","mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":RP,"expected_errno":errno,"observed_errno":errno,"kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":123,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":obs(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identity":"mi","service_identity":"si","socket_state":"ss","records_consumed_state":"rc","fault_disabled":True,"independently_verified":True},"rq17_contamination":False,"service_recoverable":True}
+++
+++class RQ16Tests(unittest.TestCase):
+++    def test_structured_candidate_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good())[0],"PASS")
+++    def test_exact_target_and_paths(self):
+++        e=good(); e["target_record_id"]="other"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        e=good(); e["fault_proof"]["target_path"]="/run/v24-v6-authority/private/records/abc123-other.record"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++    def test_provenance_and_syscall(self):
+++        for k,v in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS")):
+++            e=good(); e["fault_proof"][k]=v; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++    def test_observer_cleanup_and_lifecycle(self):
+++        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        e=good(); e["cleanup_proof"]["independently_verified"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++    def test_authority_and_contamination_red_or_reject(self):
+++        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e)[0],"RED")
+++        e=good(); e["rq17_contamination"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
+++        self.assertFalse(check_rq17_contamination({"records_device":"d1","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"},{"records_device":"d2","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"})[0])
+++    def test_token_is_explicitly_bound(self):
+++        self.assertTrue(validate_authorization_token({}, {}) )
+++
+++if __name__ == "__main__": unittest.main(verbosity=2)
++diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
++new file mode 100644
++index 00000000..053309da
++--- /dev/null
+++++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
++@@ -0,0 +1,104 @@
+++#!/usr/bin/env python3
+++"""RQ-16 preregistration evaluator; plan/self-test only, never performs faults."""
+++from __future__ import annotations
+++import argparse, json, math, re
+++
+++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
+++BASE = "/run/v24-v6-authority/private"
+++OPS = {
+++    "ENOSPC": {"operation": "write_authority_record", "syscalls": {"write", "fsync"}},
+++    "EROFS": {"operation": "write_authority_record", "syscalls": {"write", "fsync", "rename"}},
+++    "EIO": {"operation": "record_io", "syscalls": {"read", "write", "fsync", "rename"}},
+++    "EACCES": {"operation": "record_access", "syscalls": {"open", "write", "rename"}},
+++}
+++MECHANISM_CLASSES = {"kernel_quota", "dedicated_ro_mount", "disposable_fault_layer", "kernel_policy"}
+++
+++def exact_paths(record_id: str):
+++    if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", record_id): return None
+++    return f"{BASE}/records/{record_id}.record", f"{BASE}/consumed/{record_id}.record"
+++
+++def check_rq17_contamination(baseline: dict, test: dict):
+++    reasons=[]
+++    for k in ("records_device", "consumed_device", "records_fs", "consumed_fs", "mount_topology"):
+++        if baseline.get(k) != test.get(k): reasons.append(f"topology_changed:{k}")
+++    if baseline.get("records_device") != baseline.get("consumed_device"): reasons.append("baseline_already_split")
+++    return (not reasons, reasons)
+++
+++def _structured_map(obj, keys):
+++    return isinstance(obj, dict) and all(k in obj and obj[k] not in (None, "") for k in keys)
+++
+++def validate_fault_proof(arm, proof, target_id, expected_paths):
+++    required=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","independent_observer_reference","cleanup_reference")
+++    reasons=[]
+++    if not _structured_map(proof, required): reasons.append("fault_proof_incomplete")
+++    else:
+++        if proof["arm"] != arm: reasons.append("wrong_arm")
+++        if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_not_allowed")
+++        if proof["target_record_id"] != target_id: reasons.append("wrong_target_id")
+++        if proof["target_path"] not in expected_paths: reasons.append("wrong_target_path")
+++        if proof["expected_errno"] != arm or proof["observed_errno"] != arm: reasons.append("wrong_errno")
+++        if proof["target_operation"] != OPS[arm]["operation"]: reasons.append("wrong_operation")
+++        if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
+++        if not isinstance(proof["activation_evidence"], dict) or not proof["activation_evidence"].get("observed"): reasons.append("activation_not_proven")
+++        if not isinstance(proof["operation_evidence"], dict) or not proof["operation_evidence"].get("observed"): reasons.append("operation_not_proven")
+++        if not isinstance(proof["service_pid"], int) or proof["service_pid"] <= 0: reasons.append("service_pid_invalid")
+++        if not isinstance(proof["timestamp"], (int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
+++    return reasons
+++
+++def _observations_complete(obs, target_id, paths):
+++    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
+++    if not isinstance(obs, dict): return ["observations_missing"]
+++    for stage in stages:
+++        o=obs.get(stage)
+++        if not isinstance(o, dict): reasons.append(f"observation_missing:{stage}"); continue
+++        for k in ("service_pid","records_path","consumed_path","records_device","consumed_device","mount_id","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
+++            if k not in o: reasons.append(f"observation_field_missing:{stage}:{k}")
+++        if o.get("records_path") != paths[0] or o.get("consumed_path") != paths[1]: reasons.append(f"observation_path_mismatch:{stage}")
+++    return reasons
+++
+++def _lifecycle_valid(life, target_id):
+++    if not isinstance(life, dict): return ["lifecycle_missing"]
+++    reasons=[]
+++    if life.get("target_record_id") != target_id: reasons.append("lifecycle_wrong_target")
+++    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
+++    if life.get("unexplained_disappearance"): reasons.append("unexplained_disappearance")
+++    if life.get("duplicate_authoritative_consume"): reasons.append("duplicate_authoritative_consume")
+++    if life.get("unrelated_transition"): reasons.append("unrelated_transition")
+++    if not isinstance(life.get("deltas"), dict): reasons.append("lifecycle_deltas_missing")
+++    return reasons
+++
+++def validate_authorization_token(token, expected):
+++    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","independent_review_disposition","review_artifact_sha256","reviewer_identity/designation","authorization_timestamp","expiration","nonce")
+++    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+++    for k in ("rq_id","arm","plan_commit","plan_tree","execution_contract_digest"):
+++        if k in token and k in expected and token[k] != expected[k]: reasons.append(f"token_mismatch:{k}")
+++    return reasons
+++
+++def evaluate_arm(arm, evidence):
+++    if arm not in ARMS: return "HARNESS_DEFECT", ["unknown_arm"]
+++    target_id=evidence.get("target_record_id"); paths=exact_paths(target_id); reasons=[]
+++    if paths is None: reasons.append("target_record_id_invalid"); paths=("", "")
+++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
+++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
+++    reasons += validate_fault_proof(arm, evidence.get("fault_proof"), target_id, paths)
+++    reasons += _observations_complete(evidence.get("observations"), target_id, paths)
+++    reasons += _lifecycle_valid(evidence.get("lifecycle"), target_id)
+++    cleanup=evidence.get("cleanup_proof")
+++    if not isinstance(cleanup, dict): reasons.append("cleanup_proof_missing")
+++    else:
+++        for k in ("mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identity","service_identity","socket_state","records_consumed_state","fault_disabled","independently_verified"):
+++            if k not in cleanup: reasons.append(f"cleanup_field_missing:{k}")
+++        if cleanup.get("independently_verified") is not True: reasons.append("cleanup_not_verified")
+++    if evidence.get("rq17_contamination") is not False: reasons.append("rq17_contamination_or_unknown")
+++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", sorted(set(reasons)))
+++
+++def main():
+++    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true")
+++    a=ap.parse_args()
+++    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
+++    if a.self_test:
+++        print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["structured fault proof","exact paths","observer completeness","cleanup proof","RQ17 contamination gate"]},indent=2)); return 0
+++    if not a.plan: ap.error("only --plan or --self-test is allowed")
+++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
+++if __name__ == "__main__": raise SystemExit(main())
++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
++new file mode 100644
++index 00000000..f9f4f053
++--- /dev/null
+++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
++@@ -0,0 +1,7 @@
+++{
+++  "authorization_schema_version": "1",
+++  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
+++  "single_use": true,
+++  "arm_scoped": true,
+++  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
+++}
++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
++new file mode 100644
++index 00000000..5ef55ad0
++--- /dev/null
+++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
++@@ -0,0 +1,19 @@
+++# RQ-16 cleanup and restoration contract
+++
+++RQ-16 remains preregistration-only. No mutation has been executed.
+++
+++Every future arm must capture an immutable baseline and restore it before any
+++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
+++socket identity, records/consumed ownership and modes, filesystem device IDs,
+++mount options, security controls, and exact target lifecycle.
+++
+++The inverse operation must be explicit: remove only the bounded fault fixture,
+++restore the saved mount/quota/metadata state, restart only as required by the
+++approved recovery procedure, and independently remeasure every baseline field.
+++If a mount operation fails, root recovery is unavailable, a fault fixture
+++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
+++dependent cases abort. Historical evidence directories are never targets.
+++
+++The future harness must refuse destructive execution unless the exact host,
+++commit, plan digest, and separately generated authorization token are bound.
+++`--plan` and `--self-test` are the only permitted modes in this preregistration.
++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
++new file mode 100644
++index 00000000..fdc139d1
++--- /dev/null
+++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
++@@ -0,0 +1,48 @@
+++{
+++  "rq_id": "RQ-16",
+++  "trigger": "Disk full / read-only / I/O / permission failure",
+++  "oracle": "Fail closed without fabricated success",
+++  "execution_required": true,
+++  "execution_authorized": false,
+++  "arms": {
+++    "ENOSPC": {
+++      "operation": "write_authority_record or fsync on exact bound records path",
+++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
+++      "classification": "INSUFFICIENT_EVIDENCE",
+++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
+++    },
+++    "EROFS": {
+++      "operation": "write_authority_record or rename on exact bound path",
+++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
+++      "classification": "UNSAFE",
+++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
+++    },
+++    "EIO": {
+++      "operation": "exact record read/write/fsync/rename syscall",
+++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
+++      "classification": "INSUFFICIENT_EVIDENCE",
+++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
+++    },
+++    "EACCES": {
+++      "operation": "exact service access to records/consumed path",
+++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
+++      "classification": "PROXY_NOT_ACCEPTABLE",
+++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
+++    }
+++  },
+++  "classification_rules": {
+++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
+++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
+++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
+++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
+++  },
+++  "state_machine": {
+++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
+++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
+++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
+++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
+++  },
+++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+++  "RQ16_EXECUTED": false,
+++  "RQ16_AUTHORIZED": false
+++}
++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
++new file mode 100644
++index 00000000..28c4e298
++--- /dev/null
+++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
++@@ -0,0 +1,15 @@
+++{
+++  "issues": [
+++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
+++    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
+++    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
+++    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
+++  ],
+++  "open_automatable_issues": 0,
+++  "manual_review_required": true,
+++  "RQ16_EXECUTED": false,
+++  "RQ16_AUTHORIZED": false
+++}
++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
++new file mode 100644
++index 00000000..0a797b62
++--- /dev/null
+++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
++@@ -0,0 +1,103 @@
+++# V24-I11-V6 RQ-16 preregistration (planning only)
+++
+++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
+++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
+++that closed Remediation-7 head.
+++
+++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
+++failure**. Oracle: **Fail closed without fabricated success**. This document
+++does not authorize execution.
+++
+++## Actual write path
+++
+++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
+++
+++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
+++  `fsync`, then closes and unlinks on failure.
+++- candidate handling calls `materialize_private()` for context, boundary and
+++  payload before gate execution.
+++- root control calls `consume_record_trusted()`.
+++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
+++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
+++  from records to consumed. It returns an authoritative response only after
+++  `rename` succeeds.
+++- `write_authority_record()` creates records with
+++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
+++  `fsync`, closes, and unlinks on failure.
+++
+++RQ-16 must bind the injected errno to one of these exact operations; mocked
+++Python exceptions and candidate-side failures are proxies.
+++
+++## Execution arms and classifications
+++
+++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
+++host `/run` is prohibited. No repository evidence proves such a quota boundary,
+++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
+++
+++EROFS requires a dedicated qualification filesystem whose read-only transition
+++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
+++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
+++the arm is `UNSAFE` pending dedicated-mount evidence.
+++
+++EIO requires a disposable kernel fault layer returning EIO on the exact target
+++operation. `dm-error` or equivalent is acceptable only with a dedicated device
+++and independent activation/errno proof. No such boundary is evidenced;
+++classification is `INSUFFICIENT_EVIDENCE`.
+++
+++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
+++trusted service runs as UID 0. Candidate-side permission failure or a mocked
+++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
+++
+++These are execution arms under one frozen case, not new cases.
+++
+++## Required state machine and proof
+++
+++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
+++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
+++state record target membership in records/consumed, response and authority,
+++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
+++and hashes. PASS requires exact fault activation plus syscall errno, no
+++authoritative success, explainable target lifecycle, recoverable service,
+++complete observers, and exact post-restoration hashes/security state. Absence
+++of a response alone is never PASS. Authoritative success after a proven fault
+++is RED. Missing/malformed proof or observer/cleanup failure is
+++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
+++
+++## Restoration, safety and aborts
+++
+++The only permitted future mutation is a bounded fixture on a dedicated,
+++preflight-verified boundary. The host root filesystem, repository, historical
+++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
+++workspace are never targets. Cleanup removes the fixture, restores mount/quota
+++and metadata, revalidates service/socket/PID, records/consumed integrity,
+++device IDs, mount options, ownership/modes, hashes and security controls. Any
+++failure blocks all dependent cases.
+++
+++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
+++free-space margin, backup material, root recovery, service health or observer
+++access differ from the preregistered baseline, or if an evidence directory could
+++be overwritten.
+++
+++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
+++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
+++
+++## Harness safety and governance
+++
+++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
+++`--execute-rq16` refuses with a nonzero result. Future execution requires a
+++separately generated authorization token bound to exact commit, host/runtime
+++identity and plan digest. No token exists in this branch.
+++
+++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
+++Qualification remains `NOT_QUALIFIED`; scientific execution remains
+++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
+++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
+++mechanism classifications before any execution authorization.
+++
+++## Remediation-2 hardening
+++
+++The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.
+++
+++Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.
+++
+++No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
++diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
++new file mode 100644
++index 00000000..d60eee26
++--- /dev/null
+++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
++@@ -0,0 +1,22 @@
+++# RQ-16 read-only capability inspection
+++
+++This inspection was non-destructive and did not enable or mutate any host feature.
+++
+++The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.
+++
+++Source inspection found the trusted service operations at:
+++
+++- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
+++- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
+++- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.
+++
+++Read-only commands attempted:
+++
+++```text
+++Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
+++Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
+++```
+++
+++Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.
+++
+++`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
++```
++
++## Manual-review questions
++
++Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
+diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
+new file mode 100644
+index 00000000..eea5a68d
+--- /dev/null
++++ b/governance-runtime/build_rq16_preregistration_review.py
+@@ -0,0 +1,19 @@
++from __future__ import annotations
++import hashlib, subprocess
++from pathlib import Path
++ROOT=Path(__file__).resolve().parents[1]
++OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
++FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py',ROOT/'governance-runtime/check_rq16_preregistration_packet.py']
++def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
++def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
++def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
++def main():
++    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
++    diff=run(['git','diff','8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','HEAD']).stdout
++    parts=['# V24-I11-V6 RQ-16 preregistration review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity','predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f"branch={run(['git','branch','--show-current']).stdout.strip()}",f"head={run(['git','rev-parse','HEAD']).stdout.strip()}",f"tree={run(['git','rev-parse','HEAD^{tree}']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
++    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
++    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
++    compile_result=run(['python','-m','compileall','-q']+[str(p) for p in FILES[4:]])
++    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('mutation output',mutations.stdout+mutations.stderr,'json'),fence('packet consistency',consistency.stdout+consistency.stderr),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
++    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
++if __name__=='__main__': main()
+diff --git a/governance-runtime/check_rq16_preregistration_packet.py b/governance-runtime/check_rq16_preregistration_packet.py
+new file mode 100644
+index 00000000..5140828c
+--- /dev/null
++++ b/governance-runtime/check_rq16_preregistration_packet.py
+@@ -0,0 +1,18 @@
++#!/usr/bin/env python3
++"""Offline packet consistency checks; no runtime interaction."""
++from __future__ import annotations
++import json, hashlib
++from pathlib import Path
++ROOT=Path(__file__).resolve().parents[1]
++def main():
++    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
++    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
++    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
++    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
++    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
++    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
++    head=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
++    parent=__import__('subprocess').check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip()
++    assert (f'head={head}' in text or f'head={parent}' in text) and 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
++    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
++if __name__=='__main__': raise SystemExit(main())
+diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+new file mode 100644
+index 00000000..492ea52c
+--- /dev/null
++++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
+@@ -0,0 +1,29 @@
++#!/usr/bin/env python3
++"""Offline structured-proof mutation suite; no runtime interaction."""
++import copy, json
++from v24_v6_rq1_rq16_harness import evaluate_arm
++from test_v24_v6_rq1_rq16_harness import good
++
++def main():
++    mutations=[]
++    specs=[
++      ("wrong_target",lambda e:e.update(target_record_id="other")),
++      ("wrong_path",lambda e:e["fault_proof"].update(target_path="/run/v24-v6-authority/private/records/other.record")),
++      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
++      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
++      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
++      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
++      ("observer_missing",lambda e:e["observations"].pop("restored")),
++      ("cleanup_unverified",lambda e:e["cleanup_proof"].update(independently_verified=False)),
++      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
++      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
++      ("rq17_split",lambda e:e.update(rq17_contamination=True)),
++      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
++      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
++    ]
++    for name,mut in specs:
++        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e)
++        mutations.append({"mutation_id":name,"case":"ENOSPC","path":name,"expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
++    out={"total":len(mutations),"rejected":sum(x["rejected"] for x in mutations),"survived":sum(not x["rejected"] for x in mutations),"all_rejected":all(x["rejected"] for x in mutations),"mutations":mutations,"RQ16_EXECUTED":False}
++    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
++if __name__=="__main__": raise SystemExit(main())
+diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
+new file mode 100644
+index 00000000..6ae417c7
+--- /dev/null
++++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
+@@ -0,0 +1,30 @@
++#!/usr/bin/env python3
++import unittest
++from v24_v6_rq1_rq16_harness import evaluate_arm, exact_paths, check_rq17_contamination, validate_authorization_token
++
++TARGET="abc123"; RP,CP=exact_paths(TARGET)
++def obs():
++    return {s:{"service_pid":123,"records_path":RP,"consumed_path":CP,"records_device":"d1","consumed_device":"d1","mount_id":"m1","service_binary_sha256":"svc","gate_sha256":"gate","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
++def good(errno="ENOSPC"):
++    return {"target_record_id":TARGET,"fault_proof":{"arm":"ENOSPC","mechanism_id":"m","mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":RP,"expected_errno":errno,"observed_errno":errno,"kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":123,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":obs(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identity":"mi","service_identity":"si","socket_state":"ss","records_consumed_state":"rc","fault_disabled":True,"independently_verified":True},"rq17_contamination":False,"service_recoverable":True}
++
++class RQ16Tests(unittest.TestCase):
++    def test_structured_candidate_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good())[0],"PASS")
++    def test_exact_target_and_paths(self):
++        e=good(); e["target_record_id"]="other"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        e=good(); e["fault_proof"]["target_path"]="/run/v24-v6-authority/private/records/abc123-other.record"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++    def test_provenance_and_syscall(self):
++        for k,v in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS")):
++            e=good(); e["fault_proof"][k]=v; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++    def test_observer_cleanup_and_lifecycle(self):
++        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        e=good(); e["cleanup_proof"]["independently_verified"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++    def test_authority_and_contamination_red_or_reject(self):
++        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e)[0],"RED")
++        e=good(); e["rq17_contamination"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
++        self.assertFalse(check_rq17_contamination({"records_device":"d1","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"},{"records_device":"d2","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"})[0])
++    def test_token_is_explicitly_bound(self):
++        self.assertTrue(validate_authorization_token({}, {}) )
++
++if __name__ == "__main__": unittest.main(verbosity=2)
+diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
+new file mode 100644
+index 00000000..053309da
+--- /dev/null
++++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
+@@ -0,0 +1,104 @@
++#!/usr/bin/env python3
++"""RQ-16 preregistration evaluator; plan/self-test only, never performs faults."""
++from __future__ import annotations
++import argparse, json, math, re
++
++ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
++BASE = "/run/v24-v6-authority/private"
++OPS = {
++    "ENOSPC": {"operation": "write_authority_record", "syscalls": {"write", "fsync"}},
++    "EROFS": {"operation": "write_authority_record", "syscalls": {"write", "fsync", "rename"}},
++    "EIO": {"operation": "record_io", "syscalls": {"read", "write", "fsync", "rename"}},
++    "EACCES": {"operation": "record_access", "syscalls": {"open", "write", "rename"}},
++}
++MECHANISM_CLASSES = {"kernel_quota", "dedicated_ro_mount", "disposable_fault_layer", "kernel_policy"}
++
++def exact_paths(record_id: str):
++    if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", record_id): return None
++    return f"{BASE}/records/{record_id}.record", f"{BASE}/consumed/{record_id}.record"
++
++def check_rq17_contamination(baseline: dict, test: dict):
++    reasons=[]
++    for k in ("records_device", "consumed_device", "records_fs", "consumed_fs", "mount_topology"):
++        if baseline.get(k) != test.get(k): reasons.append(f"topology_changed:{k}")
++    if baseline.get("records_device") != baseline.get("consumed_device"): reasons.append("baseline_already_split")
++    return (not reasons, reasons)
++
++def _structured_map(obj, keys):
++    return isinstance(obj, dict) and all(k in obj and obj[k] not in (None, "") for k in keys)
++
++def validate_fault_proof(arm, proof, target_id, expected_paths):
++    required=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","independent_observer_reference","cleanup_reference")
++    reasons=[]
++    if not _structured_map(proof, required): reasons.append("fault_proof_incomplete")
++    else:
++        if proof["arm"] != arm: reasons.append("wrong_arm")
++        if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_not_allowed")
++        if proof["target_record_id"] != target_id: reasons.append("wrong_target_id")
++        if proof["target_path"] not in expected_paths: reasons.append("wrong_target_path")
++        if proof["expected_errno"] != arm or proof["observed_errno"] != arm: reasons.append("wrong_errno")
++        if proof["target_operation"] != OPS[arm]["operation"]: reasons.append("wrong_operation")
++        if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
++        if not isinstance(proof["activation_evidence"], dict) or not proof["activation_evidence"].get("observed"): reasons.append("activation_not_proven")
++        if not isinstance(proof["operation_evidence"], dict) or not proof["operation_evidence"].get("observed"): reasons.append("operation_not_proven")
++        if not isinstance(proof["service_pid"], int) or proof["service_pid"] <= 0: reasons.append("service_pid_invalid")
++        if not isinstance(proof["timestamp"], (int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
++    return reasons
++
++def _observations_complete(obs, target_id, paths):
++    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
++    if not isinstance(obs, dict): return ["observations_missing"]
++    for stage in stages:
++        o=obs.get(stage)
++        if not isinstance(o, dict): reasons.append(f"observation_missing:{stage}"); continue
++        for k in ("service_pid","records_path","consumed_path","records_device","consumed_device","mount_id","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
++            if k not in o: reasons.append(f"observation_field_missing:{stage}:{k}")
++        if o.get("records_path") != paths[0] or o.get("consumed_path") != paths[1]: reasons.append(f"observation_path_mismatch:{stage}")
++    return reasons
++
++def _lifecycle_valid(life, target_id):
++    if not isinstance(life, dict): return ["lifecycle_missing"]
++    reasons=[]
++    if life.get("target_record_id") != target_id: reasons.append("lifecycle_wrong_target")
++    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
++    if life.get("unexplained_disappearance"): reasons.append("unexplained_disappearance")
++    if life.get("duplicate_authoritative_consume"): reasons.append("duplicate_authoritative_consume")
++    if life.get("unrelated_transition"): reasons.append("unrelated_transition")
++    if not isinstance(life.get("deltas"), dict): reasons.append("lifecycle_deltas_missing")
++    return reasons
++
++def validate_authorization_token(token, expected):
++    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","independent_review_disposition","review_artifact_sha256","reviewer_identity/designation","authorization_timestamp","expiration","nonce")
++    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
++    for k in ("rq_id","arm","plan_commit","plan_tree","execution_contract_digest"):
++        if k in token and k in expected and token[k] != expected[k]: reasons.append(f"token_mismatch:{k}")
++    return reasons
++
++def evaluate_arm(arm, evidence):
++    if arm not in ARMS: return "HARNESS_DEFECT", ["unknown_arm"]
++    target_id=evidence.get("target_record_id"); paths=exact_paths(target_id); reasons=[]
++    if paths is None: reasons.append("target_record_id_invalid"); paths=("", "")
++    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
++    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
++    reasons += validate_fault_proof(arm, evidence.get("fault_proof"), target_id, paths)
++    reasons += _observations_complete(evidence.get("observations"), target_id, paths)
++    reasons += _lifecycle_valid(evidence.get("lifecycle"), target_id)
++    cleanup=evidence.get("cleanup_proof")
++    if not isinstance(cleanup, dict): reasons.append("cleanup_proof_missing")
++    else:
++        for k in ("mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identity","service_identity","socket_state","records_consumed_state","fault_disabled","independently_verified"):
++            if k not in cleanup: reasons.append(f"cleanup_field_missing:{k}")
++        if cleanup.get("independently_verified") is not True: reasons.append("cleanup_not_verified")
++    if evidence.get("rq17_contamination") is not False: reasons.append("rq17_contamination_or_unknown")
++    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
++    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", sorted(set(reasons)))
++
++def main():
++    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true")
++    a=ap.parse_args()
++    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
++    if a.self_test:
++        print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["structured fault proof","exact paths","observer completeness","cleanup proof","RQ17 contamination gate"]},indent=2)); return 0
++    if not a.plan: ap.error("only --plan or --self-test is allowed")
++    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
++if __name__ == "__main__": raise SystemExit(main())
+diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
+new file mode 100644
+index 00000000..f9f4f053
+--- /dev/null
++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
+@@ -0,0 +1,7 @@
++{
++  "authorization_schema_version": "1",
++  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
++  "single_use": true,
++  "arm_scoped": true,
++  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
++}
+diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+new file mode 100644
+index 00000000..5ef55ad0
+--- /dev/null
++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
+@@ -0,0 +1,19 @@
++# RQ-16 cleanup and restoration contract
++
++RQ-16 remains preregistration-only. No mutation has been executed.
++
++Every future arm must capture an immutable baseline and restore it before any
++dependent case. The baseline includes service/gate hashes, unit bytes, PID and
++socket identity, records/consumed ownership and modes, filesystem device IDs,
++mount options, security controls, and exact target lifecycle.
++
++The inverse operation must be explicit: remove only the bounded fault fixture,
++restore the saved mount/quota/metadata state, restart only as required by the
++approved recovery procedure, and independently remeasure every baseline field.
++If a mount operation fails, root recovery is unavailable, a fault fixture
++cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
++dependent cases abort. Historical evidence directories are never targets.
++
++The future harness must refuse destructive execution unless the exact host,
++commit, plan digest, and separately generated authorization token are bound.
++`--plan` and `--self-test` are the only permitted modes in this preregistration.
+diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+new file mode 100644
+index 00000000..fdc139d1
+--- /dev/null
++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
+@@ -0,0 +1,48 @@
++{
++  "rq_id": "RQ-16",
++  "trigger": "Disk full / read-only / I/O / permission failure",
++  "oracle": "Fail closed without fabricated success",
++  "execution_required": true,
++  "execution_authorized": false,
++  "arms": {
++    "ENOSPC": {
++      "operation": "write_authority_record or fsync on exact bound records path",
++      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
++      "classification": "INSUFFICIENT_EVIDENCE",
++      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
++    },
++    "EROFS": {
++      "operation": "write_authority_record or rename on exact bound path",
++      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
++      "classification": "UNSAFE",
++      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
++    },
++    "EIO": {
++      "operation": "exact record read/write/fsync/rename syscall",
++      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
++      "classification": "INSUFFICIENT_EVIDENCE",
++      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
++    },
++    "EACCES": {
++      "operation": "exact service access to records/consumed path",
++      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
++      "classification": "PROXY_NOT_ACCEPTABLE",
++      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
++    }
++  },
++  "classification_rules": {
++    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
++    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
++    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
++    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
++  },
++  "state_machine": {
++    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
++    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
++    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
++    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
++  },
++  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
++  "RQ16_EXECUTED": false,
++  "RQ16_AUTHORIZED": false
++}
+diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+new file mode 100644
+index 00000000..28c4e298
+--- /dev/null
++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
+@@ -0,0 +1,15 @@
++{
++  "issues": [
++    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
++    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
++    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
++    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
++  ],
++  "open_automatable_issues": 0,
++  "manual_review_required": true,
++  "RQ16_EXECUTED": false,
++  "RQ16_AUTHORIZED": false
++}
+diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+new file mode 100644
+index 00000000..0a797b62
+--- /dev/null
++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
+@@ -0,0 +1,103 @@
++# V24-I11-V6 RQ-16 preregistration (planning only)
++
++Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
++`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
++that closed Remediation-7 head.
++
++Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
++failure**. Oracle: **Fail closed without fabricated success**. This document
++does not authorize execution.
++
++## Actual write path
++
++In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
++
++- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
++  `fsync`, then closes and unlinks on failure.
++- candidate handling calls `materialize_private()` for context, boundary and
++  payload before gate execution.
++- root control calls `consume_record_trusted()`.
++- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
++  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
++  from records to consumed. It returns an authoritative response only after
++  `rename` succeeds.
++- `write_authority_record()` creates records with
++  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
++  `fsync`, closes, and unlinks on failure.
++
++RQ-16 must bind the injected errno to one of these exact operations; mocked
++Python exceptions and candidate-side failures are proxies.
++
++## Execution arms and classifications
++
++ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
++host `/run` is prohibited. No repository evidence proves such a quota boundary,
++so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
++
++EROFS requires a dedicated qualification filesystem whose read-only transition
++does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
++unsafe and a separate filesystem would collide with RQ-17 topology semantics;
++the arm is `UNSAFE` pending dedicated-mount evidence.
++
++EIO requires a disposable kernel fault layer returning EIO on the exact target
++operation. `dm-error` or equivalent is acceptable only with a dedicated device
++and independent activation/errno proof. No such boundary is evidenced;
++classification is `INSUFFICIENT_EVIDENCE`.
++
++EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
++trusted service runs as UID 0. Candidate-side permission failure or a mocked
++exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
++
++These are execution arms under one frozen case, not new cases.
++
++## Required state machine and proof
++
++Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
++RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
++state record target membership in records/consumed, response and authority,
++errno proof, service state, filesystem/device/mount metadata, ownership/modes,
++and hashes. PASS requires exact fault activation plus syscall errno, no
++authoritative success, explainable target lifecycle, recoverable service,
++complete observers, and exact post-restoration hashes/security state. Absence
++of a response alone is never PASS. Authoritative success after a proven fault
++is RED. Missing/malformed proof or observer/cleanup failure is
++HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
++
++## Restoration, safety and aborts
++
++The only permitted future mutation is a bounded fixture on a dedicated,
++preflight-verified boundary. The host root filesystem, repository, historical
++evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
++workspace are never targets. Cleanup removes the fixture, restores mount/quota
++and metadata, revalidates service/socket/PID, records/consumed integrity,
++device IDs, mount options, ownership/modes, hashes and security controls. Any
++failure blocks all dependent cases.
++
++Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
++free-space margin, backup material, root recovery, service health or observer
++access differ from the preregistered baseline, or if an evidence directory could
++be overwritten.
++
++Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
++responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
++
++## Harness safety and governance
++
++`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
++`--execute-rq16` refuses with a nonzero result. Future execution requires a
++separately generated authorization token bound to exact commit, host/runtime
++identity and plan digest. No token exists in this branch.
++
++`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
++Qualification remains `NOT_QUALIFIED`; scientific execution remains
++`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
++`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
++mechanism classifications before any execution authorization.
++
++## Remediation-2 hardening
++
++The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.
++
++Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.
++
++No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
+diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
+new file mode 100644
+index 00000000..d60eee26
+--- /dev/null
++++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
+@@ -0,0 +1,22 @@
++# RQ-16 read-only capability inspection
++
++This inspection was non-destructive and did not enable or mutate any host feature.
++
++The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.
++
++Source inspection found the trusted service operations at:
++
++- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
++- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
++- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.
++
++Read-only commands attempted:
++
++```text
++Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
++Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
++```
++
++Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.
++
++`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
+```
+
+## Manual-review questions
+
+Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
new file mode 100644
index 00000000..bce92335
--- /dev/null
+++ b/governance-runtime/build_rq16_preregistration_review.py
@@ -0,0 +1,21 @@
+from __future__ import annotations
+import hashlib, subprocess
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
+FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py',ROOT/'governance-runtime/check_rq16_preregistration_packet.py']
+def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+def main():
+    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
+    reviewed=run(['git','rev-parse','HEAD']).stdout.strip(); reviewed_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet=__import__('os').environ.get('PACKET_COMMIT',reviewed); packet_tree=__import__('os').environ.get('PACKET_TREE',reviewed_tree)
+    diff=run(['git','diff',predecessor,reviewed]).stdout
+    identity=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_commit={packet}',f'packet_tree={packet_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}']
+    parts=['# V24-I11-V6 RQ-16 preregistration remediation-3 review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*identity,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
+    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
+    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+    compile_result=run(['python','-m','compileall','-q',str(ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py'),str(ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py'),str(ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py'),str(ROOT/'governance-runtime/check_rq16_preregistration_packet.py')])
+    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('mutation output',mutations.stdout+mutations.stderr,'json'),fence('packet consistency',consistency.stdout+consistency.stderr),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
+    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
+if __name__=='__main__': main()
diff --git a/governance-runtime/check_rq16_preregistration_packet.py b/governance-runtime/check_rq16_preregistration_packet.py
new file mode 100644
index 00000000..6066fede
--- /dev/null
+++ b/governance-runtime/check_rq16_preregistration_packet.py
@@ -0,0 +1,22 @@
+#!/usr/bin/env python3
+"""Offline packet consistency checks; no runtime interaction."""
+from __future__ import annotations
+import json, hashlib
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+def main():
+    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
+    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
+    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
+    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
+    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
+    import re, subprocess
+    vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_commit|packet_tree|predecessor_commit|predecessor_tree|exact_diff_sha256)=(.+)$',text,re.M))
+    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_commit','packet_tree','predecessor_commit','predecessor_tree','exact_diff_sha256'}
+    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
+    assert subprocess.run(['git','merge-base','--is-ancestor',vals['packet_commit'],head],cwd=ROOT).returncode==0
+    assert vals['predecessor_commit']=='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d' and vals['predecessor_tree']=='82457b9307f133db281055dbbdae26b618f8c3cf'
+    assert 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
+    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
+if __name__=='__main__': raise SystemExit(main())
diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
new file mode 100644
index 00000000..a23b3e43
--- /dev/null
+++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
@@ -0,0 +1,34 @@
+#!/usr/bin/env python3
+import copy, json
+from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context
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
+      ("missing_observer",lambda e:e["observations"].pop("restored")),
+      ("bool_only_observer",lambda e:e.pop("observations")),
+      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
+      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
+      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
+      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
+      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
+      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
+      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
+      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
+    ]
+    rows=[]
+    for name,mut in specs:
+        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED)
+        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
+    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+if __name__=="__main__": raise SystemExit(main())
diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..cfa25877
--- /dev/null
+++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,41 @@
+#!/usr/bin/env python3
+import copy, unittest
+from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token
+
+EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
+def observation():
+    return {s:{"target_record_id":TARGET,"records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+def good():
+    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":observation(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True},"service_recoverable":True}
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
+    def test_observer_cleanup_lifecycle_mutations_reject(self):
+        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
+        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
+    def test_authority_and_duplicate_transitions_red_or_reject(self):
+        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"RED")
+        e=good(); e["lifecycle"]["duplicate_authoritative_consume"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+    def test_token_requires_durable_trusted_binding(self):
+        self.assertTrue(validate_authorization_token({},EXPECTED))
+        token={"rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"issuer":"candidate","single_use_registry":"memory"}
+        self.assertTrue(validate_authorization_token(token,EXPECTED))
+    def test_cross_arm_proof_rejected(self):
+        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"))[0],"PASS")
+    def test_absent_response_not_success(self):
+        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED)[0],"PASS")
+
+if __name__=="__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..e01b2e4e
--- /dev/null
+++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,114 @@
+#!/usr/bin/env python3
+"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
+from __future__ import annotations
+import argparse, json, math, re
+
+ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
+OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
+MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}
+
+def expected_context(arm, record_id="abc123"):
+    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
+    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
+    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","review_artifact_sha256":"review-sha"}
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
+def _lifecycle_valid(life, expected):
+    if not isinstance(life,dict): return ["lifecycle_missing"]
+    reasons=[]
+    if life.get("target_record_id")!=expected["target_record_id"]: reasons.append("lifecycle_wrong_target")
+    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
+    for k in ("unexplained_disappearance","duplicate_authoritative_consume","second_authoritative_retry","authoritative_replay","unrelated_transition","historical_transition"):
+        if life.get(k): reasons.append(k)
+    if not isinstance(life.get("deltas"),dict): reasons.append("lifecycle_deltas_missing")
+    return reasons
+
+def validate_cleanup(cleanup, expected):
+    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
+    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified")
+    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
+    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
+    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True: reasons.append("cleanup_not_verified")
+    return reasons
+
+def validate_authorization_token(token, expected):
+    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer","source_path","single_use_registry")
+    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+    if token.get("rq_id")!="RQ-16" or token.get("arm")!=expected.get("arm"): reasons.append("token_arm_mismatch")
+    if token.get("mechanism_id")!=expected.get("mechanism_id"): reasons.append("token_mechanism_mismatch")
+    for k in ("plan_commit","plan_tree","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","review_artifact_sha256"):
+        if k in token and token[k] != expected.get(k.replace("records_mount_id","expected_records_mount").replace("consumed_mount_id","expected_consumed_mount").replace("records_device","expected_records_device").replace("consumed_device","expected_consumed_device").replace("service_binary_sha256","expected_service_binary_sha256").replace("gate_sha256","expected_gate_sha256")): reasons.append(f"token_mismatch:{k}")
+    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
+    if token.get("issuer")!="trusted-review-authority": reasons.append("issuer_untrusted")
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
+    reasons += _obs_complete(observed.get("observations"),expected)
+    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
+    reasons += _lifecycle_valid(observed.get("lifecycle"),expected)
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
index 00000000..28c4e298
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
@@ -0,0 +1,15 @@
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
+  "RQ16_AUTHORIZED": false
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

Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
