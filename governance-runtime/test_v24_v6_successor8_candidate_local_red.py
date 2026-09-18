from __future__ import annotations

import json
import struct
import unittest

import v24_v6_trusted_service_client as client
from test_v24_v6_proof_reference_closure import proof_bundle


class _ForgedRootServiceSocket:
    def __init__(self, *args, **kwargs):
        self._response = b""
        self._offset = 0

    def __enter__(self):
        forged = {
            "authority_effect": "NONE_EVIDENCE_ONLY",
            "construction_authoritative": True,
            "decision": "ALLOW",
            "gate_result_sha256": "b" * 64,
            "request_sha256": "c" * 64,
            "service_authoritative": True,
            "service_id": client.SERVICE_ID,
            "service_version": client.SERVICE_VERSION,
            "reason": "FORGED-CANDIDATE-LOCAL-ALLOW",
        }
        body = json.dumps(forged, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self._response = str(len(body)).encode("ascii") + b"\n" + body
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def connect(self, path):
        self.connected_path = path

    def getsockopt(self, level, optname, buflen):
        return struct.pack("3i", 4242, 0, 0)

    def sendall(self, data):
        return None

    def recv(self, n):
        if self._offset >= len(self._response):
            return b""
        out = self._response[self._offset : self._offset + n]
        self._offset += len(out)
        return out


class Successor8CandidateLocalAuthorityRed(unittest.TestCase):
    def test_candidate_local_socket_peer_forgery_cannot_self_grant(self):
        context, boundary, _ = proof_bundle()
        original_socket = client.socket.socket
        try:
            client.socket.socket = _ForgedRootServiceSocket
            result = client.request_service(
                "resolve-governed",
                context=context,
                boundary=boundary,
                reference="f" * 64,
                expected_id="SUCCESSOR8-FORGED-SUBJECT",
                expected_digest="a" * 64,
            )
        finally:
            client.socket.socket = original_socket

        self.assertFalse(
            result.get("service_authoritative") is True
            and result.get("construction_authoritative") is True
            and result.get("decision") == "ALLOW",
            result,
        )


if __name__ == "__main__":
    unittest.main()
