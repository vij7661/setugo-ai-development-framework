from __future__ import annotations
import copy, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from r8_work_queue import next_runnable, load

class QueueTests(unittest.TestCase):
    def test_human_block_does_not_stop_independent_task(self):
        data = {"tasks":[{"id":"Q1","state":"MANUAL_INTERVENTION_REQUIRED","dependencies":[]},{"id":"Q2","state":"IN_PROGRESS","dependencies":[]}]}
        self.assertEqual(next_runnable(data)["id"], "Q2")
    def test_dependency_blocks_until_complete(self):
        data = {"tasks":[{"id":"Q1","state":"REVIEW_REQUIRED","dependencies":[]},{"id":"Q2","state":"IN_PROGRESS","dependencies":["Q1"]}]}
        self.assertIsNone(next_runnable(data))
    def test_current_manifest_preserves_authority_boundaries(self):
        data = load(); self.assertTrue(all(not v for v in data["authority"].values()))

if __name__ == "__main__": unittest.main()
