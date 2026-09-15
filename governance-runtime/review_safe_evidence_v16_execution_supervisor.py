"""V16 Slice 2 external assertion supervisor.

Construction-stage mechanism only.  The evaluated worker is untrusted.  Worker stdout is
parsed as bounded data and worker stderr is diagnostic-only.  Only this supervisor owns
the oracle and writes the completion receipt.

AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence
import unicodedata

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
MAX_CANONICAL_INTEGER = (1 << 53) - 1
CONFIG_FIELDS = frozenset({
    "schema_version",
    "operation_id",
    "worker_command",
    "worker_cwd",
    "request_input",
    "expected_result",
    "timeout_ms",
    "max_stdout_bytes",
    "max_stderr_bytes",
})
RESPONSE_FIELDS = frozenset({"schema_version", "operation_id", "result"})


class SupervisorProtocolError(ValueError):
    """Fail-closed protocol/configuration error."""


def _reject_float(token: str) -> None:
    raise SupervisorProtocolError(f"FLOAT_FORBIDDEN:{token}")


def _reject_constant(token: str) -> None:
    raise SupervisorProtocolError(f"NONFINITE_FORBIDDEN:{token}")


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    normalized: set[str] = set()
    for key, value in pairs:
        if key in out:
            raise SupervisorProtocolError(f"DUPLICATE_JSON_KEY:{key}")
        nfc = unicodedata.normalize("NFC", key)
        if nfc in normalized:
            raise SupervisorProtocolError(f"NORMALIZED_DUPLICATE_JSON_KEY:{key}")
        normalized.add(nfc)
        out[key] = value
    return out


def _validate_plain(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, bool):
        return value
    if type(value) is int:
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise SupervisorProtocolError(f"INTEGER_OUT_OF_RANGE:{path}")
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
            raise SupervisorProtocolError(f"LONE_SURROGATE_FORBIDDEN:{path}")
        if unicodedata.normalize("NFC", value) != value:
            raise SupervisorProtocolError(f"NON_NFC_STRING:{path}")
        return value
    if type(value) is list:
        return [_validate_plain(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if type(value) is dict:
        out: dict[str, Any] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise SupervisorProtocolError(f"NON_STRING_KEY:{path}")
            if unicodedata.normalize("NFC", key) != key:
                raise SupervisorProtocolError(f"NON_NFC_KEY:{path}.{key}")
            out[key] = _validate_plain(item, f"{path}.{key}")
        return out
    raise SupervisorProtocolError(f"UNSUPPORTED_JSON_VALUE:{path}:{type(value).__name__}")


def load_strict_json_bytes(data: bytes, *, label: str) -> Any:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SupervisorProtocolError(f"{label}_UTF8_INVALID") from exc
    try:
        obj = json.loads(
            text,
            object_pairs_hook=_no_duplicate_object,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except SupervisorProtocolError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise SupervisorProtocolError(f"{label}_JSON_INVALID") from exc
    return _validate_plain(obj)


def load_strict_json_file(path: Path, *, label: str) -> Any:
    return load_strict_json_bytes(path.read_bytes(), label=label)


def canonical_bytes(value: Any) -> bytes:
    plain = _validate_plain(value)
    return json.dumps(
        plain,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_config(config: Any) -> dict[str, Any]:
    if type(config) is not dict:
        raise SupervisorProtocolError("CONFIG_MUST_BE_OBJECT")
    if set(config) != CONFIG_FIELDS:
        raise SupervisorProtocolError("CONFIG_FIELDS_NOT_EXACT")
    if config.get("schema_version") != 1 or type(config.get("schema_version")) is not int:
        raise SupervisorProtocolError("CONFIG_SCHEMA_INVALID")
    operation_id = config.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id.strip():
        raise SupervisorProtocolError("OPERATION_ID_REQUIRED")
    command = config.get("worker_command")
    if type(command) is not list or not command:
        raise SupervisorProtocolError("WORKER_COMMAND_REQUIRED")
    if any(not isinstance(arg, str) or not arg for arg in command):
        raise SupervisorProtocolError("WORKER_COMMAND_ARGUMENT_INVALID")
    cwd = config.get("worker_cwd")
    if cwd is not None and (not isinstance(cwd, str) or not cwd):
        raise SupervisorProtocolError("WORKER_CWD_INVALID")
    for field in ("timeout_ms", "max_stdout_bytes", "max_stderr_bytes"):
        value = config.get(field)
        if type(value) is not int or value <= 0 or value > MAX_CANONICAL_INTEGER:
            raise SupervisorProtocolError(f"{field.upper()}_INVALID")
    if config["timeout_ms"] > 120_000:
        raise SupervisorProtocolError("TIMEOUT_MS_TOO_LARGE")
    if config["max_stdout_bytes"] > 1_048_576:
        raise SupervisorProtocolError("MAX_STDOUT_BYTES_TOO_LARGE")
    if config["max_stderr_bytes"] > 4_194_304:
        raise SupervisorProtocolError("MAX_STDERR_BYTES_TOO_LARGE")
    _validate_plain(config["request_input"], "$.request_input")
    _validate_plain(config["expected_result"], "$.expected_result")
    return dict(config)


def _terminate_process_group(proc: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass


def _run_worker_bounded(
    command: Sequence[str], *,
    cwd: str | None,
    request_bytes: bytes,
    timeout_ms: int,
    max_stdout_bytes: int,
    max_stderr_bytes: int,
) -> dict[str, Any]:
    started = time.monotonic()
    proc = subprocess.Popen(
        list(command),
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        close_fds=True,
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None
    try:
        proc.stdin.write(request_bytes)
        proc.stdin.flush()
    except BrokenPipeError:
        pass
    finally:
        try:
            proc.stdin.close()
        except BrokenPipeError:
            pass

    selector = selectors.DefaultSelector()
    for name, stream in (("stdout", proc.stdout), ("stderr", proc.stderr)):
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, data=name)

    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    limits = {"stdout": max_stdout_bytes, "stderr": max_stderr_bytes}
    overflow: str | None = None
    timed_out = False
    deadline = started + timeout_ms / 1000.0

    while selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            _terminate_process_group(proc)
            break
        events = selector.select(timeout=min(remaining, 0.05))
        if not events:
            if proc.poll() is not None:
                # Drain any bytes already readable after process termination.
                events = selector.select(timeout=0)
                if not events:
                    break
            else:
                continue
        for key, _ in events:
            stream = key.fileobj
            name = key.data
            try:
                chunk = os.read(stream.fileno(), 8192)
            except BlockingIOError:
                continue
            if not chunk:
                try:
                    selector.unregister(stream)
                except KeyError:
                    pass
                continue
            buffers[name].extend(chunk)
            if len(buffers[name]) > limits[name]:
                overflow = name
                _terminate_process_group(proc)
                break
        if overflow is not None:
            break

    if timed_out or overflow is not None:
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            _terminate_process_group(proc)
            proc.wait(timeout=2)
    else:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process_group(proc)
            proc.wait(timeout=2)

    # Drain bounded residual bytes after process termination.
    for name, stream in (("stdout", proc.stdout), ("stderr", proc.stderr)):
        while True:
            try:
                chunk = os.read(stream.fileno(), 8192)
            except BlockingIOError:
                break
            if not chunk:
                break
            buffers[name].extend(chunk)
            if len(buffers[name]) > limits[name]:
                overflow = overflow or name
                break

    selector.close()
    duration_ms = int((time.monotonic() - started) * 1000)
    return {
        "return_code": proc.returncode,
        "timed_out": timed_out,
        "overflow_stream": overflow,
        "stdout": bytes(buffers["stdout"][: max_stdout_bytes + 1]),
        "stderr": bytes(buffers["stderr"][: max_stderr_bytes + 1]),
        "duration_ms": duration_ms,
    }


def supervise(config: Mapping[str, Any]) -> dict[str, Any]:
    cfg = validate_config(dict(config))
    operation_id = cfg["operation_id"]
    request = {
        "schema_version": 1,
        "operation_id": operation_id,
        "input": cfg["request_input"],
    }
    request_bytes = canonical_bytes(request) + b"\n"
    problems: list[str] = []
    response_valid = False
    oracle_pass = False
    response_result: Any = None

    worker = _run_worker_bounded(
        cfg["worker_command"],
        cwd=cfg["worker_cwd"],
        request_bytes=request_bytes,
        timeout_ms=cfg["timeout_ms"],
        max_stdout_bytes=cfg["max_stdout_bytes"],
        max_stderr_bytes=cfg["max_stderr_bytes"],
    )

    post_worker_assertion_reached = True
    rc = worker["return_code"]
    worker_signal = -rc if isinstance(rc, int) and rc < 0 else None
    if worker["timed_out"]:
        problems.append("WORKER_TIMEOUT")
    if worker["overflow_stream"] == "stdout":
        problems.append("WORKER_STDOUT_OVERSIZE")
    elif worker["overflow_stream"] == "stderr":
        problems.append("WORKER_STDERR_OVERSIZE")
    if worker_signal is not None:
        problems.append(f"WORKER_SIGNAL:{worker_signal}")
    elif rc != 0:
        problems.append(f"WORKER_EXIT_NONZERO:{rc}")

    if not problems:
        try:
            response = load_strict_json_bytes(worker["stdout"], label="WORKER_RESPONSE")
            if type(response) is not dict:
                raise SupervisorProtocolError("WORKER_RESPONSE_MUST_BE_OBJECT")
            if set(response) != RESPONSE_FIELDS:
                raise SupervisorProtocolError("WORKER_RESPONSE_FIELDS_NOT_EXACT")
            if response.get("schema_version") != 1 or type(response.get("schema_version")) is not int:
                raise SupervisorProtocolError("WORKER_RESPONSE_SCHEMA_INVALID")
            if response.get("operation_id") != operation_id:
                raise SupervisorProtocolError("WORKER_RESPONSE_OPERATION_ID_MISMATCH")
            response_result = response.get("result")
            _validate_plain(response_result, "$.result")
            response_valid = True
        except SupervisorProtocolError as exc:
            problems.append(str(exc))

    if response_valid:
        # The load-bearing assertion is intentionally performed here, after worker
        # completion, in the supervisor process.  A worker's own PASS claim is data only.
        try:
            oracle_pass = canonical_bytes(response_result) == canonical_bytes(cfg["expected_result"])
        except SupervisorProtocolError as exc:
            problems.append(f"SUPERVISOR_ORACLE_CANONICALIZATION:{exc}")
            oracle_pass = False
        if not oracle_pass:
            problems.append("SUPERVISOR_ORACLE_MISMATCH")

    valid = not problems and response_valid and oracle_pass and post_worker_assertion_reached
    stdout = worker["stdout"]
    stderr = worker["stderr"]
    receipt = {
        "schema_version": 1,
        "object_type": "V16_SUPERVISOR_EXECUTION_RECEIPT",
        "operation_id": operation_id,
        "state": "SUPERVISOR_ORACLE_PASS_NONAUTHORITATIVE" if valid else "SUPERVISOR_FAIL_CLOSED",
        "supervisor_post_worker_assertion_reached": post_worker_assertion_reached,
        "worker_return_code": rc,
        "worker_signal": worker_signal,
        "worker_timed_out": worker["timed_out"],
        "worker_overflow_stream": worker["overflow_stream"],
        "response_valid": response_valid,
        "oracle_pass": oracle_pass,
        "request_sha256": _sha_bytes(request_bytes),
        "stdout_sha256": _sha_bytes(stdout),
        "stderr_sha256": _sha_bytes(stderr),
        "duration_ms": worker["duration_ms"],
        "problems": sorted(set(problems)),
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
    receipt["receipt_digest"] = canonical_sha256(receipt)
    return receipt


def _write_receipt(path: Path, receipt: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(dict(receipt)) + b"\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args(argv)
    receipt_path = Path(args.receipt)
    try:
        config = load_strict_json_file(Path(args.config), label="SUPERVISOR_CONFIG")
        receipt = supervise(config)
    except (OSError, SupervisorProtocolError, subprocess.SubprocessError) as exc:
        receipt = {
            "schema_version": 1,
            "object_type": "V16_SUPERVISOR_EXECUTION_RECEIPT",
            "operation_id": "UNKNOWN",
            "state": "SUPERVISOR_FAIL_CLOSED",
            "supervisor_post_worker_assertion_reached": False,
            "worker_return_code": None,
            "worker_signal": None,
            "worker_timed_out": False,
            "worker_overflow_stream": None,
            "response_valid": False,
            "oracle_pass": False,
            "request_sha256": None,
            "stdout_sha256": None,
            "stderr_sha256": None,
            "duration_ms": 0,
            "problems": [f"SUPERVISOR_CONFIGURATION_OR_LAUNCH_FAILURE:{type(exc).__name__}:{exc}"],
            "qualified": False,
            "implementation_qualification": "NOT_CLAIMED",
            "runtime_qualification": "NOT_CLAIMED",
            "authority_effect": AUTHORITY_EFFECT,
        }
        receipt["receipt_digest"] = canonical_sha256(receipt)
    _write_receipt(receipt_path, receipt)
    print(receipt["state"])
    print("AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY")
    return 0 if receipt["state"] == "SUPERVISOR_ORACLE_PASS_NONAUTHORITATIVE" else 70


if __name__ == "__main__":
    raise SystemExit(main())
