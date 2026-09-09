from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Mapping

RAW_SECRET_FIELDS = {"api_key", "apikey", "token", "password", "secret", "raw_secret"}
UPSTREAM_SUCCESS_STATES = {"REMOTE_EXECUTION_COMPLETED", "REMOTE_EXECUTION_RECONCILED", "REMOTE_EXECUTION_REPLAYED"}
LEASE_SUCCESS_STATES = {"LEASE_ISSUED", "LEASE_REPLAYED", "LEASE_CONSUMED_REFERENCE_ONLY"}
IDEMPOTENCY_FIELDS = (
    "side_effect_request_id", "project_id", "task_id", "effect_id", "terminal_execution_id",
    "remote_idempotency_key", "credential_lease_id", "credential_profile_id", "provider_id", "endpoint_id",
    "action", "resource_id", "artifact_sha", "state_version", "payload_digest", "authority_snapshot_hash",
    "lease_evidence_hash",
)


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def derive_external_idempotency_key(request: Mapping[str, Any]) -> str:
    material = {field: deepcopy(request.get(field)) for field in IDEMPOTENCY_FIELDS}
    return canonical_hash({"domain": "integrated-governed-mvp-slice10-external-idempotency", "binding": material})


def _hash_valid(value: Mapping[str, Any], hash_field: str) -> bool:
    if not isinstance(value, Mapping):
        return False
    supplied = value.get(hash_field)
    if not isinstance(supplied, str) or not supplied:
        return False
    material = deepcopy(dict(value))
    material.pop(hash_field, None)
    return canonical_hash(material) == supplied


def _sanitize_text(text: str) -> str:
    return re.sub(
        r"(?i)(api[_-]?key|token|password|secret|raw[_-]?secret)\s*[=:]\s*([^\s,;\"'}]+)",
        r"\1=[REDACTED]",
        str(text),
    )


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, Mapping):
        return {str(k): _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(v) for v in value]
    return deepcopy(value)


class TimeoutBeforeCommit(RuntimeError):
    pass


class TimeoutAfterCommit(RuntimeError):
    pass


class SimulatedCrash(RuntimeError):
    pass


class ReferenceExternalProvider:
    """Safe deterministic provider whose committed-effect state is caller-external."""

    def __init__(self, db_path: str | Path, *, allowed_targets: set[tuple[str, str]]):
        self.db_path = Path(db_path)
        self.allowed_targets = set(allowed_targets)
        self.mode = "success"
        self.failure_detail: str | None = None
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS effects (external_idempotency_key TEXT PRIMARY KEY, binding_hash TEXT NOT NULL, result_json TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS dispatches (id INTEGER PRIMARY KEY AUTOINCREMENT, external_idempotency_key TEXT NOT NULL, record_json TEXT NOT NULL)")

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def set_failure_detail(self, detail: str | None) -> None:
        self.failure_detail = detail

    def accepts_target(self, provider_id: str, endpoint_id: str) -> bool:
        return (provider_id, endpoint_id) in self.allowed_targets

    def _record_dispatch(self, key: str, value: Mapping[str, Any]) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO dispatches(external_idempotency_key,record_json) VALUES(?,?)",
                (key, _canon(_sanitize_value(value))),
            )

    def dispatch_count(self) -> int:
        with self._connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0])

    def effect_count(self) -> int:
        with self._connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM effects").fetchone()[0])

    def records(self) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT record_json FROM dispatches ORDER BY id").fetchall()
        return [json.loads(row["record_json"]) for row in rows]

    def lookup(self, external_idempotency_key: str) -> dict[str, Any] | None:
        with self._connect() as con:
            row = con.execute("SELECT result_json FROM effects WHERE external_idempotency_key=?", (external_idempotency_key,)).fetchone()
        return None if row is None else json.loads(row["result_json"])

    def dispatch(self, request: Mapping[str, Any]) -> dict[str, Any]:
        key = str(request["external_idempotency_key"])
        self._record_dispatch(key, {
            "provider_id": request.get("provider_id"),
            "endpoint_id": request.get("endpoint_id"),
            "mode": self.mode,
            "detail": self.failure_detail,
        })
        if self.failure_detail is not None:
            return {"http_status": 500, "provider_status": "ERROR", "provider_committed": False, "detail": _sanitize_text(self.failure_detail)}
        if self.mode == "timeout_before_commit":
            raise TimeoutBeforeCommit("reference timeout before provider commit")
        if self.mode == "http_5xx":
            return {"http_status": 503, "provider_status": "ERROR", "provider_committed": False}
        if self.mode == "success_without_commit":
            return {
                "http_status": 200,
                "provider_status": "SUCCESS",
                "provider_committed": False,
                "provider_id": request.get("provider_id"),
                "endpoint_id": request.get("endpoint_id"),
                "external_idempotency_key": key,
            }

        existing = self.lookup(key)
        if existing is None:
            binding = {field: deepcopy(request.get(field)) for field in IDEMPOTENCY_FIELDS}
            binding_hash = canonical_hash(binding)
            result = {
                "http_status": 200,
                "provider_status": "SUCCESS",
                "provider_committed": True,
                "provider_id": request.get("provider_id"),
                "endpoint_id": request.get("endpoint_id"),
                "external_idempotency_key": key,
                "external_effect_id": "reference-effect-" + canonical_hash({"key": key, "binding_hash": binding_hash})[:24],
                "action": request.get("action"),
                "resource_id": request.get("resource_id"),
                "artifact_sha": request.get("artifact_sha"),
                "state_version": request.get("state_version"),
                "payload_digest": request.get("payload_digest"),
                "credential_lease_id": request.get("credential_lease_id"),
                "binding_hash": binding_hash,
            }
            result["provider_result_digest"] = canonical_hash({k: deepcopy(v) for k, v in result.items() if k != "provider_result_digest"})
            with self._connect() as con:
                con.execute("INSERT INTO effects VALUES(?,?,?)", (key, binding_hash, _canon(result)))
            existing = result

        if self.mode == "timeout_after_commit":
            raise TimeoutAfterCommit("reference timeout after provider commit")
        if self.mode == "mismatched_response":
            changed = deepcopy(existing)
            changed["endpoint_id"] = "mismatched-endpoint"
            return changed
        return deepcopy(existing)


