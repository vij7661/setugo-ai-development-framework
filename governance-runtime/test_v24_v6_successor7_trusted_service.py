from __future__ import annotations

import copy
import inspect
import json
import os
import signal
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

import v24_v6_decision_apply as decision_apply
import v24_v6_material_surface as material_surface
import v24_v6_normative_clause_projection as normative_projection
from test_v24_v6_decision_apply import attach_proofs as attach_decision_proofs, bundle as decision_bundle
from test_v24_v6_normative_clause_projection import DISPOSITION_SET_ID, coverage_fixture
from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle
from v24_v6_trusted_service_client import SERVICE_SOCKET, request_service

SERVICE_PID = Path("/run/v24-v6-authority/service.pid")
SERVICE_PRIVATE = Path("/run/v24-v6-authority/private")
UNKNOWN_REFERENCE = "f" * 64
EXPECTED_ID = "SUCCESSOR7-ATTACK-SUBJECT"
EXPECTED_DIGEST = "a" * 64

PRELOAD_SOURCE = r"""
#define _GNU_SOURCE
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

int execve(const char *pathname, char *const argv[], char *const envp[]) {
    if (pathname && strcmp(pathname, "/usr/bin/python3") == 0) {
        return (int)syscall(SYS_execve, pathname, argv, envp);
    }
    return (int)syscall(SYS_execve, pathname, argv, envp);
}
"""


def _unknown_request() -> dict:
    context, boundary, _ = proof_bundle()
    return request_service(
        "resolve-governed",
        context=context,
        boundary=boundary,
        reference=UNKNOWN_REFERENCE,
        expected_id=EXPECTED_ID,
        expected_digest=EXPECTED_DIGEST,
    )


