"""Separate-process loopback MCP gateway for EXP-O Pilot 4.

This is test infrastructure, not a production MCP service. Security-sensitive
current time is read from the process-configured trusted clock, never the HTTP
request body.
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


MAX_BODY_BYTES = 1_000_000


def _json_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--ready-file", required=True)
    parser.add_argument("--clock-file", required=True)
    parser.add_argument("--enable-test-faults", action="store_true")
    args = parser.parse_args()

    key_hex = os.environ.get("EXP_O_PERMIT_KEY_HEX", "")
    if not key_hex:
        raise SystemExit("EXP_O_PERMIT_KEY_HEX is required")
    try:
        permit_key = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise SystemExit("EXP_O_PERMIT_KEY_HEX must be valid hex") from exc
    if not permit_key:
        raise SystemExit("permit key must not be empty")

    clock = FileTrustedClock(args.clock_file)
    gateway = McpGateway(permit_key, args.db)
    instance_id = f"gateway-{uuid.uuid4().hex}"

    class Handler(BaseHTTPRequestHandler):
        server_version = "ExpOPilot4Gateway/1"

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
                    "gateway_time_ms": now_ms,
                    "effect_count": gateway.effect_count(),
                    "transport": "loopback-http",
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

            # Intentionally ignore any current-time claims in body/untrusted_metadata.
            # Security time comes only from the process-configured trusted clock.
            try:
                trusted_now_ms = int(clock())
            except Exception as exc:
                self._send(
                    503,
                    {
                        "authorized": False,
                        "decision": "DENY",
                        "reason": "TRUSTED_CLOCK_UNAVAILABLE",
                        "error_class": type(exc).__name__,
                    },
                )
                return

            result = gateway.execute(
                permit=body.get("permit"),
                worker_id=str(body.get("worker_id", "")),
                worker_key_thumbprint=str(body.get("worker_key_thumbprint", "")),
                effect=body.get("effect") if isinstance(body.get("effect"), dict) else {},
                idempotency_key=str(body.get("idempotency_key", "")),
                now_ms=trusted_now_ms,
            )
            result["gateway_instance_id"] = instance_id
            result["gateway_time_ms"] = trusted_now_ms
            result["time_source"] = "GATEWAY_PROCESS_TRUSTED_CLOCK"

            fault = self.headers.get("X-EXP-O-Test-Fault", "")
            if (
                args.enable_test_faults
                and fault == "DROP_RESPONSE_AFTER_COMMIT"
                and result.get("decision") == "EXECUTED"
                and result.get("authorized") is True
            ):
                # The authoritative SQLite commit has already happened. Drop the
                # transport before a response is delivered so the client must
                # preserve UNKNOWN and reconcile by idempotency key.
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    self.connection.close()
                except OSError:
                    pass
                return

            self._send(200, result)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    port = int(server.server_address[1])
    ready_path = Path(args.ready_file)
    ready_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = ready_path.with_suffix(ready_path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(
            {
                "state": "READY",
                "pid": os.getpid(),
                "port": port,
                "gateway_instance_id": instance_id,
                "transport": "loopback-http",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    temp_path.replace(ready_path)

    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
