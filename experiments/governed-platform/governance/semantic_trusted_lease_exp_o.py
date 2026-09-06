"""EXP-O Pilot 12 trusted-time lease fencing for semantic-bound permits.

Pilot 11 intentionally allowed any different gateway instance to take over an
IN_FLIGHT exact permit because its harness proved the old process had crashed.
Pilot 12 removes that assumption: a different live instance cannot take over
until the platform-trusted lease clock reaches the durable expiry boundary.
"""
from __future__ import annotations

import copy
from contextlib import closing
import hashlib
import hmac
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Mapping

from semantic_permit_registry_exp_o import (
    DurableSemanticBoundLocalEnforcementPoint,
    DurableSemanticPermitRegistry,
    REGISTRY_BINDING_FIELDS,
    _verify,
)
from semantic_verification_binding_exp_o import digest, semantic_effect_view

LEASE_DURATION_MS = 1000


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _deny(reason: str, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


class TrustedSemanticLeaseRegistry:
    """Durable one-owner lease using a platform-owned trusted clock."""

    def __init__(
        self,
        db_path: str | Path,
        integrity_key: bytes,
        p10_registry: DurableSemanticPermitRegistry,
        trusted_clock: Callable[[], int],
        *,
        lease_duration_ms: int = LEASE_DURATION_MS,
    ) -> None:
        if not integrity_key:
            raise ValueError("trusted lease integrity key must not be empty")
        if lease_duration_ms <= 0:
            raise ValueError("lease duration must be positive")
        self.db_path = str(db_path)
        self._key = bytes(integrity_key)
        self._p10 = p10_registry
        self._clock = trusted_clock
        self.lease_duration_ms = int(lease_duration_ms)
        if Path(self.db_path).resolve() != Path(self._p10.db_path).resolve():
            raise ValueError("Pilot 12 lease and Pilot 10 registry must share one SQLite database")
        self._init_schema()

    def trusted_now_ms(self) -> int:
        return int(self._clock())

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_trusted_leases (
                    bound_permit_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL,
                    integrity_tag TEXT NOT NULL
                )
                """
            )

    def _tag(self, record: Mapping[str, Any]) -> str:
        return hmac.new(self._key, _canonical(dict(record)), hashlib.sha256).hexdigest()

    def _read(self, conn: sqlite3.Connection, bound_id: str) -> tuple[dict[str, Any] | None, str | None]:
        row = conn.execute(
            "SELECT record_json, integrity_tag FROM semantic_trusted_leases WHERE bound_permit_id = ?",
            (bound_id,),
        ).fetchone()
        if row is None:
            return None, "TRUSTED_LEASE_RECORD_MISSING"
        try:
            record = json.loads(str(row["record_json"]))
        except Exception:
            return None, "TRUSTED_LEASE_RECORD_MALFORMED"
        if not isinstance(record, dict) or record.get("bound_permit_id") != bound_id:
            return None, "TRUSTED_LEASE_RECORD_BINDING_INVALID"
        if not hmac.compare_digest(str(row["integrity_tag"]), self._tag(record)):
            return None, "TRUSTED_LEASE_INTEGRITY_INVALID"
        return record, None

    def _write(self, conn: sqlite3.Connection, record: Mapping[str, Any]) -> None:
        payload = copy.deepcopy(dict(record))
        conn.execute(
            "UPDATE semantic_trusted_leases SET record_json = ?, integrity_tag = ? WHERE bound_permit_id = ?",
            (_canonical(payload).decode("utf-8"), self._tag(payload), str(payload["bound_permit_id"])),
        )

    def _validate_bindings(self, record: Mapping[str, Any], bound_id: str, expected: Mapping[str, Any]) -> str | None:
        for field in REGISTRY_BINDING_FIELDS:
            wanted = bound_id if field == "bound_permit_id" else expected.get(field)
            if record.get(field) != wanted:
                return f"TRUSTED_LEASE_BINDING_MISMATCH:{field}"
        return None

    def register_issued(self, outer_payload: Mapping[str, Any]) -> dict[str, Any]:
        payload = copy.deepcopy(dict(outer_payload))
        for field in REGISTRY_BINDING_FIELDS:
            if payload.get(field) in (None, "", []):
                raise ValueError(f"trusted lease record missing binding {field}")
        bound_id = str(payload["bound_permit_id"])
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            p10, error = self._p10._read_verified(conn, bound_id)
            if error or p10 is None or p10.get("state") != "ISSUED":
                conn.rollback()
                raise ValueError("underlying semantic permit must exist in ISSUED state")
            record = {
                **{field: copy.deepcopy(payload[field]) for field in REGISTRY_BINDING_FIELDS},
                "state": "ISSUED",
                "lease_owner_gateway_instance_id": None,
                "lease_epoch": 0,
                "lease_expires_at_ms": None,
                "authoritative_result_digest": None,
            }
            try:
                conn.execute(
                    "INSERT INTO semantic_trusted_leases(bound_permit_id, record_json, integrity_tag) VALUES (?, ?, ?)",
                    (bound_id, _canonical(record).decode("utf-8"), self._tag(record)),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                raise ValueError("duplicate trusted lease record") from exc
            conn.commit()
        return self.inspect(bound_id)

    def inspect(self, bound_id: str) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            record, error = self._read(conn, bound_id)
        if error:
            return {"verified": False, "reason": error, "bound_permit_id": bound_id}
        assert record is not None
        return {
            "verified": True,
            "bound_permit_id": bound_id,
            "state": record["state"],
            "lease_owner_gateway_instance_id": record["lease_owner_gateway_instance_id"],
            "lease_epoch": int(record["lease_epoch"]),
            "lease_expires_at_ms": record["lease_expires_at_ms"],
            "semantic_payload_digest": record["semantic_payload_digest"],
            "effect_digest": record["effect_digest"],
            "idempotency_key": record["idempotency_key"],
            "authoritative_result_digest": record["authoritative_result_digest"],
        }

    def resolve_for_gateway(
        self,
        bound_id: str,
        *,
        gateway_instance_id: str,
        expected_bindings: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Acquire or expiry-takeover using only the registry's trusted clock."""
        if not gateway_instance_id:
            return {"resolved": False, "reason": "GATEWAY_INSTANCE_ID_REQUIRED"}
        trusted_now = self.trusted_now_ms()
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            lease, error = self._read(conn, bound_id)
            if error:
                conn.rollback()
                return {"resolved": False, "reason": error, "trusted_now_ms": trusted_now}
            assert lease is not None
            binding_error = self._validate_bindings(lease, bound_id, expected_bindings)
            if binding_error:
                conn.rollback()
                return {"resolved": False, "reason": binding_error, "trusted_now_ms": trusted_now}
            p10, p10_error = self._p10._read_verified(conn, bound_id)
            if p10_error or p10 is None:
                conn.rollback()
                return {"resolved": False, "reason": p10_error or "SEMANTIC_REGISTRY_RECORD_MISSING", "trusted_now_ms": trusted_now}
            inner = p10.get("inner_permit")
            if not isinstance(inner, Mapping) or digest(dict(inner)) != p10.get("inner_permit_digest"):
                conn.rollback()
                return {"resolved": False, "reason": "SEMANTIC_REGISTRY_INNER_PERMIT_DIGEST_MISMATCH", "trusted_now_ms": trusted_now}

            state = lease.get("state")
            owner = lease.get("lease_owner_gateway_instance_id")
            epoch = int(lease.get("lease_epoch", 0))
            expiry = lease.get("lease_expires_at_ms")
            if state == "CONSUMED" or p10.get("state") == "CONSUMED":
                conn.commit()
                return {"resolved": False, "reason": "SEMANTIC_BOUND_PERMIT_CONSUMED", "state": "CONSUMED", "lease_epoch": epoch, "lease_owner_gateway_instance_id": owner, "lease_expires_at_ms": expiry, "trusted_now_ms": trusted_now}

            if state == "ISSUED":
                if p10.get("state") != "ISSUED":
                    conn.rollback()
                    return {"resolved": False, "reason": "TRUSTED_LEASE_FIRST_OWNER_REQUIRES_UNDERLYING_ISSUED", "trusted_now_ms": trusted_now}
                idem_error = self._p10._claim_semantic_idempotency(conn, p10)
                if idem_error:
                    lease["state"] = "CONSUMED"
                    lease["authoritative_result_digest"] = "DENIED_BEFORE_INNER_EFFECT"
                    self._write(conn, lease)
                    conn.commit()
                    return {"resolved": False, "reason": idem_error, "state": "CONSUMED", "trusted_now_ms": trusted_now}
                new_expiry = trusted_now + self.lease_duration_ms
                lease.update(state="IN_FLIGHT", lease_owner_gateway_instance_id=gateway_instance_id, lease_epoch=epoch + 1, lease_expires_at_ms=new_expiry)
                p10["state"] = "IN_FLIGHT"
                p10["use_attempts"] = int(p10.get("use_attempts", 0)) + 1
                self._write(conn, lease)
                self._p10._write(conn, p10)
                conn.commit()
                return {"resolved": True, "disposition": "FIRST_OWNER", "registry_disposition": "FIRST_USE", "lease_owner_gateway_instance_id": gateway_instance_id, "lease_epoch": epoch + 1, "lease_expires_at_ms": new_expiry, "trusted_now_ms": trusted_now, "inner_permit": copy.deepcopy(dict(inner)), "inner_permit_digest": p10.get("inner_permit_digest")}

            if state != "IN_FLIGHT":
                conn.rollback()
                return {"resolved": False, "reason": "TRUSTED_LEASE_STATE_INVALID", "trusted_now_ms": trusted_now}
            if owner == gateway_instance_id:
                conn.commit()
                return {"resolved": False, "reason": "TRUSTED_LEASE_IN_FLIGHT_ALREADY_OWNED", "state": "IN_FLIGHT", "lease_owner_gateway_instance_id": owner, "lease_epoch": epoch, "lease_expires_at_ms": expiry, "trusted_now_ms": trusted_now}
            if expiry is None:
                conn.rollback()
                return {"resolved": False, "reason": "TRUSTED_LEASE_EXPIRY_MISSING", "trusted_now_ms": trusted_now}
            if trusted_now < int(expiry):
                conn.commit()
                return {"resolved": False, "reason": "TRUSTED_LEASE_LIVE_OWNER_UNEXPIRED", "state": "IN_FLIGHT", "lease_owner_gateway_instance_id": owner, "lease_epoch": epoch, "lease_expires_at_ms": int(expiry), "trusted_now_ms": trusted_now}
            if p10.get("state") != "IN_FLIGHT":
                conn.rollback()
                return {"resolved": False, "reason": "TRUSTED_LEASE_TAKEOVER_REQUIRES_UNDERLYING_IN_FLIGHT", "trusted_now_ms": trusted_now}
            idem_error = self._p10._claim_semantic_idempotency(conn, p10)
            if idem_error:
                conn.rollback()
                return {"resolved": False, "reason": idem_error, "trusted_now_ms": trusted_now}

            new_epoch = epoch + 1
            new_expiry = trusted_now + self.lease_duration_ms
            old_owner = owner
            lease["lease_owner_gateway_instance_id"] = gateway_instance_id
            lease["lease_epoch"] = new_epoch
            lease["lease_expires_at_ms"] = new_expiry
            p10["use_attempts"] = int(p10.get("use_attempts", 0)) + 1
            self._write(conn, lease)
            self._p10._write(conn, p10)
            conn.commit()
            return {"resolved": True, "disposition": "TRUSTED_EXPIRY_TAKEOVER", "registry_disposition": "RECOVERY_IN_FLIGHT", "lease_owner_gateway_instance_id": gateway_instance_id, "previous_owner_gateway_instance_id": old_owner, "lease_epoch": new_epoch, "lease_expires_at_ms": new_expiry, "trusted_now_ms": trusted_now, "inner_permit": copy.deepcopy(dict(inner)), "inner_permit_digest": p10.get("inner_permit_digest")}

    def renew(self, bound_id: str, *, gateway_instance_id: str, lease_epoch: int) -> dict[str, Any]:
        """Explicit owner-only renewal; caller time is not an input."""
        trusted_now = self.trusted_now_ms()
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            lease, error = self._read(conn, bound_id)
            if error:
                conn.rollback()
                return {"renewed": False, "reason": error, "trusted_now_ms": trusted_now}
            assert lease is not None
            if lease.get("state") != "IN_FLIGHT":
                conn.rollback()
                return {"renewed": False, "reason": "TRUSTED_LEASE_RENEW_REQUIRES_IN_FLIGHT", "trusted_now_ms": trusted_now}
            if lease.get("lease_owner_gateway_instance_id") != gateway_instance_id:
                conn.rollback()
                return {"renewed": False, "reason": "TRUSTED_LEASE_RENEW_STALE_OWNER", "trusted_now_ms": trusted_now}
            if int(lease.get("lease_epoch", 0)) != int(lease_epoch):
                conn.rollback()
                return {"renewed": False, "reason": "TRUSTED_LEASE_RENEW_STALE_EPOCH", "trusted_now_ms": trusted_now}
            expiry = int(lease.get("lease_expires_at_ms") or -1)
            if trusted_now >= expiry:
                conn.rollback()
                return {"renewed": False, "reason": "TRUSTED_LEASE_ALREADY_EXPIRED", "trusted_now_ms": trusted_now, "lease_expires_at_ms": expiry}
            new_expiry = trusted_now + self.lease_duration_ms
            if new_expiry <= expiry:
                new_expiry = expiry + self.lease_duration_ms
            lease["lease_expires_at_ms"] = new_expiry
            self._write(conn, lease)
            conn.commit()
            return {"renewed": True, "lease_owner_gateway_instance_id": gateway_instance_id, "lease_epoch": int(lease_epoch), "lease_expires_at_ms": new_expiry, "trusted_now_ms": trusted_now}

    def finalize_both(self, bound_id: str, *, gateway_instance_id: str, lease_epoch: int, authoritative_result_digest: str) -> dict[str, Any]:
        """Atomically fence owner+epoch and consume P10 + P12 records together."""
        if not authoritative_result_digest:
            return {"finalized": False, "reason": "AUTHORITATIVE_RESULT_DIGEST_REQUIRED"}
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            lease, error = self._read(conn, bound_id)
            if error:
                conn.rollback()
                return {"finalized": False, "reason": error}
            assert lease is not None
            if lease.get("state") == "CONSUMED":
                conn.commit()
                return {"finalized": False, "reason": "SEMANTIC_BOUND_PERMIT_CONSUMED"}
            if lease.get("state") != "IN_FLIGHT":
                conn.rollback()
                return {"finalized": False, "reason": "TRUSTED_LEASE_FINALIZE_REQUIRES_IN_FLIGHT"}
            if lease.get("lease_owner_gateway_instance_id") != gateway_instance_id:
                conn.rollback()
                return {"finalized": False, "reason": "TRUSTED_LEASE_STALE_OWNER"}
            if int(lease.get("lease_epoch", 0)) != int(lease_epoch):
                conn.rollback()
                return {"finalized": False, "reason": "TRUSTED_LEASE_STALE_EPOCH"}
            p10, p10_error = self._p10._read_verified(conn, bound_id)
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
            return {"finalized": True, "state": "CONSUMED", "lease_owner_gateway_instance_id": gateway_instance_id, "lease_epoch": int(lease_epoch), "authoritative_result_digest": authoritative_result_digest}


class TrustedLeaseSemanticBoundLocalEnforcementPoint:
    """Pilot 12 issuer: Pilot 10 outer permit plus trusted lease record."""

    def __init__(self, p10_lep: DurableSemanticBoundLocalEnforcementPoint, leases: TrustedSemanticLeaseRegistry) -> None:
        self._p10_lep = p10_lep
        self._leases = leases

    def authorize(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = self._p10_lep.authorize(*args, **kwargs)
        if result.get("authorized") and isinstance(result.get("permit"), Mapping):
            self._leases.register_issued(dict(result["permit"]["payload"]))
            result = copy.deepcopy(result)
            result.update(lease_state="ISSUED", lease_epoch=0, lease_expires_at_ms=None)
        return result


class TrustedLeaseProcessSemanticBoundGateway:
    """Process gateway enforcing P12 trusted lease before MCP invocation."""

    def __init__(self, p10_registry: DurableSemanticPermitRegistry, leases: TrustedSemanticLeaseRegistry, gateway: Any, *, outer_permit_verification_key: bytes, gateway_instance_id: str) -> None:
        self._p10 = p10_registry
        self._leases = leases
        self._gateway = gateway
        self._outer_key = bytes(outer_permit_verification_key)
        self.gateway_instance_id = gateway_instance_id

    def execute(self, *, permit: Mapping[str, Any] | None, candidate_payload: Mapping[str, Any], worker_id: str, worker_key_thumbprint: str, effect: Mapping[str, Any], idempotency_key: str, now_ms: int, after_resolve_hook: Any | None = None, after_gateway_hook: Any | None = None) -> dict[str, Any]:
        if not _verify(permit, self._outer_key):
            return _deny("SEMANTIC_BOUND_OUTER_PERMIT_INVALID")
        payload = dict(permit["payload"])
        candidate_digest = digest(dict(candidate_payload))
        if effect.get("semantic_payload_digest") != candidate_digest:
            return _deny("SEMANTIC_CANDIDATE_EFFECT_DIGEST_MISMATCH")
        effect_digest = digest(semantic_effect_view(effect))
        checks = {"semantic_payload_digest": candidate_digest, "effect_digest": effect_digest, "idempotency_key": idempotency_key, "worker_id": worker_id, "worker_key_thumbprint": worker_key_thumbprint, "effect_contract_id": effect.get("effect_contract_id"), "base_sha": effect.get("base_sha")}
        for field, value in checks.items():
            if payload.get(field) != value:
                return _deny(f"SEMANTIC_BOUND_OUTER_PERMIT_MISMATCH:{field}")
        bound_id = str(payload.get("bound_permit_id", ""))
        if not bound_id:
            return _deny("SEMANTIC_BOUND_PERMIT_ID_REQUIRED")
        expected = {field: payload.get(field) for field in REGISTRY_BINDING_FIELDS if field != "bound_permit_id"}
        resolved = self._leases.resolve_for_gateway(bound_id, gateway_instance_id=self.gateway_instance_id, expected_bindings=expected)
        if not resolved.get("resolved"):
            return _deny(str(resolved.get("reason", "TRUSTED_LEASE_RESOLUTION_DENIED")), lease_epoch=resolved.get("lease_epoch"), lease_owner_gateway_instance_id=resolved.get("lease_owner_gateway_instance_id"), lease_expires_at_ms=resolved.get("lease_expires_at_ms"), trusted_now_ms=resolved.get("trusted_now_ms"), lease_state=resolved.get("state"))
        epoch = int(resolved["lease_epoch"])
        if after_resolve_hook is not None:
            after_resolve_hook()
        gateway_result = self._gateway.execute(permit=resolved["inner_permit"], worker_id=worker_id, worker_key_thumbprint=worker_key_thumbprint, effect=effect, idempotency_key=idempotency_key, now_ms=now_ms)
        if after_gateway_hook is not None:
            after_gateway_hook(gateway_result)
        authoritative_result = gateway_result.get("result") if isinstance(gateway_result.get("result"), Mapping) else gateway_result
        result_digest = digest(authoritative_result)
        finalized = self._leases.finalize_both(bound_id, gateway_instance_id=self.gateway_instance_id, lease_epoch=epoch, authoritative_result_digest=result_digest)
        if not finalized.get("finalized"):
            return _deny(str(finalized.get("reason", "TRUSTED_LEASE_FINALIZATION_FAILED")), authoritative_gateway_result=gateway_result, lease_epoch=epoch)
        return {**gateway_result, "lease_disposition": resolved.get("disposition"), "lease_owner_gateway_instance_id": self.gateway_instance_id, "lease_epoch": epoch, "lease_expires_at_ms": resolved.get("lease_expires_at_ms"), "lease_state": "CONSUMED", "registry_disposition": resolved.get("registry_disposition"), "bound_permit_id": bound_id, "inner_permit_digest": resolved.get("inner_permit_digest")}

    def renew(self, bound_permit_id: str, lease_epoch: int) -> dict[str, Any]:
        return self._leases.renew(bound_permit_id, gateway_instance_id=self.gateway_instance_id, lease_epoch=lease_epoch)

    def effect_count(self) -> int:
        return self._gateway.effect_count()