def _child_request(env: dict[str, str]) -> dict:
    code = textwrap.dedent(
        """
        import json
        from test_v24_v6_proof_reference_closure import proof_bundle
        from v24_v6_trusted_service_client import request_service
        c,b,_=proof_bundle()
        r=request_service(
            "resolve-governed",
            context=c,
            boundary=b,
            reference="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            expected_id="SUCCESSOR7-ATTACK-SUBJECT",
            expected_digest="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        )
        print(json.dumps(r, sort_keys=True))
        """
    )
    proc = subprocess.run(
        ["/usr/bin/python3", "-c", code],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        raise AssertionError((proc.stdout, proc.stderr))
    return json.loads(proc.stdout.strip())


class Successor7TrustedServiceTests(unittest.TestCase):
    def test_candidate_identity_is_unprivileged_and_service_is_root(self):
        self.assertNotEqual(os.geteuid(), 0)
        self.assertTrue(Path(SERVICE_SOCKET).is_socket())
        pid = int(SERVICE_PID.read_text(encoding="utf-8").strip())
        status = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
        uid_line = next(line for line in status.splitlines() if line.startswith("Uid:"))
        self.assertEqual(int(uid_line.split()[1]), 0)

    def test_trusted_service_positive(self):
        context, boundary, refs = proof_bundle()
        result = request_service(
            "resolve-governed",
            context=context,
            boundary=boundary,
            reference=refs["root"],
            expected_id="ROOT-VERIFIER",
            expected_digest=ROOT_CONTENT,
        )
        self.assertEqual(result["decision"], "ALLOW", result)
        self.assertTrue(result["service_authoritative"])
        self.assertTrue(result["construction_authoritative"])
        self.assertEqual(len(result["request_sha256"]), 64)
        self.assertEqual(len(result["gate_result_sha256"]), 64)

    def test_unknown_reference_is_denied(self):
        result = _unknown_request()
        self.assertEqual(result["decision"], "DENY", result)

    def test_candidate_ld_preload_gate_injection_rejected_by_service(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source = td_path / "attack.c"
            library = td_path / "libv24_s7_attack.so"
            source.write_text(textwrap.dedent(PRELOAD_SOURCE), encoding="utf-8")
            subprocess.run(
                ["gcc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", str(source), "-o", str(library)],
                check=True,
                text=True,
                capture_output=True,
            )
            env = os.environ.copy()
            env["LD_PRELOAD"] = str(library)
            attacked = _child_request(env)
        self.assertEqual(attacked["decision"], "DENY", attacked)

    def test_candidate_ld_library_path_rebind_rejected_by_service(self):
        with tempfile.TemporaryDirectory() as td:
            env = os.environ.copy()
            env["LD_LIBRARY_PATH"] = td
            attacked = _child_request(env)
        self.assertEqual(attacked["decision"], "DENY", attacked)

    def test_candidate_cannot_signal_trusted_service(self):
        pid = int(SERVICE_PID.read_text(encoding="utf-8").strip())
        with self.assertRaises(PermissionError):
            os.kill(pid, signal.SIGUSR1)

    def test_candidate_cannot_access_trusted_private_result_channel(self):
        self.assertTrue(SERVICE_PRIVATE.exists())
        with self.assertRaises(PermissionError):
            list(SERVICE_PRIVATE.iterdir())
        probe = SERVICE_PRIVATE / "candidate-write"
        with self.assertRaises(PermissionError):
            probe.write_text("forged", encoding="utf-8")

    def test_caller_cannot_select_service_executable_worker_or_root(self):
        parameters = set(inspect.signature(request_service).parameters)
        self.assertNotIn("service_path", parameters)
        self.assertNotIn("worker_path", parameters)
        self.assertNotIn("trusted_root", parameters)
        self.assertEqual(SERVICE_SOCKET, "/run/v24-v6-authority/service.sock")

    def test_external_service_decision_apply_positive(self):
        payload = decision_bundle()
        context, boundary = attach_decision_proofs(payload)
        source = payload["snapshot_source"]
        result = request_service(
            "evaluate-decision-apply",
            context=context,
            boundary=boundary,
            payload=payload,
            reference=source["qualification_digest"],
            expected_id=source["mechanism_id"],
            expected_digest=source["mechanism_content_digest"],
        )
        self.assertEqual(result["decision"], "ALLOW", result)

    def test_da1_local_self_grant_does_not_cross_service_boundary(self):
        payload = decision_bundle()
        context, boundary = attach_decision_proofs(payload)
        source = payload["snapshot_source"]
        payload["decision"]["authorized_effect_path_id"] = "PATH-ATTACK"
        payload["material_effect_path"]["path_id"] = "PATH-ATTACK"
        payload["decision"]["decision_digest"] = decision_apply.canonical_decision_content_digest(
            payload["decision"]
        )

        original_da = decision_apply.close_governance_dependencies
        original_material = material_surface.close_governance_dependencies
        try:
            forged_close = lambda *args, **kwargs: {
                "qualified": True,
                "state": "PROOF_REFERENCE_CLOSED",
                "problems": [],
                "authority_effect": "NONE_EVIDENCE_ONLY",
            }
            decision_apply.close_governance_dependencies = forged_close
            material_surface.close_governance_dependencies = forged_close
            local = decision_apply.evaluate_decision_apply_latch(
                payload, proof_context=context, trusted_boundary=boundary
            )
            self.assertTrue(local["allowed"], local)
        finally:
            decision_apply.close_governance_dependencies = original_da
            material_surface.close_governance_dependencies = original_material

        result = request_service(
            "evaluate-decision-apply",
            context=context,
            boundary=boundary,
            payload=payload,
            reference=source["qualification_digest"],
            expected_id=source["mechanism_id"],
            expected_digest=source["mechanism_content_digest"],
        )
        self.assertEqual(result["decision"], "DENY", result)

    def test_external_service_normative_coverage_positive(self):
        payload, context, boundary, _ = coverage_fixture()
        result = request_service(
            "validate-normative-coverage",
            context=context,
            boundary=boundary,
            payload=payload,
            reference=payload["disposition_qualification_digest"],
            expected_id=DISPOSITION_SET_ID,
            expected_digest=payload["disposition_digest"],
        )
        self.assertEqual(result["decision"], "ALLOW", result)

    def test_ncp1_local_self_grant_does_not_cross_service_boundary(self):
        payload, context, boundary, _ = coverage_fixture()
        descriptor = payload["catalog_descriptors"][0]
        descriptor["control_id"] = "CTRL-ATTACK"
        descriptor["control_binding_content_digest"] = (
            normative_projection.canonical_catalog_control_binding_digest(descriptor)
        )

        original = normative_projection.close_governance_dependencies
        try:
            normative_projection.close_governance_dependencies = lambda *args, **kwargs: {
                "qualified": True,
                "state": "PROOF_REFERENCE_CLOSED",
                "problems": [],
                "authority_effect": "NONE_EVIDENCE_ONLY",
            }
            local = normative_projection.validate_catalog_candidate_coverage(
                payload, proof_context=context, trusted_boundary=boundary
            )
            self.assertTrue(local["qualified"], local)
        finally:
            normative_projection.close_governance_dependencies = original

        result = request_service(
            "validate-normative-coverage",
            context=context,
            boundary=boundary,
            payload=payload,
            reference=payload["disposition_qualification_digest"],
            expected_id=DISPOSITION_SET_ID,
            expected_digest=payload["disposition_digest"],
        )
        self.assertEqual(result["decision"], "DENY", result)


if __name__ == "__main__":
    unittest.main()
