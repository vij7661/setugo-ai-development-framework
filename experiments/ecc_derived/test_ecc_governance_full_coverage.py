from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ecc_governance import (  # noqa: E402
    assess_control_execution,
    authorize_learning_promotion,
    authorize_power_activation,
    check_declared_executable_equivalence,
    check_tool_configuration,
    classify_review_binding,
    qualify_role_binding,
)

CASE_IDS = [
    *[f"E1-{i:02d}" for i in range(1, 11)], "E1-P1", "E1-P2", "E1-P3",
    *[f"E2-{i:02d}" for i in range(1, 9)], "E2-P1", "E2-P2", "E2-P3",
    *[f"E3-{i:02d}" for i in range(1, 9)], "E3-P1", "E3-P2", "E3-P3",
    *[f"E4-{i:02d}" for i in range(1, 9)], "E4-P1", "E4-P2", "E4-P3",
    *[f"E5-{i:02d}" for i in range(1, 10)], "E5-P1", "E5-P2", "E5-P3",
    *[f"E6-{i:02d}" for i in range(1, 11)], "E6-P1", "E6-P2", "E6-P3", "E6-P4",
    *[f"E7-{i:02d}" for i in range(1, 11)], "E7-P1", "E7-P2", "E7-P3", "E7-P4",
]

assert len(CASE_IDS) == 86 and len(set(CASE_IDS)) == 86


def _control():
    return {"control_id": "hook-A", "version": "v1", "digest": "sha-control", "required": True}


def _event():
    return {
        "control_id": "hook-A", "version": "v1", "control_digest": "sha-control",
        "candidate": "cand-1", "action_id": "act-1", "invocation_id": "inv-1",
        "input_digest": "in-1", "result_digest": "out-1", "started": True,
        "result_recorded": True, "execution_ok": True, "script_present": True,
        "input_valid": True, "authoritative": True, "evidence_integrity": True,
        "decision": "ALLOW", "acknowledgement": "RECEIVED", "reconciled": False,
    }


def _declared():
    return {
        "mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT",
        "disable_paths": [], "contract_version": "1", "profile_digest": "prof-1",
        "scope": ["read", "write"],
    }


def _executable():
    return copy.deepcopy(_declared()) | {
        "paths": [{"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT"}],
    }


def _envelope():
    return {
        "harness_id": "h1", "runtime_version": "1.2.0", "qualified_runtime_version": "1.2.0",
        "config_digest": "cfg-1", "qualified_config_digest": "cfg-1", "complete": True,
        "capabilities": {
            "read_only_review": "NATIVE_ENFORCEMENT",
            "filesystem_write": "NATIVE_ENFORCEMENT",
            "review_isolation": "NATIVE_ENFORCEMENT",
        },
        "semantic_evidence": {"read_only_review": True, "filesystem_write": True, "review_isolation": True},
    }


def _manifest():
    return {
        "manifest_id": "p1", "digest": "m1", "powers": ["read_files", "write_files"],
        "role": "R1", "resources": ["mcp://server-a"], "revoked": False,
        "expires_sequence": 100,
    }


def _approval():
    return {
        "manifest_digest": "m1", "role": "R1", "approved_powers": ["read_files", "write_files"],
        "approved_resources": ["mcp://server-a"], "approved": True, "approval_sequence": 10,
    }


def _cfg():
    return {
        "tool_id": "mcp-a", "harness_id": "h1", "transport": "stdio", "endpoint": None,
        "argv_digest": "argv-1", "permission_profile": "read", "credential_profile": "cp1",
        "canonical_digest": "cfg-a", "semantic_digest": "semantic-a", "read_ok": True,
    }


def _binding():
    return {
        "candidate": "cand-1", "packet_digest": "pkt-1", "consented_packet_digest": "pkt-1",
        "reviewer_slot": "R2", "evidence_bound_slot": "R2", "selected_model": "model-a",
        "role_binding_model": "model-a", "selected_provider": "provider-a", "returned_provider": "provider-a",
        "gateway": None, "evidence_class": "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY",
        "packet_current": True, "context_isolation_evidenced": True, "transport_ok": True,
        "transport_enabled": True, "packet_data_classes": ["candidate", "tests"],
        "permitted_data_classes": ["candidate", "tests"],
    }


