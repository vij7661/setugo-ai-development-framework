import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import provider_router
from adapters import AdapterResult
class FakeAdapter:
 calls=[]
 def __init__(self,config): self.config=config
 def invoke(self,envelope):
  self.calls.append((self.config.provider_id,envelope['mechanism']['mechanism_id'],envelope['run_id']))
  if self.config.provider_id=='mistral': raise RuntimeError('provider HTTP 429 exhausted (attempt 3/3)')
  return AdapterResult(status='PASS',raw_output='fallback ok',provider=self.config.provider_id,mechanism_version=self.config.model,input_tokens=1,output_tokens=2,estimated_cost_usd=0.0,latency_ms=3,evidence_eligible=True)
class RouterTest(unittest.TestCase):
 def test_first_success_stops_later_calls_and_publishes_trail(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);case=root/'case.json';registry=root/'m.json';out=root/'o.json';evidence=root/'ev.json'
   case.write_text(json.dumps({'case_id':'EXP-C-001','experiment_id':'EXP-C','version':1,'risk':'HIGH','artifact_ref':'fixture','model_visible':{'task':'x'}}))
   mechanisms=[]
   for mid,provider in [('m1','mistral'),('m2','groq'),('m3','gemini')]: mechanisms.append({'mechanism_id':mid,'enabled':True,'kind':'reasoning-model','adapter':'openai-compatible','provider':provider,'base_url':'x','model':provider+'-model','api_key_env':provider.upper()+'_API_KEY'})
   registry.write_text(json.dumps({'mechanisms':mechanisms}));FakeAdapter.calls=[]
   argv=['provider_router.py','--case',str(case),'--mechanisms',str(registry),'--order','m1,m2,m3','--instruction-version','router-test-v1','--out',str(out),'--evidence-out',str(evidence)]
   with patch('provider_router.OpenAICompatibleAdapter',FakeAdapter),patch('sys.argv',argv): self.assertEqual(provider_router.main(),0)
   ev=json.loads(evidence.read_text());result=json.loads(out.read_text())
   self.assertEqual([c[0] for c in FakeAdapter.calls],['mistral','groq']);self.assertEqual(ev['selected_mechanism'],'m2');self.assertEqual([x['status'] for x in ev['attempts']],['FAILED','SUCCESS','NOT_CALLED']);self.assertEqual(ev['attempts'][0]['attempts'],3);self.assertEqual(ev['attempts'][2]['attempts'],0);self.assertEqual(ev['routing_rule'],'QUALIFIED_FIRST_SUCCESS');self.assertEqual(result['mechanism_id'],'m2');self.assertFalse(ev['portfolio_exhausted'])
if __name__=='__main__': unittest.main()
