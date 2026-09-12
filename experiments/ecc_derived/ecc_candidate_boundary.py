from __future__ import annotations

import hashlib
import json
import marshal
import sys
from pathlib import Path

import ecc_governance as gov
import ecc_governance_strict as strict_core
import ecc_reference_evidence as reference_evidence

STRICT = "REQUIREMENT_CANDIDATE"
HISTORICAL = "HISTORICAL_REFERENCE"
_COVERS = {f"EXP-ECC-{i}" for i in range(1, 8)}
_FAVORABLE = {
    "execution": {"VERIFIED", "VERIFIED_DENY"},
    "equivalence": {"EQUIVALENT"},
    "role": {"ROLE_BINDING_ELIGIBLE"},
    "activation": {"ACTIVATION_ALLOWED"},
    "config": {"TOOL_CONFIG_CURRENT"},
}


def _build_runtime_policy_verifier(gov_module, strict_module, evidence_module, boundary_file):
    sha256_fn = hashlib.sha256
    json_loads_fn = json.loads
    marshal_dumps_fn = marshal.dumps
    sys_modules = sys.modules
    path_type = Path
    path_read_text_fn = Path.read_text
    path_read_bytes_fn = Path.read_bytes
    path_resolve_fn = Path.resolve
    path_is_file_fn = Path.is_file
    path_is_symlink_fn = Path.is_symlink
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

    # V12: module-object identity is insufficient when candidate-authoritative
    # strict helpers dereference mutable attributes on those modules at runtime.
    # Bind the exact transitive primitive callables used by _sha256_json.
    strict_hashlib_sha256_fn = strict_module.hashlib.sha256
    strict_json_dumps_fn = strict_module.json.dumps

    boundary_path = path_resolve_fn(path_type(boundary_file))
    here = boundary_path.parent
    manifest_path = here / "ecc_governance_trust_manifest.json"
    public_path = here / "ecc_governance.py"
    strict_path = here / "ecc_governance_strict.py"
    evidence_path = here / "ecc_reference_evidence.py"

    def file_sha(path):
        return sha256_fn(path_read_bytes_fn(path)).hexdigest()

    def code_sha(fn):
        try:
            return sha256_fn(marshal_dumps_fn(fn.__code__)).hexdigest()
        except (AttributeError, TypeError, ValueError):
            return None

    def freeze_value(value):
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
        try:
            path = path_type(module.__file__)
            resolved = path_resolve_fn(path, strict=True)
            expected = path_resolve_fn(expected_path, strict=True)
        except (AttributeError, OSError, RuntimeError):
            return False
        if path_is_symlink_fn(path) or path_is_symlink_fn(expected_path):
            return False
        if resolved != expected:
            return False
        if module.__name__ != expected_name:
            return False
        if sys_modules.get(expected_name) is not module:
            return False
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        if not origin:
            return False
        try:
            if path_resolve_fn(path_type(origin), strict=True) != expected:
                return False
        except (OSError, RuntimeError):
            return False
        return True

    def runtime_verify():
        for path in (manifest_path, public_path, strict_path, boundary_path, evidence_path):
            try:
                if path_is_symlink_fn(path) or not path_is_file_fn(path):
                    return False
            except OSError:
                return False
        try:
            manifest = json_loads_fn(path_read_text_fn(manifest_path, encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return False

        if manifest.get("record_type") != "ECC_GOVERNANCE_V12_TRANSITIVE_PRIMITIVE_INTEGRITY_MANIFEST":
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
        if manifest.get("verifier_primitive_policy") != "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("seal_primitive_policy") != "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("path_primitive_policy") != "EXACT_PATH_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("public_path_method_alias_controls_candidate_authority") is not False:
            return False
        if manifest.get("module_global_dependency_policy") != "RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION":
            return False
        if manifest.get("transitive_module_attribute_policy") != "EXACT_STRICT_DIGEST_PRIMITIVE_CALLABLES_BOUND_AT_INITIALIZATION":
            return False
        if set(manifest.get("captured_strict_transitive_primitives") or []) != {
            "strict_core.hashlib.sha256",
            "strict_core.json.dumps",
        }:
            return False
        if set(manifest.get("config_reference_semantic_fields") or []) != {
            "permission_profile",
            "argv",
        }:
            return False
        if manifest.get("checked_entrypoint_identity_policy") != "EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED":
            return False
        if manifest.get("public_covers_global_controls_candidate_authority") is not False:
            return False
        if set(manifest.get("captured_path_primitives") or []) != {
            "Path.read_text",
            "Path.read_bytes",
            "Path.resolve",
            "Path.is_file",
            "Path.is_symlink",
        }:
            return False
        if manifest.get("public_json_alias_controls_candidate_authority") is not False:
            return False
        if manifest.get("public_marshal_alias_controls_candidate_authority") is not False:
            return False
        if manifest.get("public_core_policy") != "HISTORICAL_ONLY_NO_CALLER_STRICT_MODE":
            return False
        if manifest.get("candidate_boundary_policy") != "ONLY_PUBLIC_CANDIDATE_ELIGIBILITY_ISSUER":
            return False
        if manifest.get("reference_evidence_trust_source") != "REFERENCE_REPO_BOUND_SIMULATION_ONLY":
            return False
        if manifest.get("authority_effect") != "NONE_EVIDENCE_ONLY":
            return False
        if frozenset(manifest.get("covers") or []) != covers_expected:
            return False

        if not entrypoint_identity_ok():
            return False
        # V12: fail closed if the exact digest primitives dereferenced through
        # strict module globals have changed while the module objects themselves
        # remain identical.
        if getattr(strict_module.hashlib, "sha256", None) is not strict_hashlib_sha256_fn:
            return False
        if getattr(strict_module.json, "dumps", None) is not strict_json_dumps_fn:
            return False
        if not dependency_globals_ok():
            return False

        if not module_identity_ok(gov_module, public_path, "ecc_governance"):
            return False
        if not module_identity_ok(strict_module, strict_path, "ecc_governance_strict"):
            return False
        if not module_identity_ok(evidence_module, evidence_path, "ecc_reference_evidence"):
            return False
        try:
            if path_resolve_fn(boundary_path, strict=True) != path_resolve_fn(path_type(boundary_file), strict=True):
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
            "strict.assess_control_execution_candidate": strict_entrypoints["assess_control_execution_candidate"],
            "strict.check_declared_executable_equivalence_candidate": strict_entrypoints["check_declared_executable_equivalence_candidate"],
            "strict.qualify_role_binding_candidate": strict_entrypoints["qualify_role_binding_candidate"],
            "strict.authorize_power_activation_candidate": strict_entrypoints["authorize_power_activation_candidate"],
            "strict.check_tool_configuration_candidate": strict_entrypoints["check_tool_configuration_candidate"],
            "strict.classify_review_binding_candidate": strict_entrypoints["classify_review_binding_candidate"],
            "strict.authorize_learning_promotion_candidate": strict_entrypoints["authorize_learning_promotion_candidate"],
            "reference.lookup_reference_evidence": reference_lookup_fn,
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


def _canonical_result_digest(value):
    try:
        payload = json.dumps(
            dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(payload).hexdigest()


def _unsealed(kind, result):
    out = dict(result) if isinstance(result, dict) else {"status": "CANDIDATE_RESULT_INVALID"}
    out["evaluation_class"] = STRICT
    out["candidate_kind"] = kind
    out["candidate_eligible"] = False
    return out


def _policy_failure_unsealed(kind):
    base = {"status": "CANDIDATE_BOUNDARY_POLICY_INVALID"}
    if kind == "execution": base |= {"verified": False, "allowed": False}
    elif kind == "equivalence": base |= {"equivalent": False}
    elif kind == "role": base |= {"eligible": False}
    elif kind == "activation": base |= {"authorized": False}
    elif kind == "config": base |= {"current": False, "stale_dependents": True}
    elif kind == "review": base |= {"manual_review_threshold_contribution": 0, "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN"}
    elif kind == "learning": base |= {"promotable": False, "advisory_allowed": False}
    return _unsealed(kind, base)


def _independent_failure_unsealed(kind, status):
    base = {"status": status}
    if kind == "execution": base |= {"verified": False, "allowed": False}
    elif kind == "equivalence": base |= {"equivalent": False}
    elif kind == "role": base |= {"eligible": False}
    elif kind == "activation": base |= {"authorized": False}
    elif kind == "config": base |= {"current": False, "stale_dependents": True}
    return _unsealed(kind, base)


def _build_candidate_api(runtime_verify, strict_module, evidence_module):
    issuer_token = object()
    strict_value = STRICT
    favorable = {key: frozenset(values) for key, values in _FAVORABLE.items()}
    sha256_fn = hashlib.sha256
    json_dumps_fn = json.dumps

    def canonical_result_digest(value):
        try:
            payload = json_dumps_fn(
                dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
        except (TypeError, ValueError):
            return None
        return sha256_fn(payload).hexdigest()

    class CandidateEvaluationResult(dict):
        __slots__ = ("_issuer_token", "_sealed_digest")

        def __init__(self, payload, supplied_token):
            if supplied_token is not issuer_token:
                raise TypeError("candidate eligibility result may only be issued by governed entrypoints")
            super().__init__(payload)
            self._issuer_token = supplied_token
            self._sealed_digest = canonical_result_digest(self)
            if self._sealed_digest is None:
                raise TypeError("candidate result is not canonically sealable")

        def __reduce_ex__(self, protocol):
            raise TypeError("process-local candidate provenance is intentionally non-picklable")

    CandidateEvaluationResult.__name__ = "_BoundaryIssuedCandidateResult"
    CandidateEvaluationResult.__qualname__ = "_BoundaryIssuedCandidateResult"

    def typed(kind, result, eligible=False):
        out = dict(result) if isinstance(result, dict) else {"status": "CANDIDATE_RESULT_INVALID"}
        out["evaluation_class"] = strict_value
        out["candidate_kind"] = kind
        out["candidate_eligible"] = bool(eligible)
        if not eligible:
            return out
        return CandidateEvaluationResult(out, issuer_token)

    def valid_provenance(result):
        if type(result) is not CandidateEvaluationResult:
            return False
        if getattr(result, "_issuer_token", None) is not issuer_token:
            return False
        sealed = getattr(result, "_sealed_digest", None)
        current = canonical_result_digest(result)
        return isinstance(sealed, str) and sealed == current

    def core_favorable(kind, result):
        if not isinstance(result, dict) or result.get("status") not in favorable.get(kind, frozenset()):
            return False
        if kind == "execution": return result.get("verified") is True
        if kind == "equivalence": return result.get("equivalent") is True
        if kind == "role": return result.get("eligible") is True
        if kind == "activation": return result.get("authorized") is True
        if kind == "config": return result.get("current") is True
        return False

    def lookup(kind, evidence_id):
        return evidence_module.lookup_reference_evidence(kind, evidence_id)

    def execution_evidence_ok(record, control, event, candidate, action_id):
        return bool(record) and all((
            record.get("candidate") == candidate,
            record.get("action_id") == action_id,
            record.get("control_id") == control.get("control_id") == event.get("control_id"),
            record.get("control_version") == control.get("version") == event.get("version"),
            record.get("control_digest") == control.get("digest") == event.get("control_digest"),
            record.get("process_identity") == event.get("process_identity") == event.get("expected_process_identity"),
            record.get("action_sequence") == event.get("verified_action_sequence") == event.get("executed_action_sequence"),
            record.get("invocation_id") == event.get("invocation_id"),
        ))

    def equivalence_evidence_ok(record, declared, executable):
        paths = executable.get("paths") or []
        return bool(record) and all((
            record.get("mode") == declared.get("mode") == executable.get("runtime_mode"),
            record.get("on_internal_error") == declared.get("on_internal_error") == executable.get("runtime_on_internal_error"),
            record.get("candidate_binding") == declared.get("candidate_binding"),
            record.get("contract_version") == declared.get("contract_version"),
            record.get("profile_digest") == declared.get("profile_digest"),
            record.get("scope") == declared.get("scope"),
            record.get("path_count") == len(paths),
            bool(paths) and all(path.get("machine_verified") is True for path in paths),
        ))

    def role_evidence_ok(record, envelope):
        caps = envelope.get("capabilities") or {}
        return bool(record) and all((
            record.get("harness_id") == envelope.get("harness_id"),
            record.get("runtime_version") == envelope.get("runtime_version"),
            record.get("config_digest") == envelope.get("config_digest"),
            record.get("runtime_identity_digest") == envelope.get("runtime_identity_digest"),
            record.get("write_confinement") == caps.get("write_confinement"),
        ))

    def activation_evidence_ok(record, manifest, approval, requested_powers, role, requested_resources, current_sequence):
        return bool(record) and all((
            record.get("manifest_digest") == manifest.get("digest") == approval.get("manifest_digest"),
            record.get("project_id") == manifest.get("project_id") == approval.get("project_id"),
            record.get("role") == role == manifest.get("role") == approval.get("role"),
            record.get("approval_sequence") == approval.get("approval_sequence") == current_sequence,
            set(record.get("powers") or []) == set(requested_powers or []),
            set(record.get("resources") or []) == set(requested_resources or []),
        ))

    def config_evidence_ok(record, expected, current):
        return bool(record) and all((
            expected.get("reference_evidence_id") == current.get("reference_evidence_id"),
            record.get("tool_id") == expected.get("tool_id") == current.get("tool_id"),
            record.get("harness_id") == expected.get("harness_id") == current.get("harness_id"),
            record.get("transport") == expected.get("transport") == current.get("transport"),
            record.get("endpoint") == expected.get("endpoint") == current.get("endpoint"),
            record.get("permission_profile") == expected.get("permission_profile") == current.get("permission_profile"),
            record.get("argv") == expected.get("argv") == current.get("argv"),
            record.get("argv_digest") == expected.get("argv_digest") == current.get("argv_digest"),
            record.get("canonical_digest") == expected.get("canonical_digest") == current.get("canonical_digest"),
            record.get("credential_profile_fingerprint") == expected.get("credential_profile_fingerprint") == current.get("credential_profile_fingerprint"),
            record.get("resolved_endpoint") == expected.get("resolved_endpoint") == current.get("resolved_endpoint"),
        ))

    def finish_positive(kind, result):
        if not runtime_verify():
            return _policy_failure_unsealed(kind)
        return typed(kind, result, True)

    def candidate_result_eligible(result):
        if not runtime_verify():
            return False
        if not valid_provenance(result):
            return False
        if result.get("evaluation_class") != strict_value:
            return False
        if result.get("candidate_eligible") is not True:
            return False
        kind = result.get("candidate_kind")
        allowed = favorable.get(kind)
        if not allowed or result.get("status") not in allowed:
            return False
        return True

    def assess_control_execution_candidate(control, event, *, candidate, action_id):
        kind = "execution"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_module.assess_control_execution_candidate(control, event, candidate=candidate, action_id=action_id)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = event.get("reference_evidence_id") if isinstance(event, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not execution_evidence_ok(record, control, event, candidate, action_id): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def check_declared_executable_equivalence_candidate(declared, executable):
        kind = "equivalence"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_module.check_declared_executable_equivalence_candidate(declared, executable)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = executable.get("reference_evidence_id") if isinstance(executable, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not equivalence_evidence_ok(record, declared, executable): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def qualify_role_binding_candidate(role, selected_model, envelope, required_capabilities, *, prior_binding=None, revalidated=True, require_semantic_evidence=False):
        kind = "role"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_module.qualify_role_binding_candidate(role, selected_model, envelope, required_capabilities, prior_binding=prior_binding, revalidated=revalidated, require_semantic_evidence=require_semantic_evidence)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = envelope.get("reference_evidence_id") if isinstance(envelope, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not role_evidence_ok(record, envelope): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def authorize_power_activation_candidate(manifest, approval, requested_powers, *, role, requested_resources=None, current_sequence=None):
        kind = "activation"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_module.authorize_power_activation_candidate(manifest, approval, requested_powers, role=role, requested_resources=requested_resources, current_sequence=current_sequence)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = approval.get("reference_evidence_id") if isinstance(approval, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not activation_evidence_ok(record, manifest, approval, requested_powers, role, requested_resources, current_sequence): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def check_tool_configuration_candidate(expected, current):
        kind = "config"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_module.check_tool_configuration_candidate(expected, current)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = expected.get("reference_evidence_id") if isinstance(expected, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not config_evidence_ok(record, expected, current): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def classify_review_binding_candidate(binding):
        if not runtime_verify(): return _policy_failure_unsealed("review")
        result = strict_module.classify_review_binding_candidate(binding)
        out = typed("review", result, False)
        out["manual_review_threshold_contribution"] = 0 if binding.get("evidence_class") == "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY" else out.get("manual_review_threshold_contribution", 0)
        return out

    def authorize_learning_promotion_candidate(proposal):
        if not runtime_verify(): return _policy_failure_unsealed("learning")
        result = strict_module.authorize_learning_promotion_candidate(proposal)
        out = typed("learning", result, False)
        out["promotable"] = False
        return out

    return (
        candidate_result_eligible,
        assess_control_execution_candidate,
        check_declared_executable_equivalence_candidate,
        qualify_role_binding_candidate,
        authorize_power_activation_candidate,
        check_tool_configuration_candidate,
        classify_review_binding_candidate,
        authorize_learning_promotion_candidate,
    )


(
    candidate_result_eligible,
    assess_control_execution_candidate,
    check_declared_executable_equivalence_candidate,
    qualify_role_binding_candidate,
    authorize_power_activation_candidate,
    check_tool_configuration_candidate,
    classify_review_binding_candidate,
    authorize_learning_promotion_candidate,
) = _build_candidate_api(
    _candidate_runtime_verifier, strict_core, reference_evidence
)

# Candidate authority uses closure-held verifier/dependencies. The public verifier
# is diagnostic only. Delete temporary capability-bearing factories/handles after
# all governed entrypoints have captured them.
del _candidate_runtime_verifier
del _build_candidate_api
del _build_runtime_policy_verifier
del _build_public_runtime_verifier
