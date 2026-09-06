from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from runtime_process_exp_o import read_gateway_effect_count
from runtime_slice_exp_o import AuthorityKernel, LocalEnforcementPoint
from semantic_permit_registry_exp_o import DurableSemanticBoundLocalEnforcementPoint, DurableSemanticPermitRegistry
from semantic_process_exp_o import SemanticGatewayProcessHarness
from semantic_verification_binding_exp_o import SemanticVerificationAuthority, digest


class ExpOPilot10ProcessSemanticPermitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="exp-o-p10-process-semantic-")
        root = Path(self.tmp.name)
        self.effects_db = root / "effects.sqlite"
        self.registry_db = root / "registry.sqlite"
        self.ready = root / "ready.json"
        self.clock = root / "clock.txt"
        self.clock.write_text("100100", encoding="utf-8")

        self.kernel_key = b"p10-authority-kernel-key"
        self.inner_key = b"p10-inner-lep-permit-key"
        self.semantic_key = b"p10-independent-semantic-key"
        self.outer_key = b"p10-outer-semantic-permit-key"
        self.registry_key = b"p10-durable-registry-integrity-key"

        self.kernel = AuthorityKernel(self.kernel_key)
        self.lep = LocalEnforcementPoint(self.kernel, self.inner_key)
        self.verifier = SemanticVerificationAuthority(self.semantic_key, verifier_id="p10-independent-verifier")
        self.registry = DurableSemanticPermitRegistry(self.registry_db, self.registry_key)
        self.bound_lep = DurableSemanticBoundLocalEnforcementPoint(
            self.lep,
            semantic_verification_key=self.verifier.verification_key,
            outer_permit_signing_key=self.outer_key,
            registry=self.registry,
        )
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
        self.candidate_b = {"change_intent": "Apply different independently verified correction B", "rationale": "candidate B"}
        self.harness = SemanticGatewayProcessHarness(
            effects_db_path=self.effects_db,
            registry_db_path=self.registry_db,
            ready_path=self.ready,
            clock_path=self.clock,
            outer_permit_key=self.outer_key,
            registry_key=self.registry_key,
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
        return auth, actual_effect

    def start_client(self):
        info = self.harness.start()
        self.assertNotEqual(int(info["pid"]), os.getpid())
        return self.harness.client(timeout_s=1.5)

    def execute(self, client, auth, candidate: dict, effect: dict, key: str, *, fault_mode: str | None = None):
        return client.execute(
            permit=auth["permit"] if auth is not None else None,
            candidate_payload=candidate,
            worker_id="worker",
            worker_key_thumbprint="worker-key",
            effect=effect,
            idempotency_key=key,
            fault_mode=fault_mode,
        )

    def test_p10_01_missing_outer_permit_denies_before_effect(self) -> None:
        client = self.start_client()
        effect = self.effect_for(self.candidate_a)
        result = client.execute(
            permit=None,
            candidate_payload=self.candidate_a,
            worker_id="worker",
            worker_key_thumbprint="worker-key",
            effect=effect,
            idempotency_key="missing-permit",
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_BOUND_OUTER_PERMIT_INVALID")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_02_forged_outer_permit_denies(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="forged")
        forged = copy.deepcopy(auth)
        forged["permit"]["signature"] = "0" * 64
        client = self.start_client()
        result = self.execute(client, forged, self.candidate_a, effect, "forged")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_BOUND_OUTER_PERMIT_INVALID")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_03_candidate_substitution_denies(self) -> None:
        auth, _effect_a = self.issue(self.candidate_a, key="candidate-substitution")
        effect_b = self.effect_for(self.candidate_b)
        client = self.start_client()
        result = self.execute(client, auth, self.candidate_b, effect_b, "candidate-substitution")
        self.assertFalse(result["authorized"])
        self.assertIn("semantic_payload_digest", result["reason"])
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_04_effect_substitution_denies(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="effect-substitution")
        mutated = copy.deepcopy(effect)
        mutated["provenance_trust_classes"] = ["REMOTE_MODEL_PROPOSAL", "UNTRUSTED_TOOL_CONTENT"]
        client = self.start_client()
        result = self.execute(client, auth, self.candidate_a, mutated, "effect-substitution")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_BOUND_OUTER_PERMIT_MISMATCH:effect_digest")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_05_missing_registry_record_denies(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="missing-registry")
        bound_id = auth["permit"]["payload"]["bound_permit_id"]
        with sqlite3.connect(self.registry_db) as conn:
            conn.execute("DELETE FROM semantic_permits WHERE bound_permit_id = ?", (bound_id,))
            conn.commit()
        client = self.start_client()
        result = self.execute(client, auth, self.candidate_a, effect, "missing-registry")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_REGISTRY_RECORD_MISSING")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_06_registry_record_tamper_denies(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="tamper-registry")
        bound_id = auth["permit"]["payload"]["bound_permit_id"]
        with sqlite3.connect(self.registry_db) as conn:
            row = conn.execute("SELECT record_json FROM semantic_permits WHERE bound_permit_id = ?", (bound_id,)).fetchone()
            record = json.loads(row[0])
            record["worker_id"] = "attacker-worker"
            conn.execute("UPDATE semantic_permits SET record_json = ? WHERE bound_permit_id = ?", (json.dumps(record, sort_keys=True, separators=(",", ":")), bound_id))
            conn.commit()
        client = self.start_client()
        result = self.execute(client, auth, self.candidate_a, effect, "tamper-registry")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_REGISTRY_INTEGRITY_INVALID")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_07_cross_record_substitution_denies(self) -> None:
        auth_a, effect_a = self.issue(self.candidate_a, key="cross-a")
        auth_b, _effect_b = self.issue(self.candidate_b, key="cross-b")
        id_a = auth_a["permit"]["payload"]["bound_permit_id"]
        id_b = auth_b["permit"]["payload"]["bound_permit_id"]
        with sqlite3.connect(self.registry_db) as conn:
            row_b = conn.execute("SELECT record_json, integrity_tag FROM semantic_permits WHERE bound_permit_id = ?", (id_b,)).fetchone()
            conn.execute(
                "UPDATE semantic_permits SET record_json = ?, integrity_tag = ? WHERE bound_permit_id = ?",
                (row_b[0], row_b[1], id_a),
            )
            conn.commit()
        client = self.start_client()
        result = self.execute(client, auth_a, self.candidate_a, effect_a, "cross-a")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_REGISTRY_RECORD_BINDING_INVALID")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 0)

    def test_p10_08_clean_cross_process_execution_once(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="clean-once")
        bound_id = auth["permit"]["payload"]["bound_permit_id"]
        client = self.start_client()
        result = self.execute(client, auth, self.candidate_a, effect, "clean-once")
        self.assertTrue(result["authorized"])
        self.assertEqual(result["decision"], "EXECUTED")
        self.assertTrue(result["executed"])
        self.assertEqual(result["registry_disposition"], "FIRST_USE")
        self.assertEqual(result["registry_state"], "CONSUMED")
        self.assertEqual(result["time_source"], "SEMANTIC_GATEWAY_PROCESS_TRUSTED_CLOCK")
        self.assertEqual(result["gateway_time_ms"], 100100)
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)
        self.assertEqual(self.registry.inspect(bound_id)["state"], "CONSUMED")

    def test_p10_09_exact_replay_after_consumed_does_not_authorize(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="completed-replay")
        client = self.start_client()
        first = self.execute(client, auth, self.candidate_a, effect, "completed-replay")
        second = self.execute(client, auth, self.candidate_a, effect, "completed-replay")
        self.assertEqual(first["decision"], "EXECUTED")
        self.assertFalse(second["authorized"])
        self.assertEqual(second["reason"], "SEMANTIC_BOUND_PERMIT_CONSUMED")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p10_10_same_idempotency_key_cannot_rebind_semantic_effect(self) -> None:
        auth_a, effect_a = self.issue(self.candidate_a, key="same-semantic-key")
        client = self.start_client()
        first = self.execute(client, auth_a, self.candidate_a, effect_a, "same-semantic-key")
        self.assertEqual(first["decision"], "EXECUTED")
        auth_b, effect_b = self.issue(self.candidate_b, key="same-semantic-key")
        second = self.execute(client, auth_b, self.candidate_b, effect_b, "same-semantic-key")
        self.assertFalse(second["authorized"])
        self.assertEqual(second["reason"], "SEMANTIC_IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_EFFECT")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p10_11_consumed_state_survives_gateway_restart(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="restart-consumed")
        client = self.start_client()
        first_info = dict(self.harness.info)
        first = self.execute(client, auth, self.candidate_a, effect, "restart-consumed")
        self.assertEqual(first["decision"], "EXECUTED")
        second_info = self.harness.restart()
        self.assertNotEqual(first_info["gateway_instance_id"], second_info["gateway_instance_id"])
        replay_client = self.harness.client(timeout_s=1.5)
        replay = self.execute(replay_client, auth, self.candidate_a, effect, "restart-consumed")
        self.assertFalse(replay["authorized"])
        self.assertEqual(replay["reason"], "SEMANTIC_BOUND_PERMIT_CONSUMED")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p10_12_post_effect_crash_reconciles_inflight_without_duplicate(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="ambiguous-after-effect")
        bound_id = auth["permit"]["payload"]["bound_permit_id"]
        client = self.start_client()
        old_instance = self.harness.info["gateway_instance_id"]
        uncertain = self.execute(
            client,
            auth,
            self.candidate_a,
            effect,
            "ambiguous-after-effect",
            fault_mode="CRASH_AFTER_GATEWAY_BEFORE_REGISTRY_FINALIZE",
        )
        self.assertFalse(uncertain["transport_complete"])
        self.assertEqual(uncertain["decision"], "TRANSPORT_OUTCOME_UNKNOWN")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)
        self.assertEqual(self.registry.inspect(bound_id)["state"], "IN_FLIGHT")

        new_info = self.harness.restart()
        self.assertNotEqual(old_instance, new_info["gateway_instance_id"])
        retry_client = self.harness.client(timeout_s=1.5)
        reconciled = self.execute(retry_client, auth, self.candidate_a, effect, "ambiguous-after-effect")
        self.assertTrue(reconciled["authorized"])
        self.assertEqual(reconciled["decision"], "IDEMPOTENT_REPLAY")
        self.assertFalse(reconciled["executed"])
        self.assertTrue(reconciled["replayed"])
        self.assertEqual(reconciled["registry_disposition"], "RECOVERY_IN_FLIGHT")
        self.assertEqual(self.registry.inspect(bound_id)["state"], "CONSUMED")
        self.assertEqual(read_gateway_effect_count(self.effects_db), 1)

    def test_p10_13_raw_inner_permit_never_crosses_caller_surface(self) -> None:
        auth, effect = self.issue(self.candidate_a, key="surface-nonexposure")
        bound_id = auth["permit"]["payload"]["bound_permit_id"]
        inner = self.registry.trusted_inner_permit_for_test(bound_id)
        self.assertIsNotNone(inner)
        inner_signature = inner["signature"]
        self.assertNotIn("inner_permit", auth)
        self.assertNotIn("lep_permit", auth)

        client = self.start_client()
        result = self.execute(client, auth, self.candidate_a, effect, "surface-nonexposure")
        self.assertEqual(result["decision"], "EXECUTED")
        surfaces = json.dumps(
            {"authorization": auth, "http_request": client.last_request_body, "http_response": client.last_response_body},
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertNotIn(inner_signature, surfaces)
        self.assertNotIn(json.dumps(inner, sort_keys=True, separators=(",", ":")), surfaces)

    def test_p10_14_gateway_process_has_no_semantic_or_capability_signing_key(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "EXP_O_SEMANTIC_VERIFIER_SIGNING_KEY_HEX": self.semantic_key.hex(),
                "EXP_O_AUTHORITY_KERNEL_SIGNING_KEY_HEX": self.kernel_key.hex(),
            },
            clear=False,
        ):
            client = self.start_client()
        health = client.health()
        self.assertEqual(health["state"], "READY")
        self.assertNotEqual(health["pid"], os.getpid())
        self.assertFalse(health["semantic_verifier_signing_key_present"])
        self.assertFalse(health["authority_kernel_signing_key_present"])
        self.assertEqual(
            set(health["loaded_key_roles"]),
            {
                "OUTER_PERMIT_VERIFICATION_HMAC_PILOT_KEY",
                "SEMANTIC_REGISTRY_INTEGRITY_HMAC_PILOT_KEY",
                "INNER_LEP_PERMIT_VERIFICATION_HMAC_PILOT_KEY",
            },
        )

    def test_p10_15_fresh_clean_effect_executes_after_restart(self) -> None:
        auth_a, effect_a = self.issue(self.candidate_a, key="before-restart")
        client = self.start_client()
        first = self.execute(client, auth_a, self.candidate_a, effect_a, "before-restart")
        self.assertEqual(first["decision"], "EXECUTED")
        first_instance = self.harness.info["gateway_instance_id"]
        new_info = self.harness.restart()
        self.assertNotEqual(first_instance, new_info["gateway_instance_id"])

        auth_b, effect_b = self.issue(self.candidate_b, key="after-restart")
        fresh_client = self.harness.client(timeout_s=1.5)
        second = self.execute(fresh_client, auth_b, self.candidate_b, effect_b, "after-restart")
        self.assertTrue(second["authorized"])
        self.assertEqual(second["decision"], "EXECUTED")
        self.assertTrue(second["executed"])
        self.assertEqual(read_gateway_effect_count(self.effects_db), 2)


if __name__ == "__main__":
    unittest.main()
