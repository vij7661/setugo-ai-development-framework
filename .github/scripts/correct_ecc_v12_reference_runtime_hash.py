from __future__ import annotations

import hashlib
import json
import marshal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "experiments" / "ecc_derived"
sys.path.insert(0, str(MOD))

import ecc_reference_evidence as reference_evidence

MANIFEST = MOD / "ecc_governance_trust_manifest.json"
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V12_TRANSITIVE_PRIMITIVE_INTEGRITY_MANIFEST":
    raise SystemExit("Expected V12 manifest")

new_hash = hashlib.sha256(
    marshal.dumps(reference_evidence.lookup_reference_evidence.__code__)
).hexdigest()
old_hash = (manifest.get("runtime_code_sha256") or {}).get(
    "reference.lookup_reference_evidence"
)
manifest["runtime_code_sha256"]["reference.lookup_reference_evidence"] = new_hash
manifest["v12_reference_runtime_hash_correction"] = {
    "reason": "REFERENCE_EVIDENCE_LINE_SHIFT_CHANGED_MARSHALLED_CODE_METADATA",
    "logic_change": False,
    "previous_hash": old_hash,
    "corrected_hash": new_hash,
}
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("OLD_REFERENCE_RUNTIME_HASH=" + str(old_hash))
print("NEW_REFERENCE_RUNTIME_HASH=" + new_hash)
print("MANIFEST_SHA256=" + hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
print("V12_REFERENCE_RUNTIME_HASH_CORRECTED=1")
