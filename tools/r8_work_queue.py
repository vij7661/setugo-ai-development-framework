"""Machine-readable queue selector/report generator; human boundaries never stop other tasks."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "governance-r8/CODEX-WORK-QUEUE-51.json"
ALLOWED_STATES = {"RUNNABLE_CODING", "CODE_COMPLETE", "HUMAN_REVIEW_BLOCKED", "MANUAL_INTERVENTION_BLOCKED", "CODE_DEPENDENCY_BLOCKED", "TERMINAL"}
ALLOWED_BLOCKING = {"HUMAN_REVIEW_BLOCKED", "MANUAL_INTERVENTION_BLOCKED", "CODE_DEPENDENCY_BLOCKED"}
AUTHORITY_KEYS = {"runtime", "release", "deployment", "production", "merge", "activation"}
HEAD_RE = re.compile(r"[0-9a-f]{40}\Z")

def load():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if set(data.get("authority", {})) != AUTHORITY_KEYS or any(data["authority"].values()):
        raise ValueError("authority boundary must contain exactly false values")
    ids = {task.get("id") for task in data.get("tasks", [])}
    if None in ids or len(ids) != len(data.get("tasks", [])):
        raise ValueError("duplicate or missing task id")
    for task in data["tasks"]:
        if task.get("state") not in ALLOWED_STATES: raise ValueError("unknown queue state")
        if any(dep not in ids for dep in task.get("dependencies", [])): raise ValueError("unknown dependency")
        manual = task.get("manual")
        if not isinstance(manual, dict) or not manual.get("reason") or not manual.get("evidence_refs") or not manual.get("requested_action") or not manual.get("blocking_status"):
            raise ValueError("manual intervention record incomplete")
        if manual["blocking_status"] not in ALLOWED_BLOCKING:
            raise ValueError("unknown manual blocking status")
        if task["state"] in ALLOWED_BLOCKING and manual["blocking_status"] != task["state"]:
            raise ValueError("manual blocking status incompatible with task state")
    return data

def next_runnable(data: dict) -> dict | None:
    done = {t["id"] for t in data["tasks"] if t["state"] in {"CODE_COMPLETE", "TERMINAL"}}
    for task in data["tasks"]:
        if task["state"] != "RUNNABLE_CODING": continue
        if all(dep in done for dep in task["dependencies"]): return task
    return None

def verify_external_head(data: dict, *, report_source_head: str, final_remote_head: str | None, expected_external_head: str | None) -> bool:
    if data.get("issue") != 52 or not HEAD_RE.fullmatch(report_source_head or "") or not HEAD_RE.fullmatch(expected_external_head or "") or not HEAD_RE.fullmatch(final_remote_head or ""):
        return False
    return final_remote_head == expected_external_head

def report(data: dict, *, report_source_head: str = "EXTERNAL_INPUT_REQUIRED", final_remote_head: str | None = None, expected_external_head: str | None = None) -> str:
    verified = verify_external_head(data, report_source_head=report_source_head, final_remote_head=final_remote_head, expected_external_head=expected_external_head)
    lines = [f"# Issue #{data['issue']} consolidated queue report", "", f"report_source_head: {report_source_head}", f"final_remote_head_verified_externally: {str(verified).lower()}", "", "| PR | branch | state | reason | evidence | requested action |", "|---:|---|---|---|---|---|"]
    for t in data["tasks"]:
        m=t["manual"]; lines.append(f"| #{t['pr']} | {t['branch']} | {t['state']} | {m['reason']} | {', '.join(m['evidence_refs'])} | {m['requested_action']} |")
    lines += ["", "Authority remains NONE; no merge, activation, runtime, release, deployment, or production action is granted."]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    data = load(); task = next_runnable(data)
    print(json.dumps({"next_runnable": task, "queue_exhausted": task is None, "report": report(data)}, sort_keys=True))
