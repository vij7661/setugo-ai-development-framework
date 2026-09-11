from __future__ import annotations

import base64
from pathlib import Path
import subprocess
import tempfile

from manual_authority_verifier import (
    canonical_attestation_bytes,
    verify_signature_with_explicit_test_key,
)


def _run(*args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def test_ed25519_verifier_accepts_valid_external_signature_and_rejects_tamper():
    attestation = {
        "schema_version": 1,
        "candidate_sha": "a" * 40,
        "authority_class": "HUMAN_GOVERNANCE_OWNER",
        "decision_scope": "ACCEPTANCE_BOUNDARY_APPROVAL",
        "evidence_ref": "test-only",
        "source_kind": "MANUAL_GOVERNANCE_ATTESTATION",
        "qualification_policy_id": "TEST_ONLY",
        "qualification_policy_version": 1,
        "qualification_policy_hash": "b" * 64,
        "trust_root_id": "TEST_ONLY",
    }
    with tempfile.TemporaryDirectory(prefix="setugo-ed25519-test-") as td:
        root = Path(td)
        private_key = root / "private.pem"
        public_key = root / "public.pem"
        payload = root / "payload.json"
        signature = root / "payload.sig"

        _run("openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key))
        _run("openssl", "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key))
        payload.write_bytes(canonical_attestation_bytes(attestation))
        _run(
            "openssl", "pkeyutl", "-sign", "-inkey", str(private_key), "-rawin",
            "-in", str(payload), "-out", str(signature),
        )
        signature_b64 = base64.b64encode(signature.read_bytes()).decode("ascii")

        ok, reason = verify_signature_with_explicit_test_key(attestation, signature_b64, public_key)
        assert ok, reason

        tampered = dict(attestation)
        tampered["candidate_sha"] = "c" * 40
        ok, _ = verify_signature_with_explicit_test_key(tampered, signature_b64, public_key)
        assert not ok


def test_explicit_test_key_hook_does_not_use_production_trust_root():
    attestation = {"test": "payload"}
    with tempfile.TemporaryDirectory(prefix="setugo-ed25519-test-") as td:
        missing = Path(td) / "missing.pem"
        ok, _ = verify_signature_with_explicit_test_key(attestation, "AA==", missing)
        assert not ok
