import unittest

from impact_graph import invalidation_plan, missing_declared_relationships, transitive_dependents, validate_graph


def graph_fixture():
    return {
        "nodes": [
            {"id": "INV-1", "kind": "INVARIANT"},
            {"id": "REQ-1", "kind": "REQUIREMENT"},
            {"id": "CFG-1", "kind": "CONFIG"},
            {"id": "CODE-1", "kind": "CODE"},
            {"id": "TEST-1", "kind": "TEST"},
            {"id": "ALERT-1", "kind": "OPERATIONS"},
        ],
        "edges": [
            {"from": "REQ-1", "to": "INV-1", "relation": "DERIVED_FROM"},
            {"from": "CFG-1", "to": "REQ-1", "relation": "SATISFIES"},
            {"from": "CODE-1", "to": "REQ-1", "relation": "IMPLEMENTS"},
            {"from": "CODE-1", "to": "CFG-1", "relation": "DEPENDS_ON"},
            {"from": "TEST-1", "to": "CODE-1", "relation": "VERIFIES"},
        ],
        "evidence": [
            {"id": "ci:test-1", "artifact_id": "TEST-1"},
            {"id": "review:code-1", "artifact_id": "CODE-1"},
        ],
    }


class ImpactGraphTests(unittest.TestCase):
    def test_transitive_impact_propagates_from_invariant(self):
        impacted = transitive_dependents(graph_fixture(), ["INV-1"])
        self.assertEqual(impacted, ["CFG-1", "CODE-1", "INV-1", "REQ-1", "TEST-1"])

    def test_config_change_invalidates_code_and_test_evidence(self):
        plan = invalidation_plan(graph_fixture(), ["CFG-1"])
        self.assertEqual(plan["impacted_nodes"], ["CFG-1", "CODE-1", "TEST-1"])
        self.assertEqual(plan["stale_evidence"], ["ci:test-1", "review:code-1"])

    def test_explicit_missing_relationship_is_detected_not_invented(self):
        missing = missing_declared_relationships(
            graph_fixture(),
            [{"from": "ALERT-1", "to": "CFG-1", "relation": "DEPENDS_ON"}],
        )
        self.assertEqual(missing, [{"from": "ALERT-1", "to": "CFG-1", "relation": "DEPENDS_ON"}])

    def test_dangling_edge_fails_closed(self):
        graph = graph_fixture()
        graph["edges"].append({"from": "TEST-1", "to": "MISSING", "relation": "DEPENDS_ON"})
        with self.assertRaises(ValueError):
            validate_graph(graph)

    def test_unknown_changed_node_fails_closed(self):
        with self.assertRaises(ValueError):
            transitive_dependents(graph_fixture(), ["UNKNOWN"])


if __name__ == "__main__":
    unittest.main()
