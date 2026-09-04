import json
import os
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
        self.calls.append(self.config.provider_id)
        if self.config.provider_id == 'mistral':
            raise RuntimeError('provider HTTP 429 exhausted')
        return AdapterResult(status='PASS',raw_output='fallback ok',provider=self.config.provider_id,mechanism_version=self.config.model,input_tokens=1,output_tokens=2,estimated_cost_usd=0.0,latency_ms=3,evidence_eligible=True)


class RouterTest(unittest.TestCase):
    def test_failure_falls_through_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); envelope=root/'e.json'; registry=root/'m.json'; out=root/'o.json'; evidence=root/'ev.json'
            envelope.write_text(json.dumps({'model_visible':{},'mechanism':{}}))
            registry.write_text(json.dumps({'mechanisms':[
                {'mechanism_id':'m1','enabled':True,'provider':'mistral','base_url':'x','model':'m','api_key_env':'MISTRAL_API_KEY'},
                {'mechanism_id':'m2','enabled':True,'provider':'groq','base_url':'x','model':'g','api_key_env':'GROQ_API_KEY'}]}))
            FakeAdapter.calls=[]
            with patch('provider_router.OpenAICompatibleAdapter',FakeAdapter), patch('sys.argv',['provider_router.py','--envelope',str(envelope),'--mechanisms',str(registry),'--order','m1,m2','--out',str(out),'--evidence-out',str(evidence)]):
                self.assertEqual(provider_router.main(),0)
            ev=json.loads(evidence.read_text())
            self.assertEqual(FakeAdapter.calls,['mistral','groq'])
            self.assertEqual(ev['selected_mechanism'],'m2')
            self.assertEqual(ev['attempts'][0]['status'],'PROVIDER_FAILURE')
            self.assertEqual(ev['attempts'][1]['status'],'PASS')
            self.assertFalse(ev['portfolio_exhausted'])

if __name__=='__main__': unittest.main()
