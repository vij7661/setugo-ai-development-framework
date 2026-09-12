from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "experiments" / "ecc_derived"
sys.path.insert(0, str(MOD))

import ecc_candidate_boundary as boundary

print("PUBLIC_VERIFY=", boundary.verify_runtime_policy())

# The public verifier is diagnostic-only and closes over the internal verifier.
public_closure = dict(zip(boundary.verify_runtime_policy.__code__.co_freevars, boundary.verify_runtime_policy.__closure__ or ()))
runtime_cell = public_closure.get("runtime_verify")
if runtime_cell is None:
    raise SystemExit("runtime_verify not found in public verifier closure")
runtime_verify = runtime_cell.cell_contents
print("RUNTIME_VERIFY=", runtime_verify())
print("RUNTIME_FREEVARS=", runtime_verify.__code__.co_freevars)

cells = dict(zip(runtime_verify.__code__.co_freevars, runtime_verify.__closure__ or ()))
for helper_name in ("entrypoint_identity_ok", "dependency_globals_ok"):
    cell = cells.get(helper_name)
    if cell is not None:
        fn = cell.cell_contents
        print(f"{helper_name.upper()}=", fn())

strict_module = cells["strict_module"].cell_contents
strict_hashlib_sha256_fn = cells["strict_hashlib_sha256_fn"].cell_contents
strict_json_dumps_fn = cells["strict_json_dumps_fn"].cell_contents
print("STRICT_SHA256_IDENTITY=", strict_module.hashlib.sha256 is strict_hashlib_sha256_fn)
print("STRICT_JSON_DUMPS_IDENTITY=", strict_module.json.dumps is strict_json_dumps_fn)

manifest_path = cells["manifest_path"].cell_contents
manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
print("MANIFEST_RECORD_TYPE=", manifest.get("record_type"))
print("CAPTURED_STRICT_TRANSITIVE_PRIMITIVES=", manifest.get("captured_strict_transitive_primitives"))
print("CONFIG_REFERENCE_SEMANTIC_FIELDS=", manifest.get("config_reference_semantic_fields"))

paths = {
    "public_core": cells["public_path"].cell_contents,
    "strict_core": cells["strict_path"].cell_contents,
    "candidate_boundary": cells["boundary_path"].cell_contents,
    "reference_evidence": cells["evidence_path"].cell_contents,
}
actual_hashes = {name: hashlib.sha256(Path(path).read_bytes()).hexdigest() for name, path in paths.items()}
print("EXPECTED_HASHES=", json.dumps(manifest.get("module_sha256") or {}, sort_keys=True))
print("ACTUAL_HASHES=", json.dumps(actual_hashes, sort_keys=True))
print("HASHES_MATCH=", (manifest.get("module_sha256") or {}) == actual_hashes)

# Re-evaluate each manifest policy check in the same order as runtime_verify.
checks = [
    ("record_type", manifest.get("record_type") == "ECC_GOVERNANCE_V12_TRANSITIVE_PRIMITIVE_INTEGRITY_MANIFEST"),
    ("eligibility_provenance_policy", manifest.get("eligibility_provenance_policy") == "PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST"),
    ("serialized_candidate_authority", manifest.get("serialized_candidate_authority") == "REJECT_UNSEALED_RECONSTRUCTION"),
    ("seal_capability_policy", manifest.get("seal_capability_policy") == "POSITIVE_SEAL_CAPABILITY_CLOSURE_LOCAL_ONLY"),
    ("ordinary_module_access_can_mint_provenance", manifest.get("ordinary_module_access_can_mint_provenance") is False),
    ("public_runtime_verifier_role", manifest.get("public_runtime_verifier_role") == "DIAGNOSTIC_WRAPPER_ONLY"),
    ("candidate_runtime_verifier_policy", manifest.get("candidate_runtime_verifier_policy") == "CLOSURE_HELD_INTERNAL_VERIFIER"),
    ("candidate_dependencies_policy", manifest.get("candidate_dependencies_policy") == "CLOSURE_HELD_ORIGINAL_MODULE_OBJECTS"),
    ("public_verifier_substitution", manifest.get("public_verifier_substitution_affects_candidate_authority") is False),
    ("actual_dependency_tamper", manifest.get("actual_dependency_tamper_fail_closed") is True),
    ("verifier_primitive_policy", manifest.get("verifier_primitive_policy") == "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION"),
    ("seal_primitive_policy", manifest.get("seal_primitive_policy") == "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION"),
    ("path_primitive_policy", manifest.get("path_primitive_policy") == "EXACT_PATH_CALLABLES_CAPTURED_AT_INITIALIZATION"),
    ("public_path_alias", manifest.get("public_path_method_alias_controls_candidate_authority") is False),
    ("module_global_policy", manifest.get("module_global_dependency_policy") == "RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION"),
    ("transitive_module_attribute_policy", manifest.get("transitive_module_attribute_policy") == "EXACT_STRICT_DIGEST_PRIMITIVE_CALLABLES_BOUND_AT_INITIALIZATION"),
    ("captured_transitive_set", set(manifest.get("captured_strict_transitive_primitives") or []) == {"strict_core.hashlib.sha256", "strict_core.json.dumps"}),
    ("semantic_fields_set", set(manifest.get("config_reference_semantic_fields") or []) == {"permission_profile", "argv"}),
    ("checked_entrypoint_identity_policy", manifest.get("checked_entrypoint_identity_policy") == "EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED"),
    ("public_covers", manifest.get("public_covers_global_controls_candidate_authority") is False),
    ("public_json", manifest.get("public_json_alias_controls_candidate_authority") is False),
    ("public_marshal", manifest.get("public_marshal_alias_controls_candidate_authority") is False),
    ("public_core_policy", manifest.get("public_core_policy") == "HISTORICAL_ONLY_NO_CALLER_STRICT_MODE"),
    ("candidate_boundary_policy", manifest.get("candidate_boundary_policy") == "ONLY_PUBLIC_CANDIDATE_ELIGIBILITY_ISSUER"),
    ("reference_source", manifest.get("reference_evidence_trust_source") == "REFERENCE_REPO_BOUND_SIMULATION_ONLY"),
    ("authority_effect", manifest.get("authority_effect") == "NONE_EVIDENCE_ONLY"),
]
for name, ok in checks:
    print(f"POLICY_{name}=", ok)

print("DIAGNOSTIC_DONE=1")
