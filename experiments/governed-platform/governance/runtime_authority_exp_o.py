"""Deterministic EXP-O runtime-authority falsification mechanisms.

These helpers model the architecture contract without calling an LLM or a real
provider.  They are intentionally fail-closed and are not wired into frozen
EXP-N Pilot 8/9 execution paths.
"""
from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
from typing import Any, Iterable, Mapping


FRESHNESS_LIMIT_MS = {
    "READ_ONLY": 60_000,
    "WORKSPACE_MUTATION": 15_000,
    "EXTERNAL_MUTATION": 0,
    "RELEASE_OR_PRODUCTION": 0,
}

UNTRUSTED_PROVENANCE = {
    "UNTRUSTED_EXTERNAL_CONTENT",
    "UNTRUSTED_USER_GENERATED_CONTENT",
    "TOOL_OUTPUT",
    "MODEL_PROPOSAL",
}


def _deny(reason: str, **extra: Any) -> dict[str, Any]:
    result = {"authorized": False, "decision": "DENY", "reason": reason}
    result.update(extra)
    return result


def evaluate_authority_freshness(
    capability: Mapping[str, Any],
    local_snapshot: Mapping[str, Any],
    *,
    origin_available: bool,
    online_authority_confirmed: bool = False,
) -> dict[str, Any]:
    """Evaluate whether cached authority may cross the requested effect boundary."""
    freshness_class = capability.get("freshness_class")
    if freshness_class not in FRESHNESS_LIMIT_MS:
        return _deny("UNKNOWN_FRESHNESS_CLASS")

    try:
        age_ms = int(local_snapshot.get("age_ms"))
        capability_epoch = int(capability.get("authority_epoch"))
        local_epoch = int(local_snapshot.get("authority_epoch"))
    except (TypeError, ValueError):
        return _deny("MALFORMED_AUTHORITY_SNAPSHOT")
    if age_ms < 0:
        return _deny("MALFORMED_AUTHORITY_SNAPSHOT")

    if local_epoch != capability_epoch:
        return _deny(
            "AUTHORITY_EPOCH_MISMATCH",
            requires_refresh=bool(origin_available),
            capability_epoch=capability_epoch,
            local_epoch=local_epoch,
        )

    cap_fence = capability.get("resource_fence")
    min_fence = local_snapshot.get("minimum_resource_fence")
    if min_fence is not None:
        if cap_fence is None:
            return _deny("RESOURCE_FENCE_REQUIRED")
        try:
            if int(cap_fence) < int(min_fence):
                return _deny("STALE_RESOURCE_FENCE")
        except (TypeError, ValueError):
            return _deny("MALFORMED_RESOURCE_FENCE")

    if freshness_class in {"EXTERNAL_MUTATION", "RELEASE_OR_PRODUCTION"}:
        if not origin_available or not online_authority_confirmed:
            return _deny("ONLINE_AUTHORITY_REQUIRED")
        if freshness_class == "RELEASE_OR_PRODUCTION" and cap_fence is None:
            return _deny("RESOURCE_FENCE_REQUIRED")
        return {
            "authorized": True,
            "decision": "ALLOW",
            "reason": "ONLINE_AUTHORITY_CURRENT",
            "freshness_class": freshness_class,
            "cached_authority_age_ms": age_ms,
            "external_authoritative_effect": True,
        }

    max_age = FRESHNESS_LIMIT_MS[freshness_class]
    if age_ms > max_age:
        if origin_available:
            return _deny(
                "AUTHORITY_REFRESH_REQUIRED",
                requires_refresh=True,
                freshness_class=freshness_class,
                cached_authority_age_ms=age_ms,
                max_cached_authority_age_ms=max_age,
            )
        return _deny(
            "STALE_AUTHORITY_FAIL_CLOSED",
            requires_refresh=False,
            freshness_class=freshness_class,
            cached_authority_age_ms=age_ms,
            max_cached_authority_age_ms=max_age,
        )

    return {
        "authorized": True,
        "decision": "ALLOW",
        "reason": "LOCAL_AUTHORITY_WITHIN_FRESHNESS_BOUND",
        "freshness_class": freshness_class,
        "cached_authority_age_ms": age_ms,
        "max_cached_authority_age_ms": max_age,
        "external_authoritative_effect": False,
    }


