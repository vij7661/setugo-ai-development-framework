from verify_q16_invariant_workflow import REQUIRED, WORKFLOW, verify

def main():
    text=WORKFLOW.read_text(encoding="utf-8"); verify(text)
    for item in REQUIRED:
        try: verify(text.replace(item,"",1))
        except ValueError: pass
        else: raise AssertionError(f"workflow removal not detected: {item}")
    target=REQUIRED[0]
    commented=text.replace(f"run: python3 {target}",f"run: |\n          # python3 {target}",1)
    try: verify(commented)
    except ValueError: pass
    else: raise AssertionError("comment substitution satisfied executable coverage")
    print(f"Q16_INVARIANT_WORKFLOW_ADVERSARIAL_PASS required={len(REQUIRED)}")

if __name__=="__main__": main()
