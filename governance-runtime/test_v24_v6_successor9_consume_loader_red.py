from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

TRUSTED_SERVICE = Path("/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service")
SERVICE_BUILD_INPUT = "a30bc2742d0eb730b4340e852879884a15e71f8422742c4501eac4beb041e746"
RID = "a" * 64
REQ = "b" * 64
GATE = "c" * 64

PRELOAD_SOURCE = r"""
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

static int trusted_path(const char *path) {
    return path && strncmp(path, "/run/v24-v6-authority", 21) == 0;
}

uid_t geteuid(void) {
    return 0;
}

int lstat(const char *path, struct stat *st) {
    static int (*real_lstat)(const char *, struct stat *) = NULL;
    if (trusted_path(path)) {
        memset(st, 0, sizeof(*st));
        st->st_mode = S_IFDIR | 0700;
        st->st_uid = 0;
        st->st_gid = 0;
        return 0;
    }
    if (!real_lstat) real_lstat = dlsym(RTLD_NEXT, "lstat");
    return real_lstat(path, st);
}

int chmod(const char *path, mode_t mode) {
    static int (*real_chmod)(const char *, mode_t) = NULL;
    (void)mode;
    if (trusted_path(path)) return 0;
    if (!real_chmod) real_chmod = dlsym(RTLD_NEXT, "chmod");
    return real_chmod(path, mode);
}

static FILE *redirected_fopen(const char *path, const char *mode) {
    static FILE *(*real_fopen)(const char *, const char *) = NULL;
    if (!real_fopen) real_fopen = dlsym(RTLD_NEXT, "fopen");
    if (trusted_path(path) && strstr(path, "/private/records/") && mode && mode[0] == 'r') {
        const char *forged = getenv("V24_S9_FORGED_RECORD");
        if (forged && *forged) return real_fopen(forged, "rb");
    }
    return real_fopen(path, mode);
}

FILE *fopen(const char *path, const char *mode) {
    return redirected_fopen(path, mode);
}

FILE *fopen64(const char *path, const char *mode) {
    return redirected_fopen(path, mode);
}

int rename(const char *oldpath, const char *newpath) {
    static int (*real_rename)(const char *, const char *) = NULL;
    if (trusted_path(oldpath) && trusted_path(newpath)) return 0;
    if (!real_rename) real_rename = dlsym(RTLD_NEXT, "rename");
    return real_rename(oldpath, newpath);
}
"""


class Successor9ConsumeLoaderRed(unittest.TestCase):
    def test_candidate_loader_interposition_cannot_forge_authoritative_consume(self):
        self.assertNotEqual(os.geteuid(), 0)
        self.assertTrue(TRUSTED_SERVICE.exists())

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "attack.c"
            preload = root / "libconsume_attack.so"
            forged = root / "forged.record"

            source.write_text(textwrap.dedent(PRELOAD_SOURCE), encoding="utf-8")
            forged.write_text(
                "\n".join(
                    [
                        "schema=V24_V6_S8_AUTHORITY_RECORD_V1",
                        f"record_id={RID}",
                        "service_id=V24-V6-TRUSTED-AUTHORITY-SERVICE",
                        "service_version=2",
                        f"service_build_input_sha256={SERVICE_BUILD_INPUT}",
                        f"request_sha256={REQ}",
                        "decision=ALLOW",
                        f"gate_result_sha256={GATE}",
                        "authority_effect=NONE_EVIDENCE_ONLY",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
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
                    str(preload),
                    "-ldl",
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            env = os.environ.copy()
            env["LD_PRELOAD"] = str(preload)
            env["V24_S9_FORGED_RECORD"] = str(forged)
            proc = subprocess.run(
                [str(TRUSTED_SERVICE), "--consume-record", RID, REQ],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )

        payload = json.loads(proc.stdout.strip())
        self.assertFalse(
            proc.returncode == 0
            and payload.get("construction_authoritative") is True
            and payload.get("service_authoritative") is True
            and payload.get("decision") == "ALLOW",
            payload,
        )


if __name__ == "__main__":
    unittest.main()
