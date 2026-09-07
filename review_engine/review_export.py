from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path


SUPPORTED_REVIEW_TARGETS = frozenset({"provider-neutral", "claude", "deepseek", "kimi"})
MANUAL_RELAY_IDENTITY_ASSURANCE = "MANUAL_RELAY_UNVERIFIED_PROVIDER_IDENTITY"
RAW_HASH_BASIS = "RAW_FILE_BYTES"


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
    # Resolve only for containment validation. The retained/canonical path remains
    # the repository-relative path supplied in the source manifest.
    resolved_root = root.resolve()
    resolved_source = source.resolve()
    if resolved_source != resolved_root and resolved_root not in resolved_source.parents:
        raise ValueError(f"review source escapes repository root: {relative}")
    return source, normalized


def _render_packet(spec: ReviewExportSpec, entries: tuple[ReviewSourceEntry, ...], source_text: dict[str, str]) -> str:
    target_note = {
        "provider-neutral": "Use this packet with any independent reviewer that can consume UTF-8 text/Markdown.",
        "claude": "Claude-targeted transport hint only; reviewer identity is not proven by this file.",
        "deepseek": "DeepSeek-targeted transport hint only; this Markdown can be supplied as plain text when document upload is unavailable.",
        "kimi": "Kimi-targeted transport hint only; reviewer identity is not proven by this file.",
    }[spec.intended_reviewer]
    lines = [
        f"# Independent Review Packet — {spec.review_id}",
        "",
        f"- Candidate commit: `{spec.candidate_sha}`",
        f"- Intended reviewer target: `{spec.intended_reviewer}`",
        f"- Identity assurance for manual relay: `{MANUAL_RELAY_IDENTITY_ASSURANCE}`",
        f"- Raw artifact hash basis: `{RAW_HASH_BASIS}`",
        "",
        target_note,
        "",
        "## Review instruction",
        "",
        spec.prompt.rstrip(),
        "",
        "## Authority and provenance rules",
        "",
        "1. The files under `raw-artifacts/` and their SHA-256 hashes are the canonical review bytes.",
        "2. This Markdown is a convenience rendering and is not independently authoritative over the raw files.",
        "3. Do not infer reviewer/provider/model identity from self-declared output metadata.",
        "4. Green CI, reviewer agreement, or a PASS string is evidence only; it is not promotion authority.",
        "5. Review the exact candidate commit and report any candidate/hash mismatch.",
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
    """Build one provider-neutral, byte-bound manual-review export.

    The same raw artifact set is used regardless of Claude/DeepSeek/Kimi target.
    Target selection changes only transport/readability hints in convenience
    files; it cannot alter the reviewed source bytes or authenticate the reviewer.
    """
    spec.validate()
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
        "schema_version": 1,
        "review_id": spec.review_id,
        "candidate_sha": spec.candidate_sha,
        "intended_reviewer": spec.intended_reviewer,
        "transport": "MANUAL_RELAY",
        "reviewer_identity_assurance": MANUAL_RELAY_IDENTITY_ASSURANCE,
        "raw_hash_basis": RAW_HASH_BASIS,
        "raw_artifacts": [asdict(entry) for entry in frozen_entries],
        "output_rule": "Return the requested review result only; self-declared provider/model metadata does not authenticate reviewer identity.",
    }
    (out / "REVIEW_REQUEST.json").write_text(
        json.dumps(request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "REVIEW_PROMPT.txt").write_text(spec.prompt.rstrip() + "\n", encoding="utf-8")
    packet = _render_packet(spec, frozen_entries, source_text)
    (out / "REVIEW_PACKET.md").write_text(packet, encoding="utf-8")

    checksum_paths = [out / "REVIEW_REQUEST.json", out / "REVIEW_PROMPT.txt", out / "REVIEW_PACKET.md"]
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
        "raw_artifact_count": len(frozen_entries),
        "raw_artifacts": [asdict(entry) for entry in frozen_entries],
        "packet_sha256": sha256((out / "REVIEW_PACKET.md").read_bytes()).hexdigest(),
        "request_sha256": sha256((out / "REVIEW_REQUEST.json").read_bytes()).hexdigest(),
        "checksums_sha256": sha256((out / "SHA256SUMS.txt").read_bytes()).hexdigest(),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a deterministic Review Engine independent-review export")
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
