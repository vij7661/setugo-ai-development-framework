# V24-I11-V6 RQ-16 preregistration remediation-6 review

Planning-only artifact. No RQ-16 execution occurred.

## Identity
reviewed_source_commit=5f2bd1b88ca2f0c593da6e0fab5c5b8866058b13
reviewed_source_tree=b770f25aa0d8e0b41594e23684be0c8aab203dcc
packet_parent_commit=5f2bd1b88ca2f0c593da6e0fab5c5b8866058b13
packet_parent_tree=b770f25aa0d8e0b41594e23684be0c8aab203dcc
predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
exact_source_diff_sha256=b5fc030bb938e0d137b4d5b3005550e42c35207cff28afc79848bf2ceabecb97
source_manifest_sha256=f04ee8ce6d020579079d64c97266d973391304ec329c7c97bf6a95877e2625dd
generated_evidence_manifest_sha256=23767343e0b20f09823fb648bd2853b4507842e9ddf67fe75b1a04129bb77aa0
packet_content_identity_schema_version=2
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
    "RQ16-TEST-SUFFICIENCY": "RESOLVED",
    "RQ16-LIFECYCLE-DERIVATION": "RESOLVED",
    "RQ16-CLEANUP-BASELINE-COMPARISON": "RESOLVED",
    "RQ16-AUTHORIZATION-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-SOURCE-MANIFEST-RECOMPUTATION": "RESOLVED"
  }
}
```

## Source manifest
[{"path":"governance-runtime/build_rq16_preregistration_review.py","sha256":"ce6f7d679c824b2b495decd989be9d174582c94a3b90e6ecbadc52b97dca233a"},{"path":"governance-runtime/check_rq16_preregistration_packet.py","sha256":"cf1a6cc443631994bd40897ddc26aa5a9d640305eb5fc2b5b64fa327aee5a6be"},{"path":"governance-runtime/collect_rq16_results.py","sha256":"adab691dadc650852ea07bfa09ef5aa568b7dba628e9d6d1a6b870ef196a7ff0"},{"path":"governance-runtime/rq16_manifest.py","sha256":"895e468776d0d4a6894bbffa4c4d8de0887956ebf5def1d7efded6a80458f1b7"},{"path":"governance-runtime/run_v24_v6_rq1_rq16_mutations.py","sha256":"4cc446fa6ff059cf99bad895f5947f9091e04d4709e2a87335d7b15e5c9a4916"},{"path":"governance-runtime/test_rq16_manifest.py","sha256":"122338e681ef5df65953567d2593bea96481f470f2a3775de9e8bfc2f66d5881"},{"path":"governance-runtime/test_v24_v6_rq1_rq16_harness.py","sha256":"fa54ab8c395e1fc958b996a7e5e30957bbeac6617733d34aa0272a798f5154f5"},{"path":"governance-runtime/v24_v6_rq1_rq16_harness.py","sha256":"babe9b5030f415ce87b77c288f53776d3f14dcdbbdfeca4f3c4be532b9bff476"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json","sha256":"31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md","sha256":"958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json","sha256":"efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md","sha256":"13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json","sha256":"527ac480abf1e6b74fab31374886fde58f6dffd77c7274b92e4e481711a8fdfd"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md","sha256":"19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md","sha256":"ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b"}]

## Generated evidence manifest
[{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json","sha256":"13352f4d9f42e8ae94d9157414f3cbde667add5b7d85e65990929cb036e5b40a"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json","sha256":"c54b27af07686999f812264ff3540c4af8f780279c2cc395c2c4d718130e8c34"}]


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


### implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md sha256=958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769

```python
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


### implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json sha256=efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422

```python
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


### implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md sha256=13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00

```python
# Durable authorization nonce design

No live nonce is created in preregistration. Future authorization must use a root-owned, trusted append-only nonce ledger outside the candidate workspace. Consumption is an atomic create-with-exclusive semantics operation containing the nonce, authorization hash, arm, and timestamp. A second consume attempt fails closed as replay. The ledger must survive process restart, be non-candidate-writable, and be independently observed before and after use.

The JSON token is not authoritative by itself. The trusted issuer/reviewer artifact hash, exact plan/contract/runtime bindings, and root-owned source path must all validate before the nonce ledger is touched. No trusted issuer mechanism is available on this planning host, so future authorization remains `MANUAL_REVIEW_REQUIRED`.
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json sha256=527ac480abf1e6b74fab31374886fde58f6dffd77c7274b92e4e481711a8fdfd

```python
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
    "RQ16-TEST-SUFFICIENCY": "RESOLVED",
    "RQ16-LIFECYCLE-DERIVATION": "RESOLVED",
    "RQ16-CLEANUP-BASELINE-COMPARISON": "RESOLVED",
    "RQ16-AUTHORIZATION-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-SOURCE-MANIFEST-RECOMPUTATION": "RESOLVED"
  }
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md sha256=19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6

```python
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


### governance-runtime/build_rq16_preregistration_review.py sha256=ce6f7d679c824b2b495decd989be9d174582c94a3b90e6ecbadc52b97dca233a

```python
from __future__ import annotations
import hashlib, os, subprocess
from pathlib import Path
from rq16_manifest import canonical_review_source_files, canonical_evidence_files, build_source_manifest, build_evidence_manifest, manifest_sha256
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'
FILES=canonical_review_source_files(ROOT)
EVIDENCE_FILES=canonical_evidence_files(ROOT)
def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
def main():
    current=run(['git','rev-parse','HEAD']).stdout.strip(); current_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); reviewed=os.environ.get('REVIEWED_SOURCE_COMMIT',current); reviewed_tree=os.environ.get('REVIEWED_SOURCE_TREE',run(['git','rev-parse',f'{reviewed}^{{tree}}']).stdout.strip()); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet_parent=current; packet_parent_tree=current_tree
    diff=run(['git','diff',predecessor,reviewed,'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md']).stdout
    tests=run(['python','governance-runtime/collect_rq16_results.py']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
    source_manifest=build_source_manifest(FILES,ROOT); evidence_manifest=build_evidence_manifest(ROOT); ids=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_parent_commit={packet_parent}',f'packet_parent_tree={packet_parent_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_source_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}',f'source_manifest_sha256={manifest_sha256(source_manifest)}',f'generated_evidence_manifest_sha256={manifest_sha256(evidence_manifest)}','packet_content_identity_schema_version=2']
    parts=['# V24-I11-V6 RQ-16 preregistration remediation-6 review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*ids,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION','packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION','packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION','RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[2].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[5].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[1].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[4].read_text(),'json'), '## Source manifest',source_manifest,'## Generated evidence manifest',evidence_manifest]
    for p in FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
    for p in EVIDENCE_FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'json'))
    parts += ['## Static and behavioral results',fence('plan',plan.stdout+plan.stderr),fence('self-test',selftest.stdout+selftest.stderr),fence('tests',tests.stdout+tests.stderr),fence('mutations',mutations.stdout+mutations.stderr,'json'),fence('packet-check',consistency.stdout+consistency.stderr),fence('execution-refusal',refuse.stdout+refuse.stderr), '## Exact predecessor-to-reviewed-source diff', fence('diff',diff), '## Manual-review questions','Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.']
    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
if __name__=='__main__': main()
```


### governance-runtime/check_rq16_preregistration_packet.py sha256=cf1a6cc443631994bd40897ddc26aa5a9d640305eb5fc2b5b64fa327aee5a6be

```python
#!/usr/bin/env python3
"""Verify preregistration identities knowable before packet commit."""
import hashlib, json, re, subprocess
from pathlib import Path
from rq16_manifest import canonical_review_source_files, build_source_manifest, canonical_evidence_files, build_evidence_manifest, manifest_sha256
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'
SOURCE_FILES=canonical_review_source_files(ROOT)
def main():
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
    assert vals['packet_content_identity_schema_version']=='2'
    manifest_match=re.search(r'## Source manifest\n(.*?)(?:\n### |\n## )',text,re.S)
    assert manifest_match, 'source_manifest_section_missing'
    declared=json.loads(manifest_match.group(1).strip())
    expected_manifest=json.loads(build_source_manifest(SOURCE_FILES,ROOT))
    assert declared==expected_manifest, 'source_manifest_entries_mismatch'
    manifest=build_source_manifest(SOURCE_FILES,ROOT)
    assert manifest_sha256(manifest)==vals['source_manifest_sha256'], 'source_manifest_hash_mismatch'
    evidence_match=re.search(r'## Generated evidence manifest\n(.*?)(?:\n### |\n## )',text,re.S); assert evidence_match, 'evidence_manifest_section_missing'
    assert json.loads(evidence_match.group(1).strip())==json.loads(build_evidence_manifest(ROOT)), 'evidence_manifest_entries_mismatch'
    tests=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json').read_text()); muts=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json').read_text())
    assert tests['tests_total']==tests['tests_passed']+tests['tests_failed'] and tests['exit_code']==0, 'test_result_binding_mismatch'
    assert muts['total_mutations']==len(muts['mutations']) and muts['rejected_mutations']+muts['surviving_mutations']==muts['total_mutations'] and muts['all_rejected']==(muts['surviving_mutations']==0), 'mutation_result_binding_mismatch'
    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-[56]-REVIEW)\.md',text,re.M)
    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
```


### governance-runtime/collect_rq16_results.py sha256=adab691dadc650852ea07bfa09ef5aa568b7dba628e9d6d1a6b870ef196a7ff0

```python
#!/usr/bin/env python3
"""Generate the single authoritative offline RQ-16 test and mutation results."""
import json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEST_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json'
MUT_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json'
def main():
    runs=[subprocess.run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py'],cwd=ROOT,text=True,capture_output=True),subprocess.run(['python','governance-runtime/test_rq16_manifest.py'],cwd=ROOT,text=True,capture_output=True)]
    t=subprocess.CompletedProcess([],max((x.returncode for x in runs),default=0),stdout='\n'.join(x.stdout for x in runs),stderr='\n'.join(x.stderr for x in runs))
    m=subprocess.run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'],cwd=ROOT,text=True,capture_output=True)
    combined=re.sub(r'Ran (\d+) tests? in [0-9.]+s',r'Ran \1 tests in <elapsed>',t.stderr+t.stdout)
    matches=re.findall(r'Ran (\d+) tests?',combined); total=sum(int(x) for x in matches)
    tests=[]
    for line in combined.splitlines():
        hit=re.match(r'test_\w+ \(__main__\.[^)]+\) \.\.\. (ok|FAIL)',line)
        if hit: tests.append({'name':line.split(' (',1)[0],'result':'PASS' if hit.group(1)=='ok' else 'FAIL'})
    test_result={'tests_total':total,'tests_passed':sum(x['result']=='PASS' for x in tests),'tests_failed':sum(x['result']=='FAIL' for x in tests),'exit_code':t.returncode,'tests':tests,'stdout':'','stderr':combined}
    mutation_result=json.loads(m.stdout)
    mutation_result['exit_code']=m.returncode
    TEST_OUT.write_text(json.dumps(test_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    MUT_OUT.write_text(json.dumps(mutation_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'tests_total':test_result['tests_total'],'tests_passed':test_result['tests_passed'],'tests_failed':test_result['tests_failed'],'mutation_total':mutation_result['total_mutations'],'mutation_rejected':mutation_result['rejected_mutations'],'mutation_surviving':mutation_result['surviving_mutations'],'all_rejected':mutation_result['all_rejected']},indent=2))
    return 0 if t.returncode==0 and m.returncode==0 else 1
if __name__=='__main__': raise SystemExit(main())
```


### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=4cc446fa6ff059cf99bad895f5947f9091e04d4709e2a87335d7b15e5c9a4916

