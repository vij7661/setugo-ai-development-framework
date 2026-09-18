from __future__ import annotations

import base64
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import v24_v6_proof_reference_closure as prc
import v24_v6_root_attestation as root_attestation
from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle
from test_v24_v6_successor4_external_anchor_red import (
    TARGET_CONTENT,
    attacker_constructed_bundle,
)

RUNTIME_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = RUNTIME_DIR / "build_v24_v6_external_authority_gate.sh"
GATE = RUNTIME_DIR / ".gate-build" / "v24_v6_external_authority_gate"
GATE_ID = "V24-V6-EXTERNAL-AUTHORITY-GATE"
GATE_VERSION = "1"


def _write_bundle(directory: Path, context: dict, boundary: dict) -> tuple[Path, Path]:
    context_path = directory / "context.json"
    boundary_path = directory / "boundary.json"
    context_path.write_text(
        json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    boundary_path.write_text(
        json.dumps(boundary, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return context_path, boundary_path


def _run_gate(
    context: dict,
    boundary: dict,
    reference: str,
    *,
    expected_id: str,
    expected_digest: str,
    gate_path: Path = GATE,
    required_gate_id: str = GATE_ID,
    required_gate_version: str = GATE_VERSION,
) -> tuple[subprocess.CompletedProcess[str], dict]:
    with tempfile.TemporaryDirectory() as td:
        context_path, boundary_path = _write_bundle(Path(td), context, boundary)
        proc = subprocess.run(
            [
                str(gate_path),
                "resolve-governed",
                str(context_path),
                str(boundary_path),
                reference,
                expected_id,
                expected_digest,
                required_gate_id,
                required_gate_version,
                "enforce",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
    payload = json.loads(proc.stdout.strip())
    return proc, payload


def _attacker_signed_boundary(context: dict, boundary: dict, directory: Path) -> tuple[dict, int]:
    key_path = directory / "attacker-key.pem"
    material_path = directory / "attestation.json"
    signature_path = directory / "attestation.sig"

    subprocess.run(
        [
            "openssl",
            "genpkey",
            "-algorithm",
            "RSA",
            "-pkeyopt",
            "rsa_keygen_bits:2048",
            "-out",
            str(key_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    modulus_output = subprocess.run(
        ["openssl", "rsa", "-in", str(key_path), "-noout", "-modulus"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    attacker_modulus = int(modulus_output.split("=", 1)[1], 16)

    generation = boundary["governance_generation_id"]
    context_digest = boundary["expected_proof_context_digest"]
    scope_digest = boundary["expected_genesis_scope_digest"]
    material = root_attestation.canonical_attestation_bytes(
        governance_generation_id=generation,
        proof_context_digest=context_digest,
        genesis_trusted_scope_digest=scope_digest,
    )
    material_path.write_bytes(material)
    subprocess.run(
        [
            "openssl",
            "dgst",
            "-sha256",
            "-sign",
            str(key_path),
            "-out",
            str(signature_path),
            str(material_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    signed = copy.deepcopy(boundary)
    signed["root_attestation"] = {
        "schema_version": root_attestation.ROOT_ATTESTATION_SCHEMA_VERSION,
        "key_id": root_attestation.ROOT_ATTESTATION_KEY_ID,
        "algorithm": root_attestation.ROOT_ATTESTATION_ALGORITHM,
        "purpose": root_attestation.ROOT_ATTESTATION_PURPOSE,
        "governance_generation_id": generation,
        "proof_context_digest": context_digest,
        "genesis_trusted_scope_digest": scope_digest,
        "signature_b64": base64.b64encode(signature_path.read_bytes()).decode("ascii"),
    }
    return signed, attacker_modulus


def _fake_attestation(boundary: dict) -> dict:
    forged = copy.deepcopy(boundary)
    forged["root_attestation"] = {
        "schema_version": root_attestation.ROOT_ATTESTATION_SCHEMA_VERSION,
        "key_id": root_attestation.ROOT_ATTESTATION_KEY_ID,
        "algorithm": root_attestation.ROOT_ATTESTATION_ALGORITHM,
        "purpose": root_attestation.ROOT_ATTESTATION_PURPOSE,
        "governance_generation_id": boundary["governance_generation_id"],
        "proof_context_digest": boundary["expected_proof_context_digest"],
        "genesis_trusted_scope_digest": boundary["expected_genesis_scope_digest"],
        "signature_b64": base64.b64encode(b"\x01" * 256).decode("ascii"),
    }
    return forged


class Successor5ExternalAuthorityGateRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["bash", str(BUILD_SCRIPT)],
            cwd=RUNTIME_DIR,
            check=True,
            text=True,
            capture_output=True,
        )
        identity = json.loads(
            subprocess.run(
                [str(GATE), "--identity"],
                check=True,
                text=True,
                capture_output=True,
            ).stdout
        )
        assert identity["gate_id"] == GATE_ID
        assert identity["gate_version"] == GATE_VERSION
        assert len(identity["build_input_sha256"]) == 64

    def test_same_process_imported_verifier_substitution_rejected(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()
        original = prc.validate_root_attestation
        try:
            prc.validate_root_attestation = lambda *args, **kwargs: []
            local = prc.resolve_governed_qualification(
                leaf_ref,
                context,
                boundary,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=TARGET_CONTENT,
            )
            self.assertTrue(local["qualified"], local)

            proc, authoritative = _run_gate(
                context,
                boundary,
                leaf_ref,
                expected_id="ATTACK-TARGET",
                expected_digest=TARGET_CONTENT,
            )
        finally:
            prc.validate_root_attestation = original

        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(authoritative["decision"], "DENY")
        self.assertTrue(authoritative["construction_authoritative"])

    def test_same_process_root_key_substitution_rejected(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()
        with tempfile.TemporaryDirectory() as td:
            signed, attacker_modulus = _attacker_signed_boundary(
                context, boundary, Path(td)
            )

        original_modulus = root_attestation._RSA_MODULUS
        original_exponent = root_attestation._RSA_PUBLIC_EXPONENT
        try:
            root_attestation._RSA_MODULUS = attacker_modulus
            root_attestation._RSA_PUBLIC_EXPONENT = 65537
            local = prc.resolve_governed_qualification(
                leaf_ref,
                context,
                signed,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=TARGET_CONTENT,
            )
            self.assertTrue(local["qualified"], local)

            proc, authoritative = _run_gate(
                context,
                signed,
                leaf_ref,
                expected_id="ATTACK-TARGET",
                expected_digest=TARGET_CONTENT,
            )
        finally:
            root_attestation._RSA_MODULUS = original_modulus
            root_attestation._RSA_PUBLIC_EXPONENT = original_exponent

        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(authoritative["decision"], "DENY")
        self.assertEqual(authoritative["reason"], "ROOT_ATTESTATION_SIGNATURE_INVALID")

    def test_same_process_rsa_helper_substitution_rejected(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()
        forged = _fake_attestation(boundary)

        original = root_attestation._rsa_pkcs1_v1_5_sha256_verify
        try:
            root_attestation._rsa_pkcs1_v1_5_sha256_verify = lambda *args, **kwargs: True
            local = prc.resolve_governed_qualification(
                leaf_ref,
                context,
                forged,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=TARGET_CONTENT,
            )
            self.assertTrue(local["qualified"], local)

            proc, authoritative = _run_gate(
                context,
                forged,
                leaf_ref,
                expected_id="ATTACK-TARGET",
                expected_digest=TARGET_CONTENT,
            )
        finally:
            root_attestation._rsa_pkcs1_v1_5_sha256_verify = original

        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(authoritative["decision"], "DENY")
        self.assertEqual(authoritative["reason"], "ROOT_ATTESTATION_SIGNATURE_INVALID")

    def test_direct_python_qualified_is_nonauthoritative(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()
        original = prc.validate_root_attestation
        try:
            prc.validate_root_attestation = lambda *args, **kwargs: []
            local = prc.resolve_governed_qualification(
                leaf_ref,
                context,
                boundary,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=TARGET_CONTENT,
            )
        finally:
            prc.validate_root_attestation = original

        self.assertTrue(local["qualified"], local)
        self.assertEqual(local["authority_effect"], "NONE_EVIDENCE_ONLY")

        proc, authoritative = _run_gate(
            context,
            boundary,
            leaf_ref,
            expected_id="ATTACK-TARGET",
            expected_digest=TARGET_CONTENT,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(authoritative["decision"], "DENY")

    def test_forged_external_verdict_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            forged = Path(td) / "forged-verdict.json"
            forged.write_text(
                json.dumps(
                    {
                        "construction_authoritative": True,
                        "decision": "ALLOW",
                        "gate_id": GATE_ID,
                        "gate_version": GATE_VERSION,
                    }
                ),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [str(GATE), "consume-verdict", str(forged)],
                text=True,
                capture_output=True,
                check=False,
            )
        payload = json.loads(proc.stdout)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(payload["decision"], "DENY")
        self.assertEqual(payload["reason"], "CALLER_SUPPLIED_VERDICT_UNSUPPORTED")

    def test_verdict_context_rebind_rejected(self):
        context, boundary, refs = proof_bundle()
        rebound = copy.deepcopy(context)
        rebound["proof_context_id"] = "CTX-REBIND-ATTACK"
        prc.seal_proof_context(rebound)

        proc, payload = _run_gate(
            rebound,
            boundary,
            refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(payload["decision"], "DENY")
        self.assertEqual(payload["reason"], "EXTERNAL_CONTEXT_DIGEST_MISMATCH")

    def test_verdict_scope_or_generation_rebind_rejected(self):
        context, boundary, refs = proof_bundle()
        rebound = copy.deepcopy(context)
        rebound["governance_generation_id"] = "GEN-V24-REBIND"
        prc.seal_proof_context(rebound)

        proc, payload = _run_gate(
            rebound,
            boundary,
            refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(payload["decision"], "DENY")
        self.assertEqual(payload["reason"], "PROOF_CONTEXT_GENERATION_MISMATCH")

    def test_verifier_identity_version_rebind_rejected(self):
        context, boundary, refs = proof_bundle()
        proc, payload = _run_gate(
            context,
            boundary,
            refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
            required_gate_version="0",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(payload["reason"], "VERIFIER_VERSION_MISMATCH")

    def test_external_gate_failure_fails_closed(self):
        context, boundary, refs = proof_bundle()
        with tempfile.TemporaryDirectory() as td:
            relocated = Path(td) / GATE.name
            shutil.copy2(GATE, relocated)
            relocated.chmod(0o555)
            proc, payload = _run_gate(
                context,
                boundary,
                refs["root"],
                expected_id="ROOT-VERIFIER",
                expected_digest=ROOT_CONTENT,
                gate_path=relocated,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(payload["decision"], "DENY")
        self.assertEqual(payload["reason"], "PINNED_SOURCE_DIGEST_MISMATCH")

    def test_externally_verified_signed_context_positive(self):
        context, boundary, refs = proof_bundle()
        proc, payload = _run_gate(
            context,
            boundary,
            refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertTrue(payload["construction_authoritative"])
        self.assertEqual(payload["gate_id"], GATE_ID)
        self.assertEqual(payload["gate_version"], GATE_VERSION)
        self.assertEqual(payload["context_digest"], context["context_digest"])
        self.assertEqual(
            payload["scope_digest"],
            context["genesis_trusted_scope"]["scope_digest"],
        )


if __name__ == "__main__":
    unittest.main()
