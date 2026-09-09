from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import coding_agent_adapter as caa

SHA = "a" * 40


class FakeAdapter(caa.CodingAgentAdapter):
    def __init__(self, adapter_id: str, agent_id: str, *, capabilities=None, native_result=None):
        self._descriptor = caa.AgentDescriptor(
            adapter_id=adapter_id,
            agent_id=agent_id,
            agent_family="fake-family",
            agent_version="1.0",
            capabilities=frozenset(capabilities or {"EDIT_FILES", "RUN_TESTS"}),
        )
        self.native_result = native_result or {
            "execution_id": "exec-1",
            "completion_state": "COMPLETED",
            "changed_artifacts": ["src/a.py"],
            "commands_run": ["python -m unittest"],
            "test_results": [{"name": "unit", "status": "PASS"}],
            "failure_classification": "NONE",
            "execution_events": [{"seq": 1, "kind": "STARTED"}],
        }
        self.dispatch_count = 0

    @property
    def descriptor(self):
        return self._descriptor

    def execute(self, task):
        self.dispatch_count += 1
        return dict(self.native_result)

    def normalize(self, task, native_result):
        out = dict(native_result)
        out.update({
            "task_id": task.task_id,
            "candidate_sha": task.candidate_sha,
            "adapter_id": self.descriptor.adapter_id,
            "agent_id": self.descriptor.agent_id,
            "agent_family": self.descriptor.agent_family,
            "agent_version": self.descriptor.agent_version,
        })
        return out


def task(**overrides):
    base = dict(
        task_id="task-1",
        candidate_sha=SHA,
        goal="edit bounded source",
        allowed_paths=("src/",),
        forbidden_paths=("governance-runtime/", "standards/", ".github/workflows/"),
        acceptance_criteria=("tests pass",),
        required_tests=("tests/test_a.py",),
        forbidden_changes=("tests/test_a.py",),
        stop_conditions=("REQUIREMENT_UNRESOLVED",),
        required_capabilities=frozenset({"EDIT_FILES", "RUN_TESTS"}),
        authorized_test_changes=(),
        authorized_governance_paths=(),
        allow_governance_mutation=False,
    )
    base.update(overrides)
    return caa.GovernedCodingTask(**base)