def _resource_allowed(resource: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(resource, pattern) for pattern in patterns)


def evaluate_action_effect(
    effect_contract: Mapping[str, Any],
    action_effect: Mapping[str, Any],
    *,
    semantic_verified: bool = False,
) -> dict[str, Any]:
    """Validate concrete effect parameters against a frozen plan-step contract."""
    if action_effect.get("effect_contract_id") != effect_contract.get("effect_contract_id"):
        return _deny("EFFECT_CONTRACT_BINDING_MISMATCH")
    if action_effect.get("base_sha") != effect_contract.get("base_sha"):
        return _deny("BASE_SHA_STALE_OR_MISMATCHED")

    allowed_actions = set(effect_contract.get("allowed_action_classes", []))
    if action_effect.get("action_class") not in allowed_actions:
        return _deny("ACTION_CLASS_OUT_OF_SCOPE")

    allowed_resources = list(effect_contract.get("allowed_resources", []))
    forbidden_resources = list(effect_contract.get("forbidden_resources", []))
    targets = list(action_effect.get("target_resources", []))
    changed_files = list(action_effect.get("changed_files", []))

    if not targets:
        return _deny("TARGET_RESOURCE_REQUIRED")
    for resource in targets + changed_files:
        if _resource_allowed(resource, forbidden_resources):
            return _deny("FORBIDDEN_RESOURCE_TOUCHED", resource=resource)
        if not _resource_allowed(resource, allowed_resources):
            return _deny("RESOURCE_OUT_OF_EFFECT_CONTRACT", resource=resource)

    max_changed_files = effect_contract.get("max_changed_files")
    if max_changed_files is not None and len(changed_files) > int(max_changed_files):
        return _deny("CHANGED_FILE_BOUND_EXCEEDED")

    if action_effect.get("destructive_effect", False) and not effect_contract.get(
        "destructive_effect_allowed", False
    ):
        return _deny("DESTRUCTIVE_EFFECT_FORBIDDEN")

    provenance = set(action_effect.get("provenance_trust_classes", []))
    semantic_required = bool(effect_contract.get("semantic_correspondence_required", False))
    if semantic_required and not semantic_verified:
        return {
            "authorized": False,
            "decision": "INDEPENDENT_SEMANTIC_VERIFICATION_REQUIRED",
            "reason": "CONTENT_CORRESPONDENCE_NOT_DETERMINISTICALLY_ESTABLISHED",
            "untrusted_provenance_present": bool(provenance & UNTRUSTED_PROVENANCE),
        }

    if provenance & UNTRUSTED_PROVENANCE and not semantic_verified:
        return {
            "authorized": False,
            "decision": "INDEPENDENT_SEMANTIC_VERIFICATION_REQUIRED",
            "reason": "UNTRUSTED_CONTENT_IN_EFFECT_PROVENANCE",
            "untrusted_provenance_present": True,
        }

    return {
        "authorized": True,
        "decision": "ALLOW",
        "reason": "EFFECT_MATCHES_FROZEN_CONTRACT",
        "semantic_verified": bool(semantic_verified),
    }


def _claim_prefix(resource: str) -> str:
    if resource.endswith("/**"):
        return resource[:-3]
    if resource.endswith("*"):
        return resource[:-1]
    return resource


def resources_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    lp = _claim_prefix(left)
    rp = _claim_prefix(right)
    return lp.startswith(rp) or rp.startswith(lp)


