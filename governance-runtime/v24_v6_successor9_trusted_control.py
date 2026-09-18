from __future__ import annotations

import json
import os
import socket
import struct
import sys
from pathlib import Path
from typing import Any

import v24_v6_decision_apply as decision_apply
import v24_v6_normative_clause_projection as normative_projection
from test_v24_v6_decision_apply import attach_proofs as attach_decision_proofs, bundle as decision_bundle
from test_v24_v6_normative_clause_projection import DISPOSITION_SET_ID, coverage_fixture
from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle

SERVICE_SOCKET = "/run/v24-v6-authority/service.sock"
SERVICE_ID = "V24-V6-TRUSTED-AUTHORITY-SERVICE"
SERVICE_VERSION = "3"
MAGIC = "V24-V6-S9-CONSUME/1"


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _recv_response(sock: socket.socket) -> dict[str, Any]:
    size_line = bytearray()
    while True:
        b = sock.recv(1)
        if not b:
            raise RuntimeError("trusted service closed before control response")
        if b == b"\n":
            break
        if len(size_line) >= 32:
            raise RuntimeError("trusted control response header too long")
        size_line.extend(b)
    size = int(size_line.decode("ascii"))
    if size <= 0 or size > 1024 * 1024:
        raise RuntimeError("trusted control response size invalid")
    body = bytearray()
    while len(body) < size:
        chunk = sock.recv(size - len(body))
        if not chunk:
            raise RuntimeError("trusted control response truncated")
        body.extend(chunk)
    result = json.loads(body)
    if result.get("service_id") not in {None, SERVICE_ID}:
        raise RuntimeError("trusted control service identity mismatch")
    if result.get("service_version") not in {None, SERVICE_VERSION}:
        raise RuntimeError("trusted control service version mismatch")
    return result


def _request(mode: str) -> dict[str, Any]:
    if mode in {"positive", "positive-wrong-operation"}:
        context, boundary, refs = proof_bundle()
        return {
            "operation": "resolve-governed",
            "context": context,
            "boundary": boundary,
            "reference": refs["root"],
            "expected_id": "ROOT-VERIFIER",
            "expected_digest": ROOT_CONTENT,
            "payload": None,
        }

    if mode in {"da1", "positive-wrong-payload"}:
        payload = decision_bundle()
        context, boundary = attach_decision_proofs(payload)
        source = payload["snapshot_source"]
        payload["decision"]["authorized_effect_path_id"] = "PATH-ATTACK"
        payload["material_effect_path"]["path_id"] = "PATH-ATTACK"
        payload["decision"]["decision_digest"] = decision_apply.canonical_decision_content_digest(
            payload["decision"]
        )
        return {
            "operation": "evaluate-decision-apply",
            "context": context,
            "boundary": boundary,
            "reference": source["qualification_digest"],
            "expected_id": source["mechanism_id"],
            "expected_digest": source["mechanism_content_digest"],
            "payload": payload,
        }

    if mode == "ncp1":
        payload, context, boundary, _ = coverage_fixture()
        descriptor = payload["catalog_descriptors"][0]
        descriptor["control_id"] = "CTRL-ATTACK"
        descriptor["control_binding_content_digest"] = (
            normative_projection.canonical_catalog_control_binding_digest(descriptor)
        )
        return {
            "operation": "validate-normative-coverage",
            "context": context,
            "boundary": boundary,
            "reference": payload["disposition_qualification_digest"],
            "expected_id": DISPOSITION_SET_ID,
            "expected_digest": payload["disposition_digest"],
            "payload": payload,
        }

    raise ValueError(f"unsupported mode: {mode}")


def consume(mode: str, diagnostic_path: Path) -> dict[str, Any]:
    if os.geteuid() != 0:
        raise PermissionError("trusted semantic consume client requires root")

    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    record_id = diagnostic["trusted_record_id"]
    request = _request(mode)

    if mode == "positive-wrong-operation":
        request["operation"] = "resolve-currentness"

    context_bytes = _canonical_bytes(request["context"])
    boundary_bytes = _canonical_bytes(request["boundary"])
    payload_bytes = (
        b"" if request["payload"] is None else _canonical_bytes(request["payload"])
    )

    header = (
        f"{MAGIC}\n"
        f"{record_id}\n"
        f"{request['operation']}\n"
        f"{request['reference']}\n"
        f"{request['expected_id']}\n"
        f"{request['expected_digest']}\n"
        f"{len(context_bytes)}\n"
        f"{len(boundary_bytes)}\n"
        f"{len(payload_bytes)}\n"
    ).encode("ascii")

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(SERVICE_SOCKET)
        creds = sock.getsockopt(
            socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")
        )
        _pid, uid, _gid = struct.unpack("3i", creds)
        if uid != 0:
            raise RuntimeError("trusted semantic consume peer is not root")
        sock.sendall(header)
        sock.sendall(context_bytes)
        sock.sendall(boundary_bytes)
        if payload_bytes:
            sock.sendall(payload_bytes)
        return _recv_response(sock)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: v24_v6_successor9_trusted_control.py "
            "positive|positive-wrong-operation|positive-wrong-payload|da1|ncp1 "
            "<diagnostic-json>"
        )
    result = consume(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("decision") == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
