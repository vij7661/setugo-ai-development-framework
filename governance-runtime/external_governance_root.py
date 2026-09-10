#!/usr/bin/env python3
"""Pinned external governance-root resolver for TESTING authority verification.

The authoritative Ed25519 public key is held in a separate public, archived GitHub
repository and fetched from an exact commit. This module contains no private key
and grants no authority by itself.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping
from urllib.request import Request, urlopen

EXTERNAL_REPOSITORY = "vij7661/setugo-governance-root"
EXTERNAL_REPOSITORY_ID = 1363676838
EXTERNAL_ROOT_COMMIT = "5f470774ec8c17f5519da8db2aaae59af114cef9"
TRUST_ROOT_ID = "SETUGO_MANUAL_GOVERNANCE_ED25519_V1"
TRUST_ROOT_METADATA_PATH = f"trust-roots/{TRUST_ROOT_ID}.json"
TRUST_ROOT_PEM_PATH = f"trust-roots/{TRUST_ROOT_ID}.pem"
EXPECTED_PUBLIC_KEY_DER_SHA256 = "2b1b97ab0bf99e71f4a93f51fd8e6c3eb30063d83ba2eb4c091492a95f9c11f2"


class ExternalGovernanceRootError(RuntimeError):
    pass


def validate_repository_metadata(payload: Mapping[str, Any]) -> tuple[bool, str]:
    if payload.get("id") != EXTERNAL_REPOSITORY_ID:
        return False, "external governance-root repository id mismatch"
    if payload.get("full_name") != EXTERNAL_REPOSITORY:
        return False, "external governance-root repository identity mismatch"
    if payload.get("private") is not False:
        return False, "external governance-root repository must be public"
    if payload.get("archived") is not True:
        return False, "external governance-root repository is not archived"
    return True, "external governance-root repository is public and archived"


def validate_root_metadata(payload: Mapping[str, Any]) -> tuple[bool, str]:
    expected = {
        "schema_version": 1,
        "trust_root_id": TRUST_ROOT_ID,
        "algorithm": "Ed25519",
        "public_key_path": TRUST_ROOT_PEM_PATH,
        "public_key_der_sha256": EXPECTED_PUBLIC_KEY_DER_SHA256,
        "authority_scope": "TESTING_MANUAL_GOVERNANCE_ATTESTATION_VERIFICATION_ONLY",
        "private_key_location": "EXTERNAL_OFF_REPOSITORY_USER_CONTROLLED",
        "private_key_must_never_be_committed": True,
        "authority_effect": "NONE_BY_ITSELF",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            return False, f"external governance-root metadata mismatch: {key}"
    return True, "external governance-root metadata matches frozen contract"


def public_key_der_sha256(pem_bytes: bytes) -> str:
    try:
        with tempfile.TemporaryDirectory(prefix="setugo-external-root-") as td:
            pem_path = Path(td) / "root.pem"
            der_path = Path(td) / "root.der"
            pem_path.write_bytes(pem_bytes)
            result = subprocess.run(
                ["openssl", "pkey", "-pubin", "-in", str(pem_path), "-outform", "DER", "-out", str(der_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                check=False,
            )
            if result.returncode != 0:
                raise ExternalGovernanceRootError("external governance-root PEM is not a valid public key")
            return hashlib.sha256(der_path.read_bytes()).hexdigest()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ExternalGovernanceRootError(
            f"external governance-root fingerprint verifier unavailable: {type(exc).__name__}"
        ) from exc


def validate_public_key_bytes(pem_bytes: bytes) -> tuple[bool, str]:
    if not isinstance(pem_bytes, (bytes, bytearray)) or not pem_bytes:
        return False, "external governance-root PEM is missing"
    try:
        fingerprint = public_key_der_sha256(bytes(pem_bytes))
    except ExternalGovernanceRootError as exc:
        return False, str(exc)
    if fingerprint != EXPECTED_PUBLIC_KEY_DER_SHA256:
        return False, "external governance-root public key fingerprint mismatch"
    return True, "external governance-root public key fingerprint matches frozen contract"


def _fetch_json(url: str) -> Mapping[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "setugo-external-governance-root",
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read()
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ExternalGovernanceRootError(
            f"unable to retrieve external governance-root metadata: {type(exc).__name__}"
        ) from exc
    if not isinstance(payload, Mapping):
        raise ExternalGovernanceRootError("external governance-root metadata is malformed")
    return payload


def _fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "setugo-external-governance-root"})
    try:
        with urlopen(request, timeout=10) as response:
            return response.read()
    except Exception as exc:
        raise ExternalGovernanceRootError(
            f"unable to retrieve external governance-root material: {type(exc).__name__}"
        ) from exc


def fetch_external_public_key() -> bytes:
    repo = _fetch_json(f"https://api.github.com/repos/{EXTERNAL_REPOSITORY}")
    ok, reason = validate_repository_metadata(repo)
    if not ok:
        raise ExternalGovernanceRootError(reason)

    base = f"https://raw.githubusercontent.com/{EXTERNAL_REPOSITORY}/{EXTERNAL_ROOT_COMMIT}"
    metadata = _fetch_json(
        f"https://api.github.com/repos/{EXTERNAL_REPOSITORY}/contents/{TRUST_ROOT_METADATA_PATH}?ref={EXTERNAL_ROOT_COMMIT}"
    )
    # Contents API wraps text as base64; use raw endpoint for the canonical metadata bytes.
    metadata_raw = _fetch_bytes(f"{base}/{TRUST_ROOT_METADATA_PATH}")
    try:
        metadata_payload = json.loads(metadata_raw.decode("utf-8"))
    except Exception as exc:
        raise ExternalGovernanceRootError("external governance-root metadata file is malformed") from exc
    if not isinstance(metadata_payload, Mapping):
        raise ExternalGovernanceRootError("external governance-root metadata file is not an object")
    ok, reason = validate_root_metadata(metadata_payload)
    if not ok:
        raise ExternalGovernanceRootError(reason)
    # Require the API lookup itself to resolve the expected path at the exact commit.
    if metadata.get("sha") != "882178e631b98903de872c04aaa23c67b80a75ed":
        raise ExternalGovernanceRootError("external governance-root metadata blob mismatch")

    pem = _fetch_bytes(f"{base}/{TRUST_ROOT_PEM_PATH}")
    ok, reason = validate_public_key_bytes(pem)
    if not ok:
        raise ExternalGovernanceRootError(reason)
    return pem
