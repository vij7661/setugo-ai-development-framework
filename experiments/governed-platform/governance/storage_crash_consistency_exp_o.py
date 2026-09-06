"""EXP-O Pilot 15 deterministic storage crash-consistency prototype.

This is a falsification harness, not a production WAL/filesystem implementation.
It models written-vs-durable journal state, durable checkpoints, independent effect
identity, integrity-chain recovery, and fail-closed ambiguity handling.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

CRASH_POINTS = (
    "AFTER_AUTHORITY_RECORD_WRITE_BEFORE_FSYNC",
    "AFTER_AUTHORITY_RECORD_FSYNC_BEFORE_CHECKPOINT",
    "AFTER_CHECKPOINT_WRITE_BEFORE_FSYNC",
    "AFTER_EFFECT_COMMIT_BEFORE_EFFECT_EVIDENCE_WRITE",
    "AFTER_EFFECT_EVIDENCE_WRITE_BEFORE_FSYNC",
    "AFTER_EFFECT_EVIDENCE_FSYNC_BEFORE_AUTHORITY_CONSUMED",
    "AFTER_AUTHORITY_CONSUMED_WRITE_BEFORE_FSYNC",
    "AFTER_AUTHORITY_CONSUMED_FSYNC_BEFORE_CHECKPOINT",
    "AFTER_TAKEOVER_FENCE_WRITE_BEFORE_FSYNC",
    "AFTER_TAKEOVER_FENCE_FSYNC_BEFORE_CHECKPOINT",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def deny(reason: str, **extra: Any) -> dict[str, Any]:
    out = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


class CrashInjected(RuntimeError):
    pass


class StorageCrashPrototype:
    """Single-directory durability model with explicit durable boundaries."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.journal = self.root / "journal.frames"
        self.durable_meta = self.root / "durable-meta.json"
        self.checkpoint = self.root / "checkpoint.json"
        self.checkpoint_durable = self.root / "checkpoint.durable.json"
        self.effect_ledger = self.root / "effects.json"
        self.anchor = self.root / "external-anchor.json"
        if not self.journal.exists():
            self.journal.write_bytes(b"")
        if not self.durable_meta.exists():
            self._atomic_json(self.durable_meta, {"durable_seq": 0})
        if not self.effect_ledger.exists():
            self._atomic_json(self.effect_ledger, {"effects": {}})

    def _atomic_json(self, path: Path, value: Any) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "wb") as f:
            f.write(canonical(value))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def _load_json(self, path: Path, default: Any = None) -> Any:
        if not path.exists():
            return copy.deepcopy(default)
        return json.loads(path.read_text(encoding="utf-8"))

    def _raw_frames(self) -> list[tuple[dict[str, Any], int]]:
        data = self.journal.read_bytes()
        frames: list[tuple[dict[str, Any], int]] = []
        offset = 0
        for line in data.splitlines(keepends=True):
            offset += len(line)
            if not line.endswith(b"\n"):
                raise ValueError("TORN_FINAL_FRAME")
            try:
                frame = json.loads(line[:-1].decode("utf-8"))
            except Exception as exc:
                raise ValueError("FRAME_PARSE_INVALID") from exc
            if not isinstance(frame, dict):
                raise ValueError("FRAME_NOT_OBJECT")
            frames.append((frame, offset))
        return frames

    def validate_journal(self) -> dict[str, Any]:
        try:
            frames = self._raw_frames()
        except ValueError as exc:
            return {"valid": False, "reason": str(exc), "records": []}
        records: list[dict[str, Any]] = []
        prev = "GENESIS"
        expected_seq = 1
        for frame, _ in frames:
            if frame.get("seq") != expected_seq:
                return {"valid": False, "reason": "SEQUENCE_CONFLICT", "records": records}
            core = {
                "seq": frame.get("seq"),
                "record_type": frame.get("record_type"),
                "payload": frame.get("payload"),
                "prev_digest": frame.get("prev_digest"),
            }
            if frame.get("prev_digest") != prev:
                return {"valid": False, "reason": "PREVIOUS_DIGEST_MISMATCH", "records": records}
            expected_digest = digest(core)
            if frame.get("record_digest") != expected_digest:
                return {"valid": False, "reason": "RECORD_DIGEST_MISMATCH", "records": records}
            records.append(copy.deepcopy(frame))
            prev = expected_digest
            expected_seq += 1
        return {"valid": True, "reason": None, "records": records, "highest_seq": len(records), "highest_digest": prev}

    def append_record(self, record_type: str, payload: Mapping[str, Any], *, durable: bool) -> dict[str, Any]:
        validation = self.validate_journal()
        if not validation.get("valid"):
            raise ValueError(f"cannot append to invalid journal: {validation.get('reason')}")
        seq = int(validation.get("highest_seq", 0)) + 1
        prev = str(validation.get("highest_digest", "GENESIS"))
        core = {"seq": seq, "record_type": record_type, "payload": copy.deepcopy(dict(payload)), "prev_digest": prev}
        frame = dict(core)
        frame["record_digest"] = digest(core)
        with open(self.journal, "ab") as f:
            f.write(canonical(frame) + b"\n")
            f.flush()
            if durable:
                os.fsync(f.fileno())
        if durable:
            self._atomic_json(self.durable_meta, {"durable_seq": seq})
        return frame

    def fsync_through(self, seq: int) -> None:
        validation = self.validate_journal()
        if not validation.get("valid") or int(validation.get("highest_seq", 0)) < seq:
            raise ValueError("cannot fsync invalid/missing sequence")
        with open(self.journal, "rb") as f:
            os.fsync(f.fileno())
        self._atomic_json(self.durable_meta, {"durable_seq": int(seq)})

    def durable_seq(self) -> int:
        return int(self._load_json(self.durable_meta, {"durable_seq": 0})["durable_seq"])

    def simulate_power_loss(self) -> None:
        """Drop journal/checkpoint bytes that the prototype never marked durable."""
        durable_seq = self.durable_seq()
        try:
            frames = self._raw_frames()
        except ValueError:
            # If a torn tail exists, retain only complete frames at/below the durable marker.
            data = self.journal.read_bytes()
            lines = data.splitlines(keepends=True)
            complete = [line for line in lines if line.endswith(b"\n")]
            frames = []
            offset = 0
            for line in complete:
                offset += len(line)
                try:
                    frames.append((json.loads(line[:-1].decode("utf-8")), offset))
                except Exception:
                    break
        cutoff = 0
        for frame, offset in frames:
            if int(frame.get("seq", 0)) <= durable_seq:
                cutoff = offset
        with open(self.journal, "r+b") as f:
            f.truncate(cutoff)
            f.flush()
            os.fsync(f.fileno())
        if self.checkpoint.exists():
            self.checkpoint.unlink()

    def write_checkpoint(self, seq: int, record_digest: str, *, durable: bool) -> dict[str, Any]:
        cp = {"seq": int(seq), "record_digest": str(record_digest)}
        self.checkpoint.write_bytes(canonical(cp))
        if durable:
            with open(self.checkpoint, "rb") as f:
                os.fsync(f.fileno())
            self._atomic_json(self.checkpoint_durable, cp)
        return cp

    def durable_checkpoint(self) -> dict[str, Any] | None:
        return self._load_json(self.checkpoint_durable, None)

    def anchor_fence(self, *, term: int, index: int, lease_epoch: int, record_digest: str) -> None:
        self._atomic_json(self.anchor, {
            "term": int(term), "index": int(index), "lease_epoch": int(lease_epoch), "record_digest": record_digest
        })

    def effect_apply(self, idempotency_key: str, effect_digest: str) -> dict[str, Any]:
        ledger = self._load_json(self.effect_ledger, {"effects": {}})
        effects = ledger["effects"]
        existing = effects.get(idempotency_key)
        if existing is not None:
            if existing.get("effect_digest") != effect_digest:
                return deny("IDEMPOTENCY_EFFECT_REBINDING_DENIED")
            return {"authorized": True, "executed": False, "replayed": True, "result_id": existing["result_id"]}
        result_id = digest({"idempotency_key": idempotency_key, "effect_digest": effect_digest})
        effects[idempotency_key] = {"effect_digest": effect_digest, "result_id": result_id}
        self._atomic_json(self.effect_ledger, ledger)
        return {"authorized": True, "executed": True, "replayed": False, "result_id": result_id}

    def effect_lookup(self, idempotency_key: str) -> dict[str, Any] | None:
        return copy.deepcopy(self._load_json(self.effect_ledger, {"effects": {}})["effects"].get(idempotency_key))

    def effect_count(self) -> int:
        return len(self._load_json(self.effect_ledger, {"effects": {}})["effects"])

    def _record_at(self, records: list[dict[str, Any]], seq: int) -> dict[str, Any] | None:
        for record in records:
            if int(record["seq"]) == int(seq):
                return record
        return None

    def recover(self) -> dict[str, Any]:
        validation = self.validate_journal()
        if not validation.get("valid"):
            return deny(str(validation.get("reason")), recovery_status="CORRUPT")
        records = validation["records"]
        durable_seq = self.durable_seq()
        if int(validation.get("highest_seq", 0)) < durable_seq:
            return deny("DURABLE_MARKER_BEYOND_VALID_PREFIX", recovery_status="CORRUPT")
        durable_records = [r for r in records if int(r["seq"]) <= durable_seq]
        cp = self.durable_checkpoint()
        if cp is not None:
            if int(cp["seq"]) > len(durable_records):
                return deny("CHECKPOINT_BEYOND_VALID_PREFIX", recovery_status="CORRUPT")
            ref = self._record_at(durable_records, int(cp["seq"]))
            if ref is None or ref["record_digest"] != cp["record_digest"]:
                return deny("CHECKPOINT_DIGEST_MISMATCH", recovery_status="CORRUPT")
        anchor = self._load_json(self.anchor, None)
        authority: dict[str, Any] | None = None
        consumed: dict[str, Any] | None = None
        highest_fence: dict[str, Any] | None = None
        effect_evidence: dict[str, Any] | None = None
        for record in durable_records:
            typ = record["record_type"]
            payload = record["payload"]
            if typ in {"AUTHORITY", "TAKEOVER_FENCE"}:
                authority = copy.deepcopy(payload)
                if typ == "TAKEOVER_FENCE":
                    highest_fence = copy.deepcopy(payload)
                    highest_fence["record_digest"] = record["record_digest"]
            elif typ == "EFFECT_EVIDENCE":
                effect_evidence = copy.deepcopy(payload)
            elif typ == "AUTHORITY_CONSUMED":
                consumed = copy.deepcopy(payload)
        if anchor is not None:
            candidate = highest_fence or authority
            if candidate is None:
                return deny("ANCHORED_HIGHER_FENCE_MISSING", recovery_status="STALE_ROLLBACK_BLOCKED")
            observed = (int(candidate.get("term", 0)), int(candidate.get("index", 0)), int(candidate.get("lease_epoch", 0)))
            anchored = (int(anchor["term"]), int(anchor["index"]), int(anchor["lease_epoch"]))
            if observed < anchored:
                return deny("ANCHORED_HIGHER_FENCE_MISSING", recovery_status="STALE_ROLLBACK_BLOCKED")
            if observed == anchored and candidate.get("record_digest") not in {None, anchor.get("record_digest")}:
                return deny("ANCHORED_FENCE_DIGEST_MISMATCH", recovery_status="CORRUPT")
        # Any durable authority/fence beyond a durable checkpoint is evidence that stale
        # checkpoint state cannot be trusted for consequential use.
        cp_seq = int(cp["seq"]) if cp is not None else 0
        uncheckpointed = [r for r in durable_records if int(r["seq"]) > cp_seq]
        if uncheckpointed:
            if effect_evidence is not None or consumed is not None:
                return deny("DURABLE_STATE_AHEAD_OF_CHECKPOINT", recovery_status="RECONCILIATION_REQUIRED",
                            original_result_id=(effect_evidence or {}).get("result_id"))
            return deny("DURABLE_AUTHORITY_AHEAD_OF_CHECKPOINT", recovery_status="RECONCILIATION_REQUIRED")
        if consumed is not None:
            key = str(consumed.get("idempotency_key", ""))
            effect = self.effect_lookup(key)
            if effect is None or effect.get("result_id") != consumed.get("result_id"):
                return deny("CONSUMED_EFFECT_IDENTITY_MISSING", recovery_status="RECONCILIATION_REQUIRED")
            return deny("AUTHORITY_ALREADY_CONSUMED", recovery_status="RECOVERED_CONSUMED", original_result_id=effect["result_id"])
        if effect_evidence is not None:
            key = str(effect_evidence.get("idempotency_key", ""))
            effect = self.effect_lookup(key)
            if effect is None or effect.get("result_id") != effect_evidence.get("result_id"):
                return deny("EFFECT_EVIDENCE_LEDGER_MISMATCH", recovery_status="RECONCILIATION_REQUIRED")
            return deny("EFFECT_ALREADY_COMMITTED", recovery_status="RECOVERED_EFFECT", original_result_id=effect["result_id"])
        if authority is None:
            # Effect ledger can still prove an ambiguous prior side effect even if journal evidence was lost.
            effects = self._load_json(self.effect_ledger, {"effects": {}})["effects"]
            if effects:
                return deny("EFFECT_PRESENT_WITHOUT_AUTHORITY_EVIDENCE", recovery_status="RECONCILIATION_REQUIRED")
            return deny("NO_DURABLE_AUTHORITY", recovery_status="EMPTY")
        required = ("term", "index", "lease_owner", "lease_epoch", "idempotency_key", "effect_digest", "semantic_digest")
        if any(authority.get(k) in (None, "") for k in required):
            return deny("AUTHORITY_BINDING_INCOMPLETE", recovery_status="CORRUPT")
        return {
            "authorized": True,
            "decision": "ALLOW_RECOVERED_AUTHORITY",
            "recovery_status": "AUTHORITATIVE",
            "authority": copy.deepcopy(authority),
        }

    def use_recovered_authority(self, recovered: Mapping[str, Any], *, idempotency_key: str, effect_digest: str,
                                semantic_digest: str) -> dict[str, Any]:
        if not recovered.get("authorized") or recovered.get("recovery_status") != "AUTHORITATIVE":
            return deny("RECOVERED_AUTHORITY_REQUIRED")
        auth = recovered["authority"]
        if auth.get("idempotency_key") != idempotency_key or auth.get("effect_digest") != effect_digest or auth.get("semantic_digest") != semantic_digest:
            return deny("RECOVERED_BINDING_MISMATCH")
        existing = self.effect_lookup(idempotency_key)
        if existing is not None:
            if existing.get("effect_digest") != effect_digest:
                return deny("IDEMPOTENCY_EFFECT_REBINDING_DENIED")
            return {"authorized": False, "decision": "RECONCILED", "executed": False, "result_id": existing["result_id"]}
        return {"authorized": True, "decision": "ALLOW_EFFECT", "executed": False}


def authority_payload(*, term: int = 1, index: int = 1, owner: str = "r1", epoch: int = 1,
                      key: str = "intent-1", effect: str = "effect-A", semantic: str = "semantic-A") -> dict[str, Any]:
    return {
        "term": term, "index": index, "lease_owner": owner, "lease_epoch": epoch,
        "idempotency_key": key, "effect_digest": effect, "semantic_digest": semantic,
    }
