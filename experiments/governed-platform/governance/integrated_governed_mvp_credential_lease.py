from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping


LEASE_TTL_SECONDS = 30
RAW_SECRET_FIELDS = {"api_key", "apikey", "token", "password", "secret", "raw_secret"}
UPSTREAM_SUCCESS_STATES = {
    "REMOTE_EXECUTION_COMPLETED",
    "REMOTE_EXECUTION_RECONCILED",
    "REMOTE_EXECUTION_REPLAYED",
}
LINEAGE_FIELDS = (
    "terminal_execution_id",
    "project_id",
    "task_id",
    "effect_id",
    "action",
    "artifact_sha",
    "state_version",
    "terminal_binding_hash",
)
REQUEST_BINDING_FIELDS = (
    "lease_request_id",
    "project_id",
    "task_id",
    "effect_id",
    "action",
    "artifact_sha",
    "state_version",
    "terminal_execution_id",
    "terminal_binding_hash",
    "authority_snapshot_hash",
    "provider_id",
    "credential_profile_id",
    "resource_class",
)
LEASE_REBIND_FIELDS = (
    "credential_lease_id",
    "lease_request_id",
    "project_id",
    "task_id",
    "effect_id",
    "action",
    "artifact_sha",
    "state_version",
    "terminal_execution_id",
    "terminal_binding_hash",
    "authority_snapshot_hash",
    "provider_id",
    "credential_profile_id",
    "resource_class",
    "profile_epoch",
    "profile_snapshot_hash",
    "lease_not_before_epoch",
    "lease_expires_at_epoch",
    "lease_binding_hash",
)


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def derive_credential_lease_id(request: Mapping[str, Any]) -> str:
    body = {field: request.get(field) for field in REQUEST_BINDING_FIELDS}
    return "cred-lease-" + canonical_hash(body)[:32]


