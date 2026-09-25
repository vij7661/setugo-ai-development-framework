"""R8 v15-r1 Slice 46: exact semantic JSON equality for remaining frozen concrete instance family."""
from __future__ import annotations
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any,Dict

SCHEMA_DIR=Path(__file__).resolve().parent.parent/"schemas"/"governance-r8"/"v15-r1"
ARTIFACTS=[
 "review-presentation-schema.json",
 "gcp-rvm-2.json",
 "case-proof-contracts.json",
 "schema-provenance-generator-binding.json",
 "schema-provenance-manifest-candidate.json"
]
def _canon(v:Any)->str:
    try:
        return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    except (TypeError,ValueError) as exc:
        raise FrozenInstanceFamilyExactError("FROZEN_INSTANCE_JSON_INVALID",str(exc)) from exc

_EXPECTED={name:_canon(json.loads((SCHEMA_DIR/name).read_text())) for name in ARTIFACTS}

class FrozenInstanceFamilyExactError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def validate_frozen_instance(name:str,record:Mapping[str,Any])->Dict[str,Any]:
    if name not in _EXPECTED: raise FrozenInstanceFamilyExactError("FROZEN_INSTANCE_UNKNOWN","artifact name not in frozen family")
    if not isinstance(record,Mapping): raise FrozenInstanceFamilyExactError("FROZEN_INSTANCE_NOT_MAPPING","record must be mapping")
    if _canon(record)!=_EXPECTED[name]: raise FrozenInstanceFamilyExactError("FROZEN_INSTANCE_MISMATCH","record is not semantically identical to frozen artifact")
    return {
      "locally_valid":True,
      "artifact_name":name,
      "validation_scope":"EXACT_FROZEN_INSTANCE_SEMANTIC_EQUALITY_ONLY",
      "authority_effect":"NONE",
      "semantic_correctness_verified":False,
      "qualification_verified":False,
      "provenance_verified":False,
      "freeze_readiness_verified":False,
      "runtime_qualified":False,
      "terminal_authority":False
    }
