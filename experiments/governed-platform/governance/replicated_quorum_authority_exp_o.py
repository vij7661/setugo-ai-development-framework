"""EXP-O Pilot 13 deterministic three-replica quorum authority simulation.

This is a falsification harness, not a production consensus implementation.  It
makes quorum, term, commit-index, lease and use-time revalidation rules explicit
so unsafe distributed-authority assumptions can be tested before choosing a
production consensus substrate.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


MEMBERS = ("r1", "r2", "r3")
QUORUM = 2
LEASE_DURATION_MS = 1000
BINDING_FIELDS = (
    "semantic_payload_digest",
    "effect_digest",
    "idempotency_key",
    "worker_id",
    "worker_key_thumbprint",
    "effect_contract_id",
    "base_sha",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _deny(reason: str, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


def _binding_view(bindings: Mapping[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(bindings.get(field)) for field in BINDING_FIELDS}


def _binding_error(record: Mapping[str, Any], bindings: Mapping[str, Any]) -> str | None:
    for field in BINDING_FIELDS:
        if record.get(field) != bindings.get(field):
            return f"QUORUM_AUTHORITY_BINDING_MISMATCH:{field}"
    return None


@dataclass
class ReplicaState:
    replica_id: str
    current_term: int = 0
    leader_id: str | None = None
    commit_index: int = 0
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def clone_from(self, other: "ReplicaState") -> None:
        self.current_term = int(other.current_term)
        self.leader_id = other.leader_id
        self.commit_index = int(other.commit_index)
        self.records = copy.deepcopy(other.records)


class SQLiteEffectBoundary:
    """Durable idempotent effect sink used by Pilot 13 recovery tests."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quorum_effects (
                    idempotency_key TEXT PRIMARY KEY,
                    effect_digest TEXT NOT NULL,
                    result_digest TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def apply(self, *, idempotency_key: str, effect_digest: str) -> dict[str, Any]:
        if not idempotency_key or not effect_digest:
            return _deny("EFFECT_BINDING_REQUIRED")
        with closing(sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT effect_digest, result_digest FROM quorum_effects WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            if row is not None:
                if str(row["effect_digest"]) != effect_digest:
                    conn.rollback()
                    return _deny("IDEMPOTENCY_EFFECT_REBINDING_DENIED")
                conn.commit()
                return {
                    "authorized": True,
                    "executed": False,
                    "replayed": True,
                    "result_digest": str(row["result_digest"]),
                }
            result_digest = digest({"idempotency_key": idempotency_key, "effect_digest": effect_digest})
            conn.execute(
                "INSERT INTO quorum_effects(idempotency_key, effect_digest, result_digest) VALUES (?, ?, ?)",
                (idempotency_key, effect_digest, result_digest),
            )
            conn.commit()
            return {
                "authorized": True,
                "executed": True,
                "replayed": False,
                "result_digest": result_digest,
            }

    def count(self) -> int:
        with closing(sqlite3.connect(self.db_path)) as conn:
            row = conn.execute("SELECT COUNT(*) FROM quorum_effects").fetchone()
        return int(row[0])


class ReplicatedQuorumAuthorityCluster:
    """Three-replica deterministic authority cluster with majority-only writes."""

    def __init__(
        self,
        trusted_clock: Callable[[], int],
        *,
        cluster_id: str = "exp-o-p13-cluster",
        lease_duration_ms: int = LEASE_DURATION_MS,
    ) -> None:
        if lease_duration_ms <= 0:
            raise ValueError("lease duration must be positive")
        self.cluster_id = cluster_id
        self._clock = trusted_clock
        self.lease_duration_ms = int(lease_duration_ms)
        self.replicas = {rid: ReplicaState(rid) for rid in MEMBERS}
        self._links = {rid: set(MEMBERS) for rid in MEMBERS}

    def trusted_now_ms(self) -> int:
        return int(self._clock())

    def set_partitions(self, groups: Sequence[Sequence[str]]) -> None:
        flattened = [rid for group in groups for rid in group]
        if sorted(flattened) != sorted(MEMBERS) or len(flattened) != len(set(flattened)):
            raise ValueError("partitions must contain each frozen replica exactly once")
        self._links = {rid: set() for rid in MEMBERS}
        for group in groups:
            members = set(group)
            for rid in members:
                self._links[rid] = set(members)

    def heal_all(self) -> None:
        self.set_partitions([MEMBERS])

    def component(self, replica_id: str) -> set[str]:
        self._require_member(replica_id)
        return set(self._links[replica_id])

    def _require_member(self, replica_id: str) -> None:
        if replica_id not in self.replicas:
            raise ValueError(f"unknown replica {replica_id}")

    def elect(self, candidate_id: str, *, term: int, voters: Sequence[str] | None = None) -> dict[str, Any]:
        self._require_member(candidate_id)
        proposed = list(voters) if voters is not None else sorted(self.component(candidate_id))
        if len(proposed) != len(set(proposed)):
            return _deny("ELECTION_DUPLICATE_VOTER")
        if any(v not in self.replicas for v in proposed):
            return _deny("ELECTION_UNKNOWN_VOTER")
        if candidate_id not in proposed:
            return _deny("ELECTION_CANDIDATE_MUST_VOTE")
        if any(v not in self.component(candidate_id) for v in proposed):
            return _deny("ELECTION_VOTER_UNREACHABLE")
        if len(proposed) < QUORUM:
            return _deny("ELECTION_QUORUM_REQUIRED")
        max_term = max(self.replicas[v].current_term for v in proposed)
        if int(term) <= int(max_term):
            return _deny("ELECTION_TERM_NOT_MONOTONIC", max_observed_term=max_term)
        max_index = max(self.replicas[v].commit_index for v in proposed)
        candidate = self.replicas[candidate_id]
        if candidate.commit_index < max_index:
            return _deny("ELECTION_CANDIDATE_LOG_STALE", candidate_commit_index=candidate.commit_index, max_commit_index=max_index)

        # Candidate is the authoritative source for this election because it is
        # at least as up to date as every voter.  Voters catch up before the new
        # term is considered elected.
        source = copy.deepcopy(candidate)
        for voter in proposed:
            replica = self.replicas[voter]
            replica.clone_from(source)
            replica.current_term = int(term)
            replica.leader_id = candidate_id
        return {
            "authorized": True,
            "decision": "ELECTED",
            "leader_id": candidate_id,
            "term": int(term),
            "voters": sorted(proposed),
            "commit_index": candidate.commit_index,
        }

    def _leader_quorum(self, leader_id: str) -> tuple[list[str] | None, str | None]:
        self._require_member(leader_id)
        leader = self.replicas[leader_id]
        component = self.component(leader_id)
        if len(component) < QUORUM:
            return None, "QUORUM_UNAVAILABLE"
        if leader.leader_id != leader_id:
            return None, "NOT_CURRENT_LEADER"
        max_term = max(self.replicas[rid].current_term for rid in component)
        if leader.current_term < max_term:
            return None, "STALE_LEADER_TERM"
        voters = sorted(
            rid for rid in component
            if self.replicas[rid].current_term == leader.current_term
            and self.replicas[rid].leader_id == leader_id
        )
        if len(voters) < QUORUM:
            return None, "LEADERSHIP_NOT_QUORUM_CONFIRMED"
        return voters, None

    def _matching_record_voters(self, leader_id: str, permit_id: str) -> tuple[list[str] | None, str | None]:
        voters, error = self._leader_quorum(leader_id)
        if error:
            return None, error
        assert voters is not None
        leader = self.replicas[leader_id]
        record = leader.records.get(permit_id)
        if record is None:
            return None, "AUTHORITY_RECORD_MISSING"
        wanted_digest = digest(record)
        matches = [
            rid for rid in voters
            if self.replicas[rid].commit_index == leader.commit_index
            and digest(self.replicas[rid].records.get(permit_id)) == wanted_digest
        ]
        if len(matches) < QUORUM:
            return None, "AUTHORITY_RECORD_NOT_QUORUM_CONFIRMED"
        return matches, None

    def _certificate(self, leader_id: str, permit_id: str, voters: Sequence[str]) -> dict[str, Any]:
        leader = self.replicas[leader_id]
        record = leader.records[permit_id]
        selected = sorted(set(voters))[:QUORUM]
        return {
            "cluster_id": self.cluster_id,
            "term": int(leader.current_term),
            "leader_id": leader_id,
            "commit_index": int(leader.commit_index),
            "record_digest": digest(record),
            "bound_permit_id": permit_id,
            "lease_owner_gateway_instance_id": record.get("lease_owner_gateway_instance_id"),
            "lease_epoch": int(record.get("lease_epoch", 0)),
            "lease_expires_at_ms": record.get("lease_expires_at_ms"),
            "state": record.get("state"),
            "binding_digest": digest(_binding_view(record)),
            "voters": selected,
        }

    def validate_certificate_shape(self, certificate: Mapping[str, Any]) -> dict[str, Any]:
        voters = list(certificate.get("voters") or [])
        if len(voters) != len(set(voters)):
            return _deny("CERTIFICATE_DUPLICATE_VOTER")
        if len(voters) < QUORUM:
            return _deny("CERTIFICATE_QUORUM_REQUIRED")
        if any(v not in self.replicas for v in voters):
            return _deny("CERTIFICATE_UNKNOWN_VOTER")
        if certificate.get("cluster_id") != self.cluster_id:
            return _deny("CERTIFICATE_CLUSTER_MISMATCH")
        return {"authorized": True, "decision": "CERTIFICATE_SHAPE_VALID"}

    def _commit_record(self, leader_id: str, permit_id: str, record: Mapping[str, Any]) -> dict[str, Any]:
        voters, error = self._leader_quorum(leader_id)
        if error:
            return _deny(error)
        assert voters is not None
        leader = self.replicas[leader_id]
        next_index = max(self.replicas[rid].commit_index for rid in voters) + 1
        new_records = copy.deepcopy(leader.records)
        new_records[permit_id] = copy.deepcopy(dict(record))
        for rid in voters:
            replica = self.replicas[rid]
            replica.records = copy.deepcopy(new_records)
            replica.commit_index = int(next_index)
        certificate = self._certificate(leader_id, permit_id, voters)
        return {
            "authorized": True,
            "decision": "QUORUM_COMMITTED",
            "term": int(leader.current_term),
            "commit_index": int(next_index),
            "voters": certificate["voters"],
            "certificate": certificate,
        }

    def issue(self, leader_id: str, permit_id: str, bindings: Mapping[str, Any]) -> dict[str, Any]:
        for field in BINDING_FIELDS:
            if bindings.get(field) in (None, "", []):
                return _deny(f"AUTHORITY_BINDING_REQUIRED:{field}")
        voters, error = self._leader_quorum(leader_id)
        if error:
            return _deny(error)
        if permit_id in self.replicas[leader_id].records:
            return _deny("AUTHORITY_RECORD_ALREADY_EXISTS")
        record = {
            "bound_permit_id": permit_id,
            **_binding_view(bindings),
            "state": "ISSUED",
            "lease_owner_gateway_instance_id": None,
            "lease_epoch": 0,
            "lease_expires_at_ms": None,
            "authoritative_result_digest": None,
        }
        return self._commit_record(leader_id, permit_id, record)

    def acquire(self, leader_id: str, permit_id: str, *, owner_id: str, bindings: Mapping[str, Any]) -> dict[str, Any]:
        voters, error = self._matching_record_voters(leader_id, permit_id)
        if error:
            return _deny(error)
        record = copy.deepcopy(self.replicas[leader_id].records[permit_id])
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return _deny(mismatch)
        if record.get("state") != "ISSUED":
            return _deny("AUTHORITY_FIRST_ACQUIRE_REQUIRES_ISSUED")
        now_ms = self.trusted_now_ms()
        record.update(
            state="IN_FLIGHT",
            lease_owner_gateway_instance_id=owner_id,
            lease_epoch=1,
            lease_expires_at_ms=now_ms + self.lease_duration_ms,
        )
        committed = self._commit_record(leader_id, permit_id, record)
        if committed.get("authorized"):
            committed.update(
                disposition="FIRST_OWNER",
                trusted_now_ms=now_ms,
                lease_owner_gateway_instance_id=owner_id,
                lease_epoch=1,
                lease_expires_at_ms=record["lease_expires_at_ms"],
            )
        return committed

    def revalidate(
        self,
        leader_id: str,
        permit_id: str,
        *,
        owner_id: str,
        lease_epoch: int,
        bindings: Mapping[str, Any],
        cached_certificate: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        # cached_certificate is deliberately evidence only; authority always
        # comes from the fresh quorum read below.
        if cached_certificate is not None:
            shape = self.validate_certificate_shape(cached_certificate)
            if not shape.get("authorized"):
                return _deny(str(shape.get("reason", "CACHED_CERTIFICATE_INVALID")))
        voters, error = self._matching_record_voters(leader_id, permit_id)
        if error:
            return _deny(error)
        assert voters is not None
        record = self.replicas[leader_id].records[permit_id]
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return _deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return _deny("AUTHORITY_REVALIDATION_REQUIRES_IN_FLIGHT")
        if record.get("lease_owner_gateway_instance_id") != owner_id:
            return _deny("AUTHORITY_STALE_OWNER")
        if int(record.get("lease_epoch", 0)) != int(lease_epoch):
            return _deny("AUTHORITY_STALE_LEASE_EPOCH")
        now_ms = self.trusted_now_ms()
        expiry = record.get("lease_expires_at_ms")
        if expiry is None or now_ms >= int(expiry):
            return _deny("AUTHORITY_LEASE_EXPIRED", trusted_now_ms=now_ms, lease_expires_at_ms=expiry)
        certificate = self._certificate(leader_id, permit_id, voters)
        return {
            "authorized": True,
            "decision": "QUORUM_REVALIDATED",
            "term": self.replicas[leader_id].current_term,
            "commit_index": self.replicas[leader_id].commit_index,
            "trusted_now_ms": now_ms,
            "certificate": certificate,
        }

    def renew(self, leader_id: str, permit_id: str, *, owner_id: str, lease_epoch: int, bindings: Mapping[str, Any]) -> dict[str, Any]:
        voters, error = self._matching_record_voters(leader_id, permit_id)
        if error:
            return _deny(error)
        record = copy.deepcopy(self.replicas[leader_id].records[permit_id])
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return _deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return _deny("AUTHORITY_RENEW_REQUIRES_IN_FLIGHT")
        if record.get("lease_owner_gateway_instance_id") != owner_id:
            return _deny("AUTHORITY_RENEW_STALE_OWNER")
        if int(record.get("lease_epoch", 0)) != int(lease_epoch):
            return _deny("AUTHORITY_RENEW_STALE_EPOCH")
        now_ms = self.trusted_now_ms()
        old_expiry = record.get("lease_expires_at_ms")
        if old_expiry is None or now_ms >= int(old_expiry):
            return _deny("AUTHORITY_RENEW_LEASE_EXPIRED")
        new_expiry = now_ms + self.lease_duration_ms
        if new_expiry <= int(old_expiry):
            return _deny("AUTHORITY_RENEWAL_MUST_EXTEND_EXPIRY")
        record["lease_expires_at_ms"] = new_expiry
        committed = self._commit_record(leader_id, permit_id, record)
        if committed.get("authorized"):
            committed.update(
                disposition="LEASE_RENEWED",
                trusted_now_ms=now_ms,
                lease_epoch=int(lease_epoch),
                lease_expires_at_ms=new_expiry,
            )
        return committed

    def takeover(self, leader_id: str, permit_id: str, *, new_owner_id: str, bindings: Mapping[str, Any]) -> dict[str, Any]:
        voters, error = self._matching_record_voters(leader_id, permit_id)
        if error:
            return _deny(error)
        record = copy.deepcopy(self.replicas[leader_id].records[permit_id])
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return _deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return _deny("AUTHORITY_TAKEOVER_REQUIRES_IN_FLIGHT")
        now_ms = self.trusted_now_ms()
        expiry = record.get("lease_expires_at_ms")
        if expiry is None:
            return _deny("AUTHORITY_LEASE_EXPIRY_MISSING")
        if now_ms < int(expiry):
            return _deny(
                "AUTHORITY_LIVE_OWNER_UNEXPIRED",
                trusted_now_ms=now_ms,
                lease_expires_at_ms=int(expiry),
            )
        old_owner = record.get("lease_owner_gateway_instance_id")
        record["lease_owner_gateway_instance_id"] = new_owner_id
        record["lease_epoch"] = int(record.get("lease_epoch", 0)) + 1
        record["lease_expires_at_ms"] = now_ms + self.lease_duration_ms
        committed = self._commit_record(leader_id, permit_id, record)
        if committed.get("authorized"):
            committed.update(
                disposition="QUORUM_EXPIRY_TAKEOVER",
                previous_owner_gateway_instance_id=old_owner,
                lease_owner_gateway_instance_id=new_owner_id,
                lease_epoch=record["lease_epoch"],
                lease_expires_at_ms=record["lease_expires_at_ms"],
                trusted_now_ms=now_ms,
            )
        return committed

    def finalize(
        self,
        leader_id: str,
        permit_id: str,
        *,
        owner_id: str,
        lease_epoch: int,
        bindings: Mapping[str, Any],
        authoritative_result_digest: str,
    ) -> dict[str, Any]:
        if not authoritative_result_digest:
            return _deny("AUTHORITATIVE_RESULT_DIGEST_REQUIRED")
        voters, error = self._matching_record_voters(leader_id, permit_id)
        if error:
            return _deny(error)
        record = copy.deepcopy(self.replicas[leader_id].records[permit_id])
        mismatch = _binding_error(record, bindings)
        if mismatch:
            return _deny(mismatch)
        if record.get("state") != "IN_FLIGHT":
            return _deny("AUTHORITY_FINALIZE_REQUIRES_IN_FLIGHT")
        if record.get("lease_owner_gateway_instance_id") != owner_id:
            return _deny("AUTHORITY_FINALIZE_STALE_OWNER")
        if int(record.get("lease_epoch", 0)) != int(lease_epoch):
            return _deny("AUTHORITY_FINALIZE_STALE_EPOCH")
        expiry = record.get("lease_expires_at_ms")
        now_ms = self.trusted_now_ms()
        if expiry is None or now_ms >= int(expiry):
            return _deny("AUTHORITY_FINALIZE_LEASE_EXPIRED")
        record["state"] = "CONSUMED"
        record["authoritative_result_digest"] = authoritative_result_digest
        committed = self._commit_record(leader_id, permit_id, record)
        if committed.get("authorized"):
            committed.update(
                disposition="AUTHORITY_CONSUMED",
                authoritative_result_digest=authoritative_result_digest,
            )
        return committed

    def authoritative_read(self, replica_id: str, permit_id: str) -> dict[str, Any]:
        self._require_member(replica_id)
        component = self.component(replica_id)
        if len(component) < QUORUM:
            return {"authoritative": False, "reason": "QUORUM_UNAVAILABLE"}
        local = self.replicas[replica_id]
        max_term = max(self.replicas[rid].current_term for rid in component)
        if local.current_term < max_term:
            return {"authoritative": False, "reason": "STALE_REPLICA_TERM", "local_term": local.current_term, "max_term": max_term}
        local_record = local.records.get(permit_id)
        if local_record is None:
            return {"authoritative": False, "reason": "AUTHORITY_RECORD_MISSING"}
        local_digest = digest(local_record)
        matches = [
            rid for rid in component
            if self.replicas[rid].current_term == local.current_term
            and self.replicas[rid].leader_id == local.leader_id
            and self.replicas[rid].commit_index == local.commit_index
            and digest(self.replicas[rid].records.get(permit_id)) == local_digest
        ]
        if len(matches) < QUORUM:
            return {"authoritative": False, "reason": "STALE_REPLICA_NOT_QUORUM_CONFIRMED"}
        return {
            "authoritative": True,
            "term": local.current_term,
            "leader_id": local.leader_id,
            "commit_index": local.commit_index,
            "record": copy.deepcopy(local_record),
            "voters": sorted(matches)[:QUORUM],
        }

    def catch_up(self, replica_id: str) -> dict[str, Any]:
        self._require_member(replica_id)
        component = self.component(replica_id)
        if len(component) < QUORUM:
            return _deny("CATCH_UP_QUORUM_REQUIRED")
        source_id = max(
            component,
            key=lambda rid: (self.replicas[rid].current_term, self.replicas[rid].commit_index, rid),
        )
        source = self.replicas[source_id]
        target = self.replicas[replica_id]
        if (target.current_term, target.commit_index) > (source.current_term, source.commit_index):
            return _deny("CATCH_UP_WOULD_ROLL_BACK_TARGET")
        target.clone_from(source)
        return {
            "authorized": True,
            "decision": "CAUGHT_UP",
            "source_replica_id": source_id,
            "term": target.current_term,
            "commit_index": target.commit_index,
        }

    def inspect_replica(self, replica_id: str, permit_id: str) -> dict[str, Any]:
        self._require_member(replica_id)
        replica = self.replicas[replica_id]
        record = replica.records.get(permit_id)
        return {
            "replica_id": replica_id,
            "current_term": replica.current_term,
            "leader_id": replica.leader_id,
            "commit_index": replica.commit_index,
            "record": copy.deepcopy(record),
            "record_digest": digest(record) if record is not None else None,
            "component": sorted(self.component(replica_id)),
        }

    def execute(
        self,
        leader_id: str,
        permit_id: str,
        *,
        owner_id: str,
        lease_epoch: int,
        bindings: Mapping[str, Any],
        effect_boundary: SQLiteEffectBoundary,
        cached_certificate: Mapping[str, Any] | None = None,
        crash_after_effect: bool = False,
    ) -> dict[str, Any]:
        revalidated = self.revalidate(
            leader_id,
            permit_id,
            owner_id=owner_id,
            lease_epoch=lease_epoch,
            bindings=bindings,
            cached_certificate=cached_certificate,
        )
        if not revalidated.get("authorized"):
            return revalidated
        effect = effect_boundary.apply(
            idempotency_key=str(bindings["idempotency_key"]),
            effect_digest=str(bindings["effect_digest"]),
        )
        if not effect.get("authorized"):
            return effect
        if crash_after_effect:
            return {
                "authorized": None,
                "decision": "POST_EFFECT_FINALIZATION_UNKNOWN",
                "effect_result": effect,
                "certificate": revalidated["certificate"],
            }
        finalized = self.finalize(
            leader_id,
            permit_id,
            owner_id=owner_id,
            lease_epoch=lease_epoch,
            bindings=bindings,
            authoritative_result_digest=str(effect["result_digest"]),
        )
        return {
            **finalized,
            "effect_result": effect,
            "certificate": revalidated["certificate"],
        }
