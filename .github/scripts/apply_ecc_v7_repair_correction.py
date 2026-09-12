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

old_manifest_check = '''    if manifest.get("record_type") != "ECC_GOVERNANCE_V6_ELIGIBILITY_PROVENANCE_MANIFEST":
        return False
    if manifest.get("eligibility_provenance_policy") != "PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST":
        return False
    if manifest.get("serialized_candidate_authority") != "REJECT_UNSEALED_RECONSTRUCTION":
        return False
'''
new_manifest_check = '''    if manifest.get("record_type") != "ECC_GOVERNANCE_V7_SEAL_CAPABILITY_MANIFEST":
        return False
    if manifest.get("eligibility_provenance_policy") != "PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST":
        return False
    if manifest.get("serialized_candidate_authority") != "REJECT_UNSEALED_RECONSTRUCTION":
        return False
    if manifest.get("seal_capability_policy") != "POSITIVE_SEAL_CAPABILITY_CLOSURE_LOCAL_ONLY":
        return False
    if manifest.get("ordinary_module_access_can_mint_provenance") is not False:
        return False
    if manifest.get("candidate_entrypoints_use_dynamic_runtime_verifier") is not True:
        return False
'''
if old_manifest_check not in source:
    raise SystemExit("Expected stale V6 verifier block not found")
source = source.replace(old_manifest_check, new_manifest_check, 1)

if "def _build_candidate_api(runtime_verify):" not in source:
    raise SystemExit("Expected captured-verifier V7 factory not found")
source = source.replace("def _build_candidate_api(runtime_verify):", "def _build_candidate_api():", 1)

# Within the V7 factory the only runtime_verify references are the captured-policy
# calls introduced by the first repair. Restore dynamic policy lookup so retained
# V5/V6 policy-transition semantics remain observable and fail-closed.
if "runtime_verify()" not in source:
    raise SystemExit("Expected captured runtime verifier calls not found")
source = source.replace("runtime_verify()", "verify_runtime_policy()")

if "_build_candidate_api(verify_runtime_policy)" not in source:
    raise SystemExit("Expected captured-verifier factory invocation not found")
source = source.replace("_build_candidate_api(verify_runtime_policy)", "_build_candidate_api()", 1)

BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V7_SEAL_CAPABILITY_MANIFEST":
    raise SystemExit("Expected V7 manifest before repair correction")
manifest["candidate_entrypoints_capture_runtime_verifier"] = False
manifest["candidate_entrypoints_use_dynamic_runtime_verifier"] = True
manifest["repair_defect_correction"] = "V7_RUNTIME_VERIFIER_MANIFEST_AND_DYNAMIC_RECHECK"
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V7_REPAIR_CORRECTION_GENERATED=1")
