from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from test_v24_v6_proof_reference_closure import proof_bundle

TRUSTED_ROOT = Path("/opt/v24-v6-trusted-runtime")
GATE = TRUSTED_ROOT / ".gate-build" / "v24_v6_external_authority_gate"
GATE_ID = "V24-V6-EXTERNAL-AUTHORITY-GATE"
GATE_VERSION = "1"

UNKNOWN_REFERENCE = "f" * 64
EXPECTED_ID = "SUCCESSOR7-ATTACK-SUBJECT"
EXPECTED_DIGEST = "a" * 64

PRELOAD_SOURCE = r"""
#define _GNU_SOURCE
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

static const char *FORGED_WORKER =
"import json,sys;"
"op,cp,bp,ref,eid,edig=sys.argv[1:7];"
"c=json.load(open(cp,encoding='utf-8'));"
"s=c.get('genesis_trusted_scope') or {};"
"o={'authority_effect':'NONE_EVIDENCE_ONLY','construction_diagnostic_only':True,"
"'input_binding':{'context_digest':c.get('context_digest'),"
"'genesis_trusted_scope_digest':s.get('scope_digest'),"
"'governance_generation_id':c.get('governance_generation_id'),"
"'expected_digest':edig,'expected_id':eid},"
"'problems':[],'qualified':True,'reference_digest':ref,"
"'resolved_digests':[ref],'state':'PROOF_REFERENCE_CLOSED'};"
"print(json.dumps(o,sort_keys=True,separators=(',',':')))";

int execve(const char *pathname, char *const argv[], char *const envp[]) {
    if (pathname &&
        strcmp(pathname, "/usr/bin/python3") == 0 &&
        argv && argv[1] && argv[2] && argv[3] && argv[4] &&
        strcmp(argv[1], "-E") == 0 &&
        strcmp(argv[2], "-s") == 0 &&
        strstr(argv[3], "v24_v6_external_gate_worker.py") != 0) {
        char *replacement[] = {
            "/usr/bin/python3",
            "-c",
            (char *)FORGED_WORKER,
            argv[4],
            argv[5],
            argv[6],
            argv[7],
            argv[8],
            argv[9],
            0
        };
        return (int)syscall(SYS_execve, pathname, replacement, envp);
    }
    return (int)syscall(SYS_execve, pathname, argv, envp);
}
"""


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


def _run_gate(context: dict, boundary: dict, *, preload: Path | None = None):
    with tempfile.TemporaryDirectory() as td:
        context_path, boundary_path = _write_bundle(Path(td), context, boundary)
        env = os.environ.copy()
        if preload is not None:
            env["LD_PRELOAD"] = str(preload)
        proc = subprocess.run(
            [
                str(GATE),
                "resolve-governed",
                str(context_path),
                str(boundary_path),
                UNKNOWN_REFERENCE,
                EXPECTED_ID,
                EXPECTED_DIGEST,
                GATE_ID,
                GATE_VERSION,
                "enforce",
            ],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
    payload = json.loads(proc.stdout.strip())
    return proc, payload


class Successor7CandidateLoaderInjectionRed(unittest.TestCase):
    def test_candidate_ld_preload_cannot_forge_authoritative_allow(self):
        self.assertNotEqual(os.geteuid(), 0)
        context, boundary, _ = proof_bundle()

        baseline_proc, baseline = _run_gate(context, boundary)
        self.assertNotEqual(baseline_proc.returncode, 0, baseline)
        self.assertEqual(baseline["decision"], "DENY")

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source = td_path / "attack.c"
            library = td_path / "libv24_gate_attack.so"
            source.write_text(textwrap.dedent(PRELOAD_SOURCE), encoding="utf-8")
            subprocess.run(
                [
                    "gcc",
                    "-shared",
                    "-fPIC",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    str(source),
                    "-o",
                    str(library),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            attacked_proc, attacked = _run_gate(context, boundary, preload=library)

        self.assertFalse(
            attacked_proc.returncode == 0
            and attacked.get("construction_authoritative") is True
            and attacked.get("decision") == "ALLOW",
            attacked,
        )


if __name__ == "__main__":
    unittest.main()
