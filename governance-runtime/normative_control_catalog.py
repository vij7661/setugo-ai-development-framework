from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_ARTIFACT_CLASSES = {
    "AUTHORITATIVE_DESCRIPTOR_REQUIRED",
    "NONAUTHORITATIVE_REFERENCE",
}
ALLOWED_LEGACY_STATUSES = {
    "ACTIVE_MAPPED",
    "SUPERSEDED",
    "REFERENCE_ONLY",
}
REQUIRED_DESCRIPTOR_FIELDS = (
    "control_id",
    "normative_artifact_path",
    "normative_artifact_blob_sha",
    "clause_locator",
    "clause_sha256",
    "inherited_predecessor_control_ids",
    "authority_bearing_predicate_ids",
    "phase_severity_endpoint_mappings",
    "applicability_rules",
    "required_proof_fields",
    "protected_mutation_strength_class",
    "effective_generation",
    "effective_sequence",
)


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def git_blob_sha_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _safe_repo_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or any(part in {"", "."} for part in p.parts):
        return None
    return p.as_posix()


def _read_artifact(repo_root: Path, repo_path: str) -> bytes:
    path = (repo_root / repo_path).resolve()
    root = repo_root.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact path escapes repository root") from exc
    return path.read_bytes()


def _extract_clause(text: str, heading: str) -> str | None:
    """Extract one Markdown section by exact heading through the next same/higher-level heading."""
    if not isinstance(heading, str) or not heading.startswith("#"):
        return None
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == heading]
    if len(hits) != 1:
        return None
    start = hits[0]
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i].lstrip()
        if not stripped.startswith("#"):
            continue
        prefix = len(stripped) - len(stripped.lstrip("#"))
        if prefix <= level and len(stripped) > prefix and stripped[prefix] == " ":
            end = i
            break
    return "".join(lines[start:end]).rstrip("\r\n") + "\n"


