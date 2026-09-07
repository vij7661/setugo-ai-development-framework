from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

from .review_execution_classification import ingest_user_provided_external_content


SUPPORTED_REVIEW_TARGETS = frozenset({"provider-neutral", "claude", "deepseek", "kimi"})
EXTERNAL_CONTENT_IDENTITY_ASSURANCE = "UNAUTHENTICATED_EXTERNAL_CONTENT"
RAW_HASH_BASIS = "RAW_FILE_BYTES"
TRANSPORT_PROFILE_CHECKED_DATE = "2026-09-07"

# Convenience-only input profiles. These describe how the same canonical review
# bytes can be presented to different reviewer surfaces. They are never included
# in the raw-artifact authority set and never authenticate the reviewer/model.
TARGET_TRANSPORT_PROFILES = {
    "provider-neutral": {
        "api_family": "UNSPECIFIED",
        "manual_input_shape": "UTF8_TEXT_MARKDOWN_PLUS_RAW_FILES",
        "prompt_layout": "review instruction plus canonical source manifest and raw files",
        "structured_output": "follow REVIEW_PROMPT.txt output contract",
        "documentation_basis": [],
    },
    "claude": {
        "api_family": "ANTHROPIC_MESSAGES",
        "manual_input_shape": "UTF8_TEXT_MARKDOWN_PLUS_RAW_FILES",
        "prompt_layout": "long source/context first, explicit review instruction and output schema; XML delimiters may be used",
        "structured_output": "explicit schema/instructions in prompt or supported structured-output surface",
        "document_input_note": "Claude Messages supports document input including PDF by URL, base64 or file_id; raw text files remain canonical for code review",
        "documentation_basis": [
            "https://docs.anthropic.com/en/docs/build-with-claude/pdf-support",
            "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables",
        ],
    },
    "deepseek": {
        "api_family": "OPENAI_CHAT_COMPLETIONS_OR_RESPONSES",
        "manual_input_shape": "UTF8_TEXT_MARKDOWN_PLUS_RAW_FILES",
        "prompt_layout": "system/user instruction with explicit JSON output contract and canonical source text",
        "structured_output": "Chat Completions response_format=json_object; Responses API supports json_object/json_schema",
        "documentation_basis": [
            "https://api-docs.deepseek.com/api/create-chat-completion/",
            "https://api-docs.deepseek.com/api/create-response/",
        ],
    },
    "kimi": {
        "api_family": "MESSAGES_STYLE_CHAT",
        "manual_input_shape": "UTF8_TEXT_MARKDOWN_PLUS_RAW_FILES",
        "prompt_layout": "system/user messages with clear steps, delimiters/XML and reference text",
        "structured_output": "state the exact output schema in the prompt; this profile makes no stronger JSON-mode claim",
        "documentation_basis": [
            "https://platform.moonshot.ai/docs/guide/prompt-best-practice",
        ],
    },
}


@dataclass(frozen=True)
class ReviewSourceEntry:
    path: str
    sha256: str
    size_bytes: int
    hash_basis: str = RAW_HASH_BASIS


@dataclass(frozen=True)
class ReviewExportSpec:
    review_id: str
    candidate_sha: str
    intended_reviewer: str
    prompt: str
    source_paths: tuple[str, ...]

    def validate(self) -> None:
        if not self.review_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for ch in self.review_id):
            raise ValueError("review_id must be a non-empty safe identifier")
        if len(self.candidate_sha) != 40 or any(ch not in "0123456789abcdef" for ch in self.candidate_sha):
            raise ValueError("candidate_sha must be a lowercase 40-character git commit sha")
        if self.intended_reviewer not in SUPPORTED_REVIEW_TARGETS:
            raise ValueError("unsupported intended reviewer target")
        if not self.prompt.strip():
            raise ValueError("review prompt cannot be empty")
        if not self.source_paths:
            raise ValueError("review export requires at least one source path")
        if len(set(self.source_paths)) != len(self.source_paths):
            raise ValueError("review source paths cannot contain duplicates")


