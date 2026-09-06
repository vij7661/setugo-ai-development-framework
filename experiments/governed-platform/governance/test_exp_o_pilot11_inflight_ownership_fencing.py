from __future__ import annotations

import copy
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest

from runtime_process_exp_o import read_gateway_effect_count
from runtime_slice_exp_o import AuthorityKernel, LocalEnforcementPoint
from semantic_permit_registry_exp_o import DurableSemanticBoundLocalEnforcementPoint, DurableSemanticPermitRegistry, REGISTRY_BINDING_FIELDS
from semantic_permit_fencing_exp_o import FencedSemanticBoundLocalEnforcementPoint, SemanticPermitLeaseRegistry
from semantic_fencing_process_exp_o import FencedSemanticGatewayProcessHarness
from semantic_verification_binding_exp_o import SemanticVerificationAuthority, digest


class ExpOPilot11InflightOwnershipFencingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="exp-o-p11-fence-")
        root = Path(self.tmp.name)
        self.effects_db = root / "effects.sqlite"
        self.registry_db = root / "semantic-and-lease.sqlite"
        self.ready = root / "ready.json"
        self.clock = root / "clock.txt"
        self.clock.write_text("100100", encoding="utf-8")

        self.kernel_key = b"p11-authority-kernel-key"
        self.inner_key = b"p11-inner-permit-key"
        self.semantic_key = b"p11-semantic-verifier-key"
        self.outer_key = b"p11-outer-permit-key"
        self.registry_key = b"p11-registry-integrity-key"
        self.lease_key = b"p11-lease-integrity-key"

        self.kernel = AuthorityKernel(self.kernel_key)
        historical_lep = LocalEnforcementPoint(self.kernel, self.inner_key)
        self.verifier = SemanticVerificationAuthority(self.semantic_key, verifier_id="p11-independent-verifier")
        self.p10_registry = DurableSemanticPermitRegistry(self.registry_db, self.registry_key)
        p10_lep = DurableSemanticBoundLocalEnforcementPoint(
            historical_lep,
            semantic_verification_key=self.verifier.verification_key,
            outer_permit_signing_key=self.outer_key,
            registry=self.p10_registry,
        )
        self.leases = SemanticPermitLeaseRegistry(self.registry_db, self.lease_key, self.p10_registry)
        self.bound_lep = FencedSemanticBoundLocalEnforcementPoint(p10_lep, self.leases)
        self.capability = self.kernel.issue_capability(
            subject_id="worker",
            subject_key_thumbprint="worker-key",
            issued_at_ms=90_000,
            expires_at_ms=120_000,
            freshness_class="WORKSPACE_MUTATION",
            allowed_actions=["WRITE"],
            allowed_resources=["src/app.py"],
            effect_contract_id="contract-v1",
            base_sha="base-v1",
        )
        self.contract = {
            "effect_contract_id": "contract-v1",
            "base_sha": "base-v1",
            "allowed_action_classes": ["WRITE"],
            "allowed_resources": ["src/app.py"],
            "forbidden_resources": ["prod/**", ".github/**", "secrets/**"],
            "max_changed_files": 1,
            "destructive_effect_allowed": False,
            "semantic_correspondence_required": True,
        }
        self.candidate_a = {"change_intent": "Apply independently verified correction A", "rationale": "candidate A"}
        self.candidate_b = {"change_intent": "Apply independently verified correction B", "rationale": "candidate B"}
        self.harness = FencedSemanticGatewayProcessHarness(
            effects_db_path=self.effects_db,
            registry_db_path=self.registry_db,
            lease_db_path=self.registry_db,
            ready_path=self.ready,
            clock_path=self.clock,
            outer_permit_key=self.outer_key,
            registry_key=self.registry_key,
            lease_key=self.lease_key,
            inner_permit_key=self.inner_key,
            enable_test_faults=True,
        )

    def tearDown(self) -> None:
        self.harness.stop()
        self.tmp.cleanup()

    def effect_for(self, candidate: dict) -> dict:
        return {
            "action_class": "WRITE",
            "target_resources": ["src/app.py"],
            "changed_files": ["src/app.py"],
            "base_sha": "base-v1",
            "effect_contract_id": "contract-v1",
            "destructive_effect": False,
            "provenance_trust_classes": ["REMOTE_MODEL_PROPOSAL"],
            "semantic_payload_digest": digest(candidate),
        }

    def issue(self, candidate: dict, *, key: str, effect: dict | None = None) -> tuple[dict, dict]:
        actual_effect = copy.deepcopy(effect if effect is not None else self.effect_for(candidate))
        evidence = self.verifier.verify_candidate(candidate_payload=candidate, effect=actual_effect)
        auth = self.bound_lep.authorize(
            self.capability,
            candidate_payload=candidate,
            semantic_verification=evidence,
            worker_id="worker",
            worker_key_thumbprint="worker-key",
            effect_contract=self.contract,
            effect=actual_effect,
            idempotency_key=key,
            now_ms=100_000,
            origin_available=True,
            online_authority_confirmed=False,
        )
        self.assertTrue(auth.get("authorized"), auth)
        bound_id = auth["permit"]["payload"]["bound_permit_id"]
        lease = self.leases.inspect(bound_id)
        self.assertEqual(lease["state"], "ISSUED")
        self.assertEqual(lease["lease_epoch"], 0)
        return auth, actual_effect

    def start_client(self):
        info = self.harness.start()
        self.assertNotEqual(int(info["pid"]), os.getpid())
        return self.harness.client(timeout_s=1.5)

    def execute(self, client, auth: dict, candidate: dict, effect: dict, key: str, *, fault_mode: str | None = None):
        return client.execute(
            permit=auth["permit"],
            candidate_payload=candidate,
            worker_id="worker",
            worker_key_thumbprint="worker-key",
            effect=effect,
            idempotency_key=key,
            fault_mode=fault_mode,
        )

    def bound_id(self, auth: dict) -> str:
        return str(auth["permit"]["payload"]["bound_permit_id"])

    def expected_bindings(self, auth: dict) -> dict:
        payload = auth["permit"]["payload"]
        return {field: payload.get(field) for field in REGISTRY_BINDING_FIELDS if field != "bound_permit_id"}

    def wait_for_inflight(self, bound_id: str, *, timeout_s: float = 2.0) -> dict:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            lease = self.leases.inspect(bound_id)
            p10 = self.p10_registry.inspect(bound_id)
            if lease.get("state") == "IN_FLIGHT" and p10.get("state") == "IN_FLIGHT":
                return lease
            time.sleep(0.01)
        self.fail(f"permit {bound_id} did not become jointly IN_FLIGHT")

    def held_pair(self, *, key: str):
        auth, effect = self.issue(self.candidate_a, key=key)
        bound_id = self.bound_id(auth)
        client1 = self.start_client()
        first_box: dict = {}

        def first_call() -> None:
            first_box["result"] = self.execute(client1, auth, self.candidate_a, effect, key, fault_mode="HOLD_AFTER_RESOLVE")

        thread = threading.Thread(target=first_call, daemon=True)
        thread.start()
        lease = self.wait_for_inflight(bound_id)
        self.assertEqual(lease["lease_epoch"], 1)
        self.assertEqual(lease["lease_owner_gateway_instance_id"], self.harness.info["gateway_instance_id"])
        return auth, effect, bound_id, client1, thread, first_box

    def release_and_join(self, client, thread: threading.Thread, first_box: dict) -> dict:
        client.release_test_hold()
        thread.join(timeout=3.0)
        self.assertFalse(thread.is_alive())
        self.assertIn("result", first_box)
        return first_box["result"]

    def test_p11_01_first_use_acquires_owner_epoch_one_and_consumes(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-first")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        result = self.execute(client, auth, self.candidate_a, effect, "p11-first")
        self.assertTrue(result["authorized"])
        self.assertEqual(result["decision"], "EXECUTED")
        self.assertEqual(result["lease_disposition"], "FIRST_OWNER")
        self.assertEqual(result["lease_epoch"], 1)
        lease = self.leases.inspect(bound_id)
        self.assertEqual(lease["state"], "CONSUMED")
        self.assertEqual(lease["lease_epoch"], 1)
        self.assertEqual(self.p10_registry.inspect(bound_id)["state"], "CONSUMED")

    def test_p11_02_same_instance_duplicate_while_held_is_non_authorizing(self) -> None:
        auth, effect, _bound, client, thread, box = self.held_pair(key="p11-held-duplicate")
        loser = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-held-duplicate")
        self.assertFalse(loser["authorized"])
        self.assertEqual(loser["reason"], "SEMANTIC_IN_FLIGHT_ALREADY_OWNED")
        winner = self.release_and_join(client, thread, box)
        self.assertTrue(winner["authorized"])
        self.assertEqual(winner["decision"], "EXECUTED")

    def test_p11_03_concurrent_pair_has_only_one_fresh_authorization_success(self) -> None:
        auth, effect, _bound, client, thread, box = self.held_pair(key="p11-one-authorizer")
        loser = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-one-authorizer")
        winner = self.release_and_join(client, thread, box)
        authorized = [r for r in (winner, loser) if r.get("authorized") is True]
        self.assertEqual(len(authorized), 1)
        self.assertEqual(authorized[0]["decision"], "EXECUTED")

    def test_p11_04_concurrent_duplicate_commits_exactly_one_effect(self) -> None:
        auth, effect, _bound, client, thread, box = self.held_pair(key="p11-one-effect")
        loser = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-one-effect")
        self.assertFalse(loser["authorized"])
        self.release_and_join(client, thread, box)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_05_changed_candidate_cannot_bypass_live_owner(self) -> None:
        auth, _effect, _bound, client, thread, box = self.held_pair(key="p11-candidate-live-owner")
        effect_b = self.effect_for(self.candidate_b)
        denied = self.execute(self.harness.client(), auth, self.candidate_b, effect_b, "p11-candidate-live-owner")
        self.assertFalse(denied["authorized"])
        self.assertIn("semantic_payload_digest", denied["reason"])
        self.release_and_join(client, thread, box)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_06_changed_effect_cannot_bypass_live_owner(self) -> None:
        auth, effect, _bound, client, thread, box = self.held_pair(key="p11-effect-live-owner")
        mutated = copy.deepcopy(effect)
        mutated["provenance_trust_classes"] = ["REMOTE_MODEL_PROPOSAL", "UNTRUSTED_TOOL_CONTENT"]
        denied = self.execute(self.harness.client(), auth, self.candidate_a, mutated, "p11-effect-live-owner")
        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason"], "SEMANTIC_BOUND_OUTER_PERMIT_MISMATCH:effect_digest")
        self.release_and_join(client, thread, box)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_07_semantic_idempotency_rebinding_remains_denied(self) -> None:
        auth_a, effect_a = self.issue(self.candidate_a, key="p11-same-semantic-key")
        client = self.start_client()
        first = self.execute(client, auth_a, self.candidate_a, effect_a, "p11-same-semantic-key")
        self.assertEqual(first["decision"], "EXECUTED")
        auth_b, effect_b = self.issue(self.candidate_b, key="p11-same-semantic-key")
        second = self.execute(client, auth_b, self.candidate_b, effect_b, "p11-same-semantic-key")
        self.assertFalse(second["authorized"])
        self.assertEqual(second["reason"], "SEMANTIC_IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_EFFECT")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_08_crash_after_resolve_leaves_owner_epoch_one_inflight(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-crash-inflight")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        old_owner = self.harness.info["gateway_instance_id"]
        uncertain = self.execute(client, auth, self.candidate_a, effect, "p11-crash-inflight", fault_mode="CRASH_AFTER_RESOLVE")
        self.assertFalse(uncertain["transport_complete"])
        lease = self.leases.inspect(bound_id)
        self.assertEqual(lease["state"], "IN_FLIGHT")
        self.assertEqual(lease["lease_owner_gateway_instance_id"], old_owner)
        self.assertEqual(lease["lease_epoch"], 1)
        self.assertEqual(self.p10_registry.inspect(bound_id)["state"], "IN_FLIGHT")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p11_09_restart_exact_takeover_advances_epoch_and_executes_once(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-takeover")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        old_owner = self.harness.info["gateway_instance_id"]
        self.execute(client, auth, self.candidate_a, effect, "p11-takeover", fault_mode="CRASH_AFTER_RESOLVE")
        new_info = self.harness.restart()
        self.assertNotEqual(old_owner, new_info["gateway_instance_id"])
        result = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-takeover")
        self.assertTrue(result["authorized"])
        self.assertEqual(result["lease_disposition"], "RESTART_TAKEOVER")
        self.assertEqual(result["lease_epoch"], 2)
        self.assertEqual(result["decision"], "EXECUTED")
        lease = self.leases.inspect(bound_id)
        self.assertEqual(lease["state"], "CONSUMED")
        self.assertEqual(lease["lease_epoch"], 2)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_10_old_owner_epoch_cannot_finalize_after_takeover(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-stale-owner")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        old_owner = self.harness.info["gateway_instance_id"]
        self.execute(client, auth, self.candidate_a, effect, "p11-stale-owner", fault_mode="CRASH_AFTER_RESOLVE")
        new_info = self.harness.restart()
        takeover = self.leases.resolve_for_gateway(
            bound_id,
            gateway_instance_id=new_info["gateway_instance_id"],
            expected_bindings=self.expected_bindings(auth),
        )
        self.assertTrue(takeover["resolved"])
        self.assertEqual(takeover["lease_epoch"], 2)
        stale = self.leases.stale_finalize_probe(
            bound_id,
            gateway_instance_id=old_owner,
            lease_epoch=1,
            authoritative_result_digest="stale-result",
        )
        self.assertFalse(stale["finalized"])
        self.assertEqual(stale["reason"], "SEMANTIC_LEASE_STALE_OWNER")
        lease = self.leases.inspect(bound_id)
        self.assertEqual(lease["state"], "IN_FLIGHT")
        self.assertEqual(lease["lease_epoch"], 2)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p11_11_takeover_with_changed_candidate_is_denied_without_owner_change(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-takeover-candidate")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        self.execute(client, auth, self.candidate_a, effect, "p11-takeover-candidate", fault_mode="CRASH_AFTER_RESOLVE")
        before = self.leases.inspect(bound_id)
        self.harness.restart()
        denied = self.execute(self.harness.client(), auth, self.candidate_b, self.effect_for(self.candidate_b), "p11-takeover-candidate")
        self.assertFalse(denied["authorized"])
        after = self.leases.inspect(bound_id)
        self.assertEqual(after["lease_owner_gateway_instance_id"], before["lease_owner_gateway_instance_id"])
        self.assertEqual(after["lease_epoch"], 1)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p11_12_takeover_with_changed_idempotency_key_is_denied_without_owner_change(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-takeover-key")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        self.execute(client, auth, self.candidate_a, effect, "p11-takeover-key", fault_mode="CRASH_AFTER_RESOLVE")
        before = self.leases.inspect(bound_id)
        self.harness.restart()
        denied = self.execute(self.harness.client(), auth, self.candidate_a, effect, "different-key")
        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason"], "SEMANTIC_BOUND_OUTER_PERMIT_MISMATCH:idempotency_key")
        after = self.leases.inspect(bound_id)
        self.assertEqual(after["lease_owner_gateway_instance_id"], before["lease_owner_gateway_instance_id"])
        self.assertEqual(after["lease_epoch"], 1)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p11_13_post_effect_crash_takeover_reconciles_without_duplicate(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-post-effect-crash")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        old_owner = self.harness.info["gateway_instance_id"]
        uncertain = self.execute(
            client,
            auth,
            self.candidate_a,
            effect,
            "p11-post-effect-crash",
            fault_mode="CRASH_AFTER_GATEWAY_BEFORE_FINALIZE",
        )
        self.assertFalse(uncertain["transport_complete"])
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)
        self.assertEqual(self.leases.inspect(bound_id)["state"], "IN_FLIGHT")
        self.assertEqual(self.p10_registry.inspect(bound_id)["state"], "IN_FLIGHT")
        new_info = self.harness.restart()
        self.assertNotEqual(old_owner, new_info["gateway_instance_id"])
        result = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-post-effect-crash")
        self.assertTrue(result["authorized"])
        self.assertEqual(result["decision"], "IDEMPOTENT_REPLAY")
        self.assertFalse(result["executed"])
        self.assertTrue(result["replayed"])
        self.assertEqual(result["lease_disposition"], "RESTART_TAKEOVER")
        self.assertEqual(result["lease_epoch"], 2)
        self.assertEqual(self.leases.inspect(bound_id)["state"], "CONSUMED")
        self.assertEqual(self.p10_registry.inspect(bound_id)["state"], "CONSUMED")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_14_stale_owner_cannot_overwrite_new_result_digest(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-result-fence")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        old_owner = self.harness.info["gateway_instance_id"]
        self.execute(client, auth, self.candidate_a, effect, "p11-result-fence", fault_mode="CRASH_AFTER_GATEWAY_BEFORE_FINALIZE")
        self.harness.restart()
        result = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-result-fence")
        self.assertEqual(result["decision"], "IDEMPOTENT_REPLAY")
        snapshot = self.leases.inspect(bound_id)
        committed_digest = snapshot["authoritative_result_digest"]
        for attempted in (committed_digest, "different-stale-result"):
            stale = self.leases.stale_finalize_probe(
                bound_id,
                gateway_instance_id=old_owner,
                lease_epoch=1,
                authoritative_result_digest=attempted,
            )
            self.assertFalse(stale["finalized"])
        after = self.leases.inspect(bound_id)
        self.assertEqual(after["authoritative_result_digest"], committed_digest)
        self.assertEqual(after["state"], "CONSUMED")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_15_consumed_permit_cannot_be_taken_over_after_restart(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="p11-consumed-restart")
        bound_id = self.bound_id(auth)
        client = self.start_client()
        first = self.execute(client, auth, self.candidate_a, effect, "p11-consumed-restart")
        self.assertEqual(first["decision"], "EXECUTED")
        before = self.leases.inspect(bound_id)
        self.harness.restart()
        replay = self.execute(self.harness.client(), auth, self.candidate_a, effect, "p11-consumed-restart")
        self.assertFalse(replay["authorized"])
        self.assertEqual(replay["reason"], "SEMANTIC_BOUND_PERMIT_CONSUMED")
        after = self.leases.inspect(bound_id)
        self.assertEqual(after["lease_epoch"], before["lease_epoch"])
        self.assertEqual(after["lease_owner_gateway_instance_id"], before["lease_owner_gateway_instance_id"])
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p11_16_fresh_clean_permit_executes_after_concurrency_and_restart(self) -> None:
        auth_a, effect_a, _bound, client, thread, box = self.held_pair(key="p11-before-fresh")
        loser = self.execute(self.harness.client(), auth_a, self.candidate_a, effect_a, "p11-before-fresh")
        self.assertFalse(loser["authorized"])
        self.release_and_join(client, thread, box)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)
        self.harness.restart()
        auth_b, effect_b = self.issue(self.candidate_b, key="p11-fresh-after")
        fresh = self.execute(self.harness.client(), auth_b, self.candidate_b, effect_b, "p11-fresh-after")
        self.assertTrue(fresh["authorized"])
        self.assertEqual(fresh["decision"], "EXECUTED")
        self.assertEqual(fresh["lease_epoch"], 1)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 2)


if __name__ == "__main__":
    unittest.main()
