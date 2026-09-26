from __future__ import annotations
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from r8_deployment_qualification_gate import evaluate

class DeploymentGateTests(unittest.TestCase):
    def base(self):
        return {"schema":"deployment/v1","release_artifact_sha256":"a"*64,"environment_identity":"env-test","environment_digest":"b"*64,"config_digest":"c"*64,"migration_check":True,"preflight":True,"health_checks":True,"rollback_plan":True,"post_deploy_evidence":False,"deployment_authorized":False}
    def test_dry_run_qualifies_only_evidence(self): self.assertFalse(evaluate(self.base(), expected_artifact="a"*64, expected_environment="env-test")["deployment_authorized"])
    def test_drift_rejected(self):
        x=self.base(); x["environment_identity"]="unknown"
        with self.assertRaises(ValueError): evaluate(x, expected_artifact="a"*64, expected_environment="env-test")
    def test_partial_health_rejected(self):
        x=self.base(); x["health_checks"]=False
        with self.assertRaises(ValueError): evaluate(x, expected_artifact="a"*64, expected_environment="env-test")
    def test_missing_rollback_rejected(self):
        x=self.base(); x["rollback_plan"]=False
        with self.assertRaises(ValueError): evaluate(x, expected_artifact="a"*64, expected_environment="env-test")
    def test_authorization_rejected(self):
        x=self.base(); x["deployment_authorized"]=True
        with self.assertRaises(ValueError): evaluate(x, expected_artifact="a"*64, expected_environment="env-test")

if __name__ == "__main__": unittest.main()
