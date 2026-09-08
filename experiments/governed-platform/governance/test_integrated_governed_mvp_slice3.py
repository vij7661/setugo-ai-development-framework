from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from integrated_governed_mvp import evaluate_governed_execution
from integrated_governed_mvp_execution_gateway import ExecutionGateway
from integrated_governed_mvp_repository_gateway import (
    CrashInjected,
    RepositoryMutationGateway,
    canonical_hash,
)


class IntegratedGovernedMVPSlice3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.workspace = self.root / "workspace"
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.repo_db = str(self.root / "repo-gateway.sqlite3")
        self.slice2_db = str(self.root / "slice2.sqlite3")
        self._init_repo()

        self.route = {
            "provider": "groq",
            "model": "model-a",
            "sku": "sku-a",
            "deployment_path": "api-a",
            "qualification_ref": "q-1",
            "qualification_epoch": 7,
        }
        self.registry = {
            **self.route,
            "qualification_expires_epoch": 100,
            "eligible": True,
            "revoked": False,
        }
        self.capability = {
            "capability_id": "cap-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "subject_id": "worker-1",
            "issued_epoch": 3,
            "expires_at": "2030-01-01T00:00:00Z",
            "allowed_actions": ["WRITE"],
            "artifact_classes": ["CODE", "TEST"],
            "revoked": False,
        }
        self.request = {
            "capability_id": "cap-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "subject_id": "worker-1",
            "issued_epoch": 3,
            "action": "WRITE",
            "artifact_classes": ["CODE"],
        }
        self.model_result = {
            "evidence_eligible": True,
            "authorized_scope": ["CODE"],
            "changed_artifacts": ["CODE"],
            "review_requested": False,
        }
        self.review_gate = {"state": "CLEAR", "evidence_refs": ["ev-1"]}
        self.artifact = {
            "artifact_id": "src/app.py",
            "artifact_class": "CODE",
            "revision": self.base_sha,
        }
        self.slice2_receipt = self._make_slice2_receipt()
        self.effect_contract = self._make_effect_contract()
        self.patch = self._make_patch("value = 2\n")
        self.manifest = self._make_manifest(self.patch)

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args: str, cwd: Path | None = None) -> str:
        cp = subprocess.run(
            ["git", *args],
            cwd=str(cwd or self.workspace),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env={**os.environ, "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z"},
        )
        return cp.stdout.strip()

    def _init_repo(self) -> None:
        self.workspace.mkdir()
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.name", "Governed Test")
        self._git("config", "user.email", "governed@example.invalid")
        (self.workspace / "src").mkdir()
        (self.workspace / "tests").mkdir()
        (self.workspace / "infra").mkdir()
        (self.workspace / "src" / "app.py").write_text("value = 1\n", encoding="utf-8")
        (self.workspace / "tests" / "test_app.py").write_text("assert True\n", encoding="utf-8")
        (self.workspace / "infra" / "prod.txt").write_text("protected\n", encoding="utf-8")
        self._git("add", "src/app.py", "tests/test_app.py", "infra/prod.txt")
        self._git("commit", "-q", "-m", "base")
        self.base_sha = self._git("rev-parse", "HEAD")

    @staticmethod
    def _content_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _seal(record: dict, field: str) -> dict:
        record = deepcopy(record)
        record.pop(field, None)
        record[field] = canonical_hash(record)
        return record

    def _make_upstream(self) -> dict:
        decision = evaluate_governed_execution(
            route=deepcopy(self.route),
            registry_entry=deepcopy(self.registry),
            normalized_model_result=deepcopy(self.model_result),
            capability=deepcopy(self.capability),
            execution_request=deepcopy(self.request),
            review_gate=deepcopy(self.review_gate),
            now_epoch=10,
            now_iso="2026-09-07T00:00:00Z",
        )
        return {
            "decision": decision,
            "decision_hash": canonical_hash(decision),
            "route": deepcopy(self.route),
            "registry_entry": deepcopy(self.registry),
            "normalized_model_result": deepcopy(self.model_result),
            "capability": deepcopy(self.capability),
            "execution_request": deepcopy(self.request),
            "review_gate": deepcopy(self.review_gate),
            "decision_now_epoch": 10,
            "decision_now_iso": "2026-09-07T00:00:00Z",
            "artifact_binding": deepcopy(self.artifact),
        }

    def _make_slice2_receipt(self) -> dict:
        def worker(effect_request):
            return {
                "status": "SUCCESS",
                "worker_effect": "LOCAL_DETERMINISTIC_WRITE",
                "effect_request_hash": canonical_hash(effect_request),
                "claimed_authority": "NONE",
            }

        gateway = ExecutionGateway(self.slice2_db, worker)
        result = gateway.execute(
            upstream=self._make_upstream(),
            current_registry_entry=deepcopy(self.registry),
            current_capability=deepcopy(self.capability),
            execution_request=deepcopy(self.request),
            current_artifact_binding=deepcopy(self.artifact),
            idempotency_key="slice2-for-slice3",
            now_epoch=11,
            now_iso="2026-09-07T00:01:00Z",
        )
        evidence = gateway.get_evidence("slice2-for-slice3")
        receipt = {"result": result, "evidence": evidence}
        receipt["receipt_hash"] = canonical_hash(receipt)
        return receipt

    def _make_effect_contract(self, **overrides) -> dict:
        record = {
            "effect_contract_id": "ec-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "plan_step_id": "step-1",
            "allowed_action_classes": ["WRITE_WORKSPACE"],
            "allowed_tool_ids": ["repo.apply_patch_local"],
            "allowed_paths": ["src/**", "tests/**"],
            "forbidden_paths": ["infra/**", ".git/**"],
            "base_sha": self.base_sha,
            "max_changed_files": 2,
            "destructive_effect_allowed": False,
            "required_slice2_result_hash": self.slice2_receipt["receipt_hash"],
        }
        record.update(overrides)
        return self._seal(record, "contract_hash")

    def _make_patch(self, content: str, path: str = "src/app.py", *, expected: str = "value = 1\n") -> dict:
        return {
            "operations": [
                {
                    "path": path,
                    "expected_content_hash": self._content_hash(expected),
                    "content": content,
                }
            ]
        }

    def _make_manifest(self, patch: dict, **overrides) -> dict:
        paths = sorted(op["path"] for op in patch["operations"])
        record = {
            "action_effect_id": "ae-1",
            "effect_contract_id": self.effect_contract["effect_contract_id"],
            "effect_contract_hash": self.effect_contract["contract_hash"],
            "execution_id": self.slice2_receipt["result"]["effect_id"],
            "tool_id": "repo.apply_patch_local",
            "action_class": "WRITE_WORKSPACE",
            "idempotency_key": "repo-idem-1",
            "base_sha": self.base_sha,
            "patch_digest": canonical_hash(patch),
            "changed_files": paths,
            "target_paths": paths,
            "slice2_result_hash": self.slice2_receipt["receipt_hash"],
        }
        record.update(overrides)
        return self._seal(record, "manifest_hash")

    def _mutate(self, gateway: RepositoryMutationGateway | None = None, **overrides):
        gateway = gateway or RepositoryMutationGateway(self.repo_db)
        values = {
            "workspace": str(self.workspace),
            "slice2_receipt": deepcopy(self.slice2_receipt),
            "effect_contract": deepcopy(self.effect_contract),
            "action_manifest": deepcopy(self.manifest),
            "patch": deepcopy(self.patch),
        }
        values.update(overrides)
        return gateway.mutate(**values)

    def _head(self) -> str:
        return self._git("rev-parse", "HEAD")

    def _commit_count(self) -> int:
        return int(self._git("rev-list", "--count", "HEAD"))

    def test_s3_01_clean_exact_manifest_commits_one_local_mutation(self):
        before = self._commit_count()
        result = self._mutate()
        self.assertEqual(result["state"], "COMMITTED")
        self.assertEqual(self._commit_count(), before + 1)
        self.assertEqual((self.workspace / "src" / "app.py").read_text(encoding="utf-8"), "value = 2\n")
        self.assertEqual(result["result_commit_sha"], self._head())
        self.assertFalse(result["terminal_authority"])

    def test_s3_02_invalid_slice2_lineage_denies_before_mutation(self):
        before = self._head()
        variants = []
        variants.append({})
        forged = deepcopy(self.slice2_receipt); forged["receipt_hash"] = "forged"; variants.append(forged)
        denied = deepcopy(self.slice2_receipt); denied["result"]["state"] = "DENIED_CURRENT_STATE"; denied["receipt_hash"] = canonical_hash({"result": denied["result"], "evidence": denied["evidence"]}); variants.append(denied)
        mismatched = deepcopy(self.slice2_receipt); mismatched["result"]["effect_id"] = "other-effect"; mismatched["receipt_hash"] = canonical_hash({"result": mismatched["result"], "evidence": mismatched["evidence"]}); variants.append(mismatched)
        for index, receipt in enumerate(variants):
            result = self._mutate(slice2_receipt=receipt, action_manifest=self._make_manifest(self.patch, idempotency_key=f"s3-02-{index}"))
            self.assertEqual(result["state"], "DENIED_SLICE2")
            self.assertEqual(self._head(), before)

    def test_s3_03_contract_or_manifest_to_contract_substitution_denies(self):
        before = self._head()
        contract = self._make_effect_contract(project_id="p-2")
        self.assertEqual(self._mutate(effect_contract=contract)["state"], "DENIED_CONTRACT")
        manifest = self._make_manifest(self.patch, effect_contract_id="ec-other")
        self.assertEqual(self._mutate(action_manifest=manifest)["state"], "DENIED_CONTRACT")
        manifest = self._make_manifest(self.patch, effect_contract_hash="different")
        self.assertEqual(self._mutate(action_manifest=manifest)["state"], "DENIED_CONTRACT")
        self.assertEqual(self._head(), before)

    def test_s3_04_stale_or_unrelated_base_denies_before_mutation(self):
        before = self._head()
        (self.workspace / "src" / "other.py").write_text("x = 1\n", encoding="utf-8")
        self._git("add", "src/other.py")
        self._git("commit", "-q", "-m", "advance")
        advanced = self._head()
        result = self._mutate()
        self.assertEqual(result["state"], "DENIED_BASE")
        self.assertEqual(self._head(), advanced)
        self.assertNotEqual(advanced, before)

    def test_s3_05_manifest_or_patch_binding_substitution_denies(self):
        before = self._head()
        changed_patch = self._make_patch("value = 99\n")
        self.assertEqual(self._mutate(patch=changed_patch)["state"], "DENIED_MANIFEST")
        for field, value in (
            ("tool_id", "repo.other"),
            ("execution_id", "other-exec"),
            ("changed_files", ["tests/test_app.py"]),
            ("target_paths", ["tests/test_app.py"]),
        ):
            manifest = self._make_manifest(self.patch, **{field: value})
            self.assertEqual(self._mutate(action_manifest=manifest)["state"], "DENIED_MANIFEST")
        self.assertEqual(self._head(), before)

    def test_s3_06_allowed_forbidden_and_changed_file_bounds_enforced(self):
        before = self._head()
        forbidden_patch = self._make_patch("changed\n", "infra/prod.txt", expected="protected\n")
        forbidden_manifest = self._make_manifest(forbidden_patch)
        self.assertEqual(self._mutate(patch=forbidden_patch, action_manifest=forbidden_manifest)["state"], "DENIED_RESOURCE")
        outside_patch = self._make_patch("x\n", "docs/new.txt", expected="")
        outside_manifest = self._make_manifest(outside_patch)
        self.assertEqual(self._mutate(patch=outside_patch, action_manifest=outside_manifest)["state"], "DENIED_RESOURCE")
        many_patch = {
            "operations": [
                {"path": "src/app.py", "expected_content_hash": self._content_hash("value = 1\n"), "content": "value = 2\n"},
                {"path": "tests/test_app.py", "expected_content_hash": self._content_hash("assert True\n"), "content": "assert 1 == 1\n"},
                {"path": "src/new.py", "expected_content_hash": self._content_hash(""), "content": "new = True\n"},
            ]
        }
        many_manifest = self._make_manifest(many_patch)
        self.assertEqual(self._mutate(patch=many_patch, action_manifest=many_manifest)["state"], "DENIED_RESOURCE")
        self.assertEqual(self._head(), before)

    def test_s3_07_path_traversal_absolute_and_symlink_escape_denied(self):
        before = self._head()
        escaped = self.root / "escaped.txt"
        traversal = self._make_patch("escape\n", "../escaped.txt", expected="")
        self.assertEqual(self._mutate(patch=traversal, action_manifest=self._make_manifest(traversal))["state"], "DENIED_PATH_ESCAPE")
        absolute = self._make_patch("escape\n", str(escaped), expected="")
        self.assertEqual(self._mutate(patch=absolute, action_manifest=self._make_manifest(absolute))["state"], "DENIED_PATH_ESCAPE")
        link = self.workspace / "src" / "outside-link"
        os.symlink(self.outside, link)
        symlink_patch = self._make_patch("escape\n", "src/outside-link/escaped.txt", expected="")
        self.assertEqual(self._mutate(patch=symlink_patch, action_manifest=self._make_manifest(symlink_patch))["state"], "DENIED_PATH_ESCAPE")
        self.assertFalse(escaped.exists())
        self.assertFalse((self.outside / "escaped.txt").exists())
        self.assertEqual(self._head(), before)

    def test_s3_08_git_metadata_and_remote_control_patch_surface_denied(self):
        before = self._head()
        config_before = (self.workspace / ".git" / "config").read_text(encoding="utf-8")
        for index, path in enumerate((".git/config", ".git/hooks/post-commit", ".git/refs/heads/evil")):
            patch = self._make_patch("malicious\n", path, expected="")
            result = self._mutate(patch=patch, action_manifest=self._make_manifest(patch, idempotency_key=f"s3-08-{index}"))
            self.assertEqual(result["state"], "DENIED_GIT_METADATA")
        self.assertEqual((self.workspace / ".git" / "config").read_text(encoding="utf-8"), config_before)
        self.assertEqual(self._head(), before)

    def test_s3_09_conflicting_or_failed_patch_is_atomic_before_commit(self):
        before = self._head()
        original = (self.workspace / "src" / "app.py").read_text(encoding="utf-8")
        conflict = {
            "operations": [
                {"path": "src/app.py", "expected_content_hash": self._content_hash(original), "content": "value = 2\n"},
                {"path": "src/app.py", "expected_content_hash": self._content_hash(original), "content": "value = 3\n"},
            ]
        }
        self.assertEqual(self._mutate(patch=conflict, action_manifest=self._make_manifest(conflict))["state"], "DENIED_PATCH")
        failed = self._make_patch("value = 2\n", expected="wrong old text\n")
        self.assertEqual(self._mutate(patch=failed, action_manifest=self._make_manifest(failed, idempotency_key="s3-09-f"))["state"], "DENIED_PATCH")
        self.assertEqual((self.workspace / "src" / "app.py").read_text(encoding="utf-8"), original)
        self.assertEqual(self._head(), before)

    def test_s3_10_exact_replay_returns_same_commit_without_duplicate(self):
        gateway = RepositoryMutationGateway(self.repo_db)
        first = self._mutate(gateway)
        count = self._commit_count()
        replay = self._mutate(gateway)
        self.assertEqual(replay["state"], "REPLAYED")
        self.assertEqual(replay["result_commit_sha"], first["result_commit_sha"])
        self.assertEqual(self._commit_count(), count)

    def test_s3_11_idempotency_semantic_rebind_denied(self):
        gateway = RepositoryMutationGateway(self.repo_db)
        first = self._mutate(gateway)
        changed = self._make_patch("value = 3\n", expected="value = 2\n")
        changed_manifest = self._make_manifest(changed, base_sha=first["result_commit_sha"])
        result = self._mutate(gateway, patch=changed, action_manifest=changed_manifest)
        self.assertEqual(result["state"], "DENIED_IDEMPOTENCY_REBIND")
        self.assertEqual(self._head(), first["result_commit_sha"])

    def test_s3_12_crash_before_commit_has_no_mutation_then_retry_once(self):
        gateway = RepositoryMutationGateway(self.repo_db)
        before = self._head()
        with self.assertRaises(CrashInjected):
            self._mutate(gateway, crash_at="BEFORE_LOCAL_COMMIT")
        self.assertEqual(self._head(), before)
        result = self._mutate(gateway)
        self.assertEqual(result["state"], "COMMITTED")
        self.assertEqual(self._commit_count(), 2)

    def test_s3_13_postcommit_crash_recovers_without_duplicate_commit(self):
        gateway = RepositoryMutationGateway(self.repo_db)
        with self.assertRaises(CrashInjected):
            self._mutate(gateway, crash_at="AFTER_LOCAL_COMMIT_BEFORE_RESPONSE")
        committed = self._head()
        count = self._commit_count()
        replay = self._mutate(gateway)
        self.assertEqual(replay["state"], "RECOVERED_REPLAY")
        self.assertEqual(replay["result_commit_sha"], committed)
        self.assertEqual(self._commit_count(), count)

    def test_s3_14_concurrent_identical_requests_converge_one_commit(self):
        gateway_a = RepositoryMutationGateway(self.repo_db)
        gateway_b = RepositoryMutationGateway(self.repo_db)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda g: self._mutate(g), (gateway_a, gateway_b)))
        commits = {result["result_commit_sha"] for result in results}
        self.assertEqual(len(commits), 1)
        self.assertTrue({result["state"] for result in results}.issubset({"COMMITTED", "REPLAYED", "RECOVERED_REPLAY"}))
        self.assertEqual(self._commit_count(), 2)

    def test_s3_15_evidence_lineage_exact_and_terminal_claim_non_authorizing(self):
        gateway = RepositoryMutationGateway(self.repo_db)
        result = self._mutate(gateway)
        evidence = gateway.get_evidence(self.manifest["idempotency_key"])
        self.assertEqual(evidence["slice2_result_hash"], self.slice2_receipt["receipt_hash"])
        self.assertEqual(evidence["effect_contract_hash"], self.effect_contract["contract_hash"])
        self.assertEqual(evidence["manifest_hash"], self.manifest["manifest_hash"])
        self.assertEqual(evidence["base_sha"], self.base_sha)
        self.assertEqual(evidence["patch_digest"], canonical_hash(self.patch))
        self.assertEqual(evidence["changed_files"], ["src/app.py"])
        self.assertEqual(evidence["result_commit_sha"], result["result_commit_sha"])
        terminal = gateway.request_terminal_action("PUSH", {"claimed_by": "worker", "result_commit_sha": result["result_commit_sha"]})
        self.assertEqual(terminal["state"], "TERMINAL_AUTHORITY_REQUIRED")
        self.assertFalse(terminal["authorized"])
        self.assertFalse(terminal["terminal_authority"])

    def test_s3_16_no_remote_push_and_fresh_second_mutation_remains_live(self):
        remote = self.root / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
        self._git("remote", "add", "origin", str(remote))
        first = self._mutate()
        remote_heads_before = subprocess.run(
            ["git", "--git-dir", str(remote), "for-each-ref", "--format=%(refname):%(objectname)", "refs/heads"],
            text=True, stdout=subprocess.PIPE, check=True,
        ).stdout
        self.assertEqual(remote_heads_before, "")

        second_contract = self._make_effect_contract(
            effect_contract_id="ec-2",
            plan_step_id="step-2",
            base_sha=first["result_commit_sha"],
        )
        second_patch = self._make_patch("value = 3\n", expected="value = 2\n")
        original_contract = self.effect_contract
        self.effect_contract = second_contract
        try:
            second_manifest = self._make_manifest(
                second_patch,
                action_effect_id="ae-2",
                idempotency_key="repo-idem-2",
                base_sha=first["result_commit_sha"],
            )
        finally:
            self.effect_contract = original_contract
        second = self._mutate(
            effect_contract=second_contract,
            action_manifest=second_manifest,
            patch=second_patch,
        )
        self.assertEqual(second["state"], "COMMITTED")
        self.assertEqual(self._commit_count(), 3)
        remote_heads_after = subprocess.run(
            ["git", "--git-dir", str(remote), "for-each-ref", "--format=%(refname):%(objectname)", "refs/heads"],
            text=True, stdout=subprocess.PIPE, check=True,
        ).stdout
        self.assertEqual(remote_heads_after, "")


if __name__ == "__main__":
    unittest.main()
