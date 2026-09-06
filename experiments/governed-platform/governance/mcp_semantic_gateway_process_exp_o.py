"""EXP-O Pilot 10 separate-process semantic-bound MCP gateway.

Loopback HTTP, HMAC test keys and SQLite are deliberate pilot mechanisms. The
process never receives the semantic-verifier signing key or AuthorityKernel
capability-issuing key.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import sys
import uuid

from runtime_process_exp_o import FileTrustedClock
from runtime_slice_exp_o import McpGateway
from semantic_permit_registry_exp_o import DurableSemanticPermitRegistry, ProcessSemanticBoundGateway


MAX_BODY_BYTES = 1_000_000
FORBIDDEN_KEY_VARS = (
    "EXP_O_SEMANTIC_VERIFIER_SIGNING_KEY_HEX",
    "EXP_O_AUTHORITY_KERNEL_SIGNING_KEY_HEX",
)


def _required_key(name: str) -> bytes:
    raw = os.environ.get(name, "")
    if not raw:
        raise SystemExit(f"{name} is required")
    try:
        value = bytes.fromhex(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be valid hex") from exc
    if not value:
        raise SystemExit(f"{name} must not be empty")
    return value


def _json_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--effects-db", required=True)
    parser.add_argument("--registry-db", required=True)
    parser.add_argument("--ready-file", required=True)
    parser.add_argument("--clock-file", required=True)
    parser.add_argument("--enable-test-faults", action="store_true")
    args = parser.parse_args()

    present_forbidden = [name for name in FORBIDDEN_KEY_VARS if os.environ.get(name)]
    if present_forbidden:
        raise SystemExit("forbidden authority/signing key present in semantic gateway process")

    outer_key = _required_key("EXP_O_OUTER_PERMIT_KEY_HEX")
    registry_key = _required_key("EXP_O_SEMANTIC_REGISTRY_KEY_HEX")
    inner_key = _required_key("EXP_O_INNER_PERMIT_KEY_HEX")

    clock = FileTrustedClock(args.clock_file)
    registry = DurableSemanticPermitRegistry(args.registry_db, registry_key)
    raw_gateway = McpGateway(inner_key, args.effects_db)
    gateway = ProcessSemanticBoundGateway(
        raw_gateway,
        outer_permit_verification_key=outer_key,
        registry=registry,
    )
    instance_id = f"semantic-gateway-{uuid.uuid4().hex}"

    class Handler(BaseHTTPRequestHandler):
        server_version = "ExpOPilot10SemanticGateway/1"

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
                    "pid": os.getpid(),
                    "gateway_time_ms": now_ms,
                    "effect_count": gateway.effect_count(),
                    "transport": "loopback-http",
                    "loaded_key_roles": [
                        "OUTER_PERMIT_VERIFICATION_HMAC_PILOT_KEY",
                        "SEMANTIC_REGISTRY_INTEGRITY_HMAC_PILOT_KEY",
                        "INNER_LEP_PERMIT_VERIFICATION_HMAC_PILOT_KEY",
                    ],
                    "semantic_verifier_signing_key_present": False,
                    "authority_kernel_signing_key_present": False,
                },
            )

        def do_POST(self) -> None:
            if self.path != "/execute":
                self._send(404, {"authorized": False, "decision": "DENY", "reason": "NOT_FOUND"})
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send(400, {"authorized": False, "decision": "DENY", "reason": "INVALID_CONTENT_LENGTH"})
                return
            if content_length <= 0 or content_length > MAX_BODY_BYTES:
                self._send(400, {"authorized": False, "decision": "DENY", "reason": "INVALID_BODY_SIZE"})
                return
            try:
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            except Exception:
                self._send(400, {"authorized": False, "decision": "DENY", "reason": "INVALID_JSON"})
                return
            if not isinstance(body, dict):
                self._send(400, {"authorized": False, "decision": "DENY", "reason": "INVALID_REQUEST_OBJECT"})
                return

            # Trusted time is process configuration, never a caller field.
            try:
                trusted_now_ms = int(clock())
            except Exception as exc:
                self._send(503, {"authorized": False, "decision": "DENY", "reason": "TRUSTED_CLOCK_UNAVAILABLE", "error_class": type(exc).__name__})
                return

            fault = self.headers.get("X-EXP-O-Test-Fault", "")

            def after_inflight() -> None:
                if args.enable_test_faults and fault == "CRASH_AFTER_REGISTRY_IN_FLIGHT":
                    # The registry transition is already durably committed, but
                    # no MCP effect has yet been attempted.
                    os._exit(86)

            result = gateway.execute(
                permit=body.get("permit"),
                candidate_payload=body.get("candidate_payload") if isinstance(body.get("candidate_payload"), dict) else {},
                worker_id=str(body.get("worker_id", "")),
                worker_key_thumbprint=str(body.get("worker_key_thumbprint", "")),
                effect=body.get("effect") if isinstance(body.get("effect"), dict) else {},
                idempotency_key=str(body.get("idempotency_key", "")),
                now_ms=trusted_now_ms,
                after_inflight_hook=after_inflight,
            )
            result["gateway_instance_id"] = instance_id
            result["gateway_time_ms"] = trusted_now_ms
            result["time_source"] = "SEMANTIC_GATEWAY_PROCESS_TRUSTED_CLOCK"
            result["transport"] = "loopback-http"
            self._send(200, result)

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
                "transport": "loopback-http",
                "semantic_verifier_signing_key_present": False,
                "authority_kernel_signing_key_present": False,
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
