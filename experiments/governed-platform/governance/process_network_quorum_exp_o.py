"""EXP-O Pilot 14 independent-process authenticated quorum prototype.

This module is a falsification harness, not a production consensus protocol.
Three independent node processes keep separate SQLite authority state and obtain
fresh authenticated peer acknowledgements over loopback HTTP before any
consequential use can reach the shared idempotent effect boundary.
"""
from __future__ import annotations

import argparse
import copy
from contextlib import closing
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import time
from typing import Any, Mapping, Sequence
from urllib import error as urlerror
from urllib import request as urlrequest
import uuid

MEMBERS = ("r1", "r2", "r3")
QUORUM = 2
LEASE_DURATION_MS = 1000
CLUSTER_ID = "exp-o-p14-cluster"
MAX_BODY_BYTES = 2_000_000
PEER_TIMEOUT_S = 1.00

BINDING_FIELDS = (
    "semantic_payload_digest",
    "effect_digest",
    "idempotency_key",
    "worker_id",
    "worker_key_thumbprint",
    "effect_contract_id",
    "base_sha",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def deny(reason: str, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


def _binding_view(value: Mapping[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(value.get(field)) for field in BINDING_FIELDS}


def _binding_error(record: Mapping[str, Any], bindings: Mapping[str, Any]) -> str | None:
    for field in BINDING_FIELDS:
        if record.get(field) != bindings.get(field):
            return f"PROCESS_QUORUM_BINDING_MISMATCH:{field}"
    return None


def sign_envelope(core: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    body = copy.deepcopy(dict(core))
    return {
        "core": body,
        "auth_tag": hmac.new(key, canonical(body), hashlib.sha256).hexdigest(),
    }


def verify_envelope(
    envelope: Mapping[str, Any] | None,
    key: bytes,
    *,
    expected_cluster: str,
    expected_receiver: str | None = None,
    expected_sender: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(envelope, Mapping) or not isinstance(envelope.get("core"), Mapping):
        return None, "MESSAGE_ENVELOPE_MALFORMED"
    core = dict(envelope["core"])
    tag = str(envelope.get("auth_tag", ""))
    expected_tag = hmac.new(key, canonical(core), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(tag, expected_tag):
        return None, "MESSAGE_AUTH_INVALID"
    if core.get("cluster_id") != expected_cluster:
        return None, "MESSAGE_CLUSTER_MISMATCH"
    if core.get("sender_id") not in MEMBERS or core.get("receiver_id") not in MEMBERS:
        return None, "MESSAGE_MEMBER_INVALID"
    if expected_receiver is not None and core.get("receiver_id") != expected_receiver:
        return None, "MESSAGE_RECEIVER_MISMATCH"
    if expected_sender is not None and core.get("sender_id") != expected_sender:
        return None, "MESSAGE_SENDER_MISMATCH"
    payload = core.get("payload")
    if not isinstance(payload, Mapping):
        return None, "MESSAGE_PAYLOAD_MALFORMED"
    if core.get("payload_digest") != digest(dict(payload)):
        return None, "MESSAGE_PAYLOAD_DIGEST_MISMATCH"
    if not str(core.get("message_id", "")):
        return None, "MESSAGE_ID_REQUIRED"
    try:
        int(core.get("term"))
    except Exception:
        return None, "MESSAGE_TERM_INVALID"
    return core, None


class ReplicaStore:
    """Per-process durable authority and inbound-message ledger."""

    def __init__(self, path: str | Path, replica_id: str) -> None:
        if replica_id not in MEMBERS:
            raise ValueError("unknown frozen replica")
        self.path = str(path)
        self.replica_id = replica_id
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS replica_meta(id INTEGER PRIMARY KEY CHECK(id=1), current_term INTEGER NOT NULL, leader_id TEXT, commit_index INTEGER NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS authority_records(bound_permit_id TEXT PRIMARY KEY, record_json TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS inbound_messages(sender_id TEXT NOT NULL, message_id TEXT NOT NULL, payload_digest TEXT NOT NULL, response_json TEXT NOT NULL, PRIMARY KEY(sender_id,message_id))"
            )
            row = conn.execute("SELECT 1 FROM replica_meta WHERE id=1").fetchone()
            if row is None:
                conn.execute("INSERT INTO replica_meta(id,current_term,leader_id,commit_index) VALUES(1,0,NULL,0)")
            conn.commit()

    def snapshot(self) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            meta = conn.execute("SELECT current_term,leader_id,commit_index FROM replica_meta WHERE id=1").fetchone()
            records = {
                str(row["bound_permit_id"]): json.loads(str(row["record_json"]))
                for row in conn.execute("SELECT bound_permit_id,record_json FROM authority_records ORDER BY bound_permit_id")
            }
        assert meta is not None
        return {
            "current_term": int(meta["current_term"]),
            "leader_id": meta["leader_id"],
            "commit_index": int(meta["commit_index"]),
            "records": records,
        }

    def install_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        records = snapshot.get("records")
        if not isinstance(records, Mapping):
            raise ValueError("snapshot records missing")
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE replica_meta SET current_term=?, leader_id=?, commit_index=? WHERE id=1",
                (int(snapshot["current_term"]), snapshot.get("leader_id"), int(snapshot["commit_index"])),
            )
            conn.execute("DELETE FROM authority_records")
            for permit_id, record in sorted(records.items()):
                conn.execute(
                    "INSERT INTO authority_records(bound_permit_id,record_json) VALUES(?,?)",
                    (str(permit_id), canonical(record).decode("utf-8")),
                )
            conn.commit()

    def get_record(self, permit_id: str) -> dict[str, Any] | None:
        return copy.deepcopy(self.snapshot()["records"].get(permit_id))

    def ledger_lookup(self, sender_id: str, message_id: str) -> tuple[str, dict[str, Any]] | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT payload_digest,response_json FROM inbound_messages WHERE sender_id=? AND message_id=?",
                (sender_id, message_id),
            ).fetchone()
        if row is None:
            return None
        return str(row["payload_digest"]), json.loads(str(row["response_json"]))

    def ledger_store(self, sender_id: str, message_id: str, payload_digest: str, response: Mapping[str, Any]) -> None:
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT INTO inbound_messages(sender_id,message_id,payload_digest,response_json) VALUES(?,?,?,?)",
                (sender_id, message_id, payload_digest, canonical(response).decode("utf-8")),
            )
            conn.commit()

    def ledger_count(self) -> int:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT COUNT(*) FROM inbound_messages").fetchone()
        return int(row[0])


class EffectStore:
    """Shared pilot-only exactly-once effect boundary."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS process_quorum_effects(idempotency_key TEXT PRIMARY KEY,effect_digest TEXT NOT NULL,result_digest TEXT NOT NULL)"
            )
            conn.commit()

    def apply(self, idempotency_key: str, effect_digest: str) -> dict[str, Any]:
        with closing(sqlite3.connect(self.path, timeout=5.0, isolation_level=None)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT effect_digest,result_digest FROM process_quorum_effects WHERE idempotency_key=?",
                (idempotency_key,),
            ).fetchone()
            if row is not None:
                if str(row["effect_digest"]) != effect_digest:
                    conn.rollback()
                    return deny("IDEMPOTENCY_EFFECT_REBINDING_DENIED")
                conn.commit()
                return {"authorized": True, "executed": False, "replayed": True, "result_digest": str(row["result_digest"])}
            result_digest = digest({"idempotency_key": idempotency_key, "effect_digest": effect_digest})
            conn.execute(
                "INSERT INTO process_quorum_effects(idempotency_key,effect_digest,result_digest) VALUES(?,?,?)",
                (idempotency_key, effect_digest, result_digest),
            )
            conn.commit()
            return {"authorized": True, "executed": True, "replayed": False, "result_digest": result_digest}

    def count(self) -> int:
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute("SELECT COUNT(*) FROM process_quorum_effects").fetchone()
        return int(row[0])


class ProcessQuorumNode:
    def __init__(
        self,
        *,
        replica_id: str,
        db_path: str | Path,
        cluster_key: bytes,
        cluster_dir: str | Path,
        fault_file: str | Path,
        clock_file: str | Path,
        effect_db: str | Path,
    ) -> None:
        self.replica_id = replica_id
        self.store = ReplicaStore(db_path, replica_id)
        self.key = bytes(cluster_key)
        self.cluster_dir = Path(cluster_dir)
        self.fault_file = Path(fault_file)
        self.clock_file = Path(clock_file)
        self.effects = EffectStore(effect_db)
        self.delayed: list[tuple[str, dict[str, Any]]] = []
        self.outbound_history: dict[str, tuple[str, dict[str, Any]]] = {}
        self.response_history: list[dict[str, Any]] = []
        self._history_lock = threading.Lock()

    def trusted_now_ms(self) -> int:
        return int(self.clock_file.read_text(encoding="utf-8").strip())

    def _peer_url(self, peer_id: str) -> str:
        info = json.loads((self.cluster_dir / f"{peer_id}.ready.json").read_text(encoding="utf-8"))
        return f"http://127.0.0.1:{int(info['port'])}"

    def _fault(self, peer_id: str, message_type: str) -> str | None:
        try:
            data = json.loads(self.fault_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        value = (data.get("rules") or {}).get(f"{self.replica_id}->{peer_id}:{message_type}")
        return str(value) if value else None

    def _make_peer_envelope(
        self,
        peer_id: str,
        message_type: str,
        term: int,
        payload: Mapping[str, Any],
        *,
        message_id: str | None = None,
    ) -> dict[str, Any]:
        core = {
            "cluster_id": CLUSTER_ID,
            "sender_id": self.replica_id,
            "receiver_id": peer_id,
            "message_type": message_type,
            "term": int(term),
            "message_id": message_id or uuid.uuid4().hex,
            "payload": copy.deepcopy(dict(payload)),
            "payload_digest": digest(dict(payload)),
        }
        return sign_envelope(core, self.key)

    def _make_response(self, request_core: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
        snap = self.store.snapshot()
        core = {
            "cluster_id": CLUSTER_ID,
            "sender_id": self.replica_id,
            "receiver_id": request_core.get("sender_id"),
            "message_type": f"ACK:{request_core.get('message_type')}",
            "term": int(snap["current_term"]),
            "message_id": f"ack:{request_core.get('message_id')}",
            "payload": copy.deepcopy(dict(payload)),
            "payload_digest": digest(dict(payload)),
        }
        return sign_envelope(core, self.key)

    def _post_peer_envelope(self, peer_id: str, envelope: Mapping[str, Any]) -> dict[str, Any] | None:
        req = urlrequest.Request(
            self._peer_url(peer_id) + "/peer",
            data=canonical(envelope),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=PEER_TIMEOUT_S) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urlerror.URLError, TimeoutError, OSError, json.JSONDecodeError):
            return None
        response_env = body.get("response_envelope") if isinstance(body, Mapping) else None
        core, error = verify_envelope(
            response_env,
            self.key,
            expected_cluster=CLUSTER_ID,
            expected_receiver=self.replica_id,
            expected_sender=peer_id,
        )
        if error or core is None:
            return None
        with self._history_lock:
            self.response_history.append(copy.deepcopy(dict(response_env)))
        return copy.deepcopy(dict(response_env))

    def _send_peer(
        self,
        peer_id: str,
        message_type: str,
        term: int,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        env = self._make_peer_envelope(peer_id, message_type, term, payload)
        message_id = str(env["core"]["message_id"])
        with self._history_lock:
            self.outbound_history[message_id] = (peer_id, copy.deepcopy(env))
        fault = self._fault(peer_id, message_type)
        if fault == "DROP":
            return []
        if fault in {"DELAY_UNTIL_RELEASE", "REORDER"}:
            with self._history_lock:
                self.delayed.append((peer_id, copy.deepcopy(env)))
            return []
        send_env = copy.deepcopy(env)
        if fault == "CORRUPT_AUTH":
            send_env["auth_tag"] = "0" * 64
        deliveries = 2 if fault == "DUPLICATE" else 1
        outputs: list[dict[str, Any]] = []
        for _ in range(deliveries):
            response = self._post_peer_envelope(peer_id, send_env)
            if response is not None:
                outputs.append(response)
        return outputs

    def _response_payload(
        self,
        envelope: Mapping[str, Any],
        *,
        expected_sender: str,
        expected_type: str,
        expected_term: int,
    ) -> dict[str, Any] | None:
        core, error = verify_envelope(
            envelope,
            self.key,
            expected_cluster=CLUSTER_ID,
            expected_receiver=self.replica_id,
            expected_sender=expected_sender,
        )
        if error or core is None:
            return None
        if core.get("message_type") != f"ACK:{expected_type}":
            return None
        if int(core.get("term", -1)) != int(expected_term):
            return None
        payload = core.get("payload")
        return copy.deepcopy(dict(payload)) if isinstance(payload, Mapping) else None

    def _distinct_positive_voters(
        self,
        responses: Sequence[Mapping[str, Any]],
        *,
        expected_type: str,
        expected_term: int,
        positive_field: str,
        include_self: bool = True,
    ) -> list[str]:
        voters: set[str] = {self.replica_id} if include_self else set()
        for response in responses:
            core = response.get("core") if isinstance(response, Mapping) else None
            sender = str(core.get("sender_id", "")) if isinstance(core, Mapping) else ""
            if sender not in MEMBERS or sender == self.replica_id:
                continue
            payload = self._response_payload(
                response,
                expected_sender=sender,
                expected_type=expected_type,
                expected_term=expected_term,
            )
            if payload is not None and payload.get(positive_field) is True:
                voters.add(sender)
        return sorted(voters)

    def _current_snapshot_with(self, *, term: int | None = None, leader_id: str | None = None, commit_index: int | None = None, records: Mapping[str, Any] | None = None) -> dict[str, Any]:
        snap = self.store.snapshot()
        if term is not None:
            snap["current_term"] = int(term)
        if leader_id is not None:
            snap["leader_id"] = leader_id
        if commit_index is not None:
            snap["commit_index"] = int(commit_index)
        if records is not None:
            snap["records"] = copy.deepcopy(dict(records))
        return snap

    def elect(self, term: int, *, candidate_self_vote_copies: int = 1) -> dict[str, Any]:
        local = self.store.snapshot()
        if int(term) <= int(local["current_term"]):
            return deny("ELECTION_TERM_NOT_MONOTONIC", current_term=local["current_term"])
        candidate_snapshot = copy.deepcopy(local)
        payload = {"candidate_snapshot": candidate_snapshot, "candidate_self_vote_copies": int(candidate_self_vote_copies)}
        responses: list[dict[str, Any]] = []
        for peer in MEMBERS:
            if peer != self.replica_id:
                responses.extend(self._send_peer(peer, "VOTE", int(term), payload))
        voters = self._distinct_positive_voters(
            responses,
            expected_type="VOTE",
            expected_term=int(term),
            positive_field="granted",
            include_self=True,
        )
        if len(voters) < QUORUM:
            return deny("ELECTION_QUORUM_REQUIRED", voters=voters)
        elected_snapshot = copy.deepcopy(candidate_snapshot)
        elected_snapshot["current_term"] = int(term)
        elected_snapshot["leader_id"] = self.replica_id
        self.store.install_snapshot(elected_snapshot)
        return {"authorized": True, "decision": "ELECTED", "leader_id": self.replica_id, "term": int(term), "voters": voters, "pid": os.getpid()}

    def _leader_state(self) -> tuple[dict[str, Any] | None, str | None]:
        snap = self.store.snapshot()
        if snap.get("leader_id") != self.replica_id:
            return None, "NOT_CURRENT_LEADER"
        if int(snap.get("current_term", 0)) <= 0:
            return None, "LEADER_TERM_REQUIRED"
        return snap, None

    def _quorum_commit(self, records: Mapping[str, Any]) -> dict[str, Any]:
        local, error = self._leader_state()
        if error:
            return deny(error)
        assert local is not None
        term = int(local["current_term"])
        next_index = int(local["commit_index"]) + 1
        proposed = {
            "current_term": term,
            "leader_id": self.replica_id,
            "commit_index": next_index,
            "records": copy.deepcopy(dict(records)),
        }
        payload = {"snapshot": proposed}
        responses: list[dict[str, Any]] = []
        for peer in MEMBERS:
            if peer != self.replica_id:
                responses.extend(self._send_peer(peer, "REPLICATE", term, payload))
        voters = self._distinct_positive_voters(
            responses,
            expected_type="REPLICATE",
            expected_term=term,
            positive_field="accepted",
            include_self=True,
        )
        if len(voters) < QUORUM:
            return deny("REPLICATION_QUORUM_REQUIRED", voters=voters, proposed_commit_index=next_index)
        self.store.install_snapshot(proposed)
        return {"authorized": True, "decision": "QUORUM_COMMITTED", "term": term, "commit_index": next_index, "voters": voters}

    def _certificate(self, permit_id: str, voters: Sequence[str]) -> dict[str, Any]:
        snap = self.store.snapshot()
        record = snap["records"].get(permit_id)
        return {
            "cluster_id": CLUSTER_ID,
            "term": int(snap["current_term"]),
            "leader_id": self.replica_id,
            "commit_index": int(snap["commit_index"]),
            "bound_permit_id": permit_id,
            "record_digest": digest(record),
            "lease_owner_gateway_instance_id": record.get("lease_owner_gateway_instance_id") if isinstance(record, Mapping) else None,
            "lease_epoch": int(record.get("lease_epoch", 0)) if isinstance(record, Mapping) else 0,
            "lease_expires_at_ms": record.get("lease_expires_at_ms") if isinstance(record, Mapping) else None,
            "state": record.get("state") if isinstance(record, Mapping) else None,
            "binding_digest": digest(_binding_view(record)) if isinstance(record, Mapping) else None,
            "voters": sorted(set(voters)),
        }

    def issue(self, permit_id: str, bindings: Mapping[str, Any]) -> dict[str, Any]:
        for field in BINDING_FIELDS:
            if bindings.get(field) in (None, "", []):
                return deny(f"AUTHORITY_BINDING_REQUIRED:{field}")
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        if permit_id in snap["records"]:
            return deny("AUTHORITY_RECORD_ALREADY_EXISTS")
        record = {
            "bound_permit_id": permit_id,
            **_binding_view(bindings),
            "state": "ISSUED",
            "lease_owner_gateway_instance_id": None,
            "lease_epoch": 0,
            "lease_expires_at_ms": None,
            "authoritative_result_digest": None,
        }
        records = copy.deepcopy(snap["records"])
        records[permit_id] = record
        committed = self._quorum_commit(records)
        if committed.get("authorized"):
            committed["certificate"] = self._certificate(permit_id, committed["voters"])
        return committed

    def acquire(self, permit_id: str, owner_id: str, bindings: Mapping[str, Any]) -> dict[str, Any]:
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        record = copy.deepcopy(snap["records"].get(permit_id))
        if not isinstance(record, Mapping):
            return deny("AUTHORITY_RECORD_MISSING")
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return deny(mismatch)
        if record.get("state") != "ISSUED":
            return deny("AUTHORITY_FIRST_ACQUIRE_REQUIRES_ISSUED")
        now_ms = self.trusted_now_ms()
        record = dict(record)
        record.update(state="IN_FLIGHT", lease_owner_gateway_instance_id=owner_id, lease_epoch=1, lease_expires_at_ms=now_ms + LEASE_DURATION_MS)
        records = copy.deepcopy(snap["records"])
        records[permit_id] = record
        committed = self._quorum_commit(records)
        if committed.get("authorized"):
            committed.update(disposition="FIRST_OWNER", trusted_now_ms=now_ms, lease_epoch=1, lease_expires_at_ms=record["lease_expires_at_ms"], certificate=self._certificate(permit_id, committed["voters"]))
        return committed

    def renew(self, permit_id: str, owner_id: str, lease_epoch: int, bindings: Mapping[str, Any]) -> dict[str, Any]:
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        record = copy.deepcopy(snap["records"].get(permit_id))
        if not isinstance(record, Mapping):
            return deny("AUTHORITY_RECORD_MISSING")
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return deny("AUTHORITY_RENEW_REQUIRES_IN_FLIGHT")
        if record.get("lease_owner_gateway_instance_id") != owner_id or int(record.get("lease_epoch", 0)) != int(lease_epoch):
            return deny("AUTHORITY_RENEW_STALE_OWNER_OR_EPOCH")
        now_ms = self.trusted_now_ms()
        old_expiry = record.get("lease_expires_at_ms")
        if old_expiry is None or now_ms >= int(old_expiry):
            return deny("AUTHORITY_RENEW_LEASE_EXPIRED")
        new_expiry = now_ms + LEASE_DURATION_MS
        if new_expiry <= int(old_expiry):
            return deny("AUTHORITY_RENEWAL_MUST_EXTEND_EXPIRY")
        record["lease_expires_at_ms"] = new_expiry
        records = copy.deepcopy(snap["records"])
        records[permit_id] = record
        committed = self._quorum_commit(records)
        if committed.get("authorized"):
            committed.update(disposition="LEASE_RENEWED", lease_epoch=int(lease_epoch), lease_expires_at_ms=new_expiry, trusted_now_ms=now_ms)
        return committed

    def takeover(self, permit_id: str, new_owner_id: str, bindings: Mapping[str, Any]) -> dict[str, Any]:
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        record = copy.deepcopy(snap["records"].get(permit_id))
        if not isinstance(record, Mapping):
            return deny("AUTHORITY_RECORD_MISSING")
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return deny("AUTHORITY_TAKEOVER_REQUIRES_IN_FLIGHT")
        now_ms = self.trusted_now_ms()
        expiry = record.get("lease_expires_at_ms")
        if expiry is None:
            return deny("AUTHORITY_LEASE_EXPIRY_MISSING")
        if now_ms < int(expiry):
            return deny("AUTHORITY_LIVE_OWNER_UNEXPIRED", trusted_now_ms=now_ms, lease_expires_at_ms=int(expiry))
        old_owner = record.get("lease_owner_gateway_instance_id")
        record["lease_owner_gateway_instance_id"] = new_owner_id
        record["lease_epoch"] = int(record.get("lease_epoch", 0)) + 1
        record["lease_expires_at_ms"] = now_ms + LEASE_DURATION_MS
        records = copy.deepcopy(snap["records"])
        records[permit_id] = record
        committed = self._quorum_commit(records)
        if committed.get("authorized"):
            committed.update(disposition="QUORUM_EXPIRY_TAKEOVER", previous_owner_gateway_instance_id=old_owner, lease_owner_gateway_instance_id=new_owner_id, lease_epoch=record["lease_epoch"], lease_expires_at_ms=record["lease_expires_at_ms"], trusted_now_ms=now_ms, certificate=self._certificate(permit_id, committed["voters"]))
        return committed

    def _fresh_quorum_confirm(self, permit_id: str) -> dict[str, Any]:
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        record = snap["records"].get(permit_id)
        if not isinstance(record, Mapping):
            return deny("AUTHORITY_RECORD_MISSING")
        term = int(snap["current_term"])
        payload = {
            "expected_term": term,
            "expected_leader_id": self.replica_id,
            "expected_commit_index": int(snap["commit_index"]),
            "permit_id": permit_id,
            "expected_record_digest": digest(record),
        }
        responses: list[dict[str, Any]] = []
        for peer in MEMBERS:
            if peer != self.replica_id:
                responses.extend(self._send_peer(peer, "READ_CONFIRM", term, payload))
        voters = self._distinct_positive_voters(
            responses,
            expected_type="READ_CONFIRM",
            expected_term=term,
            positive_field="confirmed",
            include_self=True,
        )
        if len(voters) < QUORUM:
            return deny("USE_TIME_QUORUM_REQUIRED", voters=voters)
        return {"authorized": True, "decision": "USE_TIME_QUORUM_CONFIRMED", "term": term, "commit_index": int(snap["commit_index"]), "voters": voters, "certificate": self._certificate(permit_id, voters)}

    def finalize(self, permit_id: str, owner_id: str, lease_epoch: int, bindings: Mapping[str, Any], result_digest: str) -> dict[str, Any]:
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        record = copy.deepcopy(snap["records"].get(permit_id))
        if not isinstance(record, Mapping):
            return deny("AUTHORITY_RECORD_MISSING")
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return deny("AUTHORITY_FINALIZE_REQUIRES_IN_FLIGHT")
        if record.get("lease_owner_gateway_instance_id") != owner_id or int(record.get("lease_epoch", 0)) != int(lease_epoch):
            return deny("AUTHORITY_FINALIZE_STALE_OWNER_OR_EPOCH")
        now_ms = self.trusted_now_ms()
        if record.get("lease_expires_at_ms") is None or now_ms >= int(record["lease_expires_at_ms"]):
            return deny("AUTHORITY_FINALIZE_LEASE_EXPIRED")
        record["state"] = "CONSUMED"
        record["authoritative_result_digest"] = result_digest
        records = copy.deepcopy(snap["records"])
        records[permit_id] = record
        committed = self._quorum_commit(records)
        if committed.get("authorized"):
            committed.update(disposition="AUTHORITY_CONSUMED", authoritative_result_digest=result_digest)
        return committed

    def execute(self, permit_id: str, owner_id: str, lease_epoch: int, bindings: Mapping[str, Any], *, crash_after_effect: bool = False) -> dict[str, Any]:
        snap, error = self._leader_state()
        if error:
            return deny(error)
        assert snap is not None
        record = snap["records"].get(permit_id)
        if not isinstance(record, Mapping):
            return deny("AUTHORITY_RECORD_MISSING")
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return deny("AUTHORITY_REVALIDATION_REQUIRES_IN_FLIGHT")
        if record.get("lease_owner_gateway_instance_id") != owner_id or int(record.get("lease_epoch", 0)) != int(lease_epoch):
            return deny("AUTHORITY_STALE_OWNER_OR_EPOCH")
        now_ms = self.trusted_now_ms()
        if record.get("lease_expires_at_ms") is None or now_ms >= int(record["lease_expires_at_ms"]):
            return deny("AUTHORITY_LEASE_EXPIRED")
        confirmed = self._fresh_quorum_confirm(permit_id)
        if not confirmed.get("authorized"):
            return confirmed
        effect = self.effects.apply(str(bindings["idempotency_key"]), str(bindings["effect_digest"]))
        if not effect.get("authorized"):
            return effect
        if crash_after_effect:
            os._exit(91)
        finalized = self.finalize(permit_id, owner_id, lease_epoch, bindings, str(effect["result_digest"]))
        return {**finalized, "effect_result": effect, "use_time_certificate": confirmed.get("certificate")}

    def authoritative_read(self, permit_id: str) -> dict[str, Any]:
        confirmed = self._fresh_quorum_confirm(permit_id)
        if not confirmed.get("authorized"):
            return {"authoritative": False, "reason": confirmed.get("reason"), "voters": confirmed.get("voters", [])}
        return {"authoritative": True, "record": self.store.get_record(permit_id), "certificate": confirmed["certificate"]}

    def catch_up(self) -> dict[str, Any]:
        local = self.store.snapshot()
        request_term = int(local["current_term"])
        responses: list[dict[str, Any]] = []
        for peer in MEMBERS:
            if peer != self.replica_id:
                responses.extend(self._send_peer(peer, "STATE_SNAPSHOT", request_term, {"request": "CURRENT_STATE"}))
        groups: dict[tuple[int, int, str, str | None], list[tuple[str, dict[str, Any]]]] = {}
        for response in responses:
            core = response.get("core") if isinstance(response, Mapping) else None
            if not isinstance(core, Mapping):
                continue
            sender = str(core.get("sender_id", ""))
            verified, error = verify_envelope(response, self.key, expected_cluster=CLUSTER_ID, expected_receiver=self.replica_id, expected_sender=sender)
            if error or verified is None:
                continue
            payload = verified.get("payload")
            snapshot = payload.get("snapshot") if isinstance(payload, Mapping) else None
            if not isinstance(snapshot, Mapping):
                continue
            key = (int(snapshot.get("current_term", -1)), int(snapshot.get("commit_index", -1)), digest(snapshot.get("records", {})), snapshot.get("leader_id"))
            groups.setdefault(key, []).append((sender, copy.deepcopy(dict(snapshot))))
        eligible = [(key, values) for key, values in groups.items() if len({sender for sender, _ in values}) >= QUORUM]
        if not eligible:
            return deny("CATCH_UP_CURRENT_MAJORITY_REQUIRED")
        key, values = max(eligible, key=lambda item: (item[0][0], item[0][1]))
        target = values[0][1]
        if (int(target["current_term"]), int(target["commit_index"])) < (int(local["current_term"]), int(local["commit_index"])):
            return deny("CATCH_UP_WOULD_ROLL_BACK")
        self.store.install_snapshot(target)
        return {"authorized": True, "decision": "CAUGHT_UP", "term": int(target["current_term"]), "commit_index": int(target["commit_index"]), "sources": sorted({sender for sender, _ in values})}

    def handle_peer(self, envelope: Mapping[str, Any] | None) -> dict[str, Any]:
        core, error = verify_envelope(envelope, self.key, expected_cluster=CLUSTER_ID, expected_receiver=self.replica_id)
        if error or core is None:
            fake = {
                "cluster_id": CLUSTER_ID,
                "sender_id": str((envelope or {}).get("core", {}).get("sender_id", "r1")) if isinstance(envelope, Mapping) else "r1",
                "receiver_id": self.replica_id,
                "message_type": str((envelope or {}).get("core", {}).get("message_type", "INVALID")) if isinstance(envelope, Mapping) else "INVALID",
                "term": self.store.snapshot()["current_term"],
                "message_id": str((envelope or {}).get("core", {}).get("message_id", "invalid")) if isinstance(envelope, Mapping) else "invalid",
                "payload": {},
                "payload_digest": digest({}),
            }
            return {"response_envelope": self._make_response(fake, {"granted": False, "accepted": False, "confirmed": False, "reason": error or "MESSAGE_INVALID"})}

        sender = str(core["sender_id"])
        message_id = str(core["message_id"])
        payload_digest = str(core["payload_digest"])
        prior = self.store.ledger_lookup(sender, message_id)
        if prior is not None:
            prior_digest, response = prior
            if prior_digest != payload_digest:
                return {"response_envelope": self._make_response(core, {"granted": False, "accepted": False, "confirmed": False, "reason": "MESSAGE_ID_CONFLICTING_REPLAY"})}
            return {"response_envelope": copy.deepcopy(response), "replay": True}

        message_type = str(core["message_type"])
        term = int(core["term"])
        payload = dict(core["payload"])
        response_payload: dict[str, Any]
        local = self.store.snapshot()

        if message_type == "VOTE":
            candidate = payload.get("candidate_snapshot")
            if not isinstance(candidate, Mapping):
                response_payload = {"granted": False, "reason": "VOTE_SNAPSHOT_REQUIRED"}
            elif term <= int(local["current_term"]):
                response_payload = {"granted": False, "reason": "VOTE_STALE_TERM"}
            elif int(candidate.get("commit_index", -1)) < int(local["commit_index"]):
                response_payload = {"granted": False, "reason": "VOTE_CANDIDATE_LOG_STALE"}
            else:
                installed = copy.deepcopy(dict(candidate))
                installed["current_term"] = term
                installed["leader_id"] = sender
                self.store.install_snapshot(installed)
                response_payload = {"granted": True, "term": term, "commit_index": int(installed["commit_index"])}

        elif message_type == "REPLICATE":
            proposed = payload.get("snapshot")
            if not isinstance(proposed, Mapping):
                response_payload = {"accepted": False, "reason": "REPLICATION_SNAPSHOT_REQUIRED"}
            elif term < int(local["current_term"]):
                response_payload = {"accepted": False, "reason": "REPLICATION_STALE_TERM"}
            elif proposed.get("leader_id") != sender or int(proposed.get("current_term", -1)) != term:
                response_payload = {"accepted": False, "reason": "REPLICATION_LEADER_OR_TERM_MISMATCH"}
            elif term == int(local["current_term"]) and local.get("leader_id") not in (None, sender):
                response_payload = {"accepted": False, "reason": "REPLICATION_COMPETING_LEADER"}
            elif int(proposed.get("commit_index", -1)) < int(local["commit_index"]):
                response_payload = {"accepted": False, "reason": "REPLICATION_STALE_INDEX"}
            elif int(proposed.get("commit_index", -1)) == int(local["commit_index"]) and digest(proposed.get("records", {})) != digest(local.get("records", {})):
                response_payload = {"accepted": False, "reason": "REPLICATION_SAME_INDEX_DIVERGENCE"}
            else:
                self.store.install_snapshot(proposed)
                response_payload = {"accepted": True, "term": term, "commit_index": int(proposed["commit_index"]), "records_digest": digest(proposed.get("records", {}))}

        elif message_type == "READ_CONFIRM":
            if term != int(local["current_term"]):
                response_payload = {"confirmed": False, "reason": "READ_CONFIRM_STALE_TERM"}
            elif payload.get("expected_leader_id") != local.get("leader_id"):
                response_payload = {"confirmed": False, "reason": "READ_CONFIRM_LEADER_MISMATCH"}
            elif int(payload.get("expected_commit_index", -1)) != int(local["commit_index"]):
                response_payload = {"confirmed": False, "reason": "READ_CONFIRM_INDEX_MISMATCH"}
            else:
                record = local["records"].get(str(payload.get("permit_id", "")))
                if record is None or digest(record) != payload.get("expected_record_digest"):
                    response_payload = {"confirmed": False, "reason": "READ_CONFIRM_RECORD_MISMATCH"}
                else:
                    response_payload = {"confirmed": True, "term": term, "commit_index": int(local["commit_index"]), "record_digest": digest(record)}

        elif message_type == "STATE_SNAPSHOT":
            response_payload = {"snapshot": local}
        else:
            response_payload = {"granted": False, "accepted": False, "confirmed": False, "reason": "MESSAGE_TYPE_UNSUPPORTED"}

        response = self._make_response(core, response_payload)
        try:
            self.store.ledger_store(sender, message_id, payload_digest, response)
        except sqlite3.IntegrityError:
            prior = self.store.ledger_lookup(sender, message_id)
            if prior is not None and prior[0] == payload_digest:
                response = prior[1]
            else:
                response = self._make_response(core, {"granted": False, "accepted": False, "confirmed": False, "reason": "MESSAGE_ID_CONFLICTING_REPLAY"})
        return {"response_envelope": response}

    def release_delayed(self) -> dict[str, Any]:
        with self._history_lock:
            queued = list(self.delayed)
            self.delayed.clear()
        outcomes = []
        for peer_id, env in queued:
            response = self._post_peer_envelope(peer_id, env)
            outcomes.append({"peer_id": peer_id, "message_id": env["core"]["message_id"], "response_envelope": response})
        return {"released": len(queued), "outcomes": outcomes}

    def probe_peer(self, peer_id: str, message_type: str, payload: Mapping[str, Any], *, term: int | None = None) -> dict[str, Any]:
        actual_term = int(self.store.snapshot()["current_term"] if term is None else term)
        responses = self._send_peer(peer_id, message_type, actual_term, payload)
        return {"responses": responses}

    def replay_outbound_conflict(self, message_id: str, changed_payload: Mapping[str, Any]) -> dict[str, Any]:
        with self._history_lock:
            item = self.outbound_history.get(message_id)
        if item is None:
            return deny("OUTBOUND_MESSAGE_NOT_FOUND")
        peer_id, old = item
        old_core = dict(old["core"])
        changed = self._make_peer_envelope(
            peer_id,
            str(old_core["message_type"]),
            int(old_core["term"]),
            changed_payload,
            message_id=message_id,
        )
        response = self._post_peer_envelope(peer_id, changed)
        return {"authorized": False, "decision": "CONFLICT_REPLAY_SENT", "response_envelope": response}

    def inspect(self, permit_id: str | None = None) -> dict[str, Any]:
        snap = self.store.snapshot()
        return {
            "replica_id": self.replica_id,
            "pid": os.getpid(),
            "db_path": self.store.path,
            "current_term": int(snap["current_term"]),
            "leader_id": snap["leader_id"],
            "commit_index": int(snap["commit_index"]),
            "record": copy.deepcopy(snap["records"].get(permit_id)) if permit_id else None,
            "record_digest": digest(snap["records"].get(permit_id)) if permit_id and permit_id in snap["records"] else None,
            "message_ledger_count": self.store.ledger_count(),
            "effect_count": self.effects.count(),
        }


def _json_post(url: str, body: Mapping[str, Any], timeout: float = 2.0) -> dict[str, Any]:
    req = urlrequest.Request(url, data=canonical(body), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urlerror.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"authorized": None, "decision": "TRANSPORT_OUTCOME_UNKNOWN", "error_class": type(exc).__name__}


class ReplicaClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict[str, Any]:
        with urlrequest.urlopen(self.base_url + "/health", timeout=2.0) as response:
            return json.loads(response.read().decode("utf-8"))

    def post(self, path: str, **body: Any) -> dict[str, Any]:
        return _json_post(self.base_url + path, body)

    def inspect(self, permit_id: str | None = None) -> dict[str, Any]:
        return self.post("/inspect", permit_id=permit_id)


class ProcessQuorumClusterHarness:
    """Starts/stops three independent replica processes; never decides authority."""

    def __init__(self, root: str | Path, *, cluster_key: bytes) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.cluster_key = bytes(cluster_key)
        self.clock_file = self.root / "clock.txt"
        self.fault_file = self.root / "faults.json"
        self.effect_db = self.root / "effects.sqlite"
        self.clock_file.write_text("0", encoding="utf-8")
        self.fault_file.write_text('{"rules":{}}', encoding="utf-8")
        self.processes: dict[str, subprocess.Popen[bytes]] = {}

    @property
    def script_path(self) -> Path:
        return Path(__file__).resolve()

    def set_clock(self, value: int) -> None:
        temp = self.clock_file.with_suffix(".tmp")
        temp.write_text(str(int(value)), encoding="utf-8")
        temp.replace(self.clock_file)

    def set_faults(self, rules: Mapping[str, str]) -> None:
        temp = self.fault_file.with_suffix(".tmp")
        temp.write_text(json.dumps({"rules": dict(rules)}, sort_keys=True), encoding="utf-8")
        temp.replace(self.fault_file)

    def db_path(self, replica_id: str) -> Path:
        return self.root / f"{replica_id}.sqlite"

    def ready_path(self, replica_id: str) -> Path:
        return self.root / f"{replica_id}.ready.json"

    def start(self, replica_id: str, timeout_s: float = 5.0) -> dict[str, Any]:
        if replica_id in self.processes and self.processes[replica_id].poll() is None:
            raise RuntimeError(f"{replica_id} already running")
        self.ready_path(replica_id).unlink(missing_ok=True)
        args = [
            sys.executable,
            str(self.script_path),
            "--serve-replica", replica_id,
            "--db", str(self.db_path(replica_id)),
            "--cluster-dir", str(self.root),
            "--fault-file", str(self.fault_file),
            "--clock-file", str(self.clock_file),
            "--effect-db", str(self.effect_db),
            "--cluster-key-hex", self.cluster_key.hex(),
        ]
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.processes[replica_id] = proc
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"replica {replica_id} exited early with {proc.returncode}")
            if self.ready_path(replica_id).exists():
                return json.loads(self.ready_path(replica_id).read_text(encoding="utf-8"))
            time.sleep(0.02)
        self.stop(replica_id)
        raise TimeoutError(f"replica {replica_id} did not become ready")

    def start_all(self) -> dict[str, dict[str, Any]]:
        return {rid: self.start(rid) for rid in MEMBERS}

    def stop(self, replica_id: str) -> None:
        proc = self.processes.get(replica_id)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
        self.processes.pop(replica_id, None)

    def stop_all(self) -> None:
        for rid in list(self.processes):
            self.stop(rid)

    def restart(self, replica_id: str) -> dict[str, Any]:
        self.stop(replica_id)
        return self.start(replica_id)

    def client(self, replica_id: str) -> ReplicaClient:
        info = json.loads(self.ready_path(replica_id).read_text(encoding="utf-8"))
        return ReplicaClient(f"http://127.0.0.1:{int(info['port'])}")

    def __enter__(self) -> "ProcessQuorumClusterHarness":
        self.start_all()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop_all()


def serve_replica(args: argparse.Namespace) -> int:
    node = ProcessQuorumNode(
        replica_id=args.serve_replica,
        db_path=args.db,
        cluster_key=bytes.fromhex(args.cluster_key_hex),
        cluster_dir=args.cluster_dir,
        fault_file=args.fault_file,
        clock_file=args.clock_file,
        effect_db=args.effect_db,
    )

    class Handler(BaseHTTPRequestHandler):
        server_version = "ExpOPilot14Replica/1"

        def log_message(self, format, *values):
            return

        def _send(self, status: int, payload: Mapping[str, Any]) -> None:
            data = canonical(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            self.wfile.flush()

        def _body(self) -> dict[str, Any] | None:
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return None
            if size <= 0 or size > MAX_BODY_BYTES:
                return None
            try:
                value = json.loads(self.rfile.read(size).decode("utf-8"))
            except Exception:
                return None
            return value if isinstance(value, dict) else None

        def do_GET(self) -> None:
            if self.path != "/health":
                self._send(404, {"state": "NOT_FOUND"})
                return
            info = node.inspect()
            self._send(200, {"state": "READY", **info, "transport": "loopback-http-authenticated"})

        def do_POST(self) -> None:
            body = self._body()
            if body is None:
                self._send(400, deny("INVALID_BODY"))
                return
            try:
                if self.path == "/peer":
                    result = node.handle_peer(body)
                elif self.path == "/inspect":
                    result = node.inspect(body.get("permit_id"))
                elif self.path == "/client/elect":
                    result = node.elect(int(body.get("term", -1)), candidate_self_vote_copies=int(body.get("candidate_self_vote_copies", 1)))
                elif self.path == "/client/issue":
                    result = node.issue(str(body.get("permit_id", "")), body.get("bindings") or {})
                elif self.path == "/client/acquire":
                    result = node.acquire(str(body.get("permit_id", "")), str(body.get("owner_id", "")), body.get("bindings") or {})
                elif self.path == "/client/renew":
                    result = node.renew(str(body.get("permit_id", "")), str(body.get("owner_id", "")), int(body.get("lease_epoch", -1)), body.get("bindings") or {})
                elif self.path == "/client/takeover":
                    result = node.takeover(str(body.get("permit_id", "")), str(body.get("new_owner_id", "")), body.get("bindings") or {})
                elif self.path == "/client/execute":
                    result = node.execute(str(body.get("permit_id", "")), str(body.get("owner_id", "")), int(body.get("lease_epoch", -1)), body.get("bindings") or {}, crash_after_effect=bool(body.get("crash_after_effect", False)))
                elif self.path == "/client/finalize":
                    result = node.finalize(str(body.get("permit_id", "")), str(body.get("owner_id", "")), int(body.get("lease_epoch", -1)), body.get("bindings") or {}, str(body.get("result_digest", "")))
                elif self.path == "/client/authoritative-read":
                    result = node.authoritative_read(str(body.get("permit_id", "")))
                elif self.path == "/client/catch-up":
                    result = node.catch_up()
                elif self.path == "/test/release-delayed":
                    result = node.release_delayed()
                elif self.path == "/test/probe-peer":
                    result = node.probe_peer(str(body.get("peer_id", "")), str(body.get("message_type", "")), body.get("payload") or {}, term=body.get("term"))
                elif self.path == "/test/replay-outbound-conflict":
                    result = node.replay_outbound_conflict(str(body.get("message_id", "")), body.get("changed_payload") or {})
                elif self.path == "/test/response-history":
                    with node._history_lock:
                        result = {"responses": copy.deepcopy(node.response_history)}
                elif self.path == "/test/outbound-history":
                    with node._history_lock:
                        result = {"messages": [{"message_id": mid, "peer_id": peer, "envelope": env} for mid, (peer, env) in node.outbound_history.items()]}
                elif self.path == "/test/collect-responses":
                    responses = body.get("responses") if isinstance(body.get("responses"), list) else []
                    voters = node._distinct_positive_voters(responses, expected_type=str(body.get("expected_type", "")), expected_term=int(body.get("expected_term", -1)), positive_field=str(body.get("positive_field", "confirmed")), include_self=True)
                    result = {"quorum_confirmed": len(voters) >= QUORUM, "voters": voters}
                else:
                    self._send(404, {"state": "NOT_FOUND"})
                    return
            except Exception as exc:
                result = deny("PROCESS_HANDLER_EXCEPTION", error_class=type(exc).__name__, error=str(exc))
            self._send(200, result)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    ready = Path(args.cluster_dir) / f"{args.serve_replica}.ready.json"
    temp = ready.with_suffix(".tmp")
    temp.write_text(json.dumps({"replica_id": args.serve_replica, "pid": os.getpid(), "port": int(server.server_address[1]), "db_path": str(args.db)}, sort_keys=True), encoding="utf-8")
    temp.replace(ready)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve-replica", choices=MEMBERS)
    parser.add_argument("--db")
    parser.add_argument("--cluster-dir")
    parser.add_argument("--fault-file")
    parser.add_argument("--clock-file")
    parser.add_argument("--effect-db")
    parser.add_argument("--cluster-key-hex")
    args = parser.parse_args()
    if args.serve_replica:
        required = (args.db, args.cluster_dir, args.fault_file, args.clock_file, args.effect_db, args.cluster_key_hex)
        if not all(required):
            raise SystemExit("replica server arguments incomplete")
        return serve_replica(args)
    raise SystemExit("--serve-replica is required when invoked as a process")


if __name__ == "__main__":
    sys.exit(main())
