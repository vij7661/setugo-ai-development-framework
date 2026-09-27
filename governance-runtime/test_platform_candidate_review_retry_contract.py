import copy,json,unittest
from unittest.mock import Mock,patch
import platform_candidate_review as review
from provider_api_request_contract import gemini_adapter_semantic_request
class Tests(unittest.TestCase):
 def test_unsupported_retry_policy_fails_before_transport(self):
  bad=gemini_adapter_semantic_request(model="m",prompt="p");bad["retry_policy"]={"max_attempts":2,"retry_on":[]}
  with patch.object(review,"gemini_adapter_semantic_request",return_value=bad),patch.object(review,"urlopen") as transport:
   with self.assertRaisesRegex(ValueError,"unsupported Gemini semantic execution contract"):review.invoke("secret","m","p")
  transport.assert_not_called()
 def test_admitted_contract_performs_exactly_one_transport_attempt(self):
  payload={"candidates":[{"finishReason":"STOP","content":{"parts":[{"text":"{}"}]}}]};response=Mock();response.read.return_value=json.dumps(payload).encode();cm=Mock();cm.__enter__=Mock(return_value=response);cm.__exit__=Mock(return_value=False)
  with patch.object(review,"urlopen",return_value=cm) as transport:review.invoke("secret","m","p")
  transport.assert_called_once()
if __name__=="__main__":unittest.main()
