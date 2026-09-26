"""Machine-readable queue selector/report generator; human boundaries never stop other tasks."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "governance-r8/CODEX-WORK-QUEUE-51.json"

def load(): return json.loads(MANIFEST.read_text(encoding="utf-8"))

def next_runnable(data: dict) -> dict | None:
    done = {t["id"] for t in data["tasks"] if t["state"] == "CODE_COMPLETE"}
    for task in data["tasks"]:
        if task["state"] in {"CODE_COMPLETE", "MANUAL_INTERVENTION_REQUIRED", "REVIEW_REQUIRED"}: continue
        if all(dep in done for dep in task["dependencies"]): return task
    return None

def report(data: dict) -> str:
    lines = ["# Issue #51 consolidated queue report", "", "| PR | branch | state | manual intervention |", "|---:|---|---|---|"]
    for t in data["tasks"]:
        lines.append(f"| #{t['pr']} | {t['branch']} | {t['state']} | {t['manual_intervention']} |")
    lines += ["", "Authority remains NONE; no merge, activation, runtime, release, deployment, or production action is granted."]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    data = load(); task = next_runnable(data)
    print(json.dumps({"next_runnable": task, "queue_exhausted": task is None, "report": report(data)}, sort_keys=True))
