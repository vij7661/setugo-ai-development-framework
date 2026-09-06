"""EXP-O strict semantic-verification binding for use-time effects.

This module wraps the historical LocalEnforcementPoint/McpGateway pilot path so
independent semantic verification is signed and bound to the exact candidate
and effect. The inner LEP permit is retained server-side and is never returned
to the model/agent-facing caller.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
import uuid
from typing import Any, Mapping

from runtime_slice_exp_o import LocalEnforcementPoint, McpGateway


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sign(payload: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    body = copy.deepcopy(dict(payload))
    return {"payload": body, "signature": hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()}


def _verify(envelope: Mapping[str, Any] | None, key: bytes) -> bool:
    if not isinstance(envelope, Mapping):
        return False
    payload = envelope.get("payload")
    signature = envelope.get("signature")
    if not isinstance(payload, Mapping) or not isinstance(signature, str):
        return False
    expected = hmac.new(key, _canonical(dict(payload)), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def semantic_effect_view(effect: Mapping[str, Any]) -> dict[str, Any]:
    """Canonical fields whose semantics are independently verified."""
    return {
        "semantic_payload_digest": effect.get("semantic_payload_digest"),
        "action_class": effect.get("action_class"),
        "target_resources": list(effect.get("target_resources", [])),
        "changed_files": list(effect.get("changed_files", [])),
        "base_sha": effect.get("base_sha"),
        "effect_contract_id": effect.get("effect_contract_id"),
        "destructive_effect": bool(effect.get("destructive_effect", False)),
        "provenance_trust_classes": sorted(effect.get("provenance_trust_classes", [])),
    }


class SemanticVerificationAuthority:
    """Independent platform verifier that signs exact candidate/effect evidence."""

    def __init__(self, signing_key: bytes, *, verifier_id: str = "semantic-verifier") -> None:
        self._key = signing_key
        self.verifier_id = verifier_id
        self._counter = 0

    @property
    def verification_key(self) -> bytes:
        return self._key

    def verify_candidate(self, *, candidate_payload: Mapping[str, Any], effect: Mapping[str, Any]) -> dict[str, Any]:
        candidate_digest = digest(dict(candidate_payload))
        if effect.get("semantic_payload_digest") != candidate_digest:
            raise ValueError("effect semantic_payload_digest does not match candidate")
        self._counter += 1
        effect_view = semantic_effect_view(effect)
        payload = {
            "verification_id": f"semver-{self._counter}-{uuid.uuid4().hex[:12]}",
            "verifier_id": self.verifier_id,
            "verified": True,
            "semantic_payload_digest": candidate_digest,
            "effect_digest": digest(effect_view),
            "effect_contract_id": effect_view["effect_contract_id"],
            "base_sha": effect_view["base_sha"],
            "action_class": effect_view["action_class"],
            "target_resources": effect_view["target_resources"],
            "changed_files": effect_view["changed_files"],
        }
        return _sign(payload, self._key)


class _InnerPermitStore:
    """Server-side inner-permit registry; callers never receive raw LEP permits."""

    def __init__(self) -> None:
        self._permits: dict[str, dict[str, Any]] = {}

    def put(self, bound_permit_id: str, lep_permit: Mapping[str, Any]) -> None:
        self._permits[bound_permit_id] = copy.deepcopy(dict(lep_permit))

    def get(self, bound_permit_id: str) -> dict[str, Any] | None:
        value = self._permits.get(bound_permit_id)
        return copy.deepcopy(value) if value is not None else None

    def consume(self, bound_permit_id: str) -> dict[str, Any] | None:
        value = self._permits.pop(bound_permit_id, None)
        return copy.deepcopy(value) if value is not None else None


class SemanticBoundLocalEnforcementPoint:
    """Verifies exact signed semantic evidence before allowing the historical LEP."""

    def __init__(
        self,
        lep: LocalEnforcementPoint,
        *,
        semantic_verification_key: bytes,
        bound_permit_signing_key: bytes,
        permit_store: _InnerPermitStore,
    ) -> None:
        self._lep = lep
        self._semantic_key = semantic_verification_key
        self._bound_key = bound_permit_signing_key
        self._store = permit_store
        self._counter = 0

    @property
    def bound_permit_verification_key(self) -> bytes:
        return self._bound_key

    def authorize(
        self,
        capability: Mapping[str, Any] | None,
        *,
        candidate_payload: Mapping[str, Any],
        semantic_verification: Mapping[str, Any] | None,
        worker_id: str,
        worker_key_thumbprint: str,
        effect_contract: Mapping[str, Any],
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
        origin_available: bool,
        online_authority_confirmed: bool,
    ) -> dict[str, Any]:
        candidate_digest = digest(dict(candidate_payload))
        if effect.get("semantic_payload_digest") != candidate_digest:
            return {"authorized": False, "decision": "DENY", "reason": "SEMANTIC_CANDIDATE_EFFECT_DIGEST_MISMATCH"}
        if not _verify(semantic_verification, self._semantic_key):
            return {"authorized": False, "decision": "DENY", "reason": "SIGNED_SEMANTIC_VERIFICATION_REQUIRED"}

        evidence = dict(semantic_verification["payload"])
        effect_view = semantic_effect_view(effect)
        expected = {
            "semantic_payload_digest": candidate_digest,
            "effect_digest": digest(effect_view),
            "effect_contract_id": effect_view["effect_contract_id"],
            "base_sha": effect_view["base_sha"],
            "action_class": effect_view["action_class"],
            "target_resources": effect_view["target_resources"],
            "changed_files": effect_view["changed_files"],
        }
        if evidence.get("verified") is not True:
            return {"authorized": False, "decision": "DENY", "reason": "SEMANTIC_VERIFICATION_NOT_TRUE"}
        for key, value in expected.items():
            if evidence.get(key) != value:
                return {"authorized": False, "decision": "DENY", "reason": f"SEMANTIC_VERIFICATION_BINDING_MISMATCH:{key}"}

        inner = self._lep.authorize(
            capability,
            worker_id=worker_id,
            worker_key_thumbprint=worker_key_thumbprint,
            effect_contract=effect_contract,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=now_ms,
            origin_available=origin_available,
            online_authority_confirmed=online_authority_confirmed,
            semantic_verified=True,
        )
        if not inner.get("authorized", False) or not inner.get("permit"):
            return inner

        self._counter += 1
        bound_permit_id = f"semantic-permit-{self._counter}-{uuid.uuid4().hex[:12]}"
        self._store.put(bound_permit_id, inner["permit"])
        outer_payload = {
            "bound_permit_id": bound_permit_id,
            "semantic_payload_digest": candidate_digest,
            "effect_digest": digest(effect_view),
            "semantic_verification_digest": digest(semantic_verification),
            "idempotency_key": idempotency_key,
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect_contract_id": effect.get("effect_contract_id"),
            "base_sha": effect.get("base_sha"),
        }
        return {
            "authorized": True,
            "decision": "SEMANTIC_BOUND_PERMIT_ISSUED",
            "permit": _sign(outer_payload, self._bound_key),
            "inner_lep_decision": inner.get("decision"),
            "semantic_verification_id": evidence.get("verification_id"),
        }


class SemanticBoundGateway:
    """Only accepts semantic-bound permits and keeps raw LEP permits server-side."""

    def __init__(
        self,
        gateway: McpGateway,
        *,
        bound_permit_verification_key: bytes,
        permit_store: _InnerPermitStore,
    ) -> None:
        self._gateway = gateway
        self._bound_key = bound_permit_verification_key
        self._store = permit_store

    def execute(
        self,
        *,
        permit: Mapping[str, Any] | None,
        candidate_payload: Mapping[str, Any],
        worker_id: str,
        worker_key_thumbprint: str,
        effect: Mapping[str, Any],
        idempotency_key: str,
        now_ms: int,
    ) -> dict[str, Any]:
        if not _verify(permit, self._bound_key):
            return {"decision": "DENIED", "reason": "SEMANTIC_BOUND_PERMIT_INVALID"}
        payload = dict(permit["payload"])
        candidate_digest = digest(dict(candidate_payload))
        effect_view = semantic_effect_view(effect)
        checks = {
            "semantic_payload_digest": candidate_digest,
            "effect_digest": digest(effect_view),
            "idempotency_key": idempotency_key,
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect_contract_id": effect.get("effect_contract_id"),
            "base_sha": effect.get("base_sha"),
        }
        for key, value in checks.items():
            if payload.get(key) != value:
                return {"decision": "DENIED", "reason": f"SEMANTIC_BOUND_PERMIT_MISMATCH:{key}"}

        bound_permit_id = str(payload.get("bound_permit_id", ""))
        if not bound_permit_id:
            return {"decision": "DENIED", "reason": "SEMANTIC_BOUND_PERMIT_ID_REQUIRED"}
        inner_permit = self._store.consume(bound_permit_id)
        if inner_permit is None:
            return {"decision": "DENIED", "reason": "INNER_LEP_PERMIT_MISSING_OR_CONSUMED"}
        return self._gateway.execute(
            permit=inner_permit,
            worker_id=worker_id,
            worker_key_thumbprint=worker_key_thumbprint,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=now_ms,
        )

    def effect_count(self) -> int:
        return self._gateway.effect_count()


def make_permit_store() -> _InnerPermitStore:
    """Factory keeps the registry type private to callers outside the module."""
    return _InnerPermitStore()
