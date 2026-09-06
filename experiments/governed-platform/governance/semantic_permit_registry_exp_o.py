"""EXP-O Pilot 10 durable cross-process semantic-bound permit registry.

This is pilot infrastructure, not production key management. It preserves the
Pilot 9 rule that callers receive only an outer semantic-bound permit while the
raw historical LEP permit remains on the platform side of the authority
boundary.
"""
from __future__ import annotations

import copy
from contextlib import closing
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
import uuid
from typing import Any, Callable, Mapping

from runtime_slice_exp_o import LocalEnforcementPoint, McpGateway
from semantic_verification_binding_exp_o import digest, semantic_effect_view


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sign(payload: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    body = copy.deepcopy(dict(payload))
    return {"payload": body, "signature": hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()}


def _verify(envelope: Mapping[str, Any] | None, key: bytes) -> bool:
    if not isinstance(envelope, Mapping):
        return False
    payload = envelope.get("payload")
    signature = envelope.get("signature")
    if not isinstance(payload, Mapping) or not isinstance(signature, str):
        return False
    expected = hmac.new(key, _canonical(dict(payload)), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def _deny(reason: str, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


REGISTRY_BINDING_FIELDS = (
    "bound_permit_id",
    "inner_permit_digest",
    "semantic_payload_digest",
    "effect_digest",
    "semantic_verification_digest",
    "capability_digest",
    "worker_id",
    "worker_key_thumbprint",
    "effect_contract_id",
    "base_sha",
    "idempotency_key",
)


class DurableSemanticPermitRegistry:
    """Integrity-protected SQLite registry for raw inner LEP permits.

    The registry exposes sanitized state by default. `begin_use` is the only
    normal path that resolves the raw inner permit, and that method is intended
    for trusted gateway-side code. A second durable table prevents an external
    idempotency key from being rebound to different semantic content even
    though the historical MCP gateway predates semantic-payload digests.
    """

    def __init__(self, db_path: str | Path, integrity_key: bytes) -> None:
        if not integrity_key:
            raise ValueError("registry integrity key must not be empty")
        self.db_path = str(db_path)
        self._key = bytes(integrity_key)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_permits (
                    bound_permit_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL,
                    integrity_tag TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_idempotency_bindings (
                    worker_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    semantic_effect_digest TEXT NOT NULL,
                    bound_permit_id TEXT NOT NULL,
                    PRIMARY KEY(worker_id, idempotency_key)
                )
                """
            )

    def _tag(self, record: Mapping[str, Any]) -> str:
        return hmac.new(self._key, _canonical(dict(record)), hashlib.sha256).hexdigest()

    def _read_verified(self, conn: sqlite3.Connection, bound_permit_id: str) -> tuple[dict[str, Any] | None, str | None]:
        row = conn.execute(
            "SELECT bound_permit_id, record_json, integrity_tag FROM semantic_permits WHERE bound_permit_id = ?",
            (bound_permit_id,),
        ).fetchone()
        if row is None:
            return None, "SEMANTIC_REGISTRY_RECORD_MISSING"
        try:
            record = json.loads(str(row["record_json"]))
        except Exception:
            return None, "SEMANTIC_REGISTRY_RECORD_MALFORMED"
        if not isinstance(record, dict) or record.get("bound_permit_id") != bound_permit_id:
            return None, "SEMANTIC_REGISTRY_RECORD_BINDING_INVALID"
        expected = self._tag(record)
        if not hmac.compare_digest(str(row["integrity_tag"]), expected):
            return None, "SEMANTIC_REGISTRY_INTEGRITY_INVALID"
        return record, None

    def _write(self, conn: sqlite3.Connection, record: Mapping[str, Any]) -> None:
        payload = dict(record)
        conn.execute(
            "UPDATE semantic_permits SET record_json = ?, integrity_tag = ? WHERE bound_permit_id = ?",
            (_canonical(payload).decode("utf-8"), self._tag(payload), str(payload["bound_permit_id"])),
        )

    def _claim_semantic_idempotency(self, conn: sqlite3.Connection, record: Mapping[str, Any]) -> str | None:
        worker_id = str(record["worker_id"])
        idempotency_key = str(record["idempotency_key"])
        effect_digest = str(record["effect_digest"])
        bound_permit_id = str(record["bound_permit_id"])
        row = conn.execute(
            "SELECT semantic_effect_digest, bound_permit_id FROM semantic_idempotency_bindings WHERE worker_id = ? AND idempotency_key = ?",
            (worker_id, idempotency_key),
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO semantic_idempotency_bindings(worker_id, idempotency_key, semantic_effect_digest, bound_permit_id) VALUES (?, ?, ?, ?)",
                (worker_id, idempotency_key, effect_digest, bound_permit_id),
            )
            return None
        if str(row["semantic_effect_digest"]) != effect_digest:
            return "SEMANTIC_IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_EFFECT"
        if str(row["bound_permit_id"]) != bound_permit_id:
            return "SEMANTIC_IDEMPOTENCY_KEY_ALREADY_BOUND_TO_DIFFERENT_PERMIT"
        return None

    def issue(self, record: Mapping[str, Any]) -> dict[str, Any]:
        payload = copy.deepcopy(dict(record))
        for field in REGISTRY_BINDING_FIELDS:
            if field not in payload or payload[field] in (None, "", []):
                raise ValueError(f"registry record missing required binding {field}")
        inner = payload.get("inner_permit")
        if not isinstance(inner, Mapping):
            raise ValueError("raw inner permit required for trusted registry record")
        if digest(dict(inner)) != payload.get("inner_permit_digest"):
            raise ValueError("inner permit digest mismatch")
        payload["state"] = "ISSUED"
        payload["authoritative_result_digest"] = None
        payload["use_attempts"] = 0
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    "INSERT INTO semantic_permits(bound_permit_id, record_json, integrity_tag) VALUES (?, ?, ?)",
                    (
                        str(payload["bound_permit_id"]),
                        _canonical(payload).decode("utf-8"),
                        self._tag(payload),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                raise ValueError("duplicate bound_permit_id") from exc
            conn.commit()
        return self.inspect(str(payload["bound_permit_id"]))

    def inspect(self, bound_permit_id: str) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            record, error = self._read_verified(conn, bound_permit_id)
        if error:
            return {"verified": False, "reason": error, "bound_permit_id": bound_permit_id}
        assert record is not None
        return {
            "verified": True,
            "bound_permit_id": bound_permit_id,
            "state": record.get("state"),
            "inner_permit_digest": record.get("inner_permit_digest"),
            "semantic_payload_digest": record.get("semantic_payload_digest"),
            "effect_digest": record.get("effect_digest"),
            "capability_digest": record.get("capability_digest"),
            "idempotency_key": record.get("idempotency_key"),
            "authoritative_result_digest": record.get("authoritative_result_digest"),
            "use_attempts": record.get("use_attempts"),
        }

    def begin_use(self, bound_permit_id: str, *, expected_bindings: Mapping[str, Any]) -> dict[str, Any]:
        """Atomically resolve exact registry state and durably enter IN_FLIGHT."""
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            record, error = self._read_verified(conn, bound_permit_id)
            if error:
                conn.rollback()
                return {"resolved": False, "reason": error}
            assert record is not None
            for field in REGISTRY_BINDING_FIELDS:
                if field == "bound_permit_id":
                    expected = bound_permit_id
                else:
                    expected = expected_bindings.get(field)
                if record.get(field) != expected:
                    conn.rollback()
                    return {"resolved": False, "reason": f"SEMANTIC_REGISTRY_BINDING_MISMATCH:{field}"}
            inner = record.get("inner_permit")
            if not isinstance(inner, Mapping) or digest(dict(inner)) != record.get("inner_permit_digest"):
                conn.rollback()
                return {"resolved": False, "reason": "SEMANTIC_REGISTRY_INNER_PERMIT_DIGEST_MISMATCH"}

            state = record.get("state")
            if state == "CONSUMED":
                conn.commit()
                return {
                    "resolved": False,
                    "reason": "SEMANTIC_BOUND_PERMIT_CONSUMED",
                    "state": "CONSUMED",
                    "authoritative_result_digest": record.get("authoritative_result_digest"),
                }
            if state not in {"ISSUED", "IN_FLIGHT"}:
                conn.rollback()
                return {"resolved": False, "reason": "SEMANTIC_REGISTRY_STATE_INVALID"}

            idempotency_error = self._claim_semantic_idempotency(conn, record)
            if idempotency_error:
                conn.rollback()
                return {"resolved": False, "reason": idempotency_error, "state": state}

            disposition = "FIRST_USE" if state == "ISSUED" else "RECOVERY_IN_FLIGHT"
            record["state"] = "IN_FLIGHT"
            record["use_attempts"] = int(record.get("use_attempts", 0)) + 1
            self._write(conn, record)
            conn.commit()
            return {
                "resolved": True,
                "state": "IN_FLIGHT",
                "disposition": disposition,
                "inner_permit": copy.deepcopy(dict(inner)),
                "inner_permit_digest": record.get("inner_permit_digest"),
                "use_attempts": record.get("use_attempts"),
            }

    def finalize(self, bound_permit_id: str, *, authoritative_result_digest: str) -> dict[str, Any]:
        if not authoritative_result_digest:
            raise ValueError("authoritative result digest required")
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            record, error = self._read_verified(conn, bound_permit_id)
            if error:
                conn.rollback()
                return {"finalized": False, "reason": error}
            assert record is not None
            state = record.get("state")
            if state == "CONSUMED":
                if record.get("authoritative_result_digest") == authoritative_result_digest:
                    conn.commit()
                    return {"finalized": True, "state": "CONSUMED", "replayed_finalization": True}
                conn.rollback()
                return {"finalized": False, "reason": "SEMANTIC_REGISTRY_RESULT_DIGEST_CONFLICT"}
            if state != "IN_FLIGHT":
                conn.rollback()
                return {"finalized": False, "reason": "SEMANTIC_REGISTRY_FINALIZE_REQUIRES_IN_FLIGHT"}
            record["state"] = "CONSUMED"
            record["authoritative_result_digest"] = authoritative_result_digest
            self._write(conn, record)
            conn.commit()
            return {"finalized": True, "state": "CONSUMED", "replayed_finalization": False}

    def trusted_inner_permit_for_test(self, bound_permit_id: str) -> dict[str, Any] | None:
        """Trusted-harness-only inspection used to prove caller-surface non-exposure."""
        with closing(self._connect()) as conn:
            record, error = self._read_verified(conn, bound_permit_id)
        if error or record is None or not isinstance(record.get("inner_permit"), Mapping):
            return None
        return copy.deepcopy(dict(record["inner_permit"]))


class DurableSemanticBoundLocalEnforcementPoint:
    """Pilot 10 LEP-side semantic verifier and durable permit issuer."""

    def __init__(
        self,
        lep: LocalEnforcementPoint,
        *,
        semantic_verification_key: bytes,
        outer_permit_signing_key: bytes,
        registry: DurableSemanticPermitRegistry,
    ) -> None:
        self._lep = lep
        self._semantic_key = bytes(semantic_verification_key)
        self._outer_key = bytes(outer_permit_signing_key)
        self._registry = registry
        self._counter = 0

    @property
    def outer_permit_verification_key(self) -> bytes:
        return self._outer_key

    def authorize(
        self,
        capability: Mapping[str, Any] | None,
        *,
        candidate_payload: Mapping[str, Any],
        semantic_verification: Mapping[str, Any] | None,
        worker_id: str,
        worker_key_thumbprint: str,
        effect_contract: Mapping[str, Any],
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
        origin_available: bool,
        online_authority_confirmed: bool,
    ) -> dict[str, Any]:
        candidate_digest = digest(dict(candidate_payload))
        if effect.get("semantic_payload_digest") != candidate_digest:
            return _deny("SEMANTIC_CANDIDATE_EFFECT_DIGEST_MISMATCH")
        if not _verify(semantic_verification, self._semantic_key):
            return _deny("SIGNED_SEMANTIC_VERIFICATION_REQUIRED")

        evidence = dict(semantic_verification["payload"])
        effect_view = semantic_effect_view(effect)
        expected_evidence = {
            "semantic_payload_digest": candidate_digest,
            "effect_digest": digest(effect_view),
            "effect_contract_id": effect_view["effect_contract_id"],
            "base_sha": effect_view["base_sha"],
            "action_class": effect_view["action_class"],
            "target_resources": effect_view["target_resources"],
            "changed_files": effect_view["changed_files"],
        }
        if evidence.get("verified") is not True:
            return _deny("SEMANTIC_VERIFICATION_NOT_TRUE")
        for field, value in expected_evidence.items():
            if evidence.get(field) != value:
                return _deny(f"SEMANTIC_VERIFICATION_BINDING_MISMATCH:{field}")

        inner = self._lep.authorize(
            capability,
            worker_id=worker_id,
            worker_key_thumbprint=worker_key_thumbprint,
            effect_contract=effect_contract,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=now_ms,
            origin_available=origin_available,
            online_authority_confirmed=online_authority_confirmed,
            semantic_verified=True,
        )
        if not inner.get("authorized", False) or not isinstance(inner.get("permit"), Mapping):
            return inner

        self._counter += 1
        bound_permit_id = f"p10-semantic-permit-{self._counter}-{uuid.uuid4().hex[:12]}"
        inner_permit = dict(inner["permit"])
        binding = {
            "bound_permit_id": bound_permit_id,
            "inner_permit_digest": digest(inner_permit),
            "semantic_payload_digest": candidate_digest,
            "effect_digest": digest(effect_view),
            "semantic_verification_digest": digest(semantic_verification),
            "capability_digest": digest(capability),
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect_contract_id": effect.get("effect_contract_id"),
            "base_sha": effect.get("base_sha"),
            "idempotency_key": idempotency_key,
        }
        self._registry.issue({**binding, "inner_permit": inner_permit})
        return {
            "authorized": True,
            "decision": "DURABLE_SEMANTIC_BOUND_PERMIT_ISSUED",
            "permit": _sign(copy.deepcopy(binding), self._outer_key),
            "registry_state": "ISSUED",
            "inner_lep_decision": inner.get("decision"),
            "semantic_verification_id": evidence.get("verification_id"),
        }


class ProcessSemanticBoundGateway:
    """Gateway-side resolver for a separate process/HTTP boundary."""

    def __init__(
        self,
        gateway: McpGateway,
        *,
        outer_permit_verification_key: bytes,
        registry: DurableSemanticPermitRegistry,
    ) -> None:
        self._gateway = gateway
        self._outer_key = bytes(outer_permit_verification_key)
        self._registry = registry

    def execute(
        self,
        *,
        permit: Mapping[str, Any] | None,
        candidate_payload: Mapping[str, Any],
        worker_id: str,
        worker_key_thumbprint: str,
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
        after_inflight_hook: Callable[[], None] | None = None,
        after_gateway_hook: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        if not _verify(permit, self._outer_key):
            return _deny("SEMANTIC_BOUND_OUTER_PERMIT_INVALID")
        payload = dict(permit["payload"])
        candidate_digest = digest(dict(candidate_payload))
        if effect.get("semantic_payload_digest") != candidate_digest:
            return _deny("SEMANTIC_CANDIDATE_EFFECT_DIGEST_MISMATCH")
        effect_digest = digest(semantic_effect_view(effect))
        checks = {
            "semantic_payload_digest": candidate_digest,
            "effect_digest": effect_digest,
            "idempotency_key": idempotency_key,
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect_contract_id": effect.get("effect_contract_id"),
            "base_sha": effect.get("base_sha"),
        }
        for field, value in checks.items():
            if payload.get(field) != value:
                return _deny(f"SEMANTIC_BOUND_OUTER_PERMIT_MISMATCH:{field}")

        bound_permit_id = str(payload.get("bound_permit_id", ""))
        if not bound_permit_id:
            return _deny("SEMANTIC_BOUND_PERMIT_ID_REQUIRED")
        expected_registry = {field: payload.get(field) for field in REGISTRY_BINDING_FIELDS if field != "bound_permit_id"}
        resolved = self._registry.begin_use(bound_permit_id, expected_bindings=expected_registry)
        if not resolved.get("resolved", False):
            return _deny(str(resolved.get("reason", "SEMANTIC_REGISTRY_RESOLUTION_DENIED")), registry_state=resolved.get("state"))

        if after_inflight_hook is not None:
            after_inflight_hook()

        gateway_result = self._gateway.execute(
            permit=resolved["inner_permit"],
            worker_id=worker_id,
            worker_key_thumbprint=worker_key_thumbprint,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=now_ms,
        )
        if after_gateway_hook is not None:
            after_gateway_hook(gateway_result)

        authoritative_result = gateway_result.get("result") if isinstance(gateway_result.get("result"), Mapping) else gateway_result
        result_digest = digest(authoritative_result)
        finalized = self._registry.finalize(bound_permit_id, authoritative_result_digest=result_digest)
        if not finalized.get("finalized", False):
            return _deny(
                str(finalized.get("reason", "SEMANTIC_REGISTRY_FINALIZATION_FAILED")),
                authoritative_gateway_result=gateway_result,
                registry_disposition=resolved.get("disposition"),
            )
        return {
            **gateway_result,
            "registry_disposition": resolved.get("disposition"),
            "registry_state": "CONSUMED",
            "bound_permit_id": bound_permit_id,
            "inner_permit_digest": resolved.get("inner_permit_digest"),
        }

    def effect_count(self) -> int:
        return self._gateway.effect_count()
