"""EXP-O Pilot 10 loopback process harness for semantic-bound permits."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping
from urllib import error as urlerror
from urllib import request as urlrequest


class SemanticLoopbackClient:
    """Caller-facing client; raw inner LEP permits are not part of this API."""

    def __init__(self, base_url: str, *, timeout_s: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = float(timeout_s)
        self.last_request_body: dict[str, Any] | None = None
        self.last_response_body: dict[str, Any] | None = None

    def execute(
        self,
        *,
        permit: Mapping[str, Any] | None,
        candidate_payload: Mapping[str, Any],
        worker_id: str,
        worker_key_thumbprint: str,
        effect: Mapping[str, Any],
        idempotency_key: str,
        fault_mode: str | None = None,
    ) -> dict[str, Any]:
        body = {
            "permit": copy.deepcopy(dict(permit)) if isinstance(permit, Mapping) else None,
            "candidate_payload": copy.deepcopy(dict(candidate_payload)),
            "worker_id": worker_id,
            "worker_key_thumbprint": worker_key_thumbprint,
            "effect": copy.deepcopy(dict(effect)),
            "idempotency_key": idempotency_key,
        }
        self.last_request_body = copy.deepcopy(body)
        self.last_response_body = None
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
                self.last_response_body = copy.deepcopy(payload)
                return payload
        except urlerror.HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
            except Exception:
                payload = {"authorized": False, "decision": "HTTP_ERROR", "reason": f"HTTP_{exc.code}"}
            payload["transport_complete"] = True
            payload["transport_state"] = "HTTP_RESPONSE_RECEIVED"
            self.last_response_body = copy.deepcopy(payload)
            return payload
        except (urlerror.URLError, ConnectionError, TimeoutError, OSError, json.JSONDecodeError) as exc:
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


class SemanticGatewayProcessHarness:
    """Starts Pilot 10's semantic-bound gateway in a separate Python process."""

    def __init__(
        self,
        *,
        effects_db_path: str | Path,
        registry_db_path: str | Path,
        ready_path: str | Path,
        clock_path: str | Path,
        outer_permit_key: bytes,
        registry_key: bytes,
        inner_permit_key: bytes,
        enable_test_faults: bool = True,
    ) -> None:
        self.effects_db_path = Path(effects_db_path)
        self.registry_db_path = Path(registry_db_path)
        self.ready_path = Path(ready_path)
        self.clock_path = Path(clock_path)
        self.outer_permit_key = bytes(outer_permit_key)
        self.registry_key = bytes(registry_key)
        self.inner_permit_key = bytes(inner_permit_key)
        self.enable_test_faults = bool(enable_test_faults)
        self.process: subprocess.Popen[bytes] | None = None
        self.info: dict[str, Any] | None = None

    @property
    def script_path(self) -> Path:
        return Path(__file__).with_name("mcp_semantic_gateway_process_exp_o.py")

    def start(self, *, timeout_s: float = 5.0) -> dict[str, Any]:
        if self.process is not None and self.process.poll() is None:
            raise RuntimeError("semantic gateway process already running")
        self.ready_path.unlink(missing_ok=True)
        env = os.environ.copy()
        env.pop("EXP_O_SEMANTIC_VERIFIER_SIGNING_KEY_HEX", None)
        env.pop("EXP_O_AUTHORITY_KERNEL_SIGNING_KEY_HEX", None)
        env["EXP_O_OUTER_PERMIT_KEY_HEX"] = self.outer_permit_key.hex()
        env["EXP_O_SEMANTIC_REGISTRY_KEY_HEX"] = self.registry_key.hex()
        env["EXP_O_INNER_PERMIT_KEY_HEX"] = self.inner_permit_key.hex()
        args = [
            sys.executable,
            str(self.script_path),
            "--effects-db",
            str(self.effects_db_path),
            "--registry-db",
            str(self.registry_db_path),
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
                code = self.process.returncode
                self.process = None
                raise RuntimeError(f"semantic gateway process exited early with {code}")
            if self.ready_path.exists():
                self.info = json.loads(self.ready_path.read_text(encoding="utf-8"))
                return dict(self.info)
            time.sleep(0.02)
        self.stop()
        raise TimeoutError("semantic gateway process did not become ready")

    @property
    def base_url(self) -> str:
        if not self.info:
            raise RuntimeError("semantic gateway process not started")
        return f"http://127.0.0.1:{int(self.info['port'])}"

    def client(self, *, timeout_s: float = 2.0) -> SemanticLoopbackClient:
        return SemanticLoopbackClient(self.base_url, timeout_s=timeout_s)

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2.0)
        self.process = None
        self.info = None

    def restart(self, *, timeout_s: float = 5.0) -> dict[str, Any]:
        self.stop()
        return self.start(timeout_s=timeout_s)

    def __enter__(self) -> "SemanticGatewayProcessHarness":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()
