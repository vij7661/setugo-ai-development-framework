from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .configuration import build_provider_registry, build_qualification_registry, load_configuration
from .models import ReviewRequest
from .orchestrator import ReviewEngine
from .risk_guard import classify_platform_facts
from .session_store import SQLiteSessionStore
from .sqlite_memory import SQLiteMemoryStore


def build_request(payload: dict) -> ReviewRequest:
    if not isinstance(payload, dict): raise ValueError("request payload must be an object")
    request_id = payload.get("request_id")
    user_input = payload.get("user_input")
    operation_class = payload.get("operation_class", "CHAT")
    if not isinstance(request_id, str) or not request_id.strip(): raise ValueError("request_id required")
    if not isinstance(user_input, str) or not user_input.strip(): raise ValueError("user_input required")
    capabilities = payload.get("connected_tool_capabilities", [])
    if not isinstance(capabilities, list): raise ValueError("connected_tool_capabilities must be a list")
    target_environment = payload.get("target_environment")
    user_declared_risk = payload.get("risk")
    facts = classify_platform_facts(
        operation_class=str(operation_class),
        connected_tool_capabilities=[str(v) for v in capabilities],
        target_environment=None if target_environment is None else str(target_environment),
        user_declared_risk=None if user_declared_risk is None else str(user_declared_risk),
    )
    materiality = payload.get("materiality")
    order = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
    if materiality is not None:
        if materiality not in order: raise ValueError("invalid materiality")
        effective_materiality = materiality if order[materiality] > order[facts.materiality_floor] else facts.materiality_floor
    else:
        effective_materiality = facts.materiality_floor
    uncertainty = str(payload.get("uncertainty", "LOW"))
    if uncertainty not in {"LOW", "MEDIUM", "HIGH"}: raise ValueError("invalid uncertainty")
    task_type = str(payload.get("task_type", "GENERAL"))
    return ReviewRequest(
        request_id=request_id.strip(), user_input=user_input, risk=facts.risk_floor,
        materiality=effective_materiality, external_action=facts.external_action,
        mutation_requested=facts.mutation_requested,
        requirement_ambiguity=bool(payload.get("requirement_ambiguity", False)),
        evidence_complete=bool(payload.get("evidence_complete", True)), uncertainty=uncertainty,
        platform_facts={
            "operation_class": facts.operation_class,
            "risk_reasons": list(facts.reasons),
            "human_approval_required": facts.human_approval_required,
            "target_environment": target_environment,
            "connected_tool_capabilities": [str(v) for v in capabilities],
            "task_type": task_type,
        },
    )


def run_from_files(*, config_path: str, request_path: str, memory_db: str, sessions_db: str) -> dict:
    configuration = load_configuration(config_path)
    providers = build_provider_registry(configuration)
    qualifications = build_qualification_registry(configuration)
    request = build_request(json.loads(Path(request_path).read_text(encoding="utf-8")))
    memory = SQLiteMemoryStore(memory_db)
    sessions = SQLiteSessionStore(sessions_db)
    engine = ReviewEngine(providers.invoke, session_store=sessions, qualification_registry=qualifications)
    decision = engine.run(
        request,
        r1=configuration.reviewer("R1"), r2=configuration.reviewer("R2"),
        r3=configuration.reviewer("R3"), memory=memory,
    )
    result = asdict(decision)
    result.update({
        "request_id": request.request_id,
        "platform_facts": request.platform_facts,
        "assurance_mode": configuration.assurance_mode,
        "action_authorized": False,
        "human_action_approval_required": bool(request.platform_facts.get("human_approval_required")),
        "session_chain_valid": sessions.validate_chain(request.request_id),
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Governed multi-LLM Review Engine MVP")
    parser.add_argument("--config", required=True, help="reviewer/provider JSON configuration")
    parser.add_argument("--request", required=True, help="request JSON")
    parser.add_argument("--memory-db", default="review-engine-memory.db")
    parser.add_argument("--sessions-db", default="review-engine-sessions.db")
    args = parser.parse_args()
    result = run_from_files(config_path=args.config, request_path=args.request, memory_db=args.memory_db, sessions_db=args.sessions_db)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
