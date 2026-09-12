from __future__ import annotations

import hashlib
import json

TRUST_SOURCE_CLASS = "REFERENCE_REPO_BOUND_SIMULATION_ONLY"
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def _sha256_json(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


_CONFIG_MATERIAL = {
    "tool_id": "t",
    "harness_id": "h",
    "transport": "stdio",
    "endpoint": None,
    "argv": ["x"],
    "permission_profile": "r",
    "credential_profile_fingerprint": "cred-fp",
}

_REFERENCE = {
    "ECC-V5-E1-POS": {
        "kind": "execution",
        "candidate": "shaA",
        "action_id": "act1",
        "control_id": "gate",
        "control_version": 3,
        "control_digest": "c" * 64,
        "process_identity": "hook@pid:trusted",
        "action_sequence": 10,
        "invocation_id": "inv1",
    },
    "ECC-V5-E2-POS": {
        "kind": "equivalence",
        "mode": "BLOCKING",
        "on_internal_error": "DENY",
        "candidate_binding": "EXACT",
        "contract_version": 2,
        "profile_digest": "p2",
        "scope": "ALL",
        "path_count": 1,
    },
    "ECC-V5-E3-POS": {
        "kind": "role",
        "harness_id": "h1",
        "runtime_version": "1",
        "config_digest": "d",
        "runtime_identity_digest": "r" * 64,
        "write_confinement": "NATIVE_ENFORCEMENT",
    },
    "ECC-V5-E4-POS": {
        "kind": "activation",
        "manifest_digest": "m",
        "project_id": "p1",
        "role": "R1",
        "approval_sequence": 7,
        "powers": ["WRITE"],
        "resources": ["repo"],
    },
    "ECC-V5-E5-POS": {
        "kind": "config",
        "tool_id": "t",
        "harness_id": "h",
        "transport": "stdio",
        "endpoint": None,
        "argv_digest": _sha256_json(["x"]),
        "canonical_digest": _sha256_json(_CONFIG_MATERIAL),
        "credential_profile_fingerprint": "cred-fp",
        "resolved_endpoint": "LOCAL_STDIO",
    },
}


def lookup_reference_evidence(kind, evidence_id):
    if not isinstance(evidence_id, str) or not evidence_id:
        return None
    record = _REFERENCE.get(evidence_id)
    if not isinstance(record, dict) or record.get("kind") != kind:
        return None
    return dict(record)
