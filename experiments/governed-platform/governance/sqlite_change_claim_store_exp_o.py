"""Persistent SQLite Change Claim Registry for EXP-O Pilot 2.

This module exists to falsify transactional/concurrency semantics in CI.  It is
not the production persistence recommendation and is not wired into EXP-N.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable


def _canonical_resources(resources: Iterable[str]) -> list[str]:
    normalized = sorted({str(item).strip() for item in resources if str(item).strip()})
    if not normalized:
        raise ValueError("claim resource scope cannot be empty")
    return normalized


def _intent_hash(task_id: str, base_sha: str, resources: list[str], mode: str) -> str:
    payload = {
        "task_id": task_id,
        "base_sha": base_sha,
        "resources": resources,
        "mode": mode,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _claim_prefix(resource: str) -> str:
    if resource.endswith("/**"):
        return resource[:-3]
    if resource.endswith("*"):
        return resource[:-1]
    return resource


def resources_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    lp = _claim_prefix(left)
    rp = _claim_prefix(right)
    return lp.startswith(rp) or rp.startswith(lp)


class SQLiteChangeClaimStore:
    def __init__(self, path: str | Path, *, timeout_seconds: float = 5.0) -> None:
        self.path = str(path)
        self.timeout_seconds = timeout_seconds
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=self.timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS claim_state (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    next_epoch INTEGER NOT NULL CHECK (next_epoch >= 1)
                )
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO claim_state(singleton, next_epoch) VALUES (1, 1)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS change_claims (
                    claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL UNIQUE,
                    intent_hash TEXT NOT NULL,
                    base_sha TEXT NOT NULL,
                    resources_json TEXT NOT NULL,
                    mode TEXT NOT NULL CHECK (mode IN ('EXCLUSIVE', 'PARALLEL_PROPOSAL')),
                    disposition TEXT NOT NULL CHECK (
                        disposition IN ('EXCLUSIVE_GRANTED', 'PARALLEL_PROPOSAL_GRANTED')
                    ),
                    claim_epoch INTEGER NOT NULL UNIQUE,
                    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'RELEASED'))
                )
                """
            )

    def request_claim(
        self,
        *,
        task_id: str,
        base_sha: str,
        resources: Iterable[str],
        mode: str,
        inject_failure_before_commit: bool = False,
    ) -> dict[str, Any]:
        if not task_id or not base_sha:
            return {"disposition": "DENIED_MALFORMED_CLAIM"}
        if mode not in {"EXCLUSIVE", "PARALLEL_PROPOSAL"}:
            return {"disposition": "DENIED_INVALID_MODE"}
        try:
            normalized_resources = _canonical_resources(resources)
        except ValueError:
            return {"disposition": "DENIED_EMPTY_SCOPE"}
        intent_hash = _intent_hash(task_id, base_sha, normalized_resources, mode)

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")

            existing = connection.execute(
                "SELECT * FROM change_claims WHERE task_id = ?", (task_id,)
            ).fetchone()
            if existing is not None:
                if existing["intent_hash"] != intent_hash:
                    connection.rollback()
                    return {
                        "disposition": "CLAIM_INTENT_MISMATCH",
                        "claim_id": existing["claim_id"],
                        "claim_epoch": existing["claim_epoch"],
                    }
                connection.commit()
                return {
                    "disposition": existing["disposition"],
                    "claim_id": existing["claim_id"],
                    "claim_epoch": existing["claim_epoch"],
                    "retry": True,
                }

            active_rows = connection.execute(
                "SELECT task_id, resources_json, mode FROM change_claims WHERE status = 'ACTIVE'"
            ).fetchall()
            overlapping_tasks: list[str] = []
            for row in active_rows:
                other_resources = json.loads(row["resources_json"])
                overlap = any(
                    resources_overlap(left, right)
                    for left in normalized_resources
                    for right in other_resources
                )
                if not overlap:
                    continue
                overlapping_tasks.append(row["task_id"])
                if mode == "EXCLUSIVE" or row["mode"] == "EXCLUSIVE":
                    connection.rollback()
                    return {
                        "disposition": "WAITING_CONFLICT",
                        "conflicts_with": sorted(overlapping_tasks),
                    }

            state = connection.execute(
                "SELECT next_epoch FROM claim_state WHERE singleton = 1"
            ).fetchone()
            if state is None:
                raise RuntimeError("claim_state missing")
            epoch = int(state["next_epoch"])
            disposition = (
                "EXCLUSIVE_GRANTED" if mode == "EXCLUSIVE" else "PARALLEL_PROPOSAL_GRANTED"
            )
            cursor = connection.execute(
                """
                INSERT INTO change_claims(
                    task_id, intent_hash, base_sha, resources_json, mode,
                    disposition, claim_epoch, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
                """,
                (
                    task_id,
                    intent_hash,
                    base_sha,
                    json.dumps(normalized_resources, separators=(",", ":")),
                    mode,
                    disposition,
                    epoch,
                ),
            )
            connection.execute(
                "UPDATE claim_state SET next_epoch = ? WHERE singleton = 1", (epoch + 1,)
            )

            if inject_failure_before_commit:
                raise RuntimeError("INJECTED_FAILURE_BEFORE_COMMIT")

            connection.commit()
            return {
                "disposition": disposition,
                "claim_id": cursor.lastrowid,
                "claim_epoch": epoch,
                "overlaps": sorted(overlapping_tasks),
                "retry": False,
            }
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def active_claims(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM change_claims WHERE status = 'ACTIVE' ORDER BY claim_epoch"
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_claim(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM change_claims WHERE task_id = ?", (task_id,)
            ).fetchone()
            return None if row is None else self._row_to_dict(row)

    def next_epoch(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT next_epoch FROM claim_state WHERE singleton = 1"
            ).fetchone()
            if row is None:
                raise RuntimeError("claim_state missing")
            return int(row["next_epoch"])

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "claim_id": row["claim_id"],
            "task_id": row["task_id"],
            "intent_hash": row["intent_hash"],
            "base_sha": row["base_sha"],
            "resources": json.loads(row["resources_json"]),
            "mode": row["mode"],
            "disposition": row["disposition"],
            "claim_epoch": row["claim_epoch"],
            "status": row["status"],
        }
