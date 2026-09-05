from __future__ import annotations

from collections import defaultdict

from .models import MemoryRecord


class VersionedMemoryStore:
    """Append-only logical memory with lifecycle-aware current views.

    The in-memory implementation is intentionally small for the MVP. Durable
    persistence will be added behind this interface; callers must not infer
    production durability from this class.
    """

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def append(self, record: MemoryRecord, *, external_authority: bool = False) -> None:
        record.validate()
        if record.memory_class == "AUTHORITATIVE" and not external_authority:
            raise PermissionError("authoritative memory requires external/platform authority")

        history = [r for r in self._records if r.record_id == record.record_id]
        if history:
            latest = max(history, key=lambda r: r.version)
            if record.version <= latest.version:
                raise ValueError("memory version must advance monotonically")
            if record.supersedes_version is not None and record.supersedes_version != latest.version:
                raise ValueError("memory supersedes_version must bind the latest version")
        elif record.version != 1:
            raise ValueError("new memory records must start at version 1")

        self._records.append(record)

    def history(self, record_id: str | None = None) -> tuple[MemoryRecord, ...]:
        if record_id is None:
            return tuple(self._records)
        return tuple(r for r in self._records if r.record_id == record_id)

    def current(self) -> tuple[MemoryRecord, ...]:
        grouped: dict[str, list[MemoryRecord]] = defaultdict(list)
        for record in self._records:
            grouped[record.record_id].append(record)

        result: list[MemoryRecord] = []
        for records in grouped.values():
            latest = max(records, key=lambda r: r.version)
            if latest.status == "ACTIVE":
                result.append(latest)
        return tuple(sorted(result, key=lambda r: r.record_id))

    def reviewer_visible(self) -> tuple[MemoryRecord, ...]:
        result: list[MemoryRecord] = []
        for record in self.current():
            if record.memory_class in {"MODEL_PRIVATE", "PROTECTED_TRUTH"}:
                continue
            result.append(record)
        return tuple(result)
