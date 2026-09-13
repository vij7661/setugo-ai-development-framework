"""V24 I11 V6 remediation R5: independent normative clause projection/disposition.

Structural enumeration is deliberately semantic-blind: every Markdown heading and
non-empty body block becomes a candidate. Independent governed disposition decides
whether a candidate is normative. Existing catalog descriptors are never used as the
candidate-enumeration source.
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping

from normative_control_catalog import git_blob_sha_bytes
from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT, CURRENT, QUALIFIED, INSUFFICIENT_EVIDENCE, digest,
    validate_governed_qualification,
)

MATERIAL_NORMATIVE = "MATERIAL_NORMATIVE"
REFERENCE_ONLY = "REFERENCE_ONLY"
SUPERSEDED = "SUPERSEDED"
PROVEN_NON_NORMATIVE = "PROVEN_NON_NORMATIVE"
DISPOSITIONS = frozenset({MATERIAL_NORMATIVE, REFERENCE_ONLY, SUPERSEDED, PROVEN_NON_NORMATIVE, INSUFFICIENT_EVIDENCE})
NORMATIVE_CONTROL_CATALOG_INCOMPLETE = "NORMATIVE_CONTROL_CATALOG_INCOMPLETE"


def _sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _parser_subject_digest(parser: Mapping[str, Any]) -> str:
    return digest({
        "parser_profile_id": parser.get("parser_profile_id"),
        "implementation_content_digest": parser.get("implementation_content_digest"),
        "rule_digest": parser.get("rule_digest"),
    })


def _authority_set_subject_digest(authority_set: Mapping[str, Any]) -> str:
    members = sorted(authority_set.get("member_ids", [])) if isinstance(authority_set.get("member_ids"), list) else []
    domains = sorted(authority_set.get("member_control_domain_ids", [])) if isinstance(authority_set.get("member_control_domain_ids"), list) else []
    return digest({
        "authority_set_id": authority_set.get("authority_set_id"),
        "threshold": authority_set.get("threshold"),
        "member_ids": members,
        "member_control_domain_ids": domains,
    })


def _validate_bound_qualification(
    *, subject_id: str, subject_digest: str, qualification_digest: Any, qualification_record: Any, prefix: str
) -> list[str]:
    p: list[str] = []
    if not _sha(qualification_digest):
        p.append(f"{prefix}_QUALIFICATION_DIGEST_INVALID")
    if not isinstance(qualification_record, Mapping):
        p.append(f"{prefix}_QUALIFICATION_RECORD_REQUIRED")
        return p
    for problem in validate_governed_qualification(qualification_record):
        p.append(f"{prefix}_QUALIFICATION:{problem}")
    if qualification_record.get("result") != QUALIFIED:
        p.append(f"{prefix}_QUALIFICATION_NOT_QUALIFIED")
    if qualification_record.get("subject_object_id") != subject_id:
        p.append(f"{prefix}_QUALIFICATION_SUBJECT_ID_MISMATCH")
    if qualification_record.get("subject_content_digest") != subject_digest:
        p.append(f"{prefix}_QUALIFICATION_SUBJECT_DIGEST_MISMATCH")
    if qualification_record.get("qualification_digest") != qualification_digest:
        p.append(f"{prefix}_QUALIFICATION_RECORD_DIGEST_MISMATCH")
    return p


def enumerate_markdown_structural_candidates(
    *,
    artifact_bytes: bytes,
    artifact_path: str,
    parser_profile_id: str,
) -> dict[str, Any]:
    """Enumerate structural candidates from bytes only, independent of descriptors.

    Candidates are heading lines and contiguous non-empty non-heading body blocks.
    Exact line spans and block digests make insertions/deletions/change fail closed.
    """
    problems: list[str] = []
    try:
        text = artifact_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "state": "NORMATIVE_STRUCTURAL_PROJECTION_INVALID",
            "qualified": False,
            "problems": ["NORMATIVE_ARTIFACT_NOT_UTF8"],
            "candidates": [],
            "authority_effect": AUTHORITY_EFFECT,
        }
    if not _nonempty(artifact_path):
        problems.append("NORMATIVE_ARTIFACT_PATH_REQUIRED")
    if not _nonempty(parser_profile_id):
        problems.append("NORMATIVE_PARSER_PROFILE_REQUIRED")

    normalized = _normalize_lf(text)
    artifact_sha256 = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    artifact_git_blob = git_blob_sha_bytes(artifact_bytes)
    lines = normalized.splitlines()
    candidates: list[dict[str, Any]] = []

    def add(kind: str, start: int, end: int, block_lines: list[str], heading_path: list[str]) -> None:
        exact_text = "\n".join(block_lines) + "\n"
        block_digest = hashlib.sha256(exact_text.encode("utf-8")).hexdigest()
        identity = {
            "artifact_path": artifact_path,
            "artifact_sha256": artifact_sha256,
            "parser_profile_id": parser_profile_id,
            "kind": kind,
            "start_line": start,
            "end_line": end,
            "exact_text_sha256": block_digest,
            "heading_path": heading_path,
        }
        candidates.append({
            "candidate_clause_id": digest(identity),
            **identity,
            "exact_text": exact_text,
        })

    heading_stack: list[tuple[int, str]] = []
    body_start: int | None = None
    body_lines: list[str] = []
    body_heading_path: list[str] = []

    def flush_body(end_line: int) -> None:
        nonlocal body_start, body_lines, body_heading_path
        if body_start is not None and body_lines:
            add("BODY_BLOCK", body_start, end_line, body_lines, body_heading_path)
        body_start = None
        body_lines = []
        body_heading_path = []

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        is_heading = False
        level = 0
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            is_heading = 1 <= level <= 6 and len(stripped) > level and stripped[level] == " "
        if is_heading:
            flush_body(idx - 1)
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, stripped))
            add("HEADING", idx, idx, [line], [h for _, h in heading_stack[:-1]])
        elif stripped == "":
            flush_body(idx - 1)
        else:
            if body_start is None:
                body_start = idx
                body_heading_path = [h for _, h in heading_stack]
            body_lines.append(line)
    flush_body(len(lines))

    if not candidates:
        problems.append("NORMATIVE_STRUCTURAL_CANDIDATES_EMPTY")
    candidate_ids = [c["candidate_clause_id"] for c in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        problems.append("NORMATIVE_STRUCTURAL_CANDIDATE_ID_COLLISION")

    projection_material = {
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "artifact_git_blob_sha1": artifact_git_blob,
        "parser_profile_id": parser_profile_id,
        "candidate_id_order": candidate_ids,
        "candidate_structural_digests": [c["exact_text_sha256"] for c in candidates],
    }
    return {
        "state": "NORMATIVE_STRUCTURAL_PROJECTION_READY" if not problems else "NORMATIVE_STRUCTURAL_PROJECTION_INVALID",
        "qualified": not problems,
        "problems": sorted(set(problems)),
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "artifact_git_blob_sha1": artifact_git_blob,
        "parser_profile_id": parser_profile_id,
        "candidates": candidates,
        "candidate_set_digest": digest(sorted(candidate_ids)),
        "projection_digest": digest(projection_material),
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_structural_projection(bundle: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    projection = bundle.get("projection")
    parser = bundle.get("parser_descriptor")
    if not isinstance(projection, Mapping) or projection.get("qualified") is not True:
        p.append("NORMATIVE_STRUCTURAL_PROJECTION_REQUIRED")
        projection = {}
    if not isinstance(parser, Mapping):
        p.append("NORMATIVE_PARSER_DESCRIPTOR_REQUIRED")
        parser = {}
    if parser.get("qualification_state") != QUALIFIED:
        p.append("NORMATIVE_PARSER_NOT_QUALIFIED")
    if parser.get("independence_state") != QUALIFIED:
        p.append("NORMATIVE_PARSER_NOT_INDEPENDENT")
    if parser.get("currentness_result") != CURRENT:
        p.append("NORMATIVE_PARSER_NOT_CURRENT")
    if not _sha(parser.get("implementation_content_digest")):
        p.append("NORMATIVE_PARSER_IMPLEMENTATION_DIGEST_INVALID")
    if not _sha(parser.get("rule_digest")):
        p.append("NORMATIVE_PARSER_RULE_DIGEST_INVALID")
    parser_subject_digest = _parser_subject_digest(parser)
    p.extend(_validate_bound_qualification(
        subject_id=str(parser.get("parser_profile_id") or ""),
        subject_digest=parser_subject_digest,
        qualification_digest=parser.get("qualification_digest"),
        qualification_record=parser.get("qualification_record"),
        prefix="NORMATIVE_PARSER",
    ))
    if projection.get("parser_profile_id") != parser.get("parser_profile_id"):
        p.append("NORMATIVE_PARSER_PROFILE_BINDING_MISMATCH")
    expected_artifact_sha = bundle.get("expected_artifact_sha256")
    expected_blob = bundle.get("expected_artifact_git_blob_sha1")
    if projection.get("artifact_sha256") != expected_artifact_sha:
        p.append("NORMATIVE_ARTIFACT_SHA256_BINDING_MISMATCH")
    if projection.get("artifact_git_blob_sha1") != expected_blob:
        p.append("NORMATIVE_ARTIFACT_GIT_BLOB_BINDING_MISMATCH")
    return sorted(set(p))


def qualify_normative_dispositions(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Require one governed independent disposition for every structural candidate."""
    p = validate_structural_projection(bundle)
    projection = bundle.get("projection") if isinstance(bundle.get("projection"), Mapping) else {}
    candidates = projection.get("candidates") if isinstance(projection.get("candidates"), list) else []
    candidate_by_id = {c.get("candidate_clause_id"): c for c in candidates if isinstance(c, Mapping) and _nonempty(c.get("candidate_clause_id"))}

    authority_set = bundle.get("disposition_authority_set")
    if not isinstance(authority_set, Mapping):
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_SET_REQUIRED")
        authority_set = {}
    if authority_set.get("qualification_state") != QUALIFIED:
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_SET_NOT_QUALIFIED")
    if authority_set.get("currentness_result") != CURRENT:
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_SET_NOT_CURRENT")
    if authority_set.get("independence_state") != QUALIFIED:
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_SET_NOT_INDEPENDENT")
    authority_set_id = authority_set.get("authority_set_id")
    if not _nonempty(authority_set_id):
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_SET_ID_REQUIRED")
    authority_subject_digest = _authority_set_subject_digest(authority_set)
    p.extend(_validate_bound_qualification(
        subject_id=str(authority_set_id or ""),
        subject_digest=authority_subject_digest,
        qualification_digest=authority_set.get("qualification_digest"),
        qualification_record=authority_set.get("qualification_record"),
        prefix="NORMATIVE_DISPOSITION_AUTHORITY_SET",
    ))
    threshold = authority_set.get("threshold")
    members = authority_set.get("member_ids")
    domains = authority_set.get("member_control_domain_ids")
    if not isinstance(threshold, int) or threshold < 1:
        p.append("NORMATIVE_DISPOSITION_THRESHOLD_INVALID")
        threshold = 10**9
    if not isinstance(members, list) or len(set(members)) < threshold:
        p.append("NORMATIVE_DISPOSITION_THRESHOLD_MEMBERS_INSUFFICIENT")
    if not isinstance(domains, list) or len(set(domains)) < threshold:
        p.append("NORMATIVE_DISPOSITION_THRESHOLD_DOMAINS_INSUFFICIENT")
    artifact_owner_domain = bundle.get("artifact_owner_control_domain_id")
    catalog_owner_domain = bundle.get("catalog_owner_control_domain_id")
    if isinstance(domains, list) and any(d in {artifact_owner_domain, catalog_owner_domain} for d in domains):
        p.append("NORMATIVE_DISPOSITION_OWNER_CONTROL_DOMAIN_CONFLICT")

    dispositions = bundle.get("dispositions")
    if not isinstance(dispositions, list):
        dispositions = []
        p.append("NORMATIVE_DISPOSITIONS_REQUIRED")
    by_candidate: dict[str, Mapping[str, Any]] = {}
    for record in dispositions:
        if not isinstance(record, Mapping):
            p.append("NORMATIVE_DISPOSITION_RECORD_MALFORMED")
            continue
        cid = record.get("candidate_clause_id")
        if cid not in candidate_by_id:
            p.append(f"NORMATIVE_DISPOSITION_UNKNOWN_CANDIDATE:{cid}")
            continue
        if cid in by_candidate:
            p.append(f"NORMATIVE_DISPOSITION_DUPLICATE:{cid}")
            continue
        by_candidate[cid] = record
        candidate = candidate_by_id[cid]
        if record.get("artifact_sha256") != projection.get("artifact_sha256"):
            p.append(f"NORMATIVE_DISPOSITION_ARTIFACT_BINDING_MISMATCH:{cid}")
        if record.get("candidate_span_digest") != candidate.get("exact_text_sha256"):
            p.append(f"NORMATIVE_DISPOSITION_SPAN_BINDING_MISMATCH:{cid}")
        if record.get("disposition") not in DISPOSITIONS:
            p.append(f"NORMATIVE_DISPOSITION_VALUE_INVALID:{cid}")
        if record.get("authority_set_qualification_digest") != authority_set.get("qualification_digest"):
            p.append(f"NORMATIVE_DISPOSITION_AUTHORITY_BINDING_MISMATCH:{cid}")
        approvers = record.get("approver_ids")
        approver_domains = record.get("approver_control_domain_ids")
        if not isinstance(approvers, list) or len(set(approvers)) < threshold:
            p.append(f"NORMATIVE_DISPOSITION_THRESHOLD_NOT_MET:{cid}")
        if not isinstance(approver_domains, list) or len(set(approver_domains)) < threshold:
            p.append(f"NORMATIVE_DISPOSITION_DOMAIN_THRESHOLD_NOT_MET:{cid}")
        if record.get("currentness_result") != CURRENT:
            p.append(f"NORMATIVE_DISPOSITION_NOT_CURRENT:{cid}")
        evidence = record.get("evidence_digests")
        if not isinstance(evidence, list) or not evidence or not all(_sha(x) for x in evidence):
            p.append(f"NORMATIVE_DISPOSITION_EVIDENCE_REQUIRED:{cid}")
        if record.get("disposition") == INSUFFICIENT_EVIDENCE:
            p.append(f"NORMATIVE_DISPOSITION_INSUFFICIENT_EVIDENCE:{cid}")
        if record.get("disposition") == SUPERSEDED and not _nonempty(record.get("successor_control_id")):
            p.append(f"NORMATIVE_DISPOSITION_SUPERSEDED_SUCCESSOR_REQUIRED:{cid}")

    for cid in sorted(set(candidate_by_id) - set(by_candidate)):
        p.append(f"NORMATIVE_DISPOSITION_MISSING:{cid}")

    material_ids = sorted(cid for cid, r in by_candidate.items() if r.get("disposition") == MATERIAL_NORMATIVE)
    disposition_digest = digest(sorted((cid, by_candidate[cid].get("disposition"), by_candidate[cid].get("candidate_span_digest")) for cid in by_candidate))
    p = sorted(set(p))
    return {
        "state": "NORMATIVE_DISPOSITIONS_QUALIFIED" if not p else "NORMATIVE_DISPOSITIONS_INCOMPLETE",
        "qualified": not p,
        "problems": p,
        "candidate_ids": sorted(candidate_by_id),
        "material_candidate_ids": material_ids,
        "candidate_set_digest": projection.get("candidate_set_digest"),
        "disposition_digest": disposition_digest,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_catalog_candidate_coverage(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Require every material candidate to have exactly one exact-bound descriptor."""
    p: list[str] = []
    if bundle.get("disposition_qualification_state") != QUALIFIED:
        p.append("NORMATIVE_DISPOSITION_QUALIFICATION_REQUIRED")
    material_ids = set(bundle.get("material_candidate_ids", [])) if isinstance(bundle.get("material_candidate_ids"), list) else set()
    descriptors = bundle.get("catalog_descriptors")
    if not isinstance(descriptors, list):
        descriptors = []
        p.append("NORMATIVE_CATALOG_DESCRIPTORS_REQUIRED")
    artifact_sha = bundle.get("artifact_sha256")
    artifact_blob = bundle.get("artifact_git_blob_sha1")
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for d in descriptors:
        if not isinstance(d, Mapping):
            p.append("NORMATIVE_CATALOG_DESCRIPTOR_MALFORMED")
            continue
        cid = d.get("candidate_clause_id")
        if not _nonempty(cid):
            p.append(f"NORMATIVE_CATALOG_CANDIDATE_BINDING_REQUIRED:{d.get('control_id')}")
            continue
        by_candidate.setdefault(cid, []).append(d)
        if d.get("artifact_sha256") != artifact_sha:
            p.append(f"NORMATIVE_CATALOG_ARTIFACT_SHA_BINDING_MISMATCH:{d.get('control_id')}")
        if d.get("normative_artifact_blob_sha") != artifact_blob:
            p.append(f"NORMATIVE_CATALOG_ARTIFACT_BLOB_BINDING_MISMATCH:{d.get('control_id')}")
        if not _sha(d.get("candidate_span_digest")):
            p.append(f"NORMATIVE_CATALOG_SPAN_DIGEST_INVALID:{d.get('control_id')}")

    for cid in sorted(material_ids):
        mapped = by_candidate.get(cid, [])
        if not mapped:
            p.append(f"NORMATIVE_MATERIAL_CANDIDATE_UNMAPPED:{cid}")
        elif len(mapped) > 1:
            p.append(f"NORMATIVE_MATERIAL_CANDIDATE_MULTI_MAPPED:{cid}")
    for cid in sorted(set(by_candidate) - material_ids):
        p.append(f"NORMATIVE_DESCRIPTOR_TARGETS_NON_MATERIAL_CANDIDATE:{cid}")

    p = sorted(set(p))
    return {
        "state": "NORMATIVE_CANDIDATE_CATALOG_COVERAGE_QUALIFIED" if not p else NORMATIVE_CONTROL_CATALOG_INCOMPLETE,
        "qualified": not p,
        "problems": p,
        "material_candidate_ids": sorted(material_ids),
        "descriptor_candidate_ids": sorted(by_candidate),
        "coverage_digest": digest({"material_candidate_ids": sorted(material_ids), "descriptor_candidate_ids": sorted(by_candidate), "artifact_sha256": artifact_sha, "artifact_git_blob_sha1": artifact_blob}),
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {"state": "V24_V6_R5_NORMATIVE_CLAUSE_PROJECTION_CONSTRUCTION_READY", "qualified": False, "implementation_workstream": "R5", "authority_effect": AUTHORITY_EFFECT}
