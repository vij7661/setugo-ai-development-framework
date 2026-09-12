from __future__ import annotations

import hashlib
import importlib
import json
import marshal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "experiments" / "ecc_derived"
PUBLIC = MOD / "ecc_governance.py"
STRICT = MOD / "ecc_governance_strict.py"
BOUNDARY = MOD / "ecc_candidate_boundary.py"
EVIDENCE = MOD / "ecc_reference_evidence.py"
MANIFEST = MOD / "ecc_governance_trust_manifest.json"


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_sha(fn) -> str:
    return hashlib.sha256(marshal.dumps(fn.__code__)).hexdigest()


v4_core = PUBLIC.read_text(encoding="utf-8")
if "V4_HISTORICAL_RESULT_CLASSIFICATION_BOUNDARY" not in v4_core:
    raise SystemExit("Expected exact V4 core as V5 repair input")
if "requirement_candidate=False" not in v4_core:
    raise SystemExit("Expected V4 caller-selectable strict mode before V5 repair")

strict_append = r'''

# V5 internal candidate-only facades. This module is not the public candidate gate.
# These functions never issue candidate_eligible authority; only ecc_candidate_boundary may do that.
def assess_control_execution_candidate(control, event, *, candidate, action_id):
    return assess_control_execution(
        control, event, candidate=candidate, action_id=action_id, requirement_candidate=True
    )


def check_declared_executable_equivalence_candidate(declared, executable):
    return check_declared_executable_equivalence(declared, executable, requirement_candidate=True)


def qualify_role_binding_candidate(
    role,
    selected_model,
    envelope,
    required_capabilities,
    *,
    prior_binding=None,
    revalidated=True,
    require_semantic_evidence=False,
):
    return qualify_role_binding(
        role,
        selected_model,
        envelope,
        required_capabilities,
        prior_binding=prior_binding,
        revalidated=revalidated,
        require_semantic_evidence=require_semantic_evidence,
        requirement_candidate=True,
    )


def authorize_power_activation_candidate(
    manifest,
    approval,
    requested_powers,
    *,
    role,
    requested_resources=None,
    current_sequence=None,
):
    return authorize_power_activation(
        manifest,
        approval,
        requested_powers,
        role=role,
        requested_resources=requested_resources,
        current_sequence=current_sequence,
        requirement_candidate=True,
    )


def check_tool_configuration_candidate(expected, current):
    return check_tool_configuration(expected, current, requirement_candidate=True)


def classify_review_binding_candidate(binding):
    return classify_review_binding(binding, requirement_candidate=True)


def authorize_learning_promotion_candidate(proposal):
    return authorize_learning_promotion(proposal, requirement_candidate=True)
'''
STRICT.write_text(v4_core.rstrip() + strict_append + "\n", encoding="utf-8")

public_source = r'''from __future__ import annotations

# V5 public compatibility surface: historical evidence only.
# New candidate evaluation is intentionally absent from this module.
import ecc_governance_strict as _engine

HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"


def _historical(result):
    if not isinstance(result, dict):
        return result
    out = dict(result)
    out["evaluation_class"] = HISTORICAL_REFERENCE
    out.pop("candidate_eligible", None)
    out.pop("candidate_kind", None)
    return out


def assess_control_execution(control, event, *, candidate, action_id):
    return _historical(_engine.assess_control_execution(
        control, event, candidate=candidate, action_id=action_id
    ))


def check_declared_executable_equivalence(declared, executable):
    return _historical(_engine.check_declared_executable_equivalence(declared, executable))


def qualify_role_binding(
    role,
    selected_model,
    envelope,
    required_capabilities,
    *,
    prior_binding=None,
    revalidated=True,
    require_semantic_evidence=False,
):
    return _historical(_engine.qualify_role_binding(
        role,
        selected_model,
        envelope,
        required_capabilities,
        prior_binding=prior_binding,
        revalidated=revalidated,
        require_semantic_evidence=require_semantic_evidence,
    ))


def authorize_power_activation(
    manifest,
    approval,
    requested_powers,
    *,
    role,
    requested_resources=None,
    current_sequence=None,
):
    return _historical(_engine.authorize_power_activation(
        manifest,
        approval,
        requested_powers,
        role=role,
        requested_resources=requested_resources,
        current_sequence=current_sequence,
    ))


def check_tool_configuration(expected, current):
    return _historical(_engine.check_tool_configuration(expected, current))


def classify_review_binding(binding):
    return _historical(_engine.classify_review_binding(binding))


def authorize_learning_promotion(proposal):
    return _historical(_engine.authorize_learning_promotion(proposal))
'''
if "requirement_candidate" in public_source:
    raise SystemExit("V5 public core source accidentally exposes removed mode")
