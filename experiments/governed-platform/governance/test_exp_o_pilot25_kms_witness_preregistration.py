import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
PREREG=ROOT/'adjudication'/'EXP-O-PILOT25-KMS-WITNESS-INTEGRATION-PREREGISTRATION.md'
RUNNER=ROOT/'runner'/'run_exp_o_pilot25_kms_witness.py'
WORKFLOW=ROOT.parents[1]/'.github'/'workflows'/'governed-platform-exp-o-pilot25-kms-witness.yml'
TRIGGER=ROOT.parents[1]/'.github'/'exp-o-pilot25-kms-witness-trigger.json'

class ExpOPilot25PreExecutionIntegrityTests(unittest.TestCase):
    def test_preregistration_freezes_twenty_cases_and_external_path(self):
        t=PREREG.read_text()
        for i in range(1,21):
            self.assertIn(f'P25-{i:02d}',t)
        self.assertIn('ECC_NIST_P256',t)
        self.assertIn('ECDSA_SHA_256',t)
        self.assertIn('no AWS credentials',t)

    def test_runner_strips_aws_credentials_from_witness_children(self):
        t=RUNNER.read_text()
        self.assertIn('if k.startswith("AWS_")',t)
        self.assertIn('AWS_CREDENTIALS_PRESENT',t)
        self.assertIn('P25_WITNESS_KEY',t)

    def test_runner_has_exact_kms_identity_and_no_destructive_admin_calls(self):
        t=RUNNER.read_text()
        self.assertIn('57d95d4f-9b80-44e4-badf-0330ba9f897c',t)
        self.assertIn('ECDSA_SHA_256',t)
        lower=t.lower()
        for forbidden in ['disable-key','schedule-key-deletion','create-key','put-key-policy']:
            self.assertNotIn(forbidden,lower)

    def test_runner_keeps_signature_provenance_separate_from_authority(self):
        t=RUNNER.read_text()
        self.assertIn('model_authority_effect',t)
        self.assertIn('authoritative_platform_effect_count',t)
        self.assertIn('STALE_GENERATION',t)
        self.assertIn('SAME_GENERATION_CONFLICT',t)

    def test_workflow_is_trigger_only_oidc_and_exact_role(self):
        t=WORKFLOW.read_text()
        self.assertIn('id-token: write',t)
        self.assertIn('aws-actions/configure-aws-credentials@v4',t)
        self.assertIn('arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer',t)
        self.assertIn('exp-o-pilot25-kms-witness-trigger.json',t)
        self.assertNotRegex(t,re.compile(r'secrets\.[A-Za-z0-9_]*AWS',re.I))

    def test_workflow_guard_precedes_oidc_execution(self):
        t=WORKFLOW.read_text()
        self.assertLess(t.index('Enforce frozen Pilot 25 trigger'),t.index('Configure temporary AWS credentials'))
        self.assertIn("git','diff','--exit-code'",t)

    def test_trigger_if_present_binds_full_design_sha(self):
        if not TRIGGER.exists():
            return
        d=json.loads(TRIGGER.read_text())
        self.assertEqual(d['experiment'],'EXP-O')
        self.assertEqual(d['pilot'],'PILOT25-KMS-WITNESS-INTEGRATION')
        self.assertEqual(d['nonce'],'pilot25-kms-witness-1')
        self.assertRegex(d['design_commit'],r'^[0-9a-f]{40}$')
        self.assertRegex(d['created_at_utc'],r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

if __name__=='__main__':
    unittest.main()
