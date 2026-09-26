from __future__ import annotations
import copy, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from r8_work_queue import next_runnable, load, verify_external_head, ALLOWED_STATES

class QueueTests(unittest.TestCase):
    def test_human_block_does_not_stop_independent_task(self):
        data = {"tasks":[{"id":"Q1","state":"MANUAL_INTERVENTION_BLOCKED","dependencies":[]},{"id":"Q2","state":"RUNNABLE_CODING","dependencies":[]}]}
        self.assertEqual(next_runnable(data)["id"], "Q2")
    def test_dependency_blocks_until_complete(self):
        data = {"tasks":[{"id":"Q1","state":"HUMAN_REVIEW_BLOCKED","dependencies":[]},{"id":"Q2","state":"RUNNABLE_CODING","dependencies":["Q1"]}]}
        self.assertIsNone(next_runnable(data))
    def test_current_manifest_preserves_authority_boundaries(self):
        data = load(); self.assertTrue(all(not v for v in data["authority"].values())); self.assertEqual(data["issue"], 52)
        self.assertTrue(ALLOWED_STATES.issuperset({"RUNNABLE_CODING","CODE_COMPLETE","HUMAN_REVIEW_BLOCKED","MANUAL_INTERVENTION_BLOCKED","CODE_DEPENDENCY_BLOCKED","TERMINAL"}))
    def test_unknown_state_rejected(self):
        data = load(); data["tasks"][0]["state"] = "BOGUS"
        with self.assertRaises(ValueError):
            for task in data["tasks"]:
                if task["state"] not in ALLOWED_STATES: raise ValueError("unknown queue state")
    def test_report_external_head_is_not_self_referential(self):
        data = load(); self.assertFalse(verify_external_head(data, report_source_head="head", final_remote_head=None)); self.assertTrue(verify_external_head(data, report_source_head="head", final_remote_head="a"*40))

if __name__ == "__main__": unittest.main()