```python
#!/usr/bin/env python3
import copy, hashlib, json
from datetime import datetime, timezone
from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, expected_fault_observer_context, validate_authorization_token
from test_v24_v6_rq1_rq16_harness import good, TRUSTED
EXPECTED=expected_context("ENOSPC")
OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
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
      ("baseline_target_missing",lambda e:e["observations"]["baseline"].update(records_entries=[])),
      ("baseline_already_consumed",lambda e:e["observations"]["baseline"].update(consumed_entries=["abc123.record"])),
      ("post_failure_missing_both",lambda e:e["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
      ("post_failure_both",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
      ("wrong_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["other.record"])),
      ("historical_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
      ("unrelated_target_transition",lambda e:e["observations"]["post_failure"].update(records_entries=["abc123.record","other.record"])),
      ("duplicate_authoritative_consumption",lambda e:e.update(authoritative_success=True)),
      ("second_authoritative_retry",lambda e:e["observations"]["post_failure"].update(response={"service_authoritative":True})),
      ("replay_state_mutation",lambda e:e["observations"]["restored"].update(records_entries=["other.record"])),
      ("target_hash_changed",lambda e:e["observations"]["post_failure"].update(target_hash="changed")),
      ("target_identity_changed",lambda e:e["observations"]["post_failure"].update(target_record_id="other")),
      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
      ("cleanup_device",lambda e:e["cleanup_proof"]["restored_observation"].update(records_device="bad")),
      ("cleanup_mount",lambda e:e["cleanup_proof"]["restored_observation"].update(records_mount="bad")),
      ("cleanup_fs",lambda e:e["cleanup_proof"]["restored_observation"].update(records_fs="bad")),
      ("cleanup_realpath",lambda e:e["cleanup_proof"]["restored_observation"].update(records_realpath="bad")),
      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
      ("cleanup_fault_still_active",lambda e:e["cleanup_proof"]["restored_observation"].update(fault_state={"active":True})),
      ("cleanup_unrelated_record",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=["abc123.record","other.record"])),
      ("cleanup_historical_changed",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence={"intact":False})),
      ("cleanup_arbitrary_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="arbitrary")),
      ("cleanup_arbitrary_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="arbitrary")),
      ("cleanup_arbitrary_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="arbitrary")),
    ]
    rows=[]
    for name,mut in specs:
        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)
        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
    token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
    metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
    for field in auth_fields:
        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used,trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    for name,field,value in (("self_issued","issuer_identity","candidate"),("candidate_writable","source_path","candidate"),("placeholder_issuer_hash","issuer_authority_artifact_sha256","issuer-sha"),("placeholder_review_hash","review_artifact_sha256","review-sha"),("wrong_reviewer","reviewer_designation","candidate"),("generic_bounded_pass","independent_review_disposition","BOUNDED_PASS"),("changes_required","independent_review_disposition","CHANGES_REQUIRED"),("insufficient_evidence","independent_review_disposition","INSUFFICIENT_EVIDENCE")):
        bad=dict(token); bad[field]=value; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_provenance_"+name,"case":"AUTHORIZATION_PROVENANCE","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    reasons=validate_authorization_token(token,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_provenance_unavailable","case":"AUTHORIZATION_PROVENANCE","path":"trusted_provenance","before":"absent","after":"absent","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
if __name__=="__main__": raise SystemExit(main())
```


### governance-runtime/rq16_manifest.py sha256=895e468776d0d4a6894bbffa4c4d8de0887956ebf5def1d7efded6a80458f1b7

```python
#!/usr/bin/env python3
"""Canonical source/evidence manifest definitions for the RQ-16 review packet."""
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_RELATIVE=(
    "implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md",
    "governance-runtime/build_rq16_preregistration_review.py",
    "governance-runtime/check_rq16_preregistration_packet.py",
    "governance-runtime/collect_rq16_results.py",
    "governance-runtime/run_v24_v6_rq1_rq16_mutations.py",
    "governance-runtime/rq16_manifest.py",
    "governance-runtime/test_v24_v6_rq1_rq16_harness.py",
    "governance-runtime/test_rq16_manifest.py",
    "governance-runtime/v24_v6_rq1_rq16_harness.py",
)
EVIDENCE_RELATIVE=(
    "implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json",
)

def canonical_review_source_files(root=ROOT):
    return [root / rel for rel in SOURCE_RELATIVE]

def canonical_evidence_files(root=ROOT):
    return [root / rel for rel in EVIDENCE_RELATIVE]

def _entries(files, root=ROOT):
    entries=[]
    for path in files:
        rel=path.resolve().relative_to(root.resolve()).as_posix()
        if rel.startswith("/") or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ValueError(f"non-canonical path: {rel}")
        entries.append({"path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    if len({e["path"] for e in entries}) != len(entries):
        raise ValueError("duplicate canonical path")
    return sorted(entries,key=lambda e:e["path"])

def build_source_manifest(files=None, root=ROOT):
    return json.dumps(_entries(files or canonical_review_source_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"

def build_evidence_manifest(root=ROOT):
    return json.dumps(_entries(canonical_evidence_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"

def manifest_sha256(manifest):
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()
```


### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=fa54ab8c395e1fc958b996a7e5e30957bbeac6617733d34aa0272a798f5154f5

```python
#!/usr/bin/env python3
import copy, hashlib, unittest
from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context, expected_fault_observer_context

EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
TRUSTED={"issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":hashlib.sha256(b"issuer").hexdigest(),"reviewer_designation":"independent-reviewer","review_artifact_sha256":hashlib.sha256(b"review").hexdigest(),"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600"}
def observation():
    return {s:{"target_record_id":TARGET,"target_hash":"target-hash","records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
def good():
    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":OBSERVER["observer_identity"],"observer_source_sha256":OBSERVER["observer_source_sha256"],"observer_execution_identity":OBSERVER["observer_execution_identity"],"expected_evidence_root":OBSERVER["expected_evidence_root"],"expected_owner":OBSERVER["expected_owner"],"expected_mode":OBSERVER["expected_mode"],"expected_host_identity":OBSERVER["expected_host_identity"],"expected_runtime_identity":OBSERVER["expected_runtime_identity"],"raw_artifact_path":"/var/lib/v24-rq1/rq16-attestations/a.raw","raw_artifact_sha256":ARTIFACT_DIGEST,"cleanup_reference":"clean"}
    base=copy.deepcopy(EXPECTED["expected_restoration"])
    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}

class RQ16Tests(unittest.TestCase):
    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
    def test_target_mutations_reject(self):
        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_provenance_mutations_reject(self):
        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_observer_cleanup_lifecycle_mutations_reject(self):
        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        mutations=[
            ("baseline_target_missing",lambda x:x["observations"]["baseline"].update(records_entries=[])),
            ("baseline_target_already_consumed",lambda x:x["observations"]["baseline"].update(consumed_entries=[TARGET+".record"])),
            ("post_failure_target_missing_both",lambda x:x["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
            ("post_failure_target_both",lambda x:x["observations"]["post_failure"].update(consumed_entries=[TARGET+".record"])),
            ("wrong_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["other.record"])),
            ("historical_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
            ("unrelated_target_transition",lambda x:x["observations"]["post_failure"].update(records_entries=[TARGET+".record","other.record"])),
            ("duplicate_authoritative_consumption",lambda x:x.update(authoritative_success=True)),
            ("second_authoritative_retry",lambda x:x["observations"]["post_failure"].update(response={"service_authoritative":True})),
            ("replay_state_mutation",lambda x:x["observations"]["restored"].update(records_entries=["other.record"])),
            ("target_hash_changed",lambda x:x["observations"]["post_failure"].update(target_hash="changed")),
            ("target_identity_changed",lambda x:x["observations"]["post_failure"].update(target_record_id="other")),
        ]
        for _,mut in mutations:
            e=good(); mut(e); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
    def test_cleanup_exact_baseline_comparison(self):
        fields=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
        for field in fields:
            e=good(); e["cleanup_proof"]["restored_observation"][field]="arbitrary"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["cleanup_proof"].update(cleanup_ok=True); e["cleanup_proof"].pop("baseline_observation"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_authority_and_duplicate_transitions_red_or_reject(self):
        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"RED")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_token_requires_durable_trusted_binding(self):
        self.assertTrue(validate_authorization_token({},EXPECTED))
        token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
        metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"},trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
    def test_cross_arm_proof_rejected(self):
        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"),OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_absent_response_not_success(self):
        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")

if __name__=="__main__": unittest.main(verbosity=2)
```


### governance-runtime/test_rq16_manifest.py sha256=122338e681ef5df65953567d2593bea96481f470f2a3775de9e8bfc2f66d5881

```python
#!/usr/bin/env python3
import shutil, unittest
from contextlib import contextmanager
from pathlib import Path
from rq16_manifest import ROOT, canonical_review_source_files, build_source_manifest, manifest_sha256

class ManifestTests(unittest.TestCase):
    @contextmanager
    def scratch(self):
        d=ROOT/".rq16-manifest-test"; shutil.rmtree(d,ignore_errors=True); d.mkdir()
        try: yield d
        finally: shutil.rmtree(d,ignore_errors=True)
    def test_clean_manifest_is_deterministic(self):
        files=canonical_review_source_files(ROOT)
        self.assertEqual(build_source_manifest(files),build_source_manifest(list(reversed(files))))
        self.assertEqual(len({x.relative_to(ROOT).as_posix() for x in files}),len(files))
    def test_source_byte_change_changes_manifest(self):
        with self.scratch() as d:
            p=d/"x.py"; p.write_bytes(b"x=1\n"); before=build_source_manifest([p],d); p.write_bytes(b"x=2\n"); self.assertNotEqual(before,build_source_manifest([p],d))
    def test_duplicate_path_rejected(self):
        with self.scratch() as d:
            p=d/"x"; p.write_bytes(b"x");
            with self.assertRaises(ValueError): build_source_manifest([p,p],d)
    def test_missing_file_fails(self):
        with self.assertRaises(FileNotFoundError): build_source_manifest([ROOT/"does-not-exist"],ROOT)
    def test_absolute_outside_root_rejected(self):
        with self.scratch() as d:
            p=d/"x"; p.write_bytes(b"x");
            with self.assertRaises(ValueError): build_source_manifest([Path("C:/outside-rq16/x")],ROOT)
    def test_generated_packet_is_not_source(self):
        names={p.name for p in canonical_review_source_files(ROOT)}
        self.assertNotIn("V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md",names)
    def test_manifest_hash_is_content_hash(self):
        self.assertEqual(len(manifest_sha256(build_source_manifest())),64)

if __name__=="__main__": unittest.main(verbosity=2)
```


### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=babe9b5030f415ce87b77c288f53776d3f14dcdbbdfeca4f3c4be532b9bff476

