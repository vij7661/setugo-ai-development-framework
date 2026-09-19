#!/usr/bin/env python3
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v24_v6_rq1_crash_predicates import evaluate_crash_case, interpret_first_attempt
from v24_v6_rq1_remediation2_harness import current_live_first_attempt


def obs(records, consumed):
    return {"records": {"entries": [{"name": n} for n in records]}, "consumed": {"entries": [{"name": n} for n in consumed]}}


def base(case):
    target_id = "a" * 64
    target = target_id + ".record"
    src = "/run/v24-v6-authority/private/records/" + target
    dst = "/run/v24-v6-authority/private/consumed/" + target
    if case == "RQ-13":
        trace = {"pid": 7, "boundary": "before-validation", "event": "syscall_entry", "syscall": 257, "paths": [src], "error": None}
        recovery = obs([target], []); recovery_delta = ({"added": [], "removed": []}, {"added": [], "removed": []})
        retry = {"parsed": {"trusted_record_id": target_id, "service_authoritative": True, "decision": "DENY", "record_state": "CONSUMED"}}
        retry_delta = ({"added": [], "removed": [target]}, {"added": [target], "removed": []})
    elif case == "RQ-14":
        trace = {"pid": 7, "boundary": "after-validation-before-rename", "event": "syscall_entry", "syscall": 82, "paths": [src, dst], "error": None}
        recovery = obs([target], []); recovery_delta = ({"added": [], "removed": []}, {"added": [], "removed": []})
        retry = {"parsed": {"trusted_record_id": target_id, "service_authoritative": True, "decision": "DENY", "record_state": "CONSUMED"}}
        retry_delta = ({"added": [], "removed": [target]}, {"added": [target], "removed": []})
    else:
        trace = {"pid": 7, "boundary": "after-rename", "event": "syscall_exit", "syscall": 82, "paths": [src, dst], "return_value": 0, "error": None}
        recovery = obs([], [target]); recovery_delta = ({"added": [], "removed": [target]}, {"added": [target], "removed": []})
        retry = {"parsed": {"trusted_record_id": target_id, "service_authoritative": False, "reason": "AUTHORITY_RECORD_UNAVAILABLE_OR_REPLAYED"}}
        retry_delta = ({"added": [], "removed": []}, {"added": [], "removed": []})
    return {
        "target_id": target_id, "target_name": target, "service_pid": 7, "boundary": trace["boundary"],
        "tracer_ready": {"pid": 7, "boundary": trace["boundary"], "target_name": target, "attached": True, "armed": True, "timestamp": 1.0}, "control_launch_timestamp": 2.0,
        "boundary_evidence": trace, "baseline": obs([], []), "prepared": obs([target], []), "recovery": recovery,
        "first_consume": {"rc": 1, "stderr": "RuntimeError: trusted service closed before control response", "stdout": ""}, "records_delta_prepared": {"added": [target], "removed": []}, "consumed_delta_prepared": {"added": [], "removed": []},
        "records_delta_recovery": recovery_delta[0], "consumed_delta_recovery": recovery_delta[1], "retry": retry, "records_delta_retry": retry_delta[0], "consumed_delta_retry": retry_delta[1],
        "replay": {"parsed": {"trusted_record_id": "-", "service_authoritative": False, "reason": "AUTHORITY_RECORD_UNAVAILABLE_OR_REPLAYED"}}, "records_delta_post_replay": {"added": [], "removed": []}, "consumed_delta_post_replay": {"added": [], "removed": []},
        "restart_returncode": 0, "service_active": True, "state_stable": True,
    }


