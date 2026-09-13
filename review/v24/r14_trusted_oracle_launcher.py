from __future__ import annotations

import importlib.util
import pathlib
import sys


def require_runtime() -> None:
    flags={
        "isolated":bool(sys.flags.isolated),
        "no_site":bool(sys.flags.no_site),
        "ignore_environment":bool(sys.flags.ignore_environment),
        "safe_path":bool(sys.flags.safe_path),
    }
    if any(v is not True for v in flags.values()):
        raise SystemExit(f"R14_LAUNCHER_INTERPRETER_FLAGS_INVALID:{flags}")
    if sys.flags.optimize != 0:
        raise SystemExit("R14_LAUNCHER_OPTIMIZATION_FORBIDDEN")
    if "" in sys.path:
        raise SystemExit("R14_LAUNCHER_CWD_ON_SYS_PATH")


def main() -> None:
    require_runtime()
    if len(sys.argv)<3 or sys.argv[1]!="--oracle":
        raise SystemExit("R14_LAUNCHER_ORACLE_REQUIRED")
    oracle=pathlib.Path(sys.argv[2]).resolve()
    if not oracle.is_file():
        raise SystemExit("R14_LAUNCHER_ORACLE_MISSING")
    remaining=sys.argv[3:]
    spec=importlib.util.spec_from_file_location("r14_external_oracle",oracle)
    if spec is None or spec.loader is None:
        raise SystemExit("R14_LAUNCHER_ORACLE_SPEC_INVALID")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.argv=[str(oracle),*remaining]
    mod.main()


if __name__=="__main__":
    main()