class ExternalSideEffectGateway:
    def __init__(self, db_path: str | Path, provider: ReferenceExternalProvider):
        self.db_path = Path(db_path)
        self.provider = provider
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS intents (external_idempotency_key TEXT PRIMARY KEY, binding_json TEXT NOT NULL, status TEXT NOT NULL, evidence_json TEXT)")
            con.execute("CREATE TABLE IF NOT EXISTS governed_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_json TEXT NOT NULL)")

    def _record(self, value: Mapping[str, Any]) -> None:
        with self._connect() as con:
            con.execute("INSERT INTO governed_events(event_json) VALUES(?)", (_canon(_sanitize_value(value)),))

    def governed_records(self) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT event_json FROM governed_events ORDER BY id").fetchall()
        return [json.loads(row["event_json"]) for row in rows]

    def _result(self, state: str, *, reason: str = "", evidence=None, external_idempotency_key=None) -> dict[str, Any]:
        result = {
            "state": state,
            "reason": _sanitize_text(reason),
            "successful_external_effect": state in {"REFERENCE_EFFECT_APPLIED", "REFERENCE_EFFECT_REPLAYED", "RECONCILED_EXISTING_EFFECT"},
            "terminal_authority_granted": False,
            "production_side_effect_claimed": False,
            "external_idempotency_key": external_idempotency_key,
            "external_effect_evidence": deepcopy(evidence),
        }
        self._record(result)
        return result

    def _valid_upstream(self, upstream: Mapping[str, Any]) -> bool:
        if not isinstance(upstream, Mapping) or upstream.get("state") not in UPSTREAM_SUCCESS_STATES or upstream.get("successful_remote_completion") is not True:
            return False
        if upstream.get("production_remote_side_effect_claimed") is not False or not _hash_valid(upstream, "result_hash"):
            return False
        bound = upstream.get("bound_remote_execution")
        evidence = upstream.get("remote_completion_evidence")
        if not isinstance(bound, Mapping) or not isinstance(evidence, Mapping) or not _hash_valid(evidence, "remote_completion_hash"):
            return False
        binding_hash = evidence.get("binding_hash")
        if binding_hash != canonical_hash({k: deepcopy(v) for k, v in bound.items() if k != "remote_idempotency_key"}):
            return False
        expected_key = canonical_hash({
            "domain": "integrated-governed-mvp-slice8-remote-idempotency",
            "terminal_execution_id": bound.get("terminal_execution_id"),
            "binding_hash": binding_hash,
        })
        if bound.get("remote_idempotency_key") != expected_key or evidence.get("remote_idempotency_key") != expected_key:
            return False
        remote_result = evidence.get("remote_result")
        if not isinstance(remote_result, Mapping) or remote_result.get("status") != "REMOTE_REFERENCE_APPLIED":
            return False
        if remote_result.get("production_remote_side_effect_claimed") is not False:
            return False
        return evidence.get("remote_result_digest") == canonical_hash(remote_result)

    def _upstream_matches_request(self, upstream: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
        if not self._valid_upstream(upstream):
            return False
        bound = upstream["bound_remote_execution"]
        return all(request.get(field) == bound.get(field) for field in (
            "project_id", "task_id", "effect_id", "terminal_execution_id", "remote_idempotency_key",
            "action", "artifact_sha", "state_version",
        ))

    def _profile_hash_valid(self, profile: Mapping[str, Any]) -> bool:
        if not isinstance(profile, Mapping):
            return False
        material = deepcopy(dict(profile))
        supplied = material.pop("profile_snapshot_hash", None)
        return isinstance(supplied, str) and supplied == canonical_hash(material)

    def _profile_current_valid(self, profile: Mapping[str, Any], now_epoch: float) -> bool:
        if not self._profile_hash_valid(profile) or profile.get("profile_status") != "ACTIVE":
            return False
        try:
            return float(profile["not_before_epoch"]) <= float(now_epoch) < float(profile["expires_at_epoch"])
        except Exception:
            return False

    def _lease_identity_valid(self, lease: Mapping[str, Any], upstream: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
        if not isinstance(lease, Mapping) or lease.get("state") not in LEASE_SUCCESS_STATES or lease.get("successful_lease") is not True or lease.get("production_side_effect_claimed") is not False:
            return False
        bound = lease.get("bound_lease")
        evidence = lease.get("lease_evidence")
        if not isinstance(bound, Mapping) or not isinstance(evidence, Mapping) or not _hash_valid(evidence, "lease_evidence_hash"):
            return False
        if evidence.get("production_side_effect_claimed") is not False:
            return False
        binding_hash = bound.get("lease_binding_hash")
        binding_material = {k: deepcopy(v) for k, v in bound.items() if k not in {"opaque_secret_handle", "lease_binding_hash"}}
        if not isinstance(binding_hash, str) or binding_hash != canonical_hash(binding_material):
            return False
        for key, value in bound.items():
            if evidence.get(key) != value:
                return False
        if request.get("lease_evidence_hash") != evidence.get("lease_evidence_hash"):
            return False
        if request.get("credential_lease_id") != bound.get("credential_lease_id"):
            return False
        if request.get("credential_profile_id") != bound.get("credential_profile_id") or request.get("provider_id") != bound.get("provider_id"):
            return False
        if not self._valid_upstream(upstream):
            return False
        remote = upstream["bound_remote_execution"]
        terminal_binding_hash = upstream["remote_completion_evidence"]["binding_hash"]
        expected = {
            "project_id": remote.get("project_id"),
            "task_id": remote.get("task_id"),
            "effect_id": remote.get("effect_id"),
            "action": remote.get("action"),
            "artifact_sha": remote.get("artifact_sha"),
            "state_version": remote.get("state_version"),
            "terminal_execution_id": remote.get("terminal_execution_id"),
            "terminal_binding_hash": terminal_binding_hash,
        }
        return all(bound.get(k) == v for k, v in expected.items())

    def _lease_current_valid(self, lease: Mapping[str, Any], profile: Mapping[str, Any], upstream: Mapping[str, Any], request: Mapping[str, Any], now_epoch: float) -> bool:
        if not self._lease_identity_valid(lease, upstream, request) or not self._profile_current_valid(profile, now_epoch):
            return False
        bound = lease["bound_lease"]
        if profile.get("provider_id") != bound.get("provider_id") or profile.get("credential_profile_id") != bound.get("credential_profile_id"):
            return False
        if profile.get("profile_epoch") != bound.get("profile_epoch") or profile.get("profile_snapshot_hash") != bound.get("profile_snapshot_hash"):
            return False
        if request.get("project_id") not in profile.get("allowed_project_ids", []) or request.get("action") not in profile.get("allowed_actions", []):
            return False
        if bound.get("resource_class") not in profile.get("allowed_resource_classes", []):
            return False
        try:
            return float(bound["lease_not_before_epoch"]) <= float(now_epoch) < float(bound["lease_expires_at_epoch"])
        except Exception:
            return False

    def _authority_valid(self, authority: Mapping[str, Any], request: Mapping[str, Any], now_epoch: float) -> bool:
        if not isinstance(authority, Mapping) or authority.get("authority_status") != "ACTIVE":
            return False
        material = deepcopy(dict(authority))
        supplied = material.pop("authority_snapshot_hash", None)
        if supplied != canonical_hash(material) or supplied != request.get("authority_snapshot_hash"):
            return False
        try:
            if not (float(authority["not_before_epoch"]) <= float(now_epoch) < float(authority["expires_at_epoch"])):
                return False
        except Exception:
            return False
        return all(authority.get(field) == request.get(field) for field in (
            "project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version",
        ))

    def _raw_secret_supplied(self, request: Mapping[str, Any]) -> bool:
        return any(str(k).lower().replace("-", "_") in RAW_SECRET_FIELDS and v not in (None, "") for k, v in request.items())

    def _binding(self, request: Mapping[str, Any]) -> dict[str, Any]:
        return {field: deepcopy(request.get(field)) for field in IDEMPOTENCY_FIELDS}

    def _scope_valid(self, upstream: Mapping[str, Any], lease: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
        if not self._upstream_matches_request(upstream, request):
            return False
        bound_lease = lease.get("bound_lease") if isinstance(lease, Mapping) else None
        if not isinstance(bound_lease, Mapping):
            return False
        if request.get("credential_lease_id") != bound_lease.get("credential_lease_id") or request.get("credential_profile_id") != bound_lease.get("credential_profile_id"):
            return False
        if request.get("resource_id") != f"repository:{request.get('artifact_sha')}":
            return False
        return request.get("payload_digest") == canonical_hash({"artifact_sha": request.get("artifact_sha"), "action": request.get("action")})

    def _load_intent(self, key: str):
        with self._connect() as con:
            row = con.execute("SELECT binding_json,status,evidence_json FROM intents WHERE external_idempotency_key=?", (key,)).fetchone()
        if row is None:
            return None
        return {
            "binding": json.loads(row["binding_json"]),
            "status": row["status"],
            "evidence": None if row["evidence_json"] is None else json.loads(row["evidence_json"]),
        }

    def _store_intent(self, key: str, binding: Mapping[str, Any]) -> None:
        with self._connect() as con:
            con.execute("INSERT INTO intents(external_idempotency_key,binding_json,status,evidence_json) VALUES(?,?,?,NULL)", (key, _canon(binding), "IN_PROGRESS"))

    def _set_status(self, key: str, status: str, evidence=None) -> None:
        with self._connect() as con:
            con.execute("UPDATE intents SET status=?, evidence_json=? WHERE external_idempotency_key=?", (status, None if evidence is None else _canon(evidence), key))

    def _provider_response_valid(self, response: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
        if not isinstance(response, Mapping) or response.get("provider_committed") is not True:
            return False
        for field in ("provider_id", "endpoint_id", "external_idempotency_key", "action", "resource_id", "artifact_sha", "state_version", "payload_digest", "credential_lease_id"):
            if response.get(field) != request.get(field):
                return False
        digest = response.get("provider_result_digest")
        material = {k: deepcopy(v) for k, v in response.items() if k != "provider_result_digest"}
        return isinstance(digest, str) and digest == canonical_hash(material) and isinstance(response.get("external_effect_id"), str)

    def _make_evidence(self, request: Mapping[str, Any], response: Mapping[str, Any]) -> dict[str, Any]:
        body = {field: deepcopy(request.get(field)) for field in IDEMPOTENCY_FIELDS}
        body.update({
            "external_idempotency_key": request.get("external_idempotency_key"),
            "external_effect_id": response.get("external_effect_id"),
            "provider_result_digest": response.get("provider_result_digest"),
            "provider_committed": True,
            "production_side_effect_claimed": False,
            "terminal_authority_granted": False,
        })
        return {**body, "external_effect_evidence_hash": canonical_hash(body)}

    def validate_external_effect_evidence(self, evidence: Mapping[str, Any]) -> bool:
        return (
            _hash_valid(evidence, "external_effect_evidence_hash")
            and evidence.get("provider_committed") is True
            and evidence.get("production_side_effect_claimed") is False
            and evidence.get("terminal_authority_granted") is False
        )

    def execute(self, *, upstream_result: Mapping[str, Any], lease_result: Mapping[str, Any], current_profile: Mapping[str, Any], current_authority: Mapping[str, Any], side_effect_request: Mapping[str, Any], now_epoch: float, crash_point: str | None = None) -> dict[str, Any]:
        if not self._valid_upstream(upstream_result):
            return self._result("DENY_UPSTREAM_LINEAGE", reason="canonical accepted Slice8 lineage required")
        if not isinstance(side_effect_request, Mapping) or self._raw_secret_supplied(side_effect_request):
            return self._result("DENY_AUTHORITY_OR_LEASE", reason="malformed request or raw secret input")

        lease_bound = lease_result.get("bound_lease") if isinstance(lease_result, Mapping) else None
        if not isinstance(lease_bound, Mapping):
            return self._result("DENY_AUTHORITY_OR_LEASE", reason="valid Slice9 lease material required")
        if side_effect_request.get("provider_id") != lease_bound.get("provider_id") or side_effect_request.get("credential_profile_id") != lease_bound.get("credential_profile_id"):
            return self._result("DENY_TARGET_SUBSTITUTION", reason="provider or credential profile substitution")
        if not self.provider.accepts_target(str(side_effect_request.get("provider_id")), str(side_effect_request.get("endpoint_id"))):
            return self._result("DENY_TARGET_SUBSTITUTION", reason="provider or endpoint substitution")

        expected_key = derive_external_idempotency_key(side_effect_request)
        supplied_key = side_effect_request.get("external_idempotency_key")
        if supplied_key != expected_key:
            return self._result("DENY_IDEMPOTENCY_REBIND", reason="external idempotency key is not platform-derived", external_idempotency_key=supplied_key)
        binding = self._binding(side_effect_request)
        existing = self._load_intent(expected_key)
        if existing is not None and existing["binding"] != binding:
            return self._result("DENY_IDEMPOTENCY_REBIND", reason="external idempotency key rebind", external_idempotency_key=expected_key)
        if not self._scope_valid(upstream_result, lease_result, side_effect_request):
            return self._result("DENY_SCOPE_WIDENING", reason="external side-effect scope or payload widened", external_idempotency_key=expected_key)
        if not self._lease_current_valid(lease_result, current_profile, upstream_result, side_effect_request, now_epoch) or not self._authority_valid(current_authority, side_effect_request, now_epoch):
            return self._result("DENY_AUTHORITY_OR_LEASE", reason="current authority and credential lease required", external_idempotency_key=expected_key)

        if existing is not None:
            if existing["status"] == "COMPLETED" and existing["evidence"] is not None:
                return self._result("REFERENCE_EFFECT_REPLAYED", evidence=existing["evidence"], external_idempotency_key=expected_key, reason="exact completed external effect replay")
            if existing["status"] in {"UNKNOWN", "IN_PROGRESS"}:
                return self._result("OUTCOME_UNKNOWN_RECONCILE_REQUIRED", external_idempotency_key=expected_key, reason="existing ambiguous provider outcome requires reconciliation")
        else:
            self._store_intent(expected_key, binding)

        if crash_point == "before_dispatch":
            raise SimulatedCrash("before provider dispatch")
        self._record({
            "state": "EXTERNAL_DISPATCH_ATTEMPTED",
            "external_idempotency_key": expected_key,
            "binding_hash": canonical_hash(binding),
            "production_side_effect_claimed": False,
            "terminal_authority_granted": False,
        })
        try:
            response = self.provider.dispatch(side_effect_request)
        except TimeoutBeforeCommit as exc:
            self._set_status(expected_key, "FAILED")
            return self._result("REFERENCE_EFFECT_FAILED", reason=str(exc), external_idempotency_key=expected_key)
        except TimeoutAfterCommit as exc:
            self._set_status(expected_key, "UNKNOWN")
            return self._result("OUTCOME_UNKNOWN_RECONCILE_REQUIRED", reason=str(exc), external_idempotency_key=expected_key)

        if crash_point == "after_dispatch_before_response":
            raise SimulatedCrash("after provider dispatch before response interpretation")
        if crash_point == "after_provider_commit_before_local_completion" and isinstance(response, Mapping) and response.get("provider_committed") is True:
            raise SimulatedCrash("after provider commit before local completion")
        if not isinstance(response, Mapping) or int(response.get("http_status", 500)) >= 500 or response.get("provider_committed") is not True:
            self._set_status(expected_key, "FAILED")
            reason = str(response.get("detail", "provider did not commit reference effect")) if isinstance(response, Mapping) else "provider response malformed"
            return self._result("REFERENCE_EFFECT_FAILED", reason=reason, external_idempotency_key=expected_key)
        if not self._provider_response_valid(response, side_effect_request):
            self._set_status(expected_key, "UNKNOWN")
            return self._result("DENY_RESPONSE_INTEGRITY", reason="provider response does not match frozen external binding", external_idempotency_key=expected_key)

        evidence = self._make_evidence(side_effect_request, response)
        self._set_status(expected_key, "COMPLETED", evidence)
        if crash_point == "after_local_completion":
            raise SimulatedCrash("after durable local completion before caller response")
        return self._result("REFERENCE_EFFECT_APPLIED", evidence=evidence, external_idempotency_key=expected_key, reason="safe reference external effect applied")

    def recover(self, *, upstream_result: Mapping[str, Any], lease_result: Mapping[str, Any], current_profile: Mapping[str, Any], current_authority: Mapping[str, Any], side_effect_request: Mapping[str, Any], now_epoch: float) -> dict[str, Any]:
        key = side_effect_request.get("external_idempotency_key") if isinstance(side_effect_request, Mapping) else None
        if not isinstance(key, str) or key != derive_external_idempotency_key(side_effect_request):
            return self._result("DENY_IDEMPOTENCY_REBIND", reason="recovery key mismatch", external_idempotency_key=key)
        existing = self._load_intent(key)
        if existing is None or existing["binding"] != self._binding(side_effect_request):
            return self._result("DENY_IDEMPOTENCY_REBIND", reason="no exact durable intent for recovery", external_idempotency_key=key)
        if not self._upstream_matches_request(upstream_result, side_effect_request):
            return self._result("DENY_UPSTREAM_LINEAGE", reason="recovery lineage differs from durable external intent", external_idempotency_key=key)
        if not self._lease_identity_valid(lease_result, upstream_result, side_effect_request):
            return self._result("DENY_AUTHORITY_OR_LEASE", reason="recovery lease identity/evidence differs from durable external intent", external_idempotency_key=key)

        self._record({
            "state": "EXTERNAL_RECONCILIATION_ATTEMPTED",
            "external_idempotency_key": key,
            "binding_hash": canonical_hash(existing["binding"]),
            "production_side_effect_claimed": False,
            "terminal_authority_granted": False,
        })

        if existing["status"] == "COMPLETED" and existing["evidence"] is not None:
            return self._result("REFERENCE_EFFECT_REPLAYED", evidence=existing["evidence"], external_idempotency_key=key, reason="completed effect already durable")

        response = self.provider.lookup(key)
        if response is not None:
            if not self._provider_response_valid(response, side_effect_request):
                return self._result("DENY_RESPONSE_INTEGRITY", reason="reconciled provider state mismatches frozen binding", external_idempotency_key=key)
            evidence = self._make_evidence(side_effect_request, response)
            self._set_status(key, "COMPLETED", evidence)
            return self._result("RECONCILED_EXISTING_EFFECT", evidence=evidence, external_idempotency_key=key, reason="provider-side committed effect reconciled without mutation retry")

        if not self._lease_current_valid(lease_result, current_profile, upstream_result, side_effect_request, now_epoch) or not self._authority_valid(current_authority, side_effect_request, now_epoch):
            return self._result("DENY_AUTHORITY_OR_LEASE", reason="no committed effect found and current authority/lease does not permit retry", external_idempotency_key=key)
        return self._result("OUTCOME_UNKNOWN_RECONCILE_REQUIRED", reason="no committed provider state found; mutating retry requires explicit new execution path", external_idempotency_key=key)
