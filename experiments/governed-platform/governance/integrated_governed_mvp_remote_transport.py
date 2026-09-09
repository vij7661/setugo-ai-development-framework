"""Integrated Governed MVP Slice 8 reference remote terminal transport.

This module extends accepted Slice 7 with a deterministic loopback HTTP
boundary and a durable remote idempotency ledger. It is deliberately a local
reference transport: no production GitHub/cloud/release side effect is made.
"""
from __future__ import annotations

from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Mapping
from urllib import error as urlerror
from urllib import request as urlrequest

from integrated_governed_mvp_terminal_executor import canonical_hash


SLICE7_SUCCESS_STATES = frozenset(
    {"TERMINAL_EXECUTION_COMPLETED", "TERMINAL_EXECUTION_REPLAYED", "TERMINAL_EXECUTION_RECOVERED"}
)
TERMINAL_ACTIONS = frozenset({"RELEASE", "DEPLOY", "MERGE", "COMPLETE"})
REMOTE_SUCCESS_STATUS = "REMOTE_REFERENCE_APPLIED"
REMOTE_SUCCESS_STATES = frozenset(
    {"REMOTE_EXECUTION_COMPLETED", "REMOTE_EXECUTION_RECONCILED", "REMOTE_EXECUTION_REPLAYED"}
)


class SimulatedRemoteTransportFailure(RuntimeError):
    pass


def derive_remote_idempotency_key(terminal_execution_id: str, binding_hash: str) -> str:
    return canonical_hash(
        {
            "domain": "integrated-governed-mvp-slice8-remote-idempotency",
            "terminal_execution_id": terminal_execution_id,
            "binding_hash": binding_hash,
        }
    )


def _hash_valid(value: Mapping[str, Any], hash_field: str) -> bool:
    if not isinstance(value, Mapping):
        return False
    supplied = value.get(hash_field)
    if not isinstance(supplied, str) or not supplied:
        return False
    material = deepcopy(dict(value))
    material.pop(hash_field, None)
    return canonical_hash(material) == supplied


