from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "experiments/ecc_derived/ecc_governance.py"
BOUNDARY = ROOT / "experiments/ecc_derived/ecc_candidate_boundary.py"
MANIFEST = ROOT / "experiments/ecc_derived/ecc_governance_trust_manifest.json"
FROZEN_TEST = ROOT / "experiments/ecc_derived/test_ecc_governance_v4_mandatory_boundary.py"

EXPECTED_PRE_V4_CORE_SHA256 = "5609f0b7ba51246f6da017a3a47434be1e521ee25b6bb63e84897e385e26820d"
MARKER = "# V4_HISTORICAL_RESULT_CLASSIFICATION_BOUNDARY"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return subprocess.check_output(
        ["git", "hash-object", str(rel)], cwd=ROOT, text=True
    ).strip()


def main() -> None:
    if not CORE.exists() or not BOUNDARY.exists() or not MANIFEST.exists() or not FROZEN_TEST.exists():
        raise SystemExit("V4 repair inputs missing")
    if "class ECCV4MandatoryCandidateBoundary" not in FROZEN_TEST.read_text(encoding="utf-8"):
        raise SystemExit("frozen V4 assertion file mismatch")

    text = CORE.read_text(encoding="utf-8")
    if MARKER in text:
        raise SystemExit("V4 historical-classification repair already present")
    if sha256(CORE) != EXPECTED_PRE_V4_CORE_SHA256:
        raise SystemExit("shared governance core changed from frozen V3 input")

    old_imports = "import hashlib\nimport json\n"
    new_imports = "import functools\nimport hashlib\nimport json\n"
    if old_imports not in text:
        raise SystemExit("expected import block missing")
    text = text.replace(old_imports, new_imports, 1)

    constant = '_REQUIREMENT_CANDIDATE = "REQUIREMENT_CANDIDATE"\n'
    replacement = (
        '_REQUIREMENT_CANDIDATE = "REQUIREMENT_CANDIDATE"\n'
        '_HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"\n'
    )
    if constant not in text:
        raise SystemExit("candidate class constant missing")
    text = text.replace(constant, replacement, 1)

    wrapper = r'''
# V4_HISTORICAL_RESULT_CLASSIFICATION_BOUNDARY
# The historical compatibility functions remain replayable, but every result is
# explicitly typed. Only the separate ecc_candidate_boundary module is eligible
# to produce requirement-candidate evidence for new candidate evaluation.
def _classify_public_evaluation_result(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        if not isinstance(result, dict):
            return result
        if "evaluation_class" in result:
            return result
        classified = dict(result)
        classified["evaluation_class"] = (
            _REQUIREMENT_CANDIDATE
            if kwargs.get("requirement_candidate", False)
            else _HISTORICAL_REFERENCE
        )
        return classified

    return wrapped


for _public_name in (
    "assess_control_execution",
    "check_declared_executable_equivalence",
    "qualify_role_binding",
    "authorize_power_activation",
    "check_tool_configuration",
    "classify_review_binding",
    "authorize_learning_promotion",
):
    globals()[_public_name] = _classify_public_evaluation_result(globals()[_public_name])
'''
    CORE.write_text(text.rstrip() + "\n\n" + wrapper.lstrip(), encoding="utf-8")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest.update(
        {
            "record_type": "ECC_GOVERNANCE_V4_RUNTIME_TRUST_BOUNDARY_MANIFEST",
            "module_sha256": sha256(CORE),
            "module_git_blob_sha": git_blob(CORE),
            "candidate_boundary_module_path": "experiments/ecc_derived/ecc_candidate_boundary.py",
            "candidate_boundary_module_sha256": sha256(BOUNDARY),
            "candidate_boundary_module_git_blob_sha": git_blob(BOUNDARY),
            "candidate_boundary_policy": "STRICT_ONLY_NO_CALLER_MODE_SWITCH",
            "historical_result_class": "HISTORICAL_REFERENCE",
            "independent_crosscheck_covers": [
                "EXP-ECC-1",
                "EXP-ECC-2",
                "EXP-ECC-3",
                "EXP-ECC-4",
                "EXP-ECC-5",
            ],
            "legacy_path_policy": "HISTORICAL_REFERENCE_ONLY",
            "candidate_path_policy": "MANDATORY_STRICT_EVALUATION",
            "manual_review_threshold_contribution": 0,
            "authority_effect": "NONE_EVIDENCE_ONLY",
        }
    )
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"CORE_SHA256={sha256(CORE)}")
    print(f"BOUNDARY_SHA256={sha256(BOUNDARY)}")
    print(f"CORE_BLOB={git_blob(CORE)}")
    print(f"BOUNDARY_BLOB={git_blob(BOUNDARY)}")


if __name__ == "__main__":
    main()
