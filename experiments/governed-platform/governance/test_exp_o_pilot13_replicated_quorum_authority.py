from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from replicated_quorum_authority_exp_o import (
    ReplicatedQuorumAuthorityCluster,
    SQLiteEffectBoundary,
)


class MutableClock:
    def __init__(self, value: int = 0) -> None:
        self.value = int(value)

    def __call__(self) -> int:
        return int(self.value)


class ExpOPilot13ReplicatedQuorumAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.clock = MutableClock(0)
        self.cluster = ReplicatedQuorumAuthorityCluster(self.clock)
        self.effect_boundary = SQLiteEffectBoundary(Path(self.temp.name) / "effects.sqlite")
        self.bindings = {
            "semantic_payload_digest": "semantic-a",
            "effect_digest": "effect-a",
            "idempotency_key": "intent-a",
            "worker_id": "worker-a",
            "worker_key_thumbprint": "worker-key-a",
            "effect_contract_id": "contract-v1",
            "base_sha": "base-v1",
        }
        self.permit_id = "permit-a"

    def _bootstrap(self):
        elected = self.cluster.elect("r1", term=1, voters=["r1", "r2"])
        self.assertTrue(elected["authorized"])
        issued = self.cluster.issue("r1", self.permit_id, self.bindings)
        self.assertTrue(issued["authorized"])
        acquired = self.cluster.acquire(
            "r1", self.permit_id, owner_id="gateway-a", bindings=self.bindings
        )
        self.assertTrue(acquired["authorized"])
        return acquired

    def _majority_failover(self):
        acquired = self._bootstrap()
        self.cluster.set_partitions([["r1"], ["r2", "r3"]])
        elected = self.cluster.elect("r2", term=2, voters=["r2", "r3"])
        self.assertTrue(elected["authorized"])
        return acquired

    def _takeover_b(self):
        acquired = self._majority_failover()
        self.clock.value = int(acquired["lease_expires_at_ms"])
        takeover = self.cluster.takeover(
            "r2", self.permit_id, new_owner_id="gateway-b", bindings=self.bindings
        )
        self.assertTrue(takeover["authorized"])
        self.assertEqual(takeover["lease_epoch"], 2)
        return acquired, takeover

    def test_p13_01_three_member_election_requires_two_distinct_voters(self):
        duplicate = self.cluster.elect("r1", term=1, voters=["r1", "r1"])
        self.assertFalse(duplicate["authorized"])
        self.assertEqual(duplicate["reason"], "ELECTION_DUPLICATE_VOTER")
        singleton = self.cluster.elect("r1", term=1, voters=["r1"])
        self.assertFalse(singleton["authorized"])
        self.assertEqual(singleton["reason"], "ELECTION_QUORUM_REQUIRED")
        elected = self.cluster.elect("r1", term=1, voters=["r1", "r2"])
        self.assertTrue(elected["authorized"])
        self.assertEqual(elected["term"], 1)
        self.assertEqual(elected["voters"], ["r1", "r2"])

    def test_p13_02_initial_exact_authority_acquisition_is_quorum_committed(self):
        acquired = self._bootstrap()
        cert = acquired["certificate"]
        self.assertEqual(len(cert["voters"]), 2)
        self.assertEqual(len(set(cert["voters"])), 2)
        self.assertTrue(self.cluster.validate_certificate_shape(cert)["authorized"])
        r1 = self.cluster.inspect_replica("r1", self.permit_id)
        r2 = self.cluster.inspect_replica("r2", self.permit_id)
        self.assertEqual(r1["commit_index"], r2["commit_index"])
        self.assertEqual(r1["record_digest"], r2["record_digest"])
        self.assertEqual(r1["record"]["lease_owner_gateway_instance_id"], "gateway-a")
        self.assertEqual(r1["record"]["lease_epoch"], 1)

    def test_p13_03_isolated_former_leader_cannot_revalidate_consequential_use(self):
        acquired = self._bootstrap()
        self.cluster.set_partitions([["r1"], ["r2", "r3"]])
        result = self.cluster.execute(
            "r1",
            self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
            cached_certificate=acquired["certificate"],
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "QUORUM_UNAVAILABLE")
        self.assertEqual(self.effect_boundary.count(), 0)

    def test_p13_04_minority_former_leader_cannot_renew(self):
        self._bootstrap()
        before = self.cluster.inspect_replica("r1", self.permit_id)
        self.cluster.set_partitions([["r1"], ["r2", "r3"]])
        self.clock.value = 500
        result = self.cluster.renew(
            "r1", self.permit_id, owner_id="gateway-a", lease_epoch=1, bindings=self.bindings
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "QUORUM_UNAVAILABLE")
        after = self.cluster.inspect_replica("r1", self.permit_id)
        self.assertEqual(after["commit_index"], before["commit_index"])
        self.assertEqual(after["record"], before["record"])

    def test_p13_05_minority_partition_cannot_advance_term_epoch_or_mint_authority(self):
        acquired = self._bootstrap()
        self.cluster.set_partitions([["r1"], ["r2", "r3"]])
        election = self.cluster.elect("r1", term=2, voters=["r1"])
        self.assertFalse(election["authorized"])
        takeover = self.cluster.takeover(
            "r1", self.permit_id, new_owner_id="gateway-x", bindings=self.bindings
        )
        self.assertFalse(takeover["authorized"])
        state = self.cluster.inspect_replica("r1", self.permit_id)
        self.assertEqual(state["current_term"], 1)
        self.assertEqual(state["record"]["lease_epoch"], 1)
        forged = dict(acquired["certificate"])
        forged["voters"] = ["r1", "r1"]
        cert = self.cluster.validate_certificate_shape(forged)
        self.assertFalse(cert["authorized"])
        self.assertEqual(cert["reason"], "CERTIFICATE_DUPLICATE_VOTER")

    def test_p13_06_majority_partition_elects_higher_term_leader(self):
        self._majority_failover()
        r2 = self.cluster.inspect_replica("r2", self.permit_id)
        r3 = self.cluster.inspect_replica("r3", self.permit_id)
        r1 = self.cluster.inspect_replica("r1", self.permit_id)
        self.assertEqual((r2["current_term"], r2["leader_id"]), (2, "r2"))
        self.assertEqual((r3["current_term"], r3["leader_id"]), (2, "r2"))
        self.assertEqual((r1["current_term"], r1["leader_id"]), (1, "r1"))

    def test_p13_07_new_majority_leader_cannot_steal_unexpired_old_lease(self):
        acquired = self._majority_failover()
        self.clock.value = int(acquired["lease_expires_at_ms"]) - 1
        before = self.cluster.inspect_replica("r2", self.permit_id)
        result = self.cluster.takeover(
            "r2", self.permit_id, new_owner_id="gateway-b", bindings=self.bindings
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "AUTHORITY_LIVE_OWNER_UNEXPIRED")
        after = self.cluster.inspect_replica("r2", self.permit_id)
        self.assertEqual(after["record"], before["record"])
        self.assertEqual(after["commit_index"], before["commit_index"])

    def test_p13_08_exact_expiry_allows_majority_takeover_under_higher_term(self):
        acquired = self._majority_failover()
        self.clock.value = int(acquired["lease_expires_at_ms"])
        result = self.cluster.takeover(
            "r2", self.permit_id, new_owner_id="gateway-b", bindings=self.bindings
        )
        self.assertTrue(result["authorized"])
        self.assertEqual(result["term"], 2)
        self.assertEqual(result["lease_epoch"], 2)
        self.assertEqual(result["lease_owner_gateway_instance_id"], "gateway-b")
        self.assertEqual(result["lease_expires_at_ms"], self.clock.value + 1000)
        self.assertEqual(result["certificate"]["term"], 2)

    def test_p13_09_stale_term_one_leader_cannot_use_renew_finalize_or_overwrite(self):
        _, takeover = self._takeover_b()
        stale_before = self.cluster.inspect_replica("r1", self.permit_id)
        use = self.cluster.execute(
            "r1",
            self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
        )
        renew = self.cluster.renew(
            "r1", self.permit_id, owner_id="gateway-a", lease_epoch=1, bindings=self.bindings
        )
        finalize = self.cluster.finalize(
            "r1",
            self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            authoritative_result_digest="stale-result",
        )
        overwrite = self.cluster.elect("r1", term=3, voters=["r1"])
        for result in (use, renew, finalize, overwrite):
            self.assertFalse(result["authorized"])
        self.assertEqual(self.effect_boundary.count(), 0)
        stale_after = self.cluster.inspect_replica("r1", self.permit_id)
        self.assertEqual(stale_after["record"], stale_before["record"])
        self.assertEqual(takeover["lease_epoch"], 2)

    def test_p13_10_stale_replica_or_old_certificate_cannot_be_promoted_to_authoritative_use(self):
        acquired, _ = self._takeover_b()
        stale = self.cluster.authoritative_read("r1", self.permit_id)
        self.assertFalse(stale["authoritative"])
        result = self.cluster.execute(
            "r1",
            self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
            cached_certificate=acquired["certificate"],
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(self.effect_boundary.count(), 0)
        current_side_old_owner = self.cluster.execute(
            "r2",
            self.permit_id,
            owner_id="gateway-a",
            lease_epoch=1,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
            cached_certificate=acquired["certificate"],
        )
        self.assertFalse(current_side_old_owner["authorized"])
        self.assertEqual(current_side_old_owner["reason"], "AUTHORITY_STALE_OWNER")

    def test_p13_11_competing_leadership_claims_cannot_both_commit_authority(self):
        acquired = self._majority_failover()
        minority = self.cluster.elect("r1", term=3, voters=["r1"])
        self.assertFalse(minority["authorized"])
        self.clock.value = int(acquired["lease_expires_at_ms"])
        before = self.cluster.inspect_replica("r2", self.permit_id)
        changed = dict(self.bindings)
        changed["effect_digest"] = "effect-substituted"
        changed_attempt = self.cluster.takeover(
            "r2", self.permit_id, new_owner_id="gateway-b", bindings=changed
        )
        self.assertFalse(changed_attempt["authorized"])
        self.assertEqual(
            self.cluster.inspect_replica("r2", self.permit_id)["commit_index"],
            before["commit_index"],
        )
        majority = self.cluster.takeover(
            "r2", self.permit_id, new_owner_id="gateway-b", bindings=self.bindings
        )
        self.assertTrue(majority["authorized"])
        self.assertEqual(majority["term"], 2)
        self.assertEqual(majority["lease_epoch"], 2)

    def test_p13_12_total_quorum_loss_fails_closed(self):
        acquired = self._bootstrap()
        self.cluster.set_partitions([["r1"], ["r2"], ["r3"]])
        self.clock.value = int(acquired["lease_expires_at_ms"])
        operations = [
            self.cluster.renew(
                "r1", self.permit_id, owner_id="gateway-a", lease_epoch=1, bindings=self.bindings
            ),
            self.cluster.takeover(
                "r2", self.permit_id, new_owner_id="gateway-b", bindings=self.bindings
            ),
            self.cluster.finalize(
                "r1",
                self.permit_id,
                owner_id="gateway-a",
                lease_epoch=1,
                bindings=self.bindings,
                authoritative_result_digest="x",
            ),
            self.cluster.execute(
                "r1",
                self.permit_id,
                owner_id="gateway-a",
                lease_epoch=1,
                bindings=self.bindings,
                effect_boundary=self.effect_boundary,
            ),
        ]
        for result in operations:
            self.assertFalse(result["authorized"])
        self.assertFalse(self.cluster.elect("r3", term=2, voters=["r3"])["authorized"])
        self.assertEqual(self.effect_boundary.count(), 0)

    def test_p13_13_quorum_restoration_preserves_highest_committed_term_and_index(self):
        _, takeover = self._takeover_b()
        current = self.cluster.inspect_replica("r2", self.permit_id)
        stale = self.cluster.inspect_replica("r1", self.permit_id)
        self.assertLess(stale["current_term"], current["current_term"])
        self.assertLess(stale["commit_index"], current["commit_index"])
        self.cluster.heal_all()
        caught = self.cluster.catch_up("r1")
        self.assertTrue(caught["authorized"])
        repaired = self.cluster.inspect_replica("r1", self.permit_id)
        self.assertEqual(repaired["current_term"], current["current_term"])
        self.assertEqual(repaired["commit_index"], current["commit_index"])
        self.assertEqual(repaired["record_digest"], current["record_digest"])
        self.assertEqual(repaired["record"]["lease_epoch"], takeover["lease_epoch"])

    def test_p13_14_stale_replica_cannot_serve_authoritative_read_until_caught_up(self):
        self._takeover_b()
        self.cluster.heal_all()
        before = self.cluster.authoritative_read("r1", self.permit_id)
        self.assertFalse(before["authoritative"])
        self.assertEqual(before["reason"], "STALE_REPLICA_TERM")
        self.assertTrue(self.cluster.catch_up("r1")["authorized"])
        after = self.cluster.authoritative_read("r1", self.permit_id)
        self.assertTrue(after["authoritative"])
        self.assertEqual(after["record"]["lease_owner_gateway_instance_id"], "gateway-b")
        self.assertEqual(after["record"]["lease_epoch"], 2)

    def test_p13_15_effect_remains_exactly_once_across_leader_crash_after_commit_ambiguity(self):
        _, takeover = self._takeover_b()
        first = self.cluster.execute(
            "r2",
            self.permit_id,
            owner_id="gateway-b",
            lease_epoch=2,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
            crash_after_effect=True,
        )
        self.assertIsNone(first["authorized"])
        self.assertEqual(first["decision"], "POST_EFFECT_FINALIZATION_UNKNOWN")
        self.assertEqual(self.effect_boundary.count(), 1)
        self.cluster.set_partitions([["r2"], ["r1", "r3"]])
        elected = self.cluster.elect("r3", term=3, voters=["r3", "r1"])
        self.assertTrue(elected["authorized"])
        retry = self.cluster.execute(
            "r3",
            self.permit_id,
            owner_id="gateway-b",
            lease_epoch=2,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
        )
        self.assertTrue(retry["authorized"])
        self.assertTrue(retry["effect_result"]["replayed"])
        self.assertEqual(self.effect_boundary.count(), 1)
        current = self.cluster.inspect_replica("r3", self.permit_id)
        self.assertEqual(current["record"]["state"], "CONSUMED")
        self.assertEqual(current["current_term"], 3)
        self.assertEqual(current["record"]["lease_epoch"], takeover["lease_epoch"])

    def test_p13_16_fresh_clean_authority_remains_live_after_partition_and_repair(self):
        self._takeover_b()
        ambiguous = self.cluster.execute(
            "r2",
            self.permit_id,
            owner_id="gateway-b",
            lease_epoch=2,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
            crash_after_effect=True,
        )
        self.assertIsNone(ambiguous["authorized"])
        self.cluster.set_partitions([["r2"], ["r1", "r3"]])
        self.assertTrue(self.cluster.elect("r3", term=3, voters=["r3", "r1"])["authorized"])
        recovered = self.cluster.execute(
            "r3",
            self.permit_id,
            owner_id="gateway-b",
            lease_epoch=2,
            bindings=self.bindings,
            effect_boundary=self.effect_boundary,
        )
        self.assertTrue(recovered["authorized"])
        self.cluster.heal_all()
        self.assertTrue(self.cluster.catch_up("r2")["authorized"])

        fresh_bindings = dict(self.bindings)
        fresh_bindings.update(
            semantic_payload_digest="semantic-fresh",
            effect_digest="effect-fresh",
            idempotency_key="intent-fresh",
        )
        fresh_permit = "permit-fresh"
        issued = self.cluster.issue("r3", fresh_permit, fresh_bindings)
        self.assertTrue(issued["authorized"])
        acquired = self.cluster.acquire(
            "r3", fresh_permit, owner_id="gateway-fresh", bindings=fresh_bindings
        )
        self.assertTrue(acquired["authorized"])
        result = self.cluster.execute(
            "r3",
            fresh_permit,
            owner_id="gateway-fresh",
            lease_epoch=1,
            bindings=fresh_bindings,
            effect_boundary=self.effect_boundary,
        )
        self.assertTrue(result["authorized"])
        self.assertTrue(result["effect_result"]["executed"])
        self.assertEqual(self.effect_boundary.count(), 2)


if __name__ == "__main__":
    unittest.main()
