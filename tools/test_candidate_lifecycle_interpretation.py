from pathlib import Path
from r8_work_queue import current_lifecycle,load
def main():
 text=Path("standards/candidate-lifecycle-state-separation.md").read_text(encoding="utf-8")
 assert "point-in-time" in text and "never by interpreting historical negative prose" in text
 data=load();q16=next(t for t in data["tasks"] if t["id"]=="Q16");q17=next(t for t in data["tasks"] if t["id"]=="Q17")
 assert q16["candidate_state"]=="PRE_FREEZE_READY" and current_lifecycle(q16)=="FROZEN_VERIFIED"
    assert current_lifecycle(q17)=="FROZEN_VERIFIED"
 print("CANDIDATE_LIFECYCLE_INTERPRETATION_PASS")
if __name__=="__main__":main()