def _proposal():
    return {
        "proposal_id": "lp1", "scope": "project-a", "target_scope": "project-a", "confidence": 0.99,
        "source_verified": False, "independent_support": False, "governed_approval": False,
        "parent_retracted": False, "artifact_digest": "a1", "reviewed_digest": "a1",
        "requested_authority": [], "explicit_authority_grant": False, "stale": False,
        "conflicts_governed": False, "prior_rejection": False, "history_preserved": True,
    }


def run_case(case_id: str) -> bool:
    # EXP-ECC-1
    if case_id == "E1-01":
        return assess_control_execution(_control(), None, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_NOT_INVOKED"
    if case_id == "E1-02":
        e = _event(); e["execution_ok"] = False; e["error"] = "wrapper exception"
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_EXECUTION_FAILED"
    if case_id == "E1-03":
        e = _event(); e["script_present"] = False
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_EXECUTION_FAILED"
    if case_id == "E1-04":
        e = _event(); e["input_valid"] = False
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_EVIDENCE_INVALID"
    if case_id == "E1-05":
        e = _event(); e["version"] = "v0"
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_VERSION_MISMATCH"
    if case_id == "E1-06":
        e = _event(); e["action_id"] = "act-other"
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_EVIDENCE_INVALID"
    if case_id == "E1-07":
        e = _event(); e["result_recorded"] = False
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_RESULT_UNKNOWN"
    if case_id == "E1-08":
        e = _event(); e["authoritative"] = False
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_EVIDENCE_INVALID"
    if case_id == "E1-09":
        return assess_control_execution(_control(), None, candidate="cand-1", action_id="act-1")["verified"] is False
    if case_id == "E1-10":
        e = _event(); e["evidence_integrity"] = False
        return assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")["status"] == "CONTROL_EVIDENCE_INVALID"
    if case_id == "E1-P1":
        return assess_control_execution(_control(), _event(), candidate="cand-1", action_id="act-1")["status"] == "VERIFIED"
    if case_id == "E1-P2":
        denied = _event(); denied["decision"] = "DENY"
        r1 = assess_control_execution(_control(), denied, candidate="cand-1", action_id="act-1")
        r2 = assess_control_execution(_control(), _event(), candidate="cand-1", action_id="act-1")
        return r1.get("status") == "VERIFIED_DENY" and r1.get("allowed") is False and r2.get("status") == "VERIFIED"
    if case_id == "E1-P3":
        e = _event(); e["acknowledgement"] = "LOST"; e["reconciled"] = True
        r = assess_control_execution(_control(), e, candidate="cand-1", action_id="act-1")
        return r.get("status") == "VERIFIED" and r.get("invocation_id") == "inv-1"

    # EXP-ECC-2
    if case_id == "E2-01":
        d = _declared(); x = _executable(); x["on_internal_error"] = "ALLOW"
        return check_declared_executable_equivalence(d, x)["status"] == "ENFORCEMENT_MISMATCH"
    if case_id == "E2-02":
        d = _declared(); x = _executable(); x["disable_paths"] = ["ENV:SKIP_GUARD"]
        return check_declared_executable_equivalence(d, x)["equivalent"] is False
    if case_id == "E2-03":
        d = _declared(); x = _executable(); x["candidate_binding"] = "BRANCH_ONLY"
        return check_declared_executable_equivalence(d, x)["equivalent"] is False
    if case_id == "E2-04":
        d = _declared(); x = _executable(); x["mode"] = "ADVISORY"
        return check_declared_executable_equivalence(d, x)["equivalent"] is False
    if case_id == "E2-05":
        d = _declared(); x = _executable(); x["profile_digest"] = "prof-changed"
        return check_declared_executable_equivalence(d, x)["equivalent"] is False
    if case_id == "E2-06":
        d = _declared(); x = _executable(); d["mode"] = "BLOCKING"; x["mode"] = "ADVISORY"
        return check_declared_executable_equivalence(d, x)["status"] == "ENFORCEMENT_MISMATCH"
    if case_id == "E2-07":
        d = _declared(); x = _executable(); x["paths"].append({"mode": "ADVISORY", "on_internal_error": "ALLOW", "candidate_binding": "NONE"})
        return check_declared_executable_equivalence(d, x)["equivalent"] is False
    if case_id == "E2-08":
        d = _declared(); x = _executable(); x["scope"] = ["read"]
        return check_declared_executable_equivalence(d, x)["equivalent"] is False
    if case_id == "E2-P1":
        d = _declared(); x = _executable()
        return check_declared_executable_equivalence(d, x)["equivalent"] is True
    if case_id == "E2-P2":
        d = _declared(); x = _executable(); d["mode"] = x["mode"] = "ADVISORY"; d["on_internal_error"] = x["on_internal_error"] = "ALLOW"; d["candidate_binding"] = x["candidate_binding"] = "NONE"; x["paths"] = [{"mode": "ADVISORY", "on_internal_error": "ALLOW", "candidate_binding": "NONE"}]
        return check_declared_executable_equivalence(d, x)["equivalent"] is True
    if case_id == "E2-P3":
        d = _declared(); x = _executable(); d["contract_version"] = x["contract_version"] = "2"; d["profile_digest"] = x["profile_digest"] = "prof-2"
        return check_declared_executable_equivalence(d, x)["equivalent"] is True

    # EXP-ECC-3
    if case_id == "E3-01":
        e = _envelope(); e["capabilities"]["read_only_review"] = "INSTRUCTION_ONLY"
        return qualify_role_binding("R2", "model-x", e, {"read_only_review": "NATIVE_ENFORCEMENT"})["status"] == "HARNESS_CAPABILITY_INSUFFICIENT"
    if case_id == "E3-02":
        e = _envelope(); e["runtime_version"] = "1.3.0"
        return qualify_role_binding("R1", "model-x", e, {"filesystem_write": "NATIVE_ENFORCEMENT"})["status"] == "HARNESS_QUALIFICATION_STALE"
    if case_id == "E3-03":
        e = _envelope(); prior = {"role": "R1", "selected_model": "model-old", "harness_id": "h1"}
        return qualify_role_binding("R1", "model-new", e, {"filesystem_write": "NATIVE_ENFORCEMENT"}, prior_binding=prior, revalidated=False)["status"] == "ROLE_BINDING_CHANGE_REVALIDATION_REQUIRED"
    if case_id == "E3-04":
        e = _envelope(); prior = {"role": "R1", "selected_model": "model-x", "harness_id": "h0"}
        return qualify_role_binding("R1", "model-x", e, {"filesystem_write": "NATIVE_ENFORCEMENT"}, prior_binding=prior, revalidated=False)["status"] == "ROLE_BINDING_CHANGE_REVALIDATION_REQUIRED"
    if case_id == "E3-05":
        e = _envelope(); e["complete"] = False
        return qualify_role_binding("R2", "model-x", e, {"read_only_review": "NATIVE_ENFORCEMENT"})["status"] == "HARNESS_CAPABILITY_UNKNOWN"
    if case_id == "E3-06":
        e = _envelope(); e["semantic_evidence"]["read_only_review"] = False
        return qualify_role_binding("R2", "model-x", e, {"read_only_review": "NATIVE_ENFORCEMENT"}, require_semantic_evidence=True)["status"] == "HARNESS_CAPABILITY_UNVERIFIED"
    if case_id == "E3-07":
        e = _envelope(); e["config_digest"] = "cfg-new"
        return qualify_role_binding("R1", "model-x", e, {"filesystem_write": "NATIVE_ENFORCEMENT"})["status"] == "HARNESS_QUALIFICATION_STALE"
    if case_id == "E3-08":
        e = _envelope(); e["capabilities"]["review_isolation"] = "UNSUPPORTED"
        return qualify_role_binding("R3", "model-y", e, {"read_only_review": "NATIVE_ENFORCEMENT", "review_isolation": "NATIVE_ENFORCEMENT"})["status"] == "HARNESS_CAPABILITY_INSUFFICIENT"
    if case_id == "E3-P1":
        return qualify_role_binding("R1", "user-selected-model", _envelope(), {"filesystem_write": "NATIVE_ENFORCEMENT"})["status"] == "ROLE_BINDING_ELIGIBLE"
    if case_id == "E3-P2":
        e = _envelope(); e["capabilities"]["read_only_review"] = "INSTRUCTION_ONLY"
        return qualify_role_binding("R2", "model-x", e, {"read_only_review": "INSTRUCTION_ONLY"})["status"] == "ROLE_BINDING_ELIGIBLE"
    if case_id == "E3-P3":
        e = _envelope(); e["runtime_version"] = e["qualified_runtime_version"] = "1.3.0"; e["config_digest"] = e["qualified_config_digest"] = "cfg-2"
        return qualify_role_binding("R1", "model-x", e, {"filesystem_write": "NATIVE_ENFORCEMENT"})["status"] == "ROLE_BINDING_ELIGIBLE"

    # EXP-ECC-4
    if case_id == "E4-01":
        m = _manifest(); m["digest"] = "m2"; m["powers"].append("network_egress")
        return authorize_power_activation(m, _approval(), ["network_egress"], role="R1", current_sequence=20)["status"] == "ACTIVATION_BINDING_MISMATCH"
    if case_id == "E4-02":
        a = _approval(); a["approved_powers"] = ["read_files"]
        return authorize_power_activation(_manifest(), a, ["write_files"], role="R1", current_sequence=20)["status"] == "ACTIVATION_SCOPE_EXCEEDED"
    if case_id == "E4-03":
        a = _approval(); a["approved_resources"] = ["mcp://server-b"]
        return authorize_power_activation(_manifest(), a, ["read_files"], role="R1", requested_resources=["mcp://server-a"], current_sequence=20)["status"] == "ACTIVATION_RESOURCE_SCOPE_EXCEEDED"
    if case_id == "E4-04":
        return authorize_power_activation(_manifest(), None, ["write_files"], role="R1", current_sequence=20)["status"] == "ACTIVATION_NOT_APPROVED"
    if case_id == "E4-05":
        m = _manifest(); m["digest"] = "m-expanded"; m["powers"].append("process_exec")
        return authorize_power_activation(m, _approval(), ["process_exec"], role="R1", current_sequence=20)["status"] == "ACTIVATION_BINDING_MISMATCH"
    if case_id == "E4-06":
        a = _approval(); a["approved"] = False; a["user_silence"] = True
        return authorize_power_activation(_manifest(), a, ["read_files"], role="R1", current_sequence=20)["status"] == "ACTIVATION_NOT_APPROVED"
    if case_id == "E4-07":
        return authorize_power_activation(_manifest(), _approval(), ["read_files"], role="R2", current_sequence=20)["status"] == "ACTIVATION_BINDING_MISMATCH"
    if case_id == "E4-08":
        m = _manifest(); m["expires_sequence"] = 15
        return authorize_power_activation(m, _approval(), ["read_files"], role="R1", current_sequence=20)["status"] == "ACTIVATION_EXPIRED"
    if case_id == "E4-P1":
        return authorize_power_activation(_manifest(), _approval(), ["read_files"], role="R1", current_sequence=20)["status"] == "ACTIVATION_ALLOWED"
    if case_id == "E4-P2":
        m = _manifest(); m["powers"] = ["read_files"]; a = _approval(); a["approved_powers"] = ["read_files"]
        return authorize_power_activation(m, a, ["read_files"], role="R1", current_sequence=20)["status"] == "ACTIVATION_ALLOWED"
    if case_id == "E4-P3":
        m = _manifest(); m["digest"] = "m2"; m["powers"].append("network_egress"); a = _approval(); a["manifest_digest"] = "m2"; a["approved_powers"].append("network_egress")
        return authorize_power_activation(m, a, ["network_egress"], role="R1", current_sequence=20)["status"] == "ACTIVATION_ALLOWED"

    # EXP-ECC-5
    if case_id == "E5-01":
        old = _cfg(); new = _cfg(); new.update({"transport": "http", "endpoint": "https://example.invalid", "canonical_digest": "cfg-b"})
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-02":
        old = _cfg(); new = _cfg(); new["transport"] = "http"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-03":
        old = _cfg(); new = _cfg(); new["permission_profile"] = "write"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-04":
        old = _cfg(); new = _cfg(); new["argv_digest"] = "argv-2"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-05":
        old = _cfg(); new = _cfg(); new["credential_profile"] = "admin-profile"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-06":
        old = _cfg(); new = _cfg(); new["harness_id"] = "h2"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-07":
        old = _cfg(); new = _cfg(); new["semantic_digest"] = "semantic-different"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_DRIFT"
    if case_id == "E5-08":
        old = _cfg(); new = _cfg(); new["permission_profile"] = "write"
        return check_tool_configuration(old, new)["stale_dependents"] is True
    if case_id == "E5-09":
        new = _cfg(); new["read_ok"] = False
        return check_tool_configuration(_cfg(), new)["status"] == "TOOL_CONFIG_UNKNOWN"
    if case_id == "E5-P1":
        return check_tool_configuration(_cfg(), copy.deepcopy(_cfg()))["status"] == "TOOL_CONFIG_CURRENT"
    if case_id == "E5-P2":
        old = _cfg(); new = _cfg(); new["display_label"] = "Friendly label"
        return check_tool_configuration(old, new)["status"] == "TOOL_CONFIG_CURRENT"
    if case_id == "E5-P3":
        changed = _cfg(); changed["permission_profile"] = "write"; changed["canonical_digest"] = "cfg-new"; changed["semantic_digest"] = "semantic-new"
        return check_tool_configuration(changed, copy.deepcopy(changed))["status"] == "TOOL_CONFIG_CURRENT"

    # EXP-ECC-6
    if case_id == "E6-01":
        b = _binding(); b["packet_digest"] = "pkt-2"
        return classify_review_binding(b)["status"] == "REVIEW_EGRESS_BINDING_MISMATCH"
    if case_id == "E6-02":
        return classify_review_binding(_binding())["provider_relationship"] == "SAME_PROVIDER_CONFIRMED"
    if case_id == "E6-03":
        b = _binding(); b["gateway"] = "router"; b["returned_provider"] = None
        return classify_review_binding(b)["provider_relationship"] == "GATEWAY_RELATIONSHIP_UNVERIFIED"
    if case_id == "E6-04":
        b = _binding(); b["reviewer_slot"] = "R3"
        return classify_review_binding(b)["status"] == "REVIEW_ROLE_BINDING_MISMATCH"
    if case_id == "E6-05":
        b = _binding(); b["selected_model"] = "model-b"
        return classify_review_binding(b)["status"] == "REVIEW_ROLE_BINDING_MISMATCH"
    if case_id == "E6-06":
        b = _binding(); b["packet_data_classes"].append("secrets")
        return classify_review_binding(b)["status"] == "REVIEW_EGRESS_SCOPE_EXCEEDED"
    if case_id == "E6-07":
        b = _binding(); b["transport_ok"] = False
        return classify_review_binding(b)["status"] == "REVIEW_TRANSPORT_FAILED"
    if case_id == "E6-08":
        return classify_review_binding(_binding())["manual_review_threshold_contribution"] == 0
    if case_id == "E6-09":
        b = _binding(); b["context_isolation_evidenced"] = False
        return classify_review_binding(b)["status"] == "REVIEW_ISOLATION_INSUFFICIENT_EVIDENCE"
    if case_id == "E6-10":
        b = _binding(); b["packet_current"] = False
        return classify_review_binding(b)["status"] == "REVIEW_BINDING_STALE"
    if case_id == "E6-P1":
        return classify_review_binding(_binding())["manual_review_threshold_contribution"] == 0
    if case_id == "E6-P2":
        b = _binding(); b["selected_model"] = b["role_binding_model"] = "user-selected-qualified-model"
        return classify_review_binding(b)["status"] == "REVIEW_BINDING_VALID"
    if case_id == "E6-P3":
        r = classify_review_binding(_binding())
        return r["provider_relationship"] == "SAME_PROVIDER_CONFIRMED" and r["manual_review_threshold_contribution"] == 0
    if case_id == "E6-P4":
        b = _binding(); b["transport_enabled"] = False
        r = classify_review_binding(b)
        return r["status"] == "REVIEW_TRANSPORT_DISABLED" and r["manual_review_threshold_contribution"] == 0

    # EXP-ECC-7
    if case_id == "E7-01":
        return authorize_learning_promotion(_proposal())["status"] == "LEARNING_PROPOSAL_NOT_PROMOTABLE"
    if case_id == "E7-02":
        p = _proposal(); p["user_non_correction"] = True
        return authorize_learning_promotion(p)["promotable"] is False
    if case_id == "E7-03":
        p = _proposal(); p["model_consensus"] = True
        return authorize_learning_promotion(p)["promotable"] is False
    if case_id == "E7-04":
        p = _proposal(); p["target_scope"] = "global"
        return authorize_learning_promotion(p)["status"] == "LEARNING_SCOPE_WIDENING_REJECTED"
    if case_id == "E7-05":
        p = _proposal(); p["requested_authority"] = ["write_files"]
        return authorize_learning_promotion(p)["status"] == "LEARNING_AUTHORITY_NOT_GRANTED"
    if case_id == "E7-06":
        p = _proposal(); p.update({"source_verified": True, "independent_support": True, "governed_approval": True, "parent_retracted": True})
        return authorize_learning_promotion(p)["status"] == "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED"
    if case_id == "E7-07":
        p = _proposal(); p["artifact_digest"] = "a2"
        return authorize_learning_promotion(p)["status"] == "LEARNING_PROPOSAL_CHANGED_AFTER_REVIEW"
    if case_id == "E7-08":
        p = _proposal(); p["stale"] = True; p["conflicts_governed"] = True
        return authorize_learning_promotion(p)["status"] == "LEARNING_PROPOSAL_STALE_OR_CONFLICTING"
    if case_id == "E7-09":
        p = _proposal(); p["confidence"] = 1.0
        return authorize_learning_promotion(p)["promotable"] is False
    if case_id == "E7-10":
        p = _proposal(); p["prior_rejection"] = True; p["history_preserved"] = False; p.update({"source_verified": True, "independent_support": True, "governed_approval": True})
        return authorize_learning_promotion(p)["status"] == "LEARNING_HISTORY_INTEGRITY_REQUIRED"
    if case_id == "E7-P1":
        p = _proposal(); p["confidence"] = 0.999
        r = authorize_learning_promotion(p)
        return r["promotable"] is False and r.get("advisory_allowed") is True
    if case_id == "E7-P2":
        p = _proposal(); p.update({"source_verified": True, "independent_support": True, "governed_approval": True})
        return authorize_learning_promotion(p)["status"] == "LEARNING_PROPOSAL_PROMOTABLE"
    if case_id == "E7-P3":
        p = _proposal(); p.update({"source_verified": True, "independent_support": True, "governed_approval": True, "parent_retracted": True})
        r = authorize_learning_promotion(p)
        return r["status"] == "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED" and r.get("independent_support_preserved") is True
    if case_id == "E7-P4":
        p = _proposal(); p["target_scope"] = "project-a"
        r = authorize_learning_promotion(p)
        return r.get("scope_preserved") is True and r.get("advisory_allowed") is True

    raise AssertionError(f"Unhandled case: {case_id}")


class FullNamedCoverageTests(unittest.TestCase):
    pass


def _make_test(case_id):
    def test(self):
        self.assertTrue(run_case(case_id), f"Named falsification case failed: {case_id}")
    test.__name__ = f"test_{case_id.replace('-', '_')}"
    return test


for _case_id in CASE_IDS:
    setattr(FullNamedCoverageTests, f"test_{_case_id.replace('-', '_')}", _make_test(_case_id))


if __name__ == "__main__":
    unittest.main()
