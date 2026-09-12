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

old_primitives = '''def _build_runtime_policy_verifier(gov_module, strict_module, evidence_module, boundary_file):
    hashlib_module = hashlib
    json_module = json
    marshal_module = marshal
    sys_module = sys
    path_type = Path
'''
new_primitives = '''def _build_runtime_policy_verifier(gov_module, strict_module, evidence_module, boundary_file):
    sha256_fn = hashlib.sha256
    json_loads_fn = json.loads
    marshal_dumps_fn = marshal.dumps
    sys_modules = sys.modules
    path_type = Path
'''
if old_primitives not in source:
    raise SystemExit("Expected V8 verifier primitive block not found")
source = source.replace(old_primitives, new_primitives, 1)

source = source.replace(
    'return hashlib_module.sha256(path.read_bytes()).hexdigest()',
    'return sha256_fn(path.read_bytes()).hexdigest()',
    1,
)
source = source.replace(
    'return hashlib_module.sha256(marshal_module.dumps(fn.__code__)).hexdigest()',
    'return sha256_fn(marshal_dumps_fn(fn.__code__)).hexdigest()',
    1,
)
source = source.replace(
    'if sys_module.modules.get(expected_name) is not module:',
    'if sys_modules.get(expected_name) is not module:',
    1,
)
source = source.replace(
    'manifest = json_module.loads(manifest_path.read_text(encoding="utf-8"))',
    'manifest = json_loads_fn(manifest_path.read_text(encoding="utf-8"))',
    1,
)
source = source.replace(
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V8_VERIFIER_SUBSTITUTION_MANIFEST":',
    'if manifest.get("record_type") != "ECC_GOVERNANCE_V9_VERIFIER_PRIMITIVE_INTEGRITY_MANIFEST":',
    1,
)

anchor = '''        if manifest.get("actual_dependency_tamper_fail_closed") is not True:
            return False
'''
addition = '''        if manifest.get("actual_dependency_tamper_fail_closed") is not True:
            return False
        if manifest.get("verifier_primitive_policy") != "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("seal_primitive_policy") != "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION":
            return False
        if manifest.get("public_json_alias_controls_candidate_authority") is not False:
            return False
        if manifest.get("public_marshal_alias_controls_candidate_authority") is not False:
            return False
'''
if anchor not in source:
    raise SystemExit("Expected V8 manifest validation anchor not found")
source = source.replace(anchor, addition, 1)

old_candidate_primitives = '''    favorable = {key: frozenset(values) for key, values in _FAVORABLE.items()}
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
new_candidate_primitives = '''    favorable = {key: frozenset(values) for key, values in _FAVORABLE.items()}
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
'''
if old_candidate_primitives not in source:
    raise SystemExit("Expected V8 candidate seal primitive block not found")
source = source.replace(old_candidate_primitives, new_candidate_primitives, 1)

# Eligibility consumption must use the already-captured favorable-status map rather
# than return to a mutable module-global alias.
source = source.replace(
    '        allowed = _FAVORABLE.get(kind)\n',
    '        allowed = favorable.get(kind)\n',
    1,
)

BOUNDARY.write_text(source, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("record_type") != "ECC_GOVERNANCE_V8_VERIFIER_SUBSTITUTION_MANIFEST":
    raise SystemExit("Expected V8 manifest before V9 repair")
manifest["record_type"] = "ECC_GOVERNANCE_V9_VERIFIER_PRIMITIVE_INTEGRITY_MANIFEST"
manifest["verifier_primitive_policy"] = "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION"
manifest["seal_primitive_policy"] = "EXACT_CALLABLES_CAPTURED_AT_INITIALIZATION"
manifest["public_json_alias_controls_candidate_authority"] = False
manifest["public_marshal_alias_controls_candidate_authority"] = False
manifest["captured_verifier_primitives"] = [
    "hashlib.sha256",
    "json.loads",
    "marshal.dumps",
]
manifest["captured_seal_primitives"] = [
    "hashlib.sha256",
    "json.dumps",
]
manifest["remaining_primitive_boundary"] = (
    "MUTATION_OF_CAPTURED_CALLABLE_OBJECTS_OR_OTHER_INTERPRETER_PRIMITIVES_"
    "OUTSIDE_V9_BOUNDED_THREAT_MODEL"
)
manifest["module_sha256"]["candidate_boundary"] = sha256(BOUNDARY)
MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print("BOUNDARY_SHA256=" + sha256(BOUNDARY))
print("MANIFEST_SHA256=" + sha256(MANIFEST))
print("V9_VERIFIER_PRIMITIVE_REPAIR_GENERATED=1")
