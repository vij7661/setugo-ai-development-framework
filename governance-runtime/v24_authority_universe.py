"""V24-I2 authority-universe, sink, graph, and functional-closure construction.

This module is intentionally evidence-only.  It constructs and validates the
closed-world records required by the frozen V24 design but does not grant or
apply authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
FUNCTIONAL_CATCH_ALL = (
    "ANY_ENTITY_OR_PATH_CAPABLE_OF_MATERIALLY_CREATING_MUTATING_QUALIFYING_"
    "SUPPRESSING_PUBLISHING_OR_EFFECTING_AUTHORITY"
)


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _ids(records: Iterable[Mapping[str, Any]], key: str, problems: list[str], prefix: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        value = record.get(key)
        if not isinstance(value, str) or not value:
            problems.append(f"{prefix}_ID_INVALID")
            continue
        if value in result:
            problems.append(f"{prefix}_ID_DUPLICATE:{value}")
            continue
        result[value] = record
    return result


def _string_set(value: Any) -> set[str] | None:
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        return None
    return set(value)


def validate_authority_universe_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a V24 functional authority universe as a closed-world bundle.

    The independent projection is an input to this validator.  The validator
    never derives completeness from the candidate registry itself.
    """
    problems: list[str] = []
    generation = bundle.get("governance_generation_id")
    if not isinstance(generation, str) or not generation:
        problems.append("GOVERNANCE_GENERATION_ID_REQUIRED")

    universe = bundle.get("authority_universe_contract")
    if not isinstance(universe, Mapping):
        universe = {}
        problems.append("AUTHORITY_UNIVERSE_CONTRACT_REQUIRED")
    else:
        classes = _string_set(universe.get("supported_authority_classes"))
        if classes is None:
            problems.append("AUTHORITY_CLASS_SET_INVALID")
            classes = set()
        if FUNCTIONAL_CATCH_ALL not in classes:
            problems.append("FUNCTIONAL_CATCH_ALL_MISSING")
        if universe.get("unknown_class_behavior") != "FAIL_CLOSED_AUTHORITY_ADMISSION_REQUIRED":
            problems.append("UNKNOWN_CLASS_FAIL_CLOSED_REQUIRED")

    sinks = bundle.get("authority_sinks")
    effectors = bundle.get("consequential_effectors")
    graph_edges = bundle.get("dependency_edges")
    paths = bundle.get("effect_paths")
    control_planes = bundle.get("control_planes")
    subjects = bundle.get("completeness_required_subjects")
    projection = bundle.get("independent_universe_projection")

    for name, value in (
        ("authority_sinks", sinks),
        ("consequential_effectors", effectors),
        ("dependency_edges", graph_edges),
        ("effect_paths", paths),
        ("control_planes", control_planes),
        ("completeness_required_subjects", subjects),
    ):
        if not isinstance(value, list):
            problems.append(f"{name.upper()}_MISSING")
    sinks = sinks if isinstance(sinks, list) else []
    effectors = effectors if isinstance(effectors, list) else []
    graph_edges = graph_edges if isinstance(graph_edges, list) else []
    paths = paths if isinstance(paths, list) else []
    control_planes = control_planes if isinstance(control_planes, list) else []
    subjects = subjects if isinstance(subjects, list) else []

    sink_by_id = _ids(sinks, "sink_id", problems, "SINK")
    effector_by_id = _ids(effectors, "effector_id", problems, "EFFECTOR")
    path_by_id = _ids(paths, "path_id", problems, "PATH")
    plane_by_id = _ids(control_planes, "control_plane_id", problems, "CONTROL_PLANE")
    subject_by_id = _ids(subjects, "subject_id", problems, "COMPLETENESS_SUBJECT")

    edge_keys: set[tuple[str, str, str]] = set()
    for edge in graph_edges:
        if not isinstance(edge, Mapping):
            problems.append("GRAPH_EDGE_MALFORMED")
            continue
        source = edge.get("source_id")
        target = edge.get("target_id")
        edge_type = edge.get("edge_type")
        predicate_id = edge.get("predicate_id")
        if not all(isinstance(x, str) and x for x in (source, target, edge_type, predicate_id)):
            problems.append("GRAPH_EDGE_FIELDS_INVALID")
            continue
        key = (source, target, edge_type)
        if key in edge_keys:
            problems.append(f"GRAPH_EDGE_DUPLICATE:{source}:{target}:{edge_type}")
        edge_keys.add(key)
        if edge.get("material") is not True:
            problems.append(f"GRAPH_EDGE_MATERIALITY_NOT_EXPLICIT:{source}:{target}:{edge_type}")

    for sink_id, sink in sink_by_id.items():
        writers = _string_set(sink.get("admitted_writer_ids"))
        effect_classes = _string_set(sink.get("effect_classes"))
        required_planes = _string_set(sink.get("required_control_plane_ids"))
        if writers is None or not writers:
            problems.append(f"SINK_WRITER_SET_REQUIRED:{sink_id}")
        if effect_classes is None or not effect_classes:
            problems.append(f"SINK_EFFECT_CLASS_REQUIRED:{sink_id}")
        if required_planes is None or not required_planes:
            problems.append(f"SINK_CONTROL_PLANE_SET_REQUIRED:{sink_id}")
        else:
            for plane in required_planes:
                if plane not in plane_by_id:
                    problems.append(f"SINK_CONTROL_PLANE_UNKNOWN:{sink_id}:{plane}")
        if sink.get("unadmitted_writer_behavior") != "DENY":
            problems.append(f"SINK_UNADMITTED_WRITER_NOT_DENY:{sink_id}")
        if sink.get("generation_id") != generation:
            problems.append(f"SINK_GENERATION_MISMATCH:{sink_id}")

    for effector_id, effector in effector_by_id.items():
        sink_id = effector.get("sink_id")
        if sink_id not in sink_by_id:
            problems.append(f"EFFECTOR_SINK_UNKNOWN:{effector_id}:{sink_id}")
        classes = _string_set(effector.get("authority_classes"))
        if classes is None or not classes:
            problems.append(f"EFFECTOR_AUTHORITY_CLASS_REQUIRED:{effector_id}")
        if effector.get("generation_id") != generation:
            problems.append(f"EFFECTOR_GENERATION_MISMATCH:{effector_id}")

    expected_graph_edges: set[tuple[str, str, str]] = set()
    observed_material_paths: set[str] = set()
    for path_id, path in path_by_id.items():
        source = path.get("source_component_id")
        sink_id = path.get("sink_id")
        functional_effects = _string_set(path.get("functional_effects"))
        admitted_classes = _string_set(path.get("admitted_authority_classes"))
        required_planes = _string_set(path.get("control_plane_ids"))
        guards = _string_set(path.get("guard_ids"))
        material = path.get("material_authority_effect") is True
        observed = path.get("runtime_observed") is True
        if material and observed:
            observed_material_paths.add(path_id)
        if not isinstance(source, str) or not source:
            problems.append(f"PATH_SOURCE_REQUIRED:{path_id}")
        if sink_id not in sink_by_id:
            problems.append(f"PATH_SINK_UNKNOWN:{path_id}:{sink_id}")
        if functional_effects is None or (material and not functional_effects):
            problems.append(f"PATH_FUNCTIONAL_EFFECTS_REQUIRED:{path_id}")
        if admitted_classes is None or (material and not admitted_classes):
            problems.append(f"PATH_AUTHORITY_ADMISSION_REQUIRED:{path_id}")
        else:
            supported = _string_set(universe.get("supported_authority_classes")) or set()
            for klass in admitted_classes:
                if klass not in supported and klass != FUNCTIONAL_CATCH_ALL:
                    problems.append(f"PATH_UNKNOWN_AUTHORITY_CLASS:{path_id}:{klass}")
        if required_planes is None or (material and not required_planes):
            problems.append(f"PATH_CONTROL_PLANE_REQUIRED:{path_id}")
        else:
            for plane in required_planes:
                if plane not in plane_by_id:
                    problems.append(f"PATH_CONTROL_PLANE_UNKNOWN:{path_id}:{plane}")
        if guards is None or (material and not guards):
            problems.append(f"PATH_GUARD_REQUIRED:{path_id}")
        if path.get("generation_id") != generation:
            problems.append(f"PATH_GENERATION_MISMATCH:{path_id}")
        if isinstance(source, str) and source and isinstance(sink_id, str) and sink_id:
            expected_graph_edges.add((source, sink_id, "AUTHORITY_EFFECT"))

    missing_edges = sorted(expected_graph_edges - edge_keys)
    for source, sink_id, edge_type in missing_edges:
        problems.append(f"GRAPH_MATERIAL_EDGE_MISSING:{source}:{sink_id}:{edge_type}")

    if not isinstance(projection, Mapping):
        problems.append("INDEPENDENT_UNIVERSE_PROJECTION_REQUIRED")
        projection_path_ids: set[str] = set()
        projection_sink_ids: set[str] = set()
        projection_plane_ids: set[str] = set()
    else:
        if projection.get("source_kind") == "CANDIDATE_SELF_DERIVED":
            problems.append("INDEPENDENT_PROJECTION_SELF_DERIVED")
        projection_path_ids = _string_set(projection.get("material_path_ids")) or set()
        projection_sink_ids = _string_set(projection.get("sink_ids")) or set()
        projection_plane_ids = _string_set(projection.get("control_plane_ids")) or set()
        if not projection.get("derivation_authority_id"):
            problems.append("INDEPENDENT_PROJECTION_AUTHORITY_REQUIRED")
        if not projection.get("source_evidence_digest"):
            problems.append("INDEPENDENT_PROJECTION_EVIDENCE_DIGEST_REQUIRED")

    # Independent projection can be broader than the runtime-observed set; any
    # projected material member missing from the candidate bundle blocks.
    for path_id in sorted(projection_path_ids - set(path_by_id)):
        problems.append(f"PROJECTED_MATERIAL_PATH_UNRESOLVED:{path_id}")
    for sink_id in sorted(projection_sink_ids - set(sink_by_id)):
        problems.append(f"PROJECTED_SINK_UNRESOLVED:{sink_id}")
    for plane_id in sorted(projection_plane_ids - set(plane_by_id)):
        problems.append(f"PROJECTED_CONTROL_PLANE_UNRESOLVED:{plane_id}")
    for path_id in sorted(observed_material_paths - projection_path_ids):
        problems.append(f"OBSERVED_PATH_ABSENT_FROM_INDEPENDENT_PROJECTION:{path_id}")

    # Any omission-sensitive structure must be explicitly declared as a
    # completeness-required subject.
    required_subject_kinds = {
        "AUTHORITY_SINK_REGISTRY",
        "CONSEQUENTIAL_EFFECTOR_REGISTRY",
        "AUTHORITY_DEPENDENCY_GRAPH",
        "AUTHORITY_EFFECT_PATH_SET",
        "CONTROL_PLANE_SET",
    }
    present_subject_kinds = {
        s.get("subject_kind") for s in subject_by_id.values() if isinstance(s.get("subject_kind"), str)
    }
    for kind in sorted(required_subject_kinds - present_subject_kinds):
        problems.append(f"COMPLETENESS_REQUIRED_SUBJECT_MISSING:{kind}")

    problems = sorted(set(problems))
    return {
        "state": "AUTHORITY_UNIVERSE_CONSTRUCTION_VALID" if not problems else "AUTHORITY_UNIVERSE_INCOMPLETE",
        "qualified": False,
        "problems": problems,
        "counts": {
            "sinks": len(sink_by_id),
            "effectors": len(effector_by_id),
            "paths": len(path_by_id),
            "control_planes": len(plane_by_id),
            "graph_edges": len(edge_keys),
            "completeness_subjects": len(subject_by_id),
        },
        "bundle_digest": canonical_digest(bundle),
        "authority_effect": AUTHORITY_EFFECT,
    }
