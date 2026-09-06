from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from process_network_quorum_hardening_exp_o import HardenedProcessQuorumClusterHarness


class ExpOPilot14CoverageHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.h = HardenedProcessQuorumClusterHarness(
            Path(self.temp.name), cluster_key=b"exp-o-p14-auth-key"
        )
        self.h.start_all()
        self.addCleanup(self.h.stop_all)
        self.r1 = self.h.client("r1")
        self.r2 = self.h.client("r2")
        self.r3 = self.h.client("r3")
        self.permit_id = "permit-a"
        self.bindings = {
            "semantic_payload_digest": "semantic-a",
            "effect_digest": "effect-a",
            "idempotency_key": "intent-a",
            "worker_id": "worker-a",
            "worker_key_thumbprint": "worker-key-a",
            "effect_contract_id": "contract-v1",
            "base_sha": "base-v1",
        }

    def _bootstrap(self) -> dict:
        elected = self.r1.post("/client/elect", term=1)
        self.assertTrue(elected["authorized"], elected)
        issued = self.r1.post(
            "/client/issue", permit_id=self.permit_id, bindings=self.bindings
        )
        self.assertTrue(issued["authorized"], issued)
        acquired = self.r1.post(
            "/client/acquire",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            bindings=self.bindings,
        )
        self.assertTrue(acquired["authorized"], acquired)
        return acquired

    def test_h1_forged_positive_ack_is_rejected_by_exact_quorum_response_path(self):
        """Post-generation response forgery cannot add the peer to the voter set."""
        self._bootstrap()
        state = self.r2.inspect(self.permit_id)
        before_r2 = copy.deepcopy(state)
        before_effects = state["effect_count"]

        # Obtain a genuine positive signed READ_CONFIRM acknowledgement addressed
        # to r2. The peer generates it through the normal authenticated HTTP and
        # durable inbound-message path.
        genuine_probe = self.r2.post(
            "/test/probe-peer",
            peer_id="r3",
            message_type="READ_CONFIRM",
            term=state["current_term"],
            payload={
                "expected_term": state["current_term"],
                "expected_leader_id": state["leader_id"],
                "expected_commit_index": state["commit_index"],
                "permit_id": self.permit_id,
                "expected_record_digest": state["record_digest"],
            },
        )
        self.assertEqual(len(genuine_probe["responses"]), 1)
        genuine = genuine_probe["responses"][0]
        self.assertTrue(genuine["core"]["payload"]["confirmed"])
        self.assertEqual(genuine["core"]["sender_id"], "r3")
        self.assertEqual(genuine["core"]["receiver_id"], "r2")

        # Positive control: the unchanged authenticated acknowledgement is
        # accepted by the exact production voter-collection helper.
        accepted = self.r2.post(
            "/test/collect-responses",
            responses=[genuine],
            expected_type="READ_CONFIRM",
            expected_term=state["current_term"],
            positive_field="confirmed",
        )
        self.assertTrue(accepted["quorum_confirmed"])
        self.assertEqual(accepted["voters"], ["r2", "r3"])

        # H1 attack: corrupt the acknowledgement only after peer generation.
        forged = copy.deepcopy(genuine)
        forged["auth_tag"] = "0" * 64
        rejected = self.r2.post(
            "/test/collect-responses",
            responses=[forged],
            expected_type="READ_CONFIRM",
            expected_term=state["current_term"],
            positive_field="confirmed",
        )
        self.assertFalse(rejected["quorum_confirmed"])
        self.assertEqual(rejected["voters"], ["r2"])

        after_r2 = self.r2.inspect(self.permit_id)
        self.assertEqual(after_r2["current_term"], before_r2["current_term"])
        self.assertEqual(after_r2["commit_index"], before_r2["commit_index"])
        self.assertEqual(after_r2["record_digest"], before_r2["record_digest"])
        self.assertEqual(after_r2["effect_count"], before_effects)

    def test_h2_generated_valid_ack_released_after_deny_cannot_retroactively_authorize(self):
        """A peer processes the request, but its held response cannot reopen a deny."""
        self._bootstrap()
        before = self.r1.inspect(self.permit_id)
        r2_ledger_before = self.r2.inspect()["message_ledger_count"]

        self.h.set_faults(
            {
                "r1->r2:READ_CONFIRM": "DELAY_RESPONSE_UNTIL_RELEASE",
                "r1->r3:READ_CONFIRM": "DROP",
            }
        )
        denied = self.r1.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
        )
        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason"], "USE_TIME_QUORUM_REQUIRED")
        self.assertEqual(denied["voters"], ["r1"])

        # Unlike the original DELAY_UNTIL_RELEASE schedule, the peer has already
        # received, authenticated, durably ledgered, and answered the request.
        r2_ledger_after = self.r2.inspect()["message_ledger_count"]
        self.assertEqual(r2_ledger_after, r2_ledger_before + 1)

        after_deny = self.r1.inspect(self.permit_id)
        self.assertEqual(after_deny["effect_count"], 0)
        self.assertEqual(after_deny["current_term"], before["current_term"])
        self.assertEqual(after_deny["commit_index"], before["commit_index"])
        self.assertEqual(after_deny["record_digest"], before["record_digest"])
        self.assertEqual(after_deny["record"]["state"], "IN_FLIGHT")
        self.assertEqual(after_deny["record"]["lease_owner_gateway_instance_id"], "gateway-a")
        self.assertEqual(after_deny["record"]["lease_epoch"], 1)

        released = self.r1.post("/test/release-delayed")
        self.assertEqual(released["released"], 1)
        self.assertEqual(released["outcomes"], [])
        self.assertEqual(len(released["response_outcomes"]), 1)
        response = released["response_outcomes"][0]["response_envelope"]
        self.assertTrue(response["core"]["payload"]["confirmed"])
        self.assertEqual(response["core"]["sender_id"], "r2")
        self.assertEqual(response["core"]["receiver_id"], "r1")

        # Show the surfaced response is genuinely acceptable to the same
        # production response verifier/voter helper if considered in a new
        # collection. This does not resume the completed denied operation.
        valid_later = self.r1.post(
            "/test/collect-responses",
            responses=[response],
            expected_type="READ_CONFIRM",
            expected_term=before["current_term"],
            positive_field="confirmed",
        )
        self.assertTrue(valid_later["quorum_confirmed"])
        self.assertEqual(valid_later["voters"], ["r1", "r2"])

        after_release = self.r1.inspect(self.permit_id)
        self.assertEqual(after_release["effect_count"], 0)
        self.assertEqual(after_release["current_term"], before["current_term"])
        self.assertEqual(after_release["commit_index"], before["commit_index"])
        self.assertEqual(after_release["record_digest"], before["record_digest"])
        self.assertEqual(after_release["record"]["state"], "IN_FLIGHT")
        self.assertEqual(after_release["record"]["lease_owner_gateway_instance_id"], "gateway-a")
        self.assertEqual(after_release["record"]["lease_epoch"], 1)


if __name__ == "__main__":
    unittest.main()