PUBLIC.write_text(public_source, encoding="utf-8")

reference_source = r'''from __future__ import annotations

import hashlib
import json

TRUST_SOURCE_CLASS = "REFERENCE_REPO_BOUND_SIMULATION_ONLY"
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def _sha256_json(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


_CONFIG_MATERIAL = {
    "tool_id": "t",
    "harness_id": "h",
    "transport": "stdio",
    "endpoint": None,
    "argv": ["x"],
    "permission_profile": "r",
    "credential_profile_fingerprint": "cred-fp",
}

_REFERENCE = {
    "ECC-V5-E1-POS": {
        "kind": "execution",
        "candidate": "shaA",
        "action_id": "act1",
        "control_id": "gate",
        "control_version": 3,
        "control_digest": "c" * 64,
        "process_identity": "hook@pid:trusted",
        "action_sequence": 10,
        "invocation_id": "inv1",
    },
    "ECC-V5-E2-POS": {
        "kind": "equivalence",
        "mode": "BLOCKING",
        "on_internal_error": "DENY",
        "candidate_binding": "EXACT",
        "contract_version": 2,
        "profile_digest": "p2",
        "scope": "ALL",
        "path_count": 1,
    },
    "ECC-V5-E3-POS": {
        "kind": "role",
        "harness_id": "h1",
        "runtime_version": "1",
        "config_digest": "d",
        "runtime_identity_digest": "r" * 64,
        "write_confinement": "NATIVE_ENFORCEMENT",
    },
    "ECC-V5-E4-POS": {
        "kind": "activation",
        "manifest_digest": "m",
        "project_id": "p1",
        "role": "R1",
        "approval_sequence": 7,
        "powers": ["WRITE"],
        "resources": ["repo"],
    },
    "ECC-V5-E5-POS": {
        "kind": "config",
        "tool_id": "t",
        "harness_id": "h",
        "transport": "stdio",
        "endpoint": None,
        "argv_digest": _sha256_json(["x"]),
        "canonical_digest": _sha256_json(_CONFIG_MATERIAL),
        "credential_profile_fingerprint": "cred-fp",
        "resolved_endpoint": "LOCAL_STDIO",
    },
}


def lookup_reference_evidence(kind, evidence_id):
    if not isinstance(evidence_id, str) or not evidence_id:
        return None
    record = _REFERENCE.get(evidence_id)
    if not isinstance(record, dict) or record.get("kind") != kind:
        return None
    return dict(record)
'''
EVIDENCE.write_text(reference_source, encoding="utf-8")

