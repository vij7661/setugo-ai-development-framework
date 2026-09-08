from __future__ import annotations

import subprocess


def git(root, *args):
    cp = subprocess.run(
        ["git", *args], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="strict",
    )
    if cp.returncode:
        raise RuntimeError(cp.stderr.strip() or "git failed")
    return cp.stdout


def complete_changed_file_inventory(root, base_commit, candidate_commit):
    """Return the complete name-status inventory before any policy filtering."""
    text = git(root, "diff", "--name-status", "--find-renames", base_commit, candidate_commit)
    items = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R"):
            if len(parts) != 3:
                raise RuntimeError("malformed rename record")
            items.append({"status": status, "old_path": parts[1], "new_path": parts[2]})
        else:
            if len(parts) != 2:
                raise RuntimeError("malformed change record")
            items.append({"status": status, "path": parts[1]})
    return {
        "base_commit": base_commit,
        "candidate_commit": candidate_commit,
        "count": len(items),
        "changes": items,
    }
