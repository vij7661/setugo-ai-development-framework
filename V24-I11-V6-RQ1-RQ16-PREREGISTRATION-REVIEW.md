# V24-I11-V6 RQ-16 preregistration review

Planning-only artifact. No RQ-16 execution occurred.

## Identity
predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
head=80a3f65c05f2e17362ee6799f72dd01bfe41feca
tree=dde2b0fdcc4f3dde0f11ec13e53c9546aa3deba0
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
    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
  ],
  "open_automatable_issues": 0,
  "manual_review_required": true,
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```

## Included file SHA-256
e63491de1fde5387992f3bdd10499fe43ffe702338530695664da47f7e7450a8  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422  implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769  implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
b1bca1d340b9231c552a7cf44e97718a5f77a6fcfbe017c7474942b7aa6f2906  implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
3c1240fde52af3eb0c5b98b63caa8b99b8636e0cf95ec56db257e27751f412b3  governance-runtime/v24_v6_rq1_rq16_harness.py
7f1a6b461344591db378df4245b7a1cec7af9c278855a18ad99feb4ff4898044  governance-runtime/test_v24_v6_rq1_rq16_harness.py
90515988f3a7dbe5bdef48fa193a062174bcc5a6a6c9fa40817f37a070c81746  governance-runtime/run_v24_v6_rq1_rq16_mutations.py

### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=3c1240fde52af3eb0c5b98b63caa8b99b8636e0cf95ec56db257e27751f412b3

```python
#!/usr/bin/env python3
"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}

def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
    reasons = []
    if arm not in ARMS: reasons.append("unknown_arm")
    proof = evidence.get("fault_proof")
    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
    args = ap.parse_args()
    if args.execute_rq16:
        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
        return 3
    if not (args.plan or args.self_test):
        ap.error("only --plan or --self-test is allowed")
    if args.self_test:
        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
```


### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=7f1a6b461344591db378df4245b7a1cec7af9c278855a18ad99feb4ff4898044

```python
#!/usr/bin/env python3
import unittest
from v24_v6_rq1_rq16_harness import evaluate_arm

def good(errno="ENOSPC"):
    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}

class RQ16SelfTests(unittest.TestCase):
    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
    def test_missing_or_wrong_fault_proof_never_passes(self):
        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
    def test_authority_and_cleanup_fail_closed(self):
        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
    def test_arms_cannot_substitute(self):
        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")

if __name__ == "__main__": unittest.main(verbosity=2)
```


### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=90515988f3a7dbe5bdef48fa193a062174bcc5a6a6c9fa40817f37a070c81746

```python
#!/usr/bin/env python3
"""Offline RQ-16 preregistration mutation checks; never touches the runtime."""
from __future__ import annotations
import copy, json
from v24_v6_rq1_rq16_harness import evaluate_arm

GOOD = {
    "fault_proof": {"injected": True, "errno": "ENOSPC"},
    "target_path": "/run/v24-v6-authority/private/records/T.record",
    "observer_ok": True, "cleanup_verified": True, "restored_exact": True,
    "service_recoverable": True, "lifecycle_explained": True,
}

def case(name, mutate, expected="reject"):
    ev = copy.deepcopy(GOOD); mutate(ev)
    actual, reasons = evaluate_arm("ENOSPC", ev)
    return {"mutation_id": name, "expected": expected, "actual": actual,
            "reasons": reasons, "rejected": actual != "PASS"}

def main():
    muts = [
        ("missing_fault_proof", lambda e: e.pop("fault_proof")),
        ("wrong_errno", lambda e: e["fault_proof"].update(errno="EROFS")),
        ("injected_false", lambda e: e["fault_proof"].update(injected=False)),
        ("observer_failure", lambda e: e.update(observer_ok=False)),
        ("cleanup_failure", lambda e: e.update(cleanup_verified=False)),
        ("restoration_mismatch", lambda e: e.update(restored_exact=False)),
        ("service_not_recoverable", lambda e: e.update(service_recoverable=False)),
        ("lifecycle_unexplained", lambda e: e.update(lifecycle_explained=False)),
        ("authoritative_success", lambda e: e.update(authoritative_success=True)),
        ("invalid_transition", lambda e: e.update(invalid_transition=True)),
        ("missing_target", lambda e: e.pop("target_path")),
        ("unknown_arm_cross_substitution", lambda e: None),
    ]
    results = []
    for name, mutate in muts:
        if name == "unknown_arm_cross_substitution":
            actual, reasons = evaluate_arm("EROFS", GOOD)
            results.append({"mutation_id": name, "expected": "reject", "actual": actual, "reasons": reasons, "rejected": actual != "PASS"})
        else:
            results.append(case(name, mutate))
    out = {"total_mutations": len(results), "rejected_mutations": sum(r["rejected"] for r in results),
           "surviving_mutations": sum(not r["rejected"] for r in results),
           "all_rejected": all(r["rejected"] for r in results), "mutations": results,
           "RQ16_EXECUTED": False}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["all_rejected"] and out["surviving_mutations"] == 0 else 2

