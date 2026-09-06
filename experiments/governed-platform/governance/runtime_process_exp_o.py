"""EXP-O Pilot 4 trusted-time and process-boundary runtime helpers.

Security-sensitive current time is obtained from trusted component construction,
never from the worker request. The HTTP gateway process remains a pilot using
loopback transport, HMAC test keys, and SQLite persistence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable, Mapping
from urllib import error as urlerror
from urllib import request as urlrequest

from runtime_slice_exp_o import (
    AgentWorker,
    AuthorityKernel,
    DurableEvidenceSpool,
    LocalEnforcementPoint,
    _digest,
    _effect_binding,
)


ClockMs = Callable[[], int]


def system_clock_ms() -> int:
    return time.time_ns() // 1_000_000


class ManualTrustedClock:
    """Deterministic clock controlled by the trusted test harness, not requests."""

    def __init__(self, initial_ms: int) -> None:
        self._now_ms = int(initial_ms)

    def __call__(self) -> int:
        return self._now_ms

    def set(self, value_ms: int) -> None:
        self._now_ms = int(value_ms)

    def advance(self, delta_ms: int) -> None:
        self._now_ms += int(delta_ms)


class FileTrustedClock:
    """Trusted test-process clock read from a file outside the HTTP request body."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def __call__(self) -> int:
        raw = self.path.read_text(encoding="utf-8").strip()
        return int(raw)


class TrustedLocalEnforcementPoint:
    """LEP wrapper that owns its clock and never accepts caller current time."""

    def __init__(
        self,
        kernel: AuthorityKernel,
        permit_signing_key: bytes,
        *,
        clock_ms: ClockMs = system_clock_ms,
    ) -> None:
        self._inner = LocalEnforcementPoint(kernel, permit_signing_key)
        self._clock_ms = clock_ms

    @property
    def gateway_verification_key(self) -> bytes:
        return self._inner.gateway_verification_key

    def authorize(
        self,
        capability: Mapping[str, Any] | None,
        *,
        worker_id: str,
        worker_key_thumbprint: str,
        effect_contract: Mapping[str, Any],
        effect: Mapping[str, Any],
        idempotency_key: str,
        origin_available: bool,
        online_authority_confirmed: bool,
        semantic_verified: bool,
    ) -> dict[str, Any]:
        trusted_now_ms = int(self._clock_ms())
        result = self._inner.authorize(
            capability,
            worker_id=worker_id,
            worker_key_thumbprint=worker_key_thumbprint,
            effect_contract=effect_contract,
            effect=effect,
            idempotency_key=idempotency_key,
            now_ms=trusted_now_ms,
            origin_available=origin_available,
            online_authority_confirmed=online_authority_confirmed,
            semantic_verified=semantic_verified,
        )
        result["trusted_enforcement_time_ms"] = trusted_now_ms
        result["time_source"] = "LEP_TRUSTED_CLOCK"
        return result


