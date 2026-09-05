"""Out-of-band runtime identity attestation guard for qualified remote routing."""
from __future__ import annotations


def verify_runtime_identity_attestation(route: dict, qualification: dict, attestation: dict) -> dict:
    """Fail closed unless a separately verified identity attestation matches the route.

    Provider response labels are deliberately not inputs to this decision. The
    attestation is expected to be produced/verified by a trusted control-plane or
    out-of-band qualification probe and retained as governance evidence.
    """
    if not all(isinstance(x, dict) for x in (route, qualification, attestation)):
        return {"verified": False, "reason": "identity-input-malformed"}
    required = (
        "provider", "model", "sku", "deployment_path", "qualification_id",
        "qualification_epoch", "attestation_ref", "verified_by", "status",
    )
    missing = [key for key in required if attestation.get(key) in (None, "")]
    if missing:
        return {"verified": False, "reason": "identity-attestation-missing-binding", "missing": missing}
    if attestation.get("status") != "VERIFIED":
        return {"verified": False, "reason": "identity-attestation-not-verified"}
    if attestation.get("verified_by") == route.get("provider"):
        return {"verified": False, "reason": "self-attested-provider-identity-not-accepted"}
    for key in ("provider", "model", "sku", "deployment_path", "qualification_id", "qualification_epoch"):
        if route.get(key) != qualification.get(key):
            return {"verified": False, "reason": f"route-qualification-{key}-mismatch"}
        if attestation.get(key) != qualification.get(key):
            return {"verified": False, "reason": f"attestation-{key}-mismatch"}
    return {
        "verified": True,
        "reason": "out-of-band-runtime-identity-attested",
        "attestation_ref": attestation["attestation_ref"],
        "verified_by": attestation["verified_by"],
    }
