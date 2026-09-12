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
start = source.index("def _file_sha(path):\n")
end = source.index("def _canonical_result_digest(value):\n")

runtime_block = r'''def _build_runtime_policy_verifier(gov_module, strict_module, evidence_module, boundary_file):
    hashlib_module = hashlib
    json_module = json
    marshal_module = marshal
    sys_module = sys
    path_type = Path

    boundary_path = path_type(boundary_file).resolve()
    here = boundary_path.parent
    manifest_path = here / "ecc_governance_trust_manifest.json"
    public_path = here / "ecc_governance.py"
    strict_path = here / "ecc_governance_strict.py"
    evidence_path = here / "ecc_reference_evidence.py"

    def file_sha(path):
        return hashlib_module.sha256(path.read_bytes()).hexdigest()

    def code_sha(fn):
        try:
            return hashlib_module.sha256(marshal_module.dumps(fn.__code__)).hexdigest()
        except (AttributeError, TypeError, ValueError):
            return None

    def module_identity_ok(module, expected_path, expected_name):
        try:
            path = path_type(module.__file__)
            resolved = path.resolve(strict=True)
            expected = expected_path.resolve(strict=True)
        except (AttributeError, OSError, RuntimeError):
            return False
        if path.is_symlink() or expected_path.is_symlink():
            return False
        if resolved != expected:
            return False
        if module.__name__ != expected_name:
            return False
        if sys_module.modules.get(expected_name) is not module:
            return False
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        if not origin:
            return False
        try:
            if path_type(origin).resolve(strict=True) != expected:
                return False
        except (OSError, RuntimeError):
            return False
        return True

    def runtime_verify():
        for path in (manifest_path, public_path, strict_path, boundary_path, evidence_path):
            try:
                if path.is_symlink() or not path.is_file():
                    return False
            except OSError:
                return False
        try:
            manifest = json_module.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return False

        if manifest.get("record_type") != "ECC_GOVERNANCE_V8_VERIFIER_SUBSTITUTION_MANIFEST":
            return False
        if manifest.get("eligibility_provenance_policy") != "PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST":
            return False
        if manifest.get("serialized_candidate_authority") != "REJECT_UNSEALED_RECONSTRUCTION":
            return False
        if manifest.get("seal_capability_policy") != "POSITIVE_SEAL_CAPABILITY_CLOSURE_LOCAL_ONLY":
            return False
        if manifest.get("ordinary_module_access_can_mint_provenance") is not False:
            return False
        if manifest.get("public_runtime_verifier_role") != "DIAGNOSTIC_WRAPPER_ONLY":
            return False
        if manifest.get("candidate_runtime_verifier_policy") != "CLOSURE_HELD_INTERNAL_VERIFIER":
            return False
        if manifest.get("candidate_dependencies_policy") != "CLOSURE_HELD_ORIGINAL_MODULE_OBJECTS":
            return False
        if manifest.get("public_verifier_substitution_affects_candidate_authority") is not False:
            return False
        if manifest.get("actual_dependency_tamper_fail_closed") is not True:
            return False
        if manifest.get("public_core_policy") != "HISTORICAL_ONLY_NO_CALLER_STRICT_MODE":
            return False
        if manifest.get("candidate_boundary_policy") != "ONLY_PUBLIC_CANDIDATE_ELIGIBILITY_ISSUER":
            return False
        if manifest.get("reference_evidence_trust_source") != "REFERENCE_REPO_BOUND_SIMULATION_ONLY":
            return False
        if manifest.get("authority_effect") != "NONE_EVIDENCE_ONLY":
            return False
        if set(manifest.get("covers") or []) != _COVERS:
            return False

        if not module_identity_ok(gov_module, public_path, "ecc_governance"):
            return False
        if not module_identity_ok(strict_module, strict_path, "ecc_governance_strict"):
            return False
        if not module_identity_ok(evidence_module, evidence_path, "ecc_reference_evidence"):
            return False
        try:
            if boundary_path.resolve(strict=True) != path_type(boundary_file).resolve(strict=True):
                return False
        except (OSError, RuntimeError):
            return False

        expected_hashes = manifest.get("module_sha256") or {}
        actual_hashes = {
            "public_core": file_sha(public_path),
            "strict_core": file_sha(strict_path),
            "candidate_boundary": file_sha(boundary_path),
            "reference_evidence": file_sha(evidence_path),
        }
        if expected_hashes != actual_hashes:
            return False

        runtime = manifest.get("runtime_code_sha256") or {}
        strict_functions = {
            "strict.assess_control_execution_candidate": strict_module.assess_control_execution_candidate,
            "strict.check_declared_executable_equivalence_candidate": strict_module.check_declared_executable_equivalence_candidate,
            "strict.qualify_role_binding_candidate": strict_module.qualify_role_binding_candidate,
            "strict.authorize_power_activation_candidate": strict_module.authorize_power_activation_candidate,
            "strict.check_tool_configuration_candidate": strict_module.check_tool_configuration_candidate,
            "strict.classify_review_binding_candidate": strict_module.classify_review_binding_candidate,
            "strict.authorize_learning_promotion_candidate": strict_module.authorize_learning_promotion_candidate,
            "reference.lookup_reference_evidence": evidence_module.lookup_reference_evidence,
        }
        actual_runtime = {name: code_sha(fn) for name, fn in strict_functions.items()}
        if runtime != actual_runtime or any(value is None for value in actual_runtime.values()):
            return False
        return True

    return runtime_verify


def _build_public_runtime_verifier(runtime_verify):
    def diagnostic_verify_runtime_policy():
        return runtime_verify()

    diagnostic_verify_runtime_policy.__name__ = "verify_runtime_policy"
    diagnostic_verify_runtime_policy.__qualname__ = "verify_runtime_policy"
    return diagnostic_verify_runtime_policy


_candidate_runtime_verifier = _build_runtime_policy_verifier(
    gov, strict_core, reference_evidence, __file__
)
verify_runtime_policy = _build_public_runtime_verifier(_candidate_runtime_verifier)


'''