class ChangeClaimRegistry:
    """In-memory deterministic model of the preventive authoritative claim registry."""

    def __init__(self) -> None:
        self._claims: dict[str, dict[str, Any]] = {}
        self._next_epoch = 1

    def request_claim(
        self,
        *,
        task_id: str,
        base_sha: str,
        resources: list[str],
        mode: str,
    ) -> dict[str, Any]:
        if mode not in {"EXCLUSIVE", "PARALLEL_PROPOSAL"}:
            return {"disposition": "DENIED_INVALID_MODE"}
        if not resources:
            return {"disposition": "DENIED_EMPTY_SCOPE"}

        overlaps: list[str] = []
        for other_task, claim in self._claims.items():
            if claim.get("status") != "ACTIVE" or other_task == task_id:
                continue
            if any(
                resources_overlap(a, b)
                for a in resources
                for b in claim.get("resources", [])
            ):
                overlaps.append(other_task)
                if mode == "EXCLUSIVE" or claim.get("mode") == "EXCLUSIVE":
                    return {
                        "disposition": "WAITING_CONFLICT",
                        "conflicts_with": sorted(overlaps),
                    }

        disposition = (
            "EXCLUSIVE_GRANTED" if mode == "EXCLUSIVE" else "PARALLEL_PROPOSAL_GRANTED"
        )
        epoch = self._next_epoch
        self._next_epoch += 1
        self._claims[task_id] = {
            "task_id": task_id,
            "base_sha": base_sha,
            "resources": list(resources),
            "mode": mode,
            "claim_epoch": epoch,
            "status": "ACTIVE",
            "disposition": disposition,
        }
        return {
            "disposition": disposition,
            "claim_epoch": epoch,
            "overlaps": sorted(overlaps),
        }

    def revalidate_for_integration(self, task_id: str, current_head_sha: str) -> dict[str, Any]:
        claim = self._claims.get(task_id)
        if not claim or claim.get("status") != "ACTIVE":
            return {"decision": "NO_ACTIVE_CLAIM"}
        if claim.get("base_sha") != current_head_sha:
            return {
                "decision": "REVALIDATION_REQUIRED",
                "reason": "AUTHORITATIVE_HEAD_CHANGED",
                "claim_epoch": claim.get("claim_epoch"),
            }
        if claim.get("mode") == "PARALLEL_PROPOSAL":
            return {
                "decision": "COMBINED_VERIFICATION_REQUIRED",
                "reason": "PARALLEL_PROPOSAL_IS_NON_AUTHORITATIVE",
                "claim_epoch": claim.get("claim_epoch"),
            }
        return {
            "decision": "CURRENT_HEAD_VERIFICATION_REQUIRED",
            "reason": "CLAIM_CURRENT_BUT_RELEASE_NOT_IMPLIED",
            "claim_epoch": claim.get("claim_epoch"),
        }


def validate_sender_constrained_capability(
    capability: Mapping[str, Any],
    *,
    worker_id: str,
    worker_key_thumbprint: str,
) -> dict[str, Any]:
    if capability.get("revoked", False):
        return _deny("CAPABILITY_REVOKED")
    if capability.get("subject_id") != worker_id:
        return _deny("WORKER_IDENTITY_MISMATCH")
    if capability.get("subject_key_thumbprint") != worker_key_thumbprint:
        return _deny("SENDER_KEY_MISMATCH")
    if not capability.get("capability_id") or not capability.get("capability_nonce"):
        return _deny("CAPABILITY_BINDING_INCOMPLETE")
    return {"authorized": True, "decision": "ALLOW", "reason": "SENDER_BOUND"}


def reissue_for_replacement_worker(
    old_capability: Mapping[str, Any],
    *,
    new_worker_id: str,
    new_worker_key_thumbprint: str,
    new_capability_id: str,
    new_nonce: str,
    spool_reconciled: bool,
) -> dict[str, Any]:
    if not spool_reconciled:
        return {"reissued": False, "reason": "DURABLE_SPOOL_RECONCILIATION_REQUIRED"}
    if new_capability_id == old_capability.get("capability_id"):
        return {"reissued": False, "reason": "NEW_CAPABILITY_ID_REQUIRED"}
    if new_nonce == old_capability.get("capability_nonce"):
        return {"reissued": False, "reason": "NEW_CAPABILITY_NONCE_REQUIRED"}

    old_revoked = copy.deepcopy(dict(old_capability))
    old_revoked["revoked"] = True

    try:
        old_epoch = int(old_capability.get("authority_epoch", 0))
    except (TypeError, ValueError):
        return {"reissued": False, "reason": "MALFORMED_OLD_AUTHORITY_EPOCH"}

    new_capability = copy.deepcopy(dict(old_capability))
    new_capability.update(
        {
            "capability_id": new_capability_id,
            "capability_nonce": new_nonce,
            "subject_id": new_worker_id,
            "subject_key_thumbprint": new_worker_key_thumbprint,
            "authority_epoch": old_epoch + 1,
            "revoked": False,
        }
    )
    return {
        "reissued": True,
        "old_capability": old_revoked,
        "new_capability": new_capability,
        "spool_reconciled": True,
    }


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def append_evidence_record(records: list[dict[str, Any]], payload: Mapping[str, Any]) -> dict[str, Any]:
    sequence = len(records) + 1
    previous_hash = records[-1]["record_hash"] if records else "GENESIS"
    record_core = {
        "sequence": sequence,
        "previous_hash": previous_hash,
        "payload": dict(payload),
    }
    record_hash = hashlib.sha256(_canonical_json(record_core)).hexdigest()
    record = dict(record_core)
    record["record_hash"] = record_hash
    records.append(record)
    return record


