"""Candidate-side transport for the Successor-7 trusted authority service.

This module never grants authority. It speaks to one fixed root-owned Unix
socket, verifies the live server peer is UID 0, and returns the service response.
"""
from __future__ import annotations

import json
import socket
import struct
from typing import Any

SERVICE_SOCKET = "/run/v24-v6-authority/service.sock"
SERVICE_ID = "V24-V6-TRUSTED-AUTHORITY-SERVICE"
SERVICE_VERSION = "1"


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def request_service(
    operation: str,
    *,
    context: dict[str, Any],
    boundary: dict[str, Any],
    reference: str,
    expected_id: str,
    expected_digest: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context_bytes = _canonical_bytes(context)
    boundary_bytes = _canonical_bytes(boundary)
    payload_bytes = b"" if payload is None else _canonical_bytes(payload)

    header = (
        "V24-V6-S7/1\n"
        f"{operation}\n"
        f"{reference}\n"
        f"{expected_id}\n"
        f"{expected_digest}\n"
        f"{len(context_bytes)}\n"
        f"{len(boundary_bytes)}\n"
        f"{len(payload_bytes)}\n"
    ).encode("ascii")

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SERVICE_SOCKET)
        creds = s.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
        _pid, uid, _gid = struct.unpack("3i", creds)
        if uid != 0:
            raise RuntimeError("trusted authority service peer is not root")

        s.sendall(header)
        s.sendall(context_bytes)
        s.sendall(boundary_bytes)
        if payload_bytes:
            s.sendall(payload_bytes)

        size_line = bytearray()
        while True:
            b = s.recv(1)
            if not b:
                raise RuntimeError("trusted authority service closed before response")
            if b == b"\n":
                break
            if len(size_line) >= 32:
                raise RuntimeError("trusted authority service response header too long")
            size_line.extend(b)
        response_len = int(size_line.decode("ascii"))
        if response_len <= 0 or response_len > 1024 * 1024:
            raise RuntimeError("trusted authority service response size invalid")

        chunks: list[bytes] = []
        remaining = response_len
        while remaining:
            chunk = s.recv(min(65536, remaining))
            if not chunk:
                raise RuntimeError("trusted authority service response truncated")
            chunks.append(chunk)
            remaining -= len(chunk)

    result = json.loads(b"".join(chunks))
    if result.get("service_id") != SERVICE_ID:
        raise RuntimeError("trusted authority service identity mismatch")
    if result.get("service_version") != SERVICE_VERSION:
        raise RuntimeError("trusted authority service version mismatch")
    if result.get("service_authoritative") is not True:
        raise RuntimeError("trusted authority service response is not authoritative")
    return result
