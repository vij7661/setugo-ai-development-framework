#!/usr/bin/env python3
"""Pure, fail-closed predicates for the RQ-13/RQ-14/RQ-15 lifecycle.

This module has no service, filesystem, ptrace, or subprocess access.  The
live harness and offline replay both use these predicates so review cannot
approve evidence through a weaker parallel implementation.
"""
from __future__ import annotations

import json
import math
from typing import Any

SRC = "/run/v24-v6-authority/private/records/{}"
DST = "/run/v24-v6-authority/private/consumed/{}"
REPLAY_REASON = "AUTHORITY_RECORD_UNAVAILABLE_OR_REPLAYED"


def _delta(value: Any, added: list[str], removed: list[str]) -> bool:
    return value == {"added": sorted(added), "removed": sorted(removed)}


def _names(obs: Any, label: str) -> set[str] | None:
    if not isinstance(obs, dict):
        return None
    obj = obs.get(label)
    if not isinstance(obj, dict) or obj.get("error") is not None:
        return None
    entries = obj.get("entries")
    if not isinstance(entries, list):
        return None
    result: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            return None
        result.add(entry["name"])
    return result


def _life(obs: Any, target: str) -> dict[str, Any] | None:
    records, consumed = _names(obs, "records"), _names(obs, "consumed")
    if records is None or consumed is None:
        return None
    return {"records": target in records, "consumed": target in consumed}


def _trace(case: str, trace: Any, pid: int, target: str) -> tuple[bool, str]:
    if not isinstance(trace, dict):
        return False, "trace_not_dict"
    if trace.get("error") not in (None, ""):
        return False, "trace_error_present"
    if trace.get("pid") != pid:
        return False, "trace_pid_mismatch"
    expected = {
        "RQ-13": ("before-validation", 257, "syscall_entry", [SRC.format(target)]),
        "RQ-14": ("after-validation-before-rename", 82, "syscall_entry", [SRC.format(target), DST.format(target)]),
        "RQ-15": ("after-rename", 82, "syscall_exit", [SRC.format(target), DST.format(target)]),
    }[case]
    if trace.get("boundary") != expected[0]:
        return False, "trace_boundary_mismatch"
    if trace.get("syscall") != expected[1]:
        return False, "trace_syscall_mismatch"
    if trace.get("event") != expected[2]:
        return False, "trace_event_mismatch"
    paths = trace.get("paths")
    if paths != expected[3]:
        return False, "trace_paths_mismatch"
    if case == "RQ-15" and trace.get("return_value") != 0:
        return False, "rename_return_not_zero"
    return True, "ok"


