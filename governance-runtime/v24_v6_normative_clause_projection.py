"""V24 I11 V6 remediation R5: independent normative clause projection/disposition.

Structural enumeration is deliberately semantic-blind: every Markdown heading and
non-empty body block becomes a candidate. Authority-bearing parser, projection,
disposition and coverage claims must resolve exact R1 governance proofs through a
separately trusted proof context. This module remains construction/evidence only.
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping

from normative_control_catalog import git_blob_sha_bytes
from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    INSUFFICIENT_EVIDENCE,
    digest,
)
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    close_governance_dependencies,
)

MATERIAL_NORMATIVE = "MATERIAL_NORMATIVE"
REFERENCE_ONLY = "REFERENCE_ONLY"
SUPERSEDED = "SUPERSEDED"
PROVEN_NON_NORMATIVE = "PROVEN_NON_NORMATIVE"
DISPOSITIONS = frozenset(
    {
        MATERIAL_NORMATIVE,
        REFERENCE_ONLY,
        SUPERSEDED,
        PROVEN_NON_NORMATIVE,
        INSUFFICIENT_EVIDENCE,
    }
)
NORMATIVE_CONTROL_CATALOG_INCOMPLETE = "NORMATIVE_CONTROL_CATALOG_INCOMPLETE"


def _sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _append_proof(prefix: str, result: Mapping[str, Any], problems: list[str]) -> bool:
    if result.get("qualified") is True:
        return True
    child = result.get("problems")
    if isinstance(child, list) and child:
        problems.extend(f"{prefix}:{item}" for item in child)
    else:
        problems.append(f"{prefix}:PROOF_REFERENCE_CLOSURE_FAILED")
    return False


def _close(
    requirements: list[Mapping[str, Any]],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    result = close_governance_dependencies(
        requirements,
        proof_context,
        trusted_boundary,
    )
    return _append_proof(prefix, result, problems)


def enumerate_markdown_structural_candidates(
    *,
    artifact_bytes: bytes,
    artifact_path: str,
    parser_profile_id: str,
) -> dict[str, Any]:
    """Enumerate structural candidates from bytes only, independent of descriptors."""
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

    def add(
        kind: str,
        start: int,
        end: int,
        block_lines: list[str],
        heading_path: list[str],
    ) -> None:
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
        candidates.append(
            {
                "candidate_clause_id": digest(identity),
                **identity,
                "exact_text": exact_text,
            }
        )

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
            is_heading = (
                1 <= level <= 6
                and len(stripped) > level
                and stripped[level] == " "
            )
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
        "candidate_structural_digests": [
            c["exact_text_sha256"] for c in candidates
        ],
    }
    return {
        "state": (
            "NORMATIVE_STRUCTURAL_PROJECTION_READY"
            if not problems
            else "NORMATIVE_STRUCTURAL_PROJECTION_INVALID"
        ),
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


def canonical_parser_content_digest(parser: Mapping[str, Any]) -> str:
    return digest(
        {
            "parser_profile_id": parser.get("parser_profile_id"),
            "implementation_content_digest": parser.get("implementation_content_digest"),
            "rule_digest": parser.get("rule_digest"),
        }
    )


def _candidate_identity(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_path": candidate.get("artifact_path"),
        "artifact_sha256": candidate.get("artifact_sha256"),
        "parser_profile_id": candidate.get("parser_profile_id"),
        "kind": candidate.get("kind"),
        "start_line": candidate.get("start_line"),
        "end_line": candidate.get("end_line"),
        "exact_text_sha256": candidate.get("exact_text_sha256"),
        "heading_path": candidate.get("heading_path"),
    }


def canonical_projection_digest(projection: Mapping[str, Any]) -> str:
    candidates = projection.get("candidates")
    rows = candidates if isinstance(candidates, list) else []
    return digest(
        {
            "artifact_path": projection.get("artifact_path"),
            "artifact_sha256": projection.get("artifact_sha256"),
            "artifact_git_blob_sha1": projection.get("artifact_git_blob_sha1"),
            "parser_profile_id": projection.get("parser_profile_id"),
            "candidate_id_order": [
                c.get("candidate_clause_id") for c in rows if isinstance(c, Mapping)
            ],
            "candidate_structural_digests": [
                c.get("exact_text_sha256") for c in rows if isinstance(c, Mapping)
            ],
        }
    )


def _validate_projection_integrity(projection: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    candidates = projection.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return ["NORMATIVE_STRUCTURAL_CANDIDATES_REQUIRED"]
    ids: list[str] = []
    for idx, c in enumerate(candidates):
        if not isinstance(c, Mapping):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_MALFORMED:{idx}")
            continue
        cid = c.get("candidate_clause_id")
        if not _nonempty(cid):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_ID_REQUIRED:{idx}")
            continue
        ids.append(cid)
        text = c.get("exact_text")
        if not isinstance(text, str):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_TEXT_REQUIRED:{idx}")
        elif hashlib.sha256(text.encode("utf-8")).hexdigest() != c.get(
            "exact_text_sha256"
        ):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_TEXT_DIGEST_MISMATCH:{idx}")
        if digest(_candidate_identity(c)) != cid:
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_ID_MISMATCH:{idx}")
        if c.get("artifact_path") != projection.get("artifact_path"):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_PATH_MISMATCH:{idx}")
        if c.get("artifact_sha256") != projection.get("artifact_sha256"):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_ARTIFACT_MISMATCH:{idx}")
        if c.get("parser_profile_id") != projection.get("parser_profile_id"):
            p.append(f"NORMATIVE_STRUCTURAL_CANDIDATE_PARSER_MISMATCH:{idx}")
    if len(ids) != len(set(ids)):
        p.append("NORMATIVE_STRUCTURAL_CANDIDATE_ID_COLLISION")
    if projection.get("candidate_set_digest") != digest(sorted(ids)):
        p.append("NORMATIVE_STRUCTURAL_CANDIDATE_SET_DIGEST_MISMATCH")
    if projection.get("projection_digest") != canonical_projection_digest(projection):
        p.append("NORMATIVE_STRUCTURAL_PROJECTION_DIGEST_MISMATCH")
    return sorted(set(p))


def validate_structural_projection(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> list[str]:
    p: list[str] = []
    projection = bundle.get("projection")
    parser = bundle.get("parser_descriptor")
    if not isinstance(projection, Mapping) or projection.get("qualified") is not True:
        p.append("NORMATIVE_STRUCTURAL_PROJECTION_REQUIRED")
        projection = {}
    if not isinstance(parser, Mapping):
        p.append("NORMATIVE_PARSER_DESCRIPTOR_REQUIRED")
        parser = {}

    parser_id = parser.get("parser_id")
    parser_content = parser.get("parser_content_digest")
    expected_parser_content = canonical_parser_content_digest(parser)
    for key in (
        "parser_id",
        "parser_profile_id",
        "implementation_content_digest",
        "rule_digest",
        "parser_content_digest",
        "qualification_digest",
        "independence_qualification_digest",
        "currentness_binding_digest",
    ):
        if not _nonempty(parser.get(key)):
            p.append(f"NORMATIVE_PARSER_FIELD_REQUIRED:{key}")
    for key in (
        "implementation_content_digest",
        "rule_digest",
        "parser_content_digest",
        "qualification_digest",
        "independence_qualification_digest",
        "currentness_binding_digest",
    ):
        if not _sha(parser.get(key)):
            p.append(f"NORMATIVE_PARSER_DIGEST_INVALID:{key}")
    if _sha(parser_content) and parser_content != expected_parser_content:
        p.append("NORMATIVE_PARSER_CONTENT_DIGEST_MISMATCH")
    for key, expected, error in (
        ("qualification_state", QUALIFIED, "NORMATIVE_PARSER_NOT_QUALIFIED"),
        ("independence_state", QUALIFIED, "NORMATIVE_PARSER_NOT_INDEPENDENT"),
        ("currentness_result", CURRENT, "NORMATIVE_PARSER_NOT_CURRENT"),
    ):
        value = parser.get(key)
        if value is not None and value != expected:
            p.append(error)
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": parser.get("qualification_digest"),
                "subject_id": parser_id,
                "subject_content_digest": parser_content,
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": parser.get("independence_qualification_digest"),
                "subject_identity_id": parser_id,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": parser.get("currentness_binding_digest"),
                "source_id": parser_id,
                "source_digest": parser_content,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="NORMATIVE_PARSER_PROOF",
        problems=p,
    )

    if projection:
        p.extend(_validate_projection_integrity(projection))
    projection_id = bundle.get("projection_id")
    projection_q = bundle.get("projection_qualification_digest")
    if not _nonempty(projection_id):
        p.append("NORMATIVE_PROJECTION_ID_REQUIRED")
    if not _sha(projection_q):
        p.append("NORMATIVE_PROJECTION_QUALIFICATION_DIGEST_INVALID")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": projection_q,
                "subject_id": projection_id,
                "subject_content_digest": projection.get("projection_digest"),
            }
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="NORMATIVE_PROJECTION_PROOF",
        problems=p,
    )

    if projection.get("parser_profile_id") != parser.get("parser_profile_id"):
        p.append("NORMATIVE_PARSER_PROFILE_BINDING_MISMATCH")
    expected_artifact_sha = bundle.get("expected_artifact_sha256")
    expected_blob = bundle.get("expected_artifact_git_blob_sha1")
    if projection.get("artifact_sha256") != expected_artifact_sha:
        p.append("NORMATIVE_ARTIFACT_SHA256_BINDING_MISMATCH")
    if projection.get("artifact_git_blob_sha1") != expected_blob:
        p.append("NORMATIVE_ARTIFACT_GIT_BLOB_BINDING_MISMATCH")
    return sorted(set(p))


def canonical_authority_set_content_digest(record: Mapping[str, Any]) -> str:
    members = record.get("member_ids")
    domains = record.get("member_control_domain_ids")
    pairs: list[dict[str, Any]] = []
    if isinstance(members, list) and isinstance(domains, list):
        pairs = sorted(
            (
                {"member_id": mid, "control_domain_id": domain}
                for mid, domain in zip(members, domains)
            ),
            key=lambda item: (str(item["member_id"]), str(item["control_domain_id"])),
        )
    return digest(
        {
            "authority_set_id": record.get("authority_set_id"),
            "threshold": record.get("threshold"),
            "member_pairs": pairs,
        }
    )


def _authority_member_pairs(record: Mapping[str, Any]) -> set[tuple[str, str]]:
    members = record.get("member_ids")
    domains = record.get("member_control_domain_ids")
    if not isinstance(members, list) or not isinstance(domains, list):
        return set()
    return {(str(mid), str(domain)) for mid, domain in zip(members, domains)}


def canonical_disposition_content_digest(record: Mapping[str, Any]) -> str:
    approvers = record.get("approver_ids")
    domains = record.get("approver_control_domain_ids")
    approver_pairs: list[dict[str, Any]] = []
    if isinstance(approvers, list) and isinstance(domains, list):
        approver_pairs = sorted(
            (
                {"approver_id": aid, "control_domain_id": domain}
                for aid, domain in zip(approvers, domains)
            ),
            key=lambda item: (str(item["approver_id"]), str(item["control_domain_id"])),
        )
    evidence = record.get("evidence_digests")
    return digest(
        {
            "disposition_record_id": record.get("disposition_record_id"),
            "candidate_clause_id": record.get("candidate_clause_id"),
            "artifact_sha256": record.get("artifact_sha256"),
            "candidate_span_digest": record.get("candidate_span_digest"),
            "authority_set_id": record.get("authority_set_id"),
            "authority_set_qualification_digest": record.get(
                "authority_set_qualification_digest"
            ),
            "approver_pairs": approver_pairs,
            "evidence_digests": sorted(evidence) if isinstance(evidence, list) else [],
            "disposition": record.get("disposition"),
            "successor_control_id": record.get("successor_control_id"),
        }
    )


def qualify_normative_dispositions(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Require one exact proof-closed disposition for every structural candidate."""
    p = validate_structural_projection(
        bundle,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    )
    projection = (
        bundle.get("projection") if isinstance(bundle.get("projection"), Mapping) else {}
    )
    candidates = (
        projection.get("candidates")
        if isinstance(projection.get("candidates"), list)
        else []
    )
    candidate_by_id = {
        c.get("candidate_clause_id"): c
        for c in candidates
        if isinstance(c, Mapping) and _nonempty(c.get("candidate_clause_id"))
    }

    authority_set = bundle.get("disposition_authority_set")
    if not isinstance(authority_set, Mapping):
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_SET_REQUIRED")
        authority_set = {}
    authority_set_id = authority_set.get("authority_set_id")
    authority_content = authority_set.get("authority_set_content_digest")
    expected_authority_content = canonical_authority_set_content_digest(authority_set)
    for key in (
        "authority_set_id",
        "authority_set_content_digest",
        "qualification_digest",
        "independence_qualification_digest",
        "currentness_binding_digest",
    ):
        if not _nonempty(authority_set.get(key)):
            p.append(f"NORMATIVE_DISPOSITION_AUTHORITY_FIELD_REQUIRED:{key}")
    for key in (
        "authority_set_content_digest",
        "qualification_digest",
        "independence_qualification_digest",
        "currentness_binding_digest",
    ):
        if not _sha(authority_set.get(key)):
            p.append(f"NORMATIVE_DISPOSITION_AUTHORITY_DIGEST_INVALID:{key}")
    if _sha(authority_content) and authority_content != expected_authority_content:
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_CONTENT_DIGEST_MISMATCH")
    for key, expected, error in (
        ("qualification_state", QUALIFIED, "NORMATIVE_DISPOSITION_AUTHORITY_SET_NOT_QUALIFIED"),
        ("currentness_result", CURRENT, "NORMATIVE_DISPOSITION_AUTHORITY_SET_NOT_CURRENT"),
        ("independence_state", QUALIFIED, "NORMATIVE_DISPOSITION_AUTHORITY_SET_NOT_INDEPENDENT"),
    ):
        value = authority_set.get(key)
        if value is not None and value != expected:
            p.append(error)
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": authority_set.get("qualification_digest"),
                "subject_id": authority_set_id,
                "subject_content_digest": authority_content,
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": authority_set.get("independence_qualification_digest"),
                "subject_identity_id": authority_set_id,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": authority_set.get("currentness_binding_digest"),
                "source_id": authority_set_id,
                "source_digest": authority_content,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="NORMATIVE_DISPOSITION_AUTHORITY_PROOF",
        problems=p,
    )

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
    if isinstance(members, list) and isinstance(domains, list) and len(members) != len(domains):
        p.append("NORMATIVE_DISPOSITION_AUTHORITY_MEMBER_DOMAIN_CARDINALITY_MISMATCH")
    authority_pairs = _authority_member_pairs(authority_set)
    artifact_owner_domain = bundle.get("artifact_owner_control_domain_id")
    catalog_owner_domain = bundle.get("catalog_owner_control_domain_id")
    if isinstance(domains, list) and any(
        d in {artifact_owner_domain, catalog_owner_domain} for d in domains
    ):
        p.append("NORMATIVE_DISPOSITION_OWNER_CONTROL_DOMAIN_CONFLICT")

    dispositions = bundle.get("dispositions")
    if not isinstance(dispositions, list):
        dispositions = []
        p.append("NORMATIVE_DISPOSITIONS_REQUIRED")
    by_candidate: dict[str, Mapping[str, Any]] = {}
    record_digests: dict[str, str] = {}
    candidate_spans: dict[str, str] = {}
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
        if record.get("authority_set_id") != authority_set_id:
            p.append(f"NORMATIVE_DISPOSITION_AUTHORITY_SET_ID_MISMATCH:{cid}")
        if record.get("authority_set_qualification_digest") != authority_set.get(
            "qualification_digest"
        ):
            p.append(f"NORMATIVE_DISPOSITION_AUTHORITY_BINDING_MISMATCH:{cid}")

        approvers = record.get("approver_ids")
        approver_domains = record.get("approver_control_domain_ids")
        if not isinstance(approvers, list) or len(set(approvers)) < threshold:
            p.append(f"NORMATIVE_DISPOSITION_THRESHOLD_NOT_MET:{cid}")
        if not isinstance(approver_domains, list) or len(set(approver_domains)) < threshold:
            p.append(f"NORMATIVE_DISPOSITION_DOMAIN_THRESHOLD_NOT_MET:{cid}")
        if (
            isinstance(approvers, list)
            and isinstance(approver_domains, list)
            and len(approvers) != len(approver_domains)
        ):
            p.append(f"NORMATIVE_DISPOSITION_APPROVER_DOMAIN_CARDINALITY_MISMATCH:{cid}")
        if isinstance(approvers, list) and isinstance(approver_domains, list):
            submitted_pairs = {
                (str(aid), str(domain))
                for aid, domain in zip(approvers, approver_domains)
            }
            if not submitted_pairs.issubset(authority_pairs):
                p.append(f"NORMATIVE_DISPOSITION_APPROVER_NOT_IN_AUTHORITY_SET:{cid}")

        evidence = record.get("evidence_digests")
        if not isinstance(evidence, list) or not evidence or not all(_sha(x) for x in evidence):
            p.append(f"NORMATIVE_DISPOSITION_EVIDENCE_REQUIRED:{cid}")
        if record.get("disposition") == INSUFFICIENT_EVIDENCE:
            p.append(f"NORMATIVE_DISPOSITION_INSUFFICIENT_EVIDENCE:{cid}")
        if record.get("disposition") == SUPERSEDED and not _nonempty(
            record.get("successor_control_id")
        ):
            p.append(f"NORMATIVE_DISPOSITION_SUPERSEDED_SUCCESSOR_REQUIRED:{cid}")

        record_id = record.get("disposition_record_id")
        content_digest = record.get("disposition_content_digest")
        expected_content = canonical_disposition_content_digest(record)
        for key in (
            "disposition_record_id",
            "disposition_content_digest",
            "disposition_qualification_digest",
            "currentness_binding_digest",
        ):
            if not _nonempty(record.get(key)):
                p.append(f"NORMATIVE_DISPOSITION_PROOF_FIELD_REQUIRED:{cid}:{key}")
        for key in (
            "disposition_content_digest",
            "disposition_qualification_digest",
            "currentness_binding_digest",
        ):
            if not _sha(record.get(key)):
                p.append(f"NORMATIVE_DISPOSITION_PROOF_DIGEST_INVALID:{cid}:{key}")
        if _sha(content_digest) and content_digest != expected_content:
            p.append(f"NORMATIVE_DISPOSITION_CONTENT_DIGEST_MISMATCH:{cid}")
        current_state = record.get("currentness_result")
        if current_state is not None and current_state != CURRENT:
            p.append(f"NORMATIVE_DISPOSITION_NOT_CURRENT:{cid}")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": record.get("disposition_qualification_digest"),
                    "subject_id": record_id,
                    "subject_content_digest": content_digest,
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": record.get("currentness_binding_digest"),
                    "source_id": record_id,
                    "source_digest": content_digest,
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"NORMATIVE_DISPOSITION_PROOF:{cid}",
            problems=p,
        )
        if _sha(content_digest):
            record_digests[cid] = content_digest
        candidate_spans[cid] = candidate.get("exact_text_sha256")

    for cid in sorted(set(candidate_by_id) - set(by_candidate)):
        p.append(f"NORMATIVE_DISPOSITION_MISSING:{cid}")

    material_ids = sorted(
        cid
        for cid, record in by_candidate.items()
        if record.get("disposition") == MATERIAL_NORMATIVE
    )
    disposition_material = {
        "projection_id": bundle.get("projection_id"),
        "projection_digest": projection.get("projection_digest"),
        "projection_qualification_digest": bundle.get(
            "projection_qualification_digest"
        ),
        "artifact_sha256": projection.get("artifact_sha256"),
        "artifact_git_blob_sha1": projection.get("artifact_git_blob_sha1"),
        "candidate_set_digest": projection.get("candidate_set_digest"),
        "candidate_ids": sorted(candidate_by_id),
        "candidate_span_digests": [
            {"candidate_clause_id": cid, "candidate_span_digest": candidate_spans[cid]}
            for cid in sorted(candidate_spans)
        ],
        "authority_set_id": authority_set_id,
        "authority_set_content_digest": authority_content,
        "authority_set_qualification_digest": authority_set.get("qualification_digest"),
        "disposition_record_content_digests": [
            {"candidate_clause_id": cid, "disposition_content_digest": record_digests[cid]}
            for cid in sorted(record_digests)
        ],
        "material_candidate_ids": material_ids,
    }
    disposition_digest = digest(disposition_material)
    p = sorted(set(p))
    return {
        "state": (
            "NORMATIVE_DISPOSITIONS_QUALIFIED"
            if not p
            else "NORMATIVE_DISPOSITIONS_INCOMPLETE"
        ),
        "qualified": not p,
        "problems": p,
        "candidate_ids": sorted(candidate_by_id),
        "material_candidate_ids": material_ids,
        "candidate_set_digest": projection.get("candidate_set_digest"),
        "disposition_digest": disposition_digest,
        "disposition_binding_material": disposition_material,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_catalog_candidate_coverage(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Require exact qualified disposition artifact and one descriptor per material candidate."""
    p: list[str] = []
    disposition_digest = bundle.get("disposition_digest")
    material = bundle.get("disposition_binding_material")
    if not isinstance(material, Mapping):
        p.append("NORMATIVE_DISPOSITION_BINDING_MATERIAL_REQUIRED")
        material = {}
    elif digest(material) != disposition_digest:
        p.append("NORMATIVE_DISPOSITION_BINDING_MATERIAL_DIGEST_MISMATCH")

    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": bundle.get("disposition_qualification_digest"),
                "subject_id": bundle.get("disposition_set_id"),
                "subject_content_digest": disposition_digest,
            }
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="NORMATIVE_DISPOSITION_SET_PROOF",
        problems=p,
    )
    state = bundle.get("disposition_qualification_state")
    if state is not None and state != QUALIFIED:
        p.append("NORMATIVE_DISPOSITION_QUALIFICATION_REQUIRED")

    bound_material_ids = material.get("material_candidate_ids")
    material_ids = set(bound_material_ids) if isinstance(bound_material_ids, list) else set()
    caller_material_ids = bundle.get("material_candidate_ids")
    if caller_material_ids is not None:
        supplied = set(caller_material_ids) if isinstance(caller_material_ids, list) else set()
        if supplied != material_ids:
            p.append("NORMATIVE_MATERIAL_CANDIDATE_SET_BINDING_MISMATCH")

    artifact_sha = material.get("artifact_sha256")
    artifact_blob = material.get("artifact_git_blob_sha1")
    if bundle.get("artifact_sha256") is not None and bundle.get("artifact_sha256") != artifact_sha:
        p.append("NORMATIVE_CATALOG_INPUT_ARTIFACT_SHA_BINDING_MISMATCH")
    if (
        bundle.get("artifact_git_blob_sha1") is not None
        and bundle.get("artifact_git_blob_sha1") != artifact_blob
    ):
        p.append("NORMATIVE_CATALOG_INPUT_ARTIFACT_BLOB_BINDING_MISMATCH")

    span_entries = material.get("candidate_span_digests")
    span_by_candidate: dict[str, Any] = {}
    if isinstance(span_entries, list):
        span_by_candidate = {
            item.get("candidate_clause_id"): item.get("candidate_span_digest")
            for item in span_entries
            if isinstance(item, Mapping) and _nonempty(item.get("candidate_clause_id"))
        }

    descriptors = bundle.get("catalog_descriptors")
    if not isinstance(descriptors, list):
        descriptors = []
        p.append("NORMATIVE_CATALOG_DESCRIPTORS_REQUIRED")
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for descriptor in descriptors:
        if not isinstance(descriptor, Mapping):
            p.append("NORMATIVE_CATALOG_DESCRIPTOR_MALFORMED")
            continue
        cid = descriptor.get("candidate_clause_id")
        if not _nonempty(cid):
            p.append(
                f"NORMATIVE_CATALOG_CANDIDATE_BINDING_REQUIRED:{descriptor.get('control_id')}"
            )
            continue
        by_candidate.setdefault(cid, []).append(descriptor)
        if descriptor.get("artifact_sha256") != artifact_sha:
            p.append(
                f"NORMATIVE_CATALOG_ARTIFACT_SHA_BINDING_MISMATCH:{descriptor.get('control_id')}"
            )
        if descriptor.get("normative_artifact_blob_sha") != artifact_blob:
            p.append(
                f"NORMATIVE_CATALOG_ARTIFACT_BLOB_BINDING_MISMATCH:{descriptor.get('control_id')}"
            )
        if descriptor.get("candidate_span_digest") != span_by_candidate.get(cid):
            p.append(
                f"NORMATIVE_CATALOG_SPAN_BINDING_MISMATCH:{descriptor.get('control_id')}"
            )

    for cid in sorted(material_ids):
        mapped = by_candidate.get(cid, [])
        if not mapped:
            p.append(f"NORMATIVE_MATERIAL_CANDIDATE_UNMAPPED:{cid}")
        elif len(mapped) > 1:
            p.append(f"NORMATIVE_MATERIAL_CANDIDATE_MULTI_MAPPED:{cid}")
    for cid in sorted(set(by_candidate) - material_ids):
        p.append(f"NORMATIVE_DESCRIPTOR_TARGETS_NON_MATERIAL_CANDIDATE:{cid}")

    coverage_material = {
        "disposition_digest": disposition_digest,
        "material_candidate_ids": sorted(material_ids),
        "descriptor_candidate_ids": sorted(by_candidate),
        "catalog_descriptor_digests": sorted(
            digest(d) for d in descriptors if isinstance(d, Mapping)
        ),
        "artifact_sha256": artifact_sha,
        "artifact_git_blob_sha1": artifact_blob,
    }
    p = sorted(set(p))
    return {
        "state": (
            "NORMATIVE_CANDIDATE_CATALOG_COVERAGE_QUALIFIED"
            if not p
            else NORMATIVE_CONTROL_CATALOG_INCOMPLETE
        ),
        "qualified": not p,
        "problems": p,
        "material_candidate_ids": sorted(material_ids),
        "descriptor_candidate_ids": sorted(by_candidate),
        "coverage_digest": digest(coverage_material),
        "coverage_binding_material": coverage_material,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R5_NORMATIVE_PROJECTION_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R5",
        "authority_effect": AUTHORITY_EFFECT,
    }
