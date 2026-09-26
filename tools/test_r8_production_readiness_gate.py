from __future__ import annotations
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from r8_production_readiness_gate import evaluate

class ProductionReadinessTests(unittest.TestCase):
    def base(self):
        return {"schema":"production-readiness/v1","release_evidence_sha256":"a"*64,"deployment_evidence_sha256":"b"*64,"observability":True,"audit_history":True,"backup_recovery":True,"incident_rollback":True,"capacity_health":True,"secret_config":True,"dependency_failure":True,"production_authorized":False}
    def test_ready_evidence_not_authority(self): self.assertFalse(evaluate(self.base())["production_authorized"])
    def test_missing_observability_rejected(self):
        x=self.base(); x["observability"]=False
        with self.assertRaises(ValueError): evaluate(x)
    def test_missing_lineage_rejected(self):
        x=self.base(); x["release_evidence_sha256"]="x"
        with self.assertRaises(ValueError): evaluate(x)
    def test_production_authority_rejected(self):
        x=self.base(); x["production_authorized"]=True
        with self.assertRaises(ValueError): evaluate(x)

if __name__ == "__main__": unittest.main()