class CodingAgentAdapterTests(unittest.TestCase):
    def test_s11_01_generic_registration_and_descriptor(self):
        r = caa.AdapterRegistry()
        a = FakeAdapter("adapter-x", "agent-x")
        r.register(a)
        self.assertIs(r.get("adapter-x"), a)
        self.assertEqual("agent-x", r.get("adapter-x").descriptor.agent_id)

    def test_s11_02_two_named_adapters_same_contract(self):
        r = caa.AdapterRegistry()
        one = FakeAdapter("codex-adapter", "codex")
        two = FakeAdapter("other-adapter", "future-agent")
        r.register(one); r.register(two)
        engine = caa.CodingAgentExecutionGateway(r)
        a = engine.execute("codex-adapter", task(), execution_id="E1")
        b = engine.execute("other-adapter", task(), execution_id="E2")
        self.assertEqual(a["task_contract_hash"], b["task_contract_hash"])
        self.assertEqual("NONE", a["authority_effect"])
        self.assertEqual("NONE", b["authority_effect"])

    def test_s11_03_exact_sha_required_and_mismatch_rejected(self):
        with self.assertRaises(caa.AdapterContractError):
            task(candidate_sha="short")
        a = FakeAdapter("a", "agent")
        bad = dict(a.native_result)
        bad["candidate_sha"] = "b" * 40
        a.native_result = bad
        with self.assertRaises(caa.AdapterContractError):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(), execution_id="E3")

    def test_s11_04_missing_capability_fails_before_dispatch(self):
        a = FakeAdapter("a", "agent", capabilities={"EDIT_FILES"})
        gateway = caa.CodingAgentExecutionGateway.from_adapters([a])
        with self.assertRaises(caa.AdapterContractError):
            gateway.execute("a", task(), execution_id="E4")
        self.assertEqual(0, a.dispatch_count)

    def test_s11_05_allowed_change_accepted(self):
        out = caa.CodingAgentExecutionGateway.from_adapters([FakeAdapter("a", "agent")]).execute("a", task(), execution_id="E5")
        self.assertEqual(["src/a.py"], out["changed_artifacts"])

    def test_s11_06_out_of_scope_change_rejected(self):
        a = FakeAdapter("a", "agent", native_result={
            "execution_id":"E6","completion_state":"COMPLETED","changed_artifacts":["docs/x.md"],
            "commands_run":[],"test_results":[],"failure_classification":"NONE","execution_events":[]})
        with self.assertRaises(caa.ScopeViolation):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(), execution_id="E6")

    def test_s11_07_governance_path_rejected_by_default(self):
        a = FakeAdapter("a", "agent", native_result={
            "execution_id":"E7","completion_state":"COMPLETED","changed_artifacts":["governance-runtime/x.json"],
            "commands_run":[],"test_results":[],"failure_classification":"NONE","execution_events":[]})
        with self.assertRaises(caa.ScopeViolation):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(allowed_paths=("governance-runtime/",)), execution_id="E7")

    def test_s11_08_required_test_mutation_requires_explicit_authorization(self):
        a = FakeAdapter("a", "agent", native_result={
            "execution_id":"E8","completion_state":"COMPLETED","changed_artifacts":["tests/test_a.py"],
            "commands_run":[],"test_results":[],"failure_classification":"NONE","execution_events":[]})
        with self.assertRaises(caa.TestIntegrityViolation):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute(
                "a", task(allowed_paths=("tests/",), forbidden_changes=()), execution_id="E8")
        ok = caa.CodingAgentExecutionGateway.from_adapters([a]).execute(
            "a", task(allowed_paths=("tests/",), forbidden_changes=(), authorized_test_changes=("tests/test_a.py",)), execution_id="E8b")
        self.assertTrue(ok["material_test_change_requires_adjudication"])

    def test_s11_09_requirement_unresolved_preserved(self):
        a = FakeAdapter("a", "agent", native_result={
            "execution_id":"E9","completion_state":"REQUIREMENT_UNRESOLVED","changed_artifacts":[],
            "commands_run":[],"test_results":[],"failure_classification":"REQUIREMENT UNRESOLVED","execution_events":[]})
        out = caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(), execution_id="E9")
        self.assertEqual("REQUIREMENT_UNRESOLVED", out["completion_state"])
        self.assertEqual("REQUIREMENT UNRESOLVED", out["failure_classification"])

    def test_s11_10_raw_secret_rejected(self):
        a = FakeAdapter("a", "agent", native_result={
            "execution_id":"E10","completion_state":"FAILED","changed_artifacts":[],"commands_run":["export API_KEY=sk-secret-value"],
            "test_results":[],"failure_classification":"ENVIRONMENT-TOOLING DEFECT","execution_events":[]})
        with self.assertRaises(caa.SecretContainmentViolation):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(), execution_id="E10")

    def test_s11_11_agent_declared_terminal_authority_rejected(self):
        a = FakeAdapter("a", "agent", native_result={
            "execution_id":"E11","completion_state":"COMPLETED","changed_artifacts":[],"commands_run":[],"test_results":[],
            "failure_classification":"NONE","execution_events":[],"authority_effect":"DEPLOY","merge_authorized":True})
        with self.assertRaises(caa.AuthorityViolation):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(), execution_id="E11")

    def test_s11_12_13_idempotent_identical_and_conflicting_ingestion(self):
        store = caa.InMemoryExecutionStore()
        gateway = caa.CodingAgentExecutionGateway.from_adapters([FakeAdapter("a", "agent")], store=store)
        first = gateway.execute("a", task(), execution_id="E12")
        again = gateway.ingest_result(first)
        self.assertEqual(first["result_hash"], again["result_hash"])
        conflict = dict(first); conflict["completion_state"] = "FAILED"
        with self.assertRaises(caa.IdempotencyConflict):
            gateway.ingest_result(conflict)

    def test_s11_14_failed_history_retained_after_success(self):
        store = caa.InMemoryExecutionStore()
        fail = FakeAdapter("a", "agent", native_result={
            "execution_id":"EF","completion_state":"FAILED","changed_artifacts":[],"commands_run":[],"test_results":[],
            "failure_classification":"CODE DEFECT","execution_events":[]})
        gateway = caa.CodingAgentExecutionGateway.from_adapters([fail], store=store)
        gateway.execute("a", task(task_id="T"), execution_id="EF")
        success = FakeAdapter("b", "agent2")
        gateway.registry.register(success)
        gateway.execute("b", task(task_id="T"), execution_id="ES")
        hist = store.history_for_task("T")
        self.assertEqual(["FAILED", "COMPLETED"], [x["completion_state"] for x in hist])

    def test_s11_15_malformed_output_rejected(self):
        a = FakeAdapter("a", "agent", native_result={"execution_id":"E15","completion_state":"COMPLETED"})
        with self.assertRaises(caa.AdapterContractError):
            caa.CodingAgentExecutionGateway.from_adapters([a]).execute("a", task(), execution_id="E15")

    def test_s11_16_normal_schema_is_provider_neutral(self):
        a = caa.CodingAgentExecutionGateway.from_adapters([FakeAdapter("one", "codex")]).execute("one", task(), execution_id="E16a")
        b = caa.CodingAgentExecutionGateway.from_adapters([FakeAdapter("two", "claude-code")]).execute("two", task(), execution_id="E16b")
        self.assertEqual(set(a.keys()), set(b.keys()))
        self.assertNotIn("provider_specific", a)

    def test_s11_17_resume_from_durable_record(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "executions.jsonl"
            store = caa.JsonlExecutionStore(path)
            gateway = caa.CodingAgentExecutionGateway.from_adapters([FakeAdapter("a", "agent")], store=store)
            out = gateway.execute("a", task(), execution_id="E17")
            recovered = caa.JsonlExecutionStore(path).get("E17")
            self.assertEqual(out["result_hash"], recovered["result_hash"])

    def test_s11_18_testing_execution_never_dispatches_reviewer_api(self):
        called = []
        gateway = caa.CodingAgentExecutionGateway.from_adapters(
            [FakeAdapter("a", "agent")], reviewer_dispatch=lambda *_: called.append(True), phase="TESTING")
        out = gateway.execute("a", task(), execution_id="E18")
        self.assertEqual([], called)
        self.assertEqual("MANUAL_REVIEW_IF_REQUESTED", out["review_effect"])


if __name__ == "__main__":
    unittest.main()
