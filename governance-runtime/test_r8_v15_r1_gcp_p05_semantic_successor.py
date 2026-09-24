import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR = ROOT / "governance-r8/R8-V15-R1-GCP-P05-SEMANTIC-SUCCESSOR.json"
V5 = ROOT / "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V5.md"

OLD_BYTES = '{"min":-9223372036854775808,"max":9223372036854775807}'
OLD_SHA = "906c504c6a5ceabaf14e06e427a9ed6d202a1a014d3c32616b00da5040590cab"
NEW_BYTES = '{"max":9223372036854775807,"min":-9223372036854775808}'
NEW_SHA = "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb"

def test_p05_semantic_successor_is_narrow_and_hash_exact():
    data = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
    assert data["predecessor_semantic_candidate_commit"] == "c721b38cf8b00294797300b526596ce723a47ff8"
    assert data["scope"] == "GCP_P05_CANONICAL_KEY_ORDER_ONLY"
    assert data["adjudication"]["preserve_governing_key_order_rule"] is True
    assert data["adjudication"]["supersede_only_historical_p05_bytes_and_hash"] is True
    assert data["adjudication"]["new_expected_canonical_utf8"] == NEW_BYTES
    assert data["adjudication"]["new_expected_sha256"] == NEW_SHA
    assert hashlib.sha256(NEW_BYTES.encode("utf-8")).hexdigest() == NEW_SHA
    assert hashlib.sha256(OLD_BYTES.encode("utf-8")).hexdigest() == OLD_SHA

def test_key_order_is_lexicographic_nfc_scalar_order():
    assert sorted(["min", "max"]) == ["max", "min"]

def test_historical_v5_is_preserved_not_rewritten():
    text = V5.read_text(encoding="utf-8")
    assert OLD_BYTES in text
    assert OLD_SHA in text

def test_successor_grants_no_authority():
    data = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
    assert data["authority_effect"] == "NONE"
    assert all(v is False for v in data["claim_boundary"].values())
