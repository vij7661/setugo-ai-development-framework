from verify_q16_invariant_workflow import CONTRACT,WORKFLOW,verify
def rejects(text):
 try:verify(text)
 except ValueError:return
 raise AssertionError("weakened workflow accepted")
def main():
 text=WORKFLOW.read_text(encoding="utf-8");verify(text)
 name,command=next(iter(CONTRACT.items()));needle=f"run: {command}"
 for replacement in (f'run: echo "{command}"',f"run: printf '{command}'",f"run: |\n          cat <<'EOF'\n          {command}\n          EOF",f"run: |\n          exit 0\n          {command}"):
  rejects(text.replace(needle,replacement,1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        continue-on-error: true",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        shell: 'always-success {0}'",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"shell\": \"always-success {{0}}\"",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"if\": always()",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"continue-on-error\": true",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"sh\\x65ll\": \"always-success {{0}}\"",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"\\x69f\": always()",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"\\x63ontinue-on-error\": true",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        \"\\x72un\": true",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        shell: &weak always-success {{0}}",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        shell: *weak",1))
 rejects(text.replace(f"- name: {name}",f"- name: {name}\n        shell: !Ref always-success",1))
 for step,cmd in CONTRACT.items():rejects(text.replace(f"run: {cmd}","run: true",1))
 print(f"Q18_INVARIANT_WORKFLOW_ADVERSARIAL_PASS required={len(CONTRACT)}")
if __name__=="__main__":main()