boundary_source = r'''from __future__ import annotations

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


def _file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code_sha(fn):
    try:
        return hashlib.sha256(marshal.dumps(fn.__code__)).hexdigest()
    except (AttributeError, TypeError, ValueError):
        return None


def _module_identity_ok(module, expected_path, expected_name):
    try:
        path = Path(module.__file__)
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
    if sys.modules.get(expected_name) is not module:
        return False
    spec = getattr(module, "__spec__", None)
    origin = getattr(spec, "origin", None)
    if not origin:
        return False
    try:
        if Path(origin).resolve(strict=True) != expected:
            return False
    except (OSError, RuntimeError):
        return False
    return True


def verify_runtime_policy():
    here = Path(__file__).resolve().parent
    manifest_path = here / "ecc_governance_trust_manifest.json"
    public_path = here / "ecc_governance.py"
    strict_path = here / "ecc_governance_strict.py"
    boundary_path = here / "ecc_candidate_boundary.py"
    evidence_path = here / "ecc_reference_evidence.py"
    for path in (manifest_path, public_path, strict_path, boundary_path, evidence_path):
        try:
            if path.is_symlink() or not path.is_file():
                return False
        except OSError:
            return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return False

    if manifest.get("record_type") != "ECC_GOVERNANCE_V5_CLOSED_BOUNDARY_MANIFEST":
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

    if not _module_identity_ok(gov, public_path, "ecc_governance"):
        return False
    if not _module_identity_ok(strict_core, strict_path, "ecc_governance_strict"):
        return False
    if not _module_identity_ok(reference_evidence, evidence_path, "ecc_reference_evidence"):
        return False
    try:
        if Path(__file__).resolve(strict=True) != boundary_path.resolve(strict=True):
            return False
    except (OSError, RuntimeError):
        return False

    expected_hashes = manifest.get("module_sha256") or {}
    actual_hashes = {
        "public_core": _file_sha(public_path),
        "strict_core": _file_sha(strict_path),
        "candidate_boundary": _file_sha(boundary_path),
        "reference_evidence": _file_sha(evidence_path),
    }
    if expected_hashes != actual_hashes:
        return False

    runtime = manifest.get("runtime_code_sha256") or {}
    strict_functions = {
        "strict.assess_control_execution_candidate": strict_core.assess_control_execution_candidate,
        "strict.check_declared_executable_equivalence_candidate": strict_core.check_declared_executable_equivalence_candidate,
        "strict.qualify_role_binding_candidate": strict_core.qualify_role_binding_candidate,
        "strict.authorize_power_activation_candidate": strict_core.authorize_power_activation_candidate,
        "strict.check_tool_configuration_candidate": strict_core.check_tool_configuration_candidate,
        "strict.classify_review_binding_candidate": strict_core.classify_review_binding_candidate,
        "strict.authorize_learning_promotion_candidate": strict_core.authorize_learning_promotion_candidate,
        "reference.lookup_reference_evidence": reference_evidence.lookup_reference_evidence,
    }
    actual_runtime = {name: _code_sha(fn) for name, fn in strict_functions.items()}
    if runtime != actual_runtime or any(value is None for value in actual_runtime.values()):
        return False
    return True


def candidate_result_eligible(result):
    if not isinstance(result, dict):
        return False
    if result.get("evaluation_class") != STRICT:
        return False
    if result.get("candidate_eligible") is not True:
        return False
    kind = result.get("candidate_kind")
    allowed = _FAVORABLE.get(kind)
    if not allowed or result.get("status") not in allowed:
        return False
    return True


def _typed(kind, result, eligible=False):
    out = dict(result) if isinstance(result, dict) else {"status": "CANDIDATE_RESULT_INVALID"}
    out["evaluation_class"] = STRICT
    out["candidate_kind"] = kind
    out["candidate_eligible"] = bool(eligible)
    return out


def _policy_failure(kind):
    base = {"status": "CANDIDATE_BOUNDARY_POLICY_INVALID"}
    if kind == "execution": base |= {"verified": False, "allowed": False}
    elif kind == "equivalence": base |= {"equivalent": False}
    elif kind == "role": base |= {"eligible": False}
    elif kind == "activation": base |= {"authorized": False}
    elif kind == "config": base |= {"current": False, "stale_dependents": True}
    elif kind == "review": base |= {"manual_review_threshold_contribution": 0, "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN"}
    elif kind == "learning": base |= {"promotable": False, "advisory_allowed": False}
    return _typed(kind, base, False)


def _independent_failure(kind, status):
    base = {"status": status}
    if kind == "execution": base |= {"verified": False, "allowed": False}
    elif kind == "equivalence": base |= {"equivalent": False}
    elif kind == "role": base |= {"eligible": False}
    elif kind == "activation": base |= {"authorized": False}
    elif kind == "config": base |= {"current": False, "stale_dependents": True}
    return _typed(kind, base, False)


def _core_favorable(kind, result):
    if not isinstance(result, dict) or result.get("status") not in _FAVORABLE.get(kind, set()):
        return False
    if kind == "execution": return result.get("verified") is True
    if kind == "equivalence": return result.get("equivalent") is True
    if kind == "role": return result.get("eligible") is True
    if kind == "activation": return result.get("authorized") is True
    if kind == "config": return result.get("current") is True
    return False


def _lookup(kind, evidence_id):
    return reference_evidence.lookup_reference_evidence(kind, evidence_id)


def _execution_evidence_ok(record, control, event, candidate, action_id):
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


def _equivalence_evidence_ok(record, declared, executable):
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


def _role_evidence_ok(record, envelope):
    caps = envelope.get("capabilities") or {}
    return bool(record) and all((
        record.get("harness_id") == envelope.get("harness_id"),
        record.get("runtime_version") == envelope.get("runtime_version"),
        record.get("config_digest") == envelope.get("config_digest"),
        record.get("runtime_identity_digest") == envelope.get("runtime_identity_digest"),
        record.get("write_confinement") == caps.get("write_confinement"),
    ))


def _activation_evidence_ok(record, manifest, approval, requested_powers, role, requested_resources, current_sequence):
    return bool(record) and all((
        record.get("manifest_digest") == manifest.get("digest") == approval.get("manifest_digest"),
        record.get("project_id") == manifest.get("project_id") == approval.get("project_id"),
        record.get("role") == role == manifest.get("role") == approval.get("role"),
        record.get("approval_sequence") == approval.get("approval_sequence") == current_sequence,
        set(record.get("powers") or []) == set(requested_powers or []),
        set(record.get("resources") or []) == set(requested_resources or []),
    ))


def _config_evidence_ok(record, expected, current):
    return bool(record) and all((
        expected.get("reference_evidence_id") == current.get("reference_evidence_id"),
        record.get("tool_id") == expected.get("tool_id") == current.get("tool_id"),
        record.get("harness_id") == expected.get("harness_id") == current.get("harness_id"),
        record.get("transport") == expected.get("transport") == current.get("transport"),
        record.get("endpoint") == expected.get("endpoint") == current.get("endpoint"),
        record.get("argv_digest") == expected.get("argv_digest") == current.get("argv_digest"),
        record.get("canonical_digest") == expected.get("canonical_digest") == current.get("canonical_digest"),
        record.get("credential_profile_fingerprint") == expected.get("credential_profile_fingerprint") == current.get("credential_profile_fingerprint"),
        record.get("resolved_endpoint") == expected.get("resolved_endpoint") == current.get("resolved_endpoint"),
    ))


def _finish_positive(kind, result):
    if not verify_runtime_policy():
        return _policy_failure(kind)
    return _typed(kind, result, True)


def assess_control_execution_candidate(control, event, *, candidate, action_id):
    kind = "execution"
    if not verify_runtime_policy(): return _policy_failure(kind)
    result = strict_core.assess_control_execution_candidate(control, event, candidate=candidate, action_id=action_id)
    if not _core_favorable(kind, result): return _typed(kind, result, False)
    evidence_id = event.get("reference_evidence_id") if isinstance(event, dict) else None
    record = _lookup(kind, evidence_id)
    if record is None: return _independent_failure(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
    if not _execution_evidence_ok(record, control, event, candidate, action_id): return _independent_failure(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
    return _finish_positive(kind, result)


def check_declared_executable_equivalence_candidate(declared, executable):
    kind = "equivalence"
    if not verify_runtime_policy(): return _policy_failure(kind)
    result = strict_core.check_declared_executable_equivalence_candidate(declared, executable)
    if not _core_favorable(kind, result): return _typed(kind, result, False)
    evidence_id = executable.get("reference_evidence_id") if isinstance(executable, dict) else None
    record = _lookup(kind, evidence_id)
    if record is None: return _independent_failure(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
    if not _equivalence_evidence_ok(record, declared, executable): return _independent_failure(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
    return _finish_positive(kind, result)


def qualify_role_binding_candidate(role, selected_model, envelope, required_capabilities, *, prior_binding=None, revalidated=True, require_semantic_evidence=False):
    kind = "role"
    if not verify_runtime_policy(): return _policy_failure(kind)
    result = strict_core.qualify_role_binding_candidate(role, selected_model, envelope, required_capabilities, prior_binding=prior_binding, revalidated=revalidated, require_semantic_evidence=require_semantic_evidence)
    if not _core_favorable(kind, result): return _typed(kind, result, False)
    evidence_id = envelope.get("reference_evidence_id") if isinstance(envelope, dict) else None
    record = _lookup(kind, evidence_id)
    if record is None: return _independent_failure(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
    if not _role_evidence_ok(record, envelope): return _independent_failure(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
    return _finish_positive(kind, result)


def authorize_power_activation_candidate(manifest, approval, requested_powers, *, role, requested_resources=None, current_sequence=None):
    kind = "activation"
    if not verify_runtime_policy(): return _policy_failure(kind)
    result = strict_core.authorize_power_activation_candidate(manifest, approval, requested_powers, role=role, requested_resources=requested_resources, current_sequence=current_sequence)
    if not _core_favorable(kind, result): return _typed(kind, result, False)
    evidence_id = approval.get("reference_evidence_id") if isinstance(approval, dict) else None
    record = _lookup(kind, evidence_id)
    if record is None: return _independent_failure(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
    if not _activation_evidence_ok(record, manifest, approval, requested_powers, role, requested_resources, current_sequence): return _independent_failure(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
    return _finish_positive(kind, result)


def check_tool_configuration_candidate(expected, current):
    kind = "config"
    if not verify_runtime_policy(): return _policy_failure(kind)
    result = strict_core.check_tool_configuration_candidate(expected, current)
    if not _core_favorable(kind, result): return _typed(kind, result, False)
    evidence_id = expected.get("reference_evidence_id") if isinstance(expected, dict) else None
    record = _lookup(kind, evidence_id)
    if record is None: return _independent_failure(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
    if not _config_evidence_ok(record, expected, current): return _independent_failure(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
    return _finish_positive(kind, result)


def classify_review_binding_candidate(binding):
    if not verify_runtime_policy(): return _policy_failure("review")
    result = strict_core.classify_review_binding_candidate(binding)
    out = _typed("review", result, False)
    out["manual_review_threshold_contribution"] = 0 if binding.get("evidence_class") == "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY" else out.get("manual_review_threshold_contribution", 0)
    return out


def authorize_learning_promotion_candidate(proposal):
    if not verify_runtime_policy(): return _policy_failure("learning")
    result = strict_core.authorize_learning_promotion_candidate(proposal)
    out = _typed("learning", result, False)
    out["promotable"] = False
    return out
'''
if "requirement_candidate=True" in boundary_source:
    raise SystemExit("V5 boundary source contains forbidden direct strict switch")