class LoopbackMcpClient:
    """HTTP client that preserves transport uncertainty separately from effect state."""

    def __init__(self, base_url: str, *, timeout_s: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = float(timeout_s)

    def execute(
        self,
        *,
        permit: Mapping[str, Any] | None,
        worker_id: str,
        worker_key_thumbprint: str,
        effect: Mapping[str, Any],
        idempotency_key: str,
        untrusted_metadata: Mapping[str, Any] | None = None,
        fault_mode: str | None = None,
    ) -> dict[str, Any]:
        body = {
            "permit": permit,
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect": dict(effect),
            "idempotency_key": idempotency_key,
            "untrusted_metadata": dict(untrusted_metadata or {}),
        }
        data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if fault_mode:
            headers["X-EXP-O-Test-Fault"] = fault_mode
        req = urlrequest.Request(self.base_url + "/execute", data=data, headers=headers, method="POST")
        try:
            with urlrequest.urlopen(req, timeout=self.timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
                payload["transport_complete"] = True
                payload["transport_state"] = "HTTP_RESPONSE_RECEIVED"
                payload["transport"] = "loopback-http"
                return payload
        except urlerror.HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
            except Exception:
                payload = {"authorized": False, "decision": "HTTP_ERROR", "reason": f"HTTP_{exc.code}"}
            payload["transport_complete"] = True
            payload["transport_state"] = "HTTP_RESPONSE_RECEIVED"
            payload["transport"] = "loopback-http"
            return payload
        except (urlerror.URLError, ConnectionError, TimeoutError, OSError) as exc:
            return {
                "authorized": None,
                "executed": None,
                "decision": "TRANSPORT_OUTCOME_UNKNOWN",
                "authoritative_outcome": "UNKNOWN",
                "transport_complete": False,
                "transport_state": "NO_COMPLETE_HTTP_RESPONSE",
                "transport": "loopback-http",
                "transport_error_class": type(exc).__name__,
            }

    def health(self) -> dict[str, Any]:
        req = urlrequest.Request(self.base_url + "/health", method="GET")
        with urlrequest.urlopen(req, timeout=self.timeout_s) as response:
            return json.loads(response.read().decode("utf-8"))


class ProcessBoundaryWorker:
    """Worker using trusted-clock LEP and HTTP gateway client."""

    def __init__(
        self,
        *,
        worker_id: str,
        worker_key_thumbprint: str,
        lep: TrustedLocalEnforcementPoint,
        client: LoopbackMcpClient,
        spool: DurableEvidenceSpool,
    ) -> None:
        self.worker_id = worker_id
        self.worker_key_thumbprint = worker_key_thumbprint
        self._lep = lep
        self._client = client
        self._spool = spool

    def request_effect(
        self,
        *,
        capability: Mapping[str, Any] | None,
        effect_contract: Mapping[str, Any],
        effect: Mapping[str, Any],
        idempotency_key: str,
        origin_available: bool,
        online_authority_confirmed: bool,
        semantic_verified: bool,
        untrusted_metadata: Mapping[str, Any] | None = None,
        fault_mode: str | None = None,
        reconciliation: bool = False,
    ) -> dict[str, Any]:
        record_type = "EXECUTION_RETRY" if reconciliation else "EXECUTION_INTENT"
        self._spool.append(
            record_type,
            {
                "worker_id": self.worker_id,
                "idempotency_key": idempotency_key,
                "effect_digest": _digest(_effect_binding(effect, idempotency_key=idempotency_key)),
                "transport": "loopback-http",
                "untrusted_metadata": dict(untrusted_metadata or {}),
            },
        )
        auth = self._lep.authorize(
            capability,
            worker_id=self.worker_id,
            worker_key_thumbprint=self.worker_key_thumbprint,
            effect_contract=effect_contract,
            effect=effect,
            idempotency_key=idempotency_key,
            origin_available=origin_available,
            online_authority_confirmed=online_authority_confirmed,
            semantic_verified=semantic_verified,
        )
        if not auth.get("authorized", False):
            self._spool.append(
                "EXECUTION_DENIED",
                {
                    "worker_id": self.worker_id,
                    "idempotency_key": idempotency_key,
                    "reason": auth.get("reason"),
                    "time_source": auth.get("time_source"),
                    "trusted_enforcement_time_ms": auth.get("trusted_enforcement_time_ms"),
                },
            )
            return auth

        transport_result = self._client.execute(
            permit=auth["permit"],
            worker_id=self.worker_id,
            worker_key_thumbprint=self.worker_key_thumbprint,
            effect=effect,
            idempotency_key=idempotency_key,
            untrusted_metadata=untrusted_metadata,
            fault_mode=fault_mode,
        )
        if not transport_result.get("transport_complete", False):
            self._spool.append(
                "TRANSPORT_OUTCOME_UNKNOWN",
                {
                    "worker_id": self.worker_id,
                    "idempotency_key": idempotency_key,
                    "transport": transport_result.get("transport"),
                    "transport_state": transport_result.get("transport_state"),
                    "authoritative_outcome": "UNKNOWN",
                },
            )
            return transport_result

        self._spool.append(
            "EXECUTION_RESULT",
            {
                "worker_id": self.worker_id,
                "idempotency_key": idempotency_key,
                "gateway_decision": transport_result.get("decision"),
                "gateway_authorized": transport_result.get("authorized"),
                "executed": transport_result.get("executed"),
                "result": transport_result.get("result"),
                "transport": transport_result.get("transport"),
                "transport_state": transport_result.get("transport_state"),
                "gateway_instance_id": transport_result.get("gateway_instance_id"),
                "gateway_time_ms": transport_result.get("gateway_time_ms"),
            },
        )
        return transport_result

    def reconcile_and_retry(self, **kwargs: Any) -> dict[str, Any]:
        idempotency_key = str(kwargs["idempotency_key"])
        existing = self._spool.result_for_idempotency_key(idempotency_key)
        if existing is not None:
            return {
                "authorized": existing.get("gateway_authorized"),
                "decision": "LOCAL_RESULT_ALREADY_PRESENT",
                "result": existing.get("result"),
                "transport_complete": True,
            }
        self._spool.append(
            "RECONCILIATION_STARTED",
            {"worker_id": self.worker_id, "idempotency_key": idempotency_key},
        )
        retry_kwargs = dict(kwargs)
        retry_kwargs["reconciliation"] = True
        retry_kwargs.pop("fault_mode", None)
        result = self.request_effect(**retry_kwargs)
        self._spool.append(
            "RECONCILIATION_COMPLETED",
            {
                "worker_id": self.worker_id,
                "idempotency_key": idempotency_key,
                "decision": result.get("decision"),
                "transport_complete": result.get("transport_complete"),
            },
        )
        return result


class GatewayProcessHarness:
    """Starts the EXP-O pilot MCP gateway as a separate Python process."""

    def __init__(
        self,
        *,
        db_path: str | Path,
        ready_path: str | Path,
        clock_path: str | Path,
        permit_key: bytes,
        enable_test_faults: bool = True,
    ) -> None:
        self.db_path = Path(db_path)
        self.ready_path = Path(ready_path)
        self.clock_path = Path(clock_path)
        self.permit_key = permit_key
        self.enable_test_faults = bool(enable_test_faults)
        self.process: subprocess.Popen[bytes] | None = None
        self.info: dict[str, Any] | None = None

    @property
    def script_path(self) -> Path:
        return Path(__file__).with_name("mcp_gateway_process_exp_o.py")

    def start(self, *, timeout_s: float = 5.0) -> dict[str, Any]:
        if self.process is not None and self.process.poll() is None:
            raise RuntimeError("gateway process already running")
        self.ready_path.unlink(missing_ok=True)
        env = os.environ.copy()
        env["EXP_O_PERMIT_KEY_HEX"] = self.permit_key.hex()
        args = [
            sys.executable,
            str(self.script_path),
            "--db",
            str(self.db_path),
            "--ready-file",
            str(self.ready_path),
            "--clock-file",
            str(self.clock_path),
        ]
        if self.enable_test_faults:
            args.append("--enable-test-faults")
        self.process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f"gateway process exited early with {self.process.returncode}")
            if self.ready_path.exists():
                self.info = json.loads(self.ready_path.read_text(encoding="utf-8"))
                return dict(self.info)
            time.sleep(0.02)
        self.stop()
        raise TimeoutError("gateway process did not become ready")

    @property
    def base_url(self) -> str:
        if not self.info:
            raise RuntimeError("gateway process not started")
        return f"http://127.0.0.1:{int(self.info['port'])}"

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2.0)
        self.process = None
        self.info = None

    def __enter__(self) -> "GatewayProcessHarness":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()


def read_gateway_effect_count(db_path: str | Path) -> int:
    import sqlite3

    path = str(db_path)
    if not Path(path).exists():
        return 0
    conn = sqlite3.connect(path)
    try:
        row = conn.execute("SELECT COUNT(*) FROM authoritative_effects").fetchone()
        return 0 if row is None else int(row[0])
    except sqlite3.OperationalError:
        return 0
    finally:
        conn.close()


# Retain import solely so the Pilot 4 test can reproduce the frozen Pilot 3
# caller-controlled-time defect without modifying historical code.
LegacyAgentWorker = AgentWorker
