from verify_q17_ingestion_workflows import REQUIRED,verify
def main():
 for path,items in REQUIRED.items():
  text=path.read_text(encoding="utf-8");verify(path,text)
  for item in items:
   commented=text.replace("python3 "+item,"# python3 "+item,1)
   try:verify(path,commented)
   except ValueError:pass
   else:raise AssertionError(f"comment substitution accepted: {item}")
 print("Q17_INGESTION_WORKFLOW_ADVERSARIAL_PASS")
if __name__=="__main__":main()
