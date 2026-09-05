from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import MemoryRecord


class SQLiteMemoryStore:
    """Single-node persistent shared memory for the MVP.

    This provides durable local persistence and transactional append semantics.
    It does not prove distributed consistency or multi-node failover.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL,
                    memory_class TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    provenance TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_role TEXT,
                    supersedes_version INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(record_id, version)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_record_version ON memory_records(record_id, version DESC)")

    @staticmethod
    def _from_row(row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            record_id=row["record_id"],
            memory_class=row["memory_class"],
            status=row["status"],
            version=int(row["version"]),
            provenance=row["provenance"],
            content=row["content"],
            source_role=row["source_role"],
            supersedes_version=row["supersedes_version"],
        )

    def append(self, record: MemoryRecord, *, external_authority: bool = False) -> None:
        record.validate()
        if record.memory_class == "AUTHORITATIVE" and not external_authority:
            raise PermissionError("authoritative memory requires external/platform authority")

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            latest_row = conn.execute(
                "SELECT * FROM memory_records WHERE record_id=? ORDER BY version DESC LIMIT 1",
                (record.record_id,),
            ).fetchone()
            if latest_row is None:
                if record.version != 1:
                    raise ValueError("new memory records must start at version 1")
            else:
                latest_version = int(latest_row["version"])
                if record.version <= latest_version:
                    raise ValueError("memory version must advance monotonically")
                if record.supersedes_version is not None and record.supersedes_version != latest_version:
                    raise ValueError("memory supersedes_version must bind latest version")

            conn.execute(
                """
                INSERT INTO memory_records(
                    record_id, memory_class, status, version, provenance,
                    content, source_role, supersedes_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.memory_class,
                    record.status,
                    record.version,
                    record.provenance,
                    record.content,
                    record.source_role,
                    record.supersedes_version,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def history(self, record_id: str | None = None) -> tuple[MemoryRecord, ...]:
        with self._connect() as conn:
            if record_id is None:
                rows = conn.execute("SELECT * FROM memory_records ORDER BY seq").fetchall()
            else:
                rows = conn.execute("SELECT * FROM memory_records WHERE record_id=? ORDER BY version", (record_id,)).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def current(self) -> tuple[MemoryRecord, ...]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT m.* FROM memory_records m
                JOIN (
                    SELECT record_id, MAX(version) AS max_version
                    FROM memory_records
                    GROUP BY record_id
                ) latest
                ON latest.record_id=m.record_id AND latest.max_version=m.version
                WHERE m.status='ACTIVE'
                ORDER BY m.record_id
                """
            ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def reviewer_visible(self) -> tuple[MemoryRecord, ...]:
        return tuple(
            r for r in self.current()
            if r.memory_class not in {"MODEL_PRIVATE", "PROTECTED_TRUTH"}
        )