class CrashPredicateBehaviourTests(unittest.TestCase):
    def assert_passes(self, case):
        ok, reasons = evaluate_crash_case(case, base(case)); self.assertTrue(ok, reasons)

    def assert_fails(self, case, mutate):
        evidence = base(case); mutate(evidence); ok, _ = evaluate_crash_case(case, evidence); self.assertFalse(ok)

    def test_valid_predicates_pass(self):
        for case in ("RQ-13", "RQ-14", "RQ-15"):
            with self.subTest(case=case): self.assert_passes(case)

    def test_launch_before_ready_and_ready_bypass_fail(self):
        self.assert_fails("RQ-13", lambda e: e.update(control_launch_timestamp=0.5))
        self.assert_fails("RQ-13", lambda e: e["tracer_ready"].update(armed=False))
        self.assert_fails("RQ-13", lambda e: e["tracer_ready"].update(timestamp=float("nan")))

    def test_exact_target_boundary_pid_syscall_and_error_are_load_bearing(self):
        self.assert_fails("RQ-13", lambda e: e["boundary_evidence"].update(paths=["/run/v24-v6-authority/private/records/other.record"]))
        self.assert_fails("RQ-14", lambda e: e["boundary_evidence"].update(paths=[e["boundary_evidence"]["paths"][0], "/run/v24-v6-authority/private/consumed/other.record"]))
        for field, value in (("pid", 8), ("syscall", 1), ("boundary", "wrong"), ("error", "trace failed")):
            self.assert_fails("RQ-13", lambda e, f=field, v=value: e["boundary_evidence"].update({f: v}))

    def test_rq15_nonzero_rename_fails(self):
        self.assert_fails("RQ-15", lambda e: e["boundary_evidence"].update(return_value=1))

    def test_recovery_retry_and_replay_deltas_are_load_bearing(self):
        self.assert_fails("RQ-13", lambda e: e.update(records_delta_prepared={"added": [e["target_name"], "other.record"], "removed": []}))
        self.assert_fails("RQ-13", lambda e: e.update(records_delta_retry={"added": [], "removed": []}))
        self.assert_fails("RQ-14", lambda e: e.update(records_delta_retry={"added": [], "removed": []}))
        self.assert_fails("RQ-15", lambda e: e.update(consumed_delta_recovery={"added": [], "removed": []}))
        self.assert_fails("RQ-15", lambda e: e.update(records_delta_post_replay={"added": ["other.record"], "removed": []}))

    def test_rq15_retry_empty_malformed_authoritative_or_mutating_fails(self):
        for value in ({}, {"parsed": {}}, {"parsed": {"trusted_record_id": "a" * 64, "service_authoritative": True}}):
            self.assert_fails("RQ-15", lambda e, v=value: e.update(retry=v))
        self.assert_fails("RQ-15", lambda e: e.update(replay={"parsed": "not-json"}))
        self.assert_fails("RQ-15", lambda e: e.update(consumed_delta_post_replay={"added": ["other.record"], "removed": []}))

    def test_first_interrupted_attempt_authority_fails(self):
        for case in ("RQ-14", "RQ-15"):
            self.assert_fails(case, lambda e: e.update(first_consume={"rc": -9, "parsed": {"service_authoritative": True}}))

    def test_observer_error_and_cleanup_fail_closed(self):
        self.assert_fails("RQ-13", lambda e: e.update(recovery={"records": {"entries": [], "error": "PermissionError"}, "consumed": {"entries": []}}))
        self.assert_fails("RQ-13", lambda e: e.update(state_stable=False))
        self.assert_fails("RQ-13", lambda e: e.update(restart_returncode=1))

    def test_first_attempt_requires_raw_close_diagnostic(self):
        target = "a" * 64
        good = {"rc": 1, "stdout": "", "stderr": "RuntimeError: trusted service closed before control response"}
        self.assertEqual(interpret_first_attempt(good, target), (True, []))
        for bad in (
            {"rc": 1, "stdout": "", "stderr": ""},
            {"rc": 1, "stdout": "", "stderr": "unrelated"},
            {"rc": 1, "stdout": "not-json", "stderr": "trusted service closed before control response"},
            {"rc": 1, "stdout": '{"service_authoritative": true}', "stderr": ""},
            {"rc": 1, "stdout": '{"service_authoritative": true, "trusted_record_id": "%s"}' % target, "stderr": ""},
            {"rc": 1, "stdout": '{"service_authoritative": false, "trusted_record_id": "wrong"}', "stderr": ""},
            {"rc": 0, "stdout": "", "stderr": "trusted service closed before control response"},
            {"rc": 1, "stdout": "", "stderr": "trusted service closed before control response", "parsed": {}},
            {"rc": 1, "stdout": "", "stderr": "trusted service closed before control response", "parsed": {"service_authoritative": False}},
            {"rc": 1, "stdout": None, "stderr": "trusted service closed before control response"},
            {"rc": 1, "stdout": "", "stderr": None},
        ):
            ok, _ = interpret_first_attempt(bad, target)
            self.assertFalse(ok, bad)

    def test_live_builder_uses_raw_shape_and_shared_interpreter(self):
        class Control:
            returncode = 1
            stdout = ""
            stderr = "RuntimeError: trusted service closed before control response"
        control = Control()
        evidence = current_live_first_attempt(control.returncode, control.stdout, control.stderr)
        self.assertIsNone(evidence["parsed"])
        self.assertEqual(interpret_first_attempt(evidence, "a" * 64), (True, []))
        canonical = base("RQ-13")
        canonical["first_consume"] = evidence
        self.assertEqual(evaluate_crash_case("RQ-13", canonical), (True, []))
        Control.stdout = '{"service_authoritative": true}'
        bad_control = Control()
        bad = current_live_first_attempt(bad_control.returncode, bad_control.stdout, bad_control.stderr)
        self.assertFalse(interpret_first_attempt(bad, "a" * 64)[0])
        canonical["first_consume"] = bad
        self.assertFalse(evaluate_crash_case("RQ-13", canonical)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
