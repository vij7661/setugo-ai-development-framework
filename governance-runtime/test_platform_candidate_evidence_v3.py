from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "governance-runtime"
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

import platform_candidate_evidence_v3 as ev3

PINNED = "a855975a8668007bfa3fb377a0d7786d1c95691e"
PINNED_PATH = "governance-runtime/repair-preregistrations/GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001.md"


def main() -> None:
    passed = 0

    item = ev3.materialize_evidence_ref(ROOT, PINNED, {"type":"frozen_file","ref":PINNED_PATH,"commit":PINNED})
    raw = subprocess.check_output(["git","show",f"{PINNED}:{PINNED_PATH}"], cwd=ROOT)
    assert item["type"] == "frozen_file"
    assert item["source_commit"] == PINNED
    assert item["ref"] == PINNED_PATH
    assert item["sha256"] == hashlib.sha256(raw).hexdigest()
    assert item["content"].encode("utf-8") == raw
    passed += 1

    for bad in ("abc", "A" * 40, "0" * 39):
        try:
            ev3.materialize_evidence_ref(ROOT, PINNED, {"type":"frozen_file","ref":PINNED_PATH,"commit":bad})
            raise AssertionError("malformed frozen_file SHA accepted")
        except ValueError:
            pass
    passed += 1

    try:
        ev3.materialize_evidence_ref(ROOT, PINNED, {"type":"frozen_file","ref":"","commit":PINNED})
        raise AssertionError("missing frozen_file path accepted")
    except ValueError:
        pass
    passed += 1

    try:
        ev3.materialize_evidence_ref(ROOT, PINNED, {"type":"frozen_file","ref":"does/not/exist.txt","commit":PINNED})
        raise AssertionError("absent frozen file accepted")
    except RuntimeError:
        pass
    passed += 1

    candidate_item = ev3.materialize_evidence_ref(ROOT, PINNED, {"type":"file","ref":PINNED_PATH})
    assert candidate_item["type"] == "file"
    assert candidate_item["candidate_sha"] == PINNED
    assert candidate_item["sha256"] == item["sha256"]
    passed += 1

    try:
        ev3.materialize_evidence_ref(ROOT, PINNED, {"type":"mystery","ref":PINNED_PATH})
        raise AssertionError("unknown evidence type accepted")
    except ValueError:
        pass
    passed += 1

    request = {
        "artifact": {"commit": PINNED},
        "evidence_refs": [
            {"type":"file","ref":PINNED_PATH},
            {"type":"frozen_file","ref":PINNED_PATH,"commit":PINNED},
            {"type":"history","ref":"non-authoritative history fixture"},
        ],
    }
    corpus = ev3.build_corpus(ROOT, request)
    assert corpus["evidence_ref_count"] == 3
    assert corpus["materialized_evidence_count"] == 3
    assert corpus["materialization_version"] == "GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001"
    passed += 1

    print(f"Frozen cross-commit evidence tests: {passed}/7 PASS")


if __name__ == "__main__":
    main()
