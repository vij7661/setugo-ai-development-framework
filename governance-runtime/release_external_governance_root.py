#!/usr/bin/env python3
"""Pinned external governance-root resolver for RELEASE terminal authority.

The authoritative RELEASE Ed25519 public key is held in a separate public,
archived GitHub repository and fetched from an exact commit. This module
contains no private key and grants no authority by itself.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping
from urllib.request import Request, urlopen

RELEASE_EXTERNAL_REPOSITORY = "vij7661/setugo-release-governance-root"
RELEASE_EXTERNAL_REPOSITORY_ID = 1364609306
RELEASE_EXTERNAL_ROOT_COMMIT = "7300b9b0d27611bcb5ccc1638fb1d16e53dc5994"
RELEASE_TRUST_ROOT_ID = "SETUGO_RELEASE_GOVERNANCE_ED25519_V1"
RELEASE_TRUST_ROOT_METADATA_PATH = f"trust-roots/{RELEASE_TRUST_ROOT_ID}.json"
RELEASE_TRUST_ROOT_PEM_PATH = f"trust-roots/{RELEASE_TRUST_ROOT_ID}.pem"
RELEASE_EXPECTED_PUBLIC_KEY_DER_SHA256 = "91355cf1049a27aac52ea56f5ba1664054aded93500203cd23d557a710b0444c"
RELEASE_METADATA_BLOB_SHA = "da5c1892307bbf23fb1a3a105e55e8ba215d9065"


class ReleaseExternalGovernanceRootError(RuntimeError):
    pass


def validate_release_repository_metadata(payload: Mapping[str, Any]) -> tuple[bool, str]:
    if payload.get("id") != RELEASE_EXTERNAL_REPOSITORY_ID:
        return False, "release governance-root repository id mismatch"
    if payload.get("full_name") != RELEASE_EXTERNAL_REPOSITORY:
        return False, "release governance-root repository identity mismatch"
    if payload.get("private") is not False:
        return False, "release governance-root repository must be public"
    if payload.get("archived") is not True:
        return False, "release governance-root repository is not archived"
    return True, "release governance-root repository is public and archived"


def validate_release_root_metadata(payload: Mapping[str, Any]) -> tuple[bool, str]:
    expected = {
        "schema_version": 1,
        "trust_root_id": RELEASE_TRUST_ROOT_ID,
        "algorithm": "Ed25519",
        "public_key_path": RELEASE_TRUST_ROOT_PEM_PATH,
        "public_key_der_sha256": RELEASE_EXPECTED_PUBLIC_KEY_DER_SHA256,
        "authority_scope": "RELEASE_TERMINAL_AUTHORITY_ATTESTATION_VERIFICATION_ONLY",
        "permitted_authority_class": "HUMAN_RELEASE_AUTHORITY",
        "permitted_decision_scopes": [
            "TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE",
            "TERMINAL_ACTION:RELEASE:BEGIN_PRODUCTION_QUALIFICATION",
        ],
        "private_key_location": "EXTERNAL_OFF_REPOSITORY_USER_CONTROLLED",
        "private_key_must_never_be_committed": True,
        "authority_effect": "NONE_BY_ITSELF",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            return False, f"release governance-root metadata mismatch: {key}"
    return True, "release governance-root metadata matches frozen contract"


def release_public_key_der_sha256(pem_bytes: bytes) -> str:
    try:
        with tempfile.TemporaryDirectory(prefix="setugo-release-root-") as td:
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
                raise ReleaseExternalGovernanceRootError("release governance-root PEM is not a valid public key")
            return hashlib.sha256(der_path.read_bytes()).hexdigest()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReleaseExternalGovernanceRootError(
            f"release governance-root fingerprint verifier unavailable: {type(exc).__name__}"
        ) from exc


def validate_release_public_key_bytes(pem_bytes: bytes) -> tuple[bool, str]:
    if not isinstance(pem_bytes, (bytes, bytearray)) or not pem_bytes:
        return False, "release governance-root PEM is missing"
    try:
        fingerprint = release_public_key_der_sha256(bytes(pem_bytes))
    except ReleaseExternalGovernanceRootError as exc:
        return False, str(exc)
    if fingerprint != RELEASE_EXPECTED_PUBLIC_KEY_DER_SHA256:
        return False, "release governance-root public key fingerprint mismatch"
    return True, "release governance-root public key fingerprint matches frozen contract"


def _github_api_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "setugo-release-governance-root",
    }
    token = (
        os.environ.get("GOVERNANCE_GITHUB_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_json(url: str) -> Mapping[str, Any]:
    request = Request(url, headers=_github_api_headers())
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read()
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ReleaseExternalGovernanceRootError(
            f"unable to retrieve release governance-root metadata: {type(exc).__name__}"
        ) from exc
    if not isinstance(payload, Mapping):
        raise ReleaseExternalGovernanceRootError("release governance-root metadata is malformed")
    return payload


def _fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "setugo-release-governance-root"})
    try:
        with urlopen(request, timeout=10) as response:
            return response.read()
    except Exception as exc:
        raise ReleaseExternalGovernanceRootError(
            f"unable to retrieve release governance-root material: {type(exc).__name__}"
        ) from exc


def fetch_release_external_public_key() -> bytes:
    repo = _fetch_json(f"https://api.github.com/repos/{RELEASE_EXTERNAL_REPOSITORY}")
    ok, reason = validate_release_repository_metadata(repo)
    if not ok:
        raise ReleaseExternalGovernanceRootError(reason)

    base = f"https://raw.githubusercontent.com/{RELEASE_EXTERNAL_REPOSITORY}/{RELEASE_EXTERNAL_ROOT_COMMIT}"
    metadata = _fetch_json(
        f"https://api.github.com/repos/{RELEASE_EXTERNAL_REPOSITORY}/contents/{RELEASE_TRUST_ROOT_METADATA_PATH}?ref={RELEASE_EXTERNAL_ROOT_COMMIT}"
    )
    metadata_raw = _fetch_bytes(f"{base}/{RELEASE_TRUST_ROOT_METADATA_PATH}")
    try:
        metadata_payload = json.loads(metadata_raw.decode("utf-8"))
    except Exception as exc:
        raise ReleaseExternalGovernanceRootError("release governance-root metadata file is malformed") from exc
    if not isinstance(metadata_payload, Mapping):
        raise ReleaseExternalGovernanceRootError("release governance-root metadata file is not an object")
    ok, reason = validate_release_root_metadata(metadata_payload)
    if not ok:
        raise ReleaseExternalGovernanceRootError(reason)
    if metadata.get("sha") != RELEASE_METADATA_BLOB_SHA:
        raise ReleaseExternalGovernanceRootError("release governance-root metadata blob mismatch")

    pem = _fetch_bytes(f"{base}/{RELEASE_TRUST_ROOT_PEM_PATH}")
    ok, reason = validate_release_public_key_bytes(pem)
    if not ok:
        raise ReleaseExternalGovernanceRootError(reason)
    return pem
