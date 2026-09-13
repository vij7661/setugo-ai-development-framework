from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "testing/v24/WDPC_V24_I11_Falsification_Plan_V8_Clean_Review_Packet.md"
HARNESS = ROOT / "testing/v24/v24_i11_harness_contract_v7.py"
BINDING = ROOT / "testing/v24/V24-I11-FALSIFICATION-PLAN-V8-REVIEW-BINDING.json"

EXPECTED_PACKET_SHA = "2adcabff35ecc38e45977c9934873af4b3ebb11bede17a5d9959b6b79c49f881"
EXPECTED_BODY_SHA = "0a9620d696d853bb6a60de123504f5958345a3ebf63a6297c76e85c319dbb717"
EXPECTED_PACKET_BLOB = "baa5f3041d9a40fd8f641df367307860f7eff371"
EXPECTED_HARNESS_BLOB = "189d050831166868397e1ba063da57fa77f2dd42"
EXPECTED_BINDING_BLOB = "a3c7d697a9e53c6b1da3fe0475319d65dc3ceb1c"
EXPECTED_HARNESS_VERSION = "1.6.0-PLAN-REVIEW"

def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).strip()

packet_bytes = PACKET.read_bytes()
packet = packet_bytes.decode("utf-8")
if hashlib.sha256(packet_bytes).hexdigest() != EXPECTED_PACKET_SHA:
    raise SystemExit("V8 packet SHA mismatch")
if git_blob(PACKET) != EXPECTED_PACKET_BLOB:
    raise SystemExit("V8 packet Git blob mismatch")

parts = packet.split("\n---\n\n", 1)
if len(parts) != 2:
    raise SystemExit("V8 wrapper delimiter missing")
if hashlib.sha256(parts[1].encode()).hexdigest() != EXPECTED_BODY_SHA:
    raise SystemExit("V8 body SHA mismatch")

if git_blob(HARNESS) != EXPECTED_HARNESS_BLOB:
    raise SystemExit("V8 harness Git blob mismatch")
if git_blob(BINDING) != EXPECTED_BINDING_BLOB:
    raise SystemExit("V8 binding Git blob mismatch")

binding = json.loads(BINDING.read_text())
expected_binding = {
    "packet_sha256": EXPECTED_PACKET_SHA,
    "plan_body_sha256": EXPECTED_BODY_SHA,
    "packet_git_blob_sha": EXPECTED_PACKET_BLOB,
    "harness_blob_sha": EXPECTED_HARNESS_BLOB,
    "harness_version": EXPECTED_HARNESS_VERSION,
}
for key, value in expected_binding.items():
    if binding.get(key) != value:
        raise SystemExit(f"V8 binding mismatch: {key}")

required = [
    "# WDPC V24 I11 Falsification Plan V8 — Clean Independent Review Packet",
    f"**Harness blob:** `{EXPECTED_HARNESS_BLOB}`",
    f"**Harness version:** `{EXPECTED_HARNESS_VERSION}`",
    f"**Frozen harness contract version:** `{EXPECTED_HARNESS_VERSION}`",
    f"**Frozen harness Git blob:** `{EXPECTED_HARNESS_BLOB}`",
    "detached V8 review binding",
    "detached V8 review-binding",
    "Embedded V8 harness contract V7",
]
for token in required:
    if token not in packet:
        raise SystemExit(f"missing V8 token: {token}")

for stale in [
    "1.4.0-PLAN-REVIEW",
    "56e9c236d94616ec768fc2449edafbaac55a926e",
    "1.5.0-PLAN-REVIEW",
    "556bc723982a1452f61cfbb39e4756a81c7c9a37",
    "detached V6 review binding",
    "detached V7 review-binding",
]:
    if stale in packet:
        raise SystemExit(f"stale V8 identity found: {stale}")

matrix = packet[packet.index("## 12. Case audit matrix"):packet.index("## 13. Clustering")]
case_ids = re.findall(r"^\| WDPC-(\d{3}) \|", matrix, flags=re.M)
if len(case_ids) != 76 or set(map(int, case_ids)) != set(range(431, 507)):
    raise SystemExit("V8 case coverage invalid")

rows = {
    n: next(line for line in matrix.splitlines() if line.startswith(f"| WDPC-{n} |"))
    for n in ("433", "453", "458", "482")
}
if " or " in rows["433"].lower():
    raise SystemExit("WDPC-433 is still disjunctive")
if "absent/ambiguously" in rows["453"].lower() or " or " in rows["453"].lower():
    raise SystemExit("WDPC-453 is still disjunctive")
if "unavailable or" in rows["458"].lower():
    raise SystemExit("WDPC-458 is still disjunctive")
if " or " in rows["482"].lower():
    raise SystemExit("WDPC-482 is still disjunctive")

name = "v24_i11_harness_contract_v7"
spec = importlib.util.spec_from_file_location(name, HARNESS)
mod = importlib.util.module_from_spec(spec)
sys.modules[name] = mod
spec.loader.exec_module(mod)

if mod.HARNESS_VERSION != EXPECTED_HARNESS_VERSION:
    raise SystemExit("Harness version mismatch after import")
if mod.IE_TARGET_REASONS["WDPC-458"] != (
    "required external completeness authority is present but independence is unproven"
):
    raise SystemExit("WDPC-458 target reason mismatch")

cond = mod.InsufficientEvidenceEndpointCondition(
    case_id="WDPC-458",
    case_execution_evidence_bundle_present=True,
    case_preconditions_valid=True,
    target_condition_evidence_present=True,
    target_condition_observed=True,
    missing_case_execution_evidence=False,
    endpoint_emitted_by_candidate=True,
    endpoint_trigger_evidence_digest="a" * 64,
    target_reason=mod.IE_TARGET_REASONS["WDPC-458"],
)
if not cond.qualifies_for_endpoint_pass:
    raise SystemExit("V8 exact IE reason positive contract failed")

wrong = mod.InsufficientEvidenceEndpointCondition(
    **{**cond.__dict__, "target_reason": "required external completeness authority unavailable"}
)
if wrong.qualifies_for_endpoint_pass:
    raise SystemExit("V8 wrong IE reason false-green")

print("V8_PLAN_CONTRACT_PASS")
