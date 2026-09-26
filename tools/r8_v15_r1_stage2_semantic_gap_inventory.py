"""Deterministic, exact-evidence-bound semantic-gap inventory after SG-1 closure."""
from __future__ import annotations
import ast, hashlib, json, subprocess
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = "4984f06a4420b76ad1ad475751aebda04a2d2c5c"
BASE = "751162ee42c603cb6c84ee12021d16bab6fa626b"
ALLOW = "governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
SURFACE = "governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-SURFACE.json"
CLOSURE = "governance-r8/R8-V15-R1-STAGE2-SG1-CLOSURE.json"
EXPECTED_EVIDENCE = {
    ALLOW: ("15cbe7947d0f6f872fabd00b2fc5b0d01a894e2b", "297f17a2a2029ad137da90f350b6de46320e3d2a6ee6b0e81ccdb9066e65a52e"),
    SURFACE: ("94e3275edbb32baca640966830352f5e6c9f4ada", "dcbc2bed0f911a0a6886c16971e7359bba0cd0c056922275927ff2a417bafdab"),
    CLOSURE: ("95e8c4264ed483f9c6ef7f3bbad1accd7ad87f4e", "476040eb193e4a18d19f67dca0f9078a2587085a10a3097f175837865db557b5"),
}

def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

