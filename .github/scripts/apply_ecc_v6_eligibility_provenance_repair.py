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

old_record = 'if manifest.get("record_type") != "ECC_GOVERNANCE_V5_CLOSED_BOUNDARY_MANIFEST":\n        return False'
new_record = '''if manifest.get("record_type") != "ECC_GOVERNANCE_V6_ELIGIBILITY_PROVENANCE_MANIFEST":
        return False
    if manifest.get("eligibility_provenance_policy") != "PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST":
        return False
    if manifest.get("serialized_candidate_authority") != "REJECT_UNSEALED_RECONSTRUCTION":
        return False'''
if old_record not in source:
    raise SystemExit("Expected V5 manifest record check not found")
source = source.replace(old_record, new_record, 1)

old_gate = '''def candidate_result_eligible(result):
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
'''

new_gate = '''def _canonical_result_digest(value):
    try:
        payload = json.dumps(
            dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(payload).hexdigest()


def _build_process_local_provenance_codec():
    issuer_token = object()

    class CandidateEvaluationResult(dict):
        __slots__ = ("_issuer_token", "_sealed_digest")

        def __init__(self, payload, supplied_token):
            if supplied_token is not issuer_token:
                raise TypeError("candidate eligibility result may only be issued by the boundary")
            super().__init__(payload)
            self._issuer_token = supplied_token
            self._sealed_digest = _canonical_result_digest(self)
            if self._sealed_digest is None:
                raise TypeError("candidate result is not canonically sealable")

        def __reduce_ex__(self, protocol):
            raise TypeError("process-local candidate provenance is intentionally non-picklable")

    CandidateEvaluationResult.__name__ = "_BoundaryIssuedCandidateResult"
    CandidateEvaluationResult.__qualname__ = "_BoundaryIssuedCandidateResult"

    def seal(payload):
        return CandidateEvaluationResult(payload, issuer_token)

    def valid(result):
        if type(result) is not CandidateEvaluationResult:
            return False
        if getattr(result, "_issuer_token", None) is not issuer_token:
            return False
        sealed = getattr(result, "_sealed_digest", None)
        current = _canonical_result_digest(result)
        return isinstance(sealed, str) and sealed == current

    return CandidateEvaluationResult, seal, valid


_CandidateEvaluationResult, _seal_candidate_result, _valid_candidate_provenance = (
    _build_process_local_provenance_codec()
)


def candidate_result_eligible(result):
    if not verify_runtime_policy():
        return False
    if not _valid_candidate_provenance(result):
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
    return _seal_candidate_result(out) if eligible else out
'''

if old_gate not in source:
    raise SystemExit("Expected V5 eligibility gate not found")
source = source.replace(old_gate, new_gate, 1)
BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V5_CLOSED_BOUNDARY_MANIFEST":
    raise SystemExit("Expected V5 manifest before V6 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V6_ELIGIBILITY_PROVENANCE_MANIFEST"
manifest["eligibility_provenance_policy"] = "PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST"
manifest["serialized_candidate_authority"] = "REJECT_UNSEALED_RECONSTRUCTION"
manifest["process_local_provenance_only"] = True
manifest["durable_cross_process_signature_claimed"] = False
manifest["remaining_provenance_boundary"] = "DURABLE_SIGNED_RECEIPT_OR_EXTERNAL_TRUST_SERVICE_FOR_CROSS_PROCESS_USE"
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V6_PROCESS_LOCAL_PROVENANCE_REPAIR_GENERATED=1")
