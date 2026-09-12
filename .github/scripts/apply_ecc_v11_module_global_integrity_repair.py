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

needle = '''    path_is_symlink_fn = Path.is_symlink

    boundary_path = path_resolve_fn(path_type(boundary_file))
'''
replacement = '''    path_is_symlink_fn = Path.is_symlink
    covers_expected = frozenset(_COVERS)

    # Capture the exact candidate-authoritative entrypoint objects before any
    # ordinary module monkeypatching can occur. Code equality alone is not
    # sufficient because a new function object can reuse the same __code__
    # with different globals/defaults.
    strict_entrypoints = {
        "assess_control_execution_candidate": strict_module.assess_control_execution_candidate,
        "check_declared_executable_equivalence_candidate": strict_module.check_declared_executable_equivalence_candidate,
        "qualify_role_binding_candidate": strict_module.qualify_role_binding_candidate,
        "authorize_power_activation_candidate": strict_module.authorize_power_activation_candidate,
        "check_tool_configuration_candidate": strict_module.check_tool_configuration_candidate,
        "classify_review_binding_candidate": strict_module.classify_review_binding_candidate,
        "authorize_learning_promotion_candidate": strict_module.authorize_learning_promotion_candidate,
    }
    reference_lookup_fn = evidence_module.lookup_reference_evidence

    boundary_path = path_resolve_fn(path_type(boundary_file))
'''
if needle not in source:
    raise SystemExit("V11 insertion anchor not found")
source = source.replace(needle, replacement, 1)

needle = '''    def module_identity_ok(module, expected_path, expected_name):
'''
helper = '''    def freeze_value(value):
        if value is None or isinstance(value, (bool, int, float, str, bytes)):
            return ("scalar", type(value).__name__, value)
        if isinstance(value, dict):
            items = [(freeze_value(k), freeze_value(v)) for k, v in value.items()]
            items.sort(key=lambda item: repr(item[0]))
            return ("dict", tuple(items))
        if isinstance(value, (set, frozenset)):
            items = [freeze_value(v) for v in value]
            items.sort(key=repr)
            return ("set", tuple(items))
        if isinstance(value, (list, tuple)):
            return (type(value).__name__, tuple(freeze_value(v) for v in value))
        return None

    dependency_specs = []
    dependency_seen = set()

    def capture_dependency(globals_dict, name):
        key = (id(globals_dict), name)
        if key in dependency_seen or name not in globals_dict:
            return
        dependency_seen.add(key)
        value = globals_dict[name]
        frozen = freeze_value(value)
        if frozen is not None:
            dependency_specs.append((globals_dict, name, "value", frozen))
            return
        code = getattr(value, "__code__", None)
        fn_globals = getattr(value, "__globals__", None)
        if code is not None and isinstance(fn_globals, dict):
            dependency_specs.append((
                globals_dict,
                name,
                "function",
                value,
                code_sha(value),
                freeze_value(getattr(value, "__defaults__", None)),
                freeze_value(getattr(value, "__kwdefaults__", None)),
            ))
            for child_name in code.co_names:
                capture_dependency(fn_globals, child_name)
            return
        dependency_specs.append((globals_dict, name, "identity", value))

    for fn in tuple(strict_entrypoints.values()) + (reference_lookup_fn,):
        for dep_name in fn.__code__.co_names:
            capture_dependency(fn.__globals__, dep_name)

    def dependency_globals_ok():
        for spec in dependency_specs:
            globals_dict, name, mode = spec[:3]
            if name not in globals_dict:
                return False
            current = globals_dict[name]
            if mode == "value":
                if freeze_value(current) != spec[3]:
                    return False
            elif mode == "identity":
                if current is not spec[3]:
                    return False
            elif mode == "function":
                expected_fn, expected_code, expected_defaults, expected_kwdefaults = spec[3:]
                if current is not expected_fn:
                    return False
                if code_sha(current) != expected_code:
                    return False
                if freeze_value(getattr(current, "__defaults__", None)) != expected_defaults:
                    return False
                if freeze_value(getattr(current, "__kwdefaults__", None)) != expected_kwdefaults:
                    return False
            else:
                return False
        return True

    def entrypoint_identity_ok():
        for name, expected_fn in strict_entrypoints.items():
            if getattr(strict_module, name, None) is not expected_fn:
                return False
        if getattr(evidence_module, "lookup_reference_evidence", None) is not reference_lookup_fn:
            return False
        return True

    def module_identity_ok(module, expected_path, expected_name):
'''
if needle not in source:
    raise SystemExit("V11 dependency helper anchor not found")
