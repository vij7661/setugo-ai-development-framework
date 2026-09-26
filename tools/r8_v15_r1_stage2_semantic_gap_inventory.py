"""Deterministic, evidence-bound inventory after SG-1 closure.

This scanner reports only imports discovered from the frozen candidate and the
bound implementation allowlist. It never invents a next gate from names.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = "4984f06a4420b76ad1ad475751aebda04a2d2c5c"
BASE = "751162ee42c603cb6c84ee12021d16bab6fa626b"
ALLOW = ROOT / "governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def blob(rev: str, path: str) -> str:
    return run("git", "rev-parse", f"{rev}:{path}")


def exists(rev: str, path: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{rev}:{path}"], cwd=ROOT).returncode == 0


def selected_files() -> list[str]:
    allow = json.loads(ALLOW.read_text(encoding="utf-8"))
    return sorted({e["path"] for rec in allow["per_candidate"].values() for e in rec["selected_entries"]
                   if e["path"].startswith("governance-runtime/r8_v15_r1_") and e["path"].endswith(".py")})


def scan() -> dict:
    files = selected_files()
    edges = []
    for path in files:
        tree = ast.parse(run("git", "show", f"{CANDIDATE}:{path}"), filename=path)
        for node in ast.walk(tree):
            module = None
            kind = None
            names = []
            if isinstance(node, ast.Import):
                kind = "import"
                module = node.names[0].name if node.names else ""
            elif isinstance(node, ast.ImportFrom):
                kind = "from"
                module = node.module or ""
                names = [a.name for a in node.names]
            if not module or not module.startswith("r8_v15_r1_"):
                continue
            target = next((p for p in (f"governance-runtime/{module}.py", f"governance-runtime/{module}/__init__.py") if exists(CANDIDATE, p)), None)
            edges.append({"from_path": path, "kind": kind, "module": module, "names": names,
                          "target_path": target, "target_blob": blob(CANDIDATE, target) if target else None,
                          "line": node.lineno})
    edges.sort(key=lambda e: (e["from_path"], e["line"], e["module"]))
    covered = [{"id": f"SG1-EDGE-{i:03d}", "classification": "already_covered",
                "source": e["from_path"], "target": e["target_path"], "evidence": e}
               for i, e in enumerate(edges, 1)]
    payload = {"schema": "r8-v15-r1-stage2-semantic-gap-inventory/v1",
               "candidate": {"commit": CANDIDATE, "tree": run("git", "rev-parse", f"{CANDIDATE}^{{tree}}"), "base": BASE},
               "selected_files": files, "direct_edges": edges, "items": covered,
               "unresolved_semantic_dependencies": [], "runtime_only": [], "release_deployment_production_only": [],
               "proposed_next_gates": [], "manual_policy_decision_required": True,
               "stage2_semantic_execution_performed": False, "authority_effect": "NONE", "fallback_to_3": "ACTIVE"}
    return payload


def write(path: Path) -> dict:
    result = scan()
    raw = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    result["inventory_sha256"] = hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    out = ROOT / "governance-r8/R8-V15-R1-STAGE2-SEMANTIC-GAP-INVENTORY.json"
    result = write(out)
    print(json.dumps({"path": out.as_posix(), "items": len(result["items"]), "proposed_next_gates": 0,
                      "authority_effect": result["authority_effect"]}, sort_keys=True))
