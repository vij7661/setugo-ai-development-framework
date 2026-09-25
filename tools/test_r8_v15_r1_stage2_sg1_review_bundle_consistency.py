from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_r8_v15_r1_stage2_sg1_review_bundle_consistency import verify


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json"
BINDING = ROOT / "governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json"
PACKET = ROOT / "stage2-sg1-review/R8-V15-R1-STAGE2-SG1-CONSOLIDATED-REVIEW-002-PACKET.txt"


class SG1ReviewBundleConsistencyTests(unittest.TestCase):
    def assert_mutation_rejected(self, mutate):
        root = ROOT / "stage2-sg1-review"
        manifest = root / ".sg1-test-manifest.json"
        binding = root / ".sg1-test-binding.json"
        packet = root / ".sg1-test-packet.txt"
        try:
            manifest.write_bytes(MANIFEST.read_bytes())
            binding.write_bytes(BINDING.read_bytes())
            packet.write_bytes(PACKET.read_bytes())
            mutate(manifest, binding, packet)
            with self.assertRaises(SystemExit):
                verify(manifest, binding, packet)
        finally:
            for path in (manifest, binding, packet):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass

    def test_clean_bundle_passes(self):
        result = verify(MANIFEST, BINDING, PACKET)
        self.assertEqual(result["status"], "PASS")

    def test_old_gate_in_h_final_gate_rejected(self):
        def mutate(_, __, packet):
            text = packet.read_text(encoding="utf-8")
            packet.write_text(text.replace("activation-gate blob 1078bc673665b3e23d99d2d1699a7ccab90bbf6d", "activation-gate blob 056bce33da38a2178ca2827d581b5a81c8bf4416"), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_review001_cannot_be_current_review(self):
        def mutate(_, binding, packet):
            value = json.loads(binding.read_text(encoding="utf-8"))
            value["expected_review"]["path"] = "governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-001.txt"
            binding.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_proposal_identity_rejected(self):
        def mutate(manifest, _, __):
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["proposal"]["commit"] = "0" * 40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_proposal_blob_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["proposal"]["blob_sha1"]="0"*40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_candidate_commit_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["candidate"]["commit"]="0"*40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_candidate_tree_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["candidate"]["tree"]="0"*40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_candidate_parent_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["candidate"]["parent"]="0"*40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_evidence_blob_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); key=next(iter(value["evidence"])); value["evidence"][key]="0"*40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_binding_machinery_map_drift_rejected(self):
        def mutate(_, binding, __):
            value=json.loads(binding.read_text(encoding="utf-8")); key=next(iter(value["exact_required_machinery"])); value["exact_required_machinery"][key]="0"*40
            binding.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_binding_evidence_map_drift_rejected(self):
        def mutate(_, binding, __):
            value=json.loads(binding.read_text(encoding="utf-8")); key=next(iter(value["exact_required_evidence"])); value["exact_required_evidence"][key]="0"*40
            binding.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_review_path_drift_rejected(self):
        def mutate(manifest, binding, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["reviews"]["expected_fresh_review_002"]["path"]="wrong.txt"; manifest.write_text(json.dumps(value), encoding="utf-8")
            value=json.loads(binding.read_text(encoding="utf-8")); value["expected_review"]["path"]="wrong.txt"; binding.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_extra_authority_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["governance"]["broader_stage2_authorized"]=True; manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_runtime_authority_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["governance"]["runtime_release_deployment_production_policy_constitutional_root_terminal_authority"]=True; manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_six_slice_restored_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["governance"]["six_slice_cadence_restored"]=True; manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_review001_manifest_blob_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["reviews"]["historical_review_001"]["blob_sha1"]="0"*40; manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_old_gate_outside_history_rejected(self):
        def mutate(_, __, packet):
            packet.write_text(packet.read_text(encoding="utf-8") + "\n056bce33da38a2178ca2827d581b5a81c8bf4416\n", encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_wrong_machinery_blob_rejected(self):
        def mutate(manifest, _, __):
            value = json.loads(manifest.read_text(encoding="utf-8"))
            key = next(iter(value["machinery"]))
            value["machinery"][key] = "0" * 40
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_authority_and_cadence_mutations_rejected(self):
        def mutate(manifest, _, __):
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["governance"]["fallback_to_3"] = "RESTORED"
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_missing_review001_rejected(self):
        def mutate(manifest, _, __):
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["reviews"]["historical_review_001"]["disposition"] = "BOUNDED_PASS"
            manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_review001_actually_missing_rejected(self):
        def mutate(manifest, _, __):
            value=json.loads(manifest.read_text(encoding="utf-8")); value["reviews"]["historical_review_001"]["path"]="governance-r8/MISSING-REVIEW-001.txt"; manifest.write_text(json.dumps(value), encoding="utf-8")
        self.assert_mutation_rejected(mutate)

    def test_activation_artifact_is_rejected(self):
        def mutate(manifest, _, __):
            (ROOT / "governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json").write_text("{}", encoding="utf-8")
        self.assert_mutation_rejected(mutate)
        (ROOT / "governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json").unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
