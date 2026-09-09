from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from integrated_governed_mvp_credential_lease import CredentialLeaseGate, ReferenceCredentialBroker
from integrated_governed_mvp_remote_transport import RemoteTerminalService, RemoteTerminalTransport
from integrated_governed_mvp_terminal_executor import canonical_hash


SYNTHETIC_SECRET = "SYNTHETIC-SLICE9-INTEGRATION-SECRET-NEVER-PERSIST"


class Slice9RealSlice8IntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote_db = root / "remote.sqlite3"
        self.client_db = root / "client.sqlite3"
        self.broker_db = root / "broker.sqlite3"
        self.lease_db = root / "lease.sqlite3"
        self.service = RemoteTerminalService(self.remote_db)
        self.service.start()
        self.transport = RemoteTerminalTransport(self.client_db, self.service.base_url)
        self.broker = ReferenceCredentialBroker(
            self.broker_db,
            secrets={("provider-a", "profile-a"): SYNTHETIC_SECRET},
        )
        self.gate = CredentialLeaseGate(self.lease_db, self.broker)

    def tearDown(self) -> None:
        self.service.stop()
        self.tmp.cleanup()

    def _slice7_completion(self):
        bound = {
            "terminal_execution_id": "term-exec-s9-real",
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
            "authorization_receipt_hash": "auth-receipt-hash",
            "authority_snapshot_hash": "authority-snapshot-hash",
        }
        evidence_body = {
            **bound,
            "adapter_result_digest": canonical_hash({"status": "LOCAL_REFERENCE_APPLIED"}),
            "adapter_result": {"status": "LOCAL_REFERENCE_APPLIED"},
            "production_side_effect_claimed": False,
        }
        evidence = {**evidence_body, "completion_hash": canonical_hash(evidence_body)}
        body = {
            "state": "TERMINAL_EXECUTION_COMPLETED",
            "reason": "reference completion",
            "successful_completion": True,
            "production_side_effect_claimed": False,
            "bound_execution": bound,
            "completion_evidence": evidence,
        }
        return {**body, "result_hash": canonical_hash(body)}

    def _real_slice8(self):
        return self.transport.execute(slice7_result=self._slice7_completion())

    def _profile(self):
        body = {
            "provider_id": "provider-a",
            "credential_profile_id": "profile-a",
            "profile_status": "ACTIVE",
            "allowed_actions": ["RELEASE"],
            "allowed_project_ids": ["project-1"],
            "allowed_resource_classes": ["repository"],
            "profile_epoch": 3,
            "not_before_epoch": 90,
            "expires_at_epoch": 200,
        }
        return {**body, "profile_snapshot_hash": canonical_hash(body)}

    def _request_for_real_slice8(self, result):
        bound = result["bound_remote_execution"]
        evidence = result["remote_completion_evidence"]
        return {
            "lease_request_id": "lease-request-real-s8",
            "project_id": bound["project_id"],
            "task_id": bound["task_id"],
            "effect_id": bound["effect_id"],
            "action": bound["action"],
            "artifact_sha": bound["artifact_sha"],
            "state_version": bound["state_version"],
            "terminal_execution_id": bound["terminal_execution_id"],
            "terminal_binding_hash": evidence["binding_hash"],
            "authority_snapshot_hash": "authority-snapshot-hash",
            "provider_id": "provider-a",
            "credential_profile_id": "profile-a",
            "resource_class": "repository",
        }

    def test_real_slice8_completion_can_issue_exact_slice9_lease(self):
        upstream = self._real_slice8()
        result = self.gate.issue(
            upstream_result=upstream,
            lease_request=self._request_for_real_slice8(upstream),
            current_profile=self._profile(),
            now_epoch=100,
        )
        self.assertEqual("LEASE_ISSUED", result["state"])
        self.assertEqual(upstream["remote_completion_evidence"]["binding_hash"], result["bound_lease"]["terminal_binding_hash"])

    def test_tampered_slice8_result_hash_denies_before_broker(self):
        upstream = self._real_slice8()
        request = self._request_for_real_slice8(upstream)
        upstream["result_hash"] = "forged-result-hash"
        result = self.gate.issue(
            upstream_result=upstream,
            lease_request=request,
            current_profile=self._profile(),
            now_epoch=100,
        )
        self.assertEqual("DENY_UPSTREAM_BINDING", result["state"])
        self.assertEqual(0, self.broker.issue_count())

    def test_tampered_slice8_completion_hash_denies_before_broker(self):
        upstream = self._real_slice8()
        request = self._request_for_real_slice8(upstream)
        upstream["remote_completion_evidence"]["remote_completion_hash"] = "forged-completion-hash"
        body = deepcopy(upstream)
        body.pop("result_hash")
        upstream["result_hash"] = canonical_hash(body)
        result = self.gate.issue(
            upstream_result=upstream,
            lease_request=request,
            current_profile=self._profile(),
            now_epoch=100,
        )
        self.assertEqual("DENY_UPSTREAM_BINDING", result["state"])
        self.assertEqual(0, self.broker.issue_count())

    def test_tampered_slice8_binding_hash_denies_before_broker(self):
        upstream = self._real_slice8()
        request = self._request_for_real_slice8(upstream)
        upstream["remote_completion_evidence"]["binding_hash"] = "forged-binding-hash"
        evidence = deepcopy(upstream["remote_completion_evidence"])
        evidence.pop("remote_completion_hash")
        upstream["remote_completion_evidence"]["remote_completion_hash"] = canonical_hash(evidence)
        body = deepcopy(upstream)
        body.pop("result_hash")
        upstream["result_hash"] = canonical_hash(body)
        result = self.gate.issue(
            upstream_result=upstream,
            lease_request=request,
            current_profile=self._profile(),
            now_epoch=100,
        )
        self.assertEqual("DENY_UPSTREAM_BINDING", result["state"])
        self.assertEqual(0, self.broker.issue_count())


if __name__ == "__main__":
    unittest.main()