def _verify_record_chain(records: list[Mapping[str, Any]]) -> bool:
    previous_hash = "GENESIS"
    for index, record in enumerate(records, start=1):
        if record.get("sequence") != index or record.get("previous_hash") != previous_hash:
            return False
        core = {
            "sequence": record.get("sequence"),
            "previous_hash": record.get("previous_hash"),
            "payload": record.get("payload"),
        }
        expected = hashlib.sha256(_canonical_json(core)).hexdigest()
        if record.get("record_hash") != expected:
            return False
        previous_hash = expected
    return True


def merkle_root(hashes: list[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    level = [bytes.fromhex(item) for item in hashes]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            hashlib.sha256(level[i] + level[i + 1]).digest()
            for i in range(0, len(level), 2)
        ]
    return level[0].hex()


def create_checkpoint_and_anchor(
    records: list[Mapping[str, Any]],
    *,
    partition_id: str,
    covered_count: int | None = None,
    anchor_trust_domain: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if covered_count is None:
        covered_count = len(records)
    if covered_count < 0 or covered_count > len(records):
        raise ValueError("covered_count outside record range")
    covered = records[:covered_count]
    root = merkle_root([str(item["record_hash"]) for item in covered])
    checkpoint = {
        "partition_id": partition_id,
        "covered_count": covered_count,
        "merkle_root": root,
    }
    anchor = {
        "partition_id": partition_id,
        "covered_count": covered_count,
        "merkle_root": root,
        "trust_domain": anchor_trust_domain,
    }
    return checkpoint, anchor


def verify_anchored_checkpoint(
    records: list[Mapping[str, Any]],
    checkpoint: Mapping[str, Any],
    anchor: Mapping[str, Any],
    *,
    primary_trust_domain: str,
) -> dict[str, Any]:
    try:
        covered_count = int(checkpoint.get("covered_count"))
    except (TypeError, ValueError):
        return {"verified": False, "state": "MALFORMED_CHECKPOINT"}
    if covered_count < 0 or covered_count > len(records):
        return {"verified": False, "state": "MALFORMED_CHECKPOINT"}

    covered = records[:covered_count]
    if not _verify_record_chain(covered):
        return {"verified": False, "state": "COVERED_RECORD_CHAIN_TAMPER_DETECTED"}

    root = merkle_root([str(item["record_hash"]) for item in covered])
    if checkpoint.get("merkle_root") != root:
        return {"verified": False, "state": "CHECKPOINT_ROOT_MISMATCH"}
    if anchor.get("merkle_root") != root:
        return {"verified": False, "state": "ANCHOR_ROOT_MISMATCH"}
    if anchor.get("trust_domain") == primary_trust_domain:
        return {"verified": False, "state": "ANCHOR_NOT_INDEPENDENT"}

    tail = len(records) - covered_count
    if tail:
        return {
            "verified": True,
            "state": "ANCHORED_WITH_UNCHECKPOINTED_TAIL",
            "uncheckpointed_records": tail,
            "release_integrity_current": False,
        }
    return {
        "verified": True,
        "state": "FULLY_ANCHORED",
        "uncheckpointed_records": 0,
        "release_integrity_current": True,
    }


def checkpoint_due(
    *,
    records_since_checkpoint: int,
    age_ms: int,
    high_risk: bool,
) -> bool:
    if records_since_checkpoint < 0 or age_ms < 0:
        raise ValueError("checkpoint counters cannot be negative")
    if high_risk:
        return records_since_checkpoint >= 100 or age_ms >= 10_000
    return records_since_checkpoint >= 1_000 or age_ms >= 60_000
