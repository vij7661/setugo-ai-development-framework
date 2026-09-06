"""EXP-O Pilot 5 signed tool-result provenance and evidence verification.

A valid result signature establishes only provenance/integrity for this pilot.
It never grants authority and it does not prove semantic truth of tool content.
"""
from __future__ import annotations

import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping
from urllib import error as urlerror
from urllib import request as urlrequest

from runtime_slice_exp_o import _canonical, _digest, _effect_binding, _sign, _verify


REQUIRED_RESULT_FIELDS = {
    "result_schema_version",
    "result_key_id",
    "capability_id",
    "permit_id",
    "worker_id",
    "worker_key_thumbprint",
    "authority_epoch",
    "effect_contract_id",
    "effect_digest",
    "idempotency_key",
    "authoritative_effect_id",
    "execution_disposition",
    "gateway_instance_id",
    "gateway_result_time_ms",
    "tool_content",
}


def build_expected_result_lineage(
    *,
    capability: Mapping[str, Any],
    permit: Mapping[str, Any],
    worker_id: str,
    worker_key_thumbprint: str,
    effect: Mapping[str, Any],
    idempotency_key: str,
) -> dict[str, Any]:
    cap_payload = capability.get("payload") if isinstance(capability, Mapping) else None
    permit_payload = permit.get("payload") if isinstance(permit, Mapping) else None
    if not isinstance(cap_payload, Mapping) or not isinstance(permit_payload, Mapping):
        raise ValueError("capability and permit payloads are required")
    binding = _effect_binding(effect, idempotency_key=idempotency_key)
    return {
        "capability_id": cap_payload.get("capability_id"),
        "permit_id": permit_payload.get("permit_id"),
        "worker_id": worker_id,
        "worker_key_thumbprint": worker_key_thumbprint,
        "authority_epoch": permit_payload.get("authority_epoch"),
        "effect_contract_id": permit_payload.get("effect_contract_id"),
        "effect_digest": _digest(binding),
        "idempotency_key": idempotency_key,
    }


