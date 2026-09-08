from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parent


def _load(name: str):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

blind = _load("blind_packet_v1")
isolation = _load("evidence_prompt_isolation_v1")
memory = _load("memory_admissibility_v1")
sequential = _load("sequential_review_v1")


def construct_r2_packet(*, source_packet: Dict[str, Any], mandatory_evidence_ids: Iterable[str], memory_items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    reviewer_packet = blind.build_reviewer_packet(source_packet)
    blind_validation = blind.validate_blind_packet(reviewer_packet)
    if not blind_validation["valid"]:
        raise ValueError("blind packet validation failed")

    frozen_evidence = list(reviewer_packet["evidence"])
    memory_result = memory.evaluate_admissibility(
        mandatory_evidence_ids=mandatory_evidence_ids,
        frozen_evidence=frozen_evidence,
        memory_items=list(memory_items),
        frozen_disposition="PASS",
    )
    if memory_result["missing_mandatory_evidence_ids"]:
        raise ValueError("mandatory evidence missing before review")

    isolated = isolation.build_review_packet(reviewer_packet["review_id"], frozen_evidence)
    return {
        "reviewer_packet": reviewer_packet,
        "blind_validation": blind_validation,
        "memory_admissibility": memory_result,
        "isolated_evidence_packet": isolated,
    }


def construct_r3_handoff(*, review_request: Dict[str, Any], frozen_packet: Dict[str, Any], policy: Dict[str, Any], r2_result: Dict[str, Any]) -> Dict[str, Any]:
    handoff = sequential.build_frozen_handoff(
        review_request=review_request,
        frozen_packet=frozen_packet,
        policy=policy,
        r2_result=r2_result,
    )
    if policy.get("promotion_authoritative") and not handoff["r3_required"]:
        raise ValueError("promotion-authoritative review cannot skip R3")
    return handoff


def final_adjudication(*, r2_result: Dict[str, Any], r3_result: Dict[str, Any], handoff: Dict[str, Any], mandatory_evidence_ids: Iterable[str], frozen_evidence: Iterable[Dict[str, Any]], memory_items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    if not handoff.get("r3_required"):
        raise ValueError("R3 was not required by handoff")
    if r2_result.get("review_id") != handoff["r2_normalized"].get("review_id"):
        raise ValueError("R2 identity mismatch")
    if not r3_result.get("review_id"):
        raise ValueError("R3 result missing review_id")

    r2_disp = r2_result.get("disposition")
    r3_disp = r3_result.get("disposition")
    promotion_candidate = r2_disp == "PASS" and r3_disp == "PASS"

    admissibility = memory.evaluate_admissibility(
        mandatory_evidence_ids=mandatory_evidence_ids,
        frozen_evidence=list(frozen_evidence),
        memory_items=list(memory_items),
        frozen_disposition="PASS" if promotion_candidate else "BLOCK",
    )

    promotable = promotion_candidate and admissibility["promotable"]
    return {
        "r2_disposition": r2_disp,
        "r3_disposition": r3_disp,
        "mandatory_evidence_complete": not admissibility["missing_mandatory_evidence_ids"],
        "memory_independent_authority": False,
        "promotable": promotable,
        "final_disposition": "PASS" if promotable else "BLOCK",
        "admissibility_decision_sha256": admissibility["decision_sha256"],
        "handoff_hash": handoff["handoff_hash"],
    }