```python
#!/usr/bin/env python3
"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
from __future__ import annotations
import argparse, hashlib, json, math, re
from datetime import datetime, timezone

ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}
TRUSTED_AUTHORIZATION_PROVENANCE_AVAILABLE=False

def expected_trusted_authorization_provenance():
    """No governance-authorized issuer is available during preregistration."""
    return None

def expected_context(arm, record_id="abc123"):
    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
    baseline={"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_realpath":rp,"consumed_realpath":cp,"owner":{"uid":0,"gid":0},"mode":{"records":"0700","consumed":"0700"},"socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"service_identity":"uid0:trusted-service","security_controls":{"policy":"stable"},"fault_state":{"active":False},"records_entries":[record_id+".record"],"consumed_entries":[],"historical_evidence":{"intact":True}}
    stages={s:{"target_in_records":True,"target_in_consumed":False,"target_hash":"target-hash"} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
    lifecycle={"status":"MANUAL_REVIEW_REQUIRED","stages":stages,"permitted_transitions":[]}
    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_target_hash":"target-hash","expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","expected_restoration":baseline,"expected_lifecycle_contract":lifecycle}

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

def expected_fault_observer_context():
    return {"observer_identity":"trusted-root-observer","observer_source_sha256":hashlib.sha256(b"preregistered-trusted-root-observer-v1").hexdigest(),"observer_execution_identity":"root-observer-v1","expected_evidence_root":"/var/lib/v24-rq1/rq16-attestations","expected_owner":"root","expected_mode":"0600","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound"}

def validate_trusted_fault_attestation(att, expected, observer_context, actual_raw_artifact_digest):
    """Validate independently collected attestation; harness claims are not enough."""
    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity","raw_artifact_path","raw_artifact_sha256","cleanup_reference")
    if not isinstance(att,dict): return ["trusted_attestation_missing"]
    if not isinstance(observer_context,dict): return ["expected_observer_context_missing"]
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
    for k in ("observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity"):
        if att.get(k) != observer_context.get(k): reasons.append(f"observer_context_mismatch:{k}")
    if not isinstance(actual_raw_artifact_digest,str) or att["raw_artifact_sha256"] != actual_raw_artifact_digest: reasons.append("raw_artifact_digest_mismatch")
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

def _entry_name(entry):
    return entry if isinstance(entry,str) else entry.get("name") if isinstance(entry,dict) else None

def _entry_hash(entry):
    return entry.get("hash") if isinstance(entry,dict) else None

def derive_target_state(observation, expected):
    """Derive target membership from structured entries, never summary flags."""
    if not isinstance(observation,dict): return {"errors":["observation_malformed"]}
    target=expected["target_record_id"]+".record"; errors=[]
    states={}
    for field in ("records_entries","consumed_entries"):
        entries=observation.get(field)
        if not isinstance(entries,list): errors.append(f"{field}_missing"); continue
        names=[_entry_name(e) for e in entries]
        count=names.count(target)
        if count>1: errors.append(f"duplicate_target_entry:{field}")
        if any(n is None for n in names): errors.append(f"malformed_entry:{field}")
        if target in names:
            match=entries[names.index(target)]
            if isinstance(match,dict) and match.get("hash") not in (None,expected.get("expected_target_hash")):
                errors.append(f"target_hash_mismatch:{field}")
            if isinstance(match,dict) and match.get("record_id") not in (None,expected["target_record_id"]):
                errors.append(f"target_identity_mismatch:{field}")
        states[field]={"names":names,"target_present":count==1,"target_count":count}
    r=states.get("records_entries",{}).get("target_present",False); c=states.get("consumed_entries",{}).get("target_present",False)
    if r and c: errors.append("target_in_both")
    if not r and not c: errors.append("target_missing_from_both")
    if observation.get("target_hash") not in (None,expected.get("expected_target_hash")): errors.append("target_hash_mismatch:observation")
    if observation.get("target_record_id") != expected["target_record_id"]: errors.append("target_identity_mismatch:observation")
    response=observation.get("response")
    if observation.get("authoritative_success") is True or (isinstance(response,dict) and response.get("service_authoritative") is True): errors.append("authoritative_response_in_observation")
    return {"records":states.get("records_entries",{}),"consumed":states.get("consumed_entries",{}),"target_in_records":r,"target_in_consumed":c,"target_hash":observation.get("target_hash"),"errors":errors}

def derive_lifecycle_transition(before, after, expected):
    b=derive_target_state(before,expected); a=derive_target_state(after,expected); errors=list(b.get("errors",[]))+list(a.get("errors",[]));
    if errors: return {"added_records":[],"removed_records":[],"added_consumed":[],"removed_consumed":[],"errors":errors}
    def delta(k):
        bs=set(b[k]["names"]); as_=set(a[k]["names"]); return sorted(as_-bs),sorted(bs-as_)
    ar,rr=delta("records"); ac,rc=delta("consumed")
    allowed=[]
    for t in expected.get("expected_lifecycle_contract",{}).get("permitted_transitions",[]):
        if isinstance(t,dict): allowed.append((tuple(sorted(t.get("added_records",[]))),tuple(sorted(t.get("removed_records",[]))),tuple(sorted(t.get("added_consumed",[]))),tuple(sorted(t.get("removed_consumed",[])))))
    actual=(tuple(ar),tuple(rr),tuple(ac),tuple(rc))
    if actual != ((),(),(),()) and actual not in allowed: errors.append("unauthorized_lifecycle_transition")
    return {"added_records":ar,"removed_records":rr,"added_consumed":ac,"removed_consumed":rc,"errors":errors}

def validate_lifecycle_sequence(expected_contract, observations, expected):
    if not isinstance(expected_contract,dict): return ["lifecycle_contract_missing"]
    order=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored"); reasons=[]; states={}
    if not isinstance(observations,dict): return ["observations_missing"]
    for stage in order:
        if stage not in observations: reasons.append(f"observation_missing:{stage}"); continue
        derived=derive_target_state(observations[stage],expected); states[stage]=derived; reasons += [f"{stage}:{x}" for x in derived.get("errors",[])]
        contract=expected_contract.get("stages",{}).get(stage,{})
        if derived.get("target_in_records") != contract.get("target_in_records") or derived.get("target_in_consumed") != contract.get("target_in_consumed"): reasons.append(f"{stage}:unexpected_target_state")
        if derived.get("target_hash") not in (None,expected.get("expected_target_hash")): reasons.append(f"{stage}:target_hash_mismatch")
    for before,after in zip(order,order[1:]):
        if before in observations and after in observations: reasons += [f"{before}->{after}:{x}" for x in derive_lifecycle_transition(observations[before],observations[after],expected).get("errors",[])]
    return reasons

def derive_target_lifecycle(observations, expected):
    contract=expected.get("expected_lifecycle_contract",{})
    return {"errors":validate_lifecycle_sequence(contract,observations,expected)}

def _lifecycle_valid(life, expected, observations):
    reasons=derive_target_lifecycle(observations,expected).get("errors",[])
    if not isinstance(life,dict) or not isinstance(life.get("deltas"),dict): reasons.append("lifecycle_summary_missing")
    return reasons

RESTORATION_VOLATILE_FIELDS={"service_pid":"controlled restart may change PID","timestamp":"observation time changes","inode":"recreation may change inode only when preregistered"}
RESTORATION_FIELDS=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")

def compare_restoration(baseline, restored, expected, arm_cleanup_contract=None):
    result={"matched_fields":[],"allowed_changed_fields":[],"unexpected_changed_fields":[],"missing_fields":[],"fault_mechanism_disabled":False,"restoration_pass":False}
    expected_baseline=expected.get("expected_restoration",{})
    if not isinstance(baseline,dict) or not isinstance(restored,dict): result["missing_fields"] += ["baseline_observation","restored_observation"]; return result
    for field in RESTORATION_FIELDS:
        if field not in baseline or field not in restored: result["missing_fields"].append(field); continue
        if field in RESTORATION_VOLATILE_FIELDS:
            if baseline[field]!=restored[field]: result["allowed_changed_fields"].append(field)
        elif baseline[field]!=restored[field]: result["unexpected_changed_fields"].append(field)
        elif field in expected_baseline and baseline[field]!=expected_baseline[field]: result["unexpected_changed_fields"].append(f"baseline:{field}")
        else: result["matched_fields"].append(field)
    result["fault_mechanism_disabled"]=restored.get("fault_state")==expected_baseline.get("fault_state") and restored.get("fault_state",{}).get("active") is False
    result["restoration_pass"]=not result["missing_fields"] and not result["unexpected_changed_fields"] and result["fault_mechanism_disabled"]
    return result

def validate_cleanup(cleanup, expected):
    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified","baseline_observation","restored_observation")
    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
    comparison=compare_restoration(cleanup.get("baseline_observation"),cleanup.get("restored_observation"),expected)
    if not comparison["restoration_pass"]: reasons += ["restoration:"+x for x in comparison["missing_fields"]+comparison["unexpected_changed_fields"]];
    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True or not comparison["fault_mechanism_disabled"]: reasons.append("cleanup_not_verified")
    return reasons

def expected_authorization_context(expected, trusted_provenance=None):
    out={"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"RQ16_ARM_EXECUTION_AUTHORIZED"}
    if trusted_provenance: out.update({"review_artifact_sha256":trusted_provenance["review_artifact_sha256"],"reviewer_designation":trusted_provenance["reviewer_designation"],"issuer_identity":trusted_provenance["issuer_identity"],"issuer_authority_artifact_sha256":trusted_provenance["issuer_authority_artifact_sha256"]})
    return out

def validate_authorization_provenance(token, expected_trusted_provenance, actual_file_metadata=None, actual_artifact_digest=None):
    if not isinstance(expected_trusted_provenance,dict): return ["trusted_authorization_provenance_unavailable"]
    req=("issuer_identity","issuer_authority_artifact_sha256","reviewer_designation","review_artifact_sha256","trusted_storage_identity","trusted_owner","trusted_mode")
    reasons=[f"trusted_provenance_missing:{k}" for k in req if k not in expected_trusted_provenance]
    if reasons: return reasons
    for k in ("issuer_identity","reviewer_designation","review_artifact_sha256","issuer_authority_artifact_sha256"):
        if token.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"authorization_provenance_mismatch:{k}")
    if not isinstance(actual_file_metadata,dict): reasons.append("trusted_storage_metadata_missing")
    else:
        for k in ("trusted_storage_identity","trusted_owner","trusted_mode"):
            if actual_file_metadata.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"trusted_storage_mismatch:{k}")
    if actual_artifact_digest is None or actual_artifact_digest!=expected_trusted_provenance.get("review_artifact_sha256"): reasons.append("review_artifact_digest_unverified")
    if actual_file_metadata is None or actual_file_metadata.get("issuer_authority_artifact_digest")!=expected_trusted_provenance.get("issuer_authority_artifact_sha256"): reasons.append("issuer_artifact_digest_unverified")
    return reasons

def validate_authorization_token(token, expected, now=None, used_nonces=None, trusted_provenance=None, actual_file_metadata=None, actual_review_artifact_digest=None):
    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
    ctx=expected_authorization_context(expected,trusted_provenance)
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
    reasons += validate_authorization_provenance(token,trusted_provenance,actual_file_metadata,actual_review_artifact_digest)
    return reasons

def evaluate_arm(arm, observed, expected, observer_context=None, actual_raw_artifact_digest=None):
    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
    reasons=[]
    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected,observer_context,actual_raw_artifact_digest)
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


### implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json sha256=c54b27af07686999f812264ff3540c4af8f780279c2cc395c2c4d718130e8c34

```json
{
  "exit_code": 0,
  "stderr": "test_absent_response_not_success (__main__.RQ16Tests.test_absent_response_not_success) ... ok\ntest_authority_and_duplicate_transitions_red_or_reject (__main__.RQ16Tests.test_authority_and_duplicate_transitions_red_or_reject) ... ok\ntest_cleanup_exact_baseline_comparison (__main__.RQ16Tests.test_cleanup_exact_baseline_comparison) ... ok\ntest_cross_arm_proof_rejected (__main__.RQ16Tests.test_cross_arm_proof_rejected) ... ok\ntest_expected_context_required (__main__.RQ16Tests.test_expected_context_required) ... ok\ntest_observer_cleanup_lifecycle_mutations_reject (__main__.RQ16Tests.test_observer_cleanup_lifecycle_mutations_reject) ... ok\ntest_provenance_mutations_reject (__main__.RQ16Tests.test_provenance_mutations_reject) ... ok\ntest_rq17_gate_cannot_be_overridden_by_boolean (__main__.RQ16Tests.test_rq17_gate_cannot_be_overridden_by_boolean) ... ok\ntest_target_mutations_reject (__main__.RQ16Tests.test_target_mutations_reject) ... ok\ntest_token_requires_durable_trusted_binding (__main__.RQ16Tests.test_token_requires_durable_trusted_binding) ... ok\ntest_valid_structured_expected_observed_passes (__main__.RQ16Tests.test_valid_structured_expected_observed_passes) ... ok\n\n----------------------------------------------------------------------\nRan 11 tests in <elapsed>\n\nOK\n\ntest_absolute_outside_root_rejected (__main__.ManifestTests.test_absolute_outside_root_rejected) ... ok\ntest_clean_manifest_is_deterministic (__main__.ManifestTests.test_clean_manifest_is_deterministic) ... ok\ntest_duplicate_path_rejected (__main__.ManifestTests.test_duplicate_path_rejected) ... ok\ntest_generated_packet_is_not_source (__main__.ManifestTests.test_generated_packet_is_not_source) ... ok\ntest_manifest_hash_is_content_hash (__main__.ManifestTests.test_manifest_hash_is_content_hash) ... ok\ntest_missing_file_fails (__main__.ManifestTests.test_missing_file_fails) ... ok\ntest_source_byte_change_changes_manifest (__main__.ManifestTests.test_source_byte_change_changes_manifest) ... ok\n\n----------------------------------------------------------------------\nRan 7 tests in <elapsed>\n\nOK\n\n",
  "stdout": "",
  "tests": [
    {
      "name": "test_absent_response_not_success",
      "result": "PASS"
    },
    {
      "name": "test_authority_and_duplicate_transitions_red_or_reject",
      "result": "PASS"
    },
    {
      "name": "test_cleanup_exact_baseline_comparison",
      "result": "PASS"
    },
    {
      "name": "test_cross_arm_proof_rejected",
      "result": "PASS"
    },
    {
      "name": "test_expected_context_required",
      "result": "PASS"
    },
    {
      "name": "test_observer_cleanup_lifecycle_mutations_reject",
      "result": "PASS"
    },
    {
      "name": "test_provenance_mutations_reject",
      "result": "PASS"
    },
    {
      "name": "test_rq17_gate_cannot_be_overridden_by_boolean",
      "result": "PASS"
    },
    {
      "name": "test_target_mutations_reject",
      "result": "PASS"
    },
    {
      "name": "test_token_requires_durable_trusted_binding",
      "result": "PASS"
    },
    {
      "name": "test_valid_structured_expected_observed_passes",
      "result": "PASS"
    },
    {
      "name": "test_absolute_outside_root_rejected",
      "result": "PASS"
    },
    {
      "name": "test_clean_manifest_is_deterministic",
      "result": "PASS"
    },
    {
      "name": "test_duplicate_path_rejected",
      "result": "PASS"
    },
    {
      "name": "test_generated_packet_is_not_source",
      "result": "PASS"
    },
    {
      "name": "test_manifest_hash_is_content_hash",
      "result": "PASS"
    },
    {
      "name": "test_missing_file_fails",
      "result": "PASS"
    },
    {
      "name": "test_source_byte_change_changes_manifest",
      "result": "PASS"
    }
  ],
  "tests_failed": 0,
  "tests_passed": 18,
  "tests_total": 18
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json sha256=13352f4d9f42e8ae94d9157414f3cbde667add5b7d85e65990929cb036e5b40a

```json
{
  "RQ16_EXECUTED": false,
  "all_rejected": true,
  "exit_code": 0,
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
        "observer_context_mismatch:observer_identity"
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
        "raw_artifact_digest_mismatch"
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
        "fault_active->post_failure:duplicate_target_entry:consumed_entries",
        "post_failure->pre_cleanup:duplicate_target_entry:consumed_entries",
        "post_failure:duplicate_target_entry:consumed_entries"
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
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
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
        "restoration:service_binary_sha256"
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
        "restoration:gate_sha256"
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
        "restoration:mode"
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
        "restoration:owner"
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
        "restoration:socket_state"
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
        "restoration:records_entries"
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
        "restoration:historical_evidence"
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
        "cleanup_not_verified",
        "restoration:consumed_device",
        "restoration:consumed_entries",
        "restoration:consumed_fs",
        "restoration:consumed_mount",
        "restoration:consumed_realpath",
        "restoration:fault_state",
        "restoration:gate_sha256",
        "restoration:historical_evidence",
        "restoration:mode",
        "restoration:owner",
        "restoration:records_device",
        "restoration:records_entries",
        "restoration:records_fs",
        "restoration:records_mount",
        "restoration:records_realpath",
        "restoration:security_controls",
        "restoration:service_binary_sha256",
        "restoration:service_identity",
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_target_missing",
      "path": "baseline_target_missing",
      "reasons": [
        "baseline->pre_injection:target_missing_from_both",
        "baseline:target_missing_from_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_already_consumed",
      "path": "baseline_already_consumed",
      "reasons": [
        "baseline->pre_injection:target_in_both",
        "baseline:target_in_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_missing_both",
      "path": "post_failure_missing_both",
      "reasons": [
        "fault_active->post_failure:target_missing_from_both",
        "post_failure->pre_cleanup:target_missing_from_both",
        "post_failure:target_missing_from_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_both",
      "path": "post_failure_both",
      "reasons": [
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target_consumed",
      "path": "wrong_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "historical_target_consumed",
      "path": "historical_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "unrelated_target_transition",
      "path": "unrelated_target_transition",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_authoritative_consumption",
      "path": "duplicate_authoritative_consumption",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "second_authoritative_retry",
      "path": "second_authoritative_retry",
      "reasons": [
        "fault_active->post_failure:authoritative_response_in_observation",
        "post_failure->pre_cleanup:authoritative_response_in_observation",
        "post_failure:authoritative_response_in_observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "replay_state_mutation",
      "path": "replay_state_mutation",
      "reasons": [
        "post_cleanup->restored:target_missing_from_both",
        "restored:target_missing_from_both",
        "restored:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_hash_changed",
      "path": "target_hash_changed",
      "reasons": [
        "fault_active->post_failure:target_hash_mismatch:observation",
        "post_failure->pre_cleanup:target_hash_mismatch:observation",
        "post_failure:target_hash_mismatch",
        "post_failure:target_hash_mismatch:observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_identity_changed",
      "path": "target_identity_changed",
      "reasons": [
        "fault_active->post_failure:target_identity_mismatch:observation",
        "post_failure->pre_cleanup:target_identity_mismatch:observation",
        "post_failure:target_identity_mismatch:observation",
        "target_binding:target_record_id"
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
        "restoration:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_device",
      "path": "cleanup_device",
      "reasons": [
        "restoration:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mount",
      "path": "cleanup_mount",
      "reasons": [
        "restoration:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fs",
      "path": "cleanup_fs",
      "reasons": [
        "restoration:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_realpath",
      "path": "cleanup_realpath",
      "reasons": [
        "restoration:records_realpath"
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
        "restoration:owner"
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
        "restoration:mode"
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
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_still_active",
      "path": "cleanup_fault_still_active",
      "reasons": [
        "cleanup_not_verified",
        "restoration:fault_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_unrelated_record",
      "path": "cleanup_unrelated_record",
      "reasons": [
        "restoration:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_changed",
      "path": "cleanup_historical_changed",
      "reasons": [
        "restoration:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_hash",
      "path": "cleanup_arbitrary_hash",
      "reasons": [
        "restoration:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_owner",
      "path": "cleanup_arbitrary_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_mode",
      "path": "cleanup_arbitrary_mode",
      "reasons": [
        "restoration:mode"
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
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
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
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
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
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
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
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
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
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_self_issued",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_candidate_writable",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "issuer-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_issuer_hash",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "review-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_review_hash",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_wrong_reviewer",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "BOUNDED_PASS",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_generic_bounded_pass",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "CHANGES_REQUIRED",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_changes_required",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "INSUFFICIENT_EVIDENCE",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_insufficient_evidence",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "absent",
      "before": "absent",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_unavailable",
      "path": "trusted_provenance",
      "reasons": [
        "trusted_authorization_provenance_unavailable"
      ],
      "rejected": true
    }
  ],
  "rejected_mutations": 96,
  "surviving_mutations": 0,
  "total_mutations": 96
}
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
{
  "tests_total": 18,
  "tests_passed": 18,
  "tests_failed": 0,
  "mutation_total": 96,
  "mutation_rejected": 96,
  "mutation_surviving": 0,
  "all_rejected": true
}
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
        "observer_context_mismatch:observer_identity"
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
        "raw_artifact_digest_mismatch"
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
        "fault_active->post_failure:duplicate_target_entry:consumed_entries",
        "post_failure->pre_cleanup:duplicate_target_entry:consumed_entries",
        "post_failure:duplicate_target_entry:consumed_entries"
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
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
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
        "restoration:service_binary_sha256"
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
        "restoration:gate_sha256"
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
        "restoration:mode"
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
        "restoration:owner"
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
        "restoration:socket_state"
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
        "restoration:records_entries"
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
        "restoration:historical_evidence"
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
        "cleanup_not_verified",
        "restoration:consumed_device",
        "restoration:consumed_entries",
        "restoration:consumed_fs",
        "restoration:consumed_mount",
        "restoration:consumed_realpath",
        "restoration:fault_state",
        "restoration:gate_sha256",
        "restoration:historical_evidence",
        "restoration:mode",
        "restoration:owner",
        "restoration:records_device",
        "restoration:records_entries",
        "restoration:records_fs",
        "restoration:records_mount",
        "restoration:records_realpath",
        "restoration:security_controls",
        "restoration:service_binary_sha256",
        "restoration:service_identity",
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_target_missing",
      "path": "baseline_target_missing",
      "reasons": [
        "baseline->pre_injection:target_missing_from_both",
        "baseline:target_missing_from_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_already_consumed",
      "path": "baseline_already_consumed",
      "reasons": [
        "baseline->pre_injection:target_in_both",
        "baseline:target_in_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_missing_both",
      "path": "post_failure_missing_both",
      "reasons": [
        "fault_active->post_failure:target_missing_from_both",
        "post_failure->pre_cleanup:target_missing_from_both",
        "post_failure:target_missing_from_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_both",
      "path": "post_failure_both",
      "reasons": [
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target_consumed",
      "path": "wrong_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "historical_target_consumed",
      "path": "historical_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "unrelated_target_transition",
      "path": "unrelated_target_transition",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_authoritative_consumption",
      "path": "duplicate_authoritative_consumption",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "second_authoritative_retry",
      "path": "second_authoritative_retry",
      "reasons": [
        "fault_active->post_failure:authoritative_response_in_observation",
        "post_failure->pre_cleanup:authoritative_response_in_observation",
        "post_failure:authoritative_response_in_observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "replay_state_mutation",
      "path": "replay_state_mutation",
      "reasons": [
        "post_cleanup->restored:target_missing_from_both",
        "restored:target_missing_from_both",
        "restored:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_hash_changed",
      "path": "target_hash_changed",
      "reasons": [
        "fault_active->post_failure:target_hash_mismatch:observation",
        "post_failure->pre_cleanup:target_hash_mismatch:observation",
        "post_failure:target_hash_mismatch",
        "post_failure:target_hash_mismatch:observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_identity_changed",
      "path": "target_identity_changed",
      "reasons": [
        "fault_active->post_failure:target_identity_mismatch:observation",
        "post_failure->pre_cleanup:target_identity_mismatch:observation",
        "post_failure:target_identity_mismatch:observation",
        "target_binding:target_record_id"
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
        "restoration:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_device",
      "path": "cleanup_device",
      "reasons": [
        "restoration:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mount",
      "path": "cleanup_mount",
      "reasons": [
        "restoration:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fs",
      "path": "cleanup_fs",
      "reasons": [
        "restoration:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_realpath",
      "path": "cleanup_realpath",
      "reasons": [
        "restoration:records_realpath"
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
        "restoration:owner"
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
        "restoration:mode"
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
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_still_active",
      "path": "cleanup_fault_still_active",
      "reasons": [
        "cleanup_not_verified",
        "restoration:fault_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_unrelated_record",
      "path": "cleanup_unrelated_record",
      "reasons": [
        "restoration:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_changed",
      "path": "cleanup_historical_changed",
      "reasons": [
        "restoration:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_hash",
      "path": "cleanup_arbitrary_hash",
      "reasons": [
        "restoration:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_owner",
      "path": "cleanup_arbitrary_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_mode",
      "path": "cleanup_arbitrary_mode",
      "reasons": [
        "restoration:mode"
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
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
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
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
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
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
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
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
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
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_self_issued",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_candidate_writable",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "issuer-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_issuer_hash",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "review-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_review_hash",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_wrong_reviewer",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "BOUNDED_PASS",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_generic_bounded_pass",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "CHANGES_REQUIRED",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_changes_required",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "INSUFFICIENT_EVIDENCE",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_insufficient_evidence",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "absent",
      "before": "absent",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_unavailable",
      "path": "trusted_provenance",
      "reasons": [
        "trusted_authorization_provenance_unavailable"
      ],
      "rejected": true
    }
  ],
  "rejected_mutations": 96,
  "surviving_mutations": 0,
  "total_mutations": 96
}
```


### packet-check

```text
Traceback (most recent call last):
  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 35, in <module>
    if __name__=='__main__': raise SystemExit(main())
                                              ^^^^^^
  File "C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\check_rq16_preregistration_packet.py", line 22, in main
    assert declared==expected_manifest, 'source_manifest_entries_mismatch'
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: source_manifest_entries_mismatch
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
index 00000000..50e3ae54
--- /dev/null
+++ b/governance-runtime/build_rq16_preregistration_review.py
@@ -0,0 +1,22 @@
+from __future__ import annotations
+import hashlib, os, subprocess
+from pathlib import Path
+from rq16_manifest import canonical_review_source_files, canonical_evidence_files, build_source_manifest, build_evidence_manifest, manifest_sha256
+ROOT=Path(__file__).resolve().parents[1]
+OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'
+FILES=canonical_review_source_files(ROOT)
+EVIDENCE_FILES=canonical_evidence_files(ROOT)
+def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+def main():
+    current=run(['git','rev-parse','HEAD']).stdout.strip(); current_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); reviewed=os.environ.get('REVIEWED_SOURCE_COMMIT',current); reviewed_tree=os.environ.get('REVIEWED_SOURCE_TREE',run(['git','rev-parse',f'{reviewed}^{{tree}}']).stdout.strip()); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet_parent=current; packet_parent_tree=current_tree
+    diff=run(['git','diff',predecessor,reviewed,'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md']).stdout
+    tests=run(['python','governance-runtime/collect_rq16_results.py']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
+    source_manifest=build_source_manifest(FILES,ROOT); evidence_manifest=build_evidence_manifest(ROOT); ids=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_parent_commit={packet_parent}',f'packet_parent_tree={packet_parent_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_source_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}',f'source_manifest_sha256={manifest_sha256(source_manifest)}',f'generated_evidence_manifest_sha256={manifest_sha256(evidence_manifest)}','packet_content_identity_schema_version=2']
+    parts=['# V24-I11-V6 RQ-16 preregistration remediation-6 review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*ids,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION','packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION','packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION','RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[2].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[5].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[1].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[4].read_text(),'json'), '## Source manifest',source_manifest,'## Generated evidence manifest',evidence_manifest]
+    for p in FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+    for p in EVIDENCE_FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'json'))
+    parts += ['## Static and behavioral results',fence('plan',plan.stdout+plan.stderr),fence('self-test',selftest.stdout+selftest.stderr),fence('tests',tests.stdout+tests.stderr),fence('mutations',mutations.stdout+mutations.stderr,'json'),fence('packet-check',consistency.stdout+consistency.stderr),fence('execution-refusal',refuse.stdout+refuse.stderr), '## Exact predecessor-to-reviewed-source diff', fence('diff',diff), '## Manual-review questions','Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.']
+    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
+if __name__=='__main__': main()
diff --git a/governance-runtime/check_rq16_preregistration_packet.py b/governance-runtime/check_rq16_preregistration_packet.py
new file mode 100644
index 00000000..1b0ca493
--- /dev/null
+++ b/governance-runtime/check_rq16_preregistration_packet.py
@@ -0,0 +1,35 @@
+#!/usr/bin/env python3
+"""Verify preregistration identities knowable before packet commit."""
+import hashlib, json, re, subprocess
+from pathlib import Path
+from rq16_manifest import canonical_review_source_files, build_source_manifest, canonical_evidence_files, build_evidence_manifest, manifest_sha256
+ROOT=Path(__file__).resolve().parents[1]
+PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'
+SOURCE_FILES=canonical_review_source_files(ROOT)
+def main():
+    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
+    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
+    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
+    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
+    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
+    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
+    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
+    assert vals['packet_content_identity_schema_version']=='2'
+    manifest_match=re.search(r'## Source manifest\n(.*?)(?:\n### |\n## )',text,re.S)
+    assert manifest_match, 'source_manifest_section_missing'
+    declared=json.loads(manifest_match.group(1).strip())
+    expected_manifest=json.loads(build_source_manifest(SOURCE_FILES,ROOT))
+    assert declared==expected_manifest, 'source_manifest_entries_mismatch'
+    manifest=build_source_manifest(SOURCE_FILES,ROOT)
+    assert manifest_sha256(manifest)==vals['source_manifest_sha256'], 'source_manifest_hash_mismatch'
+    evidence_match=re.search(r'## Generated evidence manifest\n(.*?)(?:\n### |\n## )',text,re.S); assert evidence_match, 'evidence_manifest_section_missing'
+    assert json.loads(evidence_match.group(1).strip())==json.loads(build_evidence_manifest(ROOT)), 'evidence_manifest_entries_mismatch'
+    tests=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json').read_text()); muts=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json').read_text())
+    assert tests['tests_total']==tests['tests_passed']+tests['tests_failed'] and tests['exit_code']==0, 'test_result_binding_mismatch'
+    assert muts['total_mutations']==len(muts['mutations']) and muts['rejected_mutations']+muts['surviving_mutations']==muts['total_mutations'] and muts['all_rejected']==(muts['surviving_mutations']==0), 'mutation_result_binding_mismatch'
+    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
+    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
+    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-[56]-REVIEW)\.md',text,re.M)
+    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
+if __name__=='__main__': raise SystemExit(main())
diff --git a/governance-runtime/collect_rq16_results.py b/governance-runtime/collect_rq16_results.py
new file mode 100644
index 00000000..d1339df2
--- /dev/null
+++ b/governance-runtime/collect_rq16_results.py
@@ -0,0 +1,25 @@
+#!/usr/bin/env python3
+"""Generate the single authoritative offline RQ-16 test and mutation results."""
+import json, re, subprocess
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+TEST_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json'
+MUT_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json'
+def main():
+    runs=[subprocess.run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py'],cwd=ROOT,text=True,capture_output=True),subprocess.run(['python','governance-runtime/test_rq16_manifest.py'],cwd=ROOT,text=True,capture_output=True)]
+    t=subprocess.CompletedProcess([],max((x.returncode for x in runs),default=0),stdout='\n'.join(x.stdout for x in runs),stderr='\n'.join(x.stderr for x in runs))
+    m=subprocess.run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'],cwd=ROOT,text=True,capture_output=True)
+    combined=re.sub(r'Ran (\d+) tests? in [0-9.]+s',r'Ran \1 tests in <elapsed>',t.stderr+t.stdout)
+    matches=re.findall(r'Ran (\d+) tests?',combined); total=sum(int(x) for x in matches)
+    tests=[]
+    for line in combined.splitlines():
+        hit=re.match(r'test_\w+ \(__main__\.[^)]+\) \.\.\. (ok|FAIL)',line)
+        if hit: tests.append({'name':line.split(' (',1)[0],'result':'PASS' if hit.group(1)=='ok' else 'FAIL'})
+    test_result={'tests_total':total,'tests_passed':sum(x['result']=='PASS' for x in tests),'tests_failed':sum(x['result']=='FAIL' for x in tests),'exit_code':t.returncode,'tests':tests,'stdout':'','stderr':combined}
+    mutation_result=json.loads(m.stdout)
+    mutation_result['exit_code']=m.returncode
+    TEST_OUT.write_text(json.dumps(test_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
+    MUT_OUT.write_text(json.dumps(mutation_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
+    print(json.dumps({'tests_total':test_result['tests_total'],'tests_passed':test_result['tests_passed'],'tests_failed':test_result['tests_failed'],'mutation_total':mutation_result['total_mutations'],'mutation_rejected':mutation_result['rejected_mutations'],'mutation_surviving':mutation_result['surviving_mutations'],'all_rejected':mutation_result['all_rejected']},indent=2))
+    return 0 if t.returncode==0 and m.returncode==0 else 1
+if __name__=='__main__': raise SystemExit(main())
diff --git a/governance-runtime/rq16_manifest.py b/governance-runtime/rq16_manifest.py
new file mode 100644
index 00000000..1f1d6bfd
--- /dev/null
+++ b/governance-runtime/rq16_manifest.py
@@ -0,0 +1,53 @@
+#!/usr/bin/env python3
+"""Canonical source/evidence manifest definitions for the RQ-16 review packet."""
+import hashlib, json
+from pathlib import Path
+
+ROOT=Path(__file__).resolve().parents[1]
+SOURCE_RELATIVE=(
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md",
+    "governance-runtime/build_rq16_preregistration_review.py",
+    "governance-runtime/check_rq16_preregistration_packet.py",
+    "governance-runtime/collect_rq16_results.py",
+    "governance-runtime/run_v24_v6_rq1_rq16_mutations.py",
+    "governance-runtime/rq16_manifest.py",
+    "governance-runtime/test_v24_v6_rq1_rq16_harness.py",
+    "governance-runtime/test_rq16_manifest.py",
+    "governance-runtime/v24_v6_rq1_rq16_harness.py",
+)
+EVIDENCE_RELATIVE=(
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json",
+)
+
+def canonical_review_source_files(root=ROOT):
+    return [root / rel for rel in SOURCE_RELATIVE]
+
+def canonical_evidence_files(root=ROOT):
+    return [root / rel for rel in EVIDENCE_RELATIVE]
+
+def _entries(files, root=ROOT):
+    entries=[]
+    for path in files:
+        rel=path.resolve().relative_to(root.resolve()).as_posix()
+        if rel.startswith("/") or Path(rel).is_absolute() or ".." in Path(rel).parts:
+            raise ValueError(f"non-canonical path: {rel}")
+        entries.append({"path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
+    if len({e["path"] for e in entries}) != len(entries):
+        raise ValueError("duplicate canonical path")
+    return sorted(entries,key=lambda e:e["path"])
+
+def build_source_manifest(files=None, root=ROOT):
+    return json.dumps(_entries(files or canonical_review_source_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
+
+def build_evidence_manifest(root=ROOT):
+    return json.dumps(_entries(canonical_evidence_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
+
+def manifest_sha256(manifest):
+    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()
diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
new file mode 100644
index 00000000..51b75148
--- /dev/null
+++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
@@ -0,0 +1,86 @@
+#!/usr/bin/env python3
+import copy, hashlib, json
+from datetime import datetime, timezone
+from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, expected_fault_observer_context, validate_authorization_token
+from test_v24_v6_rq1_rq16_harness import good, TRUSTED
+EXPECTED=expected_context("ENOSPC")
+OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
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
+      ("baseline_target_missing",lambda e:e["observations"]["baseline"].update(records_entries=[])),
+      ("baseline_already_consumed",lambda e:e["observations"]["baseline"].update(consumed_entries=["abc123.record"])),
+      ("post_failure_missing_both",lambda e:e["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
+      ("post_failure_both",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
+      ("wrong_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["other.record"])),
+      ("historical_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
+      ("unrelated_target_transition",lambda e:e["observations"]["post_failure"].update(records_entries=["abc123.record","other.record"])),
+      ("duplicate_authoritative_consumption",lambda e:e.update(authoritative_success=True)),
+      ("second_authoritative_retry",lambda e:e["observations"]["post_failure"].update(response={"service_authoritative":True})),
+      ("replay_state_mutation",lambda e:e["observations"]["restored"].update(records_entries=["other.record"])),
+      ("target_hash_changed",lambda e:e["observations"]["post_failure"].update(target_hash="changed")),
+      ("target_identity_changed",lambda e:e["observations"]["post_failure"].update(target_record_id="other")),
+      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
+      ("cleanup_device",lambda e:e["cleanup_proof"]["restored_observation"].update(records_device="bad")),
+      ("cleanup_mount",lambda e:e["cleanup_proof"]["restored_observation"].update(records_mount="bad")),
+      ("cleanup_fs",lambda e:e["cleanup_proof"]["restored_observation"].update(records_fs="bad")),
+      ("cleanup_realpath",lambda e:e["cleanup_proof"]["restored_observation"].update(records_realpath="bad")),
+      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
+      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
+      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
+      ("cleanup_fault_still_active",lambda e:e["cleanup_proof"]["restored_observation"].update(fault_state={"active":True})),
+      ("cleanup_unrelated_record",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=["abc123.record","other.record"])),
+      ("cleanup_historical_changed",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence={"intact":False})),
+      ("cleanup_arbitrary_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="arbitrary")),
+      ("cleanup_arbitrary_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="arbitrary")),
+      ("cleanup_arbitrary_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="arbitrary")),
+    ]
+    rows=[]
+    for name,mut in specs:
+        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)
+        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+    token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
+    metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
+    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
+    for field in auth_fields:
+        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
+        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used,trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    for name,field,value in (("self_issued","issuer_identity","candidate"),("candidate_writable","source_path","candidate"),("placeholder_issuer_hash","issuer_authority_artifact_sha256","issuer-sha"),("placeholder_review_hash","review_artifact_sha256","review-sha"),("wrong_reviewer","reviewer_designation","candidate"),("generic_bounded_pass","independent_review_disposition","BOUNDED_PASS"),("changes_required","independent_review_disposition","CHANGES_REQUIRED"),("insufficient_evidence","independent_review_disposition","INSUFFICIENT_EVIDENCE")):
+        bad=dict(token); bad[field]=value; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_provenance_"+name,"case":"AUTHORIZATION_PROVENANCE","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    reasons=validate_authorization_token(token,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_provenance_unavailable","case":"AUTHORIZATION_PROVENANCE","path":"trusted_provenance","before":"absent","after":"absent","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
+    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+if __name__=="__main__": raise SystemExit(main())
diff --git a/governance-runtime/test_rq16_manifest.py b/governance-runtime/test_rq16_manifest.py
new file mode 100644
index 00000000..eee9c711
--- /dev/null
+++ b/governance-runtime/test_rq16_manifest.py
@@ -0,0 +1,36 @@
+#!/usr/bin/env python3
+import shutil, unittest
+from contextlib import contextmanager
+from pathlib import Path
+from rq16_manifest import ROOT, canonical_review_source_files, build_source_manifest, manifest_sha256
+
+class ManifestTests(unittest.TestCase):
+    @contextmanager
+    def scratch(self):
+        d=ROOT/".rq16-manifest-test"; shutil.rmtree(d,ignore_errors=True); d.mkdir()
+        try: yield d
+        finally: shutil.rmtree(d,ignore_errors=True)
+    def test_clean_manifest_is_deterministic(self):
+        files=canonical_review_source_files(ROOT)
+        self.assertEqual(build_source_manifest(files),build_source_manifest(list(reversed(files))))
+        self.assertEqual(len({x.relative_to(ROOT).as_posix() for x in files}),len(files))
+    def test_source_byte_change_changes_manifest(self):
+        with self.scratch() as d:
+            p=d/"x.py"; p.write_bytes(b"x=1\n"); before=build_source_manifest([p],d); p.write_bytes(b"x=2\n"); self.assertNotEqual(before,build_source_manifest([p],d))
+    def test_duplicate_path_rejected(self):
+        with self.scratch() as d:
+            p=d/"x"; p.write_bytes(b"x");
+            with self.assertRaises(ValueError): build_source_manifest([p,p],d)
+    def test_missing_file_fails(self):
+        with self.assertRaises(FileNotFoundError): build_source_manifest([ROOT/"does-not-exist"],ROOT)
+    def test_absolute_outside_root_rejected(self):
+        with self.scratch() as d:
+            p=d/"x"; p.write_bytes(b"x");
+            with self.assertRaises(ValueError): build_source_manifest([Path("C:/outside-rq16/x")],ROOT)
+    def test_generated_packet_is_not_source(self):
+        names={p.name for p in canonical_review_source_files(ROOT)}
+        self.assertNotIn("V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md",names)
+    def test_manifest_hash_is_content_hash(self):
+        self.assertEqual(len(manifest_sha256(build_source_manifest())),64)
+
+if __name__=="__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..54e6f15c
--- /dev/null
+++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,73 @@
+#!/usr/bin/env python3
+import copy, hashlib, unittest
+from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context, expected_fault_observer_context
+
+EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
+OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
+TRUSTED={"issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":hashlib.sha256(b"issuer").hexdigest(),"reviewer_designation":"independent-reviewer","review_artifact_sha256":hashlib.sha256(b"review").hexdigest(),"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600"}
+def observation():
+    return {s:{"target_record_id":TARGET,"target_hash":"target-hash","records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+def good():
+    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":OBSERVER["observer_identity"],"observer_source_sha256":OBSERVER["observer_source_sha256"],"observer_execution_identity":OBSERVER["observer_execution_identity"],"expected_evidence_root":OBSERVER["expected_evidence_root"],"expected_owner":OBSERVER["expected_owner"],"expected_mode":OBSERVER["expected_mode"],"expected_host_identity":OBSERVER["expected_host_identity"],"expected_runtime_identity":OBSERVER["expected_runtime_identity"],"raw_artifact_path":"/var/lib/v24-rq1/rq16-attestations/a.raw","raw_artifact_sha256":ARTIFACT_DIGEST,"cleanup_reference":"clean"}
+    base=copy.deepcopy(EXPECTED["expected_restoration"])
+    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}
+
+class RQ16Tests(unittest.TestCase):
+    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
+    def test_target_mutations_reject(self):
+        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
+            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
+            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
+            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_provenance_mutations_reject(self):
+        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
+            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_observer_cleanup_lifecycle_mutations_reject(self):
+        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        mutations=[
+            ("baseline_target_missing",lambda x:x["observations"]["baseline"].update(records_entries=[])),
+            ("baseline_target_already_consumed",lambda x:x["observations"]["baseline"].update(consumed_entries=[TARGET+".record"])),
+            ("post_failure_target_missing_both",lambda x:x["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
+            ("post_failure_target_both",lambda x:x["observations"]["post_failure"].update(consumed_entries=[TARGET+".record"])),
+            ("wrong_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["other.record"])),
+            ("historical_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
+            ("unrelated_target_transition",lambda x:x["observations"]["post_failure"].update(records_entries=[TARGET+".record","other.record"])),
+            ("duplicate_authoritative_consumption",lambda x:x.update(authoritative_success=True)),
+            ("second_authoritative_retry",lambda x:x["observations"]["post_failure"].update(response={"service_authoritative":True})),
+            ("replay_state_mutation",lambda x:x["observations"]["restored"].update(records_entries=["other.record"])),
+            ("target_hash_changed",lambda x:x["observations"]["post_failure"].update(target_hash="changed")),
+            ("target_identity_changed",lambda x:x["observations"]["post_failure"].update(target_record_id="other")),
+        ]
+        for _,mut in mutations:
+            e=good(); mut(e); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
+        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
+    def test_cleanup_exact_baseline_comparison(self):
+        fields=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
+        for field in fields:
+            e=good(); e["cleanup_proof"]["restored_observation"][field]="arbitrary"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["cleanup_proof"].update(cleanup_ok=True); e["cleanup_proof"].pop("baseline_observation"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_authority_and_duplicate_transitions_red_or_reject(self):
+        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"RED")
+        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_token_requires_durable_trusted_binding(self):
+        self.assertTrue(validate_authorization_token({},EXPECTED))
+        token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
+        metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
+        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
+        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
+            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
+        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"},trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
+    def test_cross_arm_proof_rejected(self):
+        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"),OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_absent_response_not_success(self):
+        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+
+if __name__=="__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..4918ad16
--- /dev/null
+++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,256 @@
+#!/usr/bin/env python3
+"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
+from __future__ import annotations
+import argparse, hashlib, json, math, re
+from datetime import datetime, timezone
+
+ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
+OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
+MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}
+TRUSTED_AUTHORIZATION_PROVENANCE_AVAILABLE=False
+
+def expected_trusted_authorization_provenance():
+    """No governance-authorized issuer is available during preregistration."""
+    return None
+
+def expected_context(arm, record_id="abc123"):
+    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
+    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
+    baseline={"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_realpath":rp,"consumed_realpath":cp,"owner":{"uid":0,"gid":0},"mode":{"records":"0700","consumed":"0700"},"socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"service_identity":"uid0:trusted-service","security_controls":{"policy":"stable"},"fault_state":{"active":False},"records_entries":[record_id+".record"],"consumed_entries":[],"historical_evidence":{"intact":True}}
+    stages={s:{"target_in_records":True,"target_in_consumed":False,"target_hash":"target-hash"} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+    lifecycle={"status":"MANUAL_REVIEW_REQUIRED","stages":stages,"permitted_transitions":[]}
+    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_target_hash":"target-hash","expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","expected_restoration":baseline,"expected_lifecycle_contract":lifecycle}
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
+def expected_fault_observer_context():
+    return {"observer_identity":"trusted-root-observer","observer_source_sha256":hashlib.sha256(b"preregistered-trusted-root-observer-v1").hexdigest(),"observer_execution_identity":"root-observer-v1","expected_evidence_root":"/var/lib/v24-rq1/rq16-attestations","expected_owner":"root","expected_mode":"0600","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound"}
+
+def validate_trusted_fault_attestation(att, expected, observer_context, actual_raw_artifact_digest):
+    """Validate independently collected attestation; harness claims are not enough."""
+    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity","raw_artifact_path","raw_artifact_sha256","cleanup_reference")
+    if not isinstance(att,dict): return ["trusted_attestation_missing"]
+    if not isinstance(observer_context,dict): return ["expected_observer_context_missing"]
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
+    for k in ("observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity"):
+        if att.get(k) != observer_context.get(k): reasons.append(f"observer_context_mismatch:{k}")
+    if not isinstance(actual_raw_artifact_digest,str) or att["raw_artifact_sha256"] != actual_raw_artifact_digest: reasons.append("raw_artifact_digest_mismatch")
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
+def _entry_name(entry):
+    return entry if isinstance(entry,str) else entry.get("name") if isinstance(entry,dict) else None
+
+def _entry_hash(entry):
+    return entry.get("hash") if isinstance(entry,dict) else None
+
+def derive_target_state(observation, expected):
+    """Derive target membership from structured entries, never summary flags."""
+    if not isinstance(observation,dict): return {"errors":["observation_malformed"]}
+    target=expected["target_record_id"]+".record"; errors=[]
+    states={}
+    for field in ("records_entries","consumed_entries"):
+        entries=observation.get(field)
+        if not isinstance(entries,list): errors.append(f"{field}_missing"); continue
+        names=[_entry_name(e) for e in entries]
+        count=names.count(target)
+        if count>1: errors.append(f"duplicate_target_entry:{field}")
+        if any(n is None for n in names): errors.append(f"malformed_entry:{field}")
+        if target in names:
+            match=entries[names.index(target)]
+            if isinstance(match,dict) and match.get("hash") not in (None,expected.get("expected_target_hash")):
+                errors.append(f"target_hash_mismatch:{field}")
+            if isinstance(match,dict) and match.get("record_id") not in (None,expected["target_record_id"]):
+                errors.append(f"target_identity_mismatch:{field}")
+        states[field]={"names":names,"target_present":count==1,"target_count":count}
+    r=states.get("records_entries",{}).get("target_present",False); c=states.get("consumed_entries",{}).get("target_present",False)
+    if r and c: errors.append("target_in_both")
+    if not r and not c: errors.append("target_missing_from_both")
+    if observation.get("target_hash") not in (None,expected.get("expected_target_hash")): errors.append("target_hash_mismatch:observation")
+    if observation.get("target_record_id") != expected["target_record_id"]: errors.append("target_identity_mismatch:observation")
+    response=observation.get("response")
+    if observation.get("authoritative_success") is True or (isinstance(response,dict) and response.get("service_authoritative") is True): errors.append("authoritative_response_in_observation")
+    return {"records":states.get("records_entries",{}),"consumed":states.get("consumed_entries",{}),"target_in_records":r,"target_in_consumed":c,"target_hash":observation.get("target_hash"),"errors":errors}
+
+def derive_lifecycle_transition(before, after, expected):
+    b=derive_target_state(before,expected); a=derive_target_state(after,expected); errors=list(b.get("errors",[]))+list(a.get("errors",[]));
+    if errors: return {"added_records":[],"removed_records":[],"added_consumed":[],"removed_consumed":[],"errors":errors}
+    def delta(k):
+        bs=set(b[k]["names"]); as_=set(a[k]["names"]); return sorted(as_-bs),sorted(bs-as_)
+    ar,rr=delta("records"); ac,rc=delta("consumed")
+    allowed=[]
+    for t in expected.get("expected_lifecycle_contract",{}).get("permitted_transitions",[]):
+        if isinstance(t,dict): allowed.append((tuple(sorted(t.get("added_records",[]))),tuple(sorted(t.get("removed_records",[]))),tuple(sorted(t.get("added_consumed",[]))),tuple(sorted(t.get("removed_consumed",[])))))
+    actual=(tuple(ar),tuple(rr),tuple(ac),tuple(rc))
+    if actual != ((),(),(),()) and actual not in allowed: errors.append("unauthorized_lifecycle_transition")
+    return {"added_records":ar,"removed_records":rr,"added_consumed":ac,"removed_consumed":rc,"errors":errors}
+
+def validate_lifecycle_sequence(expected_contract, observations, expected):
+    if not isinstance(expected_contract,dict): return ["lifecycle_contract_missing"]
+    order=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored"); reasons=[]; states={}
+    if not isinstance(observations,dict): return ["observations_missing"]
+    for stage in order:
+        if stage not in observations: reasons.append(f"observation_missing:{stage}"); continue
+        derived=derive_target_state(observations[stage],expected); states[stage]=derived; reasons += [f"{stage}:{x}" for x in derived.get("errors",[])]
+        contract=expected_contract.get("stages",{}).get(stage,{})
+        if derived.get("target_in_records") != contract.get("target_in_records") or derived.get("target_in_consumed") != contract.get("target_in_consumed"): reasons.append(f"{stage}:unexpected_target_state")
+        if derived.get("target_hash") not in (None,expected.get("expected_target_hash")): reasons.append(f"{stage}:target_hash_mismatch")
+    for before,after in zip(order,order[1:]):
+        if before in observations and after in observations: reasons += [f"{before}->{after}:{x}" for x in derive_lifecycle_transition(observations[before],observations[after],expected).get("errors",[])]
+    return reasons
+
+def derive_target_lifecycle(observations, expected):
+    contract=expected.get("expected_lifecycle_contract",{})
+    return {"errors":validate_lifecycle_sequence(contract,observations,expected)}
+
+def _lifecycle_valid(life, expected, observations):
+    reasons=derive_target_lifecycle(observations,expected).get("errors",[])
+    if not isinstance(life,dict) or not isinstance(life.get("deltas"),dict): reasons.append("lifecycle_summary_missing")
+    return reasons
+
+RESTORATION_VOLATILE_FIELDS={"service_pid":"controlled restart may change PID","timestamp":"observation time changes","inode":"recreation may change inode only when preregistered"}
+RESTORATION_FIELDS=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
+
+def compare_restoration(baseline, restored, expected, arm_cleanup_contract=None):
+    result={"matched_fields":[],"allowed_changed_fields":[],"unexpected_changed_fields":[],"missing_fields":[],"fault_mechanism_disabled":False,"restoration_pass":False}
+    expected_baseline=expected.get("expected_restoration",{})
+    if not isinstance(baseline,dict) or not isinstance(restored,dict): result["missing_fields"] += ["baseline_observation","restored_observation"]; return result
+    for field in RESTORATION_FIELDS:
+        if field not in baseline or field not in restored: result["missing_fields"].append(field); continue
+        if field in RESTORATION_VOLATILE_FIELDS:
+            if baseline[field]!=restored[field]: result["allowed_changed_fields"].append(field)
+        elif baseline[field]!=restored[field]: result["unexpected_changed_fields"].append(field)
+        elif field in expected_baseline and baseline[field]!=expected_baseline[field]: result["unexpected_changed_fields"].append(f"baseline:{field}")
+        else: result["matched_fields"].append(field)
+    result["fault_mechanism_disabled"]=restored.get("fault_state")==expected_baseline.get("fault_state") and restored.get("fault_state",{}).get("active") is False
+    result["restoration_pass"]=not result["missing_fields"] and not result["unexpected_changed_fields"] and result["fault_mechanism_disabled"]
+    return result
+
+def validate_cleanup(cleanup, expected):
+    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
+    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified","baseline_observation","restored_observation")
+    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
+    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
+    comparison=compare_restoration(cleanup.get("baseline_observation"),cleanup.get("restored_observation"),expected)
+    if not comparison["restoration_pass"]: reasons += ["restoration:"+x for x in comparison["missing_fields"]+comparison["unexpected_changed_fields"]];
+    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True or not comparison["fault_mechanism_disabled"]: reasons.append("cleanup_not_verified")
+    return reasons
+
+def expected_authorization_context(expected, trusted_provenance=None):
+    out={"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"RQ16_ARM_EXECUTION_AUTHORIZED"}
+    if trusted_provenance: out.update({"review_artifact_sha256":trusted_provenance["review_artifact_sha256"],"reviewer_designation":trusted_provenance["reviewer_designation"],"issuer_identity":trusted_provenance["issuer_identity"],"issuer_authority_artifact_sha256":trusted_provenance["issuer_authority_artifact_sha256"]})
+    return out
+
+def validate_authorization_provenance(token, expected_trusted_provenance, actual_file_metadata=None, actual_artifact_digest=None):
+    if not isinstance(expected_trusted_provenance,dict): return ["trusted_authorization_provenance_unavailable"]
+    req=("issuer_identity","issuer_authority_artifact_sha256","reviewer_designation","review_artifact_sha256","trusted_storage_identity","trusted_owner","trusted_mode")
+    reasons=[f"trusted_provenance_missing:{k}" for k in req if k not in expected_trusted_provenance]
+    if reasons: return reasons
+    for k in ("issuer_identity","reviewer_designation","review_artifact_sha256","issuer_authority_artifact_sha256"):
+        if token.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"authorization_provenance_mismatch:{k}")
+    if not isinstance(actual_file_metadata,dict): reasons.append("trusted_storage_metadata_missing")
+    else:
+        for k in ("trusted_storage_identity","trusted_owner","trusted_mode"):
+            if actual_file_metadata.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"trusted_storage_mismatch:{k}")
+    if actual_artifact_digest is None or actual_artifact_digest!=expected_trusted_provenance.get("review_artifact_sha256"): reasons.append("review_artifact_digest_unverified")
+    if actual_file_metadata is None or actual_file_metadata.get("issuer_authority_artifact_digest")!=expected_trusted_provenance.get("issuer_authority_artifact_sha256"): reasons.append("issuer_artifact_digest_unverified")
+    return reasons
+
+def validate_authorization_token(token, expected, now=None, used_nonces=None, trusted_provenance=None, actual_file_metadata=None, actual_review_artifact_digest=None):
+    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
+    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+    ctx=expected_authorization_context(expected,trusted_provenance)
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
+    reasons += validate_authorization_provenance(token,trusted_provenance,actual_file_metadata,actual_review_artifact_digest)
+    return reasons
+
+def evaluate_arm(arm, observed, expected, observer_context=None, actual_raw_artifact_digest=None):
+    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
+    reasons=[]
+    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
+    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
+    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
+    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
+    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected,observer_context,actual_raw_artifact_digest)
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
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json
new file mode 100644
index 00000000..b6385f17
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json
@@ -0,0 +1,1325 @@
+{
+  "RQ16_EXECUTED": false,
+  "all_rejected": true,
+  "exit_code": 0,
+  "mutations": [
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_device",
+      "path": "wrong_device",
+      "reasons": [
+        "fault_active:records_device_mismatch",
+        "fault_active:split_filesystem",
+        "rq17_contamination",
+        "target_binding:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_mount",
+      "path": "wrong_mount",
+      "reasons": [
+        "fault_active:records_mount_mismatch",
+        "rq17_contamination",
+        "target_binding:records_mount"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_filesystem",
+      "path": "wrong_filesystem",
+      "reasons": [
+        "fault_active:records_fs_mismatch",
+        "rq17_contamination",
+        "target_binding:records_fs"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "symlink",
+      "path": "symlink",
+      "reasons": [
+        "target_binding:records_symlink"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_target",
+      "path": "wrong_target",
+      "reasons": [
+        "wrong_target_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
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
+      "after": "mutated",
+      "before": "valid",
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
+      "after": "mutated",
+      "before": "valid",
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
+      "after": "mutated",
+      "before": "valid",
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
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_missing_raw_activation",
+      "path": "attestation_missing_raw_activation",
+      "reasons": [
+        "attestation_field_missing:fault_activation_raw_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_missing_raw_operation",
+      "path": "attestation_missing_raw_operation",
+      "reasons": [
+        "attestation_field_missing:operation_raw_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_wrong_observer",
+      "path": "attestation_wrong_observer",
+      "reasons": [
+        "observer_context_mismatch:observer_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_wrong_pid",
+      "path": "attestation_wrong_pid",
+      "reasons": [
+        "attestation_service_mismatch"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_wrong_artifact_hash",
+      "path": "attestation_wrong_artifact_hash",
+      "reasons": [
+        "raw_artifact_digest_mismatch"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_observer",
+      "path": "missing_observer",
+      "reasons": [
+        "observation_missing:restored"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "bool_only_observer",
+      "path": "bool_only_observer",
+      "reasons": [
+        "observations_missing"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_cleanup",
+      "path": "missing_cleanup",
+      "reasons": [
+        "cleanup_proof_missing"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "bool_only_cleanup",
+      "path": "bool_only_cleanup",
+      "reasons": [
+        "cleanup_proof_missing"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "duplicate_consume",
+      "path": "duplicate_consume",
+      "reasons": [
+        "fault_active->post_failure:duplicate_target_entry:consumed_entries",
+        "post_failure->pre_cleanup:duplicate_target_entry:consumed_entries",
+        "post_failure:duplicate_target_entry:consumed_entries"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "both_directories",
+      "path": "both_directories",
+      "reasons": [
+        "fault_active->post_failure:target_in_both",
+        "post_failure->pre_cleanup:target_in_both",
+        "post_failure:target_in_both",
+        "post_failure:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "rq17_false_but_changed",
+      "path": "rq17_false_but_changed",
+      "reasons": [
+        "fault_active:records_device_mismatch",
+        "fault_active:split_filesystem",
+        "rq17_contamination",
+        "target_binding:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "after": "mutated",
+      "before": "valid",
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
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "invalid_transition",
+      "path": "invalid_transition",
+      "reasons": [
+        "invalid_transition_after_fault"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "untrusted_expected_context",
+      "path": "untrusted_expected_context",
+      "reasons": [
+        "wrong_mechanism"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_service_hash",
+      "path": "cleanup_service_hash",
+      "reasons": [
+        "restoration:service_binary_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_gate_hash",
+      "path": "cleanup_gate_hash",
+      "reasons": [
+        "restoration:gate_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_mode",
+      "path": "cleanup_mode",
+      "reasons": [
+        "restoration:mode"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_owner",
+      "path": "cleanup_owner",
+      "reasons": [
+        "restoration:owner"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_socket",
+      "path": "cleanup_socket",
+      "reasons": [
+        "restoration:socket_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_fault_active",
+      "path": "cleanup_fault_active",
+      "reasons": [
+        "cleanup_not_verified"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_target_state",
+      "path": "cleanup_target_state",
+      "reasons": [
+        "restoration:records_entries"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_historical_evidence",
+      "path": "cleanup_historical_evidence",
+      "reasons": [
+        "restoration:historical_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_missing_restored",
+      "path": "cleanup_missing_restored",
+      "reasons": [
+        "cleanup_not_verified",
+        "restoration:consumed_device",
+        "restoration:consumed_entries",
+        "restoration:consumed_fs",
+        "restoration:consumed_mount",
+        "restoration:consumed_realpath",
+        "restoration:fault_state",
+        "restoration:gate_sha256",
+        "restoration:historical_evidence",
+        "restoration:mode",
+        "restoration:owner",
+        "restoration:records_device",
+        "restoration:records_entries",
+        "restoration:records_fs",
+        "restoration:records_mount",
+        "restoration:records_realpath",
+        "restoration:security_controls",
+        "restoration:service_binary_sha256",
+        "restoration:service_identity",
+        "restoration:socket_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "baseline_target_missing",
+      "path": "baseline_target_missing",
+      "reasons": [
+        "baseline->pre_injection:target_missing_from_both",
+        "baseline:target_missing_from_both",
+        "baseline:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "baseline_already_consumed",
+      "path": "baseline_already_consumed",
+      "reasons": [
+        "baseline->pre_injection:target_in_both",
+        "baseline:target_in_both",
+        "baseline:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "post_failure_missing_both",
+      "path": "post_failure_missing_both",
+      "reasons": [
+        "fault_active->post_failure:target_missing_from_both",
+        "post_failure->pre_cleanup:target_missing_from_both",
+        "post_failure:target_missing_from_both",
+        "post_failure:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "post_failure_both",
+      "path": "post_failure_both",
+      "reasons": [
+        "fault_active->post_failure:target_in_both",
+        "post_failure->pre_cleanup:target_in_both",
+        "post_failure:target_in_both",
+        "post_failure:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_target_consumed",
+      "path": "wrong_target_consumed",
+      "reasons": [
+        "fault_active->post_failure:unauthorized_lifecycle_transition",
+        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "historical_target_consumed",
+      "path": "historical_target_consumed",
+      "reasons": [
+        "fault_active->post_failure:unauthorized_lifecycle_transition",
+        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "unrelated_target_transition",
+      "path": "unrelated_target_transition",
+      "reasons": [
+        "fault_active->post_failure:unauthorized_lifecycle_transition",
+        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "duplicate_authoritative_consumption",
+      "path": "duplicate_authoritative_consumption",
+      "reasons": [
+        "authoritative_success_after_fault"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "second_authoritative_retry",
+      "path": "second_authoritative_retry",
+      "reasons": [
+        "fault_active->post_failure:authoritative_response_in_observation",
+        "post_failure->pre_cleanup:authoritative_response_in_observation",
+        "post_failure:authoritative_response_in_observation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "replay_state_mutation",
+      "path": "replay_state_mutation",
+      "reasons": [
+        "post_cleanup->restored:target_missing_from_both",
+        "restored:target_missing_from_both",
+        "restored:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "target_hash_changed",
+      "path": "target_hash_changed",
+      "reasons": [
+        "fault_active->post_failure:target_hash_mismatch:observation",
+        "post_failure->pre_cleanup:target_hash_mismatch:observation",
+        "post_failure:target_hash_mismatch",
+        "post_failure:target_hash_mismatch:observation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "target_identity_changed",
+      "path": "target_identity_changed",
+      "reasons": [
+        "fault_active->post_failure:target_identity_mismatch:observation",
+        "post_failure->pre_cleanup:target_identity_mismatch:observation",
+        "post_failure:target_identity_mismatch:observation",
+        "target_binding:target_record_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_gate_hash",
+      "path": "cleanup_gate_hash",
+      "reasons": [
+        "restoration:gate_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_device",
+      "path": "cleanup_device",
+      "reasons": [
+        "restoration:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_mount",
+      "path": "cleanup_mount",
+      "reasons": [
+        "restoration:records_mount"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_fs",
+      "path": "cleanup_fs",
+      "reasons": [
+        "restoration:records_fs"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_realpath",
+      "path": "cleanup_realpath",
+      "reasons": [
+        "restoration:records_realpath"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_owner",
+      "path": "cleanup_owner",
+      "reasons": [
+        "restoration:owner"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_mode",
+      "path": "cleanup_mode",
+      "reasons": [
+        "restoration:mode"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_socket",
+      "path": "cleanup_socket",
+      "reasons": [
+        "restoration:socket_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_fault_still_active",
+      "path": "cleanup_fault_still_active",
+      "reasons": [
+        "cleanup_not_verified",
+        "restoration:fault_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_unrelated_record",
+      "path": "cleanup_unrelated_record",
+      "reasons": [
+        "restoration:records_entries"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_historical_changed",
+      "path": "cleanup_historical_changed",
+      "reasons": [
+        "restoration:historical_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_arbitrary_hash",
+      "path": "cleanup_arbitrary_hash",
+      "reasons": [
+        "restoration:service_binary_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_arbitrary_owner",
+      "path": "cleanup_arbitrary_owner",
+      "reasons": [
+        "restoration:owner"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_arbitrary_mode",
+      "path": "cleanup_arbitrary_mode",
+      "reasons": [
+        "restoration:mode"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_arm",
+      "path": "arm",
+      "reasons": [
+        "token_mismatch:arm"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_mechanism_id",
+      "path": "mechanism_id",
+      "reasons": [
+        "token_mismatch:mechanism_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_mechanism_digest",
+      "path": "mechanism_digest",
+      "reasons": [
+        "token_mismatch:mechanism_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_plan_commit",
+      "path": "plan_commit",
+      "reasons": [
+        "token_mismatch:plan_commit"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_plan_tree",
+      "path": "plan_tree",
+      "reasons": [
+        "token_mismatch:plan_tree"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_plan_digest",
+      "path": "plan_digest",
+      "reasons": [
+        "token_mismatch:plan_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_execution_contract_digest",
+      "path": "execution_contract_digest",
+      "reasons": [
+        "token_mismatch:execution_contract_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_cleanup_contract_digest",
+      "path": "cleanup_contract_digest",
+      "reasons": [
+        "token_mismatch:cleanup_contract_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_host_identity",
+      "path": "host_identity",
+      "reasons": [
+        "token_mismatch:host_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_runtime_identity",
+      "path": "runtime_identity",
+      "reasons": [
+        "token_mismatch:runtime_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_service_binary_sha256",
+      "path": "service_binary_sha256",
+      "reasons": [
+        "token_mismatch:service_binary_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_gate_sha256",
+      "path": "gate_sha256",
+      "reasons": [
+        "token_mismatch:gate_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_records_device",
+      "path": "records_device",
+      "reasons": [
+        "token_mismatch:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_consumed_device",
+      "path": "consumed_device",
+      "reasons": [
+        "token_mismatch:consumed_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_records_mount_id",
+      "path": "records_mount_id",
+      "reasons": [
+        "token_mismatch:records_mount_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_consumed_mount_id",
+      "path": "consumed_mount_id",
+      "reasons": [
+        "token_mismatch:consumed_mount_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_independent_review_disposition",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_review_artifact_sha256",
+      "path": "review_artifact_sha256",
+      "reasons": [
+        "token_mismatch:review_artifact_sha256",
+        "authorization_provenance_mismatch:review_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_reviewer_designation",
+      "path": "reviewer_designation",
+      "reasons": [
+        "token_mismatch:reviewer_designation",
+        "authorization_provenance_mismatch:reviewer_designation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_issuer_identity",
+      "path": "issuer_identity",
+      "reasons": [
+        "token_mismatch:issuer_identity",
+        "authorization_provenance_mismatch:issuer_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_issuer_authority_artifact_sha256",
+      "path": "issuer_authority_artifact_sha256",
+      "reasons": [
+        "token_mismatch:issuer_authority_artifact_sha256",
+        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "2025-01-01T00:00:00Z",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_expired",
+      "path": "expiration",
+      "reasons": [
+        "expiration_invalid"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "2030-01-01T00:00:00Z",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_future_issued",
+      "path": "authorization_timestamp",
+      "reasons": [
+        "authorization_in_future",
+        "expiration_invalid"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "bad",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_malformed_timestamp",
+      "path": "expiration",
+      "reasons": [
+        "timestamp_unparseable"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_empty_nonce",
+      "path": "nonce",
+      "reasons": [
+        "nonce_invalid"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "used",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_reused_nonce",
+      "path": "nonce",
+      "reasons": [
+        "nonce_replay"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_untrusted_source",
+      "path": "source_path",
+      "reasons": [
+        "authorization_source_untrusted"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "memory",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_untrusted_registry",
+      "path": "single_use_registry",
+      "reasons": [
+        "nonce_registry_untrusted"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_self_issued",
+      "path": "issuer_identity",
+      "reasons": [
+        "token_mismatch:issuer_identity",
+        "authorization_provenance_mismatch:issuer_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_candidate_writable",
+      "path": "source_path",
+      "reasons": [
+        "authorization_source_untrusted"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "issuer-sha",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_placeholder_issuer_hash",
+      "path": "issuer_authority_artifact_sha256",
+      "reasons": [
+        "token_mismatch:issuer_authority_artifact_sha256",
+        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "review-sha",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_placeholder_review_hash",
+      "path": "review_artifact_sha256",
+      "reasons": [
+        "token_mismatch:review_artifact_sha256",
+        "authorization_provenance_mismatch:review_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_wrong_reviewer",
+      "path": "reviewer_designation",
+      "reasons": [
+        "token_mismatch:reviewer_designation",
+        "authorization_provenance_mismatch:reviewer_designation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "BOUNDED_PASS",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_generic_bounded_pass",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "CHANGES_REQUIRED",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_changes_required",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "INSUFFICIENT_EVIDENCE",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_insufficient_evidence",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "absent",
+      "before": "absent",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_unavailable",
+      "path": "trusted_provenance",
+      "reasons": [
+        "trusted_authorization_provenance_unavailable"
+      ],
+      "rejected": true
+    }
+  ],
+  "rejected_mutations": 96,
+  "surviving_mutations": 0,
+  "total_mutations": 96
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
index 00000000..d7308e97
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
@@ -0,0 +1,25 @@
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
+    "RQ16-TEST-SUFFICIENCY": "RESOLVED",
+    "RQ16-LIFECYCLE-DERIVATION": "RESOLVED",
+    "RQ16-CLEANUP-BASELINE-COMPARISON": "RESOLVED",
+    "RQ16-AUTHORIZATION-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
+    "RQ16-SOURCE-MANIFEST-RECOMPUTATION": "RESOLVED"
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
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json
new file mode 100644
index 00000000..ed1df712
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json
@@ -0,0 +1,82 @@
+{
+  "exit_code": 0,
+  "stderr": "test_absent_response_not_success (__main__.RQ16Tests.test_absent_response_not_success) ... ok\ntest_authority_and_duplicate_transitions_red_or_reject (__main__.RQ16Tests.test_authority_and_duplicate_transitions_red_or_reject) ... ok\ntest_cleanup_exact_baseline_comparison (__main__.RQ16Tests.test_cleanup_exact_baseline_comparison) ... ok\ntest_cross_arm_proof_rejected (__main__.RQ16Tests.test_cross_arm_proof_rejected) ... ok\ntest_expected_context_required (__main__.RQ16Tests.test_expected_context_required) ... ok\ntest_observer_cleanup_lifecycle_mutations_reject (__main__.RQ16Tests.test_observer_cleanup_lifecycle_mutations_reject) ... ok\ntest_provenance_mutations_reject (__main__.RQ16Tests.test_provenance_mutations_reject) ... ok\ntest_rq17_gate_cannot_be_overridden_by_boolean (__main__.RQ16Tests.test_rq17_gate_cannot_be_overridden_by_boolean) ... ok\ntest_target_mutations_reject (__main__.RQ16Tests.test_target_mutations_reject) ... ok\ntest_token_requires_durable_trusted_binding (__main__.RQ16Tests.test_token_requires_durable_trusted_binding) ... ok\ntest_valid_structured_expected_observed_passes (__main__.RQ16Tests.test_valid_structured_expected_observed_passes) ... ok\n\n----------------------------------------------------------------------\nRan 11 tests in <elapsed>\n\nOK\n\ntest_absolute_outside_root_rejected (__main__.ManifestTests.test_absolute_outside_root_rejected) ... ok\ntest_clean_manifest_is_deterministic (__main__.ManifestTests.test_clean_manifest_is_deterministic) ... ok\ntest_duplicate_path_rejected (__main__.ManifestTests.test_duplicate_path_rejected) ... ok\ntest_generated_packet_is_not_source (__main__.ManifestTests.test_generated_packet_is_not_source) ... ok\ntest_manifest_hash_is_content_hash (__main__.ManifestTests.test_manifest_hash_is_content_hash) ... ok\ntest_missing_file_fails (__main__.ManifestTests.test_missing_file_fails) ... ok\ntest_source_byte_change_changes_manifest (__main__.ManifestTests.test_source_byte_change_changes_manifest) ... ok\n\n----------------------------------------------------------------------\nRan 7 tests in <elapsed>\n\nOK\n\n",
+  "stdout": "",
+  "tests": [
+    {
+      "name": "test_absent_response_not_success",
+      "result": "PASS"
+    },
+    {
+      "name": "test_authority_and_duplicate_transitions_red_or_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_cleanup_exact_baseline_comparison",
+      "result": "PASS"
+    },
+    {
+      "name": "test_cross_arm_proof_rejected",
+      "result": "PASS"
+    },
+    {
+      "name": "test_expected_context_required",
+      "result": "PASS"
+    },
+    {
+      "name": "test_observer_cleanup_lifecycle_mutations_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_provenance_mutations_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_rq17_gate_cannot_be_overridden_by_boolean",
+      "result": "PASS"
+    },
+    {
+      "name": "test_target_mutations_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_token_requires_durable_trusted_binding",
+      "result": "PASS"
+    },
+    {
+      "name": "test_valid_structured_expected_observed_passes",
+      "result": "PASS"
+    },
+    {
+      "name": "test_absolute_outside_root_rejected",
+      "result": "PASS"
+    },
+    {
+      "name": "test_clean_manifest_is_deterministic",
+      "result": "PASS"
+    },
+    {
+      "name": "test_duplicate_path_rejected",
+      "result": "PASS"
+    },
+    {
+      "name": "test_generated_packet_is_not_source",
+      "result": "PASS"
+    },
+    {
+      "name": "test_manifest_hash_is_content_hash",
+      "result": "PASS"
+    },
+    {
+      "name": "test_missing_file_fails",
+      "result": "PASS"
+    },
+    {
+      "name": "test_source_byte_change_changes_manifest",
+      "result": "PASS"
+    }
+  ],
+  "tests_failed": 0,
+  "tests_passed": 18,
+  "tests_total": 18
+}
```

## Manual-review questions
Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.
