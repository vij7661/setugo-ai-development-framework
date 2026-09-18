"""Deterministic planning validator for the Remediation-2 Oracle Contract.

This validator does not execute the runtime or mutate the harness. It proves
that the contract is a closed 32-row binding to the preregistered matrix and
that no proxy row is accidentally approved.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ALLOWED = {"EXACT_MATCH", "REVIEWER_PROPOSAL_NEEDS_CORRECTION", "CURRENT_IMPLEMENTATION_IS_PROXY", "FROZEN_PLAN_AMBIGUOUS", "REQUIRES_SUCCESSOR_PREREGISTRATION"}

def validate(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    rows = obj.get("rows", [])
    assert len(rows) == 32, len(rows)
    ids = [r.get("rq_id") for r in rows]
    assert ids == [f"RQ-{i:02d}" for i in range(1, 33)], ids
    assert len(set(ids)) == 32
    for r in rows:
        assert r["exact_frozen_trigger"] and r["exact_frozen_oracle"]
        assert r["semantic_status"] in ALLOWED
        assert "PENDING_CLAUDE_REVIEW_2" not in json.dumps(r)
        assert r.get("implementation_decision") in {"KEEP", "REPLACE", "EXTEND", "BLOCK"}
        assert r.get("corrected_implementation_approach") and "generic" not in r["corrected_implementation_approach"].lower()
        assert r.get("reviewer_semantics_rationale") and r["reviewer_semantics_rationale"] != "true"
        assert r.get("independent_evidence_source") and r.get("cleanup_recovery_requirement")
        assert r.get("destructive_restoration_evidence")
        if r["implementation_decision"] == "KEEP":
            assert r["semantic_status"] == "EXACT_MATCH" and r["literal_trigger_execution"] and r["literal_oracle_proven"] and r["evidence_independent"] and r["cleanup_demonstrated"]
            assert "Claude Review #2" in r["reviewer_semantics_rationale"]
        if r["implementation_decision"] == "BLOCK":
            assert r["semantic_status"] in {"REQUIRES_SUCCESSOR_PREREGISTRATION", "FROZEN_PLAN_AMBIGUOUS"}
        assert r["semantic_status"] != "EXACT_MATCH" or (r["literal_trigger_execution"] and r["literal_oracle_proven"] and r["evidence_independent"] and r["cleanup_demonstrated"])
        assert r["cleanup_recovery_requirement"]
        assert r["independent_evidence_source"]
        if r["bound_runtime_mutation_required"]:
            assert r["cleanup_recovery_requirement"]
    c = obj["chronology"]
    for k in ("git_commit", "git_tree", "harness_sha256", "aws_instance", "frozen_baseline_ami", "frozen_snapshot", "authorization_reference", "run_timestamp", "bundle_sha256", "before_status_counts", "after_status_counts", "exact_harness_diff"):
        assert c.get(k), k
    return {"contract_validator": "PASS", "case_count": 32, "unique_ids": True, "proxy_approved": False, "destructive_cleanup_bound": True, "independent_pass_evidence_required": True}

if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("implementation/v24/V24-I11-V6-RQ1-REMEDIATION-2-ORACLE-CONTRACT.json")
    print(json.dumps(validate(p), sort_keys=True))
