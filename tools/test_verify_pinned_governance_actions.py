from verify_pinned_governance_actions import WORKFLOWS,verify
def main():
 for path in WORKFLOWS:
  text=path.read_text(encoding="utf-8");verify(text)
  mutated=text.replace("@3d3c42e5aac5ba805825da76410c181273ba90b1","@v4",1) if "@3d3c42" in text else text.replace("@65462800fd760344b1a7b4382951275a0abb4808","@v4",1)
  try:verify(mutated)
  except ValueError:pass
  else:raise AssertionError(f"mutable tag accepted: {path}")
 for bad in ("uses: actions/checkout@v4","uses: actions/checkout@v4 # mutable",'uses: "actions/checkout@v4"',"uses: 'actions/checkout@v4' # mutable"):
  try:verify("steps:\n  - "+bad+"\n")
  except ValueError:pass
  else:raise AssertionError(f"mutable quoted/comment action accepted: {bad}")
 verify("steps:\n  - uses: './.github/actions/governed' # explicit local\n")
 try:verify("steps:\n  - uses: docker://alpine:latest\n")
 except ValueError:pass
 else:raise AssertionError("mutable Docker action accepted")
 print("PINNED_GOVERNANCE_ACTIONS_ADVERSARIAL_PASS")
if __name__=="__main__":main()
