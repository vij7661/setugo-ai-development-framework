"""Plan/self-test-only runtime qualification harness.

No live provider, service, fault injection, or qualification action is exposed.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX = ROOT / "governance-r8/R8-V15-R1-RUNTIME-QUALIFICATION-MATRIX.json"


def load_matrix() -> dict:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    if data.get("status") != "PREREGISTERED_NON_AUTHORITATIVE":
        raise ValueError("matrix is not non-authoritative")
    if data.get("authority", {}).get("runtime_qualification_granted") is not False:
        raise ValueError("runtime qualification cannot be granted by harness")
    if data.get("authority", {}).get("live_execution_authorized") is not False:
        raise ValueError("live execution must remain unauthorized")
    return data


def validate_evidence(evidence: dict, *, expected_candidate: str) -> None:
    required = {"schema", "candidate_commit", "run_id", "toolchain", "environment", "arms", "independent_review"}
    if set(evidence) != required:
        raise ValueError("evidence key set mismatch")
    if evidence["candidate_commit"] != expected_candidate:
        raise ValueError("stale candidate evidence")
    if not evidence["run_id"] or not evidence["toolchain"] or not evidence["environment"]:
        raise ValueError("incomplete evidence identity")
    if evidence["independent_review"] is not False:
        raise ValueError("independent review must occur after run")
    arms = evidence["arms"]
    if not isinstance(arms, list) or not arms or any(not isinstance(a, dict) or not a.get("fault_proof") for a in arms):
        raise ValueError("missing fault proof or arms")


def evidence_digest(evidence: dict) -> str:
    return hashlib.sha256((json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if not (args.plan or args.self_test) or not args.plan and args.self_test:
        # self-test is also safe, but no default execution path exists
        pass
    matrix = load_matrix()
    if args.self_test:
        try:
            validate_evidence({"schema": "x"}, expected_candidate=matrix["candidate_commit"])
        except ValueError:
            pass
        else:
            raise SystemExit("malformed evidence accepted")
        print("RUNTIME_QUALIFICATION_HARNESS_SELF_TEST_PASS")
    if args.plan:
        print(json.dumps({"status": "PLAN_ONLY", "matrix_sha256": hashlib.sha256(MATRIX.read_bytes()).hexdigest(),
                          "arms": [a["id"] for a in matrix["arms"]], "live_execution": False,
                          "runtime_qualification_granted": False}, sort_keys=True))


if __name__ == "__main__":
    main()