BOUNDARY.write_text(boundary_source, encoding="utf-8")

# Fresh-import the generated modules solely to bind current in-memory candidate dependencies.
sys.path.insert(0, str(MOD))
for name in ("ecc_candidate_boundary", "ecc_governance", "ecc_governance_strict", "ecc_reference_evidence"):
    sys.modules.pop(name, None)
strict_mod = importlib.import_module("ecc_governance_strict")
public_mod = importlib.import_module("ecc_governance")
evidence_mod = importlib.import_module("ecc_reference_evidence")
boundary_mod = importlib.import_module("ecc_candidate_boundary")

runtime_code = {
    "strict.assess_control_execution_candidate": code_sha(strict_mod.assess_control_execution_candidate),
    "strict.check_declared_executable_equivalence_candidate": code_sha(strict_mod.check_declared_executable_equivalence_candidate),
    "strict.qualify_role_binding_candidate": code_sha(strict_mod.qualify_role_binding_candidate),
    "strict.authorize_power_activation_candidate": code_sha(strict_mod.authorize_power_activation_candidate),
    "strict.check_tool_configuration_candidate": code_sha(strict_mod.check_tool_configuration_candidate),
    "strict.classify_review_binding_candidate": code_sha(strict_mod.classify_review_binding_candidate),
    "strict.authorize_learning_promotion_candidate": code_sha(strict_mod.authorize_learning_promotion_candidate),
    "reference.lookup_reference_evidence": code_sha(evidence_mod.lookup_reference_evidence),
}

