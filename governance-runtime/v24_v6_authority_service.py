"""Successor-7 trusted authority service.

Construction-only local service. It is intended to be installed root-owned outside
candidate-writable paths and launched by the trusted bootstrap with a clean
environment. Candidate code communicates only over the fixed Unix-domain socket.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SERVICE_ID = "V24-V6-TRUSTED-AUTHORITY-SERVICE"
SERVICE_VERSION = "1"
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
TRUSTED_ROOT = Path("/opt/v24-v6-trusted-runtime")
GATE = TRUSTED_ROOT / ".gate-build" / "v24_v6_external_authority_gate"
RUN_ROOT = Path("/run/v24-v6-authority-service")
SOCKET_PATH = RUN_ROOT / "service.sock"
MAX_FRAME = 16 * 1024 * 1024
GATE_ID = "V24-V6-EXTERNAL-AUTHORITY-GATE"
GATE_VERSION = "1"

_RESOLVE_OPS = {"resolve-governed", "resolve-independence", "resolve-currentness"}
_DOWNSTREAM_OPS = {"evaluate-decision-apply", "validate-normative-coverage"}


def _recv_exact(conn: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = conn.recv(remaining)
        if not chunk:
            raise ValueError("truncated frame")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _recv_frame(conn: socket.socket) -> dict[str, Any]:
    raw_len = _recv_exact(conn, 8)
    size = struct.unpack(">Q", raw_len)[0]
    if size == 0 or size > MAX_FRAME:
        raise ValueError("frame size invalid")
    payload = json.loads(_recv_exact(conn, size).decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("request must be an object")
    return payload


def _send_frame(conn: socket.socket, payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    conn.sendall(struct.pack(">Q", len(raw)) + raw)


def _peer_credentials(conn: socket.socket) -> tuple[int, int, int]:
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    return struct.unpack("3i", raw)


def _write_json(directory: Path, name: str, value: Any) -> Path:
    path = directory / name
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o600)
    return path


def _deny(reason: str) -> dict[str, Any]:
    return {
        "authority_effect": AUTHORITY_EFFECT,
        "construction_authoritative": True,
        "decision": "DENY",
        "service_authoritative": True,
        "service_id": SERVICE_ID,
        "service_version": SERVICE_VERSION,
        "reason": reason,
    }


def _validate_exact_keys(request: dict[str, Any], expected: set[str]) -> None:
    if set(request) != expected:
        raise ValueError("request fields invalid")


def _invoke_gate(request: dict[str, Any]) -> dict[str, Any]:
    operation = request.get("operation")
    if operation in _RESOLVE_OPS:
        _validate_exact_keys(
            request,
            {
                "operation",
                "context",
                "boundary",
                "reference",
                "expected_id",
                "expected_digest",
            },
        )
    elif operation in _DOWNSTREAM_OPS:
        _validate_exact_keys(
            request,
            {
                "operation",
                "context",
                "boundary",
                "payload",
                "probe_reference",
                "probe_expected_id",
                "probe_expected_digest",
            },
        )
    else:
        return _deny("SERVICE_OPERATION_UNSUPPORTED")

    if not isinstance(request.get("context"), dict) or not isinstance(request.get("boundary"), dict):
        return _deny("SERVICE_INPUT_OBJECT_INVALID")

    env = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    with tempfile.TemporaryDirectory(prefix="request-", dir=RUN_ROOT) as td:
        directory = Path(td)
        os.chmod(directory, 0o700)
        context_path = _write_json(directory, "context.json", request["context"])
        boundary_path = _write_json(directory, "boundary.json", request["boundary"])

        if operation in _RESOLVE_OPS:
            args = [
                str(GATE),
                str(operation),
                str(context_path),
                str(boundary_path),
                str(request["reference"]),
                str(request["expected_id"]),
                str(request["expected_digest"]),
                GATE_ID,
                GATE_VERSION,
                "enforce",
            ]
        else:
            if not isinstance(request.get("payload"), dict):
                return _deny("SERVICE_PAYLOAD_OBJECT_INVALID")
            payload_path = _write_json(directory, "payload.json", request["payload"])
            args = [
                str(GATE),
                str(operation),
                str(context_path),
                str(boundary_path),
                str(payload_path),
                str(request["probe_reference"]),
                str(request["probe_expected_id"]),
                str(request["probe_expected_digest"]),
                GATE_ID,
                GATE_VERSION,
                "enforce",
            ]

        proc = subprocess.run(
            args,
            text=True,
            capture_output=True,
            check=False,
            env=env,
            cwd=TRUSTED_ROOT,
            timeout=15,
        )

    try:
        payload = json.loads(proc.stdout.strip())
    except Exception:
        return _deny("SERVICE_GATE_OUTPUT_MALFORMED")
    if not isinstance(payload, dict):
        return _deny("SERVICE_GATE_OUTPUT_INVALID")

    payload = dict(payload)
    payload["service_authoritative"] = True
    payload["service_id"] = SERVICE_ID
    payload["service_version"] = SERVICE_VERSION
    payload["service_gate_exit_code"] = proc.returncode

    if proc.returncode != 0:
        payload["decision"] = "DENY"
    if payload.get("gate_id") != GATE_ID or payload.get("gate_version") != GATE_VERSION:
        return _deny("SERVICE_GATE_IDENTITY_INVALID")
    if payload.get("construction_authoritative") is not True:
        return _deny("SERVICE_GATE_AUTHORITY_FLAG_INVALID")
    if payload.get("authority_effect") != AUTHORITY_EFFECT:
        return _deny("SERVICE_GATE_AUTHORITY_EFFECT_INVALID")
    if payload.get("decision") not in {"ALLOW", "DENY"}:
        return _deny("SERVICE_GATE_DECISION_INVALID")
    return payload


def serve(candidate_uid: int) -> int:
    if os.geteuid() != 0:
        raise SystemExit("trusted authority service must run as root")
    if candidate_uid <= 0:
        raise SystemExit("candidate uid must be non-root")

    RUN_ROOT.mkdir(mode=0o755, parents=True, exist_ok=True)
    os.chown(RUN_ROOT, 0, 0)
    os.chmod(RUN_ROOT, 0o755)

    try:
        SOCKET_PATH.unlink()
    except FileNotFoundError:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET_PATH))
    os.chown(SOCKET_PATH, 0, 0)
    os.chmod(SOCKET_PATH, 0o666)
    server.listen(16)

    while True:
        conn, _ = server.accept()
        with conn:
            try:
                _, uid, _ = _peer_credentials(conn)
                if uid != candidate_uid:
                    _send_frame(conn, _deny("SERVICE_PEER_UID_REJECTED"))
                    continue
                request = _recv_frame(conn)
                response = _invoke_gate(request)
            except Exception:
                response = _deny("SERVICE_REQUEST_FAILED")
            _send_frame(conn, response)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-uid", type=int, required=True)
    args = parser.parse_args()
    return serve(args.candidate_uid)


if __name__ == "__main__":
    raise SystemExit(main())