class GatewayLedgerReader:
    """Read-only reconciliation view of the Pilot 4/5 authoritative ledger."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)

    def lookup(self, idempotency_key: str) -> dict[str, Any] | None:
        if not Path(self.db_path).exists():
            return None
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    "SELECT idempotency_key, effect_digest, effect_id, result_json "
                    "FROM authoritative_effects WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
            except sqlite3.OperationalError:
                return None
        if row is None:
            return None
        return {
            "idempotency_key": str(row["idempotency_key"]),
            "effect_digest": str(row["effect_digest"]),
            "effect_id": str(row["effect_id"]),
            "result": json.loads(str(row["result_json"])),
        }

    def count(self) -> int:
        if not Path(self.db_path).exists():
            return 0
        with closing(sqlite3.connect(self.db_path)) as conn:
            try:
                row = conn.execute("SELECT COUNT(*) FROM authoritative_effects").fetchone()
            except sqlite3.OperationalError:
                return 0
        return 0 if row is None else int(row[0])


class ToolResultVerifier:
    """Independent evidence gate for signed tool-result envelopes."""

    def __init__(
        self,
        *,
        trusted_result_keys: Mapping[str, bytes],
        ledger_reader: GatewayLedgerReader,
    ) -> None:
        self._trusted_result_keys = dict(trusted_result_keys)
        self._ledger_reader = ledger_reader

    def verify(
        self,
        result_envelope: Mapping[str, Any] | None,
        *,
        expected_lineage: Mapping[str, Any],
        platform_authority: Mapping[str, Any] | None = None,
        transport_complete: bool = True,
    ) -> dict[str, Any]:
        authority = copy.deepcopy(dict(platform_authority or {}))
        base = {
            "transport_complete": bool(transport_complete),
            "evidence_eligible": False,
            "signature_valid": False,
            "lineage_valid": False,
            "ledger_reconciled": False,
            "effective_authority": authority,
            "tool_content_authority_effect": False,
            "follow_on_effect_authorized": False,
            "release_authorized": "RELEASE" in set(authority.get("allowed_actions", [])),
        }
        if not transport_complete:
            return {**base, "decision": "TRANSPORT_INCOMPLETE", "reason": "COMPLETE_RESULT_REQUIRED"}
        if not isinstance(result_envelope, Mapping):
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "SIGNED_RESULT_ENVELOPE_REQUIRED"}

        payload = result_envelope.get("payload")
        if not isinstance(payload, Mapping):
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "RESULT_PAYLOAD_REQUIRED"}
        missing = sorted(REQUIRED_RESULT_FIELDS - set(payload.keys()))
        if missing:
            return {
                **base,
                "decision": "RESULT_INELIGIBLE",
                "reason": "RESULT_REQUIRED_FIELD_MISSING",
                "missing_fields": missing,
            }

        key_id = payload.get("result_key_id")
        key = self._trusted_result_keys.get(str(key_id))
        if key is None:
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "RESULT_SIGNING_KEY_UNTRUSTED"}
        if not _verify(result_envelope, key):
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "RESULT_SIGNATURE_INVALID"}
        base["signature_valid"] = True

        try:
            int(payload.get("authority_epoch"))
            int(payload.get("gateway_result_time_ms"))
        except (TypeError, ValueError):
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "RESULT_LINEAGE_TYPE_INVALID"}

        for field in (
            "capability_id",
            "permit_id",
            "worker_id",
            "worker_key_thumbprint",
            "authority_epoch",
            "effect_contract_id",
            "effect_digest",
            "idempotency_key",
        ):
            if payload.get(field) != expected_lineage.get(field):
                return {
                    **base,
                    "decision": "RESULT_INELIGIBLE",
                    "reason": "RESULT_LINEAGE_MISMATCH",
                    "mismatched_field": field,
                }
        disposition = payload.get("execution_disposition")
        if disposition not in {"EXECUTED", "IDEMPOTENT_REPLAY"}:
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "RESULT_DISPOSITION_INVALID"}
        effect_id = payload.get("authoritative_effect_id")
        if not isinstance(effect_id, str) or not effect_id:
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "AUTHORITATIVE_EFFECT_ID_REQUIRED"}
        base["lineage_valid"] = True

        ledger = self._ledger_reader.lookup(str(payload.get("idempotency_key")))
        if ledger is None:
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "AUTHORITATIVE_LEDGER_RECORD_MISSING"}
        if ledger.get("effect_digest") != payload.get("effect_digest"):
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "LEDGER_EFFECT_DIGEST_MISMATCH"}
        if ledger.get("effect_id") != payload.get("authoritative_effect_id"):
            return {**base, "decision": "RESULT_INELIGIBLE", "reason": "LEDGER_EFFECT_ID_MISMATCH"}
        base["ledger_reconciled"] = True

        return {
            **base,
            "evidence_eligible": True,
            "decision": "RESULT_EVIDENCE_ELIGIBLE",
            "reason": "SIGNED_LINEAGE_AND_LEDGER_MATCH",
            "execution_disposition": disposition,
            "authoritative_effect_id": effect_id,
            "gateway_instance_id": payload.get("gateway_instance_id"),
            "gateway_result_time_ms": payload.get("gateway_result_time_ms"),
            "tool_content": copy.deepcopy(payload.get("tool_content")),
            "tool_content_trust_class": "UNTRUSTED_TOOL_RESULT_CONTENT",
        }


class SignedResultLoopbackClient:
    """HTTP client for the Pilot 5 signed-result gateway process."""

    def __init__(self, base_url: str, *, timeout_s: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = float(timeout_s)

    def execute(
        self,
        *,
        permit: Mapping[str, Any] | None,
        worker_id: str,
        worker_key_thumbprint: str,
        effect: Mapping[str, Any],
        idempotency_key: str,
        simulated_tool_content: Any = None,
        fault_mode: str | None = None,
    ) -> dict[str, Any]:
        body = {
            "permit": permit,
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect": dict(effect),
            "idempotency_key": idempotency_key,
            "simulated_tool_content": simulated_tool_content,
        }
        data = _canonical(body)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if fault_mode:
            headers["X-EXP-O-Test-Fault"] = fault_mode
        req = urlrequest.Request(self.base_url + "/execute", data=data, headers=headers, method="POST")
        try:
            with urlrequest.urlopen(req, timeout=self.timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
                payload["transport_complete"] = True
                payload["transport"] = "loopback-http"
                return payload
        except urlerror.HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
            except Exception:
                payload = {"decision": "HTTP_ERROR", "reason": f"HTTP_{exc.code}"}
            payload["transport_complete"] = True
            payload["transport"] = "loopback-http"
            return payload
        except (urlerror.URLError, ConnectionError, TimeoutError, OSError) as exc:
            return {
                "transport_complete": False,
                "transport": "loopback-http",
                "decision": "TRANSPORT_OUTCOME_UNKNOWN",
                "result_envelope": None,
                "error_class": type(exc).__name__,
            }


def sign_result_for_test(payload: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    """Test-only helper for constructing valid-signature wrong-lineage/ledger cases."""
    return _sign(dict(payload), key)
