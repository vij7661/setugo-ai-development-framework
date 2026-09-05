#!/usr/bin/env python3
"""Provider-independent bounded failover router for governed reasoning tasks."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from adapters import normalize_adapter_result
from openai_compatible import OpenAICompatibleAdapter, RemoteProviderConfig
from prepare_run import prepare

GOVERNANCE_DIR = Path(__file__).resolve().parents[1] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))
from failover_guard import authorize_failover
from runtime_identity import verify_runtime_identity_attestation


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def now():
    return datetime.now(timezone.utc).isoformat()


def _index(path: Path, key: str) -> dict:
    payload = load(path)
    return {row["mechanism_id"]: row for row in payload.get(key, [])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--mechanisms", required=True, type=Path)
    parser.add_argument("--qualifications", required=True, type=Path)
    parser.add_argument("--identity-attestations", required=True, type=Path)
    parser.add_argument("--order", required=True)
    parser.add_argument("--instruction-version", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--evidence-out", required=True, type=Path)
    args = parser.parse_args()

    case = load(args.case)
    registry = {m["mechanism_id"]: m for m in load(args.mechanisms)["mechanisms"]}
    order = [x.strip() for x in args.order.split(",") if x.strip()]
    attempts = []
    selected = None
    normalized = None

    original_route = next((registry[mid] for mid in order if registry.get(mid, {}).get("enabled")), None)
    if original_route is None:
        raise RuntimeError("eligible provider portfolio has no enabled route origin")

    for index, mechanism_id in enumerate(order):
        mechanism = registry.get(mechanism_id)
        if not mechanism or not mechanism.get("enabled"):
            attempts.append({"mechanism_id": mechanism_id, "provider": mechanism.get("provider") if mechanism else None, "status": "NOT_CALLED", "reason": "missing-or-disabled", "updated_at": now()})
            continue

        qualifications = _index(args.qualifications, "qualifications")
        attestations = _index(args.identity_attestations, "identity_attestations")
        qualification = qualifications.get(mechanism_id) or {}
        attestation = attestations.get(mechanism_id) or {}
        authorization = authorize_failover(original_route, mechanism, qualification)
        identity = verify_runtime_identity_attestation(mechanism, qualification, attestation)
        if not authorization["authorized"] or not identity["verified"]:
            reason = "qualification-denied:" + authorization["reason"] if not authorization["authorized"] else "identity-denied:" + identity["reason"]
            attempts.append({"mechanism_id": mechanism_id, "provider": mechanism.get("provider"), "model": mechanism.get("model"), "status": "NOT_CALLED", "attempts": 0, "reason": reason, "updated_at": now()})
            continue

        envelope = prepare(case, mechanism, args.instruction_version, expected_case_id=args.case.stem)
        started = now()
        try:
            adapter = OpenAICompatibleAdapter(RemoteProviderConfig(provider_id=mechanism["provider"], base_url=mechanism["base_url"], model=mechanism["model"], api_key_env=mechanism["api_key_env"]))
            result = adapter.invoke(envelope)

            # Response labels remain diagnostic only. Authority comes from the
            # out-of-band attestation above plus a fresh post-call revalidation.
            if result.provider != mechanism["provider"]:
                raise RuntimeError("transport provider identity does not match authorized route")

            # Re-read control-plane evidence after the remote call. A revocation,
            # qualification epoch change, or attestation withdrawal that occurs
            # while the call is in flight invalidates the result before admission.
            current_qualifications = _index(args.qualifications, "qualifications")
            current_attestations = _index(args.identity_attestations, "identity_attestations")
            current_qualification = current_qualifications.get(mechanism_id) or {}
            current_attestation = current_attestations.get(mechanism_id) or {}
            post_auth = authorize_failover(original_route, mechanism, current_qualification)
            post_identity = verify_runtime_identity_attestation(mechanism, current_qualification, current_attestation)
            if not post_auth["authorized"]:
                raise RuntimeError("post-call qualification revalidation failed:" + post_auth["reason"])
            if not post_identity["verified"]:
                raise RuntimeError("post-call identity revalidation failed:" + post_identity["reason"])

            candidate = normalize_adapter_result(envelope, result)
            if candidate["status"] != "PASS" or not candidate["evidence_eligible"]:
                detail = candidate.get("runtime_metadata", {}).get("normalization_error") or candidate["status"]
                raise RuntimeError(f"provider completion failed normalized evidence validation: {detail}")

            normalized = candidate
            selected = mechanism_id
            provider_attempts = None
            if result.runtime_metadata:
                value = result.runtime_metadata.get("provider_attempts")
                if isinstance(value, int) and value > 0:
                    provider_attempts = value
            attempts.append({
                "mechanism_id": mechanism_id, "provider": mechanism["provider"], "status": "SUCCESS", "model": mechanism["model"],
                "sku": mechanism["sku"], "deployment_path": mechanism["deployment_path"], "qualification_id": mechanism["qualification_id"],
                "qualification_epoch": mechanism["qualification_epoch"], "identity_attestation_ref": current_attestation.get("attestation_ref"),
                "run_id": normalized["run_id"], "attempts": provider_attempts, "started_at": started, "updated_at": now(),
            })
            for later in order[index + 1:]:
                later_mechanism = registry.get(later)
                attempts.append({"mechanism_id": later, "provider": later_mechanism.get("provider") if later_mechanism else None, "status": "NOT_CALLED", "model": later_mechanism.get("model") if later_mechanism else None, "attempts": 0, "reason": "first qualified attested success already obtained", "updated_at": now()})
            break
        except Exception as exc:
            text = str(exc)
            count = 3 if "attempt 3/3" in text else None
            attempts.append({"mechanism_id": mechanism_id, "provider": mechanism["provider"], "status": "FAILED", "model": mechanism["model"], "run_id": envelope["run_id"], "attempts": count, "started_at": started, "updated_at": now(), "reason": text[:1000]})

    evidence = {"event_type": "PROVIDER_ROUTING_COMPLETED", "updated_at": now(), "case_id": args.case.stem, "instruction_version": args.instruction_version, "selected_mechanism": selected, "attempts": attempts, "portfolio_exhausted": selected is None, "routing_rule": "QUALIFIED_ATTESTED_FIRST_SUCCESS"}
    args.evidence_out.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_out.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    if normalized is None:
        raise RuntimeError("eligible provider portfolio exhausted without usable completion")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