def _json_response(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def interpret_first_attempt(first: Any, target_id: str) -> tuple[bool, list[str]]:
    """Interpret the interrupted control attempt from raw process evidence.

    A return code alone is never evidence of non-authority.  Raw stdout takes
    precedence over any convenience ``parsed`` field, and an empty response is
    accepted only with the exact observed transport-close diagnostic.
    """
    reasons: list[str] = []
    if not isinstance(first, dict) or not isinstance(first.get("rc"), int) or first["rc"] == 0:
        return False, ["first_attempt_returncode_invalid"]
    stdout = first.get("stdout", "")
    if not isinstance(stdout, str):
        return False, ["first_attempt_stdout_invalid"]
    convenience_present = "parsed" in first and first.get("parsed") is not None
    if stdout.strip():
        try:
            parsed = json.loads(stdout)
        except (TypeError, ValueError):
            return False, ["first_attempt_stdout_malformed"]
        if not isinstance(parsed, dict):
            return False, ["first_attempt_response_not_object"]
        if parsed.get("service_authoritative") is not False:
            return False, ["first_attempt_authority_not_false"]
        if parsed.get("trusted_record_id") not in (None, target_id):
            return False, ["first_attempt_target_mismatch"]
        return True, reasons
    if convenience_present:
        return False, ["first_attempt_convenience_parsed_without_stdout"]
    if "trusted service closed before control response" not in str(first.get("stderr", "")):
        return False, ["first_attempt_close_diagnostic_missing"]
    return True, reasons


def _first_interrupted(first: Any, target_id: str) -> bool:
    ok, _ = interpret_first_attempt(first, target_id)
    return ok


def _allow_response(value: Any, target_id: str) -> bool:
    obj = _json_response(value)
    return bool(obj and obj.get("service_authoritative") is True
                and obj.get("trusted_record_id") == target_id
                and obj.get("record_state") == "CONSUMED")


def _replay_response(value: Any, target_id: str) -> bool:
    obj = _json_response(value)
    return bool(obj and obj.get("service_authoritative") is False
                and obj.get("reason") == REPLAY_REASON
                and obj.get("trusted_record_id") in {target_id, "-"})


def evaluate_crash_case(case: str, evidence: dict[str, Any]) -> tuple[bool, list[str]]:
    """Evaluate one complete evidence structure; every missing clause fails."""
    reasons: list[str] = []
    target_id, target = evidence.get("target_id"), evidence.get("target_name")
    pid = evidence.get("service_pid")
    if not isinstance(target_id, str) or not isinstance(target, str) or target != target_id + ".record":
        reasons.append("target_identity_invalid")
    if not isinstance(pid, int):
        reasons.append("service_pid_invalid")
    ready = evidence.get("tracer_ready")
    if not isinstance(ready, dict) or ready.get("pid") != pid or ready.get("boundary") != evidence.get("boundary") or ready.get("target_name") != target or ready.get("attached") is not True or ready.get("armed") is not True:
        reasons.append("tracer_ready_invalid")
    ready_ts = ready.get("timestamp") if isinstance(ready, dict) else None
    launch_ts = evidence.get("control_launch_timestamp")
    if not isinstance(ready_ts, (int, float)) or isinstance(ready_ts, bool) or not math.isfinite(float(ready_ts)):
        reasons.append("tracer_ready_timestamp_invalid")
    if not isinstance(launch_ts, (int, float)) or isinstance(launch_ts, bool) or not math.isfinite(float(launch_ts)) or (isinstance(ready_ts, (int, float)) and not isinstance(ready_ts, bool) and ready_ts >= launch_ts):
        reasons.append("control_launched_before_tracer_ready")
    trace_ok, trace_reason = _trace(case, evidence.get("boundary_evidence"), pid, target) if isinstance(pid, int) and isinstance(target, str) else (False, "trace_inputs_invalid")
    if not trace_ok:
        reasons.append(trace_reason)
    baseline, prepared = evidence.get("baseline"), evidence.get("prepared")
    if _life(baseline, target) is None or _life(prepared, target) is None:
        reasons.append("baseline_or_prepared_observation_invalid")
    if not _delta(evidence.get("records_delta_prepared"), [target], []) or not _delta(evidence.get("consumed_delta_prepared"), [], []):
        reasons.append("prepared_delta_invalid")
    if not _first_interrupted(evidence.get("first_consume"), target_id):
        reasons.append("first_consume_not_interrupted_without_authority")
    recovery = evidence.get("recovery")
    recovery_life = _life(recovery, target)
    if recovery_life is None:
        reasons.append("recovery_observation_invalid")
    retry, replay = evidence.get("retry"), evidence.get("replay")
    retry_obj = retry.get("parsed") if isinstance(retry, dict) else None
    replay_obj = replay.get("parsed") if isinstance(replay, dict) else None
    if case in {"RQ-13", "RQ-14"}:
        if recovery_life != {"records": True, "consumed": False}:
            reasons.append("recovery_target_not_unconsumed")
        if not _delta(evidence.get("records_delta_recovery"), [], []) or not _delta(evidence.get("consumed_delta_recovery"), [], []):
            reasons.append("recovery_delta_invalid")
        if not _allow_response(retry_obj, target_id):
            reasons.append("retry_allow_response_invalid")
        if not _delta(evidence.get("records_delta_retry"), [], [target]) or not _delta(evidence.get("consumed_delta_retry"), [target], []):
            reasons.append("retry_delta_invalid")
    else:
        if recovery_life != {"records": False, "consumed": True}:
            reasons.append("post_rename_recovery_state_invalid")
        if not _delta(evidence.get("records_delta_recovery"), [], [target]) or not _delta(evidence.get("consumed_delta_recovery"), [target], []):
            reasons.append("post_rename_recovery_delta_invalid")
        if not _replay_response(retry_obj, target_id):
            reasons.append("rq15_retry_replay_response_invalid")
        if not _delta(evidence.get("records_delta_retry"), [], []) or not _delta(evidence.get("consumed_delta_retry"), [], []):
            reasons.append("rq15_retry_delta_invalid")
    if not _replay_response(replay_obj, target_id):
        reasons.append("replay_response_invalid")
    if not _delta(evidence.get("records_delta_post_replay"), [], []) or not _delta(evidence.get("consumed_delta_post_replay"), [], []):
        reasons.append("post_replay_delta_invalid")
    restart_rc = evidence.get("restart_returncode")
    if restart_rc is None and isinstance(evidence.get("restart"), dict):
        restart_rc = evidence["restart"].get("rc")
    if evidence.get("service_active") is not True or evidence.get("state_stable") is not True or restart_rc != 0:
        reasons.append("runtime_stability_invalid")
    return not reasons, reasons
