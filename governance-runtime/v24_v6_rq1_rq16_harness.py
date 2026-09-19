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
