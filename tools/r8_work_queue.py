"""Machine-readable queue selector/report generator; human boundaries never stop other tasks."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "governance-r8/CODEX-WORK-QUEUE-51.json"
ALLOWED_STATES = {"RUNNABLE_CODING", "CODE_COMPLETE", "HUMAN_REVIEW_BLOCKED", "MANUAL_INTERVENTION_BLOCKED", "CODE_DEPENDENCY_BLOCKED", "TERMINAL"}

def load():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for task in data["tasks"]:
        if task.get("state") not in ALLOWED_STATES: raise ValueError("unknown queue state")
        manual = task.get("manual")
        if not isinstance(manual, dict) or not manual.get("reason") or not manual.get("evidence_refs") or not manual.get("requested_action") or not manual.get("blocking_status"):
            raise ValueError("manual intervention record incomplete")
    return data

def next_runnable(data: dict) -> dict | None:
    done = {t["id"] for t in data["tasks"] if t["state"] in {"CODE_COMPLETE", "TERMINAL"}}
    for task in data["tasks"]:
        if task["state"] != "RUNNABLE_CODING": continue
        if all(dep in done for dep in task["dependencies"]): return task
    return None

def report(data: dict) -> str:
    lines = [f"# Issue #{data['issue']} consolidated queue report", "", "report_source_head: EXTERNAL_INPUT_REQUIRED", "final_remote_head_verified_externally: false", "", "| PR | branch | state | reason | evidence | requested action |", "|---:|---|---|---|---|---|"]
    for t in data["tasks"]:
        m=t["manual"]; lines.append(f"| #{t['pr']} | {t['branch']} | {t['state']} | {m['reason']} | {', '.join(m['evidence_refs'])} | {m['requested_action']} |")
    lines += ["", "Authority remains NONE; no merge, activation, runtime, release, deployment, or production action is granted."]
    return "\n".join(lines) + "\n"

def verify_external_head(data: dict, *, report_source_head: str, final_remote_head: str | None) -> bool:
    if not report_source_head or data.get("issue") != 52: return False
    return bool(final_remote_head and len(final_remote_head) == 40 and all(c in "0123456789abcdef" for c in final_remote_head))

if __name__ == "__main__":
    data = load(); task = next_runnable(data)
    print(json.dumps({"next_runnable": task, "queue_exhausted": task is None, "report": report(data)}, sort_keys=True))
