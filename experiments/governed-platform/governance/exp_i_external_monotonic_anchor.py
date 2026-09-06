from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Mapping

SCOPE = "EXP-I-PILOT12-EXTERNAL-MONOTONIC-ANCHOR"
AUTHORITY_ID = "composite-authority-A"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _tag(payload: Mapping[str, Any], key: bytes) -> str:
    return hmac.new(key, _canon(dict(payload)), hashlib.sha256).hexdigest()


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(value), sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


class ExternalMonotonicAnchor:
    """Local prototype of freshness state held outside the rollback-target authority DB.

    The anchor record binds a generation to one checkpoint digest. A second,
    separately authenticated minimum record prevents replay of an older valid
    anchor after the minimum has advanced. This is intentionally only a local
    root-separation prototype; it does not claim same-host administrative
    independence or hardware-backed secret isolation.
    """

    def __init__(self, anchor_path: str | Path, minimum_path: str | Path, *, anchor_key: bytes, minimum_key: bytes):
        if not anchor_key or not minimum_key:
            raise ValueError("anchor and minimum keys required")
        self.anchor_path = Path(anchor_path)
        self.minimum_path = Path(minimum_path)
        self._anchor_key = bytes(anchor_key)
        self._minimum_key = bytes(minimum_key)

    @staticmethod
    def _anchor_payload(generation: int, checkpoint_digest: str) -> dict[str, Any]:
        return {
            "scope": SCOPE,
            "authority_id": AUTHORITY_ID,
            "generation": int(generation),
            "checkpoint_digest": str(checkpoint_digest),
        }

    @staticmethod
    def _minimum_payload(generation: int) -> dict[str, Any]:
        return {
            "scope": SCOPE,
            "authority_id": AUTHORITY_ID,
            "minimum_generation": int(generation),
        }

    def _load(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {"_malformed": True}
        return value if isinstance(value, dict) else {"_malformed": True}

    def read_anchor(self) -> dict[str, Any] | None:
        return self._load(self.anchor_path)

    def read_minimum(self) -> dict[str, Any] | None:
        return self._load(self.minimum_path)

    def _valid_anchor_record(self, record: Mapping[str, Any] | None) -> bool:
        if not isinstance(record, Mapping) or record.get("_malformed"):
            return False
        try:
            payload = dict(record["payload"])
            tag = str(record["tag"])
            generation = int(payload["generation"])
        except Exception:
            return False
        if generation < 1:
            return False
        if payload.get("scope") != SCOPE or payload.get("authority_id") != AUTHORITY_ID:
            return False
        if not payload.get("checkpoint_digest"):
            return False
        return hmac.compare_digest(tag, _tag(payload, self._anchor_key))

    def _valid_minimum_record(self, record: Mapping[str, Any] | None) -> bool:
        if not isinstance(record, Mapping) or record.get("_malformed"):
            return False
        try:
            payload = dict(record["payload"])
            tag = str(record["tag"])
            generation = int(payload["minimum_generation"])
        except Exception:
            return False
        if generation < 1:
            return False
        if payload.get("scope") != SCOPE or payload.get("authority_id") != AUTHORITY_ID:
            return False
        return hmac.compare_digest(tag, _tag(payload, self._minimum_key))

    def trusted_minimum(self) -> int | None:
        record = self.read_minimum()
        if not self._valid_minimum_record(record):
            return None
        return int(record["payload"]["minimum_generation"])

    def advance(self, *, generation: int, checkpoint_digest: str) -> dict[str, Any]:
        if not isinstance(generation, int) or generation < 1 or not checkpoint_digest:
            return {"ok": False, "reason": "ANCHOR_INPUT_INVALID"}
        current_anchor = self.read_anchor()
        current_min = self.read_minimum()
        if current_anchor is not None and not self._valid_anchor_record(current_anchor):
            return {"ok": False, "reason": "EXISTING_ANCHOR_INVALID"}
        if current_min is not None and not self._valid_minimum_record(current_min):
            return {"ok": False, "reason": "EXISTING_MINIMUM_INVALID"}
        old_min = 0 if current_min is None else int(current_min["payload"]["minimum_generation"])
        if generation < old_min:
            return {"ok": False, "reason": "MINIMUM_ROLLBACK_DENIED", "trusted_minimum": old_min}
        if current_anchor is not None:
            old_generation = int(current_anchor["payload"]["generation"])
            old_digest = str(current_anchor["payload"]["checkpoint_digest"])
            if generation < old_generation:
                return {"ok": False, "reason": "ANCHOR_ROLLBACK_DENIED"}
            if generation == old_generation and checkpoint_digest != old_digest:
                return {"ok": False, "reason": "ANCHOR_EQUIVOCATION_DENIED"}
            if generation == old_generation and checkpoint_digest == old_digest:
                return {"ok": True, "replay": True, "generation": generation, "checkpoint_digest": checkpoint_digest}
        anchor_payload = self._anchor_payload(generation, checkpoint_digest)
        minimum_payload = self._minimum_payload(max(old_min, generation))
        _atomic_write(self.anchor_path, {"payload": anchor_payload, "tag": _tag(anchor_payload, self._anchor_key)})
        _atomic_write(self.minimum_path, {"payload": minimum_payload, "tag": _tag(minimum_payload, self._minimum_key)})
        return {"ok": True, "replay": False, "generation": generation, "checkpoint_digest": checkpoint_digest}

    def verify_checkpoint(self, checkpoint: Mapping[str, Any], *, requested_minimum: int | None = None) -> dict[str, Any]:
        anchor = self.read_anchor()
        minimum = self.read_minimum()
        if anchor is None:
            return {"ok": False, "reason": "ANCHOR_MISSING"}
        if minimum is None:
            return {"ok": False, "reason": "MINIMUM_MISSING"}
        if not self._valid_anchor_record(anchor):
            return {"ok": False, "reason": "ANCHOR_INVALID"}
        if not self._valid_minimum_record(minimum):
            return {"ok": False, "reason": "MINIMUM_INVALID"}
        trusted_minimum = int(minimum["payload"]["minimum_generation"])
        # requested_minimum is allowed to strengthen but never lower trusted state.
        effective_minimum = max(trusted_minimum, int(requested_minimum or trusted_minimum))
        try:
            statement = dict(checkpoint["statement"])
            generation = int(statement["generation"])
            digest = str(checkpoint["checkpoint_digest"])
        except Exception:
            return {"ok": False, "reason": "CHECKPOINT_MALFORMED"}
        anchor_payload = anchor["payload"]
        if generation < effective_minimum:
            return {"ok": False, "reason": "CHECKPOINT_BELOW_EXTERNAL_MINIMUM", "trusted_minimum": trusted_minimum}
        if int(anchor_payload["generation"]) != generation:
            return {"ok": False, "reason": "ANCHOR_GENERATION_MISMATCH", "trusted_minimum": trusted_minimum}
        if str(anchor_payload["checkpoint_digest"]) != digest:
            return {"ok": False, "reason": "ANCHOR_DIGEST_MISMATCH", "trusted_minimum": trusted_minimum}
        return {
            "ok": True,
            "generation": generation,
            "checkpoint_digest": digest,
            "trusted_minimum": trusted_minimum,
            "reviewer_generated_authority": False,
            "production_authority": False,
            "release_authority": False,
        }
