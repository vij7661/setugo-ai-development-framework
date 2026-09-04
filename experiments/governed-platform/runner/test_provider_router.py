import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import provider_router
from adapters import AdapterResult


class FakeAdapter:
    calls=[]
    def __init__(self, config): self.config=config
    def invoke(self, envelope):
        self.calls.append((self.config.provider_id,envelope['mechanism']['mechanism_id'],envelope['run_id']))
        if self.config.provider_id == 'mistral':
            raise RuntimeError('provider HTTP 429 exhausted')
        return AdapterResult(status='PASS',raw_output='fallback ok',provider=self.config.provider_id,mechanism_version=self.config.model,input_tokens=1,output_tokens=2,estimated_cost_usd=0.0,latency_ms=3,evidence_eligible=True)


class RouterTest(unittest.TestCase):
    def test_failure_falls_through_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); case=root/'case.json'; registry=root/'m.json'; out=root/'o.json'; evidence=root/'ev.json'
            case.write_text(json.dumps({'case_id':'EXP-C-001','experiment_id':'EXP-C','version':1,'risk':'HIGH','artifact_ref':'fixture','model_visible':{'task':'x'}}))
            registry.write_text(json.dumps({'mechanisms':[
                {'mechanism_id':'m1','enabled':True,'kind':'reasoning-model','adapter':'openai-compatible','provider':'mistral','base_url':'x','model':'m','api_key_env':'MISTRAL_API_KEY'},
                {'mechanism_id':'m2','enabled':True,'kind':'reasoning-model','adapter':'openai-compatible','provider':'groq','base_url':'x','model':'g','api_key_env':'GROQ_API_KEY'}]}))
            FakeAdapter.calls=[]
            argv=['provider_router.py','--case',str(case),'--mechanisms',str(registry),'--order','m1,m2','--instruction-version','router-test-v1','--out',str(out),'--evidence-out',str(evidence)]
            with patch('provider_router.OpenAICompatibleAdapter',FakeAdapter), patch('sys.argv',argv):
                self.assertEqual(provider_router.main(),0)
            ev=json.loads(evidence.read_text()); result=json.loads(out.read_text())
            self.assertEqual([c[0] for c in FakeAdapter.calls],['mistral','groq'])
            self.assertEqual([c[1] for c in FakeAdapter.calls],['m1','m2'])
            self.assertNotEqual(FakeAdapter.calls[0][2],FakeAdapter.calls[1][2])
            self.assertEqual(ev['selected_mechanism'],'m2')
            self.assertEqual(ev['attempts'][0]['status'],'PROVIDER_FAILURE')
            self.assertEqual(ev['attempts'][1]['status'],'PASS')
            self.assertEqual(result['mechanism_id'],'m2')
            self.assertFalse(ev['portfolio_exhausted'])

if __name__=='__main__': unittest.main()
