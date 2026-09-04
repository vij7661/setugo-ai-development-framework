#!/usr/bin/env python3
"""Provider-independent bounded failover router for governed reasoning tasks.

The router never changes task authority or reads protected truth. Each candidate
mechanism receives its own deterministic prepared envelope so evidence remains
bound to the actual provider/model selected after failover.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from adapters import normalize_adapter_result
from openai_compatible import OpenAICompatibleAdapter, RemoteProviderConfig
from prepare_run import prepare


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--case", required=True, type=Path)
    p.add_argument("--mechanisms", required=True, type=Path)
    p.add_argument("--order", required=True, help="comma-separated mechanism ids")
    p.add_argument("--instruction-version", required=True)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--evidence-out", required=True, type=Path)
    a=p.parse_args()

    case=load(a.case)
    registry={m["mechanism_id"]:m for m in load(a.mechanisms)["mechanisms"]}
    attempts=[]
    selected=None
    normalized=None

    for mechanism_id in [x.strip() for x in a.order.split(",") if x.strip()]:
        m=registry.get(mechanism_id)
        if not m or not m.get("enabled"):
            attempts.append({"mechanism_id":mechanism_id,"status":"SKIPPED","reason":"missing-or-disabled"})
            continue

        envelope=prepare(case,m,a.instruction_version)
        try:
            adapter=OpenAICompatibleAdapter(RemoteProviderConfig(provider_id=m["provider"],base_url=m["base_url"],model=m["model"],api_key_env=m["api_key_env"]))
            result=adapter.invoke(envelope)
            normalized=normalize_adapter_result(envelope,result)
            selected=mechanism_id
            attempts.append({"mechanism_id":mechanism_id,"provider":m["provider"],"status":"PASS","model":m["model"],"run_id":normalized["run_id"]})
            break
        except Exception as exc:
            attempts.append({"mechanism_id":mechanism_id,"provider":m["provider"],"status":"PROVIDER_FAILURE","model":m["model"],"run_id":envelope["run_id"],"reason":str(exc)[:1000]})

    evidence={
        "event_type":"PROVIDER_ROUTING_COMPLETED",
        "updated_at":datetime.now(timezone.utc).isoformat(),
        "case_id":case.get("case_id"),
        "instruction_version":a.instruction_version,
        "selected_mechanism":selected,
        "attempts":attempts,
        "portfolio_exhausted":selected is None,
    }
    a.evidence_out.parent.mkdir(parents=True,exist_ok=True)
    a.evidence_out.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    if normalized is None:
        raise RuntimeError("eligible provider portfolio exhausted without usable completion")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(normalized,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(a.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
