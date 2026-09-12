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
marker = "def _canonical_result_digest(value):\n"
if marker not in source:
    raise SystemExit("Expected V6 provenance tail marker not found")
prefix = source.split(marker, 1)[0]

# Keep all positive-provenance capabilities closure-local. Global helpers below are
# deliberately incapable of issuing candidate_eligible=True provenance.
tail = r'''def _canonical_result_digest(value):
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


def _build_candidate_api(runtime_verify):
    issuer_token = object()

    class CandidateEvaluationResult(dict):
        __slots__ = ("_issuer_token", "_sealed_digest")

        def __init__(self, payload, supplied_token):
            if supplied_token is not issuer_token:
                raise TypeError("candidate eligibility result may only be issued by governed entrypoints")
            super().__init__(payload)
            self._issuer_token = supplied_token
            self._sealed_digest = _canonical_result_digest(self)
            if self._sealed_digest is None:
                raise TypeError("candidate result is not canonically sealable")

        def __reduce_ex__(self, protocol):
            raise TypeError("process-local candidate provenance is intentionally non-picklable")

    CandidateEvaluationResult.__name__ = "_BoundaryIssuedCandidateResult"
    CandidateEvaluationResult.__qualname__ = "_BoundaryIssuedCandidateResult"

    def typed(kind, result, eligible=False):
        out = dict(result) if isinstance(result, dict) else {"status": "CANDIDATE_RESULT_INVALID"}
        out["evaluation_class"] = STRICT
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
        current = _canonical_result_digest(result)
        return isinstance(sealed, str) and sealed == current

    def core_favorable(kind, result):
        if not isinstance(result, dict) or result.get("status") not in _FAVORABLE.get(kind, set()):
            return False
        if kind == "execution": return result.get("verified") is True
        if kind == "equivalence": return result.get("equivalent") is True
        if kind == "role": return result.get("eligible") is True
        if kind == "activation": return result.get("authorized") is True
        if kind == "config": return result.get("current") is True
        return False

    def lookup(kind, evidence_id):
        return reference_evidence.lookup_reference_evidence(kind, evidence_id)

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
        if result.get("evaluation_class") != STRICT:
            return False
        if result.get("candidate_eligible") is not True:
            return False
        kind = result.get("candidate_kind")
        allowed = _FAVORABLE.get(kind)
        if not allowed or result.get("status") not in allowed:
            return False
        return True

    def assess_control_execution_candidate(control, event, *, candidate, action_id):
        kind = "execution"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_core.assess_control_execution_candidate(control, event, candidate=candidate, action_id=action_id)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = event.get("reference_evidence_id") if isinstance(event, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not execution_evidence_ok(record, control, event, candidate, action_id): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def check_declared_executable_equivalence_candidate(declared, executable):
        kind = "equivalence"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_core.check_declared_executable_equivalence_candidate(declared, executable)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = executable.get("reference_evidence_id") if isinstance(executable, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not equivalence_evidence_ok(record, declared, executable): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def qualify_role_binding_candidate(role, selected_model, envelope, required_capabilities, *, prior_binding=None, revalidated=True, require_semantic_evidence=False):
        kind = "role"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_core.qualify_role_binding_candidate(role, selected_model, envelope, required_capabilities, prior_binding=prior_binding, revalidated=revalidated, require_semantic_evidence=require_semantic_evidence)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = envelope.get("reference_evidence_id") if isinstance(envelope, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not role_evidence_ok(record, envelope): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def authorize_power_activation_candidate(manifest, approval, requested_powers, *, role, requested_resources=None, current_sequence=None):
        kind = "activation"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_core.authorize_power_activation_candidate(manifest, approval, requested_powers, role=role, requested_resources=requested_resources, current_sequence=current_sequence)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = approval.get("reference_evidence_id") if isinstance(approval, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not activation_evidence_ok(record, manifest, approval, requested_powers, role, requested_resources, current_sequence): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def check_tool_configuration_candidate(expected, current):
        kind = "config"
        if not runtime_verify(): return _policy_failure_unsealed(kind)
        result = strict_core.check_tool_configuration_candidate(expected, current)
        if not core_favorable(kind, result): return typed(kind, result, False)
        evidence_id = expected.get("reference_evidence_id") if isinstance(expected, dict) else None
        record = lookup(kind, evidence_id)
        if record is None: return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
        if not config_evidence_ok(record, expected, current): return _independent_failure_unsealed(kind, "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        return finish_positive(kind, result)

    def classify_review_binding_candidate(binding):
        if not runtime_verify(): return _policy_failure_unsealed("review")
        result = strict_core.classify_review_binding_candidate(binding)
        out = typed("review", result, False)
        out["manual_review_threshold_contribution"] = 0 if binding.get("evidence_class") == "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY" else out.get("manual_review_threshold_contribution", 0)
        return out

    def authorize_learning_promotion_candidate(proposal):
        if not runtime_verify(): return _policy_failure_unsealed("learning")
        result = strict_core.authorize_learning_promotion_candidate(proposal)
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
) = _build_candidate_api(verify_runtime_policy)

# The factory owns the issuer token and all positive-sealing helpers. Remove the
# only ordinary module-level handle capable of constructing another issuer set.
del _build_candidate_api
'''

BOUNDARY.write_text(prefix + tail, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V6_ELIGIBILITY_PROVENANCE_MANIFEST":
    raise SystemExit("Expected V6 manifest before V7 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V7_SEAL_CAPABILITY_MANIFEST"
manifest["seal_capability_policy"] = "POSITIVE_SEAL_CAPABILITY_CLOSURE_LOCAL_ONLY"
manifest["ordinary_module_access_can_mint_provenance"] = False
manifest["reflective_closure_extraction_resistance_claimed"] = False
manifest["interpreter_compromise_resistance_claimed"] = False
manifest["candidate_entrypoints_capture_runtime_verifier"] = True
manifest["remaining_seal_boundary"] = "REFLECTIVE_OR_INTERPRETER_LEVEL_EXTRACTION_OUTSIDE_V7_BOUNDED_THREAT_MODEL"
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V7_SEAL_CAPABILITY_REPAIR_GENERATED=1")
