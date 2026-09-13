from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import subprocess
import sys


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_launcher_runtime() -> None:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    for key, value in flags.items():
        if value is not True:
            raise SystemExit(f"R13_LAUNCHER_FLAG_NOT_TRUE:{key}")
    if sys.flags.optimize != 0:
        raise SystemExit(f"R13_LAUNCHER_OPTIMIZATION_FORBIDDEN:{sys.flags.optimize}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle", required=True)
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--observer", required=True)
    ap.add_argument("--candidate-commit", required=True)
    ap.add_argument("--candidate-tree", required=True)
    ap.add_argument("--environment-digest", required=True)
    ap.add_argument("--interpreter-contract-digest", required=True)
    ap.add_argument("--oracle-git-blob-sha1", required=True)
    ap.add_argument("--observer-git-blob-sha1", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--round-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    require_launcher_runtime()
    oracle = pathlib.Path(args.oracle).resolve()
    observer = pathlib.Path(args.observer).resolve()
    sandbox = pathlib.Path(args.sandbox).resolve()
    if oracle.is_relative_to(sandbox) or observer.is_relative_to(sandbox):
        raise SystemExit("R13_LAUNCHER_TRUSTED_OBJECT_INSIDE_CANDIDATE")
    if not oracle.is_file() or not observer.is_file():
        raise SystemExit("R13_LAUNCHER_TRUSTED_OBJECT_MISSING")

    python_bin = pathlib.Path(sys.executable).resolve()
    env = {
        "HOME": os.environ.get("HOME", "/tmp"),
        "PATH": f"{python_bin.parent}:/usr/bin:/bin",
    }
    command = [
        str(python_bin), "-I", "-S", str(oracle),
        "--sandbox", str(sandbox),
        "--observer", str(observer),
        "--candidate-commit", args.candidate_commit,
        "--candidate-tree", args.candidate_tree,
        "--environment-digest", args.environment_digest,
        "--interpreter-contract-digest", args.interpreter_contract_digest,
        "--oracle-git-blob-sha1", args.oracle_git_blob_sha1,
        "--observer-git-blob-sha1", args.observer_git_blob_sha1,
        "--run-id", args.run_id,
        "--round-id", args.round_id,
        "--output", args.output,
    ]
    cp = subprocess.run(
        command,
        cwd=str(oracle.parent),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=300,
    )
    if cp.returncode != 0:
        raise SystemExit(
            f"R13_LAUNCHER_ORACLE_FAILED:rc={cp.returncode}:stdout={cp.stdout[-2000:]!r}:stderr={cp.stderr[-2000:]!r}"
        )
    if cp.stderr.strip():
        raise SystemExit(f"R13_LAUNCHER_ORACLE_STDERR_NOT_EMPTY:{cp.stderr[-2000:]!r}")
    if not pathlib.Path(args.output).is_file():
        raise SystemExit("R13_LAUNCHER_ORACLE_OUTPUT_MISSING")
    print(cp.stdout, end="")
    print(f"R13_LAUNCHER_ORACLE_SHA256={sha256(oracle.read_bytes())}")
    print(f"R13_LAUNCHER_OBSERVER_SHA256={sha256(observer.read_bytes())}")


if __name__ == "__main__":
    main()
