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
 rejects(text.replace("jobs:\n  invariant-gate:","jobs:\n  attacker-job:\n    runs-on: ubuntu-24.04\n    permissions:\n      contents: write\n    steps:\n      - run: whoami\n  invariant-gate:",1))
 rejects(text.replace("      - name: Verify exact candidate invariants","      - run: whoami\n      - name: Verify exact candidate invariants",1))
 rejects(text.replace("      - name: Verify exact candidate invariants","      - name: attacker\n        run: whoami\n      - name: Verify exact candidate invariants",1))
 rejects(text.replace("      - name: Verify exact candidate invariants","      - name: Verify exact candidate invariants\n        env:\n          PATH: /tmp",1))
 rejects(text.replace("    runs-on: ubuntu-24.04","    runs-on: windows-latest",1))
 rejects(text.replace("    timeout-minutes: 30","    env:\n      PYTHONPATH: /tmp\n    timeout-minutes: 30",1))
 rejects(text.replace("jobs:\n  invariant-gate:","defaults:\n  run:\n    shell: bash\njobs:\n  invariant-gate:",1))
 rejects(text.replace("jobs:\n  invariant-gate:","jobs:\n  invariant-gate:\n    container: alpine",1))
 checkout='          fetch-depth: 0\n          persist-credentials: false'
 for extra in ("ref: attacker-branch","repository: attacker/repository","path: attacker","token: secret","clean: false","sparse-checkout: src","fetch-tags: true","lfs: true","submodules: true","fetch-depth: 1","persist-credentials: true","extra-input: value"):
  replacement=extra+"\n"+checkout if extra.split(":",1)[0] not in {"fetch-depth","persist-credentials"} else extra+"\n"+("          persist-credentials: false" if extra.startswith("fetch-depth") else "          fetch-depth: 0")
  rejects(text.replace(checkout,replacement,1))
 rejects(text.replace("        shell: bash\n        run: |","        shell: always-success {0}\n        run: |",1))
 rejects(text.replace("          set -euo pipefail","          echo bypass",1))
 rejects(text.replace("          print(f\"AST_SYNTAX_PASS files={len(files)}\")","          print('bypass')",1))
 rejects(text.replace("      - name: Syntax-check changed Python without writing bytecode\n        shell: bash\n        run: |","      - name: Syntax-check changed Python without writing bytecode\n        run: |",1))
 rejects(text.replace("        run: |","        run: >",1))
 rejects(text.replace("        run: |","        run: >-",1))
 print(f"Q18_INVARIANT_WORKFLOW_ADVERSARIAL_PASS required={len(CONTRACT)}")
if __name__=="__main__":main()
