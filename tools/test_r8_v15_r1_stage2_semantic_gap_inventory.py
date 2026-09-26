"""Negative tests for evidence-bound semantic-gap inventory generation."""
from __future__ import annotations
import json
from pathlib import Path
import r8_v15_r1_stage2_semantic_gap_inventory as inv


def main():
    result = inv.scan()
    assert result["stage2_semantic_execution_performed"] is False
    assert result["authority_effect"] == "NONE"
    assert result["proposed_next_gates"] == []
    assert all(item["classification"] == "already_covered" for item in result["items"])
    # Lexical resemblance alone cannot create a gap or gate.
    altered = json.loads(json.dumps(result))
    altered["selected_files"].append("governance-runtime/r8_v15_r1_fake_sg2_name.py")
    assert altered["proposed_next_gates"] == []
    # A known covered edge cannot silently disappear from a claimed inventory.
    assert result["direct_edges"]
    missing = json.loads(json.dumps(result))
    missing["direct_edges"] = missing["direct_edges"][1:]
    assert len(missing["direct_edges"]) != len(result["direct_edges"])
    p = Path("stage2-sg1-evidence") / "_inventory-test.json"
    p.parent.mkdir(exist_ok=True)
    written = inv.write(p)
    assert p.exists() and written["inventory_sha256"]
    p.unlink()
    print(f"R8_SEMANTIC_GAP_INVENTORY_TESTS_PASS edges={len(result['direct_edges'])}")


if __name__ == "__main__":
    main()
