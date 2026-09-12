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

old = '''    sha256_fn = hashlib.sha256
    json_loads_fn = json.loads
    marshal_dumps_fn = marshal.dumps
    sys_modules = sys.modules
    path_type = Path

    boundary_path = path_type(boundary_file).resolve()
'''
new = '''    sha256_fn = hashlib.sha256
    json_loads_fn = json.loads
    marshal_dumps_fn = marshal.dumps
    sys_modules = sys.modules
    path_type = Path
    path_resolve_fn = Path.resolve
    path_is_symlink_fn = Path.is_symlink
    path_is_file_fn = Path.is_file
    path_read_text_fn = Path.read_text
    path_read_bytes_fn = Path.read_bytes

    boundary_path = path_resolve_fn(path_type(boundary_file))
'''
if old not in source:
    raise SystemExit("Expected V9 verifier primitive block not found")
source = source.replace(old, new, 1)

source = source.replace(
    'return sha256_fn(path.read_bytes()).hexdigest()',
    'return sha256_fn(path_read_bytes_fn(path)).hexdigest()',
    1,
)
source = source.replace(
    '''            resolved = path.resolve(strict=True)
            expected = expected_path.resolve(strict=True)
''',
    '''            resolved = path_resolve_fn(path, strict=True)
            expected = path_resolve_fn(expected_path, strict=True)
''',
    1,
)
source = source.replace(
    '        if path.is_symlink() or expected_path.is_symlink():',
    '        if path_is_symlink_fn(path) or path_is_symlink_fn(expected_path):',
    1,
)
source = source.replace(
    '            if path_type(origin).resolve(strict=True) != expected:',
    '            if path_resolve_fn(path_type(origin), strict=True) != expected:',
    1,
)
source = source.replace(
    '''                if path.is_symlink() or not path.is_file():
''',
    '''                if path_is_symlink_fn(path) or not path_is_file_fn(path):
''',
    1,
)
source = source.replace(
    'manifest = json_loads_fn(manifest_path.read_text(encoding="utf-8"))',
    'manifest = json_loads_fn(path_read_text_fn(manifest_path, encoding="utf-8"))',
    1,
)
source = source.replace(
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V9_VERIFIER_PRIMITIVE_INTEGRITY_MANIFEST":',
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V10_FILESYSTEM_PRIMITIVE_INTEGRITY_MANIFEST":',
    1,
)

anchor = '''        if manifest.get("public_marshal_alias_controls_candidate_authority") is not False:
            return False
'''
addition = '''        if manifest.get("public_marshal_alias_controls_candidate_authority") is not False:
            return False
        if manifest.get("filesystem_primitive_policy") != "EXACT_PATH_METHODS_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("public_path_method_substitution_affects_candidate_authority") is not False:
            return False
'''
if anchor not in source:
    raise SystemExit("Expected V9 manifest validation anchor not found")
source = source.replace(anchor, addition, 1)

source = source.replace(
    '''            if boundary_path.resolve(strict=True) != path_type(boundary_file).resolve(strict=True):
''',
    '''            if path_resolve_fn(boundary_path, strict=True) != path_resolve_fn(path_type(boundary_file), strict=True):
''',
    1,
)

BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V9_VERIFIER_PRIMITIVE_INTEGRITY_MANIFEST":
    raise SystemExit("Expected V9 manifest before V10 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V10_FILESYSTEM_PRIMITIVE_INTEGRITY_MANIFEST"
manifest["filesystem_primitive_policy"] = "EXACT_PATH_METHODS_CAPTURED_AT_INITIALIZATION"
manifest["public_path_method_substitution_affects_candidate_authority"] = False
manifest["captured_filesystem_primitives"] = [
    "Path.resolve",
    "Path.is_symlink",
    "Path.is_file",
    "Path.read_text",
    "Path.read_bytes",
]
manifest["remaining_filesystem_boundary"] = (
    "PATH_CONSTRUCTOR_CLASS_MUTATION_OR_CAPTURED_METHOD_OBJECT_MUTATION_"
    "OUTSIDE_V10_BOUNDED_THREAT_MODEL"
)
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V10_FILESYSTEM_PRIMITIVE_REPAIR_GENERATED=1")
