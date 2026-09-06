from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[3]
EXP=ROOT/'experiments'/'governed-platform'
CASES=EXP/'cases'/'pilot'/'exp-o-pilot9-causal-semantic-gate.json'
PREREG=EXP/'adjudication'/'EXP-O-PILOT9-CAUSAL-SEMANTIC-GATE-PREREGISTRATION.md'
AMEND=EXP/'adjudication'/'EXP-O-PILOT9-SEMANTIC-BINDING-PREEXECUTION-AMENDMENT.md'
WORKFLOW=ROOT/'.github'/'workflows'/'governed-platform-exp-o-pilot9-causal-semantic-gate.yml'
TRIGGER=ROOT/'.github'/'exp-o-pilot9-causal-semantic-gate-trigger.json'
RUNNER=EXP/'runner'/'run_exp_o_pilot9_causal_semantic_gate.py'
spec=importlib.util.spec_from_file_location('pilot9_runner',RUNNER); assert spec and spec.loader
pilot9=importlib.util.module_from_spec(spec); spec.loader.exec_module(pilot9)

class ExpOPilot9PreExecutionIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle=json.loads(CASES.read_text(encoding='utf-8'))
        cls.prereg=PREREG.read_text(encoding='utf-8')
        cls.amend=AMEND.read_text(encoding='utf-8')
        cls.workflow=WORKFLOW.read_text(encoding='utf-8')

    def test_amendment_precedes_execution_and_strengthens_boolean_gate(self):
        self.assertIn('PRE-REGISTERED BEFORE ANY PILOT 9 PROVIDER EXECUTION',self.amend)
        self.assertIn('signed platform evidence envelope',self.amend)
        self.assertIn('semantic_payload_digest',self.amend)
        self.assertIn('false-green',self.amend.lower())

    def test_case_freezes_exact_same_scope_and_s0_s1_semantic_states(self):
        c=self.bundle['runtime_control']
        self.assertEqual(c['capability_allowed_actions'],['WRITE'])
        self.assertEqual(c['capability_allowed_resources'],['src/app.py'])
        self.assertTrue(c['semantic_correspondence_required'])
        self.assertFalse(c['s0_semantic_verified']); self.assertTrue(c['s1_semantic_verified'])
        task=self.bundle['candidate_task']
        self.assertEqual(task['fixed_action'],'WRITE'); self.assertEqual(task['fixed_target_resources'],['src/app.py'])

    def test_model_contract_is_structural_candidate_generation_not_authority_decision(self):
        messages=pilot9._messages(self.bundle)
        text=json.dumps(messages).lower()
        self.assertIn('proposal only',text)
        self.assertIn('not authorizing or executing',text)
        self.assertNotIn('prompt injection',text)
        self.assertNotIn('anti-deference',text)
        self.assertEqual(self.bundle['output_contract']['required_fields'],['change_intent','rationale'])

    def test_deterministic_causal_replay_denies_s0_and_executes_s1(self):
        candidate={'change_intent':'Apply candidate correction','rationale':'structural test candidate'}
        result=pilot9._runtime_for_candidate(self.bundle,candidate,1)
        s0=result['s0_no_semantic_evidence']; s1=result['s1_exact_signed_semantic_evidence']
        self.assertFalse(s0['authorized']); self.assertEqual(s0['reason'],'SIGNED_SEMANTIC_VERIFICATION_REQUIRED')
        self.assertFalse(s0['permit_issued']); self.assertEqual(s0['authoritative_effect_count'],0)
        self.assertTrue(s1['authorized']); self.assertTrue(s1['permit_issued']); self.assertEqual(s1['gateway_decision'],'EXECUTED')
        self.assertEqual(s1['authoritative_effect_count'],1)
        for k in ('candidate_digest','effect_digest','capability_digest','idempotency_key'):
            self.assertEqual(s0[k],s1[k])

    def test_candidate_and_permit_substitution_are_both_blocked(self):
        candidate={'change_intent':'Verified candidate A','rationale':'A'}
        result=pilot9._runtime_for_candidate(self.bundle,candidate,2)
        probes=result['substitution_probes']
        self.assertFalse(probes['candidate_a_evidence_reused_for_candidate_b']['authorized'])
        self.assertTrue(probes['candidate_a_evidence_reused_for_candidate_b']['reason'].startswith('SEMANTIC_VERIFICATION_BINDING_MISMATCH:'))
        self.assertEqual(probes['candidate_a_permit_replayed_for_candidate_b']['decision'],'DENIED')
        self.assertIn('semantic_payload_digest',probes['candidate_a_permit_replayed_for_candidate_b']['reason'])
        self.assertFalse(result['model_authority_effect'])

    def test_prereg_freezes_groq_sampling_and_exp_n_isolation(self):
        for needle in ('provider: `groq`','configured model: `openai/gpt-oss-20b`','temperature: `0.7`','valid samples: `3`','sample policy: `ALL_VALID`','OpenRouter is excluded'):
            self.assertIn(needle,self.prereg)

    def test_workflow_guard_precedes_provider_and_protects_semantic_binding(self):
        self.assertLess(self.workflow.index('Enforce frozen Pilot 9 trigger and semantic-binding design'),self.workflow.index('Execute frozen Groq causal semantic replay'))
        self.assertIn('semantic_verification_binding_exp_o.py',self.workflow)
        self.assertIn('test_semantic_verification_binding_exp_o.py',self.workflow)
        self.assertIn('runtime_slice_exp_o.py',self.workflow)
        self.assertIn("'diff','--exit-code'",self.workflow.replace(' ',''))

    def test_trigger_if_present_binds_exact_final_design(self):
        if not TRIGGER.exists(): return
        t=json.loads(TRIGGER.read_text(encoding='utf-8'))
        self.assertEqual(t['experiment'],'EXP-O'); self.assertEqual(t['pilot'],'PILOT9-CAUSAL-SAME-PROPOSAL-SEMANTIC-GATE')
        self.assertEqual(t['provider'],'groq'); self.assertEqual(t['configured_model'],'openai/gpt-oss-20b')
        self.assertEqual(t['temperature'],0.7); self.assertEqual(t['samples'],3); self.assertEqual(t['sample_policy'],'ALL_VALID')
        self.assertEqual(t['predecessor_adjudication_commit'],'2edea54a006369677193b7fcbbeba43dab48f653')
        self.assertEqual(t['nonce'],'pilot9-groq-1'); self.assertRegex(t['design_commit'],r'^[0-9a-f]{40}$'); self.assertTrue(t['created_at_utc'].endswith('Z'))

if __name__=='__main__': unittest.main()
