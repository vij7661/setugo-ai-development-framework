from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "experiments" / "ecc_derived"
BOUNDARY = MOD / "ecc_candidate_boundary.py"
MANIFEST = MOD / "ecc_governance_trust_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source = BOUNDARY.read_text(encoding="utf-8")

needle = "    path_type = Path\n\n    boundary_path = path_type(boundary_file).resolve()\n"
replacement = '''    path_type = Path
    path_read_text_fn = Path.read_text
    path_read_bytes_fn = Path.read_bytes
    path_resolve_fn = Path.resolve
    path_is_file_fn = Path.is_file
    path_is_symlink_fn = Path.is_symlink

    boundary_path = path_resolve_fn(path_type(boundary_file))
'''
if needle not in source:
    raise SystemExit("Expected V9 path_type initialization not found")
source = source.replace(needle, replacement, 1)

replacements = {
    "return sha256_fn(path.read_bytes()).hexdigest()":
        "return sha256_fn(path_read_bytes_fn(path)).hexdigest()",
    "resolved = path.resolve(strict=True)":
        "resolved = path_resolve_fn(path, strict=True)",
    "expected = expected_path.resolve(strict=True)":
        "expected = path_resolve_fn(expected_path, strict=True)",
    "if path.is_symlink() or expected_path.is_symlink():":
        "if path_is_symlink_fn(path) or path_is_symlink_fn(expected_path):",
    "if path_type(origin).resolve(strict=True) != expected:":
        "if path_resolve_fn(path_type(origin), strict=True) != expected:",
    "if path.is_symlink() or not path.is_file():":
        "if path_is_symlink_fn(path) or not path_is_file_fn(path):",
    "manifest = json_loads_fn(manifest_path.read_text(encoding=\"utf-8\"))":
        "manifest = json_loads_fn(path_read_text_fn(manifest_path, encoding=\"utf-8\"))",
    "if boundary_path.resolve(strict=True) != path_type(boundary_file).resolve(strict=True):":
        "if path_resolve_fn(boundary_path, strict=True) != path_resolve_fn(path_type(boundary_file), strict=True):",
    "ECC_GOVERNANCE_V9_VERIFIER_PRIMITIVE_INTEGRITY_MANIFEST":
        "ECC_GOVERNANCE_V10_PATH_PRIMITIVE_INTEGRITY_MANIFEST",
}
for old, new in replacements.items():
    if old not in source:
        raise SystemExit(f"Expected V9 source fragment not found: {old}")
    source = source.replace(old, new, 1)

manifest_check_anchor = '''        if manifest.get("seal_primitive_policy") != "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
'''
manifest_check_replacement = manifest_check_anchor + '''        if manifest.get("path_primitive_policy") != "EXACT_PATH_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("public_path_method_alias_controls_candidate_authority") is not False:
            return False
        if set(manifest.get("captured_path_primitives") or []) != {
            "Path.read_text",
            "Path.read_bytes",
            "Path.resolve",
            "Path.is_file",
            "Path.is_symlink",
        }:
            return False
'''
if manifest_check_anchor not in source:
    raise SystemExit("Expected V9 manifest primitive check anchor not found")
source = source.replace(manifest_check_anchor, manifest_check_replacement, 1)

BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V9_VERIFIER_PRIMITIVE_INTEGRITY_MANIFEST":
    raise SystemExit("Expected V9 manifest before V10 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V10_PATH_PRIMITIVE_INTEGRITY_MANIFEST"
manifest["path_primitive_policy"] = "EXACT_PATH_CALLABLES_CAPTURED_AT_INITIALIZATION"
manifest["captured_path_primitives"] = [
    "Path.read_text",
    "Path.read_bytes",
    "Path.resolve",
    "Path.is_file",
    "Path.is_symlink",
]
manifest["public_path_method_alias_controls_candidate_authority"] = False
manifest["remaining_path_boundary"] = (
    "MUTATION_OF_CAPTURED_PATH_CALLABLE_OBJECTS_OR_DEEPER_OS_FILESYSTEM_PRIMITIVES_"
    "OUTSIDE_V10_BOUNDED_THREAT_MODEL"
)
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V10_PATH_PRIMITIVE_REPAIR_GENERATED=1")
