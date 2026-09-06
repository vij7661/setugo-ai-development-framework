"""Separate-process signed-result MCP gateway for EXP-O Pilot 5."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import uuid

from runtime_process_exp_o import FileTrustedClock
from runtime_slice_exp_o import McpGateway, _digest, _effect_binding, _sign, _verify


MAX_BODY_BYTES = 1_000_000
RESULT_SCHEMA_VERSION = "exp-o-pilot5-result-v1"
RESULT_KEY_ID = "exp-o-pilot5-result-key-v1"


def _json_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _result_payload(
    *,
    permit_payload,
    worker_id: str,
    worker_key_thumbprint: str,
    effect,
    idempotency_key: str,
    gateway_result,
    gateway_instance_id: str,
    gateway_result_time_ms: int,
    tool_content,
):
    result = gateway_result.get("result") or {}
    return {
        "result_schema_version": RESULT_SCHEMA_VERSION,
        "result_key_id": RESULT_KEY_ID,
        "capability_id": permit_payload.get("capability_id"),
        "permit_id": permit_payload.get("permit_id"),
        "worker_id": worker_id,
        "worker_key_thumbprint": worker_key_thumbprint,
        "authority_epoch": permit_payload.get("authority_epoch"),
        "effect_contract_id": permit_payload.get("effect_contract_id"),
        "effect_digest": _digest(_effect_binding(effect, idempotency_key=idempotency_key)),
        "idempotency_key": idempotency_key,
        "authoritative_effect_id": result.get("effect_id"),
        "execution_disposition": gateway_result.get("decision"),
        "gateway_instance_id": gateway_instance_id,
        "gateway_result_time_ms": gateway_result_time_ms,
        "tool_content": tool_content,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--ready-file", required=True)
    parser.add_argument("--clock-file", required=True)
    parser.add_argument("--enable-test-faults", action="store_true")
    args = parser.parse_args()

    permit_hex = os.environ.get("EXP_O_PERMIT_KEY_HEX", "")
    result_hex = os.environ.get("EXP_O_RESULT_KEY_HEX", "")
    if not permit_hex or not result_hex:
        raise SystemExit("EXP_O_PERMIT_KEY_HEX and EXP_O_RESULT_KEY_HEX are required")
    try:
        permit_key = bytes.fromhex(permit_hex)
        result_key = bytes.fromhex(result_hex)
    except ValueError as exc:
        raise SystemExit("pilot keys must be valid hex") from exc
    if not permit_key or not result_key or permit_key == result_key:
        raise SystemExit("non-empty distinct permit and result keys are required")

    clock = FileTrustedClock(args.clock_file)
    gateway = McpGateway(permit_key, args.db)
    instance_id = f"result-gateway-{uuid.uuid4().hex}"

    class Handler(BaseHTTPRequestHandler):
        server_version = "ExpOPilot5SignedResultGateway/1"

        def log_message(self, format, *values):
            return

        def _send(self, status: int, payload) -> None:
            data = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            self.wfile.flush()

        def do_GET(self) -> None:
            if self.path != "/health":
                self._send(404, {"state": "NOT_FOUND"})
                return
            try:
                now_ms = int(clock())
            except Exception as exc:
                self._send(503, {"state": "CLOCK_UNAVAILABLE", "error_class": type(exc).__name__})
                return
            self._send(
                200,
                {
                    "state": "READY",
                    "gateway_instance_id": instance_id,
                    "gateway_result_key_id": RESULT_KEY_ID,
                    "gateway_time_ms": now_ms,
                    "effect_count": gateway.effect_count(),
                    "transport": "loopback-http",
                },
            )

        def do_POST(self) -> None:
            if self.path != "/execute":
                self._send(404, {"decision": "DENY", "reason": "NOT_FOUND"})
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send(400, {"decision": "DENY", "reason": "INVALID_CONTENT_LENGTH"})
                return
            if content_length <= 0 or content_length > MAX_BODY_BYTES:
                self._send(400, {"decision": "DENY", "reason": "INVALID_BODY_SIZE"})
                return
            try:
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            except Exception:
                self._send(400, {"decision": "DENY", "reason": "INVALID_JSON"})
                return
            if not isinstance(body, dict):
                self._send(400, {"decision": "DENY", "reason": "INVALID_REQUEST_OBJECT"})
                return

            permit = body.get("permit")
            if not isinstance(permit, dict) or not _verify(permit, permit_key):
                result = gateway.execute(
                    permit=permit if isinstance(permit, dict) else None,
                    worker_id=str(body.get("worker_id", "")),
                    worker_key_thumbprint=str(body.get("worker_key_thumbprint", "")),
                    effect=body.get("effect") if isinstance(body.get("effect"), dict) else {},
                    idempotency_key=str(body.get("idempotency_key", "")),
                    now_ms=int(clock()),
                )
                self._send(200, {"gateway_decision": result, "result_envelope": None, "gateway_instance_id": instance_id})
                return

            permit_payload = dict(permit["payload"])
            worker_id = str(body.get("worker_id", ""))
            worker_key_thumbprint = str(body.get("worker_key_thumbprint", ""))
            effect = body.get("effect") if isinstance(body.get("effect"), dict) else {}
            idempotency_key = str(body.get("idempotency_key", ""))
            tool_content = body.get("simulated_tool_content")
            trusted_now_ms = int(clock())
            fault = self.headers.get("X-EXP-O-Test-Fault", "") if args.enable_test_faults else ""

            if fault == "SIGNED_SUCCESS_WITHOUT_LEDGER":
                fake_gateway_result = {
                    "authorized": True,
                    "decision": "EXECUTED",
                    "executed": True,
                    "result": {"effect_id": "forged-no-ledger-effect", "status": "EXECUTED"},
                }
                payload = _result_payload(
                    permit_payload=permit_payload,
                    worker_id=worker_id,
                    worker_key_thumbprint=worker_key_thumbprint,
                    effect=effect,
                    idempotency_key=idempotency_key,
                    gateway_result=fake_gateway_result,
                    gateway_instance_id=instance_id,
                    gateway_result_time_ms=trusted_now_ms,
                    tool_content=tool_content,
                )
                self._send(200, {"gateway_decision": fake_gateway_result, "result_envelope": _sign(payload, result_key), "gateway_instance_id": instance_id})
                return

            gateway_result = gateway.execute(
                permit=permit,
                worker_id=worker_id,
                worker_key_thumbprint=worker_key_thumbprint,
                effect=effect,
                idempotency_key=idempotency_key,
                now_ms=trusted_now_ms,
            )
            if gateway_result.get("authorized") is not True or gateway_result.get("decision") not in {"EXECUTED", "IDEMPOTENT_REPLAY"}:
                self._send(200, {"gateway_decision": gateway_result, "result_envelope": None, "gateway_instance_id": instance_id})
                return

            payload = _result_payload(
                permit_payload=permit_payload,
                worker_id=worker_id,
                worker_key_thumbprint=worker_key_thumbprint,
                effect=effect,
                idempotency_key=idempotency_key,
                gateway_result=gateway_result,
                gateway_instance_id=instance_id,
                gateway_result_time_ms=trusted_now_ms,
                tool_content=tool_content,
            )
            envelope = _sign(payload, result_key)

            if fault == "UNSIGNED_RESULT":
                envelope = {"payload": payload}
            elif fault == "TRUNCATED_RESULT":
                truncated = dict(payload)
                truncated.pop("authoritative_effect_id", None)
                envelope = {"payload": truncated, "signature": envelope["signature"]}
            elif fault == "TAMPER_AFTER_SIGN":
                envelope["payload"]["execution_disposition"] = "EXECUTED_AND_RELEASE_APPROVED"
            elif fault == "SIGNED_LEDGER_EFFECT_ID_MISMATCH":
                wrong = dict(payload)
                wrong["authoritative_effect_id"] = "wrong-effect-id"
                envelope = _sign(wrong, result_key)
            elif fault == "SIGNED_UNKNOWN_KEY_ID":
                unknown = dict(payload)
                unknown["result_key_id"] = "unknown-result-key"
                envelope = _sign(unknown, result_key)

            self._send(
                200,
                {
                    "gateway_decision": gateway_result,
                    "result_envelope": envelope,
                    "gateway_instance_id": instance_id,
                    "gateway_result_time_ms": trusted_now_ms,
                },
            )

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    port = int(server.server_address[1])
    ready_path = Path(args.ready_file)
    ready_path.parent.mkdir(parents=True, exist_ok=True)
    temp = ready_path.with_suffix(ready_path.suffix + ".tmp")
    temp.write_text(
        json.dumps(
            {
                "state": "READY",
                "pid": os.getpid(),
                "port": port,
                "gateway_instance_id": instance_id,
                "result_key_id": RESULT_KEY_ID,
                "transport": "loopback-http",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    temp.replace(ready_path)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