def validate_normative_catalog(
    *,
    repo_root: str | Path,
    artifact_manifest: Mapping[str, Any],
    control_catalog: Mapping[str, Any],
    legacy_qualification: Mapping[str, Any],
) -> dict[str, Any]:
    """Fail-closed validator for the V24 normative-control foundation.

    The function validates exact artifact bytes/blob identities, explicit closed-world
    clause inventories, machine-readable descriptors, and legacy lineage mappings.
    It does not grant governance authority or activate a governance generation.
    """
    problems: list[str] = []
    repo_root = Path(repo_root)

    if artifact_manifest.get("schema_version") != 1:
        problems.append("MANIFEST_SCHEMA_INVALID")
    if control_catalog.get("schema_version") != 1:
        problems.append("CATALOG_SCHEMA_INVALID")
    if legacy_qualification.get("schema_version") != 1:
        problems.append("LEGACY_SCHEMA_INVALID")

    generation = artifact_manifest.get("governance_generation")
    if not isinstance(generation, str) or not generation:
        problems.append("GENERATION_MISSING")

    artifacts = artifact_manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        problems.append("MANIFEST_ARTIFACTS_MISSING")
        artifacts = []

    manifest_by_path: dict[str, dict[str, Any]] = {}
    locator_inventory: dict[tuple[str, str], dict[str, Any]] = {}
    artifact_text: dict[str, str] = {}

    for item in artifacts:
        if not isinstance(item, Mapping):
            problems.append("MANIFEST_ARTIFACT_MALFORMED")
            continue
        path = _safe_repo_path(item.get("path"))
        if path is None:
            problems.append("MANIFEST_ARTIFACT_PATH_INVALID")
            continue
        if path in manifest_by_path:
            problems.append(f"MANIFEST_DUPLICATE_ARTIFACT:{path}")
            continue
        classification = item.get("classification")
        if classification not in ALLOWED_ARTIFACT_CLASSES:
            problems.append(f"MANIFEST_CLASSIFICATION_INVALID:{path}")
        blob_sha = item.get("blob_sha")
        if not isinstance(blob_sha, str) or not HEX40.fullmatch(blob_sha):
            problems.append(f"MANIFEST_BLOB_SHA_INVALID:{path}")
        try:
            data = _read_artifact(repo_root, path)
        except Exception:
            problems.append(f"MANIFEST_ARTIFACT_MISSING:{path}")
            data = b""
        if data:
            actual_blob = git_blob_sha_bytes(data)
            if blob_sha != actual_blob:
                problems.append(f"MANIFEST_BLOB_MISMATCH:{path}")
            try:
                artifact_text[path] = data.decode("utf-8")
            except UnicodeDecodeError:
                problems.append(f"MANIFEST_ARTIFACT_NOT_UTF8:{path}")

        locators = item.get("required_clause_locators", [])
        if classification == "AUTHORITATIVE_DESCRIPTOR_REQUIRED":
            if not isinstance(locators, list) or not locators:
                problems.append(f"AUTHORITATIVE_ARTIFACT_WITHOUT_LOCATORS:{path}")
                locators = []
        elif classification == "NONAUTHORITATIVE_REFERENCE":
            if locators not in ([], None):
                problems.append(f"REFERENCE_ARTIFACT_HAS_NORMATIVE_LOCATORS:{path}")
            locators = []

        for locator in locators:
            if not isinstance(locator, Mapping):
                problems.append(f"LOCATOR_MALFORMED:{path}")
                continue
            locator_id = locator.get("locator_id")
            heading = locator.get("heading")
            clause_sha256 = locator.get("clause_sha256")
            if not isinstance(locator_id, str) or not locator_id:
                problems.append(f"LOCATOR_ID_INVALID:{path}")
                continue
            key = (path, locator_id)
            if key in locator_inventory:
                problems.append(f"LOCATOR_DUPLICATE:{path}:{locator_id}")
                continue
            if not isinstance(heading, str) or not heading.startswith("#"):
                problems.append(f"LOCATOR_HEADING_INVALID:{path}:{locator_id}")
            if not isinstance(clause_sha256, str) or not SHA256.fullmatch(clause_sha256):
                problems.append(f"LOCATOR_CLAUSE_SHA_INVALID:{path}:{locator_id}")
            text = artifact_text.get(path)
            if text is not None and isinstance(heading, str):
                clause = _extract_clause(text, heading)
                if clause is None:
                    problems.append(f"LOCATOR_NOT_UNIQUE_OR_MISSING:{path}:{locator_id}")
                else:
                    actual_clause_sha = hashlib.sha256(clause.encode("utf-8")).hexdigest()
                    if clause_sha256 != actual_clause_sha:
                        problems.append(f"LOCATOR_CLAUSE_SHA_MISMATCH:{path}:{locator_id}")
            locator_inventory[key] = dict(locator)

        manifest_by_path[path] = dict(item)

    descriptors = control_catalog.get("descriptors")
    if not isinstance(descriptors, list):
        problems.append("CATALOG_DESCRIPTORS_MISSING")
        descriptors = []

    descriptor_by_id: dict[str, dict[str, Any]] = {}
    descriptor_by_locator: dict[tuple[str, str], list[str]] = {}

    if control_catalog.get("governance_generation") != generation:
        problems.append("CATALOG_GENERATION_MISMATCH")

    for descriptor in descriptors:
        if not isinstance(descriptor, Mapping):
            problems.append("DESCRIPTOR_MALFORMED")
            continue
        missing = [field for field in REQUIRED_DESCRIPTOR_FIELDS if field not in descriptor]
        if missing:
            problems.append("DESCRIPTOR_FIELDS_MISSING:" + ",".join(missing))
            continue

        control_id = descriptor.get("control_id")
        if not isinstance(control_id, str) or not control_id:
            problems.append("DESCRIPTOR_CONTROL_ID_INVALID")
            continue
        if control_id in descriptor_by_id:
            problems.append(f"DESCRIPTOR_CONTROL_ID_DUPLICATE:{control_id}")
            continue

        path = _safe_repo_path(descriptor.get("normative_artifact_path"))
        if path is None or path not in manifest_by_path:
            problems.append(f"DESCRIPTOR_ARTIFACT_NOT_IN_MANIFEST:{control_id}")
        else:
            if manifest_by_path[path].get("classification") != "AUTHORITATIVE_DESCRIPTOR_REQUIRED":
                problems.append(f"DESCRIPTOR_TARGETS_NONAUTHORITATIVE_ARTIFACT:{control_id}")
            if descriptor.get("normative_artifact_blob_sha") != manifest_by_path[path].get("blob_sha"):
                problems.append(f"DESCRIPTOR_BLOB_BINDING_MISMATCH:{control_id}")

        locator = descriptor.get("clause_locator")
        if not isinstance(locator, Mapping):
            problems.append(f"DESCRIPTOR_LOCATOR_INVALID:{control_id}")
            locator_id = None
        else:
            locator_id = locator.get("locator_id")
            heading = locator.get("heading")
            key = (path, locator_id) if path and isinstance(locator_id, str) else None
            if key is None or key not in locator_inventory:
                problems.append(f"DESCRIPTOR_LOCATOR_NOT_DECLARED:{control_id}")
            else:
                declared = locator_inventory[key]
                if heading != declared.get("heading"):
                    problems.append(f"DESCRIPTOR_LOCATOR_HEADING_MISMATCH:{control_id}")
                if descriptor.get("clause_sha256") != declared.get("clause_sha256"):
                    problems.append(f"DESCRIPTOR_CLAUSE_SHA_MISMATCH:{control_id}")
                descriptor_by_locator.setdefault(key, []).append(control_id)

        predecessors = descriptor.get("inherited_predecessor_control_ids")
        if not isinstance(predecessors, list) or not all(isinstance(x, str) and x for x in predecessors):
            problems.append(f"DESCRIPTOR_PREDECESSOR_IDS_INVALID:{control_id}")
        predicate_ids = descriptor.get("authority_bearing_predicate_ids")
        if not isinstance(predicate_ids, list) or not all(isinstance(x, str) and x for x in predicate_ids):
            problems.append(f"DESCRIPTOR_PREDICATE_IDS_INVALID:{control_id}")
        mappings = descriptor.get("phase_severity_endpoint_mappings")
        if not isinstance(mappings, list):
            problems.append(f"DESCRIPTOR_ENDPOINT_MAPPINGS_INVALID:{control_id}")
        applicability = descriptor.get("applicability_rules")
        if not isinstance(applicability, list):
            problems.append(f"DESCRIPTOR_APPLICABILITY_INVALID:{control_id}")
        proof = descriptor.get("required_proof_fields")
        if not isinstance(proof, list) or not all(isinstance(x, str) and x for x in proof):
            problems.append(f"DESCRIPTOR_PROOF_FIELDS_INVALID:{control_id}")
        strength = descriptor.get("protected_mutation_strength_class")
        if not isinstance(strength, str) or not strength:
            problems.append(f"DESCRIPTOR_STRENGTH_CLASS_INVALID:{control_id}")
        if descriptor.get("effective_generation") != generation:
            problems.append(f"DESCRIPTOR_GENERATION_MISMATCH:{control_id}")
        sequence = descriptor.get("effective_sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            problems.append(f"DESCRIPTOR_SEQUENCE_INVALID:{control_id}")

        descriptor_by_id[control_id] = dict(descriptor)

    for key in locator_inventory:
        mapped = descriptor_by_locator.get(key, [])
        if len(mapped) == 0:
            problems.append(f"CATALOG_REQUIRED_LOCATOR_UNMAPPED:{key[0]}:{key[1]}")
        elif len(mapped) > 1:
            problems.append(f"CATALOG_REQUIRED_LOCATOR_MULTI_MAPPED:{key[0]}:{key[1]}")

    inventory = legacy_qualification.get("legacy_clause_inventory")
    records = legacy_qualification.get("records")
    if not isinstance(inventory, list):
        problems.append("LEGACY_CLAUSE_INVENTORY_MISSING")
        inventory = []
    if not isinstance(records, list):
        problems.append("LEGACY_RECORDS_MISSING")
        records = []
    if legacy_qualification.get("governance_generation") != generation:
        problems.append("LEGACY_GENERATION_MISMATCH")

    legacy_required: dict[tuple[str, str], dict[str, Any]] = {}
    for item in inventory:
        if not isinstance(item, Mapping):
            problems.append("LEGACY_INVENTORY_ITEM_MALFORMED")
            continue
        path = _safe_repo_path(item.get("artifact_path"))
        locator_id = item.get("locator_id")
        if path is None or not isinstance(locator_id, str) or not locator_id:
            problems.append("LEGACY_INVENTORY_IDENTITY_INVALID")
            continue
        key = (path, locator_id)
        if key in legacy_required:
            problems.append(f"LEGACY_INVENTORY_DUPLICATE:{path}:{locator_id}")
        legacy_required[key] = dict(item)

    record_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            problems.append("LEGACY_RECORD_MALFORMED")
            continue
        path = _safe_repo_path(record.get("artifact_path"))
        locator_id = record.get("locator_id")
        status = record.get("status")
        if path is None or not isinstance(locator_id, str) or not locator_id:
            problems.append("LEGACY_RECORD_IDENTITY_INVALID")
            continue
        key = (path, locator_id)
        if key in record_by_key:
            problems.append(f"LEGACY_RECORD_DUPLICATE:{path}:{locator_id}")
            continue
        if status not in ALLOWED_LEGACY_STATUSES:
            problems.append(f"LEGACY_STATUS_INVALID:{path}:{locator_id}")
        target = record.get("target_control_id")
        if status == "ACTIVE_MAPPED":
            if not isinstance(target, str) or target not in descriptor_by_id:
                problems.append(f"LEGACY_ACTIVE_TARGET_INVALID:{path}:{locator_id}")
        else:
            if target not in (None, ""):
                problems.append(f"LEGACY_NONACTIVE_TARGET_PRESENT:{path}:{locator_id}")
        record_by_key[key] = dict(record)

    for key in legacy_required:
        if key not in record_by_key:
            problems.append(f"LEGACY_INVENTORY_UNQUALIFIED:{key[0]}:{key[1]}")

    for key in record_by_key:
        if key not in legacy_required:
            problems.append(f"LEGACY_RECORD_NOT_IN_INVENTORY:{key[0]}:{key[1]}")

    result = {
        "state": "NORMATIVE_CONTROL_CATALOG_QUALIFIED" if not problems else "NORMATIVE_CONTROL_CATALOG_INCOMPLETE",
        "qualified": not problems,
        "problems": sorted(set(problems)),
        "governance_generation": generation,
        "artifact_manifest_digest": sha256_json(artifact_manifest),
        "control_catalog_digest": sha256_json(control_catalog),
        "legacy_qualification_digest": sha256_json(legacy_qualification),
        "artifact_count": len(manifest_by_path),
        "descriptor_count": len(descriptor_by_id),
        "legacy_inventory_count": len(legacy_required),
        "legacy_record_count": len(record_by_key),
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    result["qualification_digest"] = sha256_json(result)
    return result
