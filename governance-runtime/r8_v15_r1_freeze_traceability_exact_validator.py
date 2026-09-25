"""R8 v15-r1 exact frozen JSON equality validator for schema-freeze traceability."""
from __future__ import annotations
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict

SCHEMA_DIR=Path(__file__).resolve().parent.parent/"schemas"/"governance-r8"/"v15-r1"
EXPECTED=json.loads((SCHEMA_DIR/"schema-freeze-traceability.json").read_text())
def _canon(value:Any)->str:
    try:
        return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    except (TypeError,ValueError) as exc:
        raise FreezeTraceabilityExactError("FROZEN_JSON_INVALID",str(exc)) from exc
EXPECTED_CANON=_canon(EXPECTED)

class FreezeTraceabilityExactError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def validate_freeze_traceability(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise FreezeTraceabilityExactError("FROZEN_JSON_NOT_MAPPING","record must be mapping")
    if _canon(record)!=EXPECTED_CANON:
        raise FreezeTraceabilityExactError("FROZEN_JSON_MISMATCH","record is not semantically identical to frozen artifact")
    return {
      "locally_valid":True,
      "validation_scope":"EXACT_FROZEN_JSON_SEMANTIC_EQUALITY_ONLY",
      "authority_effect":"NONE",
      "source_semantics_verified":False,
      "rule_execution_performed":False,
      "runtime_qualified":False,
      "terminal_authority":False
    }
