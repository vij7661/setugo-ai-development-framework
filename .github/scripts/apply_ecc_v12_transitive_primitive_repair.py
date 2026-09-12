from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "experiments" / "ecc_derived"
BOUNDARY = MOD / "ecc_candidate_boundary.py"
REFERENCE = MOD / "ecc_reference_evidence.py"
MANIFEST = MOD / "ecc_governance_trust_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


boundary = BOUNDARY.read_text(encoding="utf-8")

old = """    reference_lookup_fn = evidence_module.lookup_reference_evidence\n\n    boundary_path = path_resolve_fn(path_type(boundary_file))\n"""
new = """    reference_lookup_fn = evidence_module.lookup_reference_evidence\n\n    # V12: module-object identity is insufficient when candidate-authoritative\n    # strict helpers dereference mutable attributes on those modules at runtime.\n    # Bind the exact transitive primitive callables used by _sha256_json.\n    strict_hashlib_sha256_fn = strict_module.hashlib.sha256\n    strict_json_dumps_fn = strict_module.json.dumps\n\n    boundary_path = path_resolve_fn(path_type(boundary_file))\n"""
if old not in boundary:
    raise SystemExit("V11 strict transitive primitive anchor not found")
boundary = boundary.replace(old, new, 1)

boundary = boundary.replace(
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V11_MODULE_GLOBAL_INTEGRITY_MANIFEST":',
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V12_TRANSITIVE_PRIMITIVE_INTEGRITY_MANIFEST":',
    1,
)

old = """        if manifest.get("module_global_dependency_policy") != "RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION":\n            return False\n        if manifest.get("checked_entrypoint_identity_policy") != "EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED":\n            return False\n"""
new = """        if manifest.get("module_global_dependency_policy") != "RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION":\n            return False\n        if manifest.get("transitive_module_attribute_policy") != "EXACT_STRICT_DIGEST_PRIMITIVE_CALLABLES_BOUND_AT_INITIALIZATION":\n            return False\n        if set(manifest.get("captured_strict_transitive_primitives") or []) != {\n            "strict_core.hashlib.sha256",\n            "strict_core.json.dumps",\n        }:\n            return False\n        if set(manifest.get("config_reference_semantic_fields") or []) != {\n            "permission_profile",\n            "argv",\n        }:\n            return False\n        if manifest.get("checked_entrypoint_identity_policy") != "EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED":\n            return False\n"""
if old not in boundary:
    raise SystemExit("V11 manifest policy anchor not found")
boundary = boundary.replace(old, new, 1)

old = """        if not entrypoint_identity_ok():\n            return False\n        if not dependency_globals_ok():\n            return False\n\n        if not module_identity_ok(gov_module, public_path, "ecc_governance"):\n"""
new = """        if not entrypoint_identity_ok():\n            return False\n        # V12: fail closed if the exact digest primitives dereferenced through\n        # strict module globals have changed while the module objects themselves\n        # remain identical.\n        if getattr(strict_module.hashlib, "sha256", None) is not strict_hashlib_sha256_fn:\n            return False\n        if getattr(strict_module.json, "dumps", None) is not strict_json_dumps_fn:\n            return False\n        if not dependency_globals_ok():\n            return False\n\n        if not module_identity_ok(gov_module, public_path, "ecc_governance"):\n"""
if old not in boundary:
    raise SystemExit("V11 runtime dependency anchor not found")
boundary = boundary.replace(old, new, 1)

old = """            record.get("endpoint") == expected.get("endpoint") == current.get("endpoint"),\n            record.get("argv_digest") == expected.get("argv_digest") == current.get("argv_digest"),\n            record.get("canonical_digest") == expected.get("canonical_digest") == current.get("canonical_digest"),\n"""
new = """            record.get("endpoint") == expected.get("endpoint") == current.get("endpoint"),\n            record.get("permission_profile") == expected.get("permission_profile") == current.get("permission_profile"),\n            record.get("argv") == expected.get("argv") == current.get("argv"),\n            record.get("argv_digest") == expected.get("argv_digest") == current.get("argv_digest"),\n            record.get("canonical_digest") == expected.get("canonical_digest") == current.get("canonical_digest"),\n"""
if old not in boundary:
    raise SystemExit("V11 config evidence anchor not found")
boundary = boundary.replace(old, new, 1)
BOUNDARY.write_text(boundary, encoding="utf-8")

reference = REFERENCE.read_text(encoding="utf-8")
old = """        "transport": "stdio",\n        "endpoint": None,\n        "argv_digest": _sha256_json(["x"]),\n        "canonical_digest": _sha256_json(_CONFIG_MATERIAL),\n"""
new = """        "transport": "stdio",\n        "endpoint": None,\n        "argv": ["x"],\n        "permission_profile": "r",\n        "argv_digest": _sha256_json(["x"]),\n        "canonical_digest": _sha256_json(_CONFIG_MATERIAL),\n"""
if old not in reference:
    raise SystemExit("V11 reference config anchor not found")
reference = reference.replace(old, new, 1)
REFERENCE.write_text(reference, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V11_MODULE_GLOBAL_INTEGRITY_MANIFEST":
    raise SystemExit("Expected V11 manifest before V12 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V12_TRANSITIVE_PRIMITIVE_INTEGRITY_MANIFEST"
manifest["transitive_module_attribute_policy"] = "EXACT_STRICT_DIGEST_PRIMITIVE_CALLABLES_BOUND_AT_INITIALIZATION"
manifest["captured_strict_transitive_primitives"] = [
    "strict_core.hashlib.sha256",
    "strict_core.json.dumps",
]
manifest["config_reference_semantic_fields"] = ["permission_profile", "argv"]
manifest["transitive_digest_primitive_mutation_fail_closed"] = True
manifest["exp_ecc_5_raw_argv_semantically_bound"] = True
manifest["exp_ecc_5_permission_profile_semantically_bound"] = True
manifest["remaining_primitive_boundary"] = (
    "MUTATION_OF_CAPTURED_CALLABLE_OBJECTS_OR_OTHER_INTERPRETER_PRIMITIVES_"
    "NOT_DIRECTLY_DEREFERENCED_BY_EXP_ECC_5_STRICT_DIGEST_PATH_OUTSIDE_V12_BOUNDED_THREAT_MODEL"
)
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
manifest["module_sha256"]["reference_evidence"] = sha256(REFERENCE)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("REFERENCE_SHA256=" + sha256(REFERENCE))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V12_TRANSITIVE_PRIMITIVE_REPAIR_GENERATED=1")
