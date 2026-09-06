"""Process harness for the EXP-O Pilot 5 signed-result gateway."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


class SignedResultGatewayProcessHarness:
    def __init__(
        self,
        *,
        db_path: str | Path,
        ready_path: str | Path,
        clock_path: str | Path,
        permit_key: bytes,
        result_key: bytes,
        enable_test_faults: bool = True,
    ) -> None:
        self.db_path = Path(db_path)
        self.ready_path = Path(ready_path)
        self.clock_path = Path(clock_path)
        self.permit_key = permit_key
        self.result_key = result_key
        self.enable_test_faults = bool(enable_test_faults)
        self.process: subprocess.Popen[bytes] | None = None
        self.info: dict[str, Any] | None = None

    @property
    def script_path(self) -> Path:
        return Path(__file__).with_name("mcp_gateway_result_process_exp_o.py")

    def start(self, *, timeout_s: float = 5.0) -> dict[str, Any]:
        if self.process is not None and self.process.poll() is None:
            raise RuntimeError("signed-result gateway process already running")
        self.ready_path.unlink(missing_ok=True)
        env = os.environ.copy()
        env["EXP_O_PERMIT_KEY_HEX"] = self.permit_key.hex()
        env["EXP_O_RESULT_KEY_HEX"] = self.result_key.hex()
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
                raise RuntimeError(f"signed-result gateway exited early with {self.process.returncode}")
            if self.ready_path.exists():
                self.info = json.loads(self.ready_path.read_text(encoding="utf-8"))
                return dict(self.info)
            time.sleep(0.02)
        self.stop()
        raise TimeoutError("signed-result gateway process did not become ready")

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

    def __enter__(self) -> "SignedResultGatewayProcessHarness":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()
