import unittest
from unittest.mock import patch
from github_evidence_ingestion import GitHubREST,canonical_governed_ref
class Tests(unittest.TestCase):
 def test_branch_normalization(self):
  branch="frozen/r8-v15-r1-q17-q16-review-successor-2026-09-27"
  self.assertEqual(canonical_governed_ref(branch),"heads/"+branch)
  self.assertEqual(canonical_governed_ref("heads/"+branch),"heads/"+branch)
  self.assertEqual(canonical_governed_ref("refs/heads/"+branch),"heads/"+branch)
 def test_tag_is_explicit_policy(self):
  with self.assertRaises(ValueError):canonical_governed_ref("tags/v1")
  self.assertEqual(canonical_governed_ref("refs/tags/v1",allow_tags=True),"tags/v1")
 def test_malformed_fails_before_http(self):
  client=GitHubREST("token")
  with patch.object(client,"_get") as get:
   for value in ("","frozen//x","../x","refs/pull/1","frozen/../x"," frozen/x","frozen/x\\y"):
    with self.assertRaises(ValueError):client.resolve_ref("a/b",value)
   get.assert_not_called()
 def test_exact_url_contains_heads(self):
  client=GitHubREST("token")
  with patch.object(client,"_get",return_value={"object":{"sha":"a"*40}}) as get:
   client.resolve_ref("vij7661/setugo-ai-development-framework","frozen/r8-v15-r1-q17-q16-review-successor-2026-09-27")
   self.assertEqual(get.call_args.args[0],"https://api.github.com/repos/vij7661/setugo-ai-development-framework/git/ref/heads/frozen/r8-v15-r1-q17-q16-review-successor-2026-09-27")
if __name__=="__main__":unittest.main()
