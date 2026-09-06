from __future__ import annotations

from copy import deepcopy
from hashlib import sha256

from .models import ReviewArtifact, ReviewerConfig, ReviewRequest
from .orchestrator import ReviewEngine, _artifact_view


MANDATORY_MEMORY_CLASSES = frozenset({"AUTHORITATIVE"})


def _memory_identity(record: dict) -> tuple[str, int]:
    return str(record.get("record_id", "")), int(record.get("version", 0))


def _content_hash(record: dict) -> str:
    return sha256(str(record.get("content", "")).encode("utf-8")).hexdigest()


def _validate_retrieval_manifest(
    *,
    context: dict,
    expected_memory: list[dict],
    artifact: ReviewArtifact | None,
) -> str | None:
    """Validate selective retrieval without granting the retriever policy authority.

    The platform independently derives the eligible reviewer-visible set, then
    requires the model-visible memory to be an exact subset of that set. Records
    with platform-governance significance remain mandatory regardless of future
    semantic similarity scores.
    """
    selected = context.get("memory")
    if not isinstance(selected, list):
        return "model-visible shared memory is not a list"

    eligible = {_memory_identity(record): record for record in expected_memory}
    if len(eligible) != len(expected_memory):
        return "platform reviewer-visible memory contains duplicate record identities"

    selected_by_identity: dict[tuple[str, int], dict] = {}
    for record in selected:
        if not isinstance(record, dict):
            return "model-visible shared memory contains a non-object record"
        identity = _memory_identity(record)
        if identity in selected_by_identity:
            return "model-visible shared memory contains duplicate record identities"
        expected = eligible.get(identity)
        if expected is None or record != expected:
            return "model-visible shared memory contains an unauthorized or mutated record"
        selected_by_identity[identity] = record

    mandatory = {
        identity
        for identity, record in eligible.items()
        if record.get("memory_class") in MANDATORY_MEMORY_CLASSES
    }
    missing_mandatory = mandatory - set(selected_by_identity)
    if missing_mandatory:
        return "retrieval omitted mandatory governance memory"

    retrieval = context.get("retrieval")
    if not isinstance(retrieval, dict):
        return "retrieval evidence manifest missing"
    if not isinstance(retrieval.get("strategy"), str) or not retrieval.get("strategy"):
        return "retrieval strategy missing"
    if not isinstance(retrieval.get("strategy_version"), str) or not retrieval.get("strategy_version"):
        return "retrieval strategy version missing"

    expected_artifact_hash = artifact.artifact_hash if artifact is not None else None
    if retrieval.get("query_artifact_hash") != expected_artifact_hash:
        return "retrieval manifest artifact hash disagrees with platform artifact"

    bindings = retrieval.get("retrieved_records")
    if not isinstance(bindings, list):
        return "retrieval record bindings missing"
    if len(bindings) != len(selected):
        return "retrieval record bindings do not match selected memory cardinality"

    binding_by_identity: dict[tuple[str, int], dict] = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            return "retrieval record binding is not an object"
        identity = str(binding.get("record_id", "")), int(binding.get("version", 0))
        if identity in binding_by_identity:
            return "retrieval manifest contains duplicate record bindings"
        record = selected_by_identity.get(identity)
        if record is None:
            return "retrieval manifest references memory not shown to reviewer"
        if binding.get("memory_class") != record.get("memory_class"):
            return "retrieval manifest memory class disagrees with selected record"
        if binding.get("provenance") != record.get("provenance"):
            return "retrieval manifest provenance disagrees with selected record"
        if binding.get("content_hash") != _content_hash(record):
            return "retrieval manifest content hash disagrees with selected record"
        binding_by_identity[identity] = binding

    if set(binding_by_identity) != set(selected_by_identity):
        return "retrieval manifest does not bind the exact selected memory set"
    return None


class RetrievalAwareReviewEngine(ReviewEngine):
    """ReviewEngine variant ready for future selective RAG retrieval.

    Existing orchestration, qualification, decision, correction and reviewer
    independence logic is inherited unchanged. Only reviewer-context admission
    and evidence retention are extended for selective retrieval.
    """

    _COMPLETION_PHASE = {
        "R1_COMPLETED": "R1_INITIAL",
        "R2_COMPLETED": "R2_INDEPENDENT",
        "R1_REVISED": "R1_SCOPED_CORRECTION",
        "R3_INDEPENDENT_COMPLETED": "R3_INDEPENDENT",
        "R3_ADJUDICATION_COMPLETED": "R3_ADJUDICATION",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._retrieval_evidence: dict[tuple[str, str], dict] = {}

    @staticmethod
    def _reviewer_context_failure(
        context: dict,
        *,
        config: ReviewerConfig,
        request: ReviewRequest,
        phase: str,
        artifact: ReviewArtifact | None,
        expected_memory: list[dict],
    ) -> str | None:
        if not isinstance(context, dict):
            return "model-visible reviewer context is not an object"
        if context.get("role") != config.role:
            return "model-visible reviewer role disagrees with platform routing"
        if context.get("request_id") != request.request_id:
            return "model-visible request id disagrees with platform request"

        retrieval_failure = _validate_retrieval_manifest(
            context=context,
            expected_memory=expected_memory,
            artifact=artifact,
        )
        if retrieval_failure:
            return retrieval_failure

        if phase in {"R1_INITIAL", "R2_INDEPENDENT", "R1_SCOPED_CORRECTION", "R3_INDEPENDENT"}:
            if context.get("user_input") != request.user_input:
                return "model-visible user input disagrees with platform request"

        expected_phase = {
            "R3_INDEPENDENT": "INDEPENDENT",
            "R3_ADJUDICATION": "ADJUDICATION",
        }.get(phase)
        if expected_phase is not None and context.get("phase") != expected_phase:
            return "model-visible reviewer phase disagrees with platform routing"
        if phase == "R1_SCOPED_CORRECTION" and context.get("mode") != "SCOPED_CORRECTION":
            return "model-visible correction mode disagrees with platform routing"
        if phase == "R1_INITIAL" and ("artifact" in context or context.get("mode") == "SCOPED_CORRECTION"):
            return "initial R1 context contains unauthorized correction/artifact scope"

        if artifact is None:
            if phase != "R1_INITIAL":
                return "platform artifact binding is missing for reviewer phase"
        else:
            if context.get("artifact") != _artifact_view(artifact):
                return "model-visible artifact disagrees with platform artifact binding"
            if phase == "R3_ADJUDICATION" and context.get("artifact_hash") != artifact.artifact_hash:
                return "R3 adjudication compatibility hash disagrees with platform artifact"
        return None

    def _invoke_reviewer(self, config, context, **kwargs):
        session_id = kwargs["session_id"]
        phase = kwargs["phase"]
        response, failure = super()._invoke_reviewer(config, context, **kwargs)
        if failure is None:
            self._retrieval_evidence[(session_id, phase)] = deepcopy(context.get("retrieval", {}))
        return response, failure

    def _emit(self, session_id: str, event_type: str, payload: dict) -> None:
        retained = dict(payload)
        phase = self._COMPLETION_PHASE.get(event_type)
        if phase is not None:
            retrieval = self._retrieval_evidence.get((session_id, phase))
            if retrieval is not None:
                retained["retrieval_evidence"] = deepcopy(retrieval)
        super()._emit(session_id, event_type, retained)