def _slice7_valid(result: Mapping[str, Any]) -> bool:
    if not isinstance(result, Mapping):
        return False
    if result.get("state") not in SLICE7_SUCCESS_STATES:
        return False
    if result.get("successful_completion") is not True:
        return False
    if result.get("production_side_effect_claimed") is not False:
        return False
    if not _hash_valid(result, "result_hash"):
        return False
    bound = result.get("bound_execution")
    evidence = result.get("completion_evidence")
    if not isinstance(bound, Mapping) or not isinstance(evidence, Mapping):
        return False
    if not _hash_valid(evidence, "completion_hash"):
        return False
    required_strings = ("terminal_execution_id", "project_id", "task_id", "effect_id", "artifact_sha")
    for field in required_strings:
        if not isinstance(bound.get(field), str) or not bound.get(field):
            return False
    if bound.get("action") not in TERMINAL_ACTIONS:
        return False
    version = bound.get("state_version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 0:
        return False
    for field in (
        "terminal_execution_id",
        "project_id",
        "task_id",
        "effect_id",
        "action",
        "artifact_sha",
        "state_version",
        "authorization_receipt_hash",
        "authority_snapshot_hash",
    ):
        if evidence.get(field) != bound.get(field):
            return False
    adapter_result = evidence.get("adapter_result")
    if not isinstance(adapter_result, Mapping) or adapter_result.get("status") != "LOCAL_REFERENCE_APPLIED":
        return False
    if evidence.get("production_side_effect_claimed") is not False:
        return False
    return True


def _remote_binding(slice7_result: Mapping[str, Any]) -> dict[str, Any]:
    bound = slice7_result["bound_execution"]
    evidence = slice7_result["completion_evidence"]
    return {
        "terminal_execution_id": bound["terminal_execution_id"],
        "project_id": bound["project_id"],
        "task_id": bound["task_id"],
        "effect_id": bound["effect_id"],
        "action": bound["action"],
        "artifact_sha": bound["artifact_sha"],
        "state_version": bound["state_version"],
        "slice7_completion_hash": evidence["completion_hash"],
    }


def _result(
    state: str,
    reason: str,
    binding: Mapping[str, Any] | None,
    remote_idempotency_key: str | None,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bound = deepcopy(dict(binding)) if isinstance(binding, Mapping) else {}
    if remote_idempotency_key:
        bound["remote_idempotency_key"] = remote_idempotency_key
    body = {
        "state": state,
        "reason": reason,
        "successful_remote_completion": state in REMOTE_SUCCESS_STATES,
        "production_remote_side_effect_claimed": False,
        "bound_remote_execution": bound,
        "remote_completion_evidence": deepcopy(dict(evidence)) if evidence else None,
    }
    return {**body, "result_hash": canonical_hash(body)}


def _completion_evidence(
    binding: Mapping[str, Any],
    remote_idempotency_key: str,
    remote_receipt: Mapping[str, Any],
    remote_result: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        **deepcopy(dict(binding)),
        "binding_hash": canonical_hash(binding),
        "remote_idempotency_key": remote_idempotency_key,
        "remote_receipt_hash": remote_receipt["remote_receipt_hash"],
        "remote_result_digest": canonical_hash(remote_result),
        "remote_result": deepcopy(dict(remote_result)),
        "production_remote_side_effect_claimed": False,
    }
    return {**body, "remote_completion_hash": canonical_hash(body)}


class RemoteTerminalService:
    """Durable idempotent reference remote service exposed through loopback HTTP."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._response_override: dict[str, Any] = {}
        self._forced_failure: dict[str, Any] | None = None
        self._receipt_mode = "normal"
        self._http_requests = 0
        self._control_lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS remote_effects (
                    remote_idempotency_key TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    binding_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    result_json TEXT,
                    receipt_json TEXT
                )
                """
            )

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("remote service is not started")
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> None:
        if self._server is not None:
            return
        service = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                return

            def do_POST(self) -> None:  # noqa: N802
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    payload = json.loads(self.rfile.read(length).decode("utf-8"))
                except Exception:
                    self._send(400, {"status": "MALFORMED_REQUEST"})
                    return
                with service._control_lock:
                    service._http_requests += 1
                if self.path == "/execute":
                    code, body = service._handle_execute(payload)
                elif self.path == "/reconcile":
                    code, body = service._handle_reconcile(payload)
                else:
                    code, body = 404, {"status": "NOT_FOUND"}
                self._send(code, body)

            def _send(self, code: int, body: Mapping[str, Any]) -> None:
                data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        server = self._server
        thread = self._thread
        self._server = None
        self._thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=5)

    def set_response_override(self, override: Mapping[str, Any]) -> None:
        with self._control_lock:
            self._response_override = deepcopy(dict(override))

    def set_forced_failure(self, failure: Mapping[str, Any] | None) -> None:
        with self._control_lock:
            self._forced_failure = deepcopy(dict(failure)) if failure is not None else None

    def set_receipt_mode(self, mode: str) -> None:
        with self._control_lock:
            self._receipt_mode = mode

    def http_request_count(self) -> int:
        with self._control_lock:
            return self._http_requests

    def effect_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM remote_effects WHERE state='APPLIED'").fetchone()
        return int(row["c"])

    def _validate_envelope(self, payload: Mapping[str, Any]) -> tuple[bool, dict[str, Any], str, str]:
        if not isinstance(payload, Mapping):
            return False, {}, "", ""
        binding = payload.get("binding")
        binding_hash = payload.get("binding_hash")
        key = payload.get("remote_idempotency_key")
        if not isinstance(binding, Mapping) or not isinstance(binding_hash, str) or not isinstance(key, str):
            return False, {}, "", ""
        material = dict(binding)
        if canonical_hash(material) != binding_hash:
            return False, {}, "", ""
        required = ("terminal_execution_id", "project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "slice7_completion_hash")
        if any(field not in material for field in required):
            return False, {}, "", ""
        expected_key = derive_remote_idempotency_key(str(material["terminal_execution_id"]), binding_hash)
        if key != expected_key:
            return False, {}, "", ""
        return True, material, binding_hash, key

    def _handle_execute(self, payload: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
        valid, binding, binding_hash, key = self._validate_envelope(payload)
        if not valid:
            return 400, {"status": "INVALID_BINDING"}
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM remote_effects WHERE remote_idempotency_key=?", (key,)
            ).fetchone()
            if row is not None:
                if row["binding_hash"] != binding_hash:
                    conn.rollback()
                    return 409, {"status": "IDEMPOTENCY_REBIND_DENIED"}
                state = row["state"]
                result = json.loads(row["result_json"]) if row["result_json"] else {"status": "FAILED"}
                receipt = json.loads(row["receipt_json"]) if row["receipt_json"] else None
                conn.rollback()
                return 200, self._wire_response(state, binding, result, receipt)

            with self._control_lock:
                forced = deepcopy(self._forced_failure)
            if forced is not None:
                failure = deepcopy(forced)
                conn.execute(
                    "INSERT INTO remote_effects(remote_idempotency_key,binding_hash,binding_json,state,result_json,receipt_json) VALUES(?,?,?,?,?,NULL)",
                    (key, binding_hash, json.dumps(binding, sort_keys=True, separators=(",", ":")), "FAILED", json.dumps(failure, sort_keys=True, separators=(",", ":"))),
                )
                conn.commit()
                return 200, {"status": "FAILED", "remote_result": failure, "remote_receipt": None}

            result = {
                "status": REMOTE_SUCCESS_STATUS,
                "project_id": binding["project_id"],
                "task_id": binding["task_id"],
                "effect_id": binding["effect_id"],
                "action": binding["action"],
                "artifact_sha": binding["artifact_sha"],
                "state_version": binding["state_version"],
                "production_remote_side_effect_claimed": False,
            }
            receipt_body = {
                "remote_idempotency_key": key,
                "binding_hash": binding_hash,
                "state": "APPLIED",
                "project_id": binding["project_id"],
                "task_id": binding["task_id"],
                "effect_id": binding["effect_id"],
                "action": binding["action"],
                "artifact_sha": binding["artifact_sha"],
                "state_version": binding["state_version"],
                "slice7_completion_hash": binding["slice7_completion_hash"],
                "remote_result_digest": canonical_hash(result),
            }
            receipt = {**receipt_body, "remote_receipt_hash": canonical_hash(receipt_body)}
            conn.execute(
                "INSERT INTO remote_effects(remote_idempotency_key,binding_hash,binding_json,state,result_json,receipt_json) VALUES(?,?,?,?,?,?)",
                (
                    key,
                    binding_hash,
                    json.dumps(binding, sort_keys=True, separators=(",", ":")),
                    "APPLIED",
                    json.dumps(result, sort_keys=True, separators=(",", ":")),
                    json.dumps(receipt, sort_keys=True, separators=(",", ":")),
                ),
            )
            conn.commit()
        return 200, self._wire_response("APPLIED", binding, result, receipt)

    def _wire_response(
        self,
        state: str,
        binding: Mapping[str, Any],
        result: Mapping[str, Any],
        receipt: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        response_result = deepcopy(dict(result))
        with self._control_lock:
            response_result.update(self._response_override)
            receipt_mode = self._receipt_mode
        response_receipt = deepcopy(dict(receipt)) if receipt else None
        if response_receipt is not None and response_result != result:
            response_receipt["remote_result_digest"] = canonical_hash(response_result)
            body = deepcopy(response_receipt)
            body.pop("remote_receipt_hash", None)
            response_receipt["remote_receipt_hash"] = canonical_hash(body)
        if response_receipt is not None and receipt_mode == "missing":
            response_receipt.pop("remote_receipt_hash", None)
        elif response_receipt is not None and receipt_mode == "malformed":
            response_receipt["remote_receipt_hash"] = "malformed"
        return {
            "status": state,
            "remote_result": response_result,
            "remote_receipt": response_receipt,
            "binding": deepcopy(dict(binding)),
        }

    def _handle_reconcile(self, payload: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
        key = payload.get("remote_idempotency_key") if isinstance(payload, Mapping) else None
        binding_hash = payload.get("binding_hash") if isinstance(payload, Mapping) else None
        if not isinstance(key, str) or not isinstance(binding_hash, str):
            return 400, {"status": "INVALID_RECONCILE_REQUEST"}
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM remote_effects WHERE remote_idempotency_key=?", (key,)
            ).fetchone()
        if row is None:
            return 404, {"status": "NOT_FOUND"}
        if row["binding_hash"] != binding_hash:
            return 409, {"status": "IDEMPOTENCY_REBIND_DENIED"}
        binding = json.loads(row["binding_json"])
        result = json.loads(row["result_json"]) if row["result_json"] else {"status": "FAILED"}
        receipt = json.loads(row["receipt_json"]) if row["receipt_json"] else None
        return 200, self._wire_response(row["state"], binding, result, receipt)


class RemoteTerminalTransport:
    def __init__(self, db_path: str | Path, base_url: str):
        self.db_path = str(db_path)
        self.base_url = base_url.rstrip("/")
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS remote_attempts (
                    remote_idempotency_key TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_json TEXT
                )
                """
            )

    def _post(self, path: str, payload: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        req = urlrequest.Request(
            self.base_url + path,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlrequest.urlopen(req, timeout=5) as response:
                return int(response.status), json.loads(response.read().decode("utf-8"))
        except urlerror.HTTPError as exc:
            body = exc.read().decode("utf-8")
            return int(exc.code), json.loads(body) if body else {"status": "HTTP_ERROR"}

    def _prepare(self, slice7_result: Mapping[str, Any]):
        if not _slice7_valid(slice7_result):
            return None
        binding = _remote_binding(slice7_result)
        binding_hash = canonical_hash(binding)
        key = derive_remote_idempotency_key(binding["terminal_execution_id"], binding_hash)
        return binding, binding_hash, key

    def _local_row(self, key: str):
        with self._connect() as conn:
            return conn.execute("SELECT * FROM remote_attempts WHERE remote_idempotency_key=?", (key,)).fetchone()

    def _set_local(self, key: str, binding_hash: str, status: str, evidence: Mapping[str, Any] | None = None) -> None:
        payload = json.dumps(evidence, sort_keys=True, separators=(",", ":")) if evidence else None
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute("SELECT binding_hash FROM remote_attempts WHERE remote_idempotency_key=?", (key,)).fetchone()
            if existing is not None and existing["binding_hash"] != binding_hash:
                conn.rollback()
                raise ValueError("local remote idempotency identity rebound")
            conn.execute(
                "INSERT INTO remote_attempts(remote_idempotency_key,binding_hash,status,evidence_json) VALUES(?,?,?,?) "
                "ON CONFLICT(remote_idempotency_key) DO UPDATE SET status=excluded.status,evidence_json=excluded.evidence_json",
                (key, binding_hash, status, payload),
            )
            conn.commit()

    def _validate_remote_success(
        self,
        wire: Mapping[str, Any],
        binding: Mapping[str, Any],
        binding_hash: str,
        key: str,
    ) -> tuple[bool, dict[str, Any] | None, dict[str, Any] | None]:
        if not isinstance(wire, Mapping) or wire.get("status") != "APPLIED":
            return False, None, None
        result = wire.get("remote_result")
        receipt = wire.get("remote_receipt")
        returned_binding = wire.get("binding")
        if not isinstance(result, Mapping) or not isinstance(receipt, Mapping) or not isinstance(returned_binding, Mapping):
            return False, None, None
        if dict(returned_binding) != dict(binding):
            return False, None, None
        if not _hash_valid(receipt, "remote_receipt_hash"):
            return False, None, None
        if receipt.get("remote_idempotency_key") != key or receipt.get("binding_hash") != binding_hash:
            return False, None, None
        for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version", "slice7_completion_hash"):
            if receipt.get(field) != binding.get(field):
                return False, None, None
        if result.get("status") != REMOTE_SUCCESS_STATUS:
            return False, None, None
        if result.get("production_remote_side_effect_claimed") is not False:
            return False, None, None
        for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version"):
            if result.get(field) != binding.get(field):
                return False, None, None
        if receipt.get("remote_result_digest") != canonical_hash(result):
            return False, None, None
        return True, deepcopy(dict(receipt)), deepcopy(dict(result))

    def execute(
        self,
        *,
        slice7_result: Mapping[str, Any],
        remote_idempotency_key: str | None = None,
        failure_point: str | None = None,
    ) -> dict[str, Any]:
        prepared = self._prepare(slice7_result)
        if prepared is None:
            return _result("DENY_SLICE7_BINDING", "Slice 7 completion is malformed, non-success, tampered, or lineage-inconsistent", None, None)
        binding, binding_hash, derived_key = prepared
        if remote_idempotency_key is not None and remote_idempotency_key != derived_key:
            return _result("DENY_REMOTE_IDEMPOTENCY_REBIND", "caller-supplied remote idempotency key does not equal platform-derived key", binding, derived_key)
        key = derived_key
        row = self._local_row(key)
        if row is not None:
            if row["binding_hash"] != binding_hash:
                return _result("DENY_REMOTE_IDEMPOTENCY_REBIND", "remote idempotency identity is already bound to different inputs", binding, key)
            if row["status"] == "COMPLETED" and row["evidence_json"]:
                return _result("REMOTE_EXECUTION_REPLAYED", "exact remote execution already completed", binding, key, json.loads(row["evidence_json"]))
            if row["status"] == "AMBIGUOUS":
                return self.reconcile(slice7_result)

        self._set_local(key, binding_hash, "PENDING")
        if failure_point == "before_remote_accept":
            raise SimulatedRemoteTransportFailure("simulated failure before remote durable acceptance")

        code, wire = self._post(
            "/execute",
            {
                "binding": binding,
                "binding_hash": binding_hash,
                "remote_idempotency_key": key,
            },
        )
        if code == 409 or wire.get("status") == "IDEMPOTENCY_REBIND_DENIED":
            self._set_local(key, binding_hash, "FAILED")
            return _result("DENY_REMOTE_IDEMPOTENCY_REBIND", "remote service rejected idempotency rebinding", binding, key)
        if failure_point in {"after_remote_commit_before_ack", "timeout_after_remote_commit"}:
            self._set_local(key, binding_hash, "AMBIGUOUS")
            return _result("REMOTE_OUTCOME_AMBIGUOUS", "remote may have committed but acknowledgement was not accepted by caller", binding, key)
        if code != 200:
            self._set_local(key, binding_hash, "FAILED")
            return _result("REMOTE_DELIVERY_FAILED", f"remote HTTP delivery failed with status {code}", binding, key)
        if wire.get("status") == "FAILED":
            self._set_local(key, binding_hash, "FAILED")
            return _result("REMOTE_EXECUTION_FAILED", "remote service returned structured failure", binding, key)
        valid, receipt, remote_result = self._validate_remote_success(wire, binding, binding_hash, key)
        if not valid or receipt is None or remote_result is None:
            self._set_local(key, binding_hash, "FAILED")
            return _result("REMOTE_EXECUTION_FAILED", "remote response/receipt is malformed, widened, or inconsistent", binding, key)
        evidence = _completion_evidence(binding, key, receipt, remote_result)
        self._set_local(key, binding_hash, "COMPLETED", evidence)
        return _result("REMOTE_EXECUTION_COMPLETED", "remote reference effect completed exactly once", binding, key, evidence)

    def reconcile(self, slice7_result: Mapping[str, Any]) -> dict[str, Any]:
        prepared = self._prepare(slice7_result)
        if prepared is None:
            return _result("DENY_SLICE7_BINDING", "Slice 7 completion is malformed, non-success, tampered, or lineage-inconsistent", None, None)
        binding, binding_hash, key = prepared
        row = self._local_row(key)
        if row is not None and row["binding_hash"] != binding_hash:
            return _result("DENY_REMOTE_IDEMPOTENCY_REBIND", "local remote idempotency identity is bound to different inputs", binding, key)
        code, wire = self._post(
            "/reconcile",
            {"remote_idempotency_key": key, "binding_hash": binding_hash},
        )
        if code == 404:
            return _result("REMOTE_DELIVERY_FAILED", "remote service has no durable record for ambiguous execution", binding, key)
        if code == 409:
            return _result("DENY_REMOTE_IDEMPOTENCY_REBIND", "remote reconciliation detected idempotency rebinding", binding, key)
        if code != 200:
            return _result("REMOTE_DELIVERY_FAILED", f"remote reconciliation failed with status {code}", binding, key)
        if wire.get("status") == "FAILED":
            self._set_local(key, binding_hash, "FAILED")
            return _result("REMOTE_EXECUTION_FAILED", "remote durable record is failed", binding, key)
        valid, receipt, remote_result = self._validate_remote_success(wire, binding, binding_hash, key)
        if not valid or receipt is None or remote_result is None:
            self._set_local(key, binding_hash, "FAILED")
            return _result("REMOTE_EXECUTION_FAILED", "reconciled remote response/receipt is malformed, widened, or inconsistent", binding, key)
        evidence = _completion_evidence(binding, key, receipt, remote_result)
        self._set_local(key, binding_hash, "COMPLETED", evidence)
        return _result("REMOTE_EXECUTION_RECONCILED", "ambiguous remote outcome reconciled from durable idempotency record", binding, key, evidence)
