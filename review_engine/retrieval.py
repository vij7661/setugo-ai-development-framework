from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from .memory import VersionedMemoryStore
from .models import MemoryRecord


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
MANDATORY_RETRIEVAL_CLASSES = frozenset({"AUTHORITATIVE"})


@dataclass(frozen=True)
class RetrievalQuery:
    """Platform-owned retrieval query binding for one reviewer context."""

    role: str
    request_id: str
    artifact_id: str | None = None
    artifact_version: int | None = None
    artifact_hash: str | None = None
    # Platform-constructed retrieval text. This is retrieval input only; it does
    # not change reviewer authority or allow the retriever to create memory.
    query_text: str = ""


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


def _eligible_records(memory: VersionedMemoryStore) -> tuple[MemoryRecord, ...]:
    return tuple(
        record
        for record in memory.reviewer_visible()
        if record.memory_class != "REVIEW_EVIDENCE"
    )


class ReturnAllRetriever:
    """Current compatibility behavior behind the retrieval interface."""

    STRATEGY = "RETURN_ALL_REVIEWER_VISIBLE"
    STRATEGY_VERSION = "1"

    def retrieve(
        self,
        *,
        query: RetrievalQuery,
        memory: VersionedMemoryStore,
    ) -> RetrievalResult:
        records = _eligible_records(memory)
        return RetrievalResult(
            records=records,
            strategy=self.STRATEGY,
            strategy_version=self.STRATEGY_VERSION,
            index_id=None,
            index_version=None,
            query_artifact_hash=query.artifact_hash,
            bindings=tuple(_binding(record) for record in records),
        )


class GovernedLexicalRetriever:
    """Deterministic selective retrieval with a non-droppable governance floor.

    This is a bounded product retriever, not a semantic-completeness oracle. It
    scores reviewer-visible non-mandatory records by deterministic token overlap
    with platform-constructed query text. AUTHORITATIVE records are always
    included regardless of score. Protected/model-private/review-evidence records
    remain excluded upstream and cannot be reintroduced by retrieval.

    Exact record/version/content bindings and a deterministic index fingerprint
    are returned so the model-visible context can be audited after the fact.
    """

    STRATEGY = "GOVERNED_LEXICAL_OVERLAP"
    STRATEGY_VERSION = "1"

    def __init__(self, *, max_nonmandatory_records: int = 8, minimum_overlap: int = 1) -> None:
        if max_nonmandatory_records < 0:
            raise ValueError("max_nonmandatory_records must be >= 0")
        if minimum_overlap < 1:
            raise ValueError("minimum_overlap must be >= 1")
        self.max_nonmandatory_records = max_nonmandatory_records
        self.minimum_overlap = minimum_overlap

    @staticmethod
    def _tokens(text: str) -> frozenset[str]:
        return frozenset(token.lower() for token in TOKEN_RE.findall(text))

    def _index_identity(self, eligible: tuple[MemoryRecord, ...]) -> tuple[str, str]:
        inventory = [
            {
                "record_id": record.record_id,
                "version": record.version,
                "memory_class": record.memory_class,
                "provenance": record.provenance,
                "content_hash": _binding(record).content_hash,
            }
            for record in sorted(eligible, key=lambda item: (item.record_id, item.version))
        ]
        canonical = json.dumps(
            {
                "strategy": self.STRATEGY,
                "strategy_version": self.STRATEGY_VERSION,
                "max_nonmandatory_records": self.max_nonmandatory_records,
                "minimum_overlap": self.minimum_overlap,
                "inventory": inventory,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        return f"memory-index:{digest[:16]}", digest

    def retrieve(
        self,
        *,
        query: RetrievalQuery,
        memory: VersionedMemoryStore,
    ) -> RetrievalResult:
        eligible = _eligible_records(memory)
        mandatory = [
            record for record in eligible
            if record.memory_class in MANDATORY_RETRIEVAL_CLASSES
        ]
        nonmandatory = [
            record for record in eligible
            if record.memory_class not in MANDATORY_RETRIEVAL_CLASSES
        ]
        query_tokens = self._tokens(query.query_text)
        scored: list[tuple[int, str, int, MemoryRecord]] = []
        for record in nonmandatory:
            overlap = len(query_tokens & self._tokens(record.content))
            if overlap >= self.minimum_overlap:
                scored.append((-overlap, record.record_id, record.version, record))
        scored.sort(key=lambda item: (item[0], item[1], item[2]))
        selected_nonmandatory = [
            item[3] for item in scored[: self.max_nonmandatory_records]
        ]

        selected = tuple(
            sorted(
                mandatory + selected_nonmandatory,
                key=lambda record: (record.memory_class != "AUTHORITATIVE", record.record_id, record.version),
            )
        )
        index_id, index_version = self._index_identity(eligible)
        return RetrievalResult(
            records=selected,
            strategy=self.STRATEGY,
            strategy_version=self.STRATEGY_VERSION,
            index_id=index_id,
            index_version=index_version,
            query_artifact_hash=query.artifact_hash,
            bindings=tuple(_binding(record) for record in selected),
        )
