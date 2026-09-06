"""EXP-O Pilot 11 ownership fencing for process-separated semantic permits.

This layer leaves finalized Pilot 10 source intact. It places an integrity-
protected owner/epoch record in the same SQLite database as Pilot 10's durable
semantic permit, then atomically resolves and finalizes both records so stale
owners cannot exploit a check/use race.
"""
from __future__ import annotations

import copy
from contextlib import closing
import hashlib
import hmac
import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from semantic_permit_registry_exp_o import (
    DurableSemanticBoundLocalEnforcementPoint,
    DurableSemanticPermitRegistry,
    REGISTRY_BINDING_FIELDS,
    _verify,
)
from semantic_verification_binding_exp_o import digest, semantic_effect_view


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _deny(reason: str, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


class SemanticPermitLeaseRegistry:
    """One-owner-per-epoch fencing registry co-transactional with Pilot 10."""

    def __init__(self, db_path: str | Path, integrity_key: bytes, p10_registry: DurableSemanticPermitRegistry) -> None:
        if not integrity_key:
            raise ValueError("lease integrity key must not be empty")
        self.db_path = str(db_path)
        self._key = bytes(integrity_key)
        self._p10 = p10_registry
        if Path(self.db_path).resolve() != Path(self._p10.db_path).resolve():
            raise ValueError("Pilot 11 lease and Pilot 10 semantic registry must share one SQLite database")
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_permit_leases (
                    bound_permit_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL,
                    integrity_tag TEXT NOT NULL
                )
                """
            )

    def _tag(self, record: Mapping[str, Any]) -> str:
        return hmac.new(self._key, _canonical(dict(record)), hashlib.sha256).hexdigest()

    def _read(self, conn: sqlite3.Connection, bound_permit_id: str) -> tuple[dict[str, Any] | None, str | None]:
        row = conn.execute(
            "SELECT record_json, integrity_tag FROM semantic_permit_leases WHERE bound_permit_id = ?",
            (bound_permit_id,),
        ).fetchone()
        if row is None:
            return None, "SEMANTIC_LEASE_RECORD_MISSING"
        try:
            record = json.loads(str(row["record_json"]))
        except Exception:
            return None, "SEMANTIC_LEASE_RECORD_MALFORMED"
        if not isinstance(record, dict) or record.get("bound_permit_id") != bound_permit_id:
            return None, "SEMANTIC_LEASE_RECORD_BINDING_INVALID"
        if not hmac.compare_digest(str(row["integrity_tag"]), self._tag(record)):
            return None, "SEMANTIC_LEASE_INTEGRITY_INVALID"
        return record, None

    def _write(self, conn: sqlite3.Connection, record: Mapping[str, Any]) -> None:
        payload = copy.deepcopy(dict(record))
        conn.execute(
            "UPDATE semantic_permit_leases SET record_json = ?, integrity_tag = ? WHERE bound_permit_id = ?",
            (_canonical(payload).decode("utf-8"), self._tag(payload), str(payload["bound_permit_id"])),
        )

    def _validate_bindings(self, record: Mapping[str, Any], bound_permit_id: str, expected_bindings: Mapping[str, Any]) -> str | None:
        for field in REGISTRY_BINDING_FIELDS:
            expected = bound_permit_id if field == "bound_permit_id" else expected_bindings.get(field)
            if record.get(field) != expected:
                return f"SEMANTIC_LEASE_BINDING_MISMATCH:{field}"
        return None

    def register_issued(self, outer_permit_payload: Mapping[str, Any]) -> dict[str, Any]:
        payload = copy.deepcopy(dict(outer_permit_payload))
        for field in REGISTRY_BINDING_FIELDS:
            if payload.get(field) in (None, "", []):
                raise ValueError(f"lease record missing binding {field}")
        bound_id = str(payload["bound_permit_id"])
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            p10, p10_error = self._p10._read_verified(conn, bound_id)
            if p10_error or p10 is None or p10.get("state") != "ISSUED":
                conn.rollback()
                raise ValueError("underlying semantic permit must exist in ISSUED state")
            record = {
                **{field: copy.deepcopy(payload[field]) for field in REGISTRY_BINDING_FIELDS},
                "state": "ISSUED",
                "lease_owner_gateway_instance_id": None,
                "lease_epoch": 0,
                "authoritative_result_digest": None,
            }
            try:
                conn.execute(
                    "INSERT INTO semantic_permit_leases(bound_permit_id, record_json, integrity_tag) VALUES (?, ?, ?)",
                    (bound_id, _canonical(record).decode("utf-8"), self._tag(record)),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                raise ValueError("duplicate lease record") from exc
            conn.commit()
        return self.inspect(bound_id)

    def inspect(self, bound_permit_id: str) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            record, error = self._read(conn, bound_permit_id)
        if error:
            return {"verified": False, "reason": error, "bound_permit_id": bound_permit_id}
        assert record is not None
        return {
            "verified": True,
            "bound_permit_id": bound_permit_id,
            "state": record["state"],
            "lease_owner_gateway_instance_id": record["lease_owner_gateway_instance_id"],
            "lease_epoch": int(record["lease_epoch"]),
            "semantic_payload_digest": record["semantic_payload_digest"],
            "effect_digest": record["effect_digest"],
            "idempotency_key": record["idempotency_key"],
            "authoritative_result_digest": record["authoritative_result_digest"],
        }

    def resolve_for_gateway(
        self,
        bound_permit_id: str,
        *,
        gateway_instance_id: str,
        expected_bindings: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Atomically acquire/take over ownership and resolve P10's inner permit."""
        if not gateway_instance_id:
            return {"resolved": False, "reason": "GATEWAY_INSTANCE_ID_REQUIRED"}
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            lease, lease_error = self._read(conn, bound_permit_id)
            if lease_error:
                conn.rollback()
                return {"resolved": False, "reason": lease_error}
            assert lease is not None
            binding_error = self._validate_bindings(lease, bound_permit_id, expected_bindings)
            if binding_error:
                conn.rollback()
                return {"resolved": False, "reason": binding_error}

            p10, p10_error = self._p10._read_verified(conn, bound_permit_id)
            if p10_error or p10 is None:
                conn.rollback()
                return {"resolved": False, "reason": p10_error or "SEMANTIC_REGISTRY_RECORD_MISSING"}
            inner = p10.get("inner_permit")
            if not isinstance(inner, Mapping) or digest(dict(inner)) != p10.get("inner_permit_digest"):
                conn.rollback()
                return {"resolved": False, "reason": "SEMANTIC_REGISTRY_INNER_PERMIT_DIGEST_MISMATCH"}

            state = lease.get("state")
            owner = lease.get("lease_owner_gateway_instance_id")
            epoch = int(lease.get("lease_epoch", 0))
            if state == "CONSUMED" or p10.get("state") == "CONSUMED":
                conn.commit()
                return {
                    "resolved": False,
                    "reason": "SEMANTIC_BOUND_PERMIT_CONSUMED",
                    "state": "CONSUMED",
                    "lease_owner_gateway_instance_id": owner,
                    "lease_epoch": epoch,
                }

            if state == "ISSUED":
                if p10.get("state") != "ISSUED":
                    conn.rollback()
                    return {"resolved": False, "reason": "SEMANTIC_FIRST_OWNER_REQUIRES_UNDERLYING_ISSUED"}
                idem_error = self._p10._claim_semantic_idempotency(conn, p10)
                if idem_error:
                    lease["state"] = "CONSUMED"
                    lease["authoritative_result_digest"] = "DENIED_BEFORE_INNER_EFFECT"
                    self._write(conn, lease)
                    conn.commit()
                    return {"resolved": False, "reason": idem_error, "state": "CONSUMED"}
                new_epoch = epoch + 1
                lease["state"] = "IN_FLIGHT"
                lease["lease_owner_gateway_instance_id"] = gateway_instance_id
                lease["lease_epoch"] = new_epoch
                p10["state"] = "IN_FLIGHT"
                p10["use_attempts"] = int(p10.get("use_attempts", 0)) + 1
                self._write(conn, lease)
                self._p10._write(conn, p10)
                conn.commit()
                return {
                    "resolved": True,
                    "disposition": "FIRST_OWNER",
                    "registry_disposition": "FIRST_USE",
                    "lease_owner_gateway_instance_id": gateway_instance_id,
                    "lease_epoch": new_epoch,
                    "inner_permit": copy.deepcopy(dict(inner)),
                    "inner_permit_digest": p10.get("inner_permit_digest"),
                }

            if state != "IN_FLIGHT":
                conn.rollback()
                return {"resolved": False, "reason": "SEMANTIC_LEASE_STATE_INVALID"}
            if owner == gateway_instance_id:
                conn.commit()
                return {
                    "resolved": False,
                    "reason": "SEMANTIC_IN_FLIGHT_ALREADY_OWNED",
                    "state": "IN_FLIGHT",
                    "lease_owner_gateway_instance_id": owner,
                    "lease_epoch": epoch,
                }
            if p10.get("state") != "IN_FLIGHT":
                conn.rollback()
                return {"resolved": False, "reason": "SEMANTIC_TAKEOVER_REQUIRES_UNDERLYING_IN_FLIGHT"}
            idem_error = self._p10._claim_semantic_idempotency(conn, p10)
            if idem_error:
                conn.rollback()
                return {"resolved": False, "reason": idem_error, "state": "IN_FLIGHT"}

            new_epoch = epoch + 1
            old_owner = owner
            lease["lease_owner_gateway_instance_id"] = gateway_instance_id
            lease["lease_epoch"] = new_epoch
            p10["use_attempts"] = int(p10.get("use_attempts", 0)) + 1
            self._write(conn, lease)
            self._p10._write(conn, p10)
            conn.commit()
            return {
                "resolved": True,
                "disposition": "RESTART_TAKEOVER",
                "registry_disposition": "RECOVERY_IN_FLIGHT",
                "lease_owner_gateway_instance_id": gateway_instance_id,
                "previous_owner_gateway_instance_id": old_owner,
                "lease_epoch": new_epoch,
                "inner_permit": copy.deepcopy(dict(inner)),
                "inner_permit_digest": p10.get("inner_permit_digest"),
            }

    def finalize_both(
        self,
        bound_permit_id: str,
        *,
        gateway_instance_id: str,
        lease_epoch: int,
        authoritative_result_digest: str,
    ) -> dict[str, Any]:
        """Atomically fence owner+epoch and consume P10 + P11 records together."""
        if not authoritative_result_digest:
            return {"finalized": False, "reason": "AUTHORITATIVE_RESULT_DIGEST_REQUIRED"}
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            lease, lease_error = self._read(conn, bound_permit_id)
            if lease_error:
                conn.rollback()
                return {"finalized": False, "reason": lease_error}
            assert lease is not None
            if lease.get("state") == "CONSUMED":
                conn.commit()
                return {"finalized": False, "reason": "SEMANTIC_BOUND_PERMIT_CONSUMED"}
            if lease.get("state") != "IN_FLIGHT":
                conn.rollback()
                return {"finalized": False, "reason": "SEMANTIC_LEASE_FINALIZE_REQUIRES_IN_FLIGHT"}
            if lease.get("lease_owner_gateway_instance_id") != gateway_instance_id:
                conn.rollback()
                return {"finalized": False, "reason": "SEMANTIC_LEASE_STALE_OWNER"}
            if int(lease.get("lease_epoch", 0)) != int(lease_epoch):
                conn.rollback()
                return {"finalized": False, "reason": "SEMANTIC_LEASE_STALE_EPOCH"}

            p10, p10_error = self._p10._read_verified(conn, bound_permit_id)
            if p10_error or p10 is None:
                conn.rollback()
                return {"finalized": False, "reason": p10_error or "SEMANTIC_REGISTRY_RECORD_MISSING"}
            if p10.get("state") != "IN_FLIGHT":
                conn.rollback()
                return {"finalized": False, "reason": "SEMANTIC_REGISTRY_FINALIZE_REQUIRES_IN_FLIGHT"}

            p10["state"] = "CONSUMED"
            p10["authoritative_result_digest"] = authoritative_result_digest
            lease["state"] = "CONSUMED"
            lease["authoritative_result_digest"] = authoritative_result_digest
            self._p10._write(conn, p10)
            self._write(conn, lease)
            conn.commit()
            return {
                "finalized": True,
                "state": "CONSUMED",
                "lease_owner_gateway_instance_id": gateway_instance_id,
                "lease_epoch": int(lease_epoch),
                "authoritative_result_digest": authoritative_result_digest,
            }

    def stale_finalize_probe(
        self,
        bound_permit_id: str,
        *,
        gateway_instance_id: str,
        lease_epoch: int,
        authoritative_result_digest: str,
    ) -> dict[str, Any]:
        """Trusted harness probe uses the exact authoritative finalization path."""
        return self.finalize_both(
            bound_permit_id,
            gateway_instance_id=gateway_instance_id,
            lease_epoch=lease_epoch,
            authoritative_result_digest=authoritative_result_digest,
        )


class FencedSemanticBoundLocalEnforcementPoint:
    """Pilot 11 issuer: Pilot 10 outer permit plus a durable ISSUED fence record."""

    def __init__(self, p10_lep: DurableSemanticBoundLocalEnforcementPoint, lease_registry: SemanticPermitLeaseRegistry) -> None:
        self._p10_lep = p10_lep
        self._leases = lease_registry

    def authorize(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = self._p10_lep.authorize(*args, **kwargs)
        if result.get("authorized") and isinstance(result.get("permit"), Mapping):
            self._leases.register_issued(dict(result["permit"]["payload"]))
            result = copy.deepcopy(result)
            result["lease_state"] = "ISSUED"
            result["lease_epoch"] = 0
        return result


class FencedProcessSemanticBoundGateway:
    """Pilot 11 gateway: one active gateway owner per semantic permit epoch."""

    def __init__(
        self,
        p10_registry: DurableSemanticPermitRegistry,
        lease_registry: SemanticPermitLeaseRegistry,
        gateway: Any,
        *,
        outer_permit_verification_key: bytes,
        gateway_instance_id: str,
    ) -> None:
        self._p10 = p10_registry
        self._leases = lease_registry
        self._gateway = gateway
        self._outer_key = bytes(outer_permit_verification_key)
        self.gateway_instance_id = gateway_instance_id

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
        after_resolve_hook: Any | None = None,
        after_gateway_hook: Any | None = None,
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
        bound_id = str(payload.get("bound_permit_id", ""))
        if not bound_id:
            return _deny("SEMANTIC_BOUND_PERMIT_ID_REQUIRED")
        expected = {field: payload.get(field) for field in REGISTRY_BINDING_FIELDS if field != "bound_permit_id"}
        resolved = self._leases.resolve_for_gateway(
            bound_id,
            gateway_instance_id=self.gateway_instance_id,
            expected_bindings=expected,
        )
        if not resolved.get("resolved"):
            return _deny(
                str(resolved.get("reason", "SEMANTIC_LEASE_RESOLUTION_DENIED")),
                lease_epoch=resolved.get("lease_epoch"),
                lease_owner_gateway_instance_id=resolved.get("lease_owner_gateway_instance_id"),
                lease_state=resolved.get("state"),
            )
        epoch = int(resolved["lease_epoch"])

        if after_resolve_hook is not None:
            after_resolve_hook()

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
        finalized = self._leases.finalize_both(
            bound_id,
            gateway_instance_id=self.gateway_instance_id,
            lease_epoch=epoch,
            authoritative_result_digest=result_digest,
        )
        if not finalized.get("finalized"):
            return _deny(
                str(finalized.get("reason", "SEMANTIC_FENCED_FINALIZATION_FAILED")),
                authoritative_gateway_result=gateway_result,
                lease_epoch=epoch,
            )
        return {
            **gateway_result,
            "lease_disposition": resolved.get("disposition"),
            "lease_owner_gateway_instance_id": self.gateway_instance_id,
            "lease_epoch": epoch,
            "lease_state": "CONSUMED",
            "registry_disposition": resolved.get("registry_disposition"),
            "bound_permit_id": bound_id,
            "inner_permit_digest": resolved.get("inner_permit_digest"),
        }

    def effect_count(self) -> int:
        return self._gateway.effect_count()
