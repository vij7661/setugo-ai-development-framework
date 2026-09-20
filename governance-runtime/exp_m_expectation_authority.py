"""Externally pinned expectation authority for EXP-M R2E.

The trust root is a preregistered Git commit created before the governed R2E
implementation.  Production admissibility accepts only PredicateContext
instances materialized by this loader after hash + RSA signature verification.
No expected value is derived from the EvidenceBundle under review.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import base64
import hashlib
import hmac
import json
import subprocess
import weakref
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTHORITY_COMMIT = "e24e18a0f05e9be38e4f549a77914e014c738812"
ROOT_PATH = "experiments/governed-platform/EXP-M-R2E-AUTHORITY-ROOT.json"
_SHA256_DER_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")

# Identity registry, intentionally not equality based: copying all expected
# values and the manifest hash does not create authority.
_AUTHORIZED_CONTEXTS: dict[int, tuple[weakref.ReferenceType[Any], str, str]] = {}


def _git_bytes(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(
            ("git", "show", f"{commit}:{path}"), cwd=ROOT, stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise ValueError(f"authority_git_object_unavailable:{commit}:{path}") from exc


def _git_commit_exists(commit: str) -> bool:
    try:
        subprocess.check_call(
            ("git", "cat-file", "-e", f"{commit}^{{commit}}"),
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _verify_rsa_pkcs1_v15_sha256(raw: bytes, signature_b64: bytes, n: int, e: int) -> bool:
    try:
        signature = base64.b64decode(signature_b64.strip(), validate=True)
    except Exception:
        return False
    k = (n.bit_length() + 7) // 8
    if len(signature) != k:
        return False
    encoded = pow(int.from_bytes(signature, "big"), e, n).to_bytes(k, "big")
    digest_info = _SHA256_DER_PREFIX + hashlib.sha256(raw).digest()
    padding_len = k - len(digest_info) - 3
    if padding_len < 8:
        return False
    expected = b"\x00\x01" + (b"\xff" * padding_len) + b"\x00" + digest_info
    return hmac.compare_digest(encoded, expected)


@dataclass(frozen=True)
class AuthorityHandle:
    root_commit: str
    root_hash: str
    root: Mapping[str, Any]
    protocol_available: bool = True

    def _source_freeze(self) -> Mapping[str, Any] | None:
        """Load and independently verify the C-4 source-freeze artifact when present."""
        path = ROOT / "experiments" / "governed-platform" / "EXP-M-SOURCE-FREEZE.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError("source_freeze_unreadable") from exc
        commit = str(data.get("source_commit", ""))
        tree = str(data.get("source_tree", ""))
        if len(commit) != 40 or not _git_commit_exists(commit):
            raise ValueError("source_freeze_commit_invalid")
        try:
            actual_tree = subprocess.check_output(
                ("git", "rev-parse", f"{commit}^{{tree}}"), cwd=ROOT, text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise ValueError("source_freeze_tree_unavailable") from exc
        if actual_tree != tree:
            raise ValueError("source_freeze_tree_mismatch")
        source_files = data.get("source_files")
        if not isinstance(source_files, Mapping) or not source_files:
            raise ValueError("source_freeze_manifest_empty")
        for source_path, expected_hash in source_files.items():
            try:
                raw = _git_bytes(commit, str(source_path))
            except ValueError as exc:
                raise ValueError(f"source_freeze_file_missing:{source_path}") from exc
            if _sha256(raw) != str(expected_hash):
                raise ValueError(f"source_freeze_file_hash_mismatch:{source_path}")
            working = ROOT / str(source_path)
            if working.exists() and _sha256(working.read_bytes()) != str(expected_hash):
                raise ValueError(f"source_freeze_worktree_hash_mismatch:{source_path}")
        return data

    def resolve_reviewed_commit(self) -> str:
        freeze = self._source_freeze()
        if freeze is not None:
            return str(freeze["source_commit"])
        commit = str(self.root.get("reviewed_commit_anchor", ""))
        if len(commit) != 40 or not _git_commit_exists(commit):
            raise ValueError("reviewed_commit_not_resolved_git_object")
        return commit

    def resolve_reviewed_tree(self) -> str:
        freeze = self._source_freeze()
        if freeze is not None:
            return str(freeze["source_tree"])
        commit = self.resolve_reviewed_commit()
        try:
            return subprocess.check_output(
                ("git", "rev-parse", f"{commit}^{{tree}}"), cwd=ROOT, text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise ValueError("reviewed_tree_not_resolved_git_object") from exc

    def _load_hashed_json(self, path_key: str, hash_key: str) -> Mapping[str, Any]:
        path = str(self.root[path_key])
        raw = _git_bytes(self.root_commit, path)
        if _sha256(raw) != str(self.root[hash_key]):
            raise ValueError(f"{hash_key}_mismatch")
        return json.loads(raw)

    def resolve_retrieval_bytes(self, source_id: str, version: str, start: int, end: int) -> bytes:
        ledger = self._load_hashed_json("retrieval_source_ledger_path", "retrieval_source_ledger_sha256")
        entry = (ledger.get("sources") or {}).get(f"{source_id}|{version}")
        if not isinstance(entry, Mapping):
            raise ValueError("retrieval_source_not_authorized")
        raw = _git_bytes(self.root_commit, str(entry["path"]))
        if _sha256(raw) != str(entry["sha256"]) or len(raw) != int(entry["length"]):
            raise ValueError("retrieval_source_integrity_failure")
        if start < 0 or end < start or end > len(raw):
            raise ValueError("retrieval_range_invalid")
        return raw[start:end]

    def expected_delivery(self, request_id: str) -> Mapping[str, Any]:
        freeze = self._source_freeze()
        if freeze is not None:
            entry = ((freeze.get("delivery_authority") or {}).get("requests") or {}).get(request_id)
            if not isinstance(entry, Mapping):
                raise ValueError("delivery_request_not_authorized")
            if str(entry.get("reviewed_commit", "")) != str(freeze["source_commit"]):
                raise ValueError("delivery_source_freeze_commit_mismatch")
            return entry
        ledger = self._load_hashed_json("delivery_ledger_path", "delivery_ledger_sha256")
        entry = (ledger.get("requests") or {}).get(request_id)
        if not isinstance(entry, Mapping):
            raise ValueError("delivery_request_not_authorized")
        return entry

    def qualification_entry(self, plan_id: str) -> Mapping[str, Any]:
        ledger = self._load_hashed_json("qualification_ledger_path", "qualification_ledger_sha256")
        entry = (ledger.get("plans") or {}).get(plan_id)
        if not isinstance(entry, Mapping):
            raise ValueError("qualification_authority_plan_missing")
        return entry

    def load_r5_protocol(self) -> Mapping[str, Any]:
        if not self.protocol_available:
            raise ValueError("r5_protocol_unavailable")
        path = str(self.root["r5_protocol_path"])
        raw = _git_bytes(self.root_commit, path)
        if _sha256(raw) != str(self.root["r5_protocol_sha256"]):
            raise ValueError("r5_protocol_hash_mismatch")
        data = json.loads(raw)
        if data.get("protocol_id") != "R5-CP-1" or data.get("live_provider_execution_authorized") is not False:
            raise ValueError("r5_protocol_invalid")
        return data

    def with_missing_r5_protocol_for_test(self) -> "AuthorityHandle":
        return replace(self, protocol_available=False)

    def canonical_wire_hash_for_test(self, manifest, materialized, returned_items) -> str:
        # Public helper is intentionally limited to deterministic test wiring.
        from exp_m_deterministic import canonical_wire_hash
        return canonical_wire_hash(manifest.request_id, "a", "s", returned_items)


def load_authority(root_commit: str) -> AuthorityHandle:
    if root_commit != DEFAULT_AUTHORITY_COMMIT:
        raise ValueError("unpreregistered_authority_root")
    if not _git_commit_exists(root_commit):
        raise ValueError("authority_root_commit_missing")
    raw = _git_bytes(root_commit, ROOT_PATH)
    root_hash = _sha256(raw)
    data = json.loads(raw)
    if data.get("root_id") != "EXP-M-R2E-AUTHORITY-ROOT-1":
        raise ValueError("authority_root_id_mismatch")
    if data.get("authority_private_key_committed") is not False:
        raise ValueError("authority_private_key_boundary_invalid")
    if data.get("live_provider_execution_authorized") is not False:
        raise ValueError("authority_scope_invalid")
    # Verify every separately frozen authority input before constructing a handle.
    manifest_raw = _git_bytes(root_commit, str(data["test_expectation_manifest_path"]))
    if _sha256(manifest_raw) != str(data["test_expectation_manifest_sha256"]):
        raise ValueError("expectation_manifest_hash_mismatch")
    protocol_raw = _git_bytes(root_commit, str(data["r5_protocol_path"]))
    if _sha256(protocol_raw) != str(data["r5_protocol_sha256"]):
        raise ValueError("r5_protocol_hash_mismatch")
    for path_key, hash_key in (
        ("retrieval_source_ledger_path", "retrieval_source_ledger_sha256"),
        ("delivery_ledger_path", "delivery_ledger_sha256"),
        ("qualification_ledger_path", "qualification_ledger_sha256"),
    ):
        raw = _git_bytes(root_commit, str(data[path_key]))
        if _sha256(raw) != str(data[hash_key]):
            raise ValueError(f"{hash_key}_mismatch")
    reviewed = str(data.get("reviewed_commit_anchor", ""))
    if not _git_commit_exists(reviewed):
        raise ValueError("reviewed_commit_not_resolved_git_object")
    return AuthorityHandle(root_commit, root_hash, data)


def load_default_authority() -> AuthorityHandle:
    return load_authority(DEFAULT_AUTHORITY_COMMIT)


def load_predicate_context(authority: AuthorityHandle):
    from exp_m_deterministic import PredicateContext

    root = authority.root
    manifest_raw = _git_bytes(authority.root_commit, str(root["test_expectation_manifest_path"]))
    signature_raw = _git_bytes(authority.root_commit, str(root["test_expectation_signature_path"]))
    if _sha256(manifest_raw) != str(root["test_expectation_manifest_sha256"]):
        raise ValueError("expectation_manifest_hash_mismatch")
    if not _verify_rsa_pkcs1_v15_sha256(
        manifest_raw,
        signature_raw,
        int(root["public_modulus_decimal"]),
        int(root["public_exponent"]),
    ):
        raise ValueError("expectation_signature_invalid")
    parsed = json.loads(manifest_raw)
    if parsed.get("scope") != "OFFLINE_TEST_ONLY":
        raise ValueError("expectation_scope_invalid")
    values = dict(parsed.get("context") or {})
    # The signed manifest freezes every expected value except the final reviewed
    # source identity. C-4 moves that identity to the independently verified
    # source-freeze artifact S; before S exists the legacy root anchor remains.
    signed_reviewed_commit = str(values.get("reviewed_commit", ""))
    legacy_anchor = str(root.get("reviewed_commit_anchor", ""))
    if signed_reviewed_commit != legacy_anchor:
        raise ValueError("signed_expectation_legacy_commit_mismatch")
    values["reviewed_commit"] = authority.resolve_reviewed_commit()
    values["reviewed_tree"] = authority.resolve_reviewed_tree()
    manifest_hash = _sha256(manifest_raw)
    context = PredicateContext(**values, expectation_manifest_hash=manifest_hash)
    _AUTHORIZED_CONTEXTS[id(context)] = (weakref.ref(context), authority.root_hash, manifest_hash)
    return context


def authority_context_valid(authority: AuthorityHandle | None, context: Any) -> bool:
    if authority is None:
        return False
    row = _AUTHORIZED_CONTEXTS.get(id(context))
    if row is None:
        return False
    ref, root_hash, manifest_hash = row
    if ref() is not context:
        return False
    return (
        root_hash == authority.root_hash
        and manifest_hash == getattr(context, "expectation_manifest_hash", None)
        and getattr(context, "reviewed_commit", None) == authority.resolve_reviewed_commit()
        and getattr(context, "reviewed_tree", None) == authority.resolve_reviewed_tree()
    )


def require_authority_context(authority: AuthorityHandle | None, context: Any) -> None:
    if not authority_context_valid(authority, context):
        raise ValueError("expectation_authority_invalid")