if __name__ == "__main__": raise SystemExit(main())
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
  "results": [
    "PASS",
    "HARNESS_DEFECT",
    "HARNESS_DEFECT",
    "HARNESS_DEFECT",
    "RED",
    "HARNESS_DEFECT"
  ],
  "passed": true,
  "RQ16_EXECUTED": false
}
```


### unit output

```text
test_absent_response_is_not_success (__main__.RQ16SelfTests.test_absent_response_is_not_success) ... ok
test_arms_cannot_substitute (__main__.RQ16SelfTests.test_arms_cannot_substitute) ... ok
test_authority_and_cleanup_fail_closed (__main__.RQ16SelfTests.test_authority_and_cleanup_fail_closed) ... ok
test_missing_or_wrong_fault_proof_never_passes (__main__.RQ16SelfTests.test_missing_or_wrong_fault_proof_never_passes) ... ok
test_valid_evidence_is_only_candidate_pass (__main__.RQ16SelfTests.test_valid_evidence_is_only_candidate_pass) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```


### mutation output

```json
{
  "RQ16_EXECUTED": false,
  "all_rejected": true,
  "mutations": [
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "missing_fault_proof",
      "reasons": [
        "fault_not_proven",
        "errno_not_proven"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "wrong_errno",
      "reasons": [
        "wrong_errno"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "injected_false",
      "reasons": [
        "fault_not_proven"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "observer_failure",
      "reasons": [
        "observer_incomplete"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "cleanup_failure",
      "reasons": [
        "cleanup_not_verified"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "restoration_mismatch",
      "reasons": [
        "restoration_not_exact"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "service_not_recoverable",
      "reasons": [
        "service_not_recoverable"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "lifecycle_unexplained",
      "reasons": [
        "lifecycle_unexplained"
      ],
      "rejected": true
    },
    {
      "actual": "RED",
      "expected": "reject",
      "mutation_id": "authoritative_success",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual": "RED",
      "expected": "reject",
      "mutation_id": "invalid_transition",
      "reasons": [
        "invalid_transition_after_fault"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "missing_target",
      "reasons": [
        "target_path_missing"
      ],
      "rejected": true
    },
    {
      "actual": "HARNESS_DEFECT",
      "expected": "reject",
      "mutation_id": "unknown_arm_cross_substitution",
      "reasons": [
        "wrong_errno"
      ],
      "rejected": true
    }
  ],
  "rejected_mutations": 12,
  "surviving_mutations": 0,
  "total_mutations": 12
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
diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
new file mode 100644
index 00000000..12b110ab
--- /dev/null
+++ b/governance-runtime/build_rq16_preregistration_review.py
@@ -0,0 +1,19 @@
+from __future__ import annotations
+import hashlib, subprocess
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'
+FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py']
+def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+def main():
+    tests=run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16'])
+    diff=run(['git','diff','8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','HEAD']).stdout
+    parts=['# V24-I11-V6 RQ-16 preregistration review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity','predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f"branch={run(['git','branch','--show-current']).stdout.strip()}",f"head={run(['git','rev-parse','HEAD']).stdout.strip()}",f"tree={run(['git','rev-parse','HEAD^{tree}']).stdout.strip()}",'RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[1].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[0].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[2].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[3].read_text(),'json')]
+    parts.append('## Included file SHA-256\n' + '\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in FILES))
+    for p in FILES[4:]: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+    compile_result=run(['python','-m','compileall','-q']+[str(p) for p in FILES[4:]])
+    parts += ['## Static results', fence('plan output',plan.stdout+plan.stderr),fence('self-test output',selftest.stdout+selftest.stderr),fence('unit output',tests.stdout+tests.stderr),fence('execution refusal output',refuse.stdout+refuse.stderr),f'compile_exit={compile_result.returncode}', '## Exact diff from predecessor', fence('git diff',diff), '## Manual-review questions','','Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.']
+    OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8'); print(OUT)
+if __name__=='__main__': main()
diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..5a1d9777
--- /dev/null
+++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,21 @@
+#!/usr/bin/env python3
+import unittest
+from v24_v6_rq1_rq16_harness import evaluate_arm
+
+def good(errno="ENOSPC"):
+    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
+
+class RQ16SelfTests(unittest.TestCase):
+    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
+    def test_missing_or_wrong_fault_proof_never_passes(self):
+        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
+    def test_authority_and_cleanup_fail_closed(self):
+        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
+        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
+    def test_arms_cannot_substitute(self):
+        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
+        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
+        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
+    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")
+
+if __name__ == "__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..782816d7
--- /dev/null
+++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,44 @@
+#!/usr/bin/env python3
+"""RQ-16 preregistration harness: plan/self-test only; never executes faults."""
+from __future__ import annotations
+import argparse, json
+from pathlib import Path
+
+ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
+ERRNOS = {"ENOSPC", "EROFS", "EIO", "EACCES", "EPERM"}
+
+def evaluate_arm(arm: str, evidence: dict) -> tuple[str, list[str]]:
+    reasons = []
+    if arm not in ARMS: reasons.append("unknown_arm")
+    proof = evidence.get("fault_proof")
+    if not isinstance(proof, dict) or proof.get("injected") is not True: reasons.append("fault_not_proven")
+    if not isinstance(proof, dict) or proof.get("errno") not in ERRNOS: reasons.append("errno_not_proven")
+    if isinstance(proof, dict) and proof.get("errno") != arm and not (arm == "EACCES" and proof.get("errno") == "EPERM"): reasons.append("wrong_errno")
+    if not isinstance(evidence.get("target_path"), str): reasons.append("target_path_missing")
+    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
+    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
+    if evidence.get("observer_ok") is not True: reasons.append("observer_incomplete")
+    if evidence.get("cleanup_verified") is not True: reasons.append("cleanup_not_verified")
+    if evidence.get("restored_exact") is not True: reasons.append("restoration_not_exact")
+    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+    if evidence.get("lifecycle_explained") is not True: reasons.append("lifecycle_unexplained")
+    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", reasons)
+
+def main() -> int:
+    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--execute-rq16", action="store_true"); ap.add_argument("--authorization-token", type=Path)
+    args = ap.parse_args()
+    if args.execute_rq16:
+        print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"}))
+        return 3
+    if not (args.plan or args.self_test):
+        ap.error("only --plan or --self-test is allowed")
+    if args.self_test:
+        good = {"fault_proof":{"injected":True,"errno":"ENOSPC"},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}
+        bads = [dict(good, fault_proof={"injected":False,"errno":"ENOSPC"}), dict(good, fault_proof={"injected":True,"errno":"EROFS"}), dict(good, cleanup_verified=False), dict(good, authoritative_success=True), dict(good, observer_ok=False)]
+        results = [evaluate_arm("ENOSPC", good)[0]] + [evaluate_arm("ENOSPC", b)[0] for b in bads]
+        print(json.dumps({"mode":"SELF_TEST","results":results,"passed":results[0] == "PASS" and all(x != "PASS" for x in results[1:]),"RQ16_EXECUTED":False}, indent=2))
+        return 0 if results[0] == "PASS" and all(x != "PASS" for x in results[1:]) else 2
+    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False}, indent=2))
+    return 0
+
+if __name__ == "__main__": raise SystemExit(main())
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
index 00000000..5c0c9f14
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
@@ -0,0 +1,42 @@
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
+  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
new file mode 100644
index 00000000..00d465a3
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
@@ -0,0 +1,12 @@
+{
+  "issues": [
+    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"}
+  ],
+  "open_automatable_issues": 0,
+  "manual_review_required": true,
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
new file mode 100644
index 00000000..f0bdb1b2
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
@@ -0,0 +1,95 @@
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
```

## Manual-review questions

Determine independently whether each arm has a safe literal bound-runtime mechanism without changing the frozen oracle or colliding with RQ-17. Adjudicate the insufficient/unsafe classifications for ENOSPC, EROFS, EIO and EACCES. Do not authorize execution or RQ-16.
