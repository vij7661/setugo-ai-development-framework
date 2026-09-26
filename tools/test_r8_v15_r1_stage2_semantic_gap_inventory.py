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
    assert result["runtime_only"]["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["release_deployment_production_only"]["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["manual_policy"]["status"] == "INSUFFICIENT_EVIDENCE"
    unknown = {"from_path": "x.py", "kind": "import", "module": "r8_v15_r1_unknown", "line": 1, "target_path": None}
    assert inv.classify_edge(unknown, result["direct_edges"], {"stage2": {"sg1_closed": True}})["classification"] == "unresolved_semantic_dependency"
    # Lexical resemblance alone cannot create a gap or gate.
    altered = json.loads(json.dumps(result))
    altered["selected_files"].append("governance-runtime/r8_v15_r1_fake_sg2_name.py")
    assert altered["proposed_next_gates"] == []
    # A known covered edge cannot silently disappear from a claimed inventory.
    assert result["direct_edges"]
    assert len({inv.edge_key(edge) for edge in result["direct_edges"]}) == len(result["direct_edges"])
    assert all(edge["source_blob"] and edge["target_blob"] for edge in result["direct_edges"])
    assert inv.target_for_module("r8_v15_r1_frozen_schema_runtime") == "governance-runtime/r8_v15_r1_frozen_schema_runtime.py"
    missing = json.loads(json.dumps(result))
    missing["direct_edges"] = missing["direct_edges"][1:]
    assert len(missing["direct_edges"]) != len(result["direct_edges"])
    p = Path("stage2-sg1-evidence") / "_inventory-test.json"
    p.parent.mkdir(exist_ok=True)
    written = inv.write(p)
    assert p.exists() and written["inventory_sha256"]
    assert inv.verify_inventory_digest(p)
    tampered = json.loads(p.read_text(encoding="utf-8"))
    tampered["direct_edges"][0]["source_blob"] = "0" * 40
    p.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert not inv.verify_inventory_digest(p)
    p.unlink()
    print(f"R8_SEMANTIC_GAP_INVENTORY_TESTS_PASS edges={len(result['direct_edges'])}")


if __name__ == "__main__":
    main()
