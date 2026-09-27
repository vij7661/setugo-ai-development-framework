from verify_q17_ingestion_workflows import REQUIRED,verify
def main():
 for path,items in REQUIRED.items():
  text=path.read_text(encoding="utf-8");verify(path,text)
  for item in items:
   commented=text.replace("python3 "+item,"# python3 "+item,1)
   try:verify(path,commented)
   except ValueError:pass
   else:raise AssertionError(f"comment substitution accepted: {item}")
  for malicious in ("python3 evidence-ref/governance-runtime/github_evidence_ingestion.py","python3 evidence-ref/governance-runtime/manual_review_ingestion.py","bash evidence-ref/.github/workflows/malicious.yml"):
   try:verify(path,text+"\n      - name: malicious\n        run: "+malicious+"\n")
   except ValueError:pass
   else:raise AssertionError("evidence-ref executable code accepted")
 print("Q17_INGESTION_WORKFLOW_ADVERSARIAL_PASS")
if __name__=="__main__":main()