manifest = {
    "record_type": "ECC_GOVERNANCE_V5_CLOSED_BOUNDARY_MANIFEST",
    "covers": [f"EXP-ECC-{i}" for i in range(1, 8)],
    "public_core_policy": "HISTORICAL_ONLY_NO_CALLER_STRICT_MODE",
    "candidate_boundary_policy": "ONLY_PUBLIC_CANDIDATE_ELIGIBILITY_ISSUER",
    "candidate_eligibility_policy": "BOUNDARY_MARKER_KIND_AND_FAVORABLE_STATUS_REQUIRED",
    "reference_evidence_trust_source": "REFERENCE_REPO_BOUND_SIMULATION_ONLY",
    "live_attestation_claimed": False,
    "independent_production_trust_root_claimed": False,
    "manual_review_threshold_contribution": 0,
    "authority_effect": "NONE_EVIDENCE_ONLY",
    "module_paths": {
        "public_core": "experiments/ecc_derived/ecc_governance.py",
        "strict_core": "experiments/ecc_derived/ecc_governance_strict.py",
        "candidate_boundary": "experiments/ecc_derived/ecc_candidate_boundary.py",
        "reference_evidence": "experiments/ecc_derived/ecc_reference_evidence.py",
    },
    "module_sha256": {
        "public_core": sha256_bytes(PUBLIC),
        "strict_core": sha256_bytes(STRICT),
        "candidate_boundary": sha256_bytes(BOUNDARY),
        "reference_evidence": sha256_bytes(EVIDENCE),
    },
    "runtime_code_sha256": runtime_code,
    "deferred_experiments": ["EXP-ECC-6", "EXP-ECC-7"],
    "remaining_external_boundary": "LIVE_PLATFORM_ATTESTATION_AND_INDEPENDENT_TRUST_SOURCE",
}
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("PUBLIC_SHA256=" + sha256_bytes(PUBLIC))
print("STRICT_SHA256=" + sha256_bytes(STRICT))
print("BOUNDARY_SHA256=" + sha256_bytes(BOUNDARY))
print("REFERENCE_EVIDENCE_SHA256=" + sha256_bytes(EVIDENCE))
print("MANIFEST_SHA256=" + sha256_bytes(MANIFEST))
print("V5_REPAIR_GENERATED=1")
