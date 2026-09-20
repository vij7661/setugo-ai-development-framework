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
DEFAULT_AUTHORITY_COMMIT = "b029ac5c801b07e2e94ebd4e8d1b0a0ddad6e0fb"
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

    def resolve_reviewed_commit(self) -> str:
        commit = str(self.root.get("reviewed_commit_anchor", ""))
        if len(commit) != 40 or not _git_commit_exists(commit):
            raise ValueError("reviewed_commit_not_resolved_git_object")
        return commit

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
    if values.get("reviewed_commit") != authority.resolve_reviewed_commit():
        raise ValueError("expectation_reviewed_commit_unbound")
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
    )


def require_authority_context(authority: AuthorityHandle | None, context: Any) -> None:
    if not authority_context_valid(authority, context):
        raise ValueError("expectation_authority_invalid")
