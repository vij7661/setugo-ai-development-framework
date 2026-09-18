"""Deterministic test-only proof context factory for V24 V6 repair tests.

This module is fixture infrastructure only.  Production modules must never import
it or synthesize qualifications to make an authority decision pass.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    seal_proof_context,
)
from v24_v6_root_attestation import (
    ROOT_ATTESTATION_ALGORITHM,
    ROOT_ATTESTATION_KEY_ID,
    ROOT_ATTESTATION_PURPOSE,
    ROOT_ATTESTATION_SCHEMA_VERSION,
)

ROOT_CONTENT = "f0" * 32
D1 = "01" * 32
D2 = "02" * 32
D3 = "03" * 32
D4 = "04" * 32
D5 = "05" * 32
D6 = "06" * 32
D7 = "07" * 32
D8 = "08" * 32
D9 = "09" * 32


def _seal(record: dict[str, Any], field: str) -> dict[str, Any]:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def _currentness(source_id: str, source_digest: str, verifier_ref: str) -> dict[str, Any]:
    return _seal(
        {
            "currentness_rule_id": "TEST-CURRENTNESS-RULE",
            "source_object_id": source_id,
            "source_version_or_sequence": "1",
            "source_digest": source_digest,
            "observed_at_sequence": 1,
            "verifier_qualification_digest": verifier_ref,
            "result": CURRENT,
            "binding_digest": "",
        },
        "binding_digest",
    )


def _scope() -> dict[str, Any]:
    trusted = [{"object_id": "TEST-ROOT-VERIFIER", "content_digest": ROOT_CONTENT}]
    return _seal(
        {
            "governance_generation_id": "GEN-V24-TEST-PROOF",
            "genesis_record_digest": D1,
            "root_kernel_digest": D2,
            "trusted_objects": trusted,
            "trusted_object_pair_set_digest": digest(trusted),
            "permitted_bootstrap_roles": ["TEST_BOOTSTRAP_VERIFIER"],
            "residual_trust_reason_ids": ["TEST_GENESIS_ROOT"],
            "creation_ceremony_digest": D3,
            "durable_anchor_digest": D4,
            "scope_digest": "",
        },
        "scope_digest",
    )


def _root_qualification() -> dict[str, Any]:
    return _seal(
        {
            "qualification_id": "TEST-Q-ROOT",
            "subject_object_id": "TEST-ROOT-VERIFIER",
            "subject_content_digest": ROOT_CONTENT,
            "subject_kind": "VERIFIER",
            "subject_owner_id": "TEST-ROOT-OWNER",
            "qualification_authority_id": "TEST-ROOT-AUTHORITY",
            "authority_member_ids": ["TEST-ROOT-MEMBER"],
            "authority_control_domain_ids": ["TEST-ROOT-DOMAIN"],
            "independence_qualification_digests": [D5],
            "evidence_record_digests": [D6],
            "evidence_class_ids": ["TEST-ROOT-EVIDENCE"],
            "verifier_mechanism_id": "TEST-BOOTSTRAP-VERIFIER",
            "verifier_mechanism_qualification_digest": D7,
            "currentness_bindings": [
                _currentness("TEST-ROOT-VERIFIER", ROOT_CONTENT, D8)
            ],
            "result": QUALIFIED,
            "proof_digest": D9,
            "qualification_digest": "",
        },
        "qualification_digest",
    )


def _independence(subject_identity_id: str, root_ref: str, suffix: str) -> dict[str, Any]:
    return _seal(
        {
            "independence_qualification_id": f"TEST-IND-{suffix}",
            "independence_rule_id": "TEST-INDEPENDENCE-RULE",
            "subject_identity_id": subject_identity_id,
            "subject_control_closure": [f"ORG:{subject_identity_id}", f"KMS:{subject_identity_id}"],
            "counterparties": [
                {
                    "identity_id": f"TEST-EXTERNAL-{suffix}",
                    "control_closure": [f"ORG:EXTERNAL:{suffix}", f"KMS:EXTERNAL:{suffix}"],
                }
            ],
            "shared_control_intersections": [],
            "evidence_record_digests": [D1],
            "currentness_bindings": [
                _currentness(f"IND-EVIDENCE:{suffix}", D2, root_ref)
            ],
            "result": QUALIFIED,
            "verifier_qualification_digest": root_ref,
            "qualification_digest": "",
        },
        "qualification_digest",
    )


def _qualification(
    subject_id: str,
    content_digest: str,
    root_ref: str,
    independence_ref: str,
    suffix: str,
) -> dict[str, Any]:
    return _seal(
        {
            "qualification_id": f"TEST-Q-{suffix}",
            "subject_object_id": subject_id,
            "subject_content_digest": content_digest,
            "subject_kind": "TEST_AUTHORITY_BEARING_OBJECT",
            "subject_owner_id": f"TEST-OWNER-{suffix}",
            "qualification_authority_id": "TEST-SHARED-AUTHORITY",
            "authority_member_ids": ["TEST-SHARED-MEMBER"],
            "authority_control_domain_ids": ["TEST-SHARED-DOMAIN"],
            "independence_qualification_digests": [independence_ref],
            "evidence_record_digests": [D3],
            "evidence_class_ids": ["TEST-EVIDENCE-CLASS"],
            "verifier_mechanism_id": "TEST-ROOT-VERIFIER",
            "verifier_mechanism_qualification_digest": root_ref,
            "currentness_bindings": [
                _currentness(subject_id, content_digest, root_ref)
            ],
            "result": QUALIFIED,
            "proof_digest": D4,
            "qualification_digest": "",
        },
        "qualification_digest",
    )


def _wrap(kind: str, record: Mapping[str, Any]) -> dict[str, Any]:
    field = "binding_digest" if kind == CURRENTNESS_BINDING else "qualification_digest"
    return {
        "record_kind": kind,
        "record_digest": record[field],
        "record": dict(record),
    }



def record_test_attestation_inventory(
    context: Mapping[str, Any],
    boundary: Mapping[str, Any],
) -> None:
    """Persist unsigned deterministic context material for external signing.

    Inventory mode contains no signing key and grants no authority. It exists
    only so an out-of-process signer can attest the exact construction contexts
    later without exposing private key material to candidate/test Python.
    """
    directory = os.environ.get("V24_V6_ATTESTATION_INVENTORY_DIR")
    if not directory:
        return
    context_digest = context.get("context_digest")
    if not isinstance(context_digest, str) or len(context_digest) != 64:
        raise ValueError("attestation inventory requires sealed context_digest")
    payload = {
        "proof_context": context,
        "trusted_boundary": boundary,
    }
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"{context_digest}.json"
    target.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

_SIGNATURE_BUNDLE_PATH = (
    Path(__file__).with_name("fixtures")
    / "v24-v6-construction-context-signatures-v3.json"
)


def _construction_signature(context_digest: str) -> str:
    bundle = json.loads(_SIGNATURE_BUNDLE_PATH.read_text(encoding="utf-8"))
    if bundle.get("key_id") != ROOT_ATTESTATION_KEY_ID:
        raise ValueError("construction signature bundle key mismatch")
    if bundle.get("algorithm") != ROOT_ATTESTATION_ALGORITHM:
        raise ValueError("construction signature bundle algorithm mismatch")
    if bundle.get("purpose") != ROOT_ATTESTATION_PURPOSE:
        raise ValueError("construction signature bundle purpose mismatch")
    signatures = bundle.get("signatures")
    if not isinstance(signatures, dict):
        raise ValueError("construction signature bundle malformed")
    signature = signatures.get(context_digest)
    if not isinstance(signature, str) or not signature:
        raise ValueError(
            f"no external construction attestation for context {context_digest}"
        )
    return signature


def attested_boundary_for_test(context: Mapping[str, Any]) -> dict[str, Any]:
    """Bind an exact deterministic fixture to its externally issued signature."""
    scope = context.get("genesis_trusted_scope")
    scope_digest = scope.get("scope_digest") if isinstance(scope, Mapping) else None
    context_digest = context.get("context_digest")
    generation = context.get("governance_generation_id")
    if not isinstance(context_digest, str):
        raise ValueError("sealed context_digest required")
    if not isinstance(scope_digest, str):
        raise ValueError("sealed genesis scope digest required")
    if not isinstance(generation, str):
        raise ValueError("governance generation required")
    boundary = {
        "governance_generation_id": generation,
        "expected_proof_context_digest": context_digest,
        "expected_genesis_scope_digest": scope_digest,
        "root_attestation": {
            "schema_version": ROOT_ATTESTATION_SCHEMA_VERSION,
            "key_id": ROOT_ATTESTATION_KEY_ID,
            "algorithm": ROOT_ATTESTATION_ALGORITHM,
            "purpose": ROOT_ATTESTATION_PURPOSE,
            "governance_generation_id": generation,
            "proof_context_digest": context_digest,
            "genesis_trusted_scope_digest": scope_digest,
            "signature_b64": _construction_signature(context_digest),
        },
    }
    record_test_attestation_inventory(context, boundary)
    return boundary


def build_test_proof_context(
    specs: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """Build exact R1-valid proof records for named test requirements.

    Supported specs:
      QUALIFICATION: {kind, subject_id, content_digest}
      INDEPENDENCE: {kind, subject_identity_id}
      CURRENTNESS: {kind, source_id, source_digest}
    """
    root = _root_qualification()
    root_ref = root["qualification_digest"]
    shared_ind = _independence("TEST-SHARED-AUTHORITY", root_ref, "SHARED")
    shared_ind_ref = shared_ind["qualification_digest"]
    wrappers: list[dict[str, Any]] = [
        _wrap(GOVERNED_QUALIFICATION, root),
        _wrap(INDEPENDENCE_QUALIFICATION, shared_ind),
    ]
    refs: dict[str, str] = {}

    for index, (name, spec) in enumerate(specs.items(), start=1):
        kind = spec.get("kind")
        suffix = f"{index}-{name}"
        if kind == "QUALIFICATION":
            record = _qualification(
                str(spec["subject_id"]),
                str(spec["content_digest"]),
                root_ref,
                shared_ind_ref,
                suffix,
            )
            wrappers.append(_wrap(GOVERNED_QUALIFICATION, record))
            refs[name] = record["qualification_digest"]
        elif kind == "INDEPENDENCE":
            record = _independence(str(spec["subject_identity_id"]), root_ref, suffix)
            wrappers.append(_wrap(INDEPENDENCE_QUALIFICATION, record))
            refs[name] = record["qualification_digest"]
        elif kind == "CURRENTNESS":
            record = _currentness(
                str(spec["source_id"]), str(spec["source_digest"]), root_ref
            )
            wrappers.append(_wrap(CURRENTNESS_BINDING, record))
            refs[name] = record["binding_digest"]
        else:
            raise ValueError(f"unsupported proof fixture kind: {kind}")

    context: dict[str, Any] = {
        "proof_context_id": "TEST-PROOF-CONTEXT",
        "governance_generation_id": "GEN-V24-TEST-PROOF",
        "evidence_records": wrappers,
        "genesis_trusted_scope": _scope(),
        "context_digest": "",
    }
    seal_proof_context(context)
    return context, attested_boundary_for_test(context), refs
