#!/usr/bin/env python3
"""Provider-neutral administrative-domain quorum core for EXP-O Pilot 27.

This module does not call cloud providers and is not scientific Pilot 27 evidence.
It freezes the threshold semantics that provider adapters must feed after exact
signature/key/domain verification.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable, Mapping

PILOT = "PILOT27-INDEPENDENT-ROOT-DOMAINS"
PURPOSE = "independent-root-checkpoint-integrity"
ROOT_SET_VERSION = "pilot27-v1"


@dataclass(frozen=True)
class RegisteredRoot:
    root_id: str
    provider: str
    admin_domain_id: str
    workload_identity_id: str


@dataclass(frozen=True)
class VerifiedContribution:
    root_id: str
    admin_domain_id: str
    statement_bytes: bytes
    signature_verified: bool
    provider_identity_verified: bool


def canonical_statement(*, generation: int, root_digest: str, nonce: str,
                        project: str = "setugo", task: str = "exp-o-pilot27") -> bytes:
    obj = {
        "experiment": "EXP-O",
        "pilot": PILOT,
        "project": project,
        "task": task,
        "generation": generation,
        "root_digest": root_digest,
        "purpose": PURPOSE,
        "nonce": nonce,
        "root_set_version": ROOT_SET_VERSION,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def validate_registry(roots: Iterable[RegisteredRoot]) -> dict[str, RegisteredRoot]:
    by_root: dict[str, RegisteredRoot] = {}
    domains: set[str] = set()
    identities: set[str] = set()
    for r in roots:
        if not all((r.root_id, r.provider, r.admin_domain_id, r.workload_identity_id)):
            raise ValueError("incomplete registered root")
        if r.root_id in by_root:
            raise ValueError("duplicate root identity")
        if r.admin_domain_id in domains:
            raise ValueError("administrative domains must be distinct")
        if r.workload_identity_id in identities:
            raise ValueError("workload identity may authorize only one root")
        by_root[r.root_id] = r
        domains.add(r.admin_domain_id)
        identities.add(r.workload_identity_id)
    if len(by_root) != 3:
        raise ValueError("Pilot 27 requires exactly three registered roots")
    return by_root


def _parse_exact_statement(raw: bytes) -> dict | None:
    try:
        obj = json.loads(raw)
    except Exception:
        return None
    exact = (
        isinstance(obj, dict)
        and obj.get("experiment") == "EXP-O"
        and obj.get("pilot") == PILOT
        and obj.get("project") == "setugo"
        and obj.get("task") == "exp-o-pilot27"
        and obj.get("purpose") == PURPOSE
        and obj.get("root_set_version") == ROOT_SET_VERSION
        and isinstance(obj.get("generation"), int)
        and isinstance(obj.get("root_digest"), str)
        and isinstance(obj.get("nonce"), str)
    )
    return obj if exact else None


def evaluate_verified_contributions(
    contributions: Iterable[VerifiedContribution],
    registry: Mapping[str, RegisteredRoot],
    *,
    trusted_min_generation: int = 0,
) -> dict:
    groups: dict[str, dict] = {}
    rejected: list[dict] = []

    for index, c in enumerate(contributions):
        reg = registry.get(c.root_id)
        if reg is None:
            rejected.append({"index": index, "reason": "UNREGISTERED_ROOT"})
            continue
        if c.admin_domain_id != reg.admin_domain_id:
            rejected.append({"index": index, "root_id": c.root_id, "reason": "DOMAIN_BINDING_MISMATCH"})
            continue
        if not c.provider_identity_verified:
            rejected.append({"index": index, "root_id": c.root_id, "reason": "PROVIDER_IDENTITY_UNVERIFIED"})
            continue
        if not c.signature_verified:
            rejected.append({"index": index, "root_id": c.root_id, "reason": "SIGNATURE_INVALID"})
            continue
        obj = _parse_exact_statement(c.statement_bytes)
        if obj is None:
            rejected.append({"index": index, "root_id": c.root_id, "reason": "STATEMENT_SCOPE_INVALID"})
            continue
        if obj["generation"] < trusted_min_generation:
            rejected.append({"index": index, "root_id": c.root_id, "reason": "STALE_GENERATION"})
            continue

        h = sha256(c.statement_bytes).hexdigest()
        g = groups.setdefault(h, {"domains": set(), "roots": set(), "statement": obj})
        # Distinctness is by administrative domain; multiple signatures from one
        # domain cannot increase threshold even if the root labels differ.
        g["domains"].add(reg.admin_domain_id)
        g["roots"].add(reg.root_id)

    winners = []
    for h, g in groups.items():
        if len(g["domains"]) >= 2:
            winners.append({
                "statement_hash": h,
                "domains": sorted(g["domains"]),
                "roots": sorted(g["roots"]),
                "statement": g["statement"],
            })
    winners.sort(key=lambda x: x["statement_hash"])
    return {
        "quorum": len(winners) == 1,
        "winners": winners,
        "rejected": rejected,
        "group_domain_counts": {h: len(g["domains"]) for h, g in groups.items()},
        "model_authority_effect": False,
        "authoritative_platform_effect_count": 0,
    }
