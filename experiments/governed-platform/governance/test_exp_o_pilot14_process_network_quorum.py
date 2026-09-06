from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import time
import unittest

from process_network_quorum_exp_o import ProcessQuorumClusterHarness, digest


class ExpOPilot14ProcessNetworkQuorumTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.h = ProcessQuorumClusterHarness(Path(self.temp.name), cluster_key=b"exp-o-p14-auth-key")
        self.infos = self.h.start_all()
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

    def _bootstrap(self):
        elected = self.r1.post("/client/elect", term=1)
        self.assertTrue(elected["authorized"], elected)
        issued = self.r1.post("/client/issue", permit_id=self.permit_id, bindings=self.bindings)
        self.assertTrue(issued["authorized"], issued)
        acquired = self.r1.post(
            "/client/acquire",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            bindings=self.bindings,
        )
        self.assertTrue(acquired["authorized"], acquired)
        return acquired

    def _failover_term2(self):
        acquired = self._bootstrap()
        self.h.set_faults({
            "r2->r1:VOTE": "DROP",
            "r2->r1:REPLICATE": "DROP",
        })
        elected = self.r2.post("/client/elect", term=2)
        self.assertTrue(elected["authorized"], elected)
        self.assertEqual(elected["voters"], ["r2", "r3"])
        return acquired

    def _takeover_b(self):
        acquired = self._failover_term2()
        self.h.set_clock(int(acquired["lease_expires_at_ms"]))
        takeover = self.r2.post(
            "/client/takeover",
            permit_id=self.permit_id,
            new_owner_id="gateway-b",
            bindings=self.bindings,
        )
        self.assertTrue(takeover["authorized"], takeover)
        self.assertEqual(takeover["lease_epoch"], 2)
        return acquired, takeover

    def test_p14_01_replica_processes_are_independent_and_durably_identified(self):
        pids = {self.infos[r]["pid"] for r in ("r1", "r2", "r3")}
        dbs = {self.infos[r]["db_path"] for r in ("r1", "r2", "r3")}
        ids = {self.infos[r]["replica_id"] for r in ("r1", "r2", "r3")}
        self.assertEqual(len(pids), 3)
        self.assertEqual(len(dbs), 3)
        self.assertEqual(ids, {"r1", "r2", "r3"})
        for rid in ("r1", "r2", "r3"):
            health = self.h.client(rid).health()
            self.assertEqual(health["pid"], self.infos[rid]["pid"])
            self.assertEqual(health["replica_id"], rid)

    def test_p14_02_two_authenticated_distinct_process_votes_elect_term_one_leader(self):
        self.h.set_faults({"r1->r2:VOTE": "DROP", "r1->r3:VOTE": "DROP"})
        denied = self.r1.post("/client/elect", term=1, candidate_self_vote_copies=5)
        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason"], "ELECTION_QUORUM_REQUIRED")
        self.assertEqual(denied["voters"], ["r1"])
        self.h.set_faults({"r1->r3:VOTE": "DROP"})
        elected = self.r1.post("/client/elect", term=1)
        self.assertTrue(elected["authorized"], elected)
        self.assertEqual(elected["voters"], ["r1", "r2"])

    def test_p14_03_forged_or_unauthenticated_peer_ack_cannot_satisfy_quorum(self):
        self.h.set_faults({
            "r1->r2:VOTE": "CORRUPT_AUTH",
            "r1->r3:VOTE": "DROP",
        })
        result = self.r1.post("/client/elect", term=1)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "ELECTION_QUORUM_REQUIRED")
        self.assertEqual(self.r1.inspect()["current_term"], 0)
        self.assertEqual(self.r2.inspect()["message_ledger_count"], 0)

    def test_p14_04_duplicate_delivery_cannot_manufacture_second_voter(self):
        self.h.set_faults({
            "r1->r2:VOTE": "DUPLICATE",
            "r1->r3:VOTE": "DROP",
        })
        result = self.r1.post("/client/elect", term=1)
        self.assertTrue(result["authorized"], result)
        self.assertEqual(result["voters"], ["r1", "r2"])
        self.assertEqual(len(result["voters"]), len(set(result["voters"])))
        self.assertEqual(self.r2.inspect()["message_ledger_count"], 1)

    def test_p14_05_exact_authority_acquisition_commits_to_two_independent_durable_stores(self):
        acquired = self._bootstrap()
        a = self.r1.inspect(self.permit_id)
        b = self.r2.inspect(self.permit_id)
        self.assertNotEqual(a["db_path"], b["db_path"])
        self.assertEqual(a["current_term"], b["current_term"])
        self.assertEqual(a["commit_index"], b["commit_index"])
        self.assertEqual(a["record_digest"], b["record_digest"])
        self.assertEqual(a["record"]["lease_owner_gateway_instance_id"], "gateway-a")
        self.assertEqual(a["record"]["lease_epoch"], 1)
        self.assertGreaterEqual(len(set(acquired["certificate"]["voters"])), 2)

    def test_p14_06_lost_peer_messages_make_isolated_former_leader_fail_closed_at_use_time(self):
        acquired = self._bootstrap()
        self.h.set_faults({
            "r1->r2:READ_CONFIRM": "DROP",
            "r1->r3:READ_CONFIRM": "DROP",
        })
        result = self.r1.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            cached_certificate=acquired["certificate"],
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "USE_TIME_QUORUM_REQUIRED")
        self.assertEqual(self.r1.inspect()["effect_count"], 0)

    def test_p14_07_delayed_ack_cannot_retroactively_authorize_after_timeout(self):
        self._bootstrap()
        self.h.set_faults({
            "r1->r2:READ_CONFIRM": "DELAY_UNTIL_RELEASE",
            "r1->r3:READ_CONFIRM": "DROP",
        })
        denied = self.r1.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
        )
        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason"], "USE_TIME_QUORUM_REQUIRED")
        released = self.r1.post("/test/release-delayed")
        self.assertEqual(released["released"], 1)
        self.assertEqual(self.r1.inspect()["effect_count"], 0)
        after = self.r1.inspect(self.permit_id)
        self.assertEqual(after["record"]["state"], "IN_FLIGHT")
        self.assertEqual(after["record"]["lease_epoch"], 1)

    def test_p14_08_higher_term_majority_failover_preserves_unexpired_old_lease(self):
        acquired = self._failover_term2()
        self.h.set_clock(int(acquired["lease_expires_at_ms"]) - 1)
        before = self.r2.inspect(self.permit_id)
        result = self.r2.post(
            "/client/takeover",
            permit_id=self.permit_id,
            new_owner_id="gateway-b",
            bindings=self.bindings,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "AUTHORITY_LIVE_OWNER_UNEXPIRED")
        after = self.r2.inspect(self.permit_id)
        self.assertEqual(after["commit_index"], before["commit_index"])
        self.assertEqual(after["record"], before["record"])
        self.assertEqual(self.r1.inspect(self.permit_id)["current_term"], 1)

    def test_p14_09_stale_term_authenticated_response_cannot_satisfy_term_two_quorum(self):
        self._bootstrap()
        local = self.r2.inspect(self.permit_id)
        probe = self.r2.post(
            "/test/probe-peer",
            peer_id="r3",
            message_type="READ_CONFIRM",
            term=1,
            payload={
                "expected_term": 1,
                "expected_leader_id": "r1",
                "expected_commit_index": local["commit_index"],
                "permit_id": self.permit_id,
                "expected_record_digest": local["record_digest"],
            },
        )
        self.assertEqual(len(probe["responses"]), 1)
        stale_response = copy.deepcopy(probe["responses"][0])
        self.assertEqual(stale_response["core"]["term"], 1)
        self.h.set_faults({"r2->r1:VOTE": "DROP", "r2->r1:REPLICATE": "DROP"})
        elected = self.r2.post("/client/elect", term=2)
        self.assertTrue(elected["authorized"], elected)
        collected = self.r2.post(
            "/test/collect-responses",
            responses=[stale_response],
            expected_type="READ_CONFIRM",
            expected_term=2,
            positive_field="confirmed",
        )
        self.assertFalse(collected["quorum_confirmed"])
        self.assertEqual(collected["voters"], ["r2"])

    def test_p14_10_exact_trusted_expiry_permits_term_two_takeover_and_epoch_advance_once(self):
        acquired = self._failover_term2()
        self.h.set_clock(int(acquired["lease_expires_at_ms"]))
        takeover = self.r2.post(
            "/client/takeover",
            permit_id=self.permit_id,
            new_owner_id="gateway-b",
            bindings=self.bindings,
        )
        self.assertTrue(takeover["authorized"], takeover)
        self.assertEqual(takeover["term"], 2)
        self.assertEqual(takeover["lease_epoch"], 2)
        self.assertEqual(takeover["certificate"]["term"], 2)
        b = self.r2.inspect(self.permit_id)
        c = self.r3.inspect(self.permit_id)
        self.assertEqual(b["commit_index"], c["commit_index"])
        self.assertEqual(b["record_digest"], c["record_digest"])
        self.assertEqual(b["record"]["lease_owner_gateway_instance_id"], "gateway-b")
        self.assertEqual(b["record"]["lease_epoch"], 2)

    def test_p14_11_reordered_old_authority_message_cannot_roll_back_committed_takeover(self):
        elected = self.r1.post("/client/elect", term=1)
        self.assertTrue(elected["authorized"])
        issued = self.r1.post("/client/issue", permit_id=self.permit_id, bindings=self.bindings)
        self.assertTrue(issued["authorized"])
        self.h.set_faults({"r1->r3:REPLICATE": "REORDER"})
        acquired = self.r1.post(
            "/client/acquire",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            bindings=self.bindings,
        )
        self.assertTrue(acquired["authorized"], acquired)
        self.assertEqual(self.r3.inspect(self.permit_id)["commit_index"], 1)

        self.h.set_faults({"r2->r1:VOTE": "DROP", "r2->r1:REPLICATE": "DROP"})
        self.assertTrue(self.r2.post("/client/elect", term=2)["authorized"])
        self.h.set_clock(int(acquired["lease_expires_at_ms"]))
        self.assertTrue(self.r2.post(
            "/client/takeover",
            permit_id=self.permit_id,
            new_owner_id="gateway-b",
            bindings=self.bindings,
        )["authorized"])
        before = self.r3.inspect(self.permit_id)
        released = self.r1.post("/test/release-delayed")
        self.assertEqual(released["released"], 1)
        response = released["outcomes"][0]["response_envelope"]
        self.assertFalse(response["core"]["payload"]["accepted"])
        self.assertEqual(response["core"]["payload"]["reason"], "REPLICATION_STALE_TERM")
        after = self.r3.inspect(self.permit_id)
        self.assertEqual(after["current_term"], before["current_term"])
        self.assertEqual(after["commit_index"], before["commit_index"])
        self.assertEqual(after["record_digest"], before["record_digest"])
        self.assertEqual(after["record"]["lease_epoch"], 2)

    def test_p14_12_replica_restart_preserves_stale_fencing_and_replay_ledger(self):
        self._takeover_b()
        stale = self.r1.inspect(self.permit_id)
        self.assertEqual(stale["current_term"], 1)
        probe = self.r2.post(
            "/test/probe-peer",
            peer_id="r1",
            message_type="STATE_SNAPSHOT",
            term=2,
            payload={"request": "CURRENT_STATE"},
        )
        self.assertEqual(len(probe["responses"]), 1)
        history = self.r2.post("/test/outbound-history")["messages"]
        state_messages = [m for m in history if m["peer_id"] == "r1" and m["envelope"]["core"]["message_type"] == "STATE_SNAPSHOT"]
        self.assertTrue(state_messages)
        message_id = state_messages[-1]["message_id"]
        ledger_before = self.r1.inspect()["message_ledger_count"]
        old_pid = self.r1.health()["pid"]
        info = self.h.restart("r1")
        self.r1 = self.h.client("r1")
        self.assertNotEqual(info["pid"], old_pid)
        self.assertGreaterEqual(self.r1.inspect()["message_ledger_count"], ledger_before)
        conflict = self.r2.post(
            "/test/replay-outbound-conflict",
            message_id=message_id,
            changed_payload={"request": "DIFFERENT_STATE"},
        )
        response = conflict["response_envelope"]
        self.assertEqual(response["core"]["payload"]["reason"], "MESSAGE_ID_CONFLICTING_REPLAY")
        read = self.r1.post("/client/authoritative-read", permit_id=self.permit_id)
        self.assertFalse(read["authoritative"])
        self.h.set_faults({})
        caught = self.r1.post("/client/catch-up")
        self.assertTrue(caught["authorized"], caught)
        repaired = self.r1.inspect(self.permit_id)
        current = self.r2.inspect(self.permit_id)
        self.assertEqual(repaired["current_term"], current["current_term"])
        self.assertEqual(repaired["commit_index"], current["commit_index"])
        self.assertEqual(repaired["record_digest"], current["record_digest"])

    def test_p14_13_total_process_level_quorum_loss_denies_all_new_consequential_authority(self):
        self._bootstrap()
        rules = {}
        for sender in ("r1", "r2", "r3"):
            for receiver in ("r1", "r2", "r3"):
                if sender != receiver:
                    for message_type in ("VOTE", "REPLICATE", "READ_CONFIRM", "STATE_SNAPSHOT"):
                        rules[f"{sender}->{receiver}:{message_type}"] = "DROP"
        self.h.set_faults(rules)
        renew = self.r1.post(
            "/client/renew",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
        )
        self.assertFalse(renew["authorized"])
        finalize = self.r1.post(
            "/client/finalize",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            result_digest="result-x",
        )
        self.assertFalse(finalize["authorized"])
        execute = self.r1.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
        )
        self.assertFalse(execute["authorized"])
        election = self.r2.post("/client/elect", term=2)
        self.assertFalse(election["authorized"])
        takeover = self.r2.post(
            "/client/takeover",
            permit_id=self.permit_id,
            new_owner_id="gateway-b",
            bindings=self.bindings,
        )
        self.assertFalse(takeover["authorized"])
        fresh = dict(self.bindings)
        fresh["idempotency_key"] = "intent-new"
        fresh["effect_digest"] = "effect-new"
        issue = self.r1.post("/client/issue", permit_id="permit-new", bindings=fresh)
        self.assertFalse(issue["authorized"])
        self.assertEqual(self.r1.inspect()["effect_count"], 0)

    def test_p14_14_network_heal_and_catchup_converges_without_rollback(self):
        self._takeover_b()
        stale = self.r1.inspect(self.permit_id)
        current = self.r2.inspect(self.permit_id)
        self.assertLess(stale["current_term"], current["current_term"])
        self.assertLess(stale["commit_index"], current["commit_index"])
        self.h.set_faults({})
        caught = self.r1.post("/client/catch-up")
        self.assertTrue(caught["authorized"], caught)
        repaired = self.r1.inspect(self.permit_id)
        self.assertEqual(repaired["current_term"], current["current_term"])
        self.assertEqual(repaired["commit_index"], current["commit_index"])
        self.assertEqual(repaired["record_digest"], current["record_digest"])
        self.assertEqual(repaired["record"]["lease_epoch"], 2)
        self.assertEqual(repaired["record"]["lease_owner_gateway_instance_id"], "gateway-b")

    def test_p14_15_posteffect_leader_crash_and_higher_term_recovery_remains_exactly_once(self):
        _, takeover = self._takeover_b()
        crashed = self.r2.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-b",
            lease_epoch=2,
            bindings=self.bindings,
            crash_after_effect=True,
        )
        self.assertIsNone(crashed["authorized"])
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            proc = self.h.processes.get("r2")
            if proc is not None and proc.poll() is not None:
                break
            time.sleep(0.02)
        self.assertEqual(self.r3.inspect()["effect_count"], 1)
        self.h.set_faults({})
        elected = self.r3.post("/client/elect", term=3)
        self.assertTrue(elected["authorized"], elected)
        retry = self.r3.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-b",
            lease_epoch=takeover["lease_epoch"],
            bindings=self.bindings,
        )
        self.assertTrue(retry["authorized"], retry)
        self.assertTrue(retry["effect_result"]["replayed"])
        self.assertEqual(self.r3.inspect()["effect_count"], 1)
        current = self.r3.inspect(self.permit_id)
        self.assertEqual(current["current_term"], 3)
        self.assertEqual(current["record"]["state"], "CONSUMED")
        self.assertEqual(current["record"]["lease_epoch"], 2)

    def test_p14_16_fresh_clean_authority_remains_live_after_faults_restart_and_repair(self):
        _, takeover = self._takeover_b()
        crashed = self.r2.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-b",
            lease_epoch=2,
            bindings=self.bindings,
            crash_after_effect=True,
        )
        self.assertIsNone(crashed["authorized"])
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            proc = self.h.processes.get("r2")
            if proc is not None and proc.poll() is not None:
                break
            time.sleep(0.02)
        self.h.set_faults({})
        self.assertTrue(self.r3.post("/client/elect", term=3)["authorized"])
        recovered = self.r3.post(
            "/client/execute",
            permit_id=self.permit_id,
            owner_id="gateway-b",
            lease_epoch=takeover["lease_epoch"],
            bindings=self.bindings,
        )
        self.assertTrue(recovered["authorized"], recovered)
        self.assertEqual(self.r3.inspect()["effect_count"], 1)

        info = self.h.restart("r2")
        self.r2 = self.h.client("r2")
        self.assertEqual(info["replica_id"], "r2")
        caught = self.r2.post("/client/catch-up")
        self.assertTrue(caught["authorized"], caught)

        fresh = dict(self.bindings)
        fresh.update(
            semantic_payload_digest="semantic-fresh",
            effect_digest="effect-fresh",
            idempotency_key="intent-fresh",
        )
        permit = "permit-fresh"
        issued = self.r3.post("/client/issue", permit_id=permit, bindings=fresh)
        self.assertTrue(issued["authorized"], issued)
        acquired = self.r3.post(
            "/client/acquire",
            permit_id=permit,
            owner_id="gateway-fresh",
            bindings=fresh,
        )
        self.assertTrue(acquired["authorized"], acquired)
        result = self.r3.post(
            "/client/execute",
            permit_id=permit,
            owner_id="gateway-fresh",
            lease_epoch=1,
            bindings=fresh,
        )
        self.assertTrue(result["authorized"], result)
        self.assertTrue(result["effect_result"]["executed"])
        self.assertEqual(self.r3.inspect()["effect_count"], 2)
        a = self.r1.inspect(permit)
        b = self.r2.inspect(permit)
        c = self.r3.inspect(permit)
        digests = {x["record_digest"] for x in (a, b, c) if x["record_digest"] is not None}
        self.assertEqual(len(digests), 1)
        self.assertEqual(c["record"]["state"], "CONSUMED")


if __name__ == "__main__":
    unittest.main()
