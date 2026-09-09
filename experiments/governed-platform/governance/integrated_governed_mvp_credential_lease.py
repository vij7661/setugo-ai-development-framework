from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

LEASE_TTL_SECONDS = 30
RAW_SECRET_FIELDS = {"api_key", "apikey", "token", "password", "secret", "raw_secret"}
UPSTREAM_SUCCESS_STATES = {"REMOTE_EXECUTION_COMPLETED", "REMOTE_EXECUTION_RECONCILED", "REMOTE_EXECUTION_REPLAYED"}
UPSTREAM_LINEAGE_FIELDS = ("terminal_execution_id", "project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "slice7_completion_hash", "remote_idempotency_key")
REQUEST_BINDING_FIELDS = ("lease_request_id", "project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "terminal_execution_id", "terminal_binding_hash", "authority_snapshot_hash", "provider_id", "credential_profile_id", "resource_class")
LEASE_REBIND_FIELDS = ("credential_lease_id", "lease_request_id", "project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "terminal_execution_id", "terminal_binding_hash", "authority_snapshot_hash", "provider_id", "credential_profile_id", "resource_class", "profile_epoch", "profile_snapshot_hash", "lease_not_before_epoch", "lease_expires_at_epoch", "lease_binding_hash")


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def derive_credential_lease_id(request: Mapping[str, Any]) -> str:
    return "cred-lease-" + canonical_hash({field: request.get(field) for field in REQUEST_BINDING_FIELDS})[:32]


def _profile_hash(profile: Mapping[str, Any]) -> str:
    return canonical_hash({k: deepcopy(v) for k, v in profile.items() if k != "profile_snapshot_hash"})


def _hash_valid(value: Mapping[str, Any], hash_field: str) -> bool:
    if not isinstance(value, Mapping):
        return False
    supplied = value.get(hash_field)
    if not isinstance(supplied, str) or not supplied:
        return False
    material = deepcopy(dict(value))
    material.pop(hash_field, None)
    return canonical_hash(material) == supplied


def _derive_remote_idempotency_key(terminal_execution_id: str, binding_hash: str) -> str:
    return canonical_hash({"domain": "integrated-governed-mvp-slice8-remote-idempotency", "terminal_execution_id": terminal_execution_id, "binding_hash": binding_hash})


class ReferenceCredentialBroker:
    """Deterministic local broker. Synthetic raw secret values remain memory-only."""

    def __init__(self, db_path: str | Path, *, secrets: Mapping[tuple[str, str], str]):
        self.db_path = Path(db_path)
        self.secrets = dict(secrets)
        self._failure_detail: str | None = None
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS broker_handles (credential_lease_id TEXT PRIMARY KEY, provider_id TEXT NOT NULL, credential_profile_id TEXT NOT NULL, opaque_secret_handle TEXT NOT NULL UNIQUE)")
            con.execute("CREATE TABLE IF NOT EXISTS broker_consumptions (id INTEGER PRIMARY KEY AUTOINCREMENT, credential_lease_id TEXT NOT NULL, opaque_secret_handle TEXT NOT NULL)")

    def set_failure_detail(self, detail: str | None) -> None:
        self._failure_detail = detail

    def _redact(self, text: str) -> str:
        for secret in self.secrets.values():
            if secret:
                text = text.replace(secret, "[REDACTED]")
        return text

    def issue_handle(self, provider_id: str, credential_profile_id: str, credential_lease_id: str) -> str:
        if self._failure_detail is not None:
            raise RuntimeError(self._redact(self._failure_detail))
        if (provider_id, credential_profile_id) not in self.secrets:
            raise KeyError("credential profile has no reference secret")
        with self._connect() as con:
            row = con.execute("SELECT provider_id,credential_profile_id,opaque_secret_handle FROM broker_handles WHERE credential_lease_id=?", (credential_lease_id,)).fetchone()
            if row is not None:
                if row["provider_id"] != provider_id or row["credential_profile_id"] != credential_profile_id:
                    raise ValueError("credential lease identity rebind")
                return str(row["opaque_secret_handle"])
            handle = "opaque-" + canonical_hash({"credential_lease_id": credential_lease_id, "provider_id": provider_id, "credential_profile_id": credential_profile_id})[:40]
            con.execute("INSERT INTO broker_handles VALUES(?,?,?,?)", (credential_lease_id, provider_id, credential_profile_id, handle))
            return handle

    def consume_handle(self, credential_lease_id: str, provider_id: str, credential_profile_id: str, handle: str) -> bool:
        if (provider_id, credential_profile_id) not in self.secrets:
            return False
        with self._connect() as con:
            row = con.execute("SELECT provider_id,credential_profile_id,opaque_secret_handle FROM broker_handles WHERE credential_lease_id=?", (credential_lease_id,)).fetchone()
            if row is None or row["provider_id"] != provider_id or row["credential_profile_id"] != credential_profile_id or row["opaque_secret_handle"] != handle:
                return False
            con.execute("INSERT INTO broker_consumptions(credential_lease_id,opaque_secret_handle) VALUES(?,?)", (credential_lease_id, handle))
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
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS credential_leases (credential_lease_id TEXT PRIMARY KEY, lease_request_id TEXT NOT NULL UNIQUE, lease_status TEXT NOT NULL, bound_lease_json TEXT NOT NULL, lease_evidence_json TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS governed_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_json TEXT NOT NULL)")

    def _record(self, value: Mapping[str, Any]) -> None:
        serialized = _canon(deepcopy(dict(value)))
        for secret in self.broker.secrets.values():
            if secret:
                serialized = serialized.replace(secret, "[REDACTED]")
        with self._connect() as con:
            con.execute("INSERT INTO governed_events(event_json) VALUES(?)", (serialized,))

    def governed_records(self) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT event_json FROM governed_events ORDER BY id").fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def _result(self, state: str, *, successful_lease: bool = False, bound_lease=None, lease_evidence=None, reason: str = "") -> dict[str, Any]:
        result = {"state": state, "reason": reason, "successful_lease": successful_lease, "production_side_effect_claimed": False, "bound_lease": deepcopy(bound_lease), "lease_evidence": deepcopy(lease_evidence)}
        self._record(result)
        return result

    def _upstream_valid(self, upstream: Mapping[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        if not isinstance(upstream, Mapping) or upstream.get("state") not in UPSTREAM_SUCCESS_STATES or upstream.get("successful_remote_completion") is not True:
            return False, None
        if upstream.get("production_remote_side_effect_claimed") is not False or not _hash_valid(upstream, "result_hash"):
            return False, None
        bound = upstream.get("bound_remote_execution")
        evidence = upstream.get("remote_completion_evidence")
        if not isinstance(bound, Mapping) or not isinstance(evidence, Mapping) or not _hash_valid(evidence, "remote_completion_hash"):
            return False, None
        for field in UPSTREAM_LINEAGE_FIELDS:
            if field not in bound or evidence.get(field) != bound.get(field):
                return False, None
        for field in ("terminal_execution_id", "project_id", "task_id", "effect_id", "action", "artifact_sha", "slice7_completion_hash", "remote_idempotency_key"):
            if not isinstance(bound.get(field), str) or not bound.get(field):
                return False, None
        version = bound.get("state_version")
        if not isinstance(version, int) or isinstance(version, bool) or version < 0:
            return False, None
        binding_material = {k: deepcopy(v) for k, v in bound.items() if k != "remote_idempotency_key"}
        binding_hash = evidence.get("binding_hash")
        if not isinstance(binding_hash, str) or canonical_hash(binding_material) != binding_hash:
            return False, None
        if bound.get("remote_idempotency_key") != _derive_remote_idempotency_key(str(bound["terminal_execution_id"]), binding_hash):
            return False, None
        remote_result = evidence.get("remote_result")
        if not isinstance(remote_result, Mapping) or remote_result.get("status") != "REMOTE_REFERENCE_APPLIED" or evidence.get("remote_result_digest") != canonical_hash(remote_result):
            return False, None
        if evidence.get("production_remote_side_effect_claimed") is not False:
            return False, None
        lineage = {k: deepcopy(v) for k, v in bound.items()}
        lineage["terminal_binding_hash"] = binding_hash
        return True, lineage

    def _profile_valid(self, profile: Mapping[str, Any], now_epoch: float) -> bool:
        required = ("provider_id", "credential_profile_id", "profile_status", "allowed_actions", "allowed_project_ids", "allowed_resource_classes", "profile_epoch", "not_before_epoch", "expires_at_epoch", "profile_snapshot_hash")
        if not isinstance(profile, Mapping) or any(field not in profile for field in required) or profile.get("profile_status") != "ACTIVE":
            return False
        if not isinstance(profile.get("profile_epoch"), int) or isinstance(profile.get("profile_epoch"), bool):
            return False
        try:
            now, not_before, expires = float(now_epoch), float(profile["not_before_epoch"]), float(profile["expires_at_epoch"])
        except (TypeError, ValueError):
            return False
        return not_before <= now < expires and profile.get("profile_snapshot_hash") == _profile_hash(profile)

    def _raw_secret_supplied(self, request: Mapping[str, Any]) -> bool:
        return any(str(key).lower().replace("-", "_") in RAW_SECRET_FIELDS and value not in (None, "") for key, value in request.items())

    def _replacement_identity_supplied(self, request: Mapping[str, Any]) -> bool:
        allowed = set(REQUEST_BINDING_FIELDS)
        for key, value in request.items():
            if key in allowed or value in (None, ""):
                continue
            normalized = str(key).lower()
            if "provider_id" in normalized or "credential_profile_id" in normalized:
                return True
        return False

    def _request_lineage_matches(self, request: Mapping[str, Any], lineage: Mapping[str, Any]) -> bool:
        return all(request.get(field) == lineage.get(field) for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "terminal_execution_id", "terminal_binding_hash"))

    def _scope_allowed(self, request: Mapping[str, Any], profile: Mapping[str, Any]) -> bool:
        return request.get("project_id") in profile.get("allowed_project_ids", []) and request.get("action") in profile.get("allowed_actions", []) and request.get("resource_class") in profile.get("allowed_resource_classes", [])

    def _load_by_request(self, request_id: str):
        with self._connect() as con:
            row = con.execute("SELECT credential_lease_id,lease_status,bound_lease_json,lease_evidence_json FROM credential_leases WHERE lease_request_id=?", (request_id,)).fetchone()
        return None if row is None else {"credential_lease_id": row["credential_lease_id"], "lease_status": row["lease_status"], "bound_lease": json.loads(row["bound_lease_json"]), "lease_evidence": json.loads(row["lease_evidence_json"])}

    def _load_by_id(self, lease_id: str):
        with self._connect() as con:
            row = con.execute("SELECT lease_status,bound_lease_json,lease_evidence_json FROM credential_leases WHERE credential_lease_id=?", (lease_id,)).fetchone()
        return None if row is None else {"lease_status": row["lease_status"], "bound_lease": json.loads(row["bound_lease_json"]), "lease_evidence": json.loads(row["lease_evidence_json"])}

    def issue(self, *, upstream_result: Mapping[str, Any], lease_request: Mapping[str, Any], current_profile: Mapping[str, Any], now_epoch: float) -> dict[str, Any]:
        valid_upstream, lineage = self._upstream_valid(upstream_result)
        if not valid_upstream or lineage is None:
            return self._result("DENY_UPSTREAM_BINDING", reason="canonical accepted Slice8 completion required")
        if not isinstance(lease_request, Mapping):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="lease request malformed")
        if self._raw_secret_supplied(lease_request):
            return self._result("DENY_RAW_SECRET_INPUT", reason="raw credential material forbidden")
        if self._replacement_identity_supplied(lease_request):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="caller replacement credential identity forbidden")
        if not self._request_lineage_matches(lease_request, lineage):
            return self._result("DENY_SCOPE_WIDENING", reason="request changes accepted terminal lineage")
        if lease_request.get("provider_id") != current_profile.get("provider_id") or lease_request.get("credential_profile_id") != current_profile.get("credential_profile_id"):
            return self._result("DENY_CREDENTIAL_PROFILE", reason="credential profile identity substitution")
        if not self._profile_valid(current_profile, now_epoch):
            return self._result("DENY_PROFILE_STALE_OR_REVOKED", reason="credential profile not currently valid")
        if not self._scope_allowed(lease_request, current_profile):
            return self._result("DENY_SCOPE_WIDENING", reason="credential profile scope does not cover request")
        request_id = lease_request.get("lease_request_id")
        if not isinstance(request_id, str) or not request_id:
            return self._result("DENY_CREDENTIAL_PROFILE", reason="lease request identity required")
        existing = self._load_by_request(request_id)
        if existing is not None:
            stored = existing["bound_lease"]
            if any(stored.get(field) != lease_request.get(field) for field in REQUEST_BINDING_FIELDS):
                return self._result("DENY_LEASE_REBIND", reason="lease request rebind")
            now = float(now_epoch)
            if existing["lease_status"] == "REVOKED":
                return self._result("LEASE_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease revoked")
            if now >= float(stored["lease_expires_at_epoch"]):
                return self._result("LEASE_EXPIRED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease expired; fresh request identity required")
            return self._result("LEASE_REPLAYED", successful_lease=True, bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="exact lease replay")
        lease_id = derive_credential_lease_id(lease_request)
        try:
            handle = self.broker.issue_handle(str(lease_request["provider_id"]), str(lease_request["credential_profile_id"]), lease_id)
        except Exception as exc:
            return self._result("DENY_CREDENTIAL_PROFILE", reason=f"reference broker denied: {exc}")
        now = float(now_epoch)
        bound_lease = {**{field: deepcopy(lease_request.get(field)) for field in REQUEST_BINDING_FIELDS}, "credential_lease_id": lease_id, "profile_epoch": current_profile["profile_epoch"], "profile_snapshot_hash": current_profile["profile_snapshot_hash"], "lease_not_before_epoch": now, "lease_expires_at_epoch": min(now + LEASE_TTL_SECONDS, float(current_profile["expires_at_epoch"])), "opaque_secret_handle": handle}
        bound_lease["lease_binding_hash"] = canonical_hash({k: deepcopy(v) for k, v in bound_lease.items() if k not in {"opaque_secret_handle", "lease_binding_hash"}})
        evidence_body = {k: deepcopy(v) for k, v in bound_lease.items() if k != "opaque_secret_handle"}
        evidence_body["opaque_secret_handle"] = bound_lease["opaque_secret_handle"]
        evidence_body["production_side_effect_claimed"] = False
        lease_evidence = {**evidence_body, "lease_evidence_hash": canonical_hash(evidence_body)}
        with self._connect() as con:
            con.execute("INSERT INTO credential_leases VALUES(?,?,?,?,?)", (lease_id, request_id, "ACTIVE", _canon(bound_lease), _canon(lease_evidence)))
        return self._result("LEASE_ISSUED", successful_lease=True, bound_lease=bound_lease, lease_evidence=lease_evidence, reason="bounded reference lease issued")

    def revoke(self, credential_lease_id: str) -> None:
        with self._connect() as con:
            con.execute("UPDATE credential_leases SET lease_status='REVOKED' WHERE credential_lease_id=?", (credential_lease_id,))
        self._record({"state": "LEASE_REVOKED", "credential_lease_id": credential_lease_id, "production_side_effect_claimed": False})

    def consume(self, *, upstream_result: Mapping[str, Any], lease_result: Mapping[str, Any], current_profile: Mapping[str, Any], now_epoch: float) -> dict[str, Any]:
        valid_upstream, lineage = self._upstream_valid(upstream_result)
        if not valid_upstream or lineage is None:
            return self._result("DENY_UPSTREAM_BINDING", reason="canonical accepted Slice8 completion required")
        supplied = lease_result.get("bound_lease") if isinstance(lease_result, Mapping) else None
        if not isinstance(supplied, Mapping):
            return self._result("LEASE_CONSUMPTION_DENIED", reason="lease result malformed")
        lease_id = supplied.get("credential_lease_id")
        if not isinstance(lease_id, str) or not lease_id:
            return self._result("LEASE_CONSUMPTION_DENIED", reason="lease identity missing")
        existing = self._load_by_id(lease_id)
        if existing is None:
            return self._result("LEASE_CONSUMPTION_DENIED", reason="unknown credential lease")
        stored = existing["bound_lease"]
        if any(supplied.get(field) != stored.get(field) for field in LEASE_REBIND_FIELDS):
            return self._result("DENY_LEASE_REBIND", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease binding changed")
        if any(stored.get(field) != lineage.get(field) for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "terminal_execution_id", "terminal_binding_hash")):
            return self._result("DENY_UPSTREAM_BINDING", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="upstream lineage changed after lease issuance")
        if current_profile.get("profile_status") == "REVOKED" or existing["lease_status"] == "REVOKED":
            return self._result("LEASE_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease/profile revoked")
        if not self._profile_valid(current_profile, now_epoch):
            return self._result("DENY_PROFILE_STALE_OR_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="credential profile not currently valid")
        if current_profile.get("provider_id") != stored.get("provider_id") or current_profile.get("credential_profile_id") != stored.get("credential_profile_id") or current_profile.get("profile_epoch") != stored.get("profile_epoch") or current_profile.get("profile_snapshot_hash") != stored.get("profile_snapshot_hash"):
            return self._result("DENY_PROFILE_STALE_OR_REVOKED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="profile epoch/snapshot changed")
        if float(now_epoch) >= float(stored["lease_expires_at_epoch"]):
            with self._connect() as con:
                con.execute("UPDATE credential_leases SET lease_status='EXPIRED' WHERE credential_lease_id=?", (lease_id,))
            return self._result("LEASE_EXPIRED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="lease expired")
        if supplied.get("opaque_secret_handle") != stored.get("opaque_secret_handle"):
            return self._result("LEASE_CONSUMPTION_DENIED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="opaque handle mismatch")
        if not self._scope_allowed(stored, current_profile):
            return self._result("DENY_SCOPE_WIDENING", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="profile scope changed")
        if not self.broker.consume_handle(lease_id, str(stored["provider_id"]), str(stored["credential_profile_id"]), str(stored["opaque_secret_handle"])):
            return self._result("LEASE_CONSUMPTION_DENIED", bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="reference broker rejected opaque handle")
        with self._connect() as con:
            con.execute("UPDATE credential_leases SET lease_status='CONSUMED' WHERE credential_lease_id=?", (lease_id,))
        return self._result("LEASE_CONSUMED_REFERENCE_ONLY", successful_lease=True, bound_lease=stored, lease_evidence=existing["lease_evidence"], reason="reference credential consumed; no production side effect performed")
