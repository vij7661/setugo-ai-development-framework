"""EXP-O Pilot 3 single-host governed runtime slice.

This module intentionally uses only Python standard-library mechanisms. It is
an executable falsification slice, not a production distributed runtime.
"""
from __future__ import annotations

import copy
from contextlib import closing
import hashlib
import hmac
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Mapping

from runtime_authority_exp_o import evaluate_action_effect, evaluate_authority_freshness


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sign(payload: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    body = copy.deepcopy(dict(payload))
    signature = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    return {"payload": body, "signature": signature}


def _verify(envelope: Mapping[str, Any], key: bytes) -> bool:
    payload = envelope.get("payload")
    signature = envelope.get("signature")
    if not isinstance(payload, Mapping) or not isinstance(signature, str):
        return False
    expected = hmac.new(key, _canonical(dict(payload)), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def _deny(reason: str, **extra: Any) -> dict[str, Any]:
    out = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


def _effect_binding(effect: Mapping[str, Any], *, idempotency_key: str) -> dict[str, Any]:
    return {
        "idempotency_key": idempotency_key,
        "action_class": effect.get("action_class"),
        "target_resources": list(effect.get("target_resources", [])),
        "changed_files": list(effect.get("changed_files", [])),
        "base_sha": effect.get("base_sha"),
        "effect_contract_id": effect.get("effect_contract_id"),
        "destructive_effect": bool(effect.get("destructive_effect", False)),
        "provenance_trust_classes": sorted(effect.get("provenance_trust_classes", [])),
    }


class AuthorityKernel:
    """Trusted authority issuer. Agent/model output cannot mutate this state."""

    def __init__(self, signing_key: bytes) -> None:
        self._signing_key = signing_key
        self._epochs: dict[str, int] = {}
        self._revoked_capability_ids: set[str] = set()
        self._counter = 0

    @property
    def verification_key(self) -> bytes:
        return self._signing_key

    def current_epoch(self, subject_id: str) -> int:
        return self._epochs.setdefault(subject_id, 1)

    def advance_epoch(self, subject_id: str) -> int:
        self._epochs[subject_id] = self.current_epoch(subject_id) + 1
        return self._epochs[subject_id]

    def revoke(self, capability_id: str) -> None:
        self._revoked_capability_ids.add(capability_id)

    def is_revoked(self, capability_id: str) -> bool:
        return capability_id in self._revoked_capability_ids

    def issue_capability(
        self,
        *,
        subject_id: str,
        subject_key_thumbprint: str,
        issued_at_ms: int,
        expires_at_ms: int,
        freshness_class: str,
        allowed_actions: list[str],
        allowed_resources: list[str],
        effect_contract_id: str,
        base_sha: str,
        resource_fence: int | None = None,
    ) -> dict[str, Any]:
        self._counter += 1
        payload = {
            "capability_id": f"cap-{self._counter}-{uuid.uuid4().hex[:12]}",
            "subject_id": subject_id,
            "subject_key_thumbprint": subject_key_thumbprint,
            "authority_epoch": self.current_epoch(subject_id),
            "issued_at_ms": int(issued_at_ms),
            "expires_at_ms": int(expires_at_ms),
            "freshness_class": freshness_class,
            "allowed_actions": list(allowed_actions),
            "allowed_resources": list(allowed_resources),
            "effect_contract_id": effect_contract_id,
            "base_sha": base_sha,
            "resource_fence": resource_fence,
        }
        return _sign(payload, self._signing_key)

    def issue_replacement(
        self,
        old_capability: Mapping[str, Any],
        *,
        new_subject_id: str,
        new_subject_key_thumbprint: str,
        issued_at_ms: int,
        expires_at_ms: int,
        spool_reconciled: bool,
    ) -> dict[str, Any]:
        if not spool_reconciled:
            return {"issued": False, "reason": "DURABLE_SPOOL_RECONCILIATION_REQUIRED"}
        if not _verify(old_capability, self._signing_key):
            return {"issued": False, "reason": "OLD_CAPABILITY_SIGNATURE_INVALID"}
        old = dict(old_capability["payload"])
        self.revoke(str(old["capability_id"]))
        new_cap = self.issue_capability(
            subject_id=new_subject_id,
            subject_key_thumbprint=new_subject_key_thumbprint,
            issued_at_ms=issued_at_ms,
            expires_at_ms=expires_at_ms,
            freshness_class=str(old["freshness_class"]),
            allowed_actions=list(old["allowed_actions"]),
            allowed_resources=list(old["allowed_resources"]),
            effect_contract_id=str(old["effect_contract_id"]),
            base_sha=str(old["base_sha"]),
            resource_fence=old.get("resource_fence"),
        )
        return {"issued": True, "old_capability_revoked": True, "capability": new_cap}


class LocalEnforcementPoint:
    """Use-time enforcement point. Only this component can mint gateway permits."""

    def __init__(self, kernel: AuthorityKernel, permit_signing_key: bytes) -> None:
        self._kernel = kernel
        self._kernel_key = kernel.verification_key
        self._permit_key = permit_signing_key
        self._permit_counter = 0

    @property
    def gateway_verification_key(self) -> bytes:
        return self._permit_key

    def authorize(
        self,
        capability: Mapping[str, Any] | None,
        *,
        worker_id: str,
        worker_key_thumbprint: str,
        effect_contract: Mapping[str, Any],
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
        origin_available: bool,
        online_authority_confirmed: bool,
        semantic_verified: bool,
    ) -> dict[str, Any]:
        if capability is None:
            return _deny("PLATFORM_CAPABILITY_REQUIRED")
        if not _verify(capability, self._kernel_key):
            return _deny("CAPABILITY_SIGNATURE_INVALID")

        cap = dict(capability["payload"])
        capability_id = str(cap.get("capability_id", ""))
        if not capability_id or self._kernel.is_revoked(capability_id):
            return _deny("CAPABILITY_REVOKED_OR_MISSING")
        if cap.get("subject_id") != worker_id:
            return _deny("WORKER_IDENTITY_MISMATCH")
        if cap.get("subject_key_thumbprint") != worker_key_thumbprint:
            return _deny("SENDER_KEY_MISMATCH")

        try:
            cap_epoch = int(cap.get("authority_epoch"))
            current_epoch = int(self._kernel.current_epoch(worker_id))
            expires_at_ms = int(cap.get("expires_at_ms"))
            issued_at_ms = int(cap.get("issued_at_ms"))
        except (TypeError, ValueError):
            return _deny("MALFORMED_CAPABILITY_TIME_OR_EPOCH")
        if cap_epoch != current_epoch:
            return _deny("AUTHORITY_EPOCH_STALE", capability_epoch=cap_epoch, current_epoch=current_epoch)
        if now_ms > expires_at_ms:
            return _deny("CAPABILITY_EXPIRED")

        if cap.get("effect_contract_id") != effect_contract.get("effect_contract_id"):
            return _deny("CAPABILITY_EFFECT_CONTRACT_MISMATCH")
        if cap.get("base_sha") != effect_contract.get("base_sha"):
            return _deny("CAPABILITY_BASE_SHA_MISMATCH")
        if effect.get("action_class") not in set(cap.get("allowed_actions", [])):
            return _deny("CAPABILITY_ACTION_SCOPE_EXCEEDED")
        for resource in list(effect.get("target_resources", [])) + list(effect.get("changed_files", [])):
            if resource not in set(cap.get("allowed_resources", [])):
                return _deny("CAPABILITY_RESOURCE_SCOPE_EXCEEDED", resource=resource)

        local_snapshot = {
            "age_ms": now_ms - issued_at_ms,
            "authority_epoch": current_epoch,
            "minimum_resource_fence": effect_contract.get("minimum_resource_fence"),
        }
        freshness = evaluate_authority_freshness(
            cap,
            local_snapshot,
            origin_available=origin_available,
            online_authority_confirmed=online_authority_confirmed,
        )
        if not freshness.get("authorized", False):
            return _deny(str(freshness.get("reason", "AUTHORITY_FRESHNESS_DENIED")), freshness=freshness)

        effect_check = evaluate_action_effect(effect_contract, effect, semantic_verified=semantic_verified)
        if not effect_check.get("authorized", False):
            return _deny(str(effect_check.get("reason", effect_check.get("decision", "EFFECT_DENIED"))), effect_check=effect_check)
        if not idempotency_key:
            return _deny("IDEMPOTENCY_KEY_REQUIRED")

        self._permit_counter += 1
        binding = _effect_binding(effect, idempotency_key=idempotency_key)
        permit_payload = {
            "permit_id": f"permit-{self._permit_counter}-{uuid.uuid4().hex[:12]}",
            "capability_id": capability_id,
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "authority_epoch": current_epoch,
            "effect_contract_id": effect_contract.get("effect_contract_id"),
            "effect_digest": _digest(binding),
            "idempotency_key": idempotency_key,
            "issued_at_ms": int(now_ms),
            "expires_at_ms": int(now_ms) + 5_000,
        }
        return {
            "authorized": True,
            "decision": "PERMIT_ISSUED",
            "permit": _sign(permit_payload, self._permit_key),
            "freshness": freshness,
            "effect_check": effect_check,
        }


class DurableEvidenceSpool:
    """SQLite-backed hash-linked evidence spool."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_records (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    record_hash TEXT NOT NULL
                )
                """
            )

    def append(self, record_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        payload_json = _canonical(dict(payload)).decode("utf-8")
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT sequence, record_hash FROM evidence_records ORDER BY sequence DESC LIMIT 1").fetchone()
            next_sequence = 1 if row is None else int(row["sequence"]) + 1
            previous_hash = "GENESIS" if row is None else str(row["record_hash"])
            core = {
                "sequence": next_sequence,
                "record_type": record_type,
                "payload": json.loads(payload_json),
                "previous_hash": previous_hash,
            }
            record_hash = _digest(core)
            conn.execute(
                "INSERT INTO evidence_records(sequence, record_type, payload_json, previous_hash, record_hash) VALUES (?, ?, ?, ?, ?)",
                (next_sequence, record_type, payload_json, previous_hash, record_hash),
            )
            conn.commit()
        return {**core, "record_hash": record_hash}

    def records(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT sequence, record_type, payload_json, previous_hash, record_hash FROM evidence_records ORDER BY sequence"
            ).fetchall()
        return [
            {
                "sequence": int(row["sequence"]),
                "record_type": str(row["record_type"]),
                "payload": json.loads(str(row["payload_json"])),
                "previous_hash": str(row["previous_hash"]),
                "record_hash": str(row["record_hash"]),
            }
            for row in rows
        ]

    def verify(self) -> dict[str, Any]:
        previous_hash = "GENESIS"
        expected_sequence = 1
        for record in self.records():
            if record["sequence"] != expected_sequence:
                return {"verified": False, "state": "SEQUENCE_GAP_OR_REORDER"}
            if record["previous_hash"] != previous_hash:
                return {"verified": False, "state": "PREVIOUS_HASH_MISMATCH"}
            core = {
                "sequence": record["sequence"],
                "record_type": record["record_type"],
                "payload": record["payload"],
                "previous_hash": record["previous_hash"],
            }
            expected_hash = _digest(core)
            if not hmac.compare_digest(record["record_hash"], expected_hash):
                return {"verified": False, "state": "RECORD_HASH_MISMATCH"}
            previous_hash = expected_hash
            expected_sequence += 1
        return {"verified": True, "state": "CHAIN_VERIFIED", "record_count": expected_sequence - 1}

    def result_for_idempotency_key(self, idempotency_key: str) -> dict[str, Any] | None:
        for record in reversed(self.records()):
            if record["record_type"] != "EXECUTION_RESULT":
                continue
            payload = record["payload"]
            if payload.get("idempotency_key") == idempotency_key:
                return payload
        return None


class McpGateway:
    """Tool-effect gateway requiring a LEP-signed exact-effect permit."""

    def __init__(self, permit_verification_key: bytes, db_path: str | Path) -> None:
        self._permit_key = permit_verification_key
        self.db_path = str(db_path)
        self.reachable = True
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS authoritative_effects (
                    idempotency_key TEXT PRIMARY KEY,
                    effect_digest TEXT NOT NULL,
                    effect_id TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )

    def effect_count(self) -> int:
        with closing(self._connect()) as conn:
            return int(conn.execute("SELECT COUNT(*) FROM authoritative_effects").fetchone()[0])

    def execute(
        self,
        *,
        permit: Mapping[str, Any] | None,
        worker_id: str,
        worker_key_thumbprint: str,
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
    ) -> dict[str, Any]:
        if not self.reachable:
            return _deny("MCP_GATEWAY_UNREACHABLE")
        if permit is None:
            return _deny("LEP_PERMIT_REQUIRED")
        if not _verify(permit, self._permit_key):
            return _deny("LEP_PERMIT_SIGNATURE_INVALID")

        permit_payload = dict(permit["payload"])
        try:
            expires_at_ms = int(permit_payload.get("expires_at_ms"))
        except (TypeError, ValueError):
            return _deny("MALFORMED_PERMIT_EXPIRY")
        if now_ms > expires_at_ms:
            return _deny("LEP_PERMIT_EXPIRED")
        if permit_payload.get("worker_id") != worker_id:
            return _deny("PERMIT_WORKER_ID_MISMATCH")
        if permit_payload.get("worker_key_thumbprint") != worker_key_thumbprint:
            return _deny("PERMIT_SENDER_KEY_MISMATCH")
        if permit_payload.get("idempotency_key") != idempotency_key:
            return _deny("PERMIT_IDEMPOTENCY_BINDING_MISMATCH")

        binding = _effect_binding(effect, idempotency_key=idempotency_key)
        effect_digest = _digest(binding)
        if permit_payload.get("effect_digest") != effect_digest:
            return _deny("PERMIT_EFFECT_BINDING_MISMATCH")

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT effect_digest, effect_id, result_json FROM authoritative_effects WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                if str(existing["effect_digest"]) != effect_digest:
                    conn.rollback()
                    return _deny("IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_EFFECT")
                result = json.loads(str(existing["result_json"]))
                conn.commit()
                return {"authorized": True, "decision": "IDEMPOTENT_REPLAY", "executed": False, "replayed": True, "result": result}

            effect_id = hashlib.sha256(f"{idempotency_key}:{effect_digest}".encode()).hexdigest()[:24]
            result = {
                "effect_id": effect_id,
                "status": "EXECUTED",
                "action_class": effect.get("action_class"),
                "target_resources": list(effect.get("target_resources", [])),
            }
            conn.execute(
                "INSERT INTO authoritative_effects(idempotency_key, effect_digest, effect_id, result_json) VALUES (?, ?, ?, ?)",
                (idempotency_key, effect_digest, effect_id, _canonical(result).decode("utf-8")),
            )
            conn.commit()
        return {"authorized": True, "decision": "EXECUTED", "executed": True, "replayed": False, "result": result}


class SimulatedWorkerCrash(RuntimeError):
    pass


class AgentWorker:
    """Worker that can request effects but owns neither authority nor permit keys."""

    def __init__(
        self,
        *,
        worker_id: str,
        worker_key_thumbprint: str,
        lep: LocalEnforcementPoint,
        gateway: McpGateway,
        spool: DurableEvidenceSpool,
    ) -> None:
        self.worker_id = worker_id
        self.worker_key_thumbprint = worker_key_thumbprint
        self._lep = lep
        self._gateway = gateway
        self._spool = spool

    def request_effect(
        self,
        *,
        capability: Mapping[str, Any] | None,
        effect_contract: Mapping[str, Any],
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
        origin_available: bool,
        online_authority_confirmed: bool,
        semantic_verified: bool,
        crash_after_gateway: bool = False,
    ) -> dict[str, Any]:
        self._spool.append(
            "EXECUTION_INTENT",
            {
                "worker_id": self.worker_id,
                "idempotency_key": idempotency_key,
                "effect_digest": _digest(_effect_binding(effect, idempotency_key=idempotency_key)),
            },
        )
        auth = self._lep.authorize(
            capability,
            worker_id=self.worker_id,
            worker_key_thumbprint=self.worker_key_thumbprint,
            effect_contract=effect_contract,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=now_ms,
            origin_available=origin_available,
            online_authority_confirmed=online_authority_confirmed,
            semantic_verified=semantic_verified,
        )
        if not auth.get("authorized", False):
            self._spool.append(
                "EXECUTION_DENIED",
                {"worker_id": self.worker_id, "idempotency_key": idempotency_key, "reason": auth.get("reason")},
            )
            return auth

        gateway_result = self._gateway.execute(
            permit=auth["permit"],
            worker_id=self.worker_id,
            worker_key_thumbprint=self.worker_key_thumbprint,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=now_ms,
        )
        if crash_after_gateway and gateway_result.get("authorized", False):
            raise SimulatedWorkerCrash("worker crashed after gateway effect before local result append")

        self._spool.append(
            "EXECUTION_RESULT",
            {
                "worker_id": self.worker_id,
                "idempotency_key": idempotency_key,
                "gateway_decision": gateway_result.get("decision"),
                "gateway_authorized": bool(gateway_result.get("authorized", False)),
                "result": gateway_result.get("result"),
            },
        )
        return gateway_result

    def reconcile_and_retry(self, **kwargs: Any) -> dict[str, Any]:
        idempotency_key = str(kwargs["idempotency_key"])
        existing = self._spool.result_for_idempotency_key(idempotency_key)
        if existing is not None:
            return {
                "authorized": bool(existing.get("gateway_authorized", False)),
                "decision": "LOCAL_RESULT_ALREADY_PRESENT",
                "result": existing.get("result"),
            }
        self._spool.append("RECONCILIATION_STARTED", {"worker_id": self.worker_id, "idempotency_key": idempotency_key})
        result = self.request_effect(**kwargs)
        self._spool.append(
            "RECONCILIATION_COMPLETED",
            {"worker_id": self.worker_id, "idempotency_key": idempotency_key, "decision": result.get("decision")},
        )
        return result
