from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from .memory import VersionedMemoryStore
from .models import MemoryRecord


@dataclass(frozen=True)
class RetrievalQuery:
    """Platform-owned retrieval query binding for one reviewer context."""

    role: str
    request_id: str
    artifact_id: str | None = None
    artifact_version: int | None = None
    artifact_hash: str | None = None


@dataclass(frozen=True)
class RetrievedRecordBinding:
    """Auditable identity of a memory record included in reviewer context."""

    record_id: str
    version: int
    memory_class: str
    provenance: str
    content_hash: str


@dataclass(frozen=True)
class RetrievalResult:
    """Retrieved records plus the evidence needed to reconstruct what was seen."""

    records: tuple[MemoryRecord, ...]
    strategy: str
    strategy_version: str
    index_id: str | None
    index_version: str | None
    query_artifact_hash: str | None
    bindings: tuple[RetrievedRecordBinding, ...]

    def audit_view(self) -> dict:
        return {
            "strategy": self.strategy,
            "strategy_version": self.strategy_version,
            "index_id": self.index_id,
            "index_version": self.index_version,
            "query_artifact_hash": self.query_artifact_hash,
            "retrieved_records": [
                {
                    "record_id": binding.record_id,
                    "version": binding.version,
                    "memory_class": binding.memory_class,
                    "provenance": binding.provenance,
                    "content_hash": binding.content_hash,
                }
                for binding in self.bindings
            ],
        }


class ContextRetriever(Protocol):
    """Replaceable retrieval boundary below review/governance decision logic."""

    def retrieve(
        self,
        *,
        query: RetrievalQuery,
        memory: VersionedMemoryStore,
    ) -> RetrievalResult: ...


def _binding(record: MemoryRecord) -> RetrievedRecordBinding:
    return RetrievedRecordBinding(
        record_id=record.record_id,
        version=record.version,
        memory_class=record.memory_class,
        provenance=record.provenance,
        content_hash=sha256(record.content.encode("utf-8")).hexdigest(),
    )


class ReturnAllRetriever:
    """Current MVP behavior, made explicit behind the retrieval interface.

    Visibility policy remains owned by VersionedMemoryStore.reviewer_visible().
    The retriever does not receive protected/model-private records and excludes
    ambient REVIEW_EVIDENCE exactly as the previous ContextCompiler did.
    """

    STRATEGY = "RETURN_ALL_REVIEWER_VISIBLE"
    STRATEGY_VERSION = "1"

    def retrieve(
        self,
        *,
        query: RetrievalQuery,
        memory: VersionedMemoryStore,
    ) -> RetrievalResult:
        records = tuple(
            record
            for record in memory.reviewer_visible()
            if record.memory_class != "REVIEW_EVIDENCE"
        )
        return RetrievalResult(
            records=records,
            strategy=self.STRATEGY,
            strategy_version=self.STRATEGY_VERSION,
            index_id=None,
            index_version=None,
            query_artifact_hash=query.artifact_hash,
            bindings=tuple(_binding(record) for record in records),
        )