def _safe_source(root: Path, relative: str) -> tuple[Path, str]:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise ValueError(f"unsafe review source path: {relative}")
    normalized = rel.as_posix()
    source = root / rel
    if not source.is_file():
        raise ValueError(f"review source file not found: {relative}")
    resolved_root = root.resolve()
    resolved_source = source.resolve()
    if resolved_source != resolved_root and resolved_root not in resolved_source.parents:
        raise ValueError(f"review source escapes repository root: {relative}")
    return source, normalized


def _render_packet(spec: ReviewExportSpec, entries: tuple[ReviewSourceEntry, ...], source_text: dict[str, str]) -> str:
    target_note = {
        "provider-neutral": "Use this packet with any external reviewer that can consume UTF-8 text/Markdown.",
        "claude": "Claude-targeted input hint only; reviewer identity is not proven by this file.",
        "deepseek": "DeepSeek-targeted input hint only; this Markdown can be supplied as plain text when document upload is unavailable.",
        "kimi": "Kimi-targeted input hint only; reviewer identity is not proven by this file.",
    }[spec.intended_reviewer]
    lines = [
        f"# External Independent-Review Evidence Packet — {spec.review_id}",
        "",
        f"- Candidate commit: `{spec.candidate_sha}`",
        f"- Intended external reviewer target: `{spec.intended_reviewer}`",
        f"- Initial content classification: `USER_PROVIDED_EXTERNAL_CONTENT`",
        f"- Delivery channel: `EXTERNAL_EVIDENCE_RELAY`",
        f"- Provider identity assurance: `{EXTERNAL_CONTENT_IDENTITY_ASSURANCE}`",
        f"- Can satisfy platform API-review authority: `false`",
        f"- Raw artifact hash basis: `{RAW_HASH_BASIS}`",
        "",
        target_note,
        "",
        "`TARGET_TRANSPORT.json` is convenience metadata only. It may change as provider interfaces evolve and is not part of the canonical reviewed source set.",
        "",
        "## Review instruction",
        "",
        spec.prompt.rstrip(),
        "",
        "## Authority and provenance rules",
        "",
        "1. The files under `raw-artifacts/` and their SHA-256 hashes are the canonical review bytes.",
        "2. This Markdown is a convenience rendering and is not independently authoritative over the raw files.",
        "3. Pasted or returned content starts as USER_PROVIDED_EXTERNAL_CONTENT; self-declared reviewer/provider/model fields do not classify or authenticate it.",
        "4. Only an explicit user attestation may later classify pasted content as USER_ATTESTED_EXTERNAL_LLM_REVIEW, and that still does not become provider-API authentication.",
        "5. Only platform AUTOMATIC_API or USER_INITIATED_API execution can satisfy a provider-authenticated platform review requirement.",
        "6. Green CI, reviewer agreement, or a PASS string is evidence only; it is not promotion authority.",
        "7. Review the exact candidate commit and report any candidate/hash mismatch.",
        "",
        "## Raw artifact manifest",
        "",
        "| Path | SHA-256 | Bytes |",
        "|---|---|---:|",
    ]
    for entry in entries:
        lines.append(f"| `{entry.path}` | `{entry.sha256}` | {entry.size_bytes} |")
    lines.extend(["", "## Canonical source rendering", ""])
    for entry in entries:
        lines.extend([
            f"### `{entry.path}`",
            "",
            f"SHA-256: `{entry.sha256}`",
            "",
            "````text",
            source_text[entry.path],
            "````",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def build_review_export(repo_root: str | Path, output_dir: str | Path, spec: ReviewExportSpec) -> dict:
    """Build a provider-neutral, byte-bound external-evidence export.

    The same raw artifact set is used regardless of Claude/DeepSeek/Kimi target.
    Target selection changes only convenience input hints. The resulting handoff
    is external content, not a platform API review and not reviewer authentication.
    """
    spec.validate()
    external_classification = ingest_user_provided_external_content()
    root = Path(repo_root)
    out = Path(output_dir)
    if not root.is_dir():
        raise ValueError("repo_root must be a directory")
    if out.exists():
        shutil.rmtree(out)
    raw_dir = out / "raw-artifacts"
    raw_dir.mkdir(parents=True)

    entries: list[ReviewSourceEntry] = []
    source_text: dict[str, str] = {}
    for relative in sorted(spec.source_paths):
        source, normalized = _safe_source(root, relative)
        data = source.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"review source is not UTF-8 text: {relative}") from exc
        destination = raw_dir / normalized
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        entry = ReviewSourceEntry(
            path=normalized,
            sha256=sha256(data).hexdigest(),
            size_bytes=len(data),
        )
        entries.append(entry)
        source_text[normalized] = text

    frozen_entries = tuple(entries)
    request = {
        "schema_version": 2,
        "review_id": spec.review_id,
        "candidate_sha": spec.candidate_sha,
        "intended_external_reviewer": spec.intended_reviewer,
        "content_classification": external_classification.review_class,
        "delivery_channel": external_classification.transport,
        "platform_review_transport": None,
        "provider_api_authenticated": external_classification.provider_api_authenticated,
        "can_satisfy_platform_review": external_classification.can_satisfy_platform_review,
        "provenance_basis": external_classification.provenance_basis,
        "reviewer_identity_assurance": EXTERNAL_CONTENT_IDENTITY_ASSURANCE,
        "raw_hash_basis": RAW_HASH_BASIS,
        "raw_artifacts": [asdict(entry) for entry in frozen_entries],
        "attestation_rule": "Only an explicit user statement may later classify returned content as USER_ATTESTED_EXTERNAL_LLM_REVIEW; content metadata cannot establish its own source.",
        "output_rule": "Return the requested external assessment only; self-declared provider/model metadata does not authenticate reviewer identity or satisfy a platform API-review gate.",
    }
    (out / "REVIEW_REQUEST.json").write_text(
        json.dumps(request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "REVIEW_PROMPT.txt").write_text(spec.prompt.rstrip() + "\n", encoding="utf-8")
    packet = _render_packet(spec, frozen_entries, source_text)
    (out / "REVIEW_PACKET.md").write_text(packet, encoding="utf-8")

    transport_profile = {
        "schema_version": 1,
        "intended_reviewer": spec.intended_reviewer,
        "checked_date": TRANSPORT_PROFILE_CHECKED_DATE,
        "authority": "CONVENIENCE_ONLY_NOT_REVIEW_EVIDENCE",
        **TARGET_TRANSPORT_PROFILES[spec.intended_reviewer],
    }
    (out / "TARGET_TRANSPORT.json").write_text(
        json.dumps(transport_profile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    checksum_paths = [
        out / "REVIEW_REQUEST.json",
        out / "REVIEW_PROMPT.txt",
        out / "REVIEW_PACKET.md",
        out / "TARGET_TRANSPORT.json",
    ]
    checksum_paths.extend(raw_dir / entry.path for entry in frozen_entries)
    checksum_lines = []
    for path in sorted(checksum_paths, key=lambda value: value.relative_to(out).as_posix()):
        relative = path.relative_to(out).as_posix()
        checksum_lines.append(f"{sha256(path.read_bytes()).hexdigest()}  {relative}")
    (out / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    return {
        "review_id": spec.review_id,
        "candidate_sha": spec.candidate_sha,
        "intended_reviewer": spec.intended_reviewer,
        "content_classification": external_classification.review_class,
        "can_satisfy_platform_review": False,
        "raw_artifact_count": len(frozen_entries),
        "raw_artifacts": [asdict(entry) for entry in frozen_entries],
        "packet_sha256": sha256((out / "REVIEW_PACKET.md").read_bytes()).hexdigest(),
        "request_sha256": sha256((out / "REVIEW_REQUEST.json").read_bytes()).hexdigest(),
        "transport_profile_sha256": sha256((out / "TARGET_TRANSPORT.json").read_bytes()).hexdigest(),
        "checksums_sha256": sha256((out / "SHA256SUMS.txt").read_bytes()).hexdigest(),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a deterministic Review Engine external-review evidence export")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--target", choices=sorted(SUPPORTED_REVIEW_TARGETS), default="provider-neutral")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--source", action="append", required=True)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    result = build_review_export(
        args.repo_root,
        args.output,
        ReviewExportSpec(
            review_id=args.review_id,
            candidate_sha=args.candidate_sha,
            intended_reviewer=args.target,
            prompt=prompt,
            source_paths=tuple(args.source),
        ),
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
