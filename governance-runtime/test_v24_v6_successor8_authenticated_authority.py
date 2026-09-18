from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

import v24_v6_trusted_service_client as client
from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle

TRUSTED_SERVICE = Path("/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service")


class Successor8AuthenticatedAuthorityTests(unittest.TestCase):
    def test_genuine_client_result_is_diagnostic_only(self):
        context, boundary, refs = proof_bundle()
        result = client.request_service(
            "resolve-governed",
            context=context,
            boundary=boundary,
            reference=refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        self.assertEqual(result["decision"], "ALLOW", result)
        self.assertTrue(result["diagnostic_only"])
        self.assertFalse(result["service_authoritative"])
        self.assertFalse(result["construction_authoritative"])
        self.assertEqual(len(result["trusted_record_id"]), 64)
        self.assertEqual(
            result["request_sha256"],
            client.request_binding_digest(
                "resolve-governed",
                context=context,
                boundary=boundary,
                reference=refs["root"],
                expected_id="ROOT-VERIFIER",
                expected_digest=ROOT_CONTENT,
            ),
        )

    def test_candidate_cannot_consume_trusted_authority_record(self):
        self.assertNotEqual(os.geteuid(), 0)
        context, boundary, refs = proof_bundle()
        result = client.request_service(
            "resolve-governed",
            context=context,
            boundary=boundary,
            reference=refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        proc = subprocess.run(
            [
                str(TRUSTED_SERVICE),
                "--consume-record",
                result["trusted_record_id"],
                result["request_sha256"],
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout.strip())
        self.assertFalse(payload["construction_authoritative"])
        self.assertEqual(payload["decision"], "DENY")
        self.assertIn(
            payload["reason"],
            {"ROOT_CONSUMER_REQUIRED", "DIRECT_CONSUMER_DEAUTHORIZED"},
        )

    def test_request_digest_changes_on_reference_rebind(self):
        context, boundary, refs = proof_bundle()
        base = client.request_binding_digest(
            "resolve-governed",
            context=context,
            boundary=boundary,
            reference=refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        rebound = client.request_binding_digest(
            "resolve-governed",
            context=context,
            boundary=boundary,
            reference="f" * 64,
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        self.assertNotEqual(base, rebound)

    def test_fabricated_record_id_has_no_candidate_authority(self):
        proc = subprocess.run(
            [
                str(TRUSTED_SERVICE),
                "--consume-record",
                "a" * 64,
                "b" * 64,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout.strip())
        self.assertFalse(payload["construction_authoritative"])


if __name__ == "__main__":
    unittest.main()
