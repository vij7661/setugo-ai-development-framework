"""Durable local repository-mutation gateway for Integrated Governed MVP Slice 3.

This reference mechanism consumes an exact Slice 2 receipt plus platform-owned
Plan-Step Effect Contract and Action Effect Manifest, applies only a precomputed
patch to an isolated local Git workspace, and retains durable replay/recovery
lineage. It has no remote, terminal, release, merge, deploy, production, or
completion authority.
"""
from __future__ import annotations

from copy import deepcopy
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import subprocess
import threading
from typing import Any, Mapping


class CrashInjected(RuntimeError):
    """Controlled crash point used only by the frozen Slice 3 harness."""


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RepositoryMutationGateway:
    """SQLite-backed fail-closed gateway for one isolated local Git mutation."""

    _locks_guard = threading.Lock()
    _locks: dict[str, threading.RLock] = {}
    _SUCCESS_SLICE2_STATES = {"EXECUTED", "RECOVERED_AND_EXECUTED", "REPLAYED", "RECOVERED_REPLAY"}

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        with self._locks_guard:
            self._lock = self._locks.setdefault(self.db_path, threading.RLock())
        with self._lock:
            self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _initialize(self) -> None:
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS repository_mutations (
                    idempotency_key TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    slice2_result_hash TEXT NOT NULL,
                    effect_contract_hash TEXT NOT NULL,
                    manifest_hash TEXT NOT NULL,
                    base_sha TEXT NOT NULL,
                    patch_digest TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_commit_sha TEXT,
                    result_json TEXT,
                    evidence_json TEXT,
                    row_hash TEXT NOT NULL
                )
                """
            )
            connection.commit()

    @staticmethod
    def _deny(state: str, reason: str) -> dict[str, Any]:
        return {
            "state": state,
            "reason": reason,
            "authorized": False,
            "terminal_authority": False,
            "release_completion_authority": False,
        }

    @staticmethod
    def _self_hash_valid(record: Mapping[str, Any], field: str) -> bool:
        try:
            supplied = record[field]
            if not isinstance(supplied, str) or not supplied:
                return False
            material = deepcopy(dict(record))
            material.pop(field, None)
            return canonical_hash(material) == supplied
        except (KeyError, TypeError, ValueError):
            return False

    @classmethod
    def _row_payload(cls, row: Mapping[str, Any]) -> dict[str, Any]:
        fields = (
            "idempotency_key",
            "binding_hash",
            "slice2_result_hash",
            "effect_contract_hash",
            "manifest_hash",
            "base_sha",
            "patch_digest",
            "status",
            "result_commit_sha",
            "result_json",
            "evidence_json",
        )
        return {field: row[field] for field in fields}

    @classmethod
    def _row_hash(cls, row: Mapping[str, Any]) -> str:
        return canonical_hash(cls._row_payload(row))

    @classmethod
    def _row_valid(cls, row: Mapping[str, Any]) -> bool:
        try:
            if row["status"] not in {"INTENT", "COMMITTED", "ACKED"}:
                return False
            for field in (
                "idempotency_key",
                "binding_hash",
                "slice2_result_hash",
                "effect_contract_hash",
                "manifest_hash",
                "base_sha",
                "patch_digest",
                "row_hash",
            ):
                if not isinstance(row[field], str) or not row[field]:
                    return False
            if row["row_hash"] != cls._row_hash(row):
                return False
            if row["status"] == "INTENT":
                return (
                    row["result_commit_sha"] is None
                    and row["result_json"] is None
                    and row["evidence_json"] is None
                )
            for field in ("result_commit_sha", "result_json", "evidence_json"):
                if not isinstance(row[field], str) or not row[field]:
                    return False
            result = json.loads(row["result_json"])
            evidence = json.loads(row["evidence_json"])
            return (
                isinstance(result, dict)
                and isinstance(evidence, dict)
                and result.get("result_commit_sha") == row["result_commit_sha"]
                and evidence.get("result_commit_sha") == row["result_commit_sha"]
                and evidence.get("slice2_result_hash") == row["slice2_result_hash"]
                and evidence.get("effect_contract_hash") == row["effect_contract_hash"]
                and evidence.get("manifest_hash") == row["manifest_hash"]
                and evidence.get("base_sha") == row["base_sha"]
                and evidence.get("patch_digest") == row["patch_digest"]
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return False

    @staticmethod
    def _load_row(connection: sqlite3.Connection, key: str) -> sqlite3.Row | None:
        return connection.execute(
            "SELECT * FROM repository_mutations WHERE idempotency_key = ?", (key,)
        ).fetchone()

    @staticmethod
    def _git(workspace: Path, *args: str) -> str:
        cp = subprocess.run(
            ["git", *args],
            cwd=str(workspace),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env={
                **os.environ,
                "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
                "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
            },
        )
        if cp.returncode != 0:
            raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "git command failed")
        return cp.stdout.strip()

    @classmethod
    def _workspace_root(cls, workspace_value: str) -> tuple[Path | None, str | None]:
        try:
            workspace = Path(workspace_value).resolve(strict=True)
            if not workspace.is_dir():
                return None, "workspace is not a directory"
            git_control = workspace / ".git"
            # This slice deliberately supports only an ordinary isolated local
            # repository. Linked worktrees/submodules with a .git indirection are
            # deferred rather than silently expanding the authority surface.
            if not git_control.is_dir():
                return None, "workspace is not an ordinary isolated Git repository"
            top = Path(cls._git(workspace, "rev-parse", "--show-toplevel")).resolve(strict=True)
            if top != workspace:
                return None, "Git top-level differs from the authorized workspace"
            return workspace, None
        except (OSError, RuntimeError, ValueError):
            return None, "workspace cannot be verified as the exact isolated Git repository"

    @staticmethod
    def _verify_slice2(receipt: Mapping[str, Any]) -> tuple[bool, str, dict[str, Any]]:
        try:
            if not isinstance(receipt, Mapping):
                return False, "Slice 2 receipt is malformed", {}
            supplied = receipt["receipt_hash"]
            result = receipt["result"]
            evidence = receipt["evidence"]
            if not isinstance(supplied, str) or not supplied or not isinstance(result, Mapping) or not isinstance(evidence, Mapping):
                return False, "Slice 2 receipt is malformed", {}
            material = {"result": deepcopy(dict(result)), "evidence": deepcopy(dict(evidence))}
            if canonical_hash(material) != supplied:
                return False, "Slice 2 receipt hash is invalid", {}
            if result.get("state") not in RepositoryMutationGateway._SUCCESS_SLICE2_STATES:
                return False, "Slice 2 result is non-authorizing", {}
            if bool(result.get("terminal_authority", False)) or bool(result.get("release_completion_authority", False)):
                return False, "Slice 2 receipt attempts terminal authority", {}
            if not isinstance(result.get("effect_id"), str) or not result.get("effect_id"):
                return False, "Slice 2 result lacks effect identity", {}
            if result.get("effect_id") != evidence.get("effect_id"):
                return False, "Slice 2 result/evidence effect identity mismatch", {}
            lineage = evidence.get("capability_lineage")
            if not isinstance(lineage, Mapping):
                return False, "Slice 2 capability lineage is missing", {}
            for field in ("project_id", "task_id"):
                if not isinstance(lineage.get(field), str) or not lineage.get(field):
                    return False, "Slice 2 capability lineage is incomplete", {}
            return True, "Slice 2 receipt verified", {
                "receipt_hash": supplied,
                "effect_id": result["effect_id"],
                "project_id": lineage["project_id"],
                "task_id": lineage["task_id"],
            }
        except (KeyError, TypeError, ValueError):
            return False, "Slice 2 receipt is malformed", {}

    @staticmethod
    def _raw_path_classification(path_value: Any) -> tuple[str | None, str | None]:
        if not isinstance(path_value, str) or not path_value:
            return "DENIED_PATCH", "patch path is missing"
        # Treat backslashes as separators too so Windows-style traversal cannot
        # be smuggled through a POSIX CI environment.
        normalized = path_value.replace("\\", "/")
        pure = PurePosixPath(normalized)
        if pure.is_absolute() or os.path.isabs(path_value):
            return "DENIED_PATH_ESCAPE", "absolute patch path is forbidden"
        if ".." in pure.parts:
            return "DENIED_PATH_ESCAPE", "parent traversal in patch path is forbidden"
        if any(part in {"", "."} for part in pure.parts):
            return "DENIED_PATH_ESCAPE", "ambiguous normalized patch path is forbidden"
        if pure.parts and pure.parts[0].lower() == ".git":
            return "DENIED_GIT_METADATA", "Git control metadata is outside the mutation surface"
        return None, None

    @staticmethod
    def _matches(path: str, patterns: Any) -> bool:
        if not isinstance(patterns, list):
            return False
        return any(isinstance(pattern, str) and fnmatch.fnmatchcase(path, pattern) for pattern in patterns)

    @classmethod
    def _validate_patch_shape(cls, patch: Mapping[str, Any]) -> tuple[bool, str, list[dict[str, Any]]]:
        if not isinstance(patch, Mapping):
            return False, "patch is not an object", []
        operations = patch.get("operations")
        if not isinstance(operations, list) or not operations:
            return False, "patch operations are missing", []
        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for op in operations:
            if not isinstance(op, Mapping):
                return False, "patch operation is malformed", []
            path = op.get("path")
            if not isinstance(path, str) or not path:
                return False, "patch operation path is malformed", []
            canonical_path = path.replace("\\", "/")
            if canonical_path in seen:
                return False, "patch contains conflicting duplicate path operations", []
            seen.add(canonical_path)
            expected = op.get("expected_content_hash")
            content = op.get("content")
            if not isinstance(expected, str) or not expected or not isinstance(content, str):
                return False, "patch operation content binding is malformed", []
            normalized.append({"path": canonical_path, "expected_content_hash": expected, "content": content})
        return True, "patch structure valid", normalized

    @classmethod
    def _safe_paths(
        cls,
        workspace: Path,
        operations: list[dict[str, Any]],
        contract: Mapping[str, Any],
    ) -> tuple[str | None, str | None]:
        workspace_real = workspace.resolve(strict=True)
        if len(operations) > int(contract.get("max_changed_files", -1)):
            return "DENIED_RESOURCE", "patch exceeds maximum changed-file count"
        for op in operations:
            path = op["path"]
            state, reason = cls._raw_path_classification(path)
            if state:
                return state, reason
            if cls._matches(path, contract.get("forbidden_paths")):
                return "DENIED_RESOURCE", "patch targets a forbidden resource"
            if not cls._matches(path, contract.get("allowed_paths")):
                return "DENIED_RESOURCE", "patch target is outside allowed resources"
            target = workspace / Path(path)
            try:
                # Resolve an existing parent chain. This detects symlink escape
                # even when the final file does not yet exist.
                parent_real = target.parent.resolve(strict=True)
                parent_real.relative_to(workspace_real)
            except (OSError, ValueError):
                return "DENIED_PATH_ESCAPE", "patch parent escapes or cannot be proven inside workspace"
            if target.exists() or target.is_symlink():
                try:
                    target_real = target.resolve(strict=True)
                    target_real.relative_to(workspace_real)
                except (OSError, ValueError):
                    return "DENIED_PATH_ESCAPE", "patch target resolves outside workspace"
        return None, None

    @staticmethod
    def _success(state: str, row: Mapping[str, Any]) -> dict[str, Any]:
        result = json.loads(row["result_json"])
        return {
            **result,
            "state": state,
            "terminal_authority": False,
            "release_completion_authority": False,
        }

    def _update_ack(self, connection: sqlite3.Connection, row: Mapping[str, Any], disposition: str) -> sqlite3.Row:
        evidence = json.loads(row["evidence_json"])
        evidence["disposition"] = disposition
        updated = dict(row)
        updated["status"] = "ACKED"
        updated["evidence_json"] = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        updated["row_hash"] = self._row_hash(updated)
        connection.execute(
            "UPDATE repository_mutations SET status = ?, evidence_json = ?, row_hash = ? WHERE idempotency_key = ?",
            (updated["status"], updated["evidence_json"], updated["row_hash"], row["idempotency_key"]),
        )
        connection.commit()
        return self._load_row(connection, row["idempotency_key"])

    @classmethod
    def _restore_files(cls, workspace: Path, snapshots: Mapping[str, tuple[bool, str]]) -> None:
        for path, (existed, content) in snapshots.items():
            target = workspace / path
            if existed:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            elif target.exists() or target.is_symlink():
                if target.is_file() or target.is_symlink():
                    target.unlink()
        try:
            cls._git(workspace, "reset", "--mixed", "HEAD")
        except RuntimeError:
            pass

    def mutate(
        self,
        *,
        workspace: str,
        slice2_receipt: Mapping[str, Any],
        effect_contract: Mapping[str, Any],
        action_manifest: Mapping[str, Any],
        patch: Mapping[str, Any],
        crash_at: str | None = None,
    ) -> dict[str, Any]:
        slice2_ok, slice2_reason, slice2 = self._verify_slice2(slice2_receipt)
        if not slice2_ok:
            return self._deny("DENIED_SLICE2", slice2_reason)

        if not isinstance(effect_contract, Mapping) or not self._self_hash_valid(effect_contract, "contract_hash"):
            return self._deny("DENIED_CONTRACT", "effect contract hash is invalid")
        contract = deepcopy(dict(effect_contract))
        if (
            contract.get("project_id") != slice2["project_id"]
            or contract.get("task_id") != slice2["task_id"]
            or contract.get("required_slice2_result_hash") != slice2["receipt_hash"]
            or contract.get("destructive_effect_allowed") is not False
            or not isinstance(contract.get("effect_contract_id"), str)
            or not contract.get("effect_contract_id")
            or not isinstance(contract.get("plan_step_id"), str)
            or not contract.get("plan_step_id")
            or not isinstance(contract.get("allowed_action_classes"), list)
            or not isinstance(contract.get("allowed_tool_ids"), list)
            or not isinstance(contract.get("allowed_paths"), list)
            or not isinstance(contract.get("forbidden_paths"), list)
            or not isinstance(contract.get("base_sha"), str)
            or not contract.get("base_sha")
            or not isinstance(contract.get("max_changed_files"), int)
            or isinstance(contract.get("max_changed_files"), bool)
            or contract.get("max_changed_files", 0) < 1
        ):
            return self._deny("DENIED_CONTRACT", "effect contract does not match authoritative Slice 2 lineage or frozen policy shape")

        if not isinstance(action_manifest, Mapping) or not self._self_hash_valid(action_manifest, "manifest_hash"):
            return self._deny("DENIED_MANIFEST", "action effect manifest hash is invalid")
        manifest = deepcopy(dict(action_manifest))

        patch_ok, patch_reason, operations = self._validate_patch_shape(patch)
        if not patch_ok:
            return self._deny("DENIED_PATCH", patch_reason)

        # Path escape and Git-control attempts are classification-significant and
        # are evaluated before generic resource subset checks.
        for op in operations:
            state, reason = self._raw_path_classification(op["path"])
            if state:
                return self._deny(state, reason or "patch path denied")

        patch_digest = canonical_hash(patch)
        changed_files = sorted(op["path"] for op in operations)
        if (
            manifest.get("effect_contract_id") != contract["effect_contract_id"]
            or manifest.get("effect_contract_hash") != contract["contract_hash"]
            or manifest.get("execution_id") != slice2["effect_id"]
            or manifest.get("slice2_result_hash") != slice2["receipt_hash"]
            or manifest.get("base_sha") != contract["base_sha"]
            or manifest.get("patch_digest") != patch_digest
            or manifest.get("changed_files") != changed_files
            or manifest.get("target_paths") != changed_files
            or manifest.get("action_class") not in contract["allowed_action_classes"]
            or manifest.get("tool_id") not in contract["allowed_tool_ids"]
            or not isinstance(manifest.get("idempotency_key"), str)
            or not manifest.get("idempotency_key")
        ):
            return self._deny("DENIED_MANIFEST", "action manifest differs from the exact contract, patch, or Slice 2 binding")

        key = manifest["idempotency_key"]
        binding_material = {
            "slice2_result_hash": slice2["receipt_hash"],
            "effect_contract_hash": contract["contract_hash"],
            "manifest_hash": manifest["manifest_hash"],
            "base_sha": manifest["base_sha"],
            "patch_digest": patch_digest,
        }
        binding_hash = canonical_hash(binding_material)

        with self._lock:
            with self._connect() as connection:
                row = self._load_row(connection, key)
                if row is not None:
                    if not self._row_valid(row):
                        return self._deny("BLOCKED_AMBIGUOUS_DURABLE_STATE", "durable repository mutation state is malformed or conflicting")
                    if row["binding_hash"] != binding_hash:
                        return self._deny("DENIED_IDEMPOTENCY_REBIND", "idempotency key is already bound to different repository mutation semantics")
                    if row["status"] in {"COMMITTED", "ACKED"}:
                        replay_state = "RECOVERED_REPLAY" if row["status"] == "COMMITTED" else "REPLAYED"
                        if row["status"] == "COMMITTED":
                            row = self._update_ack(connection, row, replay_state)
                        return self._success(replay_state, row)

                verified_workspace, workspace_reason = self._workspace_root(workspace)
                if verified_workspace is None:
                    return self._deny("DENIED_PATH_ESCAPE", workspace_reason or "workspace verification failed")

                try:
                    head = self._git(verified_workspace, "rev-parse", "HEAD")
                except RuntimeError:
                    return self._deny("DENIED_BASE", "workspace HEAD cannot be verified")
                if head != contract["base_sha"]:
                    return self._deny("DENIED_BASE", "workspace HEAD differs from the frozen base SHA")

                resource_state, resource_reason = self._safe_paths(verified_workspace, operations, contract)
                if resource_state:
                    return self._deny(resource_state, resource_reason or "patch resource denied")

                snapshots: dict[str, tuple[bool, str]] = {}
                for op in operations:
                    target = verified_workspace / op["path"]
                    existed = target.exists()
                    try:
                        current = target.read_text(encoding="utf-8") if existed else ""
                    except (OSError, UnicodeError):
                        return self._deny("DENIED_PATCH", "current file content cannot be deterministically verified")
                    if _content_hash(current) != op["expected_content_hash"]:
                        return self._deny("DENIED_PATCH", "patch expected-content binding does not match current workspace")
                    snapshots[op["path"]] = (existed, current)

                recovered_intent = row is not None and row["status"] == "INTENT"
                if row is None:
                    pending = {
                        "idempotency_key": key,
                        "binding_hash": binding_hash,
                        "slice2_result_hash": slice2["receipt_hash"],
                        "effect_contract_hash": contract["contract_hash"],
                        "manifest_hash": manifest["manifest_hash"],
                        "base_sha": contract["base_sha"],
                        "patch_digest": patch_digest,
                        "status": "INTENT",
                        "result_commit_sha": None,
                        "result_json": None,
                        "evidence_json": None,
                    }
                    pending["row_hash"] = self._row_hash(pending)
                    connection.execute(
                        """INSERT INTO repository_mutations
                        (idempotency_key, binding_hash, slice2_result_hash, effect_contract_hash,
                         manifest_hash, base_sha, patch_digest, status, result_commit_sha,
                         result_json, evidence_json, row_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        tuple(pending[field] for field in (
                            "idempotency_key", "binding_hash", "slice2_result_hash", "effect_contract_hash",
                            "manifest_hash", "base_sha", "patch_digest", "status", "result_commit_sha",
                            "result_json", "evidence_json", "row_hash"
                        )),
                    )
                    connection.commit()

                if crash_at == "BEFORE_LOCAL_COMMIT":
                    raise CrashInjected("injected before local repository commit")

                try:
                    for op in operations:
                        target = verified_workspace / op["path"]
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(op["content"], encoding="utf-8")
                    self._git(verified_workspace, "add", "--", *changed_files)
                    staged = sorted(filter(None, self._git(verified_workspace, "diff", "--cached", "--name-only", "--").splitlines()))
                    if staged != changed_files:
                        raise RuntimeError("staged changed-file set differs from frozen manifest")
                    message = f"governed-mutation:{manifest.get('action_effect_id', 'unknown')}:{manifest['manifest_hash'][:12]}"
                    self._git(
                        verified_workspace,
                        "-c", "core.hooksPath=/dev/null",
                        "-c", "commit.gpgsign=false",
                        "commit", "-q", "-m", message,
                    )
                    result_commit = self._git(verified_workspace, "rev-parse", "HEAD")
                except (OSError, RuntimeError, UnicodeError):
                    self._restore_files(verified_workspace, snapshots)
                    return self._deny("DENIED_PATCH", "patch application or local commit failed atomically")

                disposition = "RECOVERED_AND_COMMITTED" if recovered_intent else "COMMITTED"
                result = {
                    "result_commit_sha": result_commit,
                    "changed_files": changed_files,
                    "terminal_authority": False,
                    "release_completion_authority": False,
                }
                evidence = {
                    "slice2_result_hash": slice2["receipt_hash"],
                    "effect_contract_hash": contract["contract_hash"],
                    "manifest_hash": manifest["manifest_hash"],
                    "base_sha": contract["base_sha"],
                    "patch_digest": patch_digest,
                    "changed_files": changed_files,
                    "result_commit_sha": result_commit,
                    "disposition": disposition,
                    "terminal_authority": False,
                    "release_completion_authority": False,
                }
                committed = {
                    "idempotency_key": key,
                    "binding_hash": binding_hash,
                    "slice2_result_hash": slice2["receipt_hash"],
                    "effect_contract_hash": contract["contract_hash"],
                    "manifest_hash": manifest["manifest_hash"],
                    "base_sha": contract["base_sha"],
                    "patch_digest": patch_digest,
                    "status": "COMMITTED",
                    "result_commit_sha": result_commit,
                    "result_json": json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
                    "evidence_json": json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
                }
                committed["row_hash"] = self._row_hash(committed)
                connection.execute(
                    """UPDATE repository_mutations
                    SET status = ?, result_commit_sha = ?, result_json = ?, evidence_json = ?, row_hash = ?
                    WHERE idempotency_key = ?""",
                    (
                        committed["status"], committed["result_commit_sha"], committed["result_json"],
                        committed["evidence_json"], committed["row_hash"], key,
                    ),
                )
                connection.commit()

                if crash_at == "AFTER_LOCAL_COMMIT_BEFORE_RESPONSE":
                    raise CrashInjected("injected after local commit before response")

                row = self._load_row(connection, key)
                row = self._update_ack(connection, row, disposition)
                return self._success("COMMITTED", row)

    def get_evidence(self, idempotency_key: str) -> dict[str, Any]:
        with self._lock:
            with self._connect() as connection:
                row = self._load_row(connection, idempotency_key)
                if row is None or not self._row_valid(row) or row["evidence_json"] is None:
                    return {}
                return json.loads(row["evidence_json"])

    def request_terminal_action(self, action: str, context: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "state": "TERMINAL_AUTHORITY_REQUIRED",
            "authorized": False,
            "action": action,
            "context": deepcopy(dict(context)),
            "terminal_authority": False,
            "release_completion_authority": False,
            "reason": "remote push, merge, release, deploy, production, and completion actions require a separate external authority gate",
        }