@lru_cache(maxsize=None)
def git_bytes(rev: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{rev}:{path}"), cwd=ROOT)

@lru_cache(maxsize=None)
def blob(rev: str, path: str) -> str:
    return run("git", "rev-parse", f"{rev}:{path}")

def bound_json(path: str) -> dict:
    expected_blob, expected_sha = EXPECTED_EVIDENCE[path]
    raw = git_bytes("HEAD", path)
    if blob("HEAD", path) != expected_blob or hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError(f"substituted evidence input: {path}")
    return json.loads(raw.decode("utf-8"))

def selected_files(allow: dict | None = None) -> list[str]:
    allow = allow or bound_json(ALLOW)
    return sorted({e["path"] for rec in allow["per_candidate"].values() for e in rec["selected_entries"] if e["path"].startswith("governance-runtime/r8_v15_r1_") and e["path"].endswith(".py")})

def target_for_module(module: str) -> str | None:
    dotted = module.replace(".", "/")
    for candidate in (f"governance-runtime/{dotted}.py", f"governance-runtime/{dotted}/__init__.py"):
        if subprocess.run(["git", "cat-file", "-e", f"{CANDIDATE}:{candidate}"], cwd=ROOT, stderr=subprocess.DEVNULL).returncode == 0:
            return candidate
    return None

def importfrom_targets(module: str, names: list[str]) -> list[tuple[str, list[str]]]:
    """Resolve actual dotted submodules without treating symbols as modules."""
    resolved = []
    remaining = []
    for name in names:
        dotted = f"{module}.{name}"
        if target_for_module(dotted):
            resolved.append((dotted, [name]))
        else:
            remaining.append(name)
    if remaining and target_for_module(module):
        resolved.append((module, remaining))
    return resolved

def edge_key(edge: dict) -> tuple:
    return (edge.get("from_path"), edge.get("source_blob"), edge.get("import_kind", edge.get("kind")), edge.get("import_module", edge.get("module")), tuple(edge.get("imported_names", edge.get("names", []))), edge.get("lineno", edge.get("line")), edge.get("target_path"), edge.get("target_blob"))

def discover_edges(files: list[str]) -> list[dict]:
    edges = []
    for path in files:
        tree = ast.parse(git_bytes(CANDIDATE, path).decode("utf-8"), filename=path)
        source_blob = blob(CANDIDATE, path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                aliases = [(alias.name, []) for alias in node.names]
                kind = "import"
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if not module.startswith("r8_v15_r1_"):
                    continue
                aliases = importfrom_targets(module, [a.name for a in node.names])
                kind = "from"
            else:
                continue
            for module, names in aliases:
                if not module.startswith("r8_v15_r1_"):
                    continue
                target = target_for_module(module)
                edges.append({"from_path": path, "source_blob": source_blob, "import_kind": kind, "import_module": module, "imported_names": names, "target_path": target, "target_blob": blob(CANDIDATE, target) if target else None, "lineno": node.lineno})
    return sorted(edges, key=lambda e: (e["from_path"], e["lineno"], e["import_module"], tuple(e["imported_names"])))

def classify_edge(edge: dict, bound_edges: list[dict], closure: dict) -> dict:
    return {"classification": "already_covered", "evidence": "semantic-surface + SG1 closure"} if edge_key(edge) in {edge_key(e) for e in bound_edges} and closure.get("stage2", {}).get("sg1_closed") is True else {"classification": "unresolved_semantic_dependency", "evidence": "not present in exact bound semantic surface"}

def scan() -> dict:
    allow = bound_json(ALLOW)
    surface = bound_json(SURFACE)
    closure = bound_json(CLOSURE)
    if surface.get("candidate") != CANDIDATE or surface.get("base") != BASE or closure.get("candidate", {}).get("commit") != CANDIDATE or closure.get("candidate", {}).get("parent") != BASE:
        raise ValueError("frozen candidate/base mismatch")
    files = selected_files(allow)
    edges = discover_edges(files)
    bound_edges = []
    for edge in surface.get("edges", []):
        enriched = dict(edge)
        enriched.update({"source_blob": blob(CANDIDATE, edge["from_path"]), "import_kind": edge["import_kind"], "import_module": edge["import_module"], "imported_names": edge.get("imported_names", []), "lineno": edge["lineno"], "target_blob": edge.get("target_blob_candidate", edge.get("target_blob"))})
        bound_edges.append(enriched)
    bound_keys = {edge_key(e) for e in bound_edges}
    covered = []
    for i, edge in enumerate(edges, 1):
        classification = classify_edge(edge, bound_edges, closure)["classification"] if edge_key(edge) not in bound_keys else "already_covered"
        covered.append({"id": f"SG1-EDGE-{i:03d}", "source": edge["from_path"], "target": edge["target_path"], "evidence": "semantic-surface + SG1 closure" if classification == "already_covered" else "not present in exact bound semantic surface", "classification": classification, "edge": edge})
    unresolved = [x for x in covered if x["classification"] != "already_covered"]
    return {"schema": "r8-v15-r1-stage2-semantic-gap-inventory/v2", "candidate": {"commit": CANDIDATE, "tree": run("git", "rev-parse", f"{CANDIDATE}^{{tree}}"), "base": BASE}, "evidence_inputs": {p: {"blob": EXPECTED_EVIDENCE[p][0], "sha256": EXPECTED_EVIDENCE[p][1]} for p in EXPECTED_EVIDENCE}, "selected_files": files, "direct_edges": edges, "items": covered, "unresolved_semantic_dependencies": unresolved, "runtime_only": {"status": "INSUFFICIENT_EVIDENCE", "items": []}, "release_deployment_production_only": {"status": "INSUFFICIENT_EVIDENCE", "items": []}, "manual_policy": {"status": "INSUFFICIENT_EVIDENCE", "items": []}, "proposed_next_gates": [], "manual_policy_decision_required": True, "stage2_semantic_execution_performed": False, "authority_effect": "NONE", "fallback_to_3": "ACTIVE"}

def write(path: Path) -> dict:
    result = scan()
    raw = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    result["inventory_sha256"] = hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result

def verify_inventory(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    declared = data.pop("inventory_sha256", None)
    raw = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    if declared != hashlib.sha256(raw).hexdigest():
        return False
    expected = scan()
    return data == expected

def verify_inventory_digest(path: Path) -> bool:
    return verify_inventory(path)

if __name__ == "__main__":
    out = ROOT / "governance-r8/R8-V15-R1-STAGE2-SEMANTIC-GAP-INVENTORY.json"
    result = write(out)
    print(json.dumps({"path": out.as_posix(), "items": len(result["items"]), "edges": len(result["direct_edges"]), "authority_effect": result["authority_effect"]}, sort_keys=True))