source = source[:start] + runtime_block + source[end:]

old_factory = "def _build_candidate_api():\n    issuer_token = object()\n"
new_factory = '''def _build_candidate_api(runtime_verify, strict_module, evidence_module):
    issuer_token = object()
    strict_value = STRICT
    favorable = {key: frozenset(values) for key, values in _FAVORABLE.items()}
    hashlib_module = hashlib
    json_module = json

    def canonical_result_digest(value):
        try:
            payload = json_module.dumps(
                dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
        except (TypeError, ValueError):
            return None
        return hashlib_module.sha256(payload).hexdigest()
'''
if old_factory not in source:
    raise SystemExit("Expected V7 candidate API factory not found")
source = source.replace(old_factory, new_factory, 1)

factory_start = source.index("def _build_candidate_api(runtime_verify, strict_module, evidence_module):\n")
factory_end = source.index("\n\n(\n    candidate_result_eligible,", factory_start)
factory = source[factory_start:factory_end]

factory = factory.replace("_canonical_result_digest(self)", "canonical_result_digest(self)")
factory = factory.replace("_canonical_result_digest(result)", "canonical_result_digest(result)")
factory = factory.replace("_FAVORABLE.get(kind, set())", "favorable.get(kind, frozenset())")
factory = factory.replace("result.get(\"evaluation_class\") != STRICT", "result.get(\"evaluation_class\") != strict_value")
factory = factory.replace('out["evaluation_class"] = STRICT', 'out["evaluation_class"] = strict_value')
factory = factory.replace("reference_evidence.lookup_reference_evidence", "evidence_module.lookup_reference_evidence")
factory = factory.replace("strict_core.", "strict_module.")
factory = factory.replace("verify_runtime_policy()", "runtime_verify()")
source = source[:factory_start] + factory + source[factory_end:]

old_invocation = ") = _build_candidate_api()\n\n# The factory owns the issuer token and all positive-sealing helpers. Remove the\n# only ordinary module-level handle capable of constructing another issuer set.\ndel _build_candidate_api"
new_invocation = ''') = _build_candidate_api(
    _candidate_runtime_verifier, strict_core, reference_evidence
)

# Candidate authority uses closure-held verifier/dependencies. The public verifier
# is diagnostic only. Delete temporary capability-bearing factories/handles after
# all governed entrypoints have captured them.
del _candidate_runtime_verifier
del _build_candidate_api
del _build_runtime_policy_verifier
del _build_public_runtime_verifier'''
if old_invocation not in source:
    raise SystemExit("Expected V7 candidate API invocation not found")
source = source.replace(old_invocation, new_invocation, 1)

BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V7_SEAL_CAPABILITY_MANIFEST":
    raise SystemExit("Expected V7 manifest before V8 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V8_VERIFIER_SUBSTITUTION_MANIFEST"
manifest["public_runtime_verifier_role"] = "DIAGNOSTIC_WRAPPER_ONLY"
manifest["candidate_runtime_verifier_policy"] = "CLOSURE_HELD_INTERNAL_VERIFIER"
manifest["candidate_dependencies_policy"] = "CLOSURE_HELD_ORIGINAL_MODULE_OBJECTS"
manifest["public_verifier_substitution_affects_candidate_authority"] = False
manifest["actual_dependency_tamper_fail_closed"] = True
manifest["candidate_entrypoints_capture_runtime_verifier"] = True
manifest["candidate_entrypoints_use_dynamic_runtime_verifier"] = False
manifest["candidate_entrypoints_use_closure_held_runtime_verifier"] = True
manifest["internal_verifier_module_handle_exported"] = False
manifest["remaining_verifier_boundary"] = "REFLECTIVE_CLOSURE_OR_INTERPRETER_COMPROMISE_OUTSIDE_V8_BOUNDED_THREAT_MODEL"
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V8_VERIFIER_SUBSTITUTION_REPAIR_GENERATED=1")
