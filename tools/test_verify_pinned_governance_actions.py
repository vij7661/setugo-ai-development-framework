from pathlib import Path
from verify_pinned_governance_actions import WORKFLOWS,verify,verify_inventory
def rejects(value):
 try:verify(value)
 except ValueError:return
 raise AssertionError("mutable/unsafe action accepted")
def main():
 verify_inventory()
 for bad in ("uses: actions/checkout@v4","uses: actions/checkout@v4 # mutable",'uses: "actions/checkout@v4"',"uses: 'actions/checkout@v4' # mutable",'steps:\n  - {"uses": actions/checkout@v4}',"steps:\n  - {'uses': actions/checkout@v4}","jobs:\n  reusable:\n    uses: owner/workflow/.github/workflows/reuse.yml@v4","uses: docker://alpine:latest"):
   rejects(bad)
 for bad in ("uses: >-\n  actions/checkout@v4","uses: |\n  actions/checkout@v4","steps:\n  - {uses: >-\n      actions/checkout@v4}"):
  rejects(bad)
 for bad in ('steps:\n  - {"u\\x73es": actions/checkout@v4}','steps:\n  - {uses: &pin actions/checkout@v4}','steps:\n  - {uses: *pin}','steps:\n  - {uses: !Ref actions/checkout@v4}','steps:\n  - {uses:\n      actions/checkout@v4}'):
  rejects(bad)
 verify("steps:\n  - {uses: actions/checkout@"+"a"*40+"}")
 verify("steps:\n  - uses: docker://alpine@sha256:"+"a"*64)
 verify("steps:\n  - uses: './.github/actions/governed'")
 rejects("steps:\n  - uses: ./../outside")
 try:verify_inventory(tuple(WORKFLOWS[:-1]))
 except ValueError:pass
 else:raise AssertionError("omitted governed workflow accepted")
 print("PINNED_GOVERNANCE_ACTIONS_ADVERSARIAL_PASS")
if __name__=="__main__":main()
