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
import os
import subprocess
import weakref
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTHORITY_COMMIT = "f0792cc01915eb3accd893aba2ed107bed9ec560"
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


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _delivery_binding_from_policy(policy: Mapping[str, Any], reviewed_commit: str) -> Mapping[str, Any]:
    request_id = str(policy.get("request_id", ""))
    items = policy.get("items")
    if not request_id or not isinstance(items, Mapping) or not items:
        raise ValueError("delivery_binding_policy_invalid")
    normalized_items: dict[str, dict[str, Any]] = {}
    for item_id, meta in sorted(items.items()):
        if not isinstance(meta, Mapping):
            raise ValueError("delivery_binding_policy_invalid")
        sha = str(meta.get("sha256", ""))
        size = int(meta.get("size", -1))
        if len(sha) != 64 or size < 0:
            raise ValueError("delivery_binding_policy_invalid")
        normalized_items[str(item_id)] = {"sha256": sha, "size": size}
    body = {"request_id": request_id, "reviewed_commit": reviewed_commit, "items": normalized_items}
    return {
        "policy_id": str(policy.get("policy_id", "")),
        "role": "DERIVED_BINDING_EVIDENCE",
        "authoritative": False,
        "request_id": request_id,
        "reviewed_commit": reviewed_commit,
        "items": normalized_items,
        "manifest_hash": _sha256(_canonical_json(body)),
    }


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
    source_commit: str = ""
    source_tree: str = ""

    def _require_source_binding(self) -> tuple[str, str]:
        """Return the explicit content-addressed S identity bound at execution entry."""
        commit = str(self.source_commit)
        tree = str(self.source_tree)
        if len(commit) != 40 or not _git_commit_exists(commit):
            raise ValueError("source_identity_binding_required")
        try:
            actual_tree = subprocess.check_output(
                ("git", "rev-parse", f"{commit}^{{tree}}"), cwd=ROOT, text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise ValueError("source_identity_tree_unavailable") from exc
        if not tree or tree != actual_tree:
            raise ValueError("source_identity_tree_mismatch")
        return commit, tree

    def resolve_reviewed_commit(self) -> str:
        commit, _ = self._require_source_binding()
        return commit

    def resolve_reviewed_tree(self) -> str:
        _, tree = self._require_source_binding()
        return tree

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
        policy = self.root.get("delivery_binding_policy")
        if not isinstance(policy, Mapping):
            raise ValueError("delivery_binding_policy_missing")
        if str(policy.get("request_id", "")) != request_id:
            raise ValueError("delivery_request_not_authorized")
        source_commit, _ = self._require_source_binding()
        derived = _delivery_binding_from_policy(policy, source_commit)
        # Current-S identity is supplied explicitly by the execution boundary.
        # The generated source-freeze artifact remains evidence only and is never
        # consulted by production authority resolution.
        return {
            "reviewed_commit": derived["reviewed_commit"],
            "manifest_hash": derived["manifest_hash"],
            "request_id": derived["request_id"],
            "policy_id": derived["policy_id"],
        }

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


def _explicit_source_binding(source_commit: str | None, source_tree: str | None) -> tuple[str, str]:
    commit = str(source_commit or os.environ.get("EXP_M_SOURCE_COMMIT", "")).strip()
    if len(commit) != 40 or not _git_commit_exists(commit):
        raise ValueError("source_identity_binding_required")
    try:
        actual_tree = subprocess.check_output(
            ("git", "rev-parse", f"{commit}^{{tree}}"), cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise ValueError("source_identity_tree_unavailable") from exc
    supplied_tree = str(source_tree or os.environ.get("EXP_M_SOURCE_TREE", "")).strip()
    if supplied_tree and supplied_tree != actual_tree:
        raise ValueError("source_identity_tree_mismatch")
    return commit, actual_tree


def load_authority(
    root_commit: str,
    *,
    source_commit: str | None = None,
    source_tree: str | None = None,
) -> AuthorityHandle:
    if root_commit != DEFAULT_AUTHORITY_COMMIT:
        raise ValueError("unpreregistered_authority_root")
    if not _git_commit_exists(root_commit):
        raise ValueError("authority_root_commit_missing")
    raw = _git_bytes(root_commit, ROOT_PATH)
    root_hash = _sha256(raw)
    data = json.loads(raw)
    if data.get("root_id") != "EXP-M-R2E-AUTHORITY-ROOT-3" or str(data.get("version", "")) != "3":
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
        ("qualification_ledger_path", "qualification_ledger_sha256"),
    ):
        raw = _git_bytes(root_commit, str(data[path_key]))
        if _sha256(raw) != str(data[hash_key]):
            raise ValueError(f"{hash_key}_mismatch")
    reviewed = str(data.get("reviewed_commit_anchor", ""))
    if not _git_commit_exists(reviewed):
        raise ValueError("reviewed_commit_not_resolved_git_object")
    if data.get("reviewed_commit_anchor_semantics") != "LEGACY_SIGNED_EXPECTATION_SENTINEL_ONLY":
        raise ValueError("reviewed_commit_anchor_semantics_invalid")
    source_policy = data.get("current_source_identity_policy") or {}
    delivery_policy = data.get("delivery_binding_policy") or {}
    if source_policy.get("policy_id") != "CURRENT-SOURCE-FREEZE-V1":
        raise ValueError("current_source_identity_policy_invalid")
    if delivery_policy.get("policy_id") != "SOURCE-FREEZE-DELIVERY-DERIVATION-V1":
        raise ValueError("delivery_binding_policy_invalid")
    # Validate the fixed request/item rule now. Current S is an explicit
    # content-addressed execution input; generated source-freeze evidence cannot
    # redirect the production authority.
    _delivery_binding_from_policy(delivery_policy, reviewed)
    bound_commit, bound_tree = _explicit_source_binding(source_commit, source_tree)
    return AuthorityHandle(root_commit, root_hash, data, True, bound_commit, bound_tree)


def load_default_authority(
    source_commit: str | None = None,
    source_tree: str | None = None,
) -> AuthorityHandle:
    return load_authority(
        DEFAULT_AUTHORITY_COMMIT,
        source_commit=source_commit,
        source_tree=source_tree,
    )


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