def _profile_hash(profile: Mapping[str, Any]) -> str:
    body = {k: deepcopy(v) for k, v in profile.items() if k != "profile_snapshot_hash"}
    return canonical_hash(body)


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class ReferenceCredentialBroker:
    """Deterministic local broker. Raw synthetic secret values remain in memory only."""

    def __init__(self, db_path: str | Path, *, secrets: Mapping[tuple[str, str], str]):
        self.db_path = Path(db_path)
        self.secrets = dict(secrets)
        self._failure_detail: str | None = None
        self._init_db()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS broker_handles (
                    credential_lease_id TEXT PRIMARY KEY,
                    provider_id TEXT NOT NULL,
                    credential_profile_id TEXT NOT NULL,
                    opaque_secret_handle TEXT NOT NULL UNIQUE
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS broker_consumptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    credential_lease_id TEXT NOT NULL,
                    opaque_secret_handle TEXT NOT NULL
                )
                """
            )

    def set_failure_detail(self, detail: str | None) -> None:
        self._failure_detail = detail

    def _redact(self, text: str) -> str:
        result = text
        for secret in self.secrets.values():
            if secret:
                result = result.replace(secret, "[REDACTED]")
        return result

    def issue_handle(self, provider_id: str, credential_profile_id: str, credential_lease_id: str) -> str:
        if self._failure_detail is not None:
            raise RuntimeError(self._redact(self._failure_detail))
        identity = (provider_id, credential_profile_id)
        if identity not in self.secrets:
            raise KeyError("credential profile has no reference secret")
        with self._connect() as con:
            row = con.execute(
                "SELECT provider_id, credential_profile_id, opaque_secret_handle FROM broker_handles WHERE credential_lease_id=?",
                (credential_lease_id,),
            ).fetchone()
            if row is not None:
                if row["provider_id"] != provider_id or row["credential_profile_id"] != credential_profile_id:
                    raise ValueError("credential lease identity rebind")
                return str(row["opaque_secret_handle"])
            handle = "opaque-" + canonical_hash(
                {
                    "credential_lease_id": credential_lease_id,
                    "provider_id": provider_id,
                    "credential_profile_id": credential_profile_id,
                }
            )[:40]
            con.execute(
                "INSERT INTO broker_handles(credential_lease_id, provider_id, credential_profile_id, opaque_secret_handle) VALUES(?,?,?,?)",
                (credential_lease_id, provider_id, credential_profile_id, handle),
            )
            return handle

    def consume_handle(self, credential_lease_id: str, provider_id: str, credential_profile_id: str, handle: str) -> bool:
        identity = (provider_id, credential_profile_id)
        if identity not in self.secrets:
            return False
        with self._connect() as con:
            row = con.execute(
                "SELECT provider_id, credential_profile_id, opaque_secret_handle FROM broker_handles WHERE credential_lease_id=?",
                (credential_lease_id,),
            ).fetchone()
            if row is None:
                return False
            if (
                row["provider_id"] != provider_id
                or row["credential_profile_id"] != credential_profile_id
                or row["opaque_secret_handle"] != handle
            ):
                return False
            con.execute(
                "INSERT INTO broker_consumptions(credential_lease_id, opaque_secret_handle) VALUES(?,?)",
                (credential_lease_id, handle),
            )
            return True

    def issue_count(self) -> int:
        with self._connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM broker_handles").fetchone()[0])

    def consume_count(self) -> int:
        with self._connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM broker_consumptions").fetchone()[0])


class CredentialLeaseGate:
    def __init__(self, db_path: str | Path, broker: ReferenceCredentialBroker):
        self.db_path = Path(db_path)
        self.broker = broker
        self._init_db()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS credential_leases (
                    credential_lease_id TEXT PRIMARY KEY,
                    lease_request_id TEXT NOT NULL UNIQUE,
                    lease_status TEXT NOT NULL,
                    bound_lease_json TEXT NOT NULL,
                    lease_evidence_json TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS governed_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_json TEXT NOT NULL
                )
                """
            )

    def _record(self, value: Mapping[str, Any]) -> None:
        safe = deepcopy(dict(value))
        serialized = _canon(safe)
        for secret in self.broker.secrets.values():
            if secret and secret in serialized:
                serialized = serialized.replace(secret, "[REDACTED]")
        with self._connect() as con:
            con.execute("INSERT INTO governed_events(event_json) VALUES(?)", (serialized,))

    def governed_records(self) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT event_json FROM governed_events ORDER BY id").fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def _result(self, state: str, *, successful_lease: bool = False, bound_lease=None, lease_evidence=None, reason: str = "") -> dict[str, Any]:
        result = {
            "state": state,
            "reason": reason,
            "successful_lease": successful_lease,
            "production_side_effect_claimed": False,
            "bound_lease": deepcopy(bound_lease),
            "lease_evidence": deepcopy(lease_evidence),
        }
        self._record(result)
        return result

    def _upstream_valid(self, upstream: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any] | None]:
        if not isinstance(upstream, Mapping):
            return False, None
        if upstream.get("state") not in UPSTREAM_SUCCESS_STATES or upstream.get("successful_remote_completion") is not True:
            return False, None
        if upstream.get("production_remote_side_effect_claimed") is not False:
            return False, None
        bound = upstream.get("bound_remote_execution")
        evidence = upstream.get("remote_completion_evidence")
        if not isinstance(bound, Mapping) or not isinstance(evidence, Mapping):
            return False, None
        for field in LINEAGE_FIELDS:
            if bound.get(field) != evidence.get(field):
                return False, None
        if not isinstance(evidence.get("remote_completion_hash"), str) or not evidence.get("remote_completion_hash"):
            return False, None
        return True, bound

    def _profile_valid(self, profile: Mapping[str, Any], now_epoch: float) -> bool:
        if not isinstance(profile, Mapping):
            return False
        required = (
            "provider_id",
            "credential_profile_id",
            "profile_status",
            "allowed_actions",
            "allowed_project_ids",
            "allowed_resource_classes",
            "profile_epoch",
            "not_before_epoch",
            "expires_at_epoch",
            "profile_snapshot_hash",
        )
        if any(field not in profile for field in required):
            return False
        if profile.get("profile_status") != "ACTIVE":
            return False
        if not isinstance(profile.get("profile_epoch"), int) or isinstance(profile.get("profile_epoch"), bool):
            return False
        try:
            not_before = float(profile.get("not_before_epoch"))
            expires = float(profile.get("expires_at_epoch"))
            now = float(now_epoch)
        except (TypeError, ValueError):
            return False
        if not (not_before <= now < expires):
            return False
        return profile.get("profile_snapshot_hash") == _profile_hash(profile)

    def _raw_secret_supplied(self, request: Mapping[str, Any]) -> bool:
        for key, value in request.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in RAW_SECRET_FIELDS and value not in (None, ""):
                return True
        return False

    def _replacement_identity_supplied(self, request: Mapping[str, Any]) -> bool:
        allowed = set(REQUEST_BINDING_FIELDS)
        for key, value in request.items():
            if key in allowed or value in (None, ""):
                continue
            normalized = str(key).lower()
            if "provider_id" in normalized or "credential_profile_id" in normalized:
                return True
        return False

    def _request_lineage_matches(self, request: Mapping[str, Any], bound: Mapping[str, Any]) -> bool:
        for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "terminal_execution_id", "terminal_binding_hash"):
            if request.get(field) != bound.get(field):
                return False
        return True

    def _scope_allowed(self, request: Mapping[str, Any], profile: Mapping[str, Any]) -> bool:
        return (
            request.get("project_id") in profile.get("allowed_project_ids", [])
            and request.get("action") in profile.get("allowed_actions", [])
            and request.get("resource_class") in profile.get("allowed_resource_classes", [])
        )

    def _load_by_request(self, lease_request_id: str):
        with self._connect() as con:
            row = con.execute(
                "SELECT credential_lease_id, lease_status, bound_lease_json, lease_evidence_json FROM credential_leases WHERE lease_request_id=?",
                (lease_request_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "credential_lease_id": row["credential_lease_id"],
            "lease_status": row["lease_status"],
            "bound_lease": json.loads(row["bound_lease_json"]),
            "lease_evidence": json.loads(row["lease_evidence_json"]),
        }

    def _load_by_id(self, credential_lease_id: str):
        with self._connect() as con:
            row = con.execute(
                "SELECT lease_status, bound_lease_json, lease_evidence_json FROM credential_leases WHERE credential_lease_id=?",
                (credential_lease_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "lease_status": row["lease_status"],
            "bound_lease": json.loads(row["bound_lease_json"]),
            "lease_evidence": json.loads(row["lease_evidence_json"]),
        }

    def issue(self, *, upstream_result: Mapping[str, Any], lease_request: Mapping[str, Any], current_profile: Mapping[str, Any], now_epoch: float) -> dict[str, Any]:
        valid_upstream, bound = self._upstream_valid(upstream_result)
        if not valid_upstream or bound is None:
            return self._result("DENY_UPSTREAM_BINDING", reason="exact accepted upstream terminal lineage required")
        if not isinstance(lease_request, Mapping):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="lease request malformed")
        if self._raw_secret_supplied(lease_request):
            return self._result("DENY_RAW_SECRET_INPUT", reason="raw credential material forbidden")
        if self._replacement_identity_supplied(lease_request):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="caller-supplied replacement credential identity forbidden")
        if not self._request_lineage_matches(lease_request, bound):
            return self._result("DENY_SCOPE_WIDENING", reason="request widens or changes terminal lineage")
        if (
            lease_request.get("provider_id") != current_profile.get("provider_id")
            or lease_request.get("credential_profile_id") != current_profile.get("credential_profile_id")
        ):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="credential profile identity substitution")
        if not self._profile_valid(current_profile, now_epoch):
            return self._result("DENY_PROFILE_STALE_OR_REVOKED", reason="credential profile not currently valid")
        if not self._scope_allowed(lease_request, current_profile):
            return self._result("DENY_SCOPE_WIDENING", reason="credential profile scope does not cover request")
        if not isinstance(lease_request.get("lease_request_id"), str) or not lease_request.get("lease_request_id"):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="lease request identity required")
        existing = self._load_by_request(str(lease_request["lease_request_id"]))
        if existing is not None:
            stored = existing["bound_lease"]
            for field in REQUEST_BINDING_FIELDS:
                if field == "lease_request_id":
                    if stored.get(field) != lease_request.get(field):
                        return self._result("DENY_LEASE_REBIND", reason="lease request rebind")
                    continue
                if field in stored and stored.get(field) != lease_request.get(field):
                    return self._result("DENY_LEASE_REBIND", reason="lease request rebind")
            now = float(now_epoch)
            if existing["lease_status"] == "REVOKED":
                return self._result("LEASE_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease revoked")
            if now >= float(stored["lease_expires_at_epoch"]):
                return self._result("LEASE_EXPIRED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease expired; fresh request identity required")
            return self._result("LEASE_REPLAYED", successful_lease=True, bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="exact lease replay")

        lease_id = derive_credential_lease_id(lease_request)
        try:
            handle = self.broker.issue_handle(
                str(lease_request["provider_id"]),
                str(lease_request["credential_profile_id"]),
                lease_id,
            )
        except Exception as exc:
            return self._result("DENY_CREDENTIAL_PROFILE", reason=f"reference broker denied: {_safe_text(exc)}")

        now = float(now_epoch)
        lease_expires = min(now + LEASE_TTL_SECONDS, float(current_profile["expires_at_epoch"]))
        bound_lease = {
            **{field: deepcopy(lease_request.get(field)) for field in REQUEST_BINDING_FIELDS},
            "credential_lease_id": lease_id,
            "profile_epoch": current_profile["profile_epoch"],
            "profile_snapshot_hash": current_profile["profile_snapshot_hash"],
            "lease_not_before_epoch": now,
            "lease_expires_at_epoch": lease_expires,
            "opaque_secret_handle": handle,
        }
        binding_body = {k: deepcopy(v) for k, v in bound_lease.items() if k not in {"opaque_secret_handle", "lease_binding_hash"}}
        bound_lease["lease_binding_hash"] = canonical_hash(binding_body)
        evidence_body = {
            "credential_lease_id": lease_id,
            "lease_request_id": bound_lease["lease_request_id"],
            "project_id": bound_lease["project_id"],
            "task_id": bound_lease["task_id"],
            "effect_id": bound_lease["effect_id"],
            "action": bound_lease["action"],
            "artifact_sha": bound_lease["artifact_sha"],
            "state_version": bound_lease["state_version"],
            "terminal_execution_id": bound_lease["terminal_execution_id"],
            "terminal_binding_hash": bound_lease["terminal_binding_hash"],
            "authority_snapshot_hash": bound_lease["authority_snapshot_hash"],
            "provider_id": bound_lease["provider_id"],
            "credential_profile_id": bound_lease["credential_profile_id"],
            "resource_class": bound_lease["resource_class"],
            "profile_epoch": bound_lease["profile_epoch"],
            "profile_snapshot_hash": bound_lease["profile_snapshot_hash"],
            "lease_not_before_epoch": bound_lease["lease_not_before_epoch"],
            "lease_expires_at_epoch": bound_lease["lease_expires_at_epoch"],
            "opaque_secret_handle": bound_lease["opaque_secret_handle"],
            "lease_binding_hash": bound_lease["lease_binding_hash"],
            "production_side_effect_claimed": False,
        }
        lease_evidence = {**evidence_body, "lease_evidence_hash": canonical_hash(evidence_body)}
        with self._connect() as con:
            con.execute(
                "INSERT INTO credential_leases(credential_lease_id, lease_request_id, lease_status, bound_lease_json, lease_evidence_json) VALUES(?,?,?,?,?)",
                (lease_id, str(lease_request["lease_request_id"]), "ACTIVE", _canon(bound_lease), _canon(lease_evidence)),
            )
        return self._result("LEASE_ISSUED", successful_lease=True, bound_lease=bound_lease, lease_evidence=lease_evidence, reason="bounded reference lease issued")

    def revoke(self, credential_lease_id: str) -> None:
        with self._connect() as con:
            con.execute("UPDATE credential_leases SET lease_status='REVOKED' WHERE credential_lease_id=?", (credential_lease_id,))
        self._record({"state": "LEASE_REVOKED", "credential_lease_id": credential_lease_id, "production_side_effect_claimed": False})

    def consume(self, *, upstream_result: Mapping[str, Any], lease_result: Mapping[str, Any], current_profile: Mapping[str, Any], now_epoch: float) -> dict[str, Any]:
        valid_upstream, bound = self._upstream_valid(upstream_result)
        if not valid_upstream or bound is None:
            return self._result("DENY_UPSTREAM_BINDING", reason="exact accepted upstream terminal lineage required")
        if not isinstance(lease_result, Mapping) or not isinstance(lease_result.get("bound_lease"), Mapping):
            return self._result("LEASE_CONSUMPTION_DENIED", reason="lease result malformed")
        supplied = lease_result["bound_lease"]
        lease_id = supplied.get("credential_lease_id")
        if not isinstance(lease_id, str) or not lease_id:
            return self._result("LEASE_CONSUMPTION_DENIED", reason="lease identity missing")
        existing = self._load_by_id(lease_id)
        if existing is None:
            return self._result("LEASE_CONSUMPTION_DENIED", reason="unknown credential lease")
        stored = existing["bound_lease"]
        for field in LEASE_REBIND_FIELDS:
            if supplied.get(field) != stored.get(field):
                return self._result("DENY_LEASE_REBIND", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason=f"lease binding changed: {field}")
        for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "terminal_execution_id", "terminal_binding_hash"):
            if stored.get(field) != bound.get(field):
                return self._result("DENY_UPSTREAM_BINDING", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="upstream lineage changed after lease issuance")
        if current_profile.get("profile_status") == "REVOKED" or existing["lease_status"] == "REVOKED":
            return self._result("LEASE_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease/profile revoked")
        if not self._profile_valid(current_profile, now_epoch):
            return self._result("DENY_PROFILE_STALE_OR_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="credential profile not currently valid")
        if (
            current_profile.get("provider_id") != stored.get("provider_id")
            or current_profile.get("credential_profile_id") != stored.get("credential_profile_id")
            or current_profile.get("profile_epoch") != stored.get("profile_epoch")
            or current_profile.get("profile_snapshot_hash") != stored.get("profile_snapshot_hash")
        ):
            return self._result("DENY_PROFILE_STALE_OR_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="profile epoch/snapshot changed")
        if float(now_epoch) >= float(stored["lease_expires_at_epoch"]):
            with self._connect() as con:
                con.execute("UPDATE credential_leases SET lease_status='EXPIRED' WHERE credential_lease_id=?", (lease_id,))
            return self._result("LEASE_EXPIRED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease expired")
        if supplied.get("opaque_secret_handle") != stored.get("opaque_secret_handle"):
            return self._result("LEASE_CONSUMPTION_DENIED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="opaque handle mismatch")
        if not self._scope_allowed(stored, current_profile):
            return self._result("DENY_SCOPE_WIDENING", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="profile scope changed")
        consumed = self.broker.consume_handle(
            lease_id,
            str(stored["provider_id"]),
            str(stored["credential_profile_id"]),
            str(stored["opaque_secret_handle"]),
        )
        if not consumed:
            return self._result("LEASE_CONSUMPTION_DENIED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="reference broker rejected opaque handle")
        with self._connect() as con:
            con.execute("UPDATE credential_leases SET lease_status='CONSUMED' WHERE credential_lease_id=?", (lease_id,))
        return self._result(
            "LEASE_CONSUMED_REFERENCE_ONLY",
            successful_lease=True,
            bound_lease=stored,
            lease_evidence=existing["lease_evidence"],
            reason="reference credential consumed; no production side effect performed",
        )