source = source.replace(needle, helper, 1)

source = source.replace(
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V10_PATH_PRIMITIVE_INTEGRITY_MANIFEST":',
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V11_MODULE_GLOBAL_INTEGRITY_MANIFEST":',
    1,
)

needle = '''        if manifest.get("public_path_method_alias_controls_candidate_authority") is not False:
            return False
'''
replacement = '''        if manifest.get("public_path_method_alias_controls_candidate_authority") is not False:
            return False
        if manifest.get("module_global_dependency_policy") != "RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION":
            return False
        if manifest.get("checked_entrypoint_identity_policy") != "EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED":
            return False
        if manifest.get("public_covers_global_controls_candidate_authority") is not False:
            return False
'''
if needle not in source:
    raise SystemExit("V11 manifest policy anchor not found")
source = source.replace(needle, replacement, 1)

source = source.replace(
    'if set(manifest.get("covers") or []) != _COVERS:',
    'if frozenset(manifest.get("covers") or []) != covers_expected:',
    1,
)

needle = '''        if not module_identity_ok(gov_module, public_path, "ecc_governance"):
            return False
'''
replacement = '''        if not entrypoint_identity_ok():
            return False
        if not dependency_globals_ok():
            return False

        if not module_identity_ok(gov_module, public_path, "ecc_governance"):
            return False
'''
if needle not in source:
    raise SystemExit("V11 runtime integrity anchor not found")
source = source.replace(needle, replacement, 1)

old = '''        strict_functions = {
            "strict.assess_control_execution_candidate": strict_module.assess_control_execution_candidate,
            "strict.check_declared_executable_equivalence_candidate": strict_module.check_declared_executable_equivalence_candidate,
            "strict.qualify_role_binding_candidate": strict_module.qualify_role_binding_candidate,
            "strict.authorize_power_activation_candidate": strict_module.authorize_power_activation_candidate,
            "strict.check_tool_configuration_candidate": strict_module.check_tool_configuration_candidate,
            "strict.classify_review_binding_candidate": strict_module.classify_review_binding_candidate,
            "strict.authorize_learning_promotion_candidate": strict_module.authorize_learning_promotion_candidate,
            "reference.lookup_reference_evidence": evidence_module.lookup_reference_evidence,
        }
'''
new = '''        strict_functions = {
            "strict.assess_control_execution_candidate": strict_entrypoints["assess_control_execution_candidate"],
            "strict.check_declared_executable_equivalence_candidate": strict_entrypoints["check_declared_executable_equivalence_candidate"],
            "strict.qualify_role_binding_candidate": strict_entrypoints["qualify_role_binding_candidate"],
            "strict.authorize_power_activation_candidate": strict_entrypoints["authorize_power_activation_candidate"],
            "strict.check_tool_configuration_candidate": strict_entrypoints["check_tool_configuration_candidate"],
            "strict.classify_review_binding_candidate": strict_entrypoints["classify_review_binding_candidate"],
            "strict.authorize_learning_promotion_candidate": strict_entrypoints["authorize_learning_promotion_candidate"],
            "reference.lookup_reference_evidence": reference_lookup_fn,
        }
'''
if old not in source:
    raise SystemExit("V11 strict runtime mapping anchor not found")
source = source.replace(old, new, 1)

BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V10_PATH_PRIMITIVE_INTEGRITY_MANIFEST":
    raise SystemExit("Expected V10 manifest before V11 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V11_MODULE_GLOBAL_INTEGRITY_MANIFEST"
manifest["module_global_dependency_policy"] = "RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION"
manifest["checked_entrypoint_identity_policy"] = "EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED"
manifest["public_covers_global_controls_candidate_authority"] = False
manifest["module_global_mutation_fail_closed"] = True
manifest["same_code_new_function_object_fail_closed"] = True
manifest["remaining_module_global_boundary"] = "CONCURRENT_TOCTOU_MUTATION_BETWEEN_VERIFY_AND_EXECUTION_AND_REFLECTIVE_CAPTURED_OBJECT_MUTATION_OUTSIDE_V11_BOUNDED_THREAT_MODEL"
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V11_MODULE_GLOBAL_INTEGRITY_REPAIR_GENERATED=1")
